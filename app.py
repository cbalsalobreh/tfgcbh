
from datetime import timedelta
import re
import ssl
from flask import Flask, jsonify, request, send_from_directory, session
from flask_session import Session
from flask_socketio import SocketIO, disconnect
import whisper
from flask_cors import CORS, cross_origin
from flask_ngrok import run_with_ngrok
import base64
import tempfile
from unidecode import unidecode
from flask_wtf.csrf import generate_csrf
from flask_jwt_extended import JWTManager, decode_token, jwt_required, create_access_token, get_jwt_identity, verify_jwt_in_request
from backend.devices import DeviceManager
from backend.text_analysis import TextAnalyzer
from backend.database import DatabaseManager
from backend.rooms import RoomManager

app = Flask(__name__, static_url_path='', static_folder='client/build')
app.config['SECRET_KEY'] = 'secret!'  
app.config['SESSION_TYPE'] = 'filesystem'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

# Configuración de CORS para toda la aplicación
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Configuración de Flask-SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuración de JWT
jwt = JWTManager(app)

# Configuración de Flask-Session
Session(app)

run_with_ngrok(app) 

ssl._create_default_https_context = ssl._create_unverified_context

audio_model = whisper.load_model("small")
print("Cargado whisper")

db_path = 'backend/db/database.db'
db_manager = DatabaseManager(db_path)
room_manager = RoomManager(db_path)
device_manager = DeviceManager(db_path)
text_analyzer = TextAnalyzer(db_path)

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
    try:
        token = obtener_token_de_la_solicitud()
        usuario_id = get_user_id_from_token(token)
        audio_bytes = base64.b64decode(audio_data)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
            temp_audio_file.write(audio_bytes)
            temp_audio_file_path = temp_audio_file.name
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
            estado = db_manager.get_estado_dispositivo(dispositivo, habitacion)
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
    try:
        audio_bytes = base64.b64decode(audio_data)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
            temp_audio_file.write(audio_bytes)
            temp_audio_file_path = temp_audio_file.name
        audio = whisper.load_audio(temp_audio_file_path)
        print("Cargado audio en whisper")
        transcript = audio_model.transcribe(audio, language='es')
        text_transcription = transcript['text']
        texto_limpio = re.sub(r'[^\w\sñÑ]', '', text_transcription)
        socketio.emit('transcription', texto_limpio)
        print("Transcripción emitida al cliente:", texto_limpio)

        dispositivo, nuevo_estado = text_analyzer.analyze_device(texto_limpio, nombre_hab)
        print(dispositivo, nuevo_estado)
        if dispositivo and nuevo_estado:
                print('Estado del dispositivo actualizado:', dispositivo, nuevo_estado)
                socketio.emit('actualizar_estado', {'dispositivo': dispositivo, 'nuevo_estado': nuevo_estado})
        else:
            print('No se encontró dispositivo o comando válido en la transcripción')
            socketio.emit('actualizar_estado', {'error': 'No se encontró dispositivo o comando válido en la transcripción'})
    
    except Exception as e:
        print(f"Error processing audio: {e}")


# REST API Endpoints
@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')

@app.route("/<path:path>", defaults={'path':''})
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

@app.route('/csrf-token', methods=['GET'])
def index():
    try:
        csrf_token = generate_csrf()
        session['csrf_token'] = csrf_token
        return jsonify({'csrf_token': csrf_token}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/tipos-habitaciones', methods=['GET'])
def obtener_tipos_habitaciones():
    try:
        tipos_habitaciones = room_manager.get_tipos_habitaciones()
        if tipos_habitaciones is not None:
            return jsonify({'tipos_habitaciones': tipos_habitaciones}), 200
        else:
            return jsonify({'error': 'No se pudieron obtener los tipos de habitaciones'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/tipos-habitaciones/<nombre>/dispositivos', methods=['GET'])
def obtener_dispositivos_predeterminados(nombre):
    try:
        tipo_id = room_manager.get_tipo_id(nombre)
        if tipo_id is None:
            return jsonify({'error': 'Tipo de habitación no encontrado'}), 404
        dispositivos = room_manager.get_dispositivos_predeterminados_por_tipo(tipo_id)
        return jsonify({'dispositivos': dispositivos}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Gestión de Autentificación
@app.route('/login', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def login():
    try:
        if request.method == 'POST':
            data = request.json
            username = data.get('username')
            password = data.get('password')
            remember_me = data.get('rememberMe')
            redirect_url = f'/usuarios/{username}/habitaciones'
            if db_manager.check_credentials(username, password):
                usuario_id = db_manager.get_user_id(username)
                expires = timedelta(days=30) if remember_me else timedelta(minutes=60)
                access_token = create_access_token(identity=usuario_id, expires_delta=expires)
                return jsonify(token=access_token, user_id=usuario_id, redirect=redirect_url), 200
            else:
                return jsonify({'error': 'Credenciales incorrectas'}), 401
        else:
            return jsonify({'error': 'Método no aceptado'}), 405
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/register', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def register():
    try:
        if request.method == 'POST':
            data = request.json
            username = data.get('registerUsername')
            email = data.get('registerEmail')
            password = data.get('registerPassword')
            db_manager.save_user_to_database(username, email, password)
            return jsonify({'mensaje': 'Registro exitoso'}), 200
        else:
            return jsonify({'error': 'Método no aceptado'}), 405
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def logout():
    try:
        if request.method == 'DELETE':
            session.clear()
            return jsonify({'mensaje': 'Logout exitoso'}), 200
        else:
            return jsonify({'error': 'Método no aceptado'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Gestión de usuario

@app.route('/usuarios/<username>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@jwt_required()
@cross_origin()
def get_user_data(username):
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({'error': 'Usuario no encontrado'}), 401
        if request.method == 'GET':
            if not username:
                return jsonify({'error': 'Usuarrio no encontrado'}), 404
            user_data = db_manager.get_user_data(username)
            if user_data:
                return jsonify(user_data), 200
        else:
            return jsonify({'error': 'Método no aceptado'}), 405
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/usuario/<username>/password', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@jwt_required()
def change_password_route():
    try:
        if request.method == 'PATCH':
            data = request.json
            new_password = data.get('newPassword')
            usuario_id = get_jwt_identity()
            if not usuario_id:
                return jsonify({'error': 'Usuario no encontrado'}), 401
            if usuario_id:
                db_manager.change_password(usuario_id, new_password)
                return jsonify({'mensaje': 'Contraseña cambiada exitosamente'}), 200
        else:
            return jsonify({'error': 'Método no aceptado'}), 405    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Gestión de habitaciones
@app.route('/usuarios/<username>/habitaciones', methods=['GET', 'POST', 'DELETE', 'PUT', 'PATCH'])
@jwt_required()
@cross_origin()
def manejar_habitaciones(username):
    try:
        usuario_id = get_jwt_identity()
        if not username or not usuario_id:
            return jsonify({'error': 'Usuario no encontrado'}), 401
        if request.method == 'GET':
            habitaciones = room_manager.get_habitaciones(usuario_id)
            return jsonify({'habitaciones': habitaciones}), 200
        if request.method == 'POST':
            nombre = request.json.get('nombre')
            tipo = request.json.get('tipo')
            if not nombre or not tipo:
                return jsonify({'error': 'Nombre y tipo de habitación son necesarios'}), 400
            room_manager.add_habitacion(nombre, tipo, usuario_id)
            return jsonify({'mensaje': 'Habitación añadida'}, nombre, tipo), 200
        else:
            return jsonify({'error': 'Método no aceptado'}), 405
    except Exception as e:
        return jsonify({'error': 'Ocurrió un error {e} en el servidor.'}), 500

@app.route('/usuarios/<username>/habitaciones/<nombre>', methods=['GET', 'POST', 'DELETE', 'PUT', 'PATCH'])
@jwt_required()
@cross_origin()
def manejar_habitacion(username, nombre):
    try:
        usuario_id = get_jwt_identity()
        if not usuario_id or not username:
            return jsonify({'error': 'Usuario no encontrado'}), 401
        if request.method == 'PATCH':
            nuevo_nombre = request.json.get('nuevo_nombre')
            if not nuevo_nombre:
                return jsonify({'error': 'El nuevo nombre de la habitación es necesario'}), 400
            if room_manager.update_habitacion(usuario_id, nombre, nuevo_nombre):
                return jsonify({'mensaje': f'Nombre de la habitación {nombre} cambiado a {nuevo_nombre}'}), 201
            else:
                return jsonify({'error': 'No se pudo cambiar el nombre de la habitación.'}), 401
        if request.method == 'DELETE':
            room_manager.delete_habitacion(nombre)
            return jsonify({'mensaje': 'Habitación eliminada'}), 200
        else:
            return jsonify({'error': 'Método no aceptado'}), 405
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Gestión de dispositivos
@app.route('/usuarios/<username>/habitaciones/<nombre>/dispositivos', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@jwt_required()
@cross_origin()
def manejar_dispositivos(username, nombre):
    try:
        usuario_id = get_jwt_identity()
        if not usuario_id or not username:
            return jsonify({'error': 'Usuario no encontrado'}), 401
        if not nombre:
            return jsonify({'error': 'Habitación no encontrada'}), 404
        if request.method == 'GET':
            habitaciones = room_manager.get_habitaciones(usuario_id)
            habitacion = next((h for h in habitaciones if h[1] == nombre), None)
            if habitacion:
                dispositivos = room_manager.get_dispositivos_por_habitacion(habitacion[0])
                return jsonify({'habitacion': habitacion, 'dispositivos': dispositivos}), 200
            else:
                return jsonify({'error': 'Habitación no encontrada'}), 404
        elif request.method == 'POST':
            habitacion = next((h for h in room_manager.get_habitaciones(usuario_id) if h[1] == nombre), None)
            if not habitacion:
                return jsonify({'error': 'Habitación no encontrada'}), 404
            nombre = request.json.get('nombre')
            tipo = request.json.get('tipo')
            if not nombre or not tipo:
                return jsonify({'error': 'Nombre y tipo del dispositivo son necesarios'}), 400
            device_manager.add_dispositivo(nombre, tipo, habitacion[0])
            return jsonify({'mensaje': 'Dispositivo añadido'}, nombre), 200
        else:
            return jsonify({'error': 'Método no aceptado'}), 405
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/usuarios/<username>/habitaciones/<nombre>/dispositivos/<dispositivo_id>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@jwt_required()
@cross_origin()
def manejar_dispositivo(username, nombre, dispositivo_id):
    try:
        usuario_id = get_jwt_identity()
        if not usuario_id or not username:
            return jsonify({'error': 'Usuario no encontrado'}), 401
        if request.method == 'DELETE':
            device_manager.eliminar_dispositivo(dispositivo_id)
            return jsonify({'mensaje': 'Dispositivo eliminado'}), 200
        elif request.method == 'PATCH':
            nuevo_nombre = request.json.get('nuevo_nombre')
            if not nuevo_nombre:
                return jsonify({'error': 'El nuevo nombre del dispositivo es necesario'}), 400
            if device_manager.actualizar_nombre_dispositivo(usuario_id, nombre, dispositivo_id, nuevo_nombre):
                return jsonify({'mensaje': f'Nombre del dispositivo actualizado correctamente a {nuevo_nombre}'}), 201
            else:
                return jsonify({'error': 'No se pudo actualizar el nombre del dispositivo.'}), 401
        else:
            return jsonify({'error': 'Método no aceptado'}), 405
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    socketio.run(app, port=5001)
