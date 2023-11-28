# an object which has a dictionary to store the parsed data from the chatbot
import soft_constraints_util as scu
from datetime import datetime, timedelta


class ProblemData:

    REQUIRED_FIELDS = ["start_date", "total_time", "number_of_subjects"]
    SUBJECT_REQUIRED_FIELDS = ["name", "number_of_units", "hours_per_unit"]

    def __init__(self):
        # Inicializa un diccionario con valores vacios
        self.data = {
            "hard_constraints": {
                "start_date": None,  # esto debe ser una fecha con string
                # "end_date": None,  # Fecha limite
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
        # day ranges until 4 pm because the generator makes 8 slots
        # las slot should be 4pm to 5pm
        self.time_list = self.generate_hour_ranges("9:00 AM", "4:00 PM", 1)
        self.current_context = None
        self.context_temp = None
        self.current_context_temp = None
        self.add_info_to_subject = False
        self.subject_list = []
        self.edit = False
        self.complete = False

    # subject_list is a list with the names of the subjects

    def set_subject_list(self, subject_list: list):

        for subject in subject_list:
            if subject not in self.subject_list:
                self.subject_list.append(subject)

    def pop_subject_list(self, subject_list: list):
        subject_list = self.get_subject_list()
        del subject_list[0]
        self.set_subject_list(subject_list)

    def set_edit_flag(self, value: bool):
        self.edit = value

    # returns a subject_list based on the saved info of the problem NOT the variable subject_list

    def get_subject(self, name: str):
        subject_list = self.data["hard_constraints"]["subjects"]
        for s in subject_list:
            if s.data["name"] == name:
                return s
        return None

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

    def get_hours_per_day(self):
        return self.data["hard_constraints"]["hours_per_day"]

    def get_hours_per_subject(self):
        subject_list = self.data["hard_constraints"]["subjects"]
        hours_per_subject = {}
        for s in subject_list:
            name = s.get_key("name")
            number_of_units = s.get_key("number_of_units")
            hours_per_unit = s.get_key("hours_per_unit")
            hps = number_of_units * hours_per_unit
            hours_per_subject.update({name: hps})
        return hours_per_subject

    def get_total_time(self):
        return self.data["hard_constraints"]["total_time"]

    def get_start_date(self):
        date = self.data["hard_constraints"]["start_date"]
        return scu.extract_dates(date)

    def get_no_study_days(self):
        # we get a list with the no study days
        nsd = self.data["soft_constraints"]["no_study_days"]
        total_datetime_list = scu.generate_total_time_datetime_list(self)
        new_nsd = []
        for item in nsd:
            i = item.data
            # all dates are going to be flatten to a unique list
            date_list = scu.flatten_list(i["dates"])
            for date in date_list:
                if i["constraint_type"] == "strong":
                    weight = 5
                else:
                    weight = 1
                constraint = {"weight": weight, "day": (
                    total_datetime_list.index(date)+1)}
                new_nsd.append(constraint)
        return new_nsd
    # falta transformar de fechas a numero de días

    def get_no_study_hours(self):

        #  {"hour_range": time_list, "dates": None, "everyday": Everyday, "constraint_type": constraint_type})

        # we get a list with the no study hours
        nsh = self.data["soft_constraints"]["no_study_hours"]
        total_datetime_list = scu.generate_total_time_datetime_list(self)
        total_time = self.data["hard_constraints"]["total_time"]
        hour_list = self.time_list
        new_nsh = []
        for item in nsh:

            i = item.data

            if i["everyday"] == False:
                # all dates are going to be flatten to a unique list
                if type(i["dates"]) == list:
                    date_list = i["dates"]
                elif type(i["dates"]) == datetime:
                    date_list = [i["dates"]]
            elif i["everyday"] == True:
                date_list = range(1, total_time+1)

            for date in date_list:
                date_num = date
                if type(date_num) == datetime:
                    date_num = total_datetime_list.index(date_num)+1

                if i["constraint_type"] == "strong":
                    weight = 5
                else:
                    weight = 1

                hour_range = self.find_ranges_by_time(
                    hour_list, i["hour_range"][0], i["hour_range"][1])

                for h in hour_range:

                    constraint = {"weight": weight,
                                  "day": date_num, "hour": h}
                    new_nsh.append(constraint)

        return new_nsh

    def generate_hour_ranges(self, start, end, duration):
        # Convert start and end hours to datetime objects
        start_time = datetime.strptime(start, "%I:%M %p")
        end_time = datetime.strptime(end, "%I:%M %p")

        # Initialize the list of lists
        ranges = []

        # Create the hour ranges
        while start_time <= end_time:
            # Get the current and end time of the range
            current_time = start_time.time()
            end_hour = (start_time + timedelta(hours=duration)).time()

            # Add the range to the list
            ranges.append([current_time, end_hour])

            # Move to the next range
            start_time += timedelta(hours=duration)

        return ranges

    # this function transforms the hour range from the soft constraints into
    # the number of the hour in the study plan
    def find_ranges_by_time(self, original_ranges, target_start, target_end):
        indices = []

        for i, (start, end) in enumerate(original_ranges):
            if start <= target_start < end or start < target_end <= end or (start > target_start and end <= target_end):
                indices.append(i+1)

        return indices

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
