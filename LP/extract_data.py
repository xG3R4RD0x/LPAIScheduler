from datetime import datetime
from NLP.problem_data import ProblemData as pd


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
        "start_date": ProblemData.get_start_date()
    }

    return extracted_data


def extract_data(ProblemData: dict):
    extracted_data = {"hours_per_day": None,
                      "total_time": None,
                      "subject_list": None,
                      "hours_per_subject": None,

                      }
    # getting total time from start and end dates
    start_date = ProblemData["start_date"]
    end_date = ProblemData["end_date"]
    if start_date is not None:
        total_time = get_total_time(start_date, end_date)
        extracted_data["total_time"] = total_time
    else:
        extracted_data["total_time"] = ProblemData["total_time"]

    return extracted_data


def get_total_time(start_date: datetime, end_date: datetime):

    total_time = start_date - end_date
    return total_time.days


data = {
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

example_data = {
    "hard_constraints": {
        "number_of_subjects": 3,
        "subjects":
            [{"name": "Math", "number_of_units": 4, "hours_per_unit": 2},
             {"name": "Literature", "number_of_units": 5, "hours_per_unit": 2},
             {"name": "Chemistry", "number_of_units": 10, "hours_per_unit": 1}],
            "total_time": 30,
            "hours_per_day": 8,
        "duration_of_hour": 45
    }}
