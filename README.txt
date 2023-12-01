This is a README file for the repository LPAIScheduler

1st. install pipreqs from pip to get the dependencies
    pip install pipreqs

2nd install the dependencies from the requirements.txt
    pip intall -r ./requirements.txt
    or run the update_dependecies.py file

IMPORTANT: I'm not using a virtual enviroment so I installed the dependencies globally

3rd. download the language model for spaCy
    python -m spacy download en_core_web_sm

4th. Start webapp running the file app.py
 the app should be hosted in http://127.0.0.1:5000
look at the messages in the console, there is also the address


#### HINWEIS ####
To restart the chat, the web aplication should also be restarted

-due to the small amount of training data used to train this model it only recognizes
basic sentence formulations

-to check if the problem is ready to generate send an empty message to the chatbot
after entering all the needed information



##### NON WORKING SCENARIOS ####

-submitting an empty message instead of the subject names
-sometimes soft constraints are not recognized
-Editing subjects doesn't work properly



