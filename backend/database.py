import sqlite3
import bcrypt
from threading import local

class DatabaseManager:
    _connections = local()

    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = None

    def execute_query(self, query, parameters=[]):     
        try:
            self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
            cursor = self.conn.cursor()
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)
            self.conn.commit()
            result = cursor.fetchall()
            cursor.close()
            return result
        except sqlite3.Error as e:
            print("Error executing query:", e, "Query:", query, "Parameters:", parameters)
            return None
        finally:
            if self.conn:
                self.conn.close()

# Gestión de autentificación

    def save_user_to_database(self, username, email, password):
        # Genera un hash de la contraseña utilizando bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        query = 'INSERT INTO users (username, email, password) VALUES (?, ?, ?)'
        self.execute_query(query, (username, email, hashed_password.decode('utf-8')))

    def check_credentials(self, username, password):
        query = "SELECT password FROM users WHERE username = ?"
        result = self.execute_query(query, (username,))
        if result:
            stored_password = result[0][0]  # Obtener el hash almacenado
            # Comparar la contraseña proporcionada con el hash almacenado
            return bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
        return False

    def get_user_id(self, username):
        query = "SELECT id FROM users WHERE username = ?"
        result = self.execute_query(query, (username,))
        return result[0][0] if result else None
    
# Gestión de usuarios

    def get_user_data(self, username):
        query = "SELECT * FROM users WHERE username = ?"
        return self.execute_query(query, (username,))

    def change_password(self, user_id, new_password):
        hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        query = "UPDATE users SET password = ? WHERE id = ?"
        self.execute_query(query, (hashed_new_password, user_id))

# Text Analyzer

    def get_habitaciones_por_usuario(self, user_id):
        query = """
            SELECT h.nombre 
            FROM habitaciones h
            WHERE h.usuario_id = ?
        """
        result = self.execute_query(query, (user_id,))
        return [habitacion[0].lower() for habitacion in result]

    def get_dispositivos_por_usuario(self, user_id):
        query = """
            SELECT d.nombre 
            FROM dispositivos d
            JOIN habitaciones h ON d.habitacion_id = h.id
            WHERE h.usuario_id = ?
        """
        result = self.execute_query(query, (user_id,))
        return [dispositivo[0].lower() for dispositivo in result]
    
    def get_id_habitacion(self, habitacion):
        query = "SELECT id FROM habitaciones WHERE nombre = ?"
        result_id = self.execute_query(query, (habitacion,))
        return result_id[0][0] if result_id else None
    
    def get_nombre_dispositivos_habitacion(self, hab_id):
        query = "SELECT nombre FROM dispositivos WHERE habitacion_id = ?"
        result = self.execute_query(query, (hab_id,))
        return [dispositivo[0].lower() for dispositivo in result]

    def get_estado_dispositivo(self, dispositivo, habitacion):
        query = '''
            SELECT d.estado FROM dispositivos d
            JOIN habitaciones h ON d.habitacion_id = h.id
            WHERE d.nombre = ? AND h.nombre = ?
            '''
        result = self.execute_query(query, (dispositivo, habitacion))
        return result[0] if result else None

    def get_dispositivo_id(self, dispositivo):
        query = "SELECT id FROM dispositivos WHERE nombre = ?"
        result = self.execute_query(query, (dispositivo,))
        return result[0][0] if result else None
    
    def get_tipo_dispositivo_id(self, dispositivo):
        # Consulta para obtener el tipo y habitacion_id del dispositivo
        query = """
            SELECT d.tipo, h.tipo_id
            FROM dispositivos d
            LEFT JOIN habitaciones h ON d.habitacion_id = h.id
            WHERE d.nombre = ?
        """
        result = self.execute_query(query, (dispositivo,))
        # Consulta para obtener el ID del tipo de dispositivo
        query_tipo_dispositivo_id = """
            SELECT id 
            FROM tipos_dispositivos 
            WHERE nombre = ? 
            AND tipo_habitacion_id = ?
        """
        result_tipo_dispositivo_id = self.execute_query(query_tipo_dispositivo_id, (result[0]))
        # Verificar si se encontró el ID del tipo de dispositivo
        if result_tipo_dispositivo_id:
            tipo_dispositivo_id = result_tipo_dispositivo_id[0]
            return tipo_dispositivo_id
            
        return None  # Retorna None si no se encontró el ID del tipo de dispositivo

    def get_acciones_permitidas(self, tipo_dispositivo_id):
        query = "SELECT acciones.nombre FROM acciones JOIN acciones_por_tipo ON acciones.id = acciones_por_tipo.accion_id WHERE acciones_por_tipo.tipo_dispositivo_id = ?"
        result = self.execute_query(query, (tipo_dispositivo_id,))
        print(result)
        return [accion[0].lower() for accion in result]
    
    def get_estado_por_accion(self, accion):
        query = "SELECT estado FROM acciones WHERE nombre = ?"
        result = self.execute_query(query, (accion,))
        return result[0] if result else None

    def actualizar_estado_dispositivo(self, dispositivo, accion, habitacion_id):
        query = "UPDATE dispositivos SET estado = ? WHERE nombre = ? AND habitacion_id = ?"
        self.execute_query(query, (accion, dispositivo, habitacion_id))
