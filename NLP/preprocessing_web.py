import spacy
import numpy as np
import re
from datetime import datetime
from word2number import w2n
from NLP import soft_constraints_util as scu
from NLP import chat as c
# load pre trained tokenization spanish model
# nlp = spacy.load("es_core_news_sm")

# load pre trained tokenization English model
# in command line
# python -m spacy download en_core_web_sm

# Carga el modelo de spaCy en inglés
nlp = spacy.load("en_core_web_sm")


def test_spacy(sentence):
    doc = nlp(sentence)
    for token in doc:
        print(
            f"Token: {token.text}, POS: {token.pos_}, Etiqueta: {token.tag_},Entity: {token.ent_type_}")


def tag_date(sentence):
    doc = nlp(sentence)

    date_list = []
    current_date = ""

    for ent in doc.ents:
        if ent.label_ == "DATE":
            # hotfix fow when "days" comes into the input
            if "day" in ent.text.lower():
                today = datetime.now()
                current_date = today.strftime("%b %d %Y")

            else:
                current_date = ent.text

            for token in ent:
                if token.pos_ == "ADP":
                    current_date = current_date.replace(token.text, ", ")
                elif token.pos_ == "CCONJ":
                    current_date = current_date.replace(
                        token.text, ", ")
            current_date_range = current_date.split(", ")
            if len(current_date_range) > 1:
                current_date_range = [date.strip()
                                      for date in current_date_range]
                date_list.append(current_date_range)
            else:
                date_list.append(current_date_range[0].strip())

    if date_list == []:
        c.send_output(
            "Sorry I didn't get the date...\n can you please write like this: January 4th?")
        new_str = c.await_for_message()
        return tag_date(new_str)
    else:
        return date_list
# NO OLVIDAR usar extract_dates() de soft_constraints_util al final para transformar todo en formato datetime


def tag_time(text):
    # Regular expression to find hours and minutes in various formats
    time_pattern = r"(\d{1,2}(?::\d{2})?(?: ?[APap][Mm])?)"

    # Regular expression to find ranges of hours
    range_pattern = rf"{time_pattern}\s*(?:to|–|-)\s*{time_pattern}"

    # Find all matches of hours and ranges of hours in the text
    time_matches = re.findall(time_pattern, text)
    range_matches = re.findall(range_pattern, text)

    # Initialize a list to store hours in time format
    hours = []

    # Process matches of ranges of hours
    for match in range_matches:
        start_time, end_time = match

        # Convert to 24-hour format if necessary
        if "pm" in end_time.lower() and not "pm" in start_time.lower():
            start_time = convert_to_24_hour_format(start_time)
        if "am" in end_time.lower() and not "am" in start_time.lower():
            start_time = convert_to_24_hour_format(start_time)

        # Create time objects for the hours and add them to the list
        start_time_obj = create_time_from_time(start_time)
        end_time_obj = create_time_from_time(end_time)
        hours.append(f"{start_time_obj} - {end_time_obj}")

    # Process matches of individual hours
    for match in time_matches:
        # Create a time object for the hour and add it to the list
        time_obj = create_time_from_time(match)
        hours.append(time_obj)

    return hours


def convert_to_24_hour_format(time_str):
    # Función para convertir a formato de 24 horas
    if "pm" in time_str.lower() and ":" in time_str:
        hour, minute = map(int, time_str.replace("pm", "").split(":"))
        if hour != 12:
            hour += 12
        return f"{hour:02}:{minute:02}"
    elif "am" in time_str.lower() and ":" in time_str:
        hour, minute = map(int, time_str.replace("am", "").split(":"))
        if hour == 12:
            hour = 0
        return f"{hour:02}:{minute:02}"
    else:
        return time_str


def create_time_from_time(time_str):
    # Función para crear un objeto time a partir de una hora en formato de 12 horas
    if ":" in time_str:
        return datetime.strptime(time_str, "%I:%M %p").time()
    else:
        return datetime.strptime(time_str, "%I %p").time()


def tag_subjects(sentence):
    doc = nlp(sentence)

    # Inicializa una lista para almacenar los nombres de materias encontrados
    subjects = []

    # Itera a través de los tokens en el documento procesado

    for token in doc:
        # print(f"Token: {token.text}, POS: {token.pos_}, Etiqueta: {token.tag_}")
        # Verifica si el token es un sustantivo propio (que a menudo se usa para nombres de materias)
        if token.pos_ == "PROPN" or token.pos_ == "NOUN":
            # It appends the token with a Capitalized letter
            subjects.append(token.text.title())

    return subjects


def number_from_text(sentence):
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
                # Si no se puede convertir a entero, verifica si es una palabra numérica y conviértela
                try:
                    anzahl += w2n.word_to_num(token.text)
                except ValueError:
                    # Si no se puede convertir, continúa con el siguiente token
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
