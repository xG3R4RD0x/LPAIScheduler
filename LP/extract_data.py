import pulp
 

def extract_data(ProblemData):
    


data = {
    "hard_constraints": {
        "start_date": None,  # esto debe ser una fecha con string
        "end_date": None,  # Fecha limite
        "number_of_subjects": None,
        "subjects": [],
        "total_time": None,  # default 30 days
        "hours_per_day": 8,  # default 8hours per day
        "duration_of_hour": 45,  # default 45 min y 15min de descanso entre horas
    },
    "soft_constraints": {
        "no_study_days": [],
        "no_study_hours": []
    }
}

example_data = {
    "hard_constraints": {
        "number_of_subjects": 3,
        "subjects":
            [{"name": "Math", "number_of_units": 4, "hours_per_unit": 2},
             {"name": "Literature", "number_of_units": 5, "hours_per_unit": 2},
             {"name": "Chemistry", "number_of_units": 10, "hours_per_unit": 1}],
            "total_time": 30,
            "hours_per_day": 8,
        "duration_of_hour": 45
    }}
