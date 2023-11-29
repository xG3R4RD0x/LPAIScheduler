import chat_util as cu
from problem_data import ProblemData
from preprocessing import bag_of_words, preprocess_text
from model import NeuralNet
from generate_plan import PlanGenerator as pg
import json
import torch
from flask_socketio import SocketIO
import threading


message_in = False
message = None
condition = threading.Condition()


def enter_message(input_text):
    global message
    global message_in
    with condition:
        message_in = True
        print("enter message function")
        message = input_text
        condition.notify()


def await_for_message():
    global message_in
    with condition:
        while not message_in:
            condition.wait()
        message_in = False
        return message


def send_output(socket, output):
    socket.emit('chatbot_output', output)


def start_chat():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    with open('./NLP/intents.json', 'r') as f:
        intents = json.load(f)

    FILE = "./NLP/data.pth"
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

    print("Let's chat!, Let me help you, build your study plan")

    problem_data = ProblemData()
    problem_data.set_current_context("Main")

    while True:

        sentence = input('You: ')
        # adding subject information hotfix
        if "Name" in problem_data.current_context or "UTime" in problem_data.current_context:
            sentence = cu.force_unit_string(sentence)
        elif "Unit" in problem_data.current_context:
            sentence = cu.force_utime_string(sentence)

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

            if cu.check_context(problem_data.current_context, new_context):

                if problem_data.add_info_to_subject is True:
                    # print("add_info enabled")
                    # sacamos la lista de subjects como stack
                    # agregamos al contexto nuevo el primer subject del stack
                    # se va eliminar el elemento de la lista después de poner todos los datos
                    # esto va a seguir hasta que se cambie la flag
                    subject_list = problem_data.get_subject_list()
                    # unimos la materia con un espacio para que detecte el contexto
                    new_context = new_context + " " + subject_list[0]

                # cambiar el contexto a por materia

                ##################
                response = cu.handle_input(new_context, problem_data.current_context, problem_data.context_temp,
                                           problem_data.current_context_temp, problem_data, input_str)
                # current_context_update
                if problem_data.subject_list == [] and ("Unit" in problem_data.current_context or "UTime" in problem_data.current_context):
                    problem_data.set_current_context("Main")
                else:
                    problem_data.set_current_context(new_context)

                # breaks while and goes to generator if everything is complete
                if problem_data.complete == True:
                    break
                # print handler responses
                print(
                    f"{botname} (Tag: {intent_tag}, Constraint: {constraint_type})\n"+response)

            else:
                # siempre que se salga del arbol asumimos que quiere regresarse a Main
                # guardamos el contexto que acaba de entrar para después de que el usuario confirme el back_to_main

                # we back up the new and current contexts in case of going back
                problem_data.set_context_temp(new_context)
                problem_data.set_current_context_temp(
                    problem_data.current_context)
                print(
                    f"new_context:{new_context}, current_context:{problem_data.current_context}")
                print(f"{botname}: no pasó el check context ")
                response = cu.handle_input(
                    "Main", problem_data.current_context, problem_data.context_temp, None, problem_data)
                print(response)
                problem_data.set_current_context = "Main"
        else:
            # cuando no se entiende el contexto
            # mostramos el string con los datos que faltan y pedimos que se los llene
            missing_fields = problem_data.validate_data()
            # revisar la respuesta anterior basada en el current context

            response = cu.generate_response(
                missing_fields, problem_data)

            print(f"{botname}: Sorry... I didn't get that.\n{response}")

    if problem_data.complete == True:
        # Generate Study Plan
        generated_plan = pg(problem_data)
