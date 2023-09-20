import random
import json
import torch
from model import NeuralNet
from preprocessing import bag_of_words, preprocess_text

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

print("Let's chat!, tell me what you need")

while True:
    sentence = input('You: ')
    if sentence == "quit":
        break

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
        for intent in intents["intents"]:
            # aquí debo poner el codigo para las subpreguntas para las materias y horas con un if
            # puedo hacer que entre a un estado de subpregunta con un while true y salir si con una intent de salir de la subpregunta (gracias u otra materia)

            ###
            # if intent_tag == materias:
            # ***entrar a las subpreguntas de materias
            # if intent_tag == días que no se pueden || horas que no se pueden
            # *** preguntar si es un evento recurrente
            # ** else que siga normal
            # if intent_tag == "Number of Subjects":
            #     print(
            #         f"{botname} (Tag: {intent_tag}, Constraint: {constraint_type}): {random.choice(intent['responses'])}")
            #     print(
            #         f"{botname} (Tag: {intent_tag}, Constraint: {constraint_type}): {random.choice(intent['responses'])}")

            if intent_tag == intent["tag"]:
                print(
                    f"{botname} (Tag: {intent_tag}, Constraint: {constraint_type}): {random.choice(intent['responses'])}")
    else:
        print(f"{botname}: Sorry... I didn't get that")
