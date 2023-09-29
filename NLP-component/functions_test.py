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

    def test_generate_response(self):
        missing_fields = self.data.validate_data()
        checked_fields = cu.read_missing_fields(missing_fields)

        response_options = [
            "We are doing great so far! \n But I still need you to tell me {checked_fields} before we can go on",
            "Awesome! \n But I still need you to tell me {checked_fields} before we can go on",
            "Thanks for the info! \n But I still need {checked_fields} to be able to do your plan :) ",
            "To proceed, I still need you to give me {checked_fields}",
            "We're making progress! However, I still require {checked_fields} before we can proceed.",
            "Great job! Nonetheless, I still need you to provide {checked_fields} before we can continue.",
            "Thank you for the information! Nevertheless, I still need {checked_fields} to proceed with your plan.",
            "To move forward, I still need you to furnish {checked_fields}."
        ]
        # make checked_fields to string

        checked_fields_str = ""

        # makes a String with all the checked fields
        for field in checked_fields:
            if type(field) is dict:
                # checks the dictionary
                if "subjects" in field:
                    checked_fields_str = checked_fields_str[:-2]
                    checked_fields_str += " and in the Subjects: \n"
                    # iterates through the subject_list
                    for subjects in field["subjects"]:
                        for sub in subjects:
                            checked_fields_str += sub
            else:
                checked_fields_str += field
        response_options_checked = []
        for option in response_options:
            option = option.replace("{checked_fields}", checked_fields_str)
            response_options_checked.append(option)

        response = cu.generate_response(missing_fields)
        if response in response_options_checked:
            response_in_options = True
        else:
            response_in_options = False
        self.assertTrue(response_in_options)

    def test_check_context(self):
        new_context = "Subject"
        current_context = "Main"
        check_context = cu.check_context(current_context, new_context)
        self.assertTrue(check_context)

    def test_check_context_subject(self):
        new_context = "Unit Math"
        current_context = "Name"
        check_context = cu.check_context(current_context, new_context)
        self.assertTrue(check_context)

    def test_validate_subject(self):
        missing_fields_subjects = self.data.validate_subjects()
        # print(missing_fields_subjects)
        self.assertEqual(type(missing_fields_subjects), list)

    def test_handle_context_back_to_main(self):
        current_context = "Unit Math"
        context_temp = "Subject"
        response = cu.handle_context_back_to_main(
            current_context, context_temp)
        self.assertEqual(type(response), str)

    def test_handle_input_denial(self):
        current_context = "Back to Main"
        context_temp = "Unit Math"
        Problem_data = self.data
        response = cu.handle_input(
            "Denial", current_context, context_temp, None, Problem_data)
        # print(response)
        self.assertEqual(type(response), str)

    def test_handle_input_main(self):
        current_context = "Main"
        new_context = "Main-total_time"
        Problem_data = self.data
        response = cu.handle_input(
            new_context, current_context, None, None, Problem_data)
        print(response)
        self.assertEqual(type(response), str)

    # mf means missing fields

    def test_generate_response_individual_subject_with_mf(self):
        problem_data = self.data
        subject_context = "Unit Math"
        response = cu.generate_response_individual_subject(
            subject_context, problem_data)
        # print(response)
        self.assertTrue(type(response), str)
    # mf means missing fields

    def test_generate_response_individual_subject_wo_mf(self):
        sub_info = {
            "name": "Math",
            "number_of_units": 10,
            "hours_per_unit": 3
        }
        du.update_subject(self.test_sub, sub_info)
        problem_data = self.data
        subject_context = "Unit Math"
        response = cu.generate_response_individual_subject(
            subject_context, problem_data)
        # print(response)
        self.assertTrue(type(response), str)


if __name__ == '__main__':
    unittest.main()
