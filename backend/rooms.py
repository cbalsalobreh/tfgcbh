import sqlite3

from database import get_tipo_id

def add_habitacion(nombre, tipo_nombre, usuario_id):
    tipo_id = get_tipo_id(tipo_nombre)
    if not tipo_id:
        print(f"No se encontró el ID para el tipo de habitación '{tipo_nombre}'")
        return
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO habitaciones (nombre, tipo_id) VALUES (?, ?)", (nombre, tipo_id))
        habitacion_id = cursor.lastrowid 
        cursor.execute("INSERT INTO usuarios_habitaciones (id_usuario, id_habitacion) VALUES (?, ?)", (usuario_id, habitacion_id))
        conn.commit()
    except sqlite3.Error as e:
        print("Error al agregar habitación:", e)
    finally:
        cursor.close()
        conn.close()

def get_habitaciones(usuario_id):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
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
    except sqlite3.Error as e:
        print("Error getting rooms:", e)
        return []
    finally:
        cursor.close()
        conn.close()

def update_habitacion(usuario_id, nombre_actual, nuevo_nombre):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT h.id 
            FROM habitaciones h
            JOIN usuarios_habitaciones uh ON h.id = uh.id_habitacion
            WHERE h.nombre = ? AND uh.id_usuario = ?
        """, (nombre_actual, usuario_id))
        habitacion_id = cursor.fetchone()
        print(f'Hab ID:', habitacion_id)
        
        if habitacion_id:
            cursor.execute("UPDATE habitaciones SET nombre = ? WHERE id = ?", (nuevo_nombre, habitacion_id[0]))
            conn.commit()
            return True
        else:
            return False
    except sqlite3.Error as e:
        print("Error updating room:", e)
        return False  # Ocurrió un error al actualizar el nombre
    finally:
        cursor.close()
        conn.close()

def delete_habitacion(nombre):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    try:
        # Iniciar una transacción
        conn.execute('BEGIN')

        # Obtener el id de la habitación a eliminar
        cursor.execute("SELECT id FROM habitaciones WHERE nombre = ?", (nombre,))
        habitacion_id = cursor.fetchone()

        if habitacion_id:
            # Eliminar dispositivos asociados a la habitación
            cursor.execute("DELETE FROM dispositivos WHERE habitacion_id = ?", (habitacion_id[0],))

            # Eliminar referencias en usuarios_habitaciones
            cursor.execute("DELETE FROM usuarios_habitaciones WHERE id_habitacion = ?", (habitacion_id[0],))

            # Eliminar la habitación
            cursor.execute("DELETE FROM habitaciones WHERE id = ?", (habitacion_id[0],))

            # Confirmar la transacción
            conn.commit()
        else:
            print("Habitación no encontrada.")
    except sqlite3.Error as e:
        print("Error deleting room:", e)
        conn.rollback()  # Revertir la transacción en caso de error
    finally:
        cursor.close()
        conn.close()

def add_dispositivo(nombre, tipo, habitacion_id):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    try:
        # Asegurarse de que la habitación existe
        cursor.execute("SELECT id FROM habitaciones WHERE id = ?", (habitacion_id,))
        if cursor.fetchone() is None:
            raise ValueError("Habitación no encontrada")

        # Insertar el nuevo dispositivo
        cursor.execute("INSERT INTO dispositivos (nombre, tipo, habitacion_id) VALUES (?, ?, ?)", 
                    (nombre, tipo, habitacion_id))
        conn.commit()
    except sqlite3.Error as e:
        print("Error adding device:", e)
    finally:
        cursor.close()
        conn.close()

def get_dispositivos_por_habitacion(habitacion_id):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, nombre, tipo, estado
            FROM dispositivos
            WHERE habitacion_id = ?
        """, (habitacion_id,))
        dispositivos = cursor.fetchall()
        return [{'id': d[0], 'nombre': d[1], 'tipo': d[2], 'estado': d[3]} for d in dispositivos]
    except sqlite3.Error as e:
        print("Error getting devices:", e)
        return []
    finally:
        cursor.close()
        conn.close()

def get_nombre_dispositivos_habitacion(hab_id):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT nombre FROM dispositivos WHERE habitacion_id = ?", (hab_id,))
        dispositivos = cursor.fetchall()
        return [dispositivo[0].lower() for dispositivo in dispositivos]
    except sqlite3.Error as e:
        print("Error getting devices:", e)
        return []
    finally:
        cursor.close()
        conn.close()

def eliminar_dispositivo(dispositivo_id):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM dispositivos WHERE id = ?", (dispositivo_id,))
        conn.commit()
    except sqlite3.Error as e:
        print("Error deleting device:", e)
    finally:
        cursor.close()
        conn.close()


def get_estado_dispositivo(dispositivo, habitacion):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    try:
        query = '''
        SELECT d.estado FROM dispositivos d
        JOIN habitaciones h ON d.habitacion_id = h.id
        WHERE d.nombre = ? AND h.nombre = ?
        '''
        cursor.execute(query, (dispositivo, habitacion))
        result = cursor.fetchone()
        return result[0] if result else None
    except sqlite3.Error as e:
        print("Error getting device status:", e)
        return None
    finally:
        cursor.close()
        conn.close()

def update_device_state(dispositivo, accion):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    try:
        # Actualizar el estado del dispositivo basado en la acción
        if accion:
            cursor.execute("UPDATE dispositivos SET estado = ? WHERE nombre = ?", (accion, dispositivo))
            conn.commit()
    except sqlite3.Error as e:
        print("Error updating device state:", e)
    finally:
        cursor.close()
        conn.close()
