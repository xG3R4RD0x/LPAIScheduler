import chat_util as cu
import torch
import unittest
import json
from model import NeuralNet
from preprocessing import bag_of_words, preprocess_text
import preprocessing as pre
from problem_data import ProblemData
from subject import Subject
import data_util as du
import datetime
import soft_constraints_util as scu
from soft_constraints import no_study_day, no_study_hours


class ChatTest(unittest.TestCase):
    def setUp(self):
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.device = device

        with open('./NLP/intents.json', 'r') as f:
            intents = json.load(f)

        FILE = "./NLP/data.pth"
        data = torch.load(FILE)
        input_size = data["input_size"]
        hidden_size = data["hidden_size"]
        output_size_intent = data["output_size_intent"]
        output_size_constraint = data["output_size_constraint"]
        all_words = data["all_words"]
        self.all_words = all_words
        tags = data["tags"]
        self.tags = tags

        # Agrega esto para cargar los tipos de restricción
        constraint_types = data["constraint_types"]
        self.constraint_types = constraint_types
        model_state = data["model_state"]

        model = NeuralNet(input_size, hidden_size, output_size_intent,
                          output_size_constraint).to(device)
        model.load_state_dict(model_state)
        model.eval()
        self.model = model
        botname = "LPAIbot"

        self.current_context = "Main"
        self.context_temp = None
        self.current_context_temp = None
        self.problem_data = ProblemData()

    def input_sentence(self, sentence, all_words, device, tags, constraint_types, model):
        sentence = preprocess_text(sentence)
        x = bag_of_words(sentence, all_words)
        x = x.reshape(1, x.shape[0])
        x = torch.from_numpy(x).to(device)

        intent_output, constraint_output = model(x)
        _, predicted_intent = torch.max(intent_output, dim=1)
        intent_tag = tags[predicted_intent.item()]
        _, predicted_constraint = torch.max(constraint_output, dim=1)
        # Obtén el tipo de restricción
        constraint_type = constraint_types[predicted_constraint.item()]

        # check the probabilities
        intent_probs = torch.softmax(intent_output, dim=1)
        intent_prob = intent_probs[0][predicted_intent.item()]

        # Revisa las probabilidades para el tipo de restricción
        constraint_probs = torch.softmax(constraint_output, dim=1)
        constraint_prob = constraint_probs[0][predicted_constraint.item()]
        return {"intent_tag": intent_tag, "constraint_type": constraint_type}

    def test_chat_subject(self):
        print("test_chat_subject:")
        sentence = "I want to do 3 Exams this semester"
        chat_data = self.input_sentence(
            sentence, self.all_words, self.device, self.tags, self.constraint_types, self.model)
        chat_data_string = chat_data["intent_tag"] + \
            " " + chat_data["constraint_type"]
        print(chat_data_string)

        new_context = chat_data["intent_tag"]

        response = cu.handle_input(new_context, self.current_context, self.context_temp,
                                   self.current_context_temp, self.problem_data, sentence)
        print(response)
        self.assertTrue(type(chat_data_string))
        self.assertTrue(type(response))

    def test_chat_names(self):
        print("test_chat_names:")
        self.current_context = "Subject"
        self.context_temp = None
        self.current_context_temp = None
        self.problem_data = ProblemData()
        sentence = "Math, Chemistry and Literature"
        chat_data = self.input_sentence(
            sentence, self.all_words, self.device, self.tags, self.constraint_types, self.model)
        chat_data_string = chat_data["intent_tag"] + \
            " " + chat_data["constraint_type"]
        print(chat_data_string)

        new_context = chat_data["intent_tag"]

        response = cu.handle_input(new_context, self.current_context, self.context_temp,
                                   self.current_context_temp, self.problem_data, sentence)
        print(response)
        self.assertTrue(type(chat_data_string))
        self.assertTrue(type(response))

    def test_chat_unit(self):
        print("test_chatunit:")
        self.current_context = "Name"
        self.context_temp = None
        self.current_context_temp = None
        self.problem_data = ProblemData()
        subject_name = "Literature"
        self.create_test_subject(self.problem_data, subject_name)
        sentence = "This course has 8 Units"
        chat_data = self.input_sentence(
            sentence, self.all_words, self.device, self.tags, self.constraint_types, self.model)
        chat_data_string = chat_data["intent_tag"] + \
            " " + chat_data["constraint_type"]
        print(chat_data_string)

        new_context = chat_data["intent_tag"]+" "+subject_name

        response = cu.handle_input(new_context, self.current_context, self.context_temp,
                                   self.current_context_temp, self.problem_data, sentence)
        print(response)
        self.assertTrue(type(chat_data_string))
        self.assertTrue(type(response))

    def test_chat_time_per_unit(self):
        print("test_chat_time_per_unit:")
        self.current_context = "Unit"
        self.context_temp = None
        self.current_context_temp = None
        self.problem_data = ProblemData()
        subject_name = "Literature"
        self.create_test_subject(self.problem_data, subject_name)
        subject = du.get_subject_by_name(self.problem_data, subject_name)
        self.problem_data.set_subject_list([subject_name])
        du.update_subject(subject, {"number_of_units": 4})
        sentence = "I need 4 hours per Unit"
        chat_data = self.input_sentence(
            sentence, self.all_words, self.device, self.tags, self.constraint_types, self.model)
        chat_data_string = chat_data["intent_tag"] + \
            " " + chat_data["constraint_type"]
        print(chat_data_string)

        new_context = chat_data["intent_tag"]+" "+subject_name

        response = cu.handle_input(new_context, self.current_context, self.context_temp,
                                   self.current_context_temp, self.problem_data, sentence)
        print(response)
        self.assertTrue(type(chat_data_string))
        self.assertTrue(type(response))

    @unittest.skip("está esperando input")
    def test_second_subject(self):
        print("test_second_subject:")
        self.current_context = "UTime Literature"
        self.context_temp = None
        self.current_context_temp = None
        self.problem_data = ProblemData()
        du.add_info(self.problem_data, "number_of_subjects", 2)
        subject_name = "Literature"
        subject_name2 = "Math"
        self.create_test_subject(self.problem_data, subject_name)
        self.create_test_subject(self.problem_data, subject_name2)
        subject = du.get_subject_by_name(self.problem_data, subject_name)
        self.problem_data.set_subject_list([subject_name2])
        du.update_subject(subject, {"number_of_units": 4, "hours_per_unit": 2})
        sentence = "the subject has 4 Units"
        chat_data = self.input_sentence(
            sentence, self.all_words, self.device, self.tags, self.constraint_types, self.model)
        chat_data_string = chat_data["intent_tag"] + \
            " " + chat_data["constraint_type"]
        print(chat_data_string)

        new_context = chat_data["intent_tag"]+" "+subject_name

        response = cu.handle_input(new_context, self.current_context, self.context_temp,
                                   self.current_context_temp, self.problem_data, sentence)
        print(response)
        self.assertTrue(type(chat_data_string))
        self.assertTrue(type(response))

    def test_next_subject_existing_next_subject(self):
        self.current_context = "Unit Math"
        self.context_temp = None
        self.current_context_temp = None
        self.problem_data = ProblemData()
        du.add_info(self.problem_data, "number_of_subjects", 2)
        subject_name = "Math"
        subject_name2 = "Science"
        self.problem_data.set_subject_list(["Math", "Science"])
        self.create_test_subject(self.problem_data, subject_name)
        self.create_test_subject(self.problem_data, subject_name2)
        subject_Math = du.get_subject_by_name(self.problem_data, subject_name)
        du.update_subject(subject_Math, {"number_of_units": 8})
        sentence = "It takes me 5 Hours per Unit"
        chat_data = self.input_sentence(
            sentence, self.all_words, self.device, self.tags, self.constraint_types, self.model)
        chat_data_string = chat_data["intent_tag"] + \
            " " + chat_data["constraint_type"]
        # print(chat_data_string)

        new_context = chat_data["intent_tag"]+" "+subject_name

        response = cu.handle_input(new_context, self.current_context, self.context_temp,
                                   self.current_context_temp, self.problem_data, sentence)

        # print(response)
        self.assertTrue(type(chat_data_string))
        self.assertTrue(type(response))

    def test_input_sentence(self):
        response = cu.input_sentence(
            " I prefer not to study on friday 13th of November")

        print("test_input_sentence\n")
        print(response)
        self.assertTrue(type(response), dict)

    def test_no_study_day(self):
        sentence = "I prefer not to study from July 15th to July 20th "
        print("test_no_study_day\n")
        pd = ProblemData()
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

        nsd_list = pd.data["soft_constraints"]["no_study_days"]

        for nsd in nsd_list:
            self.assertTrue(type(nsd), no_study_day)

    def test_no_study_hour(self):
        pd = ProblemData()
        sentence = "I can't study after 7 PM"
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

        nsh_list = pd.data["soft_constraints"]["no_study_hours"]
        for i in nsh_list:
            print(i.data)
        for nsd in nsh_list:
            self.assertTrue(type(nsd), no_study_day)


###### Test Utility Functions ######

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
