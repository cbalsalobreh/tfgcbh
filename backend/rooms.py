import sqlite3

class RoomManager:
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

    def get_habitaciones(self, usuario_id):
        query = """
            SELECT h.id, h.nombre, th.nombre AS tipo
            FROM habitaciones h
            JOIN usuarios_habitaciones uh ON h.id = uh.id_habitacion
            JOIN tipos_habitaciones th ON h.tipo_id = th.id
            WHERE uh.id_usuario = ?
        """
        return self.execute_query(query, (usuario_id,))

    def get_tipo_id(self, tipo_nombre):
        query = "SELECT id FROM tipos_habitaciones WHERE nombre = ?"
        return self.execute_query(query, (tipo_nombre,))

    def add_habitacion(self, nombre, tipo_nombre, usuario_id):
        tipo_id = self.get_tipo_id(tipo_nombre)
        if not tipo_id:
            print(f"No se encontró el ID para el tipo de habitación '{tipo_nombre}'")
            return
        query_insert_habitacion = "INSERT INTO habitaciones (nombre, tipo_id) VALUES (?, ?)"
        query_insert_usuario_habitacion = "INSERT INTO usuarios_habitaciones (id_usuario, id_habitacion) VALUES (?, ?)"
        self.execute_query(query_insert_habitacion, (nombre, tipo_id))
        habitacion_id = self.conn.lastrowid
        self.execute_query(query_insert_usuario_habitacion, (usuario_id, habitacion_id))

    def delete_habitacion_id(self, id):
        query_dispositivos = "DELETE FROM dispositivos WHERE habitacion_id = ?"
        query_usuarios_habitaciones = "DELETE FROM usuarios_habitaciones WHERE id_habitacion = ?"
        query_habitaciones = "DELETE FROM habitaciones WHERE id = ?"
        self.execute_query(query_dispositivos, (id,))
        self.execute_query(query_usuarios_habitaciones, (id,))
        self.execute_query(query_habitaciones, (id,))

    def delete_habitacion(self, nombre):
        query = """
            SELECT id FROM habitaciones WHERE nombre = ?
        """
        habitacion_id = self.execute_query(query, (nombre,))
        if habitacion_id:
            self.delete_habitacion_id(habitacion_id[0][0])
        else:
            print("Habitación no encontrada.")

    def update_habitacion(self, usuario_id, nombre_actual, nuevo_nombre):
        query_select = """
            SELECT h.id 
            FROM habitaciones h
            JOIN usuarios_habitaciones uh ON h.id = uh.id_habitacion
            WHERE h.nombre = ? AND uh.id_usuario = ?
        """
        query_update = "UPDATE habitaciones SET nombre = ? WHERE id = ?"
        habitacion_id = self.execute_query(query_select, (nombre_actual, usuario_id))
        if habitacion_id:
            self.execute_query(query_update, (nuevo_nombre, habitacion_id[0][0]))
            return True
        else:
            return False

    def get_tipos_habitaciones(self):
        query = "SELECT id, nombre FROM tipos_habitaciones"
        result = self.execute_query(query)
        return [{'id': th[0], 'nombre': th[1]} for th in result]

    def get_dispositivos_predeterminados_por_tipo(self, tipo_id):
        query = "SELECT nombre FROM tipos_dispositivos WHERE tipo_habitacion_id = ?"
        result = self.execute_query(query, (tipo_id,))
        return [dispositivo[0] for dispositivo in result]

    def get_dispositivos_por_habitacion(self, habitacion_id):
        query = """
            SELECT id, nombre, tipo, estado
            FROM dispositivos
            WHERE habitacion_id = ?
        """
        result = self.execute_query(query, (habitacion_id,))
        return [{'id': d[0], 'nombre': d[1], 'tipo': d[2], 'estado': d[3]} for d in result]
