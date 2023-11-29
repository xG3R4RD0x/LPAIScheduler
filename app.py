from flask import Flask, render_template
from flask_socketio import SocketIO
from backend_test import test

app = Flask(__name__)
socketio = SocketIO(app)

# Variable global para almacenar la entrada del usuario
user_input = None


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('get_user_input')
def get_user_input():
    global user_input
    # Envia la solicitud al cliente para obtener la entrada del usuario
    socketio.emit('request_user_input')

    # Espera hasta que se reciba la entrada del usuario desde el frontend
    while user_input is None:
        socketio.sleep(1)

    # Envia la entrada del usuario al cliente
    socketio.emit('user_input', user_input)

    # Restablece la variable de entrada del usuario
    user_input = None


@socketio.on('send_user_input')
def send_user_input(input_text):

    # send input from frontend to backend
    test.enter_message(input_text)

    # # Envia la entrada del usuario al cliente
    socketio.emit('user_input', input_text)


@socketio.on('chatbot_start')
def chatbot_start():
    # es el evento inicial que inicia el chatbot después de cargar la pagina
    # iniciar chatbot
    socket = socketio
    socketio.start_background_task(test.chatbot_dummy_dos, socket)


if __name__ == '__main__':
    socketio.run(app, debug=True)
