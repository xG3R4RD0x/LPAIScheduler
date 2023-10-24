import problem_data as pd
from subject import Subject
from soft_constraints import no_study_day, no_study_hours
from datetime import datetime

# utility functions to update the Problem Data Dictionary


def add_info(problem_data: pd, key, value):
    current_data = problem_data.data

    for info in current_data:
        if info == "hard_constraints":
            current_data[info][key] = value

        if info == "soft_constraints":
            current_data[info][key] = value
            break


def get_info(problem_data: pd, key):
    return problem_data.data.get(key)


def get_data(problem_data: pd):
    return problem_data.data


def get_subjects(problem_data: pd):
    return problem_data.data["hard_constraints"]["subjects"]


def add_subject(problem_data: pd, subject: Subject):
    current_subjects = problem_data.data["hard_constraints"]["subjects"]
    subject_list = problem_data.get_subject_list_from_data()
    if subject.data["name"] not in subject_list:
        subject_temp = subject
        current_subjects.append(subject_temp)
        return True
    else:
        return False


def get_subject_by_name(problem_data: pd, name_of_the_subject: str):
    for subject in problem_data.data["hard_constraints"]["subjects"]:
        if subject.get_key("name") == name_of_the_subject:
            return subject
    return None

# update subject accepts the subject and the info in a key - value format
# For Example  update(subject, {"name": "Math"})
#              update(subject, {"number_of_units": 4})
#              update(subject, {"hours_per_units": 3})


def update_subject(subject: Subject, info: dict):
    subject.data.update(info)

# update Problem Data
# info should be a dictionary with a key - Value that's inside
# info = {"hard_constraints": {"total_time":40, "hours_per_day":5}}
#
# For Example update_data(problem_data, info)


def add_no_study_day(problem_data: pd, no_study_day: no_study_day):
    problem_data.data["soft_constraints"]["no_study_days"].append(no_study_day)


def add_no_study_hours(problem_data: pd, no_study_hours: no_study_hours):
    problem_data.data["soft_constraints"]["no_study_hours"].append(
        no_study_hours)


def get_nsd_by_datetime(problem_data: pd, date: datetime):
    for nsd in problem_data.data["soft_constraints"]["no_study_days"]:
        if nsd.get_key("dates") == date:
            return nsd
    return None
