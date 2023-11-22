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
from soft_constraints import no_study_day, no_study_hours
import soft_constraints_util as scu
import datetime
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

with open('./NLP/intents.json', 'r') as f:
    intents = json.load(f)

FILE = "./NLP/data.pth"
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
        "context": "Back", "subcontext": ["Confirmation", "Denial"]
    },
    {
        "context": "Main", "subcontext": ["Main", "Subject", "Main-total_time", "No_study_hours", "No_study_days", "Edit"]
    },
    {
        "context": "Subject", "subcontext": ["Name"]
    },
    {
        "context": "Name", "subcontext": ["Unit", "Utime", "Main"]
    },
    {
        "context": "Unit", "subcontext": ["Unit", "UTime", "Main"]
    },
    {
        "context": "UTime", "subcontext": ["Unit", "UTime", "Main"]
    },
    {
        "context": "Confirmation", "subcontext": ["Main", "UTime", "Unit"]
    },
    {
        "context": "Denial", "subcontext": ["Main", "UTime", "Unit"]
    },
    {
        "context": "Edit", "subcontext": ["Back", "UTime", "Unit"]
    },
    {
        "context": "No_study_days", "subcontext": ["Main", "Subject", "Main-total_time", "No_study_hours", "No_study_days", "Edit"]
    },
    {
        "context": "No_study_hours", "subcontext": ["Main", "Subject", "Main-total_time", "No_study_hours", "No_study_days", "Edit"]
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
        if c["context"] in current_context:
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
        if input["intent_tag"] == "Confirmation":

            return "everything is fine"
        else:
            if input["intent_tag"] == "Denial":
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
                    # print(subject)
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


def handle_input(new_context, current_context, context_temp=None, current_context_temp=None, ProblemData=None, input_sentence=None, constraint_type=None):

    if new_context == "Denial":
        # necesito un string para cuando sea un subject para recordarle lo que le falta
        return handle_context_denial(context_temp, ProblemData)

    elif new_context == "Confirmation":
        # we handle the context_temp as if it was the new_context
        ProblemData.set_add_info_to_subject(False)
        return handle_input(context_temp, current_context)

    elif new_context == "Back":
        return handle_context_back_to_main(current_context, context_temp)

    elif "Main" in new_context:
        print("handle_input_Main")
        return handle_context_main(new_context, ProblemData, input_sentence)

    elif new_context == "Subject":
        return handle_context_subject(input_sentence, ProblemData)

    elif new_context == "Name":
        # flag so we can put info per subject
        ProblemData.set_add_info_to_subject(True)
        response = handle_context_name(
            input_sentence, ProblemData) + "\n" + next_subject(ProblemData)
        return response

    elif "UTime" in new_context:
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

    elif "Unit" in new_context:
        # We need to add info to the problem data
        # we check if the edit flag is True or False
        if ProblemData.edit is False:
            response = handle_context_unit(
                input_sentence, ProblemData, new_context)
            subject_name = new_context.split()[1]
            subject = du.get_subject_by_name(
                ProblemData, subject_name)
            if subject_complete(ProblemData, subject):
                follow_up_str = next_subject(
                    ProblemData)
            else:
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

    elif new_context == "Edit":
        # activamos la edit flag
        ProblemData.set_edit_flag(True)
        response = handle_context_edit(
            input_sentence, ProblemData)
        return response

    elif new_context == "No_study_days":
        response = handle_context_no_study_days(
            input_sentence, ProblemData, constraint_type)
        # tengo que hacer una función que cuando compruebe que la constraint esté completa
        # ahí recién cree las constraints con un for loop
        # o sea crea una constraint por día haciendo que la fecha agregue +1 hasta llegar al end date
        return response

    elif new_context == "No_study_hours":
        response = handle_context_no_study_hours(
            input_sentence, ProblemData, constraint_type)
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
# TODO ask for confirmation to leave the current context
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


def handle_context_main(new_context, ProblemData: pd, sentence: str):
    print("dentro del handle_context main")
    if "-total_time" in new_context:
        field = readable_field("total_time")
        total_time = pre.number_from_text(sentence)
        du.add_total_time(ProblemData, total_time)
        print("LPAIbot: When do you want to start?(date)")
        date_input = input("You: ")
        date = pre.tag_date(date_input)
        print("LPAIbot: We are going to start from:"+date[0])
        du.add_start_date(ProblemData, date[0])

    elif "-duration_of_hour" in new_context:
        field = readable_field("duration_of_hour")
        duration_of_hour = pre.number_from_text(sentence)
        du.add_duration_of_hour(ProblemData, duration_of_hour)
        print("LPAIbot: cool, we are going to make your hours with a duration of" +
              str(duration_of_hour)+" minutes")

    elif "-hours_per_day" in new_context:
        field = readable_field("hours_per_day")
        hours_per_day = abs(pre.number_from_text(sentence))
        while hours_per_day > 8:
            print(
                "LPAIbot: Studying for more than 8 hours per day is not healthy, try with less hours please")
            hours_per_day = abs(pre.number_from_text(input("You: ")))
        print("We are going to plan your days with " +
              str(hours_per_day)+"h for studying")

    missing_fields = ProblemData.validate_data()
    response = generate_response(missing_fields)
    if new_context != "Main":
        added_info_response = "You just added: " + field + "\n" + response
        return added_info_response

    return response


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


def handle_context_no_study_days(sentence: str, ProblemData: pd, constraint_type):
    constraint_type = constraint_type
    dates = pre.tag_date(sentence)
    dates_w_range = dates
    dates = scu.extract_dates(dates)
    # procesar las dates por si son individuales o en rango
    dates_str = ""
    dates_str_list = []
    for d in dates_w_range:
        if type(d) == list:
            dates_str = "from "+d[0] + "to "+d[1]
            dates_str_list.append(dates_str)
        else:
            dates_str_list.append(d)

    # creating no_study objects
    for d in dates:
        nsd_temp = no_study_day()
        nsd_temp.data.update(
            {"dates": d, "constraint_type": constraint_type, "repeating_event": None})
        du.add_no_study_day(ProblemData, nsd_temp)
    # ask_if_repeating event
    repeating = False
    print("LPAIbot: Is this weekly?")
    repeating_sentence = input('You: ')
    inps = input_sentence(repeating_sentence)
    print("intent_tag:"+inps["intent_tag"])
    if inps["intent_tag"] == "Confirmation":
        repeating = True
        # agregar flag a todas las fechas
        for d in dates:
            nsd = du.get_nsd_by_datetime(ProblemData, d)
            nsd.data.update({"repeating_event": True})
    elif inps["intent_tag"] == "Denial":
        repeating = False
    # show nsd information
    response_str = "Got it, I am going to take in consideration these dates for you to not to study:"
    for d in dates_w_range:
        response_str += "\n-"+str(d)
    if repeating == True:
        response_str += "\nand it's going to be repeated weekly"
    return response_str


def handle_context_no_study_hours(sentence: str, ProblemData: pd, constraint_type):
    # extraer la hora o el rango de horas del input
    time_list = pre.tag_time(sentence)
    time_str = ""
    print(time_list)
    # check if range
    # if not range we check the sentence from start or untill end of the day
    if type(time_list[0]) == str:
        time_str = time_list[0]
        time_list.pop(0)
    else:
        for t in time_list:
            time_str += t.strftime("%I:%M %p")

    print("LPAIbot: Great!, well take in consideration not to assign you study time during these hours:\n"+time_str)
    print("Do you want this for everyday?")
    date_question = input_sentence(input("You: "))
    if date_question["intent_tag"] == "Confirmation":
        response_str = "Cool, We are going to do this for everyday"
        Everyday = True
        dates = None
    if date_question["intent_tag"] == "Denial":
        print("Can you tell me for which date or dates do you want this to be taken in consideration?")
        date_input = pre.tag_date(input("You: "))
        dates_str_list = []
        dates = scu.extract_dates(date_input)
        for d in date_input:
            if type(d) == list:
                dates_str = "from "+d[0] + "to "+d[1]
                dates_str_list.append(dates_str)
            else:
                dates_str_list.append(d)

        response_str = "Got it, I am going to take in consideration these dates:"
        for d in dates_str_list:
            response_str += "\n-"+d

    # creating the no_study_hour_object
    # we take out the first element of the list because it is a string with the time
    # the rest is going to be a range of time
    if len(time_list) < 2:
        end_of_day_time = datetime.time(23, 59)
        time_list.append(end_of_day_time)
    if type(dates) == list:
        for d in dates:
            nsh_temp = no_study_hours()
            nsh_temp.data.update(
                {"hour_range": time_list, "dates": d, "everyday": Everyday, "constraint_type": constraint_type})
            du.add_no_study_hours(ProblemData, nsh_temp)
    else:
        nsh_temp = no_study_hours()
        nsh_temp.data.update(
            {"hour_range": time_list, "dates": None, "everyday": Everyday, "constraint_type": constraint_type})
        du.add_no_study_hours(ProblemData, nsh_temp)

    # We need to verifz at the end that all data has been generated correctly
    # If I got a nsh withoutdate I have to ask for it, but if it is for everyday
    # I have to assign it and copy it in every day

    return response_str


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
    if input["intent_tag"] == "Confirmation":
        fields = subject.get_fields()
        fields_str = "\n".join([f"- {valor}" for valor in fields])

        return "Nice, what do you want to change from the subject?\n"+fields_str
    else:
        # si ya no se quiere seguir editando:
        if input["intent_tag"] == "Denial":
            # se quita la flag de edicion y se regresa a main
            ProblemData.pop_subject_list()
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
    if missing_fields == True:
        missing_fields = []

    length_mf = len(missing_fields)
    if length_mf >= 2:
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
        # print("next_subject current_context:"+ProblemData.current_context)
        return ask_for_subject_data(current_subject)
    else:
        # if there are no more subjects in the list
        # we generate a string asking for the rest of missing fields
        missing_fields = ProblemData.validate_data()
        response = generate_response(missing_fields)
        ProblemData.set_current_context("Main")
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
