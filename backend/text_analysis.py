from database import DatabaseManager
import spacy # type: ignore
from utils import obtener_participio
from unidecode import unidecode # type: ignore

class TextAnalyzer:
    def __init__(self, db_path):
        self.db_path = db_path
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
        acciones_comunes = ["encender", "apagar", "subir", "bajar", "echar", "recoger", "sacar", "reproducir", "poner"]
        
        doc = self.nlp(text)
        habitacion_id = self.database_manager.get_id_habitacion(nombre_hab)
        dispositivos = self.database_manager.get_nombre_dispositivos_habitacion(habitacion_id)

        dispositivos = [unidecode(dispositivo.lower()) for dispositivo in dispositivos]
        print(f'Habitación ID: {habitacion_id}, Dispositivos: {dispositivos}')

        dispositivo = None
        accion = None
        estado = None

        tokens = [unidecode(token.text.lower()) for token in doc]

        for i in range(len(tokens)):
            for j in range(i + 1, len(tokens) + 1):
                possible_device = ' '.join(tokens[i:j])
                if possible_device in dispositivos:
                    dispositivo = possible_device
                    break
            if dispositivo:
                break
        
        if dispositivo:
            for token in tokens:
                if token in acciones_comunes:
                    accion = token
                    break

        if dispositivo and accion:
            accion_start_index = text.lower().find(accion)
            dispositivo_start_index = text.lower().find(dispositivo)
            print(f'acción empieza en: {accion_start_index}, dispositivo empieza en: {dispositivo_start_index}')
            if dispositivo_start_index != -1 and accion_start_index != -1:
                if dispositivo_start_index > accion_start_index:
                    estado = text[dispositivo_start_index + len(dispositivo):].strip()
                else:
                    estado = text[accion_start_index + len(accion):].strip()

            print(f'Dispositivo encontrado: {dispositivo}, Estado: {estado}, Acción: {accion}')
            if not estado:
                accion_participio = obtener_participio(accion)
                self.database_manager.actualizar_estado_dispositivo(dispositivo, accion_participio, habitacion_id)
            else:
                self.database_manager.actualizar_estado_dispositivo(dispositivo, estado, habitacion_id)
            
            return dispositivo, estado or accion_participio

        print(f'Dispositivo o acción no encontrado. Dispositivo: {dispositivo}, Acción: {accion}')
        return None, None





