
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

        function generarTabla(horario) {
            horario = JSON.parse(horario);
            horario = transpose(horario);
            
            // Crear el contenedor de la tabla
            var tableContainer = document.getElementById('studyplan-container');
        
            // Crear la tabla
            var table = document.createElement('table');
            var tbody = document.createElement('tbody');
        
            for (var i = 0; i < horario.length; i++) {
                if (i ==0){
                    var header = document.createElement('tr');
                    header.className="day-number";
                    for(var d=0;d<horario[i].length; d++){
                        var day_header = document.createElement('td');
                        day_header.textContent= "day " + (d+1).toString();
                        header.appendChild(day_header);
                    }
                    tbody.appendChild(header);
                }
                var row = document.createElement('tr');
                
                for (var j = 0; j < horario[i].length; j++) {
                    var cell = document.createElement('td');
                    cell.textContent = horario[i][j] || '---'; // si es nulo, mostramos un guion
                    row.appendChild(cell);
                }
        
                tbody.appendChild(row);
            }
        
            table.appendChild(tbody);
        
            tableContainer.appendChild(table);
        
        }

          function transpose(matrix) {
            return matrix[0].map((col, i) => matrix.map(row => row[i]));
        }

        
//Event handlers

        socket.on('chatbot_start_from_server', function(output){
            //output of initial message
            var ul = document.getElementById('messages');
            var li = document.createElement('li');
            li.appendChild(document.createTextNode(output));
            ul.appendChild(li);
            //emit event get_user_input
            socket.emit('get_user_input');
        });

        socket.on('chatbot_output', function (output) {
            // Shows Chatbot output in Frontend
            var ul = document.getElementById('messages');
            var li = document.createElement('li');
            li.appendChild(document.createTextNode("LPAIbot: "+ output));
            ul.appendChild(li);
        });

        socket.on('user_input', function (inputText) {
            // Shows User Input on Frontend
            var ul = document.getElementById('messages');
            var li = document.createElement('li');
            li.appendChild(document.createTextNode("You: "+ inputText));
            ul.appendChild(li);
            socket.emit('get_response',inputText);
        });

        socket.on('generated_plan', function(study_plan){
            generarTabla(study_plan);
        });

    