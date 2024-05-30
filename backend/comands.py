import sqlite3

def add_command(comando, accion):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO comandos (comando, accion) VALUES (?, ?)", (comando, accion))
        conn.commit()
    except sqlite3.Error as e:
        print("Error adding command:", e)
    finally:
        cursor.close()
        conn.close()

def get_commands():
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM comandos")
        commands = cursor.fetchall()
        return commands
    except sqlite3.Error as e:
        print("Error getting commands:", e)
    finally:
        cursor.close()
        conn.close()

def get_accion_por_dispositivo(dispositivo):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT accion FROM comandos WHERE comando LIKE ?", ('%' + dispositivo + '%',))
        result = cursor.fetchone()
        return result[0] if result else None
    except sqlite3.Error as e:
        print("Error fetching command:", e)
        return None
    finally:
        cursor.close()
        conn.close()

def get_accion_por_comando(comando):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
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
        conn.close()

def obtener_participio(verbo):
    if verbo.endswith("ar"):
        return verbo[:-2] + "ado"
    elif verbo.endswith("er") or verbo.endswith("ir"):
        return verbo[:-2] + "ido"
    return verbo

def actualizar_estado_dispositivo(dispositivo, accion, habitacion_id):
    participio_accion = obtener_participio(accion)
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE dispositivos SET estado = ? WHERE nombre = ? AND habitacion_id = ?", (participio_accion, dispositivo, habitacion_id))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error updating device state:", e)
    finally:
        cursor.close()
        conn.close()
