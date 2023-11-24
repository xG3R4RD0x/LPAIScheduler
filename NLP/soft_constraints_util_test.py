from typing import Any, NoReturn
import unittest
import soft_constraints_util as scu
from datetime import datetime
from problem_data import ProblemData
import data_util as du
from soft_constraints import no_study_day as nsd, no_study_hours
import preprocessing as pre


class SoftConstraintsTest(unittest.TestCase):

    def setUp(self) -> None:
        return super().setUp()

    def test_extract_dates(self):
        date_list = [['July 15th', 'July 20th'], 'july 25th']
        response = scu.extract_dates(date_list)
        print("test_extract_dates")
        print(response)
        self.assertTrue(type(response), list)

    def test_process_dates(self):
        date_list = [[datetime(2023, 7, 15, 0, 0), datetime(
            2023, 7, 20, 0, 0)], datetime(2023, 7, 25, 0, 0)]
        response = scu.process_dates(date_list)
        print("test_process_dates")
        print(response)
        assertion = [[datetime(2023, 7, 15, 0, 0), datetime(2023, 7, 16, 0, 0), datetime(2023, 7, 17,
                                                                                         0, 0), datetime(2023, 7, 18, 0, 0), datetime(2023, 7, 19, 0, 0), datetime(2023, 7, 20, 0, 0)], datetime(2023, 7, 25, 0, 0)]
        self.assertEqual(response, assertion)

    def test_process_dates_start_date(self):
        dates = pre.tag_date("July 1st")
        print(dates)
        start_date = scu.extract_dates(dates)
        print(start_date)
        self.assertTrue(type(start_date[0]), datetime)

    def test_get_nsd_by_date(self):
        date = datetime(2023, 8, 18, 0, 0)
        pd = ProblemData()
        nsd_test = nsd()
        nsd_test.data.update({"dates": date, "constraint_type": "strong"})
        du.add_no_study_day(pd, nsd_test)
        nsd_by_date = du.get_nsd_by_datetime(pd, date)
        self.assertEqual(nsd_by_date, nsd_test)


if __name__ == '__main__':
    unittest.main()
