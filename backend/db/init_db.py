import sqlite3

# Initialize the database and create tables
def init_db():
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()

    # Users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        email TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL)''')

    # Comandos table
    cursor.execute('''CREATE TABLE IF NOT EXISTS comandos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        comando TEXT NOT NULL,
                        accion TEXT NOT NULL)''')

    # Habitaciones table
    cursor.execute('''CREATE TABLE IF NOT EXISTS habitaciones (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT NOT NULL UNIQUE,
                        tipo_id INTEGER NOT NULL,
                        FOREIGN KEY (tipo_id) REFERENCES tipos_habitaciones(id))''')

    # Dispositivos table
    cursor.execute('''CREATE TABLE IF NOT EXISTS dispositivos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT NOT NULL UNIQUE,
                        tipo TEXT NOT NULL,
                        habitacion_id INTEGER,
                        estado TEXT,
                        FOREIGN KEY (habitacion_id) REFERENCES habitaciones(id))''')

    # Relationship between users and habitaciones (many-to-many)
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios_habitaciones (
                        id_usuario INTEGER,
                        id_habitacion INTEGER,
                        PRIMARY KEY (id_usuario, id_habitacion),
                        FOREIGN KEY (id_usuario) REFERENCES users(id),
                        FOREIGN KEY (id_habitacion) REFERENCES habitaciones(id))''')

    # Relationship between habitaciones and dispositivos (one-to-many)
    # Already captured in dispositivos table with habitacion_id as foreign key

    # Relationship between dispositivos and comandos (many-to-many)
    cursor.execute('''CREATE TABLE IF NOT EXISTS dispositivos_comandos (
                        id_dispositivo INTEGER,
                        id_comando INTEGER,
                        PRIMARY KEY (id_dispositivo, id_comando),
                        FOREIGN KEY (id_dispositivo) REFERENCES dispositivos(id),
                        FOREIGN KEY (id_comando) REFERENCES comandos(id))''')
    
    cursor.execute('''CREATE TABLE tipos_habitaciones (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT NOT NULL UNIQUE''')
    
    cursor.execute('''CREATE TABLE tipos_dispositivos (    
                        id INTEGER PRIMARY KEY,    
                        nombre TEXT NOT NULL,    
                        tipo_habitacion_id INTEGER,    
                        FOREIGN KEY (tipo_habitacion_id) REFERENCES tipos_habitaciones(id))''')
    conn.commit()
    conn.close()

def insert_default_data():
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()

    # Insert default habitaciones
    habitaciones = [
        ('cuarto', 'cuarto'),
        ('baño', 'baño'),
        ('habitacion principal', 'habitacion principal'),
        ('jardin', 'jardin'),
        ('salon', 'salon'),
        ('sala de estar', 'sala de estar'),
        ('cocina', 'cocina')
    ]

    cursor.executemany('INSERT OR IGNORE INTO habitaciones (nombre, tipo) VALUES (?, ?)', habitaciones)
    
    # Get habitaciones ids
    cursor.execute('SELECT id, nombre FROM habitaciones')
    habitaciones_dict = {row[1]: row[0] for row in cursor.fetchall()}
    
    # Insert default dispositivos
    dispositivos = [
        ('luz', 'luz', habitaciones_dict['cuarto']),
        ('lampara', 'lampara', habitaciones_dict['cuarto']),
        ('television', 'television', habitaciones_dict['cuarto']),
        ('reproductor de musica', 'reproductor de musica', habitaciones_dict['cuarto']),
        ('persiana', 'persiana', habitaciones_dict['cuarto']),
        
        ('luz', 'luz', habitaciones_dict['baño']),
        ('ducha', 'ducha', habitaciones_dict['baño']),
        ('bañera', 'bañera', habitaciones_dict['baño']),
        
        ('luz', 'luz', habitaciones_dict['habitacion principal']),
        ('lampara', 'lampara', habitaciones_dict['habitacion principal']),
        ('television', 'television', habitaciones_dict['habitacion principal']),
        ('alarma', 'alarma', habitaciones_dict['habitacion principal']),
        ('persiana', 'persiana', habitaciones_dict['habitacion principal']),
        
        ('riego', 'riego', habitaciones_dict['jardin']),
        ('toldo', 'toldo', habitaciones_dict['jardin']),
        
        ('luz', 'luz', habitaciones_dict['salon']),
        ('lampara', 'lampara', habitaciones_dict['salon']),
        ('television', 'television', habitaciones_dict['salon']),
        ('reproductor de musica', 'reproductor de musica', habitaciones_dict['salon']),
        ('persiana', 'persiana', habitaciones_dict['salon']),
        
        ('luz', 'luz', habitaciones_dict['sala de estar']),
        ('control de temperatura', 'control de temperatura', habitaciones_dict['sala de estar']),
        
        ('luz', 'luz', habitaciones_dict['cocina']),
        ('control de temperatura', 'control de temperatura', habitaciones_dict['cocina']),
        ('nevera', 'nevera', habitaciones_dict['cocina']),
        ('congelador', 'congelador', habitaciones_dict['cocina']),
        ('lavadora', 'lavadora', habitaciones_dict['cocina']),
        ('secadora', 'secadora', habitaciones_dict['cocina']),
    ]

    cursor.executemany('INSERT OR IGNORE INTO dispositivos (nombre, tipo, habitacion_id) VALUES (?, ?, ?)', dispositivos)

    # Insert default comandos
    comandos = [
        ('apagar luz', 'apagar'),
        ('encender luz', 'encender'),
        ('apagar lampara', 'apagar'),
        ('encender lampara', 'encender'),
        ('apagar television', 'apagar'),
        ('encender television', 'encender'),
        ('activar ducha', 'activar'),
        ('desactivar ducha', 'desactivar'),
        ('activar bañera', 'activar'),
        ('desactivar bañera', 'desactivar'),
        ('activar riego', 'activar'),
        ('desactivar riego', 'desactivar'),
        
        ('temperatura nevera', 'temperatura'),
        ('temperatura congelador', 'temperatura'),
        ('temperatura calefaccion', 'temperatura'),
        ('temperatura aire acondicionado', 'temperatura'),
        ('temperatura lavadora', 'temperatura'),
        ('temperatura secadora', 'temperatura'),
        
        ('sacar toldo', 'sacar'),
        ('echar toldo', 'echar'),
        ('recoger toldo', 'recoger'),
        
        ('bajar persiana', 'bajar'),
        ('subir persiana', 'subir')
    ]

    cursor.executemany('INSERT OR IGNORE INTO comandos (comando, accion) VALUES (?, ?)', comandos)

    conn.commit()
    conn.close()

init_db()
insert_default_data()