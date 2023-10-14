import chat_util as cu
import torch
import unittest
import json
from model import NeuralNet
from preprocessing import bag_of_words, preprocess_text
from problem_data import ProblemData
from subject import Subject
import data_util as du


class ChatTest(unittest.TestCase):
    def setUp(self):
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.device = device

        with open('./NLP-component/intents.json', 'r') as f:
            intents = json.load(f)

        FILE = "./NLP-component/data.pth"
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
        sentence = "I want to do 3 Exams this semester"
        chat_data = self.input_sentence(
            sentence, self.all_words, self.device, self.tags, self.constraint_types, self.model)
        chat_data_string = chat_data["intent_tag"] + \
            " " + chat_data["constraint_type"]
        print(chat_data_string)

        new_context = chat_data["intent_tag"]

        response = cu.handle_input(new_context, self.current_context, self.context_temp,
                                   self.current_context_temp, self.problem_data, sentence)
        # print(response)
        self.assertTrue(type(chat_data_string))
        self.assertTrue(type(response))

    def test_chat_names(self):
        self.current_context = "Subject"
        self.context_temp = None
        self.current_context_temp = None
        self.problem_data = ProblemData()
        sentence = "Math, Chemistry and Literature"
        chat_data = self.input_sentence(
            sentence, self.all_words, self.device, self.tags, self.constraint_types, self.model)
        chat_data_string = chat_data["intent_tag"] + \
            " " + chat_data["constraint_type"]
        # print(chat_data_string)

        new_context = chat_data["intent_tag"]

        response = cu.handle_input(new_context, self.current_context, self.context_temp,
                                   self.current_context_temp, self.problem_data, sentence)
        # print(response)
        self.assertTrue(type(chat_data_string))
        self.assertTrue(type(response))

    def test_chat_unit(self):
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

    def test_next_subject_existing_next_subject(self):
        self.current_context = "Unit Literature"
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
        print(chat_data_string)

        new_context = chat_data["intent_tag"]+" "+subject_name

        response = cu.handle_input(new_context, self.current_context, self.context_temp,
                                   self.current_context_temp, self.problem_data, sentence)

        # print(response)
        self.assertTrue(type(chat_data_string))
        self.assertTrue(type(response))

    def test_input_sentence(self):
        response = cu.input_sentence(
            " I want to study for 3 Exams this semester")

        print("test_input_sentence\n")
        print(response)
        self.assertTrue(type(response), dict)


###### Test Utility Functions ######


    def create_test_subject(self, problem_data: ProblemData, subject_name: str):
        subject = Subject(subject_name)
        du.add_subject(problem_data, subject)


if __name__ == '__main__':
    unittest.main()
