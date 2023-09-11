import spacy
# load pre trained tokenization spanish model
nlp = spacy.load("es_core_news_sm")


def preprocess_text(sentence):
    # Procesar el texto del usuario
    doc = nlp(sentence)

    # Inicializar una lista para almacenar los tokens
    tokens = []

    # Recorrer las palabras tokenizadas y agregarlas a la lista
    for token in doc:
        lemma = token.lemma_.lower()
        tokens.append(lemma)

    return tokens


def bag_of_words(tokenized_sentence, all_words):
    pass


a = "hola, me gusta comer pan"
print(a)
a = preprocess_text(a)
print(a)
