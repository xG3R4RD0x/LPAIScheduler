# contexts represents the context of the last input of the user
# This is the context Hierarchy, I use this to give a direction to the conversation
# For Example If I start with Subject, then I have to go to Name and then Unit
# after Unit comes Unit Time and I have to check if there are any more subjects
# if there are more subjects then I go back to Name and keep filling the subjects
# if not then I go back to main to fill the rest of the problem Data

import random
import torch
import json
from model import NeuralNet
from problem_data import ProblemData as pd
import preprocessing as pre
import data_util as du
from subject import Subject

# TODO estructurar el chatbot workflow haciendo un arbol de decisiones
# tiene que entrar en un estado diferente por cada rama del arbol

# ------pesudo code---
#
# if "new_context" is in (following_context_list):
#       do: guardar contexto//este es el estado del chatbot
#           if context_guardado == Complete || ok || back: //el escape del contexto actual al Main
#               mandar a que se validen los datos
#               if datos validos is True:
#                   print(mensaje de perfecto,)
#                   return problem_data //confirma los datos y manda a hacer el horario
#               else:
#                   generar respuesta con missing_fields
#           else: //si es un contexto normal
#               hacer un handler que haga lo que tiene que hacer según el contexto
#
#
#
#
#
# TODO ver como hago para que edite las cosas
#
#
#
#
# model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('./NLP-component/intents.json', 'r') as f:
    intents = json.load(f)

FILE = "./NLP-component/data.pth"
data = torch.load(FILE)
input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size_intent = data["output_size_intent"]
output_size_constraint = data["output_size_constraint"]
all_words = data["all_words"]
tags = data["tags"]
# Agrega esto para cargar los tipos de restricción
constraint_types = data["constraint_types"]
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size_intent,
                  output_size_constraint).to(device)
model.load_state_dict(model_state)
model.eval()


# model


hierarchy = [
    {
        "context": "Back_to_Main", "subcontext": ["Confirmation", "Denial"]
    },
    {
        "context": "Main", "subcontext": ["Main", "Subject"]
    },
    {
        "context": "Main-total_time", "subcontext": ["Main", "Subject"]
    },
    {
        "context": "Main-Hour_Duration", "subcontext": ["Main", "Subject"]
    },
    {
        "context": "Main-Unavailable_Hours", "subcontext": ["Main", "Subject"]
    },
    {
        "context": "Main-Unavailable_Days", "subcontext": ["Main", "Subject"]
    },
    {
        "context": "Subject", "subcontext": ["Name"]
    },
    {
        "context": "Name", "subcontext": ["Unit"]
    },
    {
        "context": "Unit", "subcontext": ["UTime"]
    },
    {
        "context": "UTime", "subcontext": ["Unit", "Main"]
    },
    {
        "context": "Confirmation", "subcontext": ["Main", "UTime", "Unit"]
    },
    {
        "context": "Denial", "subcontext": ["Main", "UTime", "Unit"]
    },
    {
        "context": "Edit", "subcontext": ["Back_to_Main", "UTime", "Unit"]
    }
]


response_options = [
    "We are doing great so far! \n But I still need you to tell me {checked_fields} before we can go on",
    "Awesome! \n But I still need you to tell me {checked_fields} before we can go on",
    "Thanks for the info! \n But I still need {checked_fields} to be able to do your plan :) ",
    "To proceed, I still need you to give me {checked_fields}",
    "We're making progress! However, I still require {checked_fields} before we can proceed.",
    "We are going great so far but I still need you to provide {checked_fields} before we can continue.",
    "Thank you for the information! Nevertheless, I still need {checked_fields} to proceed with your plan.",
    "To move forward, I still need you to add {checked_fields}."
]

field_names = {
    "start_date": "the start date",
    "end_date": "the end date",
    "number_of_subjects": "the number of subjects",
    "subjects": "the subjects",
    "total_time": "the total study time",
    "hours_per_day": "the number of study hours per day",
    "duration_of_hour": "the duration of each study hour",
    "no_study_days": "the days you don't want to study",
    "no_study_hours": "the hours you prefer not to study",
    "number_of_units": "the number of units",
    "hours_per_unit": "the average number of hours you need for each unit"
}


# check if the input is inside the context rules


def check_context(current_context, new_context):
    for c in hierarchy:
        if current_context == c["context"]:
            if new_context in c["subcontext"]:
                return True
            else:
                # checks if the new context string is in one of the string of the subcontexts
                # with this I can allow individual subject-contexts to run
                for sc in c["subcontext"]:
                    if sc in new_context:
                        return True
                return False

    return False


def generate_response(missing_fields):
    if missing_fields is True:
        # insert a response that says that everything is correctly filled

        sentence = input(
            "It looks like I got all the information I need, do you want to add or change anything?")
        input = input_sentence(sentence)
        if input["intent_tag"] is "Confirmation":

            return "everything is fine"
        else:
            if input["intent_tag"] is "Denial":
                response = "Perfect! I will start working on your study plan right away!"
                return response
    if missing_fields is False:
        return "Error with Problem Data"

    if type(missing_fields) is list:
        checked_fields = read_missing_fields(missing_fields)
        checked_fields_str = ""
        # makes a String with all the checked fields
        for field in checked_fields:
            if type(field) is dict:
                # checks the dictionary
                if "subjects" in field:
                    checked_fields_str = checked_fields_str[:-2]
                    checked_fields_str += " and in the Subjects: \n"
                    # iterates through the subject_list
                    for subjects in field["subjects"]:
                        for sub in subjects:
                            checked_fields_str += sub
            else:
                checked_fields_str += field

        # tengo que hacer checked_fields un string

        response = random.choice(response_options)
        response = response.replace("{checked_fields}", checked_fields_str)

        return response


def generate_response_individual_subject(subject_context, ProblemData):
    words = subject_context.split(' ')
    subject_from_context = words[1]
    subject_list_missing_fields = pd.validate_subjects(ProblemData)
    subject_from_list = None
    subject_missing_fields = ""
    for s in subject_list_missing_fields:
        if subject_from_context in s:
            subject_from_list = s
            break
    if subject_from_list is not None:
        for field in subject_from_list:
            if field in field_names:
                # this changes the name to the one in field names to make it more readable
                f = "-" + field_names.get(field) + "\n"
                subject_missing_fields = subject_missing_fields+f
        response = "To keep developing your plan I still need you to give some information about the subject: {subject_from_context}\n Please add: \n{subject_missing_fields}"
        response = response.replace(
            "{subject_from_context}", subject_from_context)
        response = response.replace(
            "{subject_missing_fields}", subject_missing_fields)
        return response

    else:
        response = "Do you want to do any changes to the subject: {subject_from_context}?"
        response = response.replace(
            "{subject_from_context}", subject_from_context)
        return response


# read_missing_fields has to return a list with better written missing fields just to print
def read_missing_fields(missing_fields):

    checked_fields = []
    for field in missing_fields:
        if type(field) is dict:
            if "subjects" in field:
                subjects = field["subjects"]
                subjects_temp = []
                for subject in subjects:
                    print(subject)
                    course_temp = []
                    for subject_field in subject:
                        if subject_field in field_names:
                            new_sub_field = field_names.get(subject_field)
                            course_temp.append("-"+new_sub_field+"\n")
                        else:
                            # the name of the subject is going to be added to the list here
                            course_temp.append(subject_field+": \n")
                    # add the subject to the subject_list
                    subjects_temp.append(course_temp)
                # add the list with the subjects to the main list as a dictionary subject: list
                checked_fields.append({"subjects": subjects_temp})

        else:
            field_temp = field_names.get(field)
            checked_fields.append(field_temp+", ")

    return checked_fields

# To add a new context handler we have to add it in the function handle_input


def handle_input(new_context, current_context, context_temp=None, current_context_temp=None, ProblemData=None, input_sentence=None):

    if new_context == "Denial":
        # necesito un string para cuando sea un subject para recordarle lo que le falta
        return handle_context_denial(context_temp, ProblemData)

    else:
        if new_context == "Confirmation":
            # we handle the context_temp as if it was the new_context
            ProblemData.set_add_info_to_subject(False)
            return handle_input(context_temp, current_context)
        else:
            if new_context == "Back_to_Main":
                return handle_context_back_to_main(current_context)
            else:
                if "Main" in new_context:
                    return handle_context_main(new_context, ProblemData)
                else:
                    if new_context == "Subject":
                        return handle_context_subject(input_sentence, ProblemData)
                    else:
                        if new_context == "Name":

                            # flag so we can put info per subject
                            ProblemData.set_add_info_to_subject(True)
                            response = handle_context_name(
                                input_sentence, ProblemData) + "\n" + next_subject(ProblemData)
                            return response
                        else:
                            if "UTime" in new_context:
                                if ProblemData.edit is False:
                                    response = handle_context_unit_time(
                                        input_sentence, ProblemData, new_context)
                                    subject_name = new_context.split()[1]
                                    subject = du.get_subject_by_name(
                                        ProblemData, subject_name)
                                    if subject_complete(ProblemData, subject):
                                        follow_up_str = next_subject(
                                            ProblemData)
                                    else:
                                        follow_up_str = generate_response_individual_subject(
                                            new_context, ProblemData)

                                    response_str = response + "\n" + follow_up_str
                                else:
                                    response = handle_context_unit_time(
                                        input_sentence, ProblemData, new_context)
                                    print(response)
                                    return keep_editing(ProblemData, subject)

                                # agregar lo que pasa al editar
                                return response_str
                            else:
                                if "Unit" in new_context:
                                    # We need to add info to the problem data
                                    # we check if the edit flag is True or False
                                    if ProblemData.edit is False:
                                        response = handle_context_unit(
                                            input_sentence, ProblemData, new_context)
                                        follow_up_str = ask_for_subject_data_follow_up(
                                            new_context, ProblemData)
                                        response_str = response + "\n" + follow_up_str
                                    else:
                                        response = handle_context_unit_time(
                                            input_sentence, ProblemData, new_context)
                                        print(response)
                                        return keep_editing(ProblemData, subject)

                                    # agregar lo que pasa al editar
                                    return response_str
                                else:
                                    if new_context == "Edit":
                                        # activamos la edit flag
                                        ProblemData.set_edit_flag(True)
                                        response = handle_context_edit(
                                            input_sentence, ProblemData)

                                        return response

                                    else:
                                        # if no handler was identified we return False
                                        return False


def handle_context_back_to_main(current_context, context_temp):
    # I want to ask the user if he wants to leave the current context
    if "Unit" in current_context or "Utime" in current_context:
        words = current_context.split(' ')
        subject_from_context = words[1]
        response_string = "Are you sure that you want to stop adding information to the subject: {subject_from_context}? \n don\'t worry, we can come back here later :)"
        response_string = response_string.replace(
            "{subject_from_context}", subject_from_context)
        return response_string
# redireccionar bien esto
    if context_temp in field_names:
        context_string = field_names.get(context_temp)
        response_string = "we can add more information here later.\n Are you sure you want to add information to {context_string}?"
        response_string = response_string.replace(
            "{context_string}", context_string)
    return response_string


def handle_context_denial(context_temp, Problem_data):
    if "Unit" in context_temp:
        response = generate_response_individual_subject(
            context_temp, Problem_data)

    return response


def handle_context_main(new_context, ProblemData):
    if "-total_time" in new_context:
        field = readable_field("total_time")
    else:
        if "-duration_of_hour" in new_context:
            field = readable_field("duration_of_hour")
        else:
            if "-no_study_hours" in new_context:
                field = readable_field("no_study_hours")
            else:
                if "-no_study_days" in new_context:
                    field = readable_field("no_study_days")
    missing_fields = ProblemData.validate_data()
    response = generate_response(missing_fields)
    added_info_response = "You just added: " + field + "\n" + response

    return added_info_response


def handle_context_subject(input_sentence, ProblemData: pd):
    number_of_subjects = pre.number_from_text(input_sentence)
    du.add_info(ProblemData, "number_of_subjects", number_of_subjects)
    response_str = "Great! you are working on " + \
        str(number_of_subjects)+" subjects.\nHow are these subjects called?"
    return response_str


def handle_context_name(input_sentence, ProblemData: pd):
    # TODO necesito una función que identifique los subjects y los meta en un array
    # quiero que de este array se actualice el numero de subjects

    # subjects_list tiene una lista de los nombres de los subjects
    subjects_list = pre.tag_subjects(input_sentence)
    # subject_list is a string list with the names of the subjects
    ProblemData.set_subject_list(subjects_list)
    for s in subjects_list:
        # creamos un subject() con cada nombre de la lista y lo agregamos
        du.add_subject(ProblemData, Subject(s))
    subjects_str = ""
    if len(subjects_list) == 1:
        subjects_str = subjects_str.join(subjects_list[0])
    else:
        subjects_str = ", ".join(subjects_list[:-1])
        subjects_str += f" and {subjects_list[-1]}"

    response = "Great to hear that you are studying for " + subjects_str
    return response


def handle_context_unit(input_sentence, ProblemData: pd, new_context):
    number_of_units = pre.number_from_text(input_sentence)
    # we split the new context and extract the name of the current subject
    subject_name = new_context.split()[1]
    subject = du.get_subject_by_name(ProblemData, subject_name)
    info = {"number_of_units": number_of_units}
    du.update_subject(subject, info)

    response = subject_name+" has "+str(number_of_units)+" Units. Got it!"
    return response


def handle_context_unit_time(input_sentence, ProblemData: pd, new_context):
    hours_per_unit = pre.number_from_text(input_sentence)
    # we split the new context and extract the name of the current subject
    subject_name = new_context.split()[1]
    subject = du.get_subject_by_name(ProblemData, subject_name)
    info = {"hours_per_unit": hours_per_unit}
    du.update_subject(subject, info)

    response = "We will take as a guideline that each " + subject_name + \
        " unit will take you " + str(hours_per_unit) + " hours."
    return response


def handle_context_edit(input_sentence, ProblemData: pd):
    # we need to analize the sentence to see if there is a subject inside
    subject_list = ProblemData.get_subject_list_from_data()
    str_in_subject = str_in_subject(input_sentence, subject_list)
    in_list = str_in_subject[0]
    sub = str_in_subject[1]
    # si se encontró el subject en la string se trabajará con ese
    if in_list:
        # después de que se definió el subject a edit:
        # seteamos el flag de add_info to subject
        ProblemData.set_add_info_to_subject(True)
    # vaciamos la subject_list y la llenamos solo con un elemento que es nuestro subject
        ProblemData.subject_list = [sub]
    # devolvemos un string con los fields de los subjects que se pueden editar
        subject = du.get_subject_by_name(ProblemData, sub)
        field_list = subject.get_fields()
        fields_str = "\n".join([f"- {valor}" for valor in field_list])
        response_str = "you can change the following information from the subject "+sub + fields_str
        return response_str
    # si no se encontró el subject en la string se le preguntará por la materia
    else:
        # ask about subject
        subjects_str = ""
        subjects_str = ", ".join(subject_list[:-1])
        subjects_str += f" or {subject_list[-1]}"
        sentence = input(
            'Which subject do you want to edit?\n'+subjects_str+'?')
        # we check if the subject is in the string
        str_in_subject = str_in_subject(sentence, subject_list)
        in_list = str_in_subject[0]
        sub = str_in_subject[1]
        if in_list:
            handle_context_edit(sentence, ProblemData)
        else:
            response = "Sorry I don't recognize that subject, try typing it all again"
            ProblemData.set_edit_flag(False)
            return response


def str_in_subject(sentence: str, subject_list: list):
    sentence = sentence.split()
    in_list = False
    # I need to check if a subject from the subject_list is in the sentence
    for word in sentence:
        if word in subject_list:
            in_list = True
            subject = word
            break
    return ((in_list, subject))


def keep_editing(ProblemData: pd, subject: Subject):
    # aquí le preguntamos al usuario si quiere seguir editando
    keep_editing_str = "Do you want to keep editing?"
    sentence = input(keep_editing_str)
    # se debe dar un codigo que acepte valores solo de si o no
    input = input_sentence(sentence)

    # si se quiere seguir editando
    # devolvemos un string con los fields de los subjects que se pueden editar
    if input["intent_tag"] is "Confirmation":
        fields = subject.get_fields()
        fields_str = "\n".join([f"- {valor}" for valor in fields])

        return "Nice, what do you want to change from the subject?\n"+fields_str
    else:
        # si ya no se quiere seguir editando:
        if input["intent_tag"] is "Denial":
            # se quita la flag de edicion y se regresa a main
            ProblemData.set_add_info_to_subject(False)
            ProblemData.set_edit_flag(False)
            ProblemData.current_context = "Main"
            missing_fields = ProblemData.validate_data()
            return generate_response(missing_fields)


def readable_field(field):
    return field_names.get(field)


def subject_complete(ProblemData: pd, subject: Subject):
    if subject.validate_data() is True:
        subject_list = ProblemData.get_subject_list
        print(subject_list)
        ProblemData.pop_subject_list(subject_list)
        return True
    else:
        return False


# This function generate a response asking for the data of a subject
# this is suposed to be triggered after adding the subject
def ask_for_subject_data(subject: Subject):
    subject_name = subject.get_key("name")
    missing_fields = subject.validate_data()
    missing_fields_str = ""
    for mf in missing_fields:
        missing_fields_str += f"- {readable_field(mf)}\n"
    response_str = "Do you mind adding the following information for " + \
        subject_name+"?\n" + missing_fields_str
    return response_str


def ask_for_subject_data_follow_up(new_context, ProblemData: pd):
    subject_name = new_context.split()[1]
    subject = du.get_subject_by_name(ProblemData, subject_name)
    missing_fields = subject.validate_data()
    missing_fields_str = ""
    if len(missing_fields) >= 2:
        for mf in missing_fields:
            missing_fields_str += f"- {readable_field(mf)}\n"
        response_str = "Dont forget to add:\n"+missing_fields_str
    else:
        mf = readable_field(missing_fields[0])
        response_str = "Do you know " + mf + "?"
    return response_str

# this function check which subject is currently being added info to
# and returns a string asking to fill up the missing fields of the subject


def next_subject(ProblemData: pd):
    subject_list = ProblemData.get_subject_list()
    if len(subject_list) >= 1:
        current_subject = du.get_subject_by_name(ProblemData, subject_list[0])
        return ask_for_subject_data(current_subject)
    else:
        # if there are no more subjects in the list
        # we generate a string asking for the rest of missing fields
        missing_fields = ProblemData.validate_data()
        response = generate_response(missing_fields)
        return response


def input_sentence(sentence, all_words=all_words, device=device, tags=tags, constraint_types=constraint_types, model=model):
    sentence = pre.preprocess_text(sentence)
    x = pre.bag_of_words(sentence, all_words)
    x = x.reshape(1, x.shape[0])
    x = torch.from_numpy(x).to(device)

    intent_output, constraint_output = model(x)
    _, predicted_intent = torch.max(intent_output, dim=1)
    intent_tag = tags[predicted_intent.item()]
    _, predicted_constraint = torch.max(constraint_output, dim=1)
    # Obtén el tipo de restricción
    constraint_type = constraint_types[predicted_constraint.item()]

    # check the probabilities
    intent_probs = torch.softmax(intent_output, dim=1)
    intent_prob = intent_probs[0][predicted_intent.item()]

    # Revisa las probabilidades para el tipo de restricción
    constraint_probs = torch.softmax(constraint_output, dim=1)
    constraint_prob = constraint_probs[0][predicted_constraint.item()]

    if intent_prob.item() > 0.75:
        return {"intent_tag": intent_tag, "constraint_type": constraint_type}
    else:
        sentence = input(
            "Sorry, I didn't get that... can you type that again?")
        input_sentence(sentence)