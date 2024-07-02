import re
from backend.database import DatabaseManager
import spacy
from unidecode import unidecode

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

        dispositivos = [dispositivo.lower() for dispositivo in dispositivos]
        print(f'Habitación ID: {habitacion_id}, Dispositivos: {dispositivos}')

        dispositivo = None
        accion = None
        estado = None

        tokens = [token.text.lower() for token in doc]

        for i in range(len(tokens)):
            for j in range(i + 1, len(tokens) + 1):
                possible_device = ' '.join(tokens[i:j])
                if possible_device in dispositivos:
                    dispositivo = possible_device
                    break
            if dispositivo:
                break
        
        if dispositivo:
            dispositivo_id = self.database_manager.get_tipo_dispositivo_id(dispositivo)
            dispositivo_id_int = dispositivo_id[0]
            acciones_por_dispositivo = self.database_manager.get_acciones_permitidas(dispositivo_id_int)

            for i in range(len(tokens)):
                for j in range(i + 1, len(tokens) + 1):
                    accion_posible = ' '.join(tokens[i:j])
                    if accion_posible in acciones_por_dispositivo:
                        accion = accion_posible
                        break
                if accion:
                    break

        if dispositivo and accion:
            # Detección de números en el texto usando spaCy
            numeros_detectados = [token.text for token in doc if token.pos_ == 'NUM']
            # Para subir y bajar persiana o sacar toldo
            if "subir" in accion and "persiana" in dispositivo or "bajar" in accion and "persiana" in dispositivo or "sacar" in accion:
                if "mitad" in text:
                    estado = "abierto a la mitad"
                elif numeros_detectados:
                    estado = f"abierto al {numeros_detectados[0]}%"
                elif "subir" in accion and "persiana" in dispositivo:
                    estado = "abierta"
                elif "bajar" in accion and "persiana" in dispositivo:
                    estado = "cerrada"
                elif "sacar" in accion:
                    estado = "abierto"
                else:
                    estado = None
            # Para controles de temperatura, nevera y congelador
            elif "regular" in accion or "establecer" in accion or "ajustar" in accion:
                if "grados" in text:
                    estado = re.search(r'\d+ grados', text).group()
                elif numeros_detectados:
                    estado = f"{numeros_detectados[0]}"
                else:
                    estado = None
            # Para lo demás
            else:
                estado = self.database_manager.get_estado_por_accion(accion)[0]
            
            print(f'Dispositivo encontrado: {dispositivo}, Estado: {estado}, Acción: {accion}')
            self.database_manager.actualizar_estado_dispositivo(dispositivo, estado, habitacion_id)            
            return dispositivo, estado

        print(f'Dispositivo o acción no encontrado. Dispositivo: {dispositivo}, Acción: {accion}')
        return None, None