# an object which has a dictionary to store the parsed data from the chatbot


class ProblemData:
    def __init__(self):
        # Inicializa un diccionario con valores vacios
        self.data = {
            "subjects": [],
            "hard_constraints": {
                "start_date": None,  # esto debe ser una fecha con string
                "end_date": None,  # Fecha limite
                "total_time": 30,  # default 30 days
                "hours_per_day": 8,  # default 8hours per day
                "duration_of_hour": 45,  # default 45 min y 15min de descanso entre horas
            },
            "soft_constraints": {
                "no_study_days": [],
                "no_study_hours": []
            }
        }
