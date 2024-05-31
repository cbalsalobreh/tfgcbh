from rooms import RoomManager
from comands import CommandManager
from database import DatabaseManager
import spacy # type: ignore
from unidecode import unidecode # type: ignore

class TextAnalyzer:
    def __init__(self, db_path):
        self.db_path = db_path
        self.room_manager = RoomManager(db_path)
        self.command_manager = CommandManager(db_path)
        self.database_manager = DatabaseManager(db_path)
        self.nlp = spacy.load('es_core_news_sm')

    def analyze_text(self, text, user_id):
        doc = self.nlp(text)

        # Palabras clave para dispositivos y habitaciones
        habitaciones = self.database_manager.get_habitaciones_por_usuario(user_id)
        dispositivos = self.database_manager.get_dispositivos_por_usuario(user_id)
        print(f'Habitaciones: {habitaciones}, Dispositivos: {dispositivos}')
        habitaciones = [unidecode(habitacion.lower()) for habitacion in habitaciones]
        dispositivos = [unidecode(dispositivo.lower()) for dispositivo in dispositivos]
        print(f'Habitaciones: {habitaciones}, Dispositivos: {dispositivos}')

        # Inicializa las variables para el dispositivo y la habitación
        habitacion = None
        dispositivo = None

        # Función para generar n-gramas del texto
        def generate_ngrams(text, n):
            words = text.split()
            ngrams = []
            for i in range(len(words) - n + 1):
                ngrams.append(' '.join(words[i:i + n]))
            return ngrams

        # Generar n-gramas del texto (hasta 3-gramas)
        ngrams = []
        for n in range(1, 4):
            ngrams.extend(generate_ngrams(text, n))
        ngrams = [unidecode(ngram.lower()) for ngram in ngrams]
        print(f'N-gramas generados: {ngrams}')

        # Busca dispositivos y habitaciones en los n-gramas
        for ngram in ngrams:
            if ngram in dispositivos and dispositivo is None:
                dispositivo = ngram
            if ngram in habitaciones and habitacion is None:
                habitacion = ngram

        return habitacion, dispositivo

    def analyze_device(self, text, nombre_hab):
        doc = self.nlp(text)
        habitacion_id = self.database_manager.get_id_habitacion(nombre_hab)
        dispositivos = self.room_manager.get_nombre_dispositivos_habitacion(habitacion_id)

        dispositivos = [unidecode(dispositivo.lower()) for dispositivo in dispositivos]
        print(f'Habitación ID: {habitacion_id}, Dispositivos: {dispositivos}')

        dispositivo = None
        comando = None

        for token in doc:
            token_text = unidecode(token.text.lower())
            print(f'Analizando token: {token_text}')
            if token_text in dispositivos:
                dispositivo = token_text
                comando = unidecode(text.lower())
                break

        print(f'Dispositivo encontrado: {dispositivo}, Comando encontrado: {comando}') 

        if dispositivo and comando:
            accion = self.command_manager.get_accion_por_comando(comando)
            print(f'Acción encontrada: {accion}')
            self.command_manager.actualizar_estado_dispositivo(dispositivo, accion, habitacion_id)
            return dispositivo, accion

        return dispositivo, None
