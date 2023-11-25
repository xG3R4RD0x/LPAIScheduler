import chat_util as cu

import unittest
import preprocessing as pre
from problem_data import ProblemData
from subject import Subject
import data_util as du
import test_util as tu
import soft_constraints_util as scu
from soft_constraints import no_study_day, no_study_hours
import extract_data as ed
from generate_plan import PlanGenerator


class LPTest(unittest.TestCase):
    def setUp(self):
        self.pd = tu.create_test_problem_data()

    def test_extract_data(self):
        print("test_extract_data")
        print(self.pd)
        extracted_data = ed.extract_data(self.pd)
        print(extracted_data)
        self.assertTrue(type(extracted_data), dict)

    def test_generate_plan(self):
        print("test_generate_plan")
        plan = PlanGenerator(self.pd)
        self.assertEqual(len(plan.generated_plan), 30)


if __name__ == '__main__':
    unittest.main()
