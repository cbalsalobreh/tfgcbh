import spacy # type: ignore
from unidecode import unidecode # type: ignore

def get_base_verb(text):
    # Lista de verbos irregulares y sus formas base
    irregular_verbs = {
        'enciende': 'encender',
    }
    # Dividir el texto en palabras
    words = text.split()
    # Tomar la primera palabra
    first_word = words[0]    
    # Verificar si el verbo está en la lista de verbos irregulares
    if first_word in irregular_verbs:
        return irregular_verbs[first_word]
    # Si el verbo no es irregular, utilizar Spacy
    nlp = spacy.load('es_core_news_sm')
    doc = nlp(text)
    verb_lemma = None
    for token in doc:
        if token.pos_ == 'VERB':
            verb_lemma = token.lemma_
            break
    return verb_lemma