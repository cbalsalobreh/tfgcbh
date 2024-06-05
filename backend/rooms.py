import sqlite3
from database import DatabaseManager

class RoomManager:
    def __init__(self, db_file):
        self.db_file = db_file
        self.db_manager = DatabaseManager(db_file)
        self.conn = None

    def add_habitacion(self, nombre, tipo_nombre, usuario_id):
        self.conn = sqlite3.connect(self.db_file)
        tipo_id = self.db_manager.get_tipo_id(tipo_nombre)
        if not tipo_id:
            print(f"No se encontró el ID para el tipo de habitación '{tipo_nombre}'")
            return
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO habitaciones (nombre, tipo_id) VALUES (?, ?)", (nombre, tipo_id))
            habitacion_id = cursor.lastrowid 
            cursor.execute("INSERT INTO usuarios_habitaciones (id_usuario, id_habitacion) VALUES (?, ?)", (usuario_id, habitacion_id))
            self.conn.commit()
        except Exception as e:
            print("Error al agregar habitación:", e)
        finally:
            cursor.close()

    def get_habitaciones(self, usuario_id):
        self.conn = sqlite3.connect(self.db_file)
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT h.id, h.nombre, th.nombre AS tipo
                FROM habitaciones h
                JOIN usuarios_habitaciones uh ON h.id = uh.id_habitacion
                JOIN tipos_habitaciones th ON h.tipo_id = th.id
                WHERE uh.id_usuario = ?
            """, (usuario_id,))
            habitaciones = cursor.fetchall()
            return [{'id': h[0], 'nombre': h[1], 'tipo': h[2]} for h in habitaciones]
        except Exception as e:
            print("Error getting rooms:", e)
            return []
        finally:
            cursor.close()
    
    def delete_habitacion_id(self, id):
        self.conn = sqlite3.connect(self.db_file)
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM dispositivos WHERE habitacion_id = ?", (id,))
            cursor.execute("DELETE FROM usuarios_habitaciones WHERE id_habitacion = ?", (id,))
            cursor.execute("DELETE FROM habitaciones WHERE id = ?", (id,))
            self.conn.commit()
        except Exception as e:
            print("Error deleting room:", e)
            self.conn.rollback()
        finally:
            cursor.close()

    def update_habitacion(self, usuario_id, nombre_actual, nuevo_nombre):
        self.conn = sqlite3.connect(self.db_file)
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT h.id 
                FROM habitaciones h
                JOIN usuarios_habitaciones uh ON h.id = uh.id_habitacion
                WHERE h.nombre = ? AND uh.id_usuario = ?
            """, (nombre_actual, usuario_id))
            habitacion_id = cursor.fetchone()
            
            if habitacion_id:
                cursor.execute("UPDATE habitaciones SET nombre = ? WHERE id = ?", (nuevo_nombre, habitacion_id[0]))
                self.conn.commit()
                return True
            else:
                return False
        except Exception as e:
            print("Error updating room:", e)
            return False
        finally:
            cursor.close()

    def delete_habitacion(self, nombre):
        self.conn = sqlite3.connect(self.db_file)
        cursor = self.conn.cursor()
        try:
            self.conn.execute('BEGIN')
            cursor.execute("SELECT id FROM habitaciones WHERE nombre = ?", (nombre,))
            habitacion_id = cursor.fetchone()

            if habitacion_id:
                cursor.execute("DELETE FROM dispositivos WHERE habitacion_id = ?", (habitacion_id[0],))
                cursor.execute("DELETE FROM usuarios_habitaciones WHERE id_habitacion = ?", (habitacion_id[0],))
                cursor.execute("DELETE FROM habitaciones WHERE id = ?", (habitacion_id[0],))
                self.conn.commit()
            else:
                print("Habitación no encontrada.")
        except Exception as e:
            print("Error deleting room:", e)
            self.conn.rollback()
        finally:
            cursor.close()

    def add_dispositivo(self, nombre, tipo, habitacion_id):
        self.conn = sqlite3.connect(self.db_file)
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT id FROM habitaciones WHERE id = ?", (habitacion_id,))
            if cursor.fetchone() is None:
                raise ValueError("Habitación no encontrada")
            cursor.execute("INSERT INTO dispositivos (nombre, tipo, habitacion_id) VALUES (?, ?, ?)", 
                        (nombre, tipo, habitacion_id))
            self.conn.commit()
        except Exception as e:
            print("Error adding device:", e)
        finally:
            cursor.close()

    def get_dispositivos_por_habitacion(self, habitacion_id):
        self.conn = sqlite3.connect(self.db_file)
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT id, nombre, tipo, estado
                FROM dispositivos
                WHERE habitacion_id = ?
            """, (habitacion_id,))
            dispositivos = cursor.fetchall()
            return [{'id': d[0], 'nombre': d[1], 'tipo': d[2], 'estado': d[3]} for d in dispositivos]
        except Exception as e:
            print("Error getting devices:", e)
            return []
        finally:
            cursor.close()

    def get_nombre_dispositivos_habitacion(self, hab_id):
        self.conn = sqlite3.connect(self.db_file)
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT nombre FROM dispositivos WHERE habitacion_id = ?", (hab_id,))
            dispositivos = cursor.fetchall()
            return [dispositivo[0].lower() for dispositivo in dispositivos]
        except Exception as e:
            print("Error getting devices:", e)
            return []
        finally:
            cursor.close()

    def actualizar_nombre_dispositivo(self, usuario_id, nombre_habitacion, dispositivo_id, nuevo_nombre):
        self.conn = sqlite3.connect(self.db_file)
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT d.id
                FROM dispositivos d
                JOIN habitaciones h ON d.habitacion_id = h.id
                JOIN usuarios_habitaciones uh ON h.id = uh.id_habitacion
                WHERE d.id = ? AND h.nombre = ? AND uh.id_usuario = ?
            """, (dispositivo_id, nombre_habitacion, usuario_id))
            dispositivo_existente = cursor.fetchone()
            if dispositivo_existente:
                cursor.execute("UPDATE dispositivos SET nombre = ? WHERE id = ?", (nuevo_nombre, dispositivo_id))
                self.conn.commit()
                return True
            else:
                return False
        except Exception as e:
            print("Error updating device name:", e)
            return False
        finally:
            cursor.close()

    def eliminar_dispositivo(self, dispositivo_id):
        self.conn = sqlite3.connect(self.db_file)
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM dispositivos WHERE id = ?", (dispositivo_id,))
            self.conn.commit()
        except Exception as e:
            print("Error deleting device:", e)
        finally:
            cursor.close()

    def get_estado_dispositivo(self, dispositivo, habitacion):
        self.conn = sqlite3.connect(self.db_file)
        cursor = self.conn.cursor()
        try:
            query = '''
            SELECT d.estado FROM dispositivos d
            JOIN habitaciones h ON d.habitacion_id = h.id
            WHERE d.nombre = ? AND h.nombre = ?
            '''
            cursor.execute(query, (dispositivo, habitacion))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print("Error getting device status:", e)
            return None
        finally:
            cursor.close()
