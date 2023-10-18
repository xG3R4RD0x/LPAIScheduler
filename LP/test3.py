import pulp


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

# definicion de variables basadas en datos proporcionados
# me baso en esto para crear las variables

subjects = ["Math", "Literature", "Chemistry"]
total_time = range(1, 60+1)
hours_per_day = 8
horas_por_materia = {"Math": 85,
                     "Literature": 90, "Chemistry": 65}

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


# soft constraints


# Resolver el problema
problema.solve()

# Imprimir resultados
print("Estado:", pulp.LpStatus[problema.status])

# Imprimir el horario de estudio
print("\nHorario de Estudio:")
for dia in total_time:
    print(f"Día {dia}:")
    for materia in subjects:
        print(f"{materia}: ", end="")
        horas_asignadas = [hora for hora in range(
            1, hours_per_day + 1) if x[(dia, materia, hora)].varValue == 1]
        print(horas_asignadas)
