from problem_data import ProblemData
import data_util as du
import chat_util as cu
import preprocessing as pre
from subject import Subject
import unittest


class FunctionsTest(unittest.TestCase):
    def setUp(self):
        self.data = ProblemData()
        self.test_sub = Subject("Math")

        sub_info = {
            "name": "Math",
            "number_of_units": 10,
            "hours_per_unit": None
        }

        # du.update_subject(self.test_sub, sub_info)
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
            "We are going great so far but I still need you to provide {checked_fields} before we can continue.",
            "Thank you for the information! Nevertheless, I still need {checked_fields} to proceed with your plan.",
            "To move forward, I still need you to add {checked_fields}."
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
            print(response)
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
        # print(response)
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

    def test_tag_subjects(self):
        sentence = "I have to study Math chemistry and literature"
        response = pre.tag_subjects(sentence)
        # print("tag_subjects")
        # print(response)
        self.assertEqual(response, ["Math", "Chemistry", "Literature"])

    def test_number_of_subjects(self):

        sentence = "I have 6 exams"
        response = pre.number_from_text(sentence)
        # print("test_number_of_subjects")
        # print(response)
        self.assertEqual(response, 6)

    def test_get_subject_list_from_data(self):
        subject_list = self.data.get_subject_list_from_data()
        print("test_get_subject_list_from_data:\n")
        # print(subject_list)
        self.assertTrue(type(subject_list), list)

    def test_ask_for_subject_data(self):
        subject_name = "Test"
        subject = Subject(subject_name)
        response = cu.ask_for_subject_data(subject)
        assertion_string = "Do you mind adding the following information for "+subject_name+"?"
        # print(response)
        self.assertIn(assertion_string, response)

    def test_subject_complete(self):
        subject_name = "Math"
        du.add_subject(self.data, Subject(subject_name))
        self.data.set_subject_list(["Math"])
        subject = du.get_subject_by_name(self.data, subject_name)
        du.update_subject(subject, {"number_of_units": 7, "hours_per_unit": 4})
        print("test_subject_complete: "+str(subject.get_data()))
        sc = cu.subject_complete(self.data, subject)
        print(sc)
        self.assertTrue(sc)

    def test_tag_dates(self):
        sentence = "I'm not available from July 15th to July 20th for the event but on july 25th I will be available"
        print("test_tag_dates")
        response = pre.tag_date(sentence)
        print(response)
        assertion = [['July 15th', 'July 20th'], 'july 25th']
        self.assertEqual(response, assertion)

    def test_tag_time(self):
        sentence = "The meeting is from 3 PM to 5 PM"
        print("test_tag_time")
        response = pre.tag_time(sentence)
        print(response)
        self.assertTrue(type(sentence), str)

    def test_tag_date_and_time(self):
        sentence = "I can't study after 7 PM"
        print("test_tag_date_and_time")
        time_list = pre.tag_time(sentence)
        # print("time_list: "+str(time_list)+" date_list: "+str(date_list))
        print(str(time_list))
        self.assertTrue(type(sentence), str)

    def test_spacy(self):
        sentence = "The meeting is from 3 PM to 5 PM"
        print("test_spacy")
        pre.test_spacy(sentence)
        self.assertTrue(type(sentence), str)


if __name__ == '__main__':
    unittest.main()
