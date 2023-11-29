
        var socket = io.connect('http://' + document.domain + ':' + location.port);

        function getUserInput() {
            // Solicita la entrada del usuario al servidor
            socket.emit('get_user_input');
        }

        function chatbot_start(){
            //sends first event after loading the page at the start
            socket.emit('chatbot_start');

        }

        function send_user_input(){
        var input = document.getElementById('message-input');
        var input_text = input.value.trim();
        console.log("este es el input:"+ input_text);
        socket.emit('send_user_input',input_text);
        input.value=""
        }

        function page_loaded(){
            console.log('Chatbot started');
            socket.emit('chatbot_start');
        }
        
//Event handlers

        socket.once('chatbot_start_from_server', function(output){
            //output of initial message
            var ul = document.getElementById('messages');
            var li = document.createElement('li');
            li.appendChild(document.createTextNode(output));
            ul.appendChild(li);
            //emit event get_user_input
            socket.emit('get_user_input');
        });

        socket.on('chatbot_output', function (output) {
            // Muestra la entrada del usuario en la página
            var ul = document.getElementById('messages');
            var li = document.createElement('li');
            li.appendChild(document.createTextNode("LPAIbot: "+ output));
            ul.appendChild(li);
        });

        socket.on('user_input', function (inputText) {
            // Muestra la entrada del usuario en la página
            var ul = document.getElementById('messages');
            var li = document.createElement('li');
            li.appendChild(document.createTextNode("You: "+ inputText));
            ul.appendChild(li);
            socket.emit('get_response',inputText);
        });

        socket.on('generated_plan', function(study_plan){
            


        });

    