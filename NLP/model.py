import torch
import torch.nn as nn


class NeuralNet(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes, constraint_classes):
        super(NeuralNet, self).__init__()
        self.l1 = nn.Linear(input_size, hidden_size)
        self.l2 = nn.Linear(hidden_size, hidden_size)
        self.l3 = nn.Linear(hidden_size, num_classes)
        # capa adicional para clasificar constraints
        self.l4 = nn.Linear(hidden_size, constraint_classes)
        self.relu = nn.ReLU()

    def forward(self, x):
        out = self.l1(x)
        out = self.relu(out)
        out = self.l2(out)
        out = self.relu(out)
        out1 = self.l3(out)  # salida para la clasificación original
        out2 = self.l4(out)  # salida para la clasificación de constraints
        return out1, out2
