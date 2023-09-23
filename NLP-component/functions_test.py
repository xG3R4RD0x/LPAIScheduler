from problem_data import ProblemData
import data_util as du
import chat_util as cu
from subject import Subject
import unittest


class FunctionsTest(unittest.TestCase):
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

    def test_testeo(self):
        result = self.data.testeo()  # Llamando al método testeo de la instancia data
        # Reemplaza expected_value con el valor esperado
        self.assertEqual(result, ['start_date', 'total_time', {
                         'subjects': [(0, ['hours_per_unit'])]}])

    def test_generate_response(self):
        missing_fields = self.data.validate_data
        response = cu.generate_response(missing_fields)
        self.assertEqual(
            response, "can u fill up the information missing please?")

    def test_check_context(self):
        new_context = "Subject"
        current_context = "Main"
        check_context = cu.check_context(current_context, new_context)
        self.assertTrue(check_context)


if __name__ == '__main__':
    unittest.main()
