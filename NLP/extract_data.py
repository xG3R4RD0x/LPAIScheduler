from datetime import datetime
from problem_data import ProblemData as pd


def extract_data(ProblemData: pd):
    subjects = ["Math", "Literature", "Chemistry"]
    total_time = range(1, 60+1)
    hours_per_day = 8
    horas_por_materia = {"Math": 85,
                         "Literature": 90, "Chemistry": 65}

    #########
    extracted_data = {
        "subjects": ProblemData.get_subject_list_from_data(),
        "total_time": range(1, ProblemData.get_total_time()+1),
        "hours_per_day": ProblemData.get_hours_per_day(),
        "hours_per_subject": ProblemData.get_hours_per_subject(),
        "start_date": ProblemData.get_start_date(),
        "no_study_days": ProblemData.get_no_study_days(),
        "no_study_hours": ProblemData.get_no_study_hours()
    }

    return extracted_data


def get_total_time(start_date: datetime, end_date: datetime):

    total_time = start_date - end_date
    return total_time.days


# example_data = {
#     "hard_constraints": {
#         "number_of_subjects": 3,
#         "subjects":
#             [{"name": "Math", "number_of_units": 4, "hours_per_unit": 2},
#              {"name": "Literature", "number_of_units": 5, "hours_per_unit": 2},
#              {"name": "Chemistry", "number_of_units": 10, "hours_per_unit": 1}],
#             "total_time": 30,
#             "hours_per_day": 8,
#         "duration_of_hour": 45
#     },
#     "soft_contraints":
#         {"no_study_days": [{"dates": [datetime.date(2023, 11, 16), datetime.date(2023, 11, 19)], "constraint_type": "soft"}],
#          "no_study_hours": [{"hour_range": ["15:00:00", "18:00:00"],
#                              "everyday": False,
#                              "dates": [datetime.date(2023, 11, 20), datetime.date(2023, 11, 25)],
#                              "constraint_type": "strong"}]
#          }}

# no olvidar convertir en set las constraints para que no se repitan los días


# cuando tenga una hard_constraint aquí le doy un numero muy alto de peso
# y a las soft_ constraints uno no tan alto
# así puedo meterlas a ambas en la misma lista
