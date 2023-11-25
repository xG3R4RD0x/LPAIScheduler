import pulp
from problem_data import ProblemData
import extract_data as ed


class PlanGenerator:
    def __init__(self, pd: ProblemData):
        self.problem_data = pd

        extracted_data = ed.extract_data(self.problem_data)

        subjects = extracted_data["subjects"]
        total_time = extracted_data["total_time"]
        hours_per_day = extracted_data["hours_per_day"]
        horas_por_materia = extracted_data["hours_per_subject"]
        no_study_days_constraints = extracted_data["no_study_days"]
        no_study_hours_constraints = extracted_data["no_study_hours"]

        # Matriz del Horario
        self.generated_plan = [[None for _ in range(
            hours_per_day)] for _ in range(len(total_time))]

        # Datos proporcionados
        data = {
            "hard_constraints": {
                "number_of_subjects": 3,
                "subjects": [
                    {"name": "Math", "number_of_units": 8, "hours_per_unit": 2},
                    {"name": "Literature", "number_of_units": 10, "hours_per_unit": 2},
                    {"name": "Chemistry", "number_of_units": 10, "hours_per_unit": 2}
                ],
                "total_time": 30,
                "hours_per_day": 8,
                "duration_of_hour": 45
            }
        }

        # creamos el problema
        problema = pulp.LpProblem("PlanificacionEstudio", pulp.LpMaximize)

        # es como crear un horario vacio pero para cada materia por separado
        # me refiero a una tabla con todos los días y slots de 8h para cada materia
        x = pulp.LpVariable.dicts("Horas", [(dia, materia, hora) for dia in total_time for materia in subjects for hora in range(1, hours_per_day + 1)],
                                  lowBound=0, upBound=1, cat=pulp.LpInteger)

        # Define las variables de decisión: horas libres por día
        # es un valor que indica el numero de horas libres por día
        horas_libres = pulp.LpVariable.dicts(
            "HorasLibres", total_time, lowBound=0, upBound=hours_per_day, cat=pulp.LpInteger)

        ## Hard Constraints##

        # Restricción para evitar estudiar más de dos horas seguidas de la misma materia
        for dia in total_time:
            for materia in subjects:
                for hora in range(1, hours_per_day):
                    problema += x[(dia, materia, hora)] + \
                        x[(dia, materia, hora + 1)] <= 1

        # Restricción de disponibilidad de tiempo total por día
        for dia in total_time:
            problema += pulp.lpSum(x[(dia, materia, hora)] for materia in subjects for hora in range(
                1, hours_per_day + 1)) == hours_per_day - horas_libres[dia]

        # Restricción de duración total de estudio por materia
        #
        # pupl.lpSum lo que hace es sumar todas las variables de decisión y compararla con el valor deseado
        # en este caso hacemos esto para cada materia y sumamos todas las variables de decision y deben dar el numero max por materia
        for materia in subjects:
            problema += pulp.lpSum(x[(dia, materia, hora)] for dia in total_time for hora in range(
                1, hours_per_day + 1)) == horas_por_materia[materia]

        # Restricción para evitar que se estudie más de una materia a la vez
        # es una restriccion que se ejerce en cada hora para comprobar que no se
        # estudien dos materias al mismo tiempo en una hora
        # usa pulp.lpsum para calcular la variable de decision x para cada materia en un día y hora específicos
        # en este caso solo puede haber una materia en ese día y hora así que debe ser igual o menor a 1
        for dia in total_time:
            for hora in range(1, hours_per_day + 1):
                problema += pulp.lpSum(x[(dia, materia, hora)]
                                       for materia in subjects) <= 1

        for nsd in no_study_days_constraints:
            for dia in total_time:
                # definimos el día a no estudiar
                if dia == nsd["day"]:

                    # se revisa la sumatoria de todas las materias para todas las horas del día especificado
                    # esto tiene que matchear con el valor que pongamos
                    # un día que no se estudia tiene todas las materias y horas en 0
                    # así que el problema se premia cuando es cero
                    # si la suma da 0 se le suma el peso y este valor debe ser igual al peso
                    # eso quiere decir que 0+peso == peso
                    # y se recompensa al problema con ese valor
                    problema += pulp.lpSum(x[(dia, materia, hora)] for materia in subjects for hora in range(
                        1, hours_per_day + 1))+nsd["weight"] == nsd["weight"], f"No_study_day_constraint_{dia}"

        # no_study_hours
        for nsh in no_study_hours_constraints:
            for dia in total_time:
                if dia == nsh["day"]:
                    for materia in subjects:
                        for hora in range(1, hours_per_day+1):
                            if hora == nsh["hour"]:
                                problema += (pulp.lpSum(x[(dia, materia, hora)]
                                                        for materia in subjects) + nsh["weight"]) == nsh["weight"], f"No_study_hours_constraint_{dia}_{hora}_{materia}"

        # Resolver el problema
        problema.solve()

        # Imprimir resultados
        print("Estado:", pulp.LpStatus[problema.status])

        # Llenar la matriz con el horario
        for dia in total_time:
            for hora in range(1, hours_per_day + 1):
                for materia in subjects:
                    if x[(dia, materia, hora)].varValue == 1:
                        self.generated_plan[dia - 1][hora - 1] = materia

        print(self.generated_plan)

        # # Imprimir el horario de estudio
        # print("\nHorario de Estudio:")
        # for dia in total_time:
        #     print(f"Día {dia}:")
        #     for materia in subjects:
        #         print(f"{materia}: ", end="")
        #         horas_asignadas = [hora for hora in range(
        #             1, hours_per_day + 1) if x[(dia, materia, hora)].varValue == 1]
        #         print(horas_asignadas)

        # example_data = {'subjects': ['Math', 'Literature', 'Chemistry'],
        #                 'total_time': range(1, 31),
        #                 'hours_per_day': 8,
        #                 'hours_per_subject': {'Math': 50, 'Literature': 36, 'Chemistry': 40},
        #                 'start_date': [datetime.datetime(2023, 7, 1, 0, 0)],
        #                 'no_study_days': [{'weight': 5, 'day': 15},
        #                                   {'weight': 5, 'day': 16}],
        #                 'no_study_hours': [{'weight': 50, 'day': 25, 'hour': 6},
        #                                    {'weight': 50, 'day': 25, 'hour': 7},
        #                                    {'weight': 50, 'day': 25, 'hour': 8}]}
