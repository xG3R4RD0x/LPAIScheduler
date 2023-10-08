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
        print(response)
        if response in response_options_checked:
            response_in_options = True
        else:
            response_in_options = False
        self.assertTrue(response_in_options)


if __name__ == '__main__':
    unittest.main()
