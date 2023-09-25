# contexts represents the context of the last input of the user
# This is the context Hierarchy, I use this to give a direction to the conversation
# For Example If I start with Subject, then I have to go to Name and then Unit
# after Unit comes Unit Time and I have to check if there are any more subjects
# if there are more subjects then I go back to Name and keep filling the subjects
# if not then I go back to main to fill the rest of the problem Data

import random

hierarchy = [{
    "context": "All", "subcontext": ["Confirmation"]
}, {
    "context": "Main", "subcontext": ["Subject"]
},
    {
        "context": "Subject", "subcontext": ["Name", "All"]
},
    {
        "context": "Unit Time", "subcontext": ["Name", "All"]
},
    {
        "context": "Name", "subcontext": ["Unit", "All"]
},
    {
        "context": "Unit", "subcontext": ["Unit Time", "All"]
}
]

response_options = [
    "We are doing great so far! \n But I still need you to tell me {checked_fields} before we can go on",
    "Awesome! \n But I still need you to tell me {checked_fields} before we can go on",
    "Thanks for the info! \n But I still need {checked_fields} to be able to do your plan :) ",
    "To proceed, I still need you to give me {checked_fields}",
    "We're making progress! However, I still require {checked_fields} before we can proceed.",
    "Great job! Nonetheless, I still need you to provide {checked_fields} before we can continue.",
    "Thank you for the information! Nevertheless, I still need {checked_fields} to proceed with your plan.",
    "To move forward, I still need you to furnish {checked_fields}."
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
    "number_of_units": "the number of unit",
    "hours_per_unit": "the average number of hours per unit"
}


# check if the input is inside the context rules


def check_context(current_context, new_context):
    for c in hierarchy:
        if current_context == c["context"]:
            if new_context in c["subcontext"]:
                return True
            else:
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


# TODO ver una forma de poder editar los subjects en el chat
