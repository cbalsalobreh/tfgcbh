import sqlite3
from utils import get_base_verb

class CommandManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def add_command(self, id, comando):
        conn = self._connect()
        cursor = conn.cursor()
        try:
            # Obtener el ID del tipo de dispositivo
            cursor.execute("SELECT tipo FROM dispositivos WHERE id = ?", (id,))
            tipo = cursor.fetchone()
            if not tipo:
                print(f"No se encontró el tipo para el ID de dispositivo '{id}'")
                return False

            # Verificar si el comando ya existe en la tabla comandos
            cursor.execute("SELECT id, accion FROM comandos WHERE comando = ?", (comando,))
            row = cursor.fetchone()
            if row:
                comando = row[0]
                accion = row[1]
            else:
                # Obtener la acción del comando (el primer verbo en el comando)
                accion = comando.split()[0]
                accion = get_base_verb(comando)
                # Insertar el nuevo comando en la tabla comandos
                cursor.execute("INSERT INTO comandos (comando, accion) VALUES (?, ?)", (comando, accion))
                id = cursor.lastrowid

            # Insertar el comando para el tipo de dispositivo
            print(tipo[0], id)
            cursor.execute("INSERT INTO tipos_dispositivos_comandos (tipo, id_comando) VALUES (?, ?)", (tipo[0], id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print("Error adding command to device type:", e)
            return False
        finally:
            cursor.close()
            conn.close()

    def get_commands(self, dispositivo_id):
        self.conn = self._connect()
        cursor = self.conn.cursor()
        try:
            # Obtener el tipo de dispositivo
            cursor.execute("SELECT tipo FROM dispositivos WHERE id = ?", (dispositivo_id,))
            dispositivo = cursor.fetchone()
            if not dispositivo:
                return []
            tipo = dispositivo[0]
            
            # Obtener los comandos asociados al tipo de dispositivo
            cursor.execute("""
                SELECT c.comando
                FROM comandos c
                INNER JOIN tipos_dispositivos_comandos tdc ON c.id = tdc.id_comando
                WHERE tdc.tipo = ?
            """, (tipo,))
            commands = cursor.fetchall()
            return commands
        except sqlite3.Error as e:
            print("Error getting commands:", e)
            return []
        finally:
            cursor.close()
            self.conn.close()

    def get_accion_por_dispositivo(self, dispositivo):
        self.conn = self._connect()
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT accion FROM comandos WHERE comando LIKE ?", ('%' + dispositivo + '%',))
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print("Error fetching command:", e)
            return None
        finally:
            cursor.close()
            self.conn.close()

    def get_accion_por_comando(self, comando):
        self.conn = self._connect()
        cursor = self.conn.cursor()
        try:
            comando = comando.lower().strip()
            cursor.execute("SELECT accion FROM comandos WHERE comando = ?", (comando,))
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print("Error fetching command:", e)
            return None
        finally:
            cursor.close()
            self.conn.close()

    def obtener_participio(self, verbo):
        if verbo.endswith("ar"):
            return verbo[:-2] + "ado"
        elif verbo.endswith("er") or verbo.endswith("ir"):
            return verbo[:-2] + "ido"
        return verbo

    def actualizar_estado_dispositivo(self, dispositivo, accion, habitacion_id):
        if habitacion_id is None:
            pass
        participio_accion = self.obtener_participio(accion)
        self.conn = self._connect()
        cursor = self.conn.cursor()
        try:
            cursor.execute("UPDATE dispositivos SET estado = ? WHERE nombre = ? AND habitacion_id = ?", 
                        (participio_accion, dispositivo, habitacion_id))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error updating device state:", e)
            pass
        finally:
            cursor.close()
            self.conn.close()

    def actualizar_estado_electrodomestico_temperatura(self, dispositivo, estado, habitacion_id):
        self.conn = self._connect()
        cursor = self.conn.cursor()
        try:
            cursor.execute("UPDATE dispositivos SET estado = ? WHERE nombre = ? AND habitacion_id = ?", 
                        (estado, dispositivo, habitacion_id))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error updating device state:", e)
        finally:
            cursor.close()
            self.conn.close()
