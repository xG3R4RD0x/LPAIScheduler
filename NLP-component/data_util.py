import problem_data as pd
import subject
from soft_constraints import no_study_day, no_study_hours

# utility functions to update the Problem Data Dictionary


def add_info(problem_data: pd, key, value):
    problem_data.data[key] = value


def get_info(problem_data: pd, key):
    return problem_data.data.get(key)


def get_data(problem_data: pd):
    return problem_data.data


def add_subject(problem_data: pd, subject: subject):
    problem_data.data["subjects"].append(subject)


def get_subject_by_name(problem_data: pd, name_of_the_subject: str):
    for subject in problem_data.data["subjects"]:
        if subject["name"] == name_of_the_subject:
            return subject
    return None

# update subject accepts the subject and the info in a key - value format
# For Example  update(subject, {"name": "Math"})
#              update(subject, {"number_of_units": 4})
#              update(subject, {"hours_per_units": 3})


def update_subject(subject: subject, info: dict):
    subject.data.update(info)

# update Problem Data
# info should be a dictionary with a key - Value that's inside
# info = {"hard_constraints": {"total_time":40, "hours_per_day":5}}
#
# For Example update_data(problem_data, info)


def update_data(problem_data: pd, info: dict):
    problem_data.data.update(info)


def add_no_study_day(problem_data: pd, no_study_day: no_study_day):
    problem_data.data["soft_constraints"]["no_study_days"].append(no_study_day)


def add_no_study_hours(problem_data: pd, no_study_hours: no_study_hours):
    problem_data.data["soft_constraints"]["no_study_hours"].append(
        no_study_hours)
