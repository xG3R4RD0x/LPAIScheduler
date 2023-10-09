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

        self.current_context = None
        self.context_temp = None
        self.current_context_temp = None
        self.add_info_to_subject = False
        self.subject_list = []
        self.edit = False

    # validate data does not validate the soft_constraints yet
    # TODO validate also soft_constraints
    # subject_list is a list with the names of the subjects
    def set_subject_list(self, subject_list: list):

        for subject in subject_list:
            if subject not in self.subject_list:
                self.subject_list.append(subject)

    def pop_subject_list(self, subject_list: list):
        subject_list = self.get_subject_list()
        del subject_list[0]
        self.set_subject_list(subject_list)

    # returns a subject_list based on the saved info of the problem NOT the variable subject_list
    def get_subject_list_from_data(self):
        subject_list = self.data["hard_constraints"]["subjects"]
        subject_list_names = []
        for s in subject_list:
            subject_list_names.append(s.get_key("name"))
        return subject_list_names

    def get_subject_list(self):
        return self.subject_list

    def set_add_info_to_subject(self, value: bool):
        self.add_info_to_subject = value

    def set_current_context(self, context):
        self.current_context = context

    def set_context_temp(self, context):
        self.context_temp = context

    def set_current_context_temp(self, context):
        self.current_context_temp = context

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
                # course representa al subject() dentro de subject_list
                course_temp = []
                # for field in ProblemData.SUBJECT_REQUIRED_FIELDS:
                #     # imprime el nombre de la materia y su empty_field
                #     course_field = course[field]
                #     if field is "name":
                #         course_temp.append(course_field.get_key("name"))
                #     if course_field is None:
                #         course_temp.append(field)
                mf_course = course.validate_data()
                if mf_course is not True:
                    course_name = course.get_key("name")
                    course_temp = mf_course
                    course_temp.insert(0, course_name)
                    missing_fields.append(course_temp)

            if missing_fields is []:
                return True
            else:
                return missing_fields
        else:
            return False
