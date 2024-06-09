from database import DatabaseManager
import spacy # type: ignore
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
        doc = self.nlp(text)
        habitacion_id = self.database_manager.get_id_habitacion(nombre_hab)
        dispositivos = self.database_manager.get_nombre_dispositivos_habitacion(habitacion_id)

        dispositivos = [unidecode(dispositivo.lower()) for dispositivo in dispositivos]
        print(f'Habitación ID: {habitacion_id}, Dispositivos: {dispositivos}')

        dispositivo = None
        accion = None

        # Generar n-gramas desde la transcripción por palabras
        words = [token.text.lower() for token in doc if not token.is_punct and not token.is_space]
        ngrams = [unidecode(' '.join(words[i:i+n])) for n in range(1, len(words)+1) for i in range(len(words)-n+1)]

        print(f'N-gramas generados: {ngrams}')

        # Buscar dispositivos en los n-gramas
        for ngram in ngrams:
            if ngram in dispositivos:
                dispositivo = ngram
                print(f'Dispositivo encontrado: {dispositivo}')
                break

        # Buscar comandos asociados al dispositivo
        if dispositivo:
            for token in doc:
                token_text = unidecode(token.text.lower())
                print(f'Analizando token: {token_text}')

        if dispositivo and accion:
            print(f'Dispositivo: {dispositivo}, Acción: {accion}')
            # Actualizar el estado del dispositivo en la base de datos
            self.database_manager.actualizar_estado_dispositivo(dispositivo, accion, habitacion_id)
            return dispositivo, accion

        print('No se encontró dispositivo o comando válido en la transcripción')
        return None, None
