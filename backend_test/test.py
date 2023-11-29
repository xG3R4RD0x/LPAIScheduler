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


def chatbot_dummy_dos(socket):
    print("chatbot_dummy_dos")
    send_output(socket, "Chat_Iniciado")
    while True:
        message = await_for_message()
        response = "mensaje procesado: " + str(message)
        send_output(socket, response)
