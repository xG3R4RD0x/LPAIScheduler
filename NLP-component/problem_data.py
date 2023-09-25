# an object which has a dictionary to store the parsed data from the chatbot
import subject


class ProblemData:

    REQUIRED_FIELDS = ["start_date", "total_time", "number_of_subjects"]
    SUBJECT_REQUIRED_FIELDS = ["name", "number_of_units", "hours_per_unit"]

    def __init__(self):
        # Inicializa un diccionario con valores vacios
        self.data = {
            "hard_constraints": {
                "start_date": None,  # esto debe ser una fecha con string
                "end_date": None,  # Fecha limite
                "number_of_subjects": None,
                "subjects": [],
                "total_time": None,  # default 30 days
                "hours_per_day": 8,  # default 8hours per day
                "duration_of_hour": 45,  # default 45 min y 15min de descanso entre horas
            },
            "soft_constraints": {
                "no_study_days": [],
                "no_study_hours": []
            }
        }

    # validate data does not validate the soft_constraints yet
    # TODO validate also soft_constraints
    def validate_data(self):
        missing_fields = []
        hard_constraints = self.data["hard_constraints"]

        for field in ProblemData.REQUIRED_FIELDS:
            if hard_constraints[field] is None:
                missing_fields.append(field)
        missing_subjects = ProblemData.validate_subjects(self)
        if type(missing_subjects) is not bool:
            missing_subjects_temp = {"subjects": missing_subjects}
            missing_fields.append(missing_subjects_temp)
        if missing_fields is not []:
            return missing_fields
        else:
            return True
        return missing_fields
    # validates that the subjects in subject list are complete
    # if they are not complete we get a list with the missing fields and the number
    # of the course on the list

    # it delivers which subject is missing what information
    def validate_subjects(self):
        missing_fields = []
        number_of_subjects = self.data["hard_constraints"]["number_of_subjects"]
        subject_list = self.data["hard_constraints"]["subjects"]

        if number_of_subjects is None:
            number_of_subjects = 0
        if number_of_subjects == len(subject_list):
            for course in subject_list:
                course_temp = []
                for field in ProblemData.SUBJECT_REQUIRED_FIELDS:

                    # imprime el nombre de la materia y su empty_field
                    course_field = course[field]
                    if field is "name":
                        course_temp.append(course_field)
                    if course_field is None:
                        course_temp.append(field)

                if len(course_temp) >= 2:
                    missing_fields.append(course_temp)
            if missing_fields is []:
                return True
            else:
                return missing_fields
        else:
            return False
