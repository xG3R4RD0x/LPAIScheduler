import chat_util as cu

import unittest
import preprocessing as pre
from problem_data import ProblemData
from subject import Subject
import data_util as du
import datetime
import soft_constraints_util as scu
from soft_constraints import no_study_day, no_study_hours
import extract_data as ed


class LPTest(unittest.TestCase):
    def setUp(self):
        self.pd = self.create_test_problem_data()

    def test_extract_data(self):
        print("test_extract_data")
        print(self.pd)
        extracted_data = ed.extract_data(self.pd)
        print(extracted_data)
        self.assertTrue(type(extracted_data), dict)

    # test_utilities

    def create_test_subject(self, problem_data: ProblemData, subject_name: str):
        subject = Subject(subject_name)
        du.add_subject(problem_data, subject)

    def create_test_nsh(self, problem_data: ProblemData):
        pd = problem_data
        sentence = "I can't study after 2 PM"
        time_list = pre.tag_time(sentence)
        time_str = ""
        # print added for debugging
        print("test_no_study_hour")

        # check if range
        # if not range we check the sentence from start or untill end of the day
        if type(time_list[0]) == str:
            time_str = time_list[0]
            time_list.pop(0)
        else:
            for t in time_list:
                time_str += t.strftime("%I:%M %p")

        Everyday = False
        date_sentence = "from July 25th to July 30th "
        date_input = pre.tag_date(date_sentence)
        dates = scu.extract_dates(date_input)
        # creating the no_study_hour_object
        # we take out the first element of the list because it is a string with the time
        # the rest is going to be a range of time
        if len(time_list) < 2:
            end_of_day_time = datetime.time(23, 59)
            time_list.append(end_of_day_time)
        # si es un rango de fechas creamos un no study hours contraint object para cada fecha
        # y lo agregamos al problem data

        if type(dates) == list:
            for d in dates:
                nsh_temp = no_study_hours()
                nsh_temp.data.update(
                    {"hour_range": time_list, "dates": d, "everyday": Everyday, "constraint_type": "weak"})
                du.add_no_study_hours(pd, nsh_temp)
        else:
            nsh_temp = no_study_hours()
            nsh_temp.data.update(
                {"hour_range": time_list, "dates": None, "everyday": Everyday, "constraint_type": "weak"})
            du.add_no_study_hours(pd, nsh_temp)

    def create_test_nsd(self, problem_data: ProblemData,):
        sentence = "I prefer not to study from July 15th to July 20th "
        print("test_no_study_day\n")
        pd = problem_data
        constraint_type = "soft"
        dates = pre.tag_date(sentence)

        dates_w_range = dates
        dates = scu.extract_dates(dates)
        # process dates to check if they are individual or a range of dates
        dates_str = ""
        dates_str_list = []
        for d in dates_w_range:
            if type(d) == list:
                dates_str = "from "+d[0] + "to "+d[1]
                dates_str_list.append(dates_str)
            else:
                dates_str_list.append(d)

        # creating no_study objects
        for d in dates:
            nsd_temp = no_study_day()
            nsd_temp.data.update(
                {"dates": [d], "constraint_type": constraint_type, "repeating_event": False})
            du.add_no_study_day(pd, nsd_temp)

    def create_test_problem_data(self):
        pd = ProblemData()
        du.add_info(pd, "number_of_subjects", 3)
        # adding subjects
        self.create_test_subject(pd, "Math")
        subject = du.get_subject_by_name(pd, "Math")
        info = {"number_of_units": 4, "hours_per_unit": 2}
        du.update_subject(subject, info)
        self.create_test_subject(pd, "Literature")
        subject = du.get_subject_by_name(pd, "Literature")
        info = {"number_of_units": 5, "hours_per_unit": 2}
        du.update_subject(subject, info)
        self.create_test_subject(pd, "Chemistry")
        subject = du.get_subject_by_name(pd, "Chemistry")
        info = {"number_of_units": 10, "hours_per_unit": 1}
        du.update_subject(subject, info)
        # total_time
        du.add_total_time(pd, 30)
        # start_date
        start_date = scu.extract_dates(pre.tag_date("July 1st"))
        du.add_start_date(pd, start_date)
        # Constraints
        self.create_test_nsd(pd)
        self.create_test_nsh(pd)
        return pd


if __name__ == '__main__':
    unittest.main()
