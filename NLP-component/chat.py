import random
import json
import torch
from model import NeuralNet
from preprocessing import bag_of_words, preprocess_text

device = torch.device('cude' if torch.cuda.is_available() else 'cpu')

with open('./NLP-component/intents.json', 'r') as f:
    intents = json.load(f)


FILE = "./NLP-component/data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data["all_words"]
tags = data["tags"]
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
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

    output = model(x)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]

    # check the probabilities
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    if prob.item() > 0.75:
        for intent in intents["intents"]:
            if tag == intent["tag"]:
                print(f"{botname}: {random.choice(intent['responses'])}")
    else:
        print(f"{botname}: Sorry... I didn't get that")
