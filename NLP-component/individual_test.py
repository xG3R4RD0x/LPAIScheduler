from problem_data import ProblemData
import data_util as du
import chat_util as cu
import preprocessing as pre
from subject import Subject
import unittest


class IndividualTest(unittest.TestCase):
    def setUp(self):
        self.data = ProblemData()
        self.test_sub = Subject()

        sub_info = {
            "name": "Math",
            "number_of_units": 10,
            "hours_per_unit": None
        }

        du.update_subject(self.test_sub, sub_info)
        du.add_subject(self.data, self.test_sub)
        du.add_info(self.data, "number_of_subjects", 1)


if __name__ == '__main__':
    unittest.main()
