import sqlite3

class CommandManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def add_command(self, comando, accion):
        self.conn = self._connect()
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO comandos (comando, accion) VALUES (?, ?)", (comando, accion))
            self.conn.commit()
        except sqlite3.Error as e:
            print("Error adding command:", e)
        finally:
            cursor.close()
            self.conn.close()

    def get_commands(self):
        self.conn = self._connect()
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT * FROM comandos")
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
        participio_accion = self.obtener_participio(accion)
        self.conn = self._connect()
        cursor = self.conn.cursor()
        try:
            cursor.execute("UPDATE dispositivos SET estado = ? WHERE nombre = ? AND habitacion_id = ?", 
                        (participio_accion, dispositivo, habitacion_id))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error updating device state:", e)
        finally:
            cursor.close()
            self.conn.close()
