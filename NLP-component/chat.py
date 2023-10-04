import random
import json
import torch
from model import NeuralNet
from preprocessing import bag_of_words, preprocess_text
from problem_data import ProblemData
import chat_util as cu
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('./NLP-component/intents.json', 'r') as f:
    intents = json.load(f)


FILE = "./NLP-component/data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size_intent = data["output_size_intent"]
output_size_constraint = data["output_size_constraint"]
all_words = data["all_words"]
tags = data["tags"]


# Agrega esto para cargar los tipos de restricción
constraint_types = data["constraint_types"]
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size_intent,
                  output_size_constraint).to(device)
model.load_state_dict(model_state)
model.eval()

botname = "LPAIbot"

current_context = "Main"
context_temp = None
current_context_temp = None

print("Let's chat!, Let me help you, build you study plan")

problem_data = ProblemData()

while True:
    sentence = input('You: ')
    if sentence == "quit":
        break
    # we save the input sentence to extract the information
    input_str = sentence
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

    if intent_prob.item() > 0.75:

        new_context = intent_tag

        if cu.check_context(current_context, new_context):

            cu.handle_input(new_context, current_context, context_temp,
                            current_context_temp, problem_data.data)
            # current_context_update
            current_context = new_context

            # tengo que hacer una función que revise los datos que se acaban
            # de ingresar, los analice y agregue al problem data
            # por ejemplo si ingresa el nombre de las materias que les haga tokens
            # y las ingrese uno por uno y cambie a un nuevo contexto

            # tengo que hacer una función que devuelva una respuesta en base
            # al contexto que se acaba de ingresar

            print(
                f"{botname} (Tag: {intent_tag}, Constraint: {constraint_type}): response_place_holder")
        else:
            # siempre que se salga del arbol asumimos que quiere regresarse a Main
            # guardamos el contexto que acaba de entrar para después de que el usuario confirme el back_to_main

            # we back up the new and current contexts in case of going back
            context_temp = new_context
            current_context_temp = current_context
            print(
                f"new_context:{new_context}, current_context:{current_context}")
            print(f"{botname}: no pasó el check context ")
            cu.handle_input(
                "Back_to_Main", current_context, context_temp)
            current_context = "Back_to_Main"
    else:
        # cuando no se entiende el contexto
        # mostramos el string con los datos que faltan y pedimos que se los llene
        missing_fields = data.validate_data()
        response = cu.generate_response(missing_fields)

        print(f"{botname}: Sorry... I didn't get that.\n{response}")
