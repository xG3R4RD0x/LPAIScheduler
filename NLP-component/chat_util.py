# contexts represents the context of the last input of the user
# This is the context Hierarchy, I use this to give a direction to the conversation
# For Example If I start with Subject, then I have to go to Name and then Unit
# after Unit comes Unit Time and I have to check if there are any more subjects
# if there are more subjects then I go back to Name and keep filling the subjects
# if not then I go back to main to fill the rest of the problem Data

import random
from problem_data import ProblemData as pd

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
        "context": "Unit", "subcontext": ["Unit-Time"]
    },
    {
        "context": "Unit-Time", "subcontext": ["Unit", "Main"]
    },
    {
        "context": "Confirmation", "subcontext": ["Main", "Unit_Time", "Unit"]
    },
    {
        "context": "Denial", "subcontext": ["Main", "Unit_Time", "Unit"]
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
        return "everything is fine"
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
            return handle_input(context_temp, current_context)
        else:
            if new_context == "Back_to_Main":
                return handle_context_back_to_main(current_context)
            else:
                if "Main" in new_context:
                    return handle_context_main(new_context, ProblemData)
                else:
                    if new_context == "Subject":
                        return handle_context_subject(input_sentence)
                    else:
                        if new_context == "Name":
                            pass
                        else:
                            if new_context == "Unit-Time":
                                pass
                            else:
                                if "Unit" in new_context:
                                    pass
                                else:
                                    # if no handler was identified we return False
                                    return False


def handle_context_back_to_main(current_context, context_temp):
    # I want to ask the user if he wants to leave the current context
    if "Unit" in current_context:
        words = current_context.split(' ')
        subject_from_context = words[1]
        response_string = "Are you sure that you want to stop adding information to the subject: {subject_from_context}? \n don\'t worry, we can come back here later :)"
        response_string = response_string.replace(
            "{subject_from_context}", subject_from_context)
        return response_string

    if context_temp in field_names:
        context_string = field_names.get(context_temp)
        response_string = "we can add more information here later.\n Are you sure you want to add information to {context_string}"
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


def handle_context_subject(input_sentence):

    # TODO necesito una función que identifique los subjects y los meta en un array
    # quiero que de este array se actualice el numero de subjects
    return "String response de Subject"


def readable_field(field):
    return field_names.get(field)

# def extract_from_input(input_string, context):
#     if context=="Subject":

# TODO ver una forma de poder editar los subjects en el chat
