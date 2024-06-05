from datetime import timedelta
import re
from flask import Flask, jsonify, request, session
from flask_session import Session
from flask_socketio import SocketIO, emit, disconnect
import whisper
from flask_cors import CORS, cross_origin
import base64
import tempfile
from unidecode import unidecode # type: ignore
from flask_wtf.csrf import generate_csrf
from flask_jwt_extended import JWTManager, decode_token, jwt_required, create_access_token, get_jwt_identity, verify_jwt_in_request
from comands import CommandManager
from text_analysis import TextAnalyzer
from database import DatabaseManager
from rooms import RoomManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'  
app.config['SESSION_TYPE'] = 'filesystem'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key' 
Session(app)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app, resources={r"/*": {"origins": "*"}})
jwt = JWTManager(app)

audio_model = whisper.load_model("small")
print("Cargado whisper")

db_path = 'db/database.db'
db_manager = DatabaseManager(db_path)
room_manager = RoomManager(db_path)
command_manager = CommandManager('db/database.db')
text_analyzer = TextAnalyzer('db/database.db')

# Servidor WebSockets
@socketio.on('connect')
def handle_connect():
    try:
        csrf_token = request.args.get('csrf_token')
        if csrf_token == session.get('csrf_token'):
            print("Token CSRF válido")
        else:
            print("Token CSRF inválido")
            disconnect()
    except Exception as e:
        print("Error al manejar la conexión:", e)

def get_user_id_from_token(token):
    try:
        # Decodificar el token JWT para obtener la identidad del usuario
        decoded_token = decode_token(token)
        user_id = decoded_token['sub']  # El ID del usuario se encuentra en la clave 'sub' del token
        return user_id
    except Exception as e:
        print(f"Error al decodificar el token JWT: {e}")
        return None

def obtener_token_de_la_solicitud():
    # Obtener el token de autorización de la cabecera de la solicitud
    token = request.headers.get('Authorization')
    # Verificar si se proporcionó un token de autorización
    if token:
        token_parts = token.split()
        if len(token_parts) == 2:
            return token_parts[1]  # Devolver solo el token sin 'Bearer'
    return None  # Devolver None si no se proporcionó un token

@socketio.on('audio')
@jwt_required()
def handle_audio(audio_data):
    print("Audio recibido")
    try:
        token = obtener_token_de_la_solicitud()  
        usuario_id = get_user_id_from_token(token)
        print("USER ID:", usuario_id)
        audio_bytes = base64.b64decode(audio_data)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
            temp_audio_file.write(audio_bytes)
            temp_audio_file_path = temp_audio_file.name
        print("Audio guardado en archivo temporal:", temp_audio_file_path)

        audio = whisper.load_audio(temp_audio_file_path)
        print("Cargado audio en whisper")
        transcript = audio_model.transcribe(audio, language='es')
        text_transcription = transcript['text']
        texto_sin_comas = unidecode(re.sub(r'[^\w\s]', '', text_transcription))
        socketio.emit('transcription', texto_sin_comas)
        print("Transcripción emitida al cliente:", texto_sin_comas)

        habitacion, dispositivo = text_analyzer.analyze_text(texto_sin_comas, usuario_id)
        print('Texto analizado:', dispositivo, habitacion)
        if dispositivo and habitacion:
            estado = room_manager.get_estado_dispositivo(dispositivo, habitacion)
            if estado:
                socketio.emit('estado_dispositivo', {'dispositivo': dispositivo, 'estado': estado, 'habitacion': habitacion})
            else:
                socketio.emit('estado_dispositivo', {'dispositivo': dispositivo, 'estado': 'No encontrado', 'habitacion': habitacion})
        else:
            socketio.emit('estado_dispositivo', {'dispositivo': 'No encontrado', 'estado': 'No encontrado', 'habitacion': 'No encontrado'})

    except Exception as e:
        print(f"Error processing audio: {e}")

@socketio.on('audio_room')
def handle_audio(data):
    audio_data = data.get('audioData')
    nombre_hab = data.get('nombreHab')
    print("Audio recibido")
    try:
        audio_bytes = base64.b64decode(audio_data)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
            temp_audio_file.write(audio_bytes)
            temp_audio_file_path = temp_audio_file.name
        print("Audio guardado en archivo temporal:", temp_audio_file_path)

        audio = whisper.load_audio(temp_audio_file_path)
        print("Cargado audio en whisper")
        transcript = audio_model.transcribe(audio, language='es')
        text_transcription = transcript['text']
        texto_sin_comas = unidecode(re.sub(r'[^\w\s]', '', text_transcription))
        socketio.emit('transcription', texto_sin_comas)
        print("Transcripción emitida al cliente:", texto_sin_comas)

        dispositivo, nuevo_estado = text_analyzer.analyze_device(texto_sin_comas, nombre_hab)
        print(dispositivo, nuevo_estado)
        if dispositivo and nuevo_estado:
            if command_manager.actualizar_estado_dispositivo(dispositivo, nuevo_estado):
                print('Estado del dispositivo actualizado:', dispositivo, nuevo_estado)
                socketio.emit('actualizar_estado', {'dispositivo': dispositivo, 'nuevo_estado': nuevo_estado})
            else:
                print('Error al actualizar el estado del dispositivo:', dispositivo)
                socketio.emit('actualizar_estado', {'error': 'Error al actualizar el estado del dispositivo'})
        else:
            print('No se encontró dispositivo o comando válido en la transcripción')
            socketio.emit('actualizar_estado', {'error': 'No se encontró dispositivo o comando válido en la transcripción'})

    except Exception as e:
        print(f"Error processing audio: {e}")


# REST API Endpoints
@app.route('/')
def index():
    csrf_token = generate_csrf()
    session['csrf_token'] = csrf_token
    return jsonify({'csrf_token': csrf_token})

# Gestión de Autentificación
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    login_username = data.get('loginUsername')
    login_password = data.get('loginPassword')
    remember_me = data.get('rememberMe')

    if db_manager.check_credentials(login_username, login_password):
        usuario_id = db_manager.get_user_id(login_username)
        expires = timedelta(days=30) if remember_me else timedelta(minutes=15)
        access_token = create_access_token(identity=usuario_id, expires_delta=expires)
        return jsonify(token=access_token, user_id=usuario_id, redirect='/casa-domotica'), 200
    else:
        return jsonify({'message': 'Credenciales incorrectas'}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('registerUsername')
    email = data.get('registerEmail')
    password = data.get('registerPassword')
    db_manager.save_user_to_database(username, email, password)
    return jsonify({'message': 'Registro exitoso'}) 

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logout exitoso'})

@app.route('/change_password', methods=['POST'])
@jwt_required()
def change_password_route():
    data = request.json
    new_password = data.get('newPassword')
    user_id = get_jwt_identity()
    if user_id:
        db_manager.change_password(user_id, new_password)
        return jsonify({'message': 'Contraseña cambiada exitosamente'})
    else:
        return jsonify({'message': 'Usuario no autenticado'}), 401

# Gestión de usuario
@app.route('/casa-domotica', methods=['GET', 'POST'])
@jwt_required()
@cross_origin()
def manejar_habitaciones():
    try:
        usuario_id = get_jwt_identity()
        if request.method == 'POST':
            nombre = request.json.get('nombre')
            tipo = request.json.get('tipo')
            if not nombre or not tipo:
                return jsonify({'mensaje': 'Nombre y tipo de habitación son necesarios'}), 400
            room_manager.add_habitacion(nombre, tipo, usuario_id)
            return jsonify({'mensaje': 'Habitación añadida'})
        else:
            habitaciones = room_manager.get_habitaciones(usuario_id)
            return jsonify(habitaciones)
    except Exception as e:
        print(f"Error en /casa-domotica: {e}")
        return jsonify({'error': 'Ocurrió un error en el servidor.'}), 500

@app.route('/casa-domotica/<nombre>', methods=['GET', 'DELETE'])
@jwt_required()
@cross_origin()
def manejar_habitacion(nombre):
    usuario_id = get_jwt_identity()
    if request.method == 'DELETE':
        room_manager.delete_habitacion(nombre)
        return jsonify({'mensaje': 'Habitación eliminada'})
    else:
        habitaciones = room_manager.get_habitaciones(usuario_id)
        habitacion = next((h for h in habitaciones if h['nombre'] == nombre), None)
        if habitacion:
            dispositivos = room_manager.get_dispositivos_por_habitacion(habitacion['id'])
            return jsonify({'habitacion': habitacion, 'dispositivos': dispositivos})
        else:
            return jsonify({'mensaje': 'Habitación no encontrada'}), 404


@app.route('/<id_habitacion>', methods=['DELETE'])
def borrar_habitacion(id_habitacion):
    try:
        room_manager.delete_habitacion_id(id_habitacion)
        return jsonify({'mensaje': 'Habitación eliminada'}), 200
    except Exception as e:
        print("Error inesperado:", e)
        return jsonify({'error': 'Error inesperado'}), 500

        
@app.route('/casa-domotica/<nombre>', methods=['PUT'])
@jwt_required()
@cross_origin()
def cambiar_nombre_habitacion(nombre):
    try:
        usuario_id = get_jwt_identity()
        nuevo_nombre = request.json.get('nuevo_nombre')
        if not nuevo_nombre:
            return jsonify({'mensaje': 'El nuevo nombre de la habitación es necesario'}), 400
        if room_manager.update_habitacion(usuario_id, nombre, nuevo_nombre):
            return jsonify({'mensaje': f'Nombre de la habitación {nombre} cambiado a {nuevo_nombre}'}), 200
        else:
            return jsonify({'mensaje': 'No se pudo cambiar el nombre de la habitación. Verifique que tiene acceso a la habitación y que el nuevo nombre no esté ya en uso.'}), 400
    except Exception as e:
        return jsonify({'error': 'Ocurrió un error al cambiar el nombre de la habitación'}), 500
        
@app.route('/tipos-habitaciones', methods=['GET'])
def obtener_tipos_habitaciones():
    try:
        tipos_habitaciones = db_manager.get_tipos_habitaciones()
        if tipos_habitaciones is not None:
            return jsonify({'tipos_habitaciones': tipos_habitaciones}), 200
        else:
            return jsonify({'error': 'No se pudieron obtener los tipos de habitaciones'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tipos-habitaciones', methods=['POST'])
def agregar_tipo_habitacion():
    data = request.json
    nombre = data.get('nombre')
    try:
        nuevo_tipo_id = db_manager.add_tipo_habitacion(nombre)
        return jsonify({'id': nuevo_tipo_id, 'nombre': nombre}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tipos-habitaciones/<tipo_nombre>')
def obtener_tipo_habitacion(tipo_nombre):
    try:
        tipo_id = db_manager.get_tipo_id(tipo_nombre)
        if tipo_id:
            return jsonify({'tipo_id': tipo_id, 'tipo_nombre': tipo_nombre})
        else:
            return jsonify({'mensaje': 'Tipo de habitación no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': 'Ocurrió un error al obtener el tipo de habitación'}), 500
    
@app.route('/tipos-habitaciones/<nombre>/dispositivos', methods=['GET'])
def obtener_dispositivos_predeterminados(nombre):
    try:
        tipo_id = db_manager.get_tipo_id(nombre)
        if tipo_id is None:
            return jsonify({'error': 'Tipo de habitación no encontrado'}), 404
        
        dispositivos = db_manager.get_dispositivos_predeterminados_por_tipo(tipo_id)
        return jsonify({'dispositivos': dispositivos}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/get_user_data', methods=['GET'])
@jwt_required()
def get_username():
    user_id = get_jwt_identity()
    username = db_manager.get_username_with_id(user_id)
    if username:
        return jsonify({'username': username})
    else:
        return jsonify({'message': 'Usuario no encontrado'}), 404

@app.route('/usuario/<username>', methods=['GET'])
@jwt_required()
@cross_origin()
def get_user_data(username):
    user_data = db_manager.get_user_data(username)
    if user_data:
        return jsonify(user_data)
    else:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    
# Gestión de dispositivos
@app.route('/casa-domotica/<nombre>/dispositivos', methods=['POST'])
@jwt_required()
@cross_origin()
def manejar_dispositivos(nombre):
    usuario_id = get_jwt_identity()
    habitacion = next((h for h in room_manager.get_habitaciones(usuario_id) if h['nombre'] == nombre), None)
    if not habitacion:
        return jsonify({'mensaje': 'Habitación no encontrada'}), 404
    nombre_dispositivo = request.json.get('nombre')
    tipo_dispositivo = request.json.get('tipo')
    if not nombre_dispositivo or not tipo_dispositivo:
        return jsonify({'mensaje': 'Nombre y tipo del dispositivo son necesarios'}), 400
    room_manager.add_dispositivo(nombre_dispositivo, tipo_dispositivo, habitacion['id'])
    return jsonify({'mensaje': 'Dispositivo añadido'}), 201

@app.route('/casa-domotica/<nombre>/dispositivos/<dispositivo_id>', methods=['DELETE'])
@jwt_required()
@cross_origin()
def eliminar_dispositivo_ruta(nombre, dispositivo_id):
    room_manager.eliminar_dispositivo(dispositivo_id)
    return jsonify({'mensaje': 'Dispositivo eliminado'}), 200

@app.route('/casa-domotica/<nombre_habitacion>/dispositivos/<dispositivo_id>', methods=['PUT'])
@jwt_required()
def actualizar_nombre_dispositivo(nombre_habitacion, dispositivo_id):
    try:
        usuario_id = get_jwt_identity()
        nuevo_nombre = request.json.get('nuevo_nombre')
        if not nuevo_nombre:
            return jsonify({'mensaje': 'El nuevo nombre del dispositivo es necesario'}), 400
        if room_manager.actualizar_nombre_dispositivo(usuario_id, nombre_habitacion, dispositivo_id, nuevo_nombre):
            return jsonify({'mensaje': f'Nombre del dispositivo actualizado correctamente a {nuevo_nombre}'}), 200
        else:
            return jsonify({'mensaje': 'No se pudo actualizar el nombre del dispositivo. Verifique que tiene acceso al dispositivo y que el nuevo nombre no esté ya en uso.'}), 400
    except Exception as e:
        return jsonify({'error': 'Ocurrió un error al actualizar el nombre del dispositivo'}), 500

@app.route('/casa-domotica/<nombre>/dispositivos/estado', methods=['PUT'])
@jwt_required()
@cross_origin()
def actualizar_estado(nombre):
    data = request.json
    dispositivo_id = data.get('dispositivo')
    nuevo_estado = data.get('nuevo_estado')

    if not dispositivo_id or not nuevo_estado:
        return jsonify({"error": "Datos incompletos"}), 400

    try:
        if command_manager.actualizar_estado_dispositivo(dispositivo_id, nuevo_estado):
            socketio.emit('actualizar_estado', {'dispositivoId': dispositivo_id, 'nuevoEstado': nuevo_estado})
            return jsonify({"message": "Estado actualizado correctamente"}), 200
        else:
            return jsonify({"error": "Error al actualizar el estado"}), 500
    except Exception as e:
        print(f"Error inesperado: {e}")
        return jsonify({"error": "Error inesperado"}), 500

# Gestión de comandos
@app.route('/casa-domotica/comandos/<int:dispositivo_id>', methods=['GET'])
@jwt_required()
def get_commandos_dispositivo(dispositivo_id):
    comandos = command_manager.get_commands(dispositivo_id)
    if comandos:
        return jsonify({'comandos': [comando[0] for comando in comandos]})
    else:
        return jsonify({'comandos': []})

@app.route('/casa-domotica/<tipo_dispositivo>/comando', methods=['POST'])
def manejar_comando(tipo_dispositivo):
    comando = request.json.get('comando')
    accion = command_manager.add_command(tipo_dispositivo, comando)
    if accion:
        return jsonify({'accion': accion})
    else:
        return jsonify({'error': 'Comando no encontrado'}), 404

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)
