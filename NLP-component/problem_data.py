# an object which has a dictionary to store the parsed data from the chatbot
import subject


class ProblemData:

    REQUIRED_FIELDS = ["start_date", "total_time", "number_of_subjects"]

    def __init__(self):
        # Inicializa un diccionario con valores vacios
        self.data = {
            "hard_constraints": {
                "start_date": None,  # esto debe ser una fecha con string
                "end_date": None,  # Fecha limite
                "number_of_subjects": None,
                "subjects": [],
                "total_time": 30,  # default 30 days
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
                return missing_fields

        return True

    # validates that the subjects in subject list are complete
    # if they are not complete we get a list with the missing fields and the number
    # of the course on the list

    def validate_subjects(self):
        missing_fields = []
        number_of_subjects = self.data["hard_constraints"]["number_of_subjects"]
        subject_list = self.data["hard_constraints"]["subjects"]
        if number_of_subjects == len(subject_list):
            for index, course in enumerate(subject_list):
                checked_data = course.validate_data()
                if checked_data is not True:
                    missing_fields.append((index, checked_data))
            return missing_fields

        else:
            return False

# TODO tratar de crear un archivo .json para que lo lea el Pulp
# o que lea este archivo para extraer datos
