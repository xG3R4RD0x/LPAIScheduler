import spacy

# Cargar el modelo de spaCy en tu idioma
# Cambia "es_core_news_sm" por el modelo de tu idioma
nlp = spacy.load("es_core_news_sm")

# Función para analizar el input del usuario


def analizar_input(input_text):
    # Procesar el texto del usuario
    doc = nlp(input_text)

    # Recorrer las palabras tokenizadas y obtener información
    for token in doc:
        print(
            f"Palabra: {token.text}, Etiqueta POS: {token.pos_}, Etiqueta de dependencia: {token.dep_}")


# Input del usuario
usuario_input = "Quiero reservar una mesa para dos personas en un restaurante cercano."

# Llamar a la función para analizar el input
analizar_input(usuario_input)
