import spacy
import numpy as np
from word2number import w2n
# load pre trained tokenization spanish model
# nlp = spacy.load("es_core_news_sm")

# load pre trained tokenization English model
# in command line
# python -m spacy download en_core_web_sm

nlp = spacy.load("en_core_web_sm")


def tag_subjects(sentence):
    doc = nlp(sentence)

    # Inicializa una lista para almacenar los nombres de materias encontrados
    subjects = []

    # Itera a través de los tokens en el documento procesado
    for token in doc:
        # Verifica si el token es un sustantivo propio (que a menudo se usa para nombres de materias)
        if token.pos_ == "PROPN":
            subjects.append(token.text)

    return subjects


# Carga el modelo de spaCy en inglés
nlp = spacy.load("en_core_web_sm")


def number_of_subjects(sentence):
    # Procesa el texto con spaCy
    doc = nlp(sentence)

    # Inicializa una variable para contar los números de exámenes
    anzahl = 0

    # Itera a través de los tokens en el documento
    for token in doc:
        if token.like_num:
            # Si el token parece ser un número, intenta convertirlo a entero
            try:
                anzahl += int(token.text)
            except ValueError:
                # Si no se puede convertir a entero, continúa con el siguiente token
                continue

    return anzahl


def preprocess_text(sentence):
    # Procesar el texto del usuario
    doc = nlp(sentence)

    # Inicializar una lista para almacenar los tokens
    tokens = []

    # Recorrer las palabras tokenizadas y agregarlas a la lista
    for token in doc:
        lemma = token.lemma_.lower()
        tokens.append(lemma)

    filtered_tokens = [token for token in tokens if not nlp(token)[0].is_punct]

    return filtered_tokens


def bag_of_words(tokenized_sentence, all_words):
    """
    return bag of words array:
    1 for each known word that exists in the sentence, 0 otherwise
    example:
    sentence = ["hello", "how", "are", "you"]
    words = ["hi", "hello", "I", "you", "bye", "thank", "cool"]
    bag   = [  0 ,    1 ,    0 ,   1 ,    0 ,    0 ,      0]
    """

    bag = np.zeros(len(all_words), dtype=np.float32)
    for idx, w in enumerate(all_words):
        if w in tokenized_sentence:
            bag[idx] = 1.0
    return bag
