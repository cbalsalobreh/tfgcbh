import sqlite3
import json

# Helper functions for database operations
def save_user_to_database(username, email, password):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, password))
        conn.commit()
    except sqlite3.Error as e:
        print("Error saving user to database:", e)
    finally:
        cursor.close()
        conn.close()

def check_credentials(username, password):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user and user[3] == password:
            return True
        return False
    except sqlite3.Error as e:
        print("Error checking credentials:", e)
        return False
    finally:
        cursor.close()
        conn.close()

def get_user_data(username):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user_data = cursor.fetchall()
        column_names = [column[0] for column in cursor.description]
        user_data_dict = [dict(zip(column_names, row)) for row in user_data]
        user_data_json = json.dumps(user_data_dict, indent=4, separators=(',', ': '))
        return user_data_json
    except sqlite3.Error as e:
        print("Error getting user data:", e)
        return None
    finally:
        cursor.close()
        conn.close()

def get_user_id(username):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        return user[0] if user else None
    except sqlite3.Error as e:
        print("Error getting user ID:", e)
        return None
    finally:
        cursor.close()
        conn.close()

def change_password(username, new_password):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
        conn.commit()
    except sqlite3.Error as e:
        print("Error changing password:", e)
    finally:
        cursor.close()
        conn.close()

def get_tipo_id(tipo_nombre):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM tipos_habitaciones WHERE nombre = ?", (tipo_nombre,))
        result = cursor.fetchone()
        return result[0] if result else None
    except sqlite3.Error as e:
        print("Error getting room type ID:", e)
        return None
    finally:
        cursor.close()
        conn.close()

def get_id_habitacion(habitacion):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM habitaciones WHERE nombre = ?", (habitacion,))
        result = cursor.fetchone()
        return result[0] if result else None
    except sqlite3.Error as e:
        print("Error getting room type ID:", e)
        return None
    finally:
        cursor.close()
        conn.close()

def add_tipo_habitacion(nombre):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO tipos_habitaciones (nombre) VALUES (?)", (nombre,))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print("Error adding room type:", e)
        raise e
    finally:
        cursor.close()
        conn.close()

def get_tipos_habitaciones():
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, nombre FROM tipos_habitaciones")
        tipos_habitaciones = cursor.fetchall()
        return [{'id': th[0], 'nombre': th[1]} for th in tipos_habitaciones]
    except sqlite3.Error as e:
        print("Error getting room types:", e)
        return []
    finally:
        cursor.close()
        conn.close()

def get_dispositivos_predeterminados_por_tipo(tipo_id):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT nombre FROM tipos_dispositivos WHERE tipo_habitacion_id = ?", (tipo_id,))
        dispositivos = cursor.fetchall()
        return [dispositivo[0] for dispositivo in dispositivos]
    except sqlite3.Error as e:
        print(f"Error getting default devices:", e)
        return []
    finally:
        cursor.close()
        conn.close()

def get_habitaciones_por_usuario(user_id):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    try:
        # Consulta que une las tablas habitaciones y usuarios_habitaciones
        cursor.execute("""
            SELECT h.nombre 
            FROM habitaciones h
            JOIN usuarios_habitaciones uh ON h.id = uh.id_habitacion
            WHERE uh.id_usuario = ?
        """, (user_id,))
        habitaciones = cursor.fetchall()
        return [habitacion[0].lower() for habitacion in habitaciones]
    except sqlite3.Error as e:
        print("Error getting rooms for user:", e)
        return []
    finally:
        cursor.close()
        conn.close()

def get_dispositivos_por_usuario(user_id):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    try:
        # Consulta que une las tablas usuarios_habitaciones, habitaciones y dispositivos
        cursor.execute("""
            SELECT d.nombre 
            FROM dispositivos d
            JOIN habitaciones h ON d.habitacion_id = h.id
            JOIN usuarios_habitaciones uh ON h.id = uh.id_habitacion
            WHERE uh.id_usuario = ?
        """, (user_id,))
        dispositivos = cursor.fetchall()
        return [dispositivo[0].lower() for dispositivo in dispositivos]
    except sqlite3.Error as e:
        print("Error getting devices for user:", e)
        return []
    finally:
        cursor.close()
        conn.close()