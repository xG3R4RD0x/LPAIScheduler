import json
import numpy as np


import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from model import NeuralNet


from preprocessing import preprocess_text, bag_of_words


with open('./NLP-component/intents.json', 'r') as f:
    intents = json.load(f)

    all_words = []
    tags = []
    xy = []

    for intent in intents['intents']:
        tag = intent['tag']
        tags.append(tag)
        for pattern in intent['patterns']:
            text = pattern['text']
            constraint_type = pattern['constraint_type']
            w = preprocess_text(text)
            all_words.extend(w)
            xy.append((w, tag, constraint_type))

    all_words = sorted(set(all_words))  # to avoid duplicates
    tags = sorted(set(tags))  # unique labels, just in case

    x_train = []
    y_train_intent = []
    y_train_constraint = []

    # I fill the length of the list to match with every pattern sentence
    max_length = max(len(pattern_sentence) for pattern_sentence, _, _ in xy)

    for (pattern_sentence, tag, constraint_type) in xy:
        bag = bag_of_words(pattern_sentence, all_words)

        while len(bag) < max_length:
            bag.append(0)

        x_train.append(bag)

        label_intent = tags.index(tag)
        y_train_intent.append(label_intent)

        #  0 para 'none', 1 para 'weak', 2 para 'strong'
        if constraint_type == 'none':
            label_constraint = 0
        elif constraint_type == 'weak':
            label_constraint = 1
        elif constraint_type == 'strong':
            label_constraint = 2
        else:
            raise ValueError(
                f'Tipo de restricción desconocido: {constraint_type}')

        y_train_constraint.append(label_constraint)

x_train = np.array(x_train)
y_train_intent = np.array(y_train_intent)
y_train_constraint = np.array(y_train_constraint)


class ChatDataset(Dataset):
    def __init__(self):
        self.n_samples = len(x_train)
        self.x_data = x_train
        self.y_data_intent = y_train_intent
        self.y_data_constraint = y_train_constraint
    # Dataset[index]

    def __getitem__(self, index):
        return self.x_data[index], self.y_data_intent[index], self.y_data_constraint[index]

    def __len__(self):
        return self.n_samples

# hyperparameters


batch_size = 8
hidden_size = 8
input_size = len(x_train[0])
output_size_intent = len(tags)
output_size_constraint = 3
learning_rate = 0.001
num_epochs = 1000

dataset = ChatDataset()

train_loader = DataLoader(
    dataset=dataset, batch_size=batch_size, shuffle=True, num_workers=0)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model = NeuralNet(input_size, hidden_size,
                  output_size_intent, output_size_constraint)

# Loss y optimizer
criterion_intent = nn.CrossEntropyLoss()
criterion_constraint = nn.CrossEntropyLoss()

optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

for epoch in range(num_epochs):
    for (words, labels_intent, labels_constraint) in train_loader:
        words = words.to(device)
        labels_intent = labels_intent.to(device, dtype=torch.int64)
        labels_constraint = labels_constraint.to(device, dtype=torch.int64)

        # Forward pass
        intent_out, constraint_out = model(words)

        # Calcular las pérdidas
        loss_intent = criterion_intent(intent_out, labels_intent)
        loss_constraint = criterion_constraint(
            constraint_out, labels_constraint)

        # Calcular la pérdida total
        total_loss = loss_intent + loss_constraint

        # Backpropagation y optimización
        optimizer.zero_grad()
        total_loss.backward()
        optimizer.step()

    if (epoch+1) % 100 == 0:
        print(
            f'Epoch [{epoch+1}/{num_epochs}], Loss Intent: {loss_intent.item():.4f}, Loss Constraint: {loss_constraint.item():.4f}')

print(
    f'Final Loss Intent: {loss_intent.item():.4f}, Final Loss Constraint: {loss_constraint.item():.4f}')


# Save the Data

data = {
    "model_state": model.state_dict(),
    "input_size": input_size,
    "output_size_intent": output_size_intent,
    "output_size_constraint": output_size_constraint,
    "hidden_size": hidden_size,
    "all_words": all_words,
    "tags": tags,
    "constraint_types": ["none", "weak", "strong"]

}

FILE = "./NLP-component/data.pth"
torch.save(data, FILE)

print(f'training complete, file saved to {FILE}')
