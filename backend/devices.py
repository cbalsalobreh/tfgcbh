import sqlite3

class DeviceManager:
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

    def _connect(self):
        return sqlite3.connect(self.db_file)
    
    def add_dispositivo(self, nombre, tipo, habitacion_id):
        query_insert = "INSERT INTO dispositivos (nombre, tipo, habitacion_id) VALUES (?, ?, ?)"
        try:
            self.execute_query(query_insert, (nombre, tipo, habitacion_id))
        except Exception as e:
            print("Error adding device:", e)
        finally:
            if self.conn:
                self.conn.close()
    
    def actualizar_nombre_dispositivo(self, usuario_id, nombre_habitacion, dispositivo_id, nuevo_nombre):
        query_select = """
            SELECT d.id
            FROM dispositivos d
            JOIN habitaciones h ON d.habitacion_id = h.id
            WHERE d.id = ? AND h.nombre = ? AND h.usuario_id = ?
        """
        query_update = "UPDATE dispositivos SET nombre = ? WHERE id = ?"
        try:
            dispositivo_existente = self.execute_query(query_select, (dispositivo_id, nombre_habitacion, usuario_id))
            if dispositivo_existente:
                self.execute_query(query_update, (nuevo_nombre, dispositivo_id))
                return True
            else:
                return False
        except Exception as e:
            print("Error updating device name:", e)
            return False
        finally:
            if self.conn:
                self.conn.close()

    def eliminar_dispositivo(self, dispositivo_id):
        query_delete = "DELETE FROM dispositivos WHERE id = ?"
        try:
            self.execute_query(query_delete, (dispositivo_id,))
        except Exception as e:
            print("Error deleting device:", e)
