import sqlite3

class DatabaseManager:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = None

    def execute_query(self, query, parameters=[]):
        try:
            self.conn = sqlite3.connect(self.db_file)
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


    def save_user_to_database(self, username, email, password):
        query = 'INSERT INTO users (username, email, password) VALUES (?, ?, ?)'
        self.execute_query(query, (username, email, password))

    def check_credentials(self, username, password):
        query = "SELECT * FROM users WHERE username = ? AND password = ?"
        result = self.execute_query(query, (username, password))
        return bool(result)

    def get_user_data(self, username):
        query = "SELECT * FROM users WHERE username = ?"
        return self.execute_query(query, (username,))

    def get_user_id(self, username):
        query = "SELECT id FROM users WHERE username = ?"
        result = self.execute_query(query, (username,))
        return result[0][0] if result else None
    
    def get_username_with_id(self, user_id):
        query = "SELECT username FROM users WHERE id = ?"
        result = self.execute_query(query, (user_id,))
        return result[0][0] if result else None


    def change_password(self, user_id, new_password):
        query = "UPDATE users SET password = ? WHERE id = ?"
        self.execute_query(query, (new_password, user_id))

    def get_tipo_id(self, tipo_nombre):
        query = "SELECT id FROM tipos_habitaciones WHERE nombre = ?"
        result = self.execute_query(query, (tipo_nombre,))
        return result[0][0] if result else None

    def get_id_habitacion(self, habitacion):
        query = "SELECT id FROM habitaciones WHERE nombre = ?"
        result = self.execute_query(query, (habitacion,))
        return result[0][0] if result else None

    def add_tipo_habitacion(self, nombre):
        query = "INSERT INTO tipos_habitaciones (nombre) VALUES (?)"
        self.execute_query(query, (nombre,))
        return self.execute_query("SELECT last_insert_rowid()")[0][0]

    def get_tipos_habitaciones(self):
        query = "SELECT id, nombre FROM tipos_habitaciones"
        result = self.execute_query(query)
        return [{'id': th[0], 'nombre': th[1]} for th in result]

    def get_dispositivos_predeterminados_por_tipo(self, tipo_id):
        query = "SELECT nombre FROM tipos_dispositivos WHERE tipo_habitacion_id = ?"
        result = self.execute_query(query, (tipo_id,))
        return [dispositivo[0] for dispositivo in result]

    def get_habitaciones_por_usuario(self, user_id):
        query = """
            SELECT h.nombre 
            FROM habitaciones h
            JOIN usuarios_habitaciones uh ON h.id = uh.id_habitacion
            WHERE uh.id_usuario = ?
        """
        result = self.execute_query(query, (user_id,))
        return [habitacion[0].lower() for habitacion in result]

    def get_dispositivos_por_usuario(self, user_id):
        query = """
            SELECT d.nombre 
            FROM dispositivos d
            JOIN habitaciones h ON d.habitacion_id = h.id
            JOIN usuarios_habitaciones uh ON h.id = uh.id_habitacion
            WHERE uh.id_usuario = ?
        """
        result = self.execute_query(query, (user_id,))
        return [dispositivo[0].lower() for dispositivo in result]
