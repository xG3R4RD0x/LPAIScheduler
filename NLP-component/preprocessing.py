import spacy
import numpy as np
# load pre trained tokenization spanish model
# nlp = spacy.load("es_core_news_sm")

# load pre trained tokenization English model
nlp = spacy.load("en_core_web_sm")


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
