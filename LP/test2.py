import pulp

# Define el problema de programación lineal
problema = pulp.LpProblem("PlanificacionEstudio", pulp.LpMaximize)

# Define las materias, días de estudio y horas por materia
materias = ["Matematicas", "Fisica", "Quimica"]
dias_estudio = range(1, 60)
horas_por_materia = {"Matematicas": 85,
                     "Fisica": 90, "Quimica": 65}
horas_por_dia = 8

# Define las variables de decisión: horas de estudio por materia, día y hora
x = pulp.LpVariable.dicts("Horas", [(dia, materia, hora) for dia in dias_estudio for materia in materias for hora in range(1, horas_por_dia + 1)],
                          lowBound=0, upBound=1, cat=pulp.LpInteger)

# Define las variables de decisión: horas libres por día
horas_libres = pulp.LpVariable.dicts(
    "HorasLibres", dias_estudio, lowBound=0, upBound=horas_por_dia, cat=pulp.LpInteger)

# Define las variables de decisión para las restricciones débiles
restricciones_debiles = pulp.LpVariable.dicts(
    "RestriccionDebil", range(1, 4), cat=pulp.LpBinary)  # 1, 2 y 3 restricciones débiles

# Define la función objetivo: maximizar la cantidad de restricciones débiles cumplidas
problema += pulp.lpSum(restricciones_debiles[i]
                       for i in range(1, 4)), "Maximize_Restricciones_Debiles"

# Restricción para evitar estudiar más de dos horas seguidas de la misma materia
for dia in dias_estudio:
    for materia in materias:
        for hora in range(1, horas_por_dia):
            problema += x[(dia, materia, hora)] + \
                x[(dia, materia, hora + 1)] <= 1

# Restricción de disponibilidad de tiempo total por día
for dia in dias_estudio:
    problema += pulp.lpSum(x[(dia, materia, hora)] for materia in materias for hora in range(
        1, horas_por_dia + 1)) == horas_por_dia - horas_libres[dia]

# Restricción de duración total de estudio por materia
for materia in materias:
    problema += pulp.lpSum(x[(dia, materia, hora)] for dia in dias_estudio for hora in range(
        1, horas_por_dia + 1)) == horas_por_materia[materia]

# Restricción para evitar que se estudie más de una materia a la vez
for dia in dias_estudio:
    for hora in range(1, horas_por_dia + 1):
        problema += pulp.lpSum(x[(dia, materia, hora)]
                               for materia in materias) <= 1

# Restricciones débiles

# Restricción: Tener al menos 2 horas libres al día
for dia in dias_estudio:
    problema += horas_libres[dia] >= 2  # Restricción débil

# Restricción: Martes no puede estudiar la 3 y 4 hora
for materia in materias:
    problema += x[(3, materia, 3)] + x[(3, materia, 4)
                                       ] == 0  # Restricción débil para martes

# Restricción: Viernes solo se estudien las 5 primeras horas
for materia in materias:
    for hora in range(6, horas_por_dia + 1):
        # Restricción débil para viernes
        problema += x[(5, materia, hora)] == 0

# Resolver el problema
problema.solve()

# Imprimir resultados
print("Estado:", pulp.LpStatus[problema.status])

# Imprimir el horario de estudio
print("\nHorario de Estudio:")
for dia in dias_estudio:
    print(f"Día {dia}:")
    for materia in materias:
        print(f"{materia}: ", end="")
        horas_asignadas = [hora for hora in range(
            1, horas_por_dia + 1) if x[(dia, materia, hora)].varValue == 1]
        print(horas_asignadas)
