from rooms import get_nombre_dispositivos_habitacion
from comands import actualizar_estado_dispositivo, get_accion_por_comando
from database import get_dispositivos_por_usuario, get_habitaciones_por_usuario, get_id_habitacion, get_user_id
import spacy # type: ignore
from unidecode import unidecode # type: ignore

# Carga el modelo de idioma en español de spaCy
nlp = spacy.load('es_core_news_sm')

def analyze_text(text, user_id):
    # Procesa el texto con spaCy
    doc = nlp(text)
    
    # Palabras clave para dispositivos y habitaciones
    habitaciones = get_habitaciones_por_usuario(user_id)
    dispositivos = get_dispositivos_por_usuario(user_id)
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

def analyze_device(text, nombre_hab):
    doc = nlp(text)
    habitacion_id = get_id_habitacion(nombre_hab)
    dispositivos = get_nombre_dispositivos_habitacion(habitacion_id)
    
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
        accion = get_accion_por_comando(comando)
        print(f'Acción encontrada: {accion}')
        actualizar_estado_dispositivo(dispositivo, accion, habitacion_id)
        return dispositivo, accion

    return dispositivo, None


