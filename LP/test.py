import pulp

# Crear un problema de programación lineal para scheduling y timetabling
problema = pulp.LpProblem("SchedulingTimetablingEstudio", pulp.LpMaximize)

# Definir las variables de decisión (horas de estudio por día y materia)
dias = range(1, 31)  # Número de días en el mes
materias = ["Matematicas", "Historia", "Ciencias"]

x = pulp.LpVariable.dicts("Horas", [(dia, materia) for dia in dias for materia in materias],
                          lowBound=0, upBound=8, cat=pulp.LpInteger)

# Definir la función objetivo (maximizar el tiempo total de estudio)
problema += pulp.lpSum(x[(dia, materia)]
                       for dia in dias for materia in materias)

# Restricción de disponibilidad de tiempo (por ejemplo, 30 horas en total en el mes)
problema += pulp.lpSum(x[(dia, materia)]
                       for dia in dias for materia in materias) <= 30 * 8

# Restricciones de partes por materia (por ejemplo, máximo 8 horas por día para cada materia)
for materia in materias:
    for dia in dias:
        problema += x[(dia, materia)] <= 8

# Restricciones de equidad en la distribución (diferencia máxima de 2 horas)
for dia in dias:
    problema += x[(dia, "Matematicas")] - x[(dia, "Historia")] <= 2
    problema += x[(dia, "Historia")] - x[(dia, "Matematicas")] <= 2
    problema += x[(dia, "Matematicas")] - x[(dia, "Ciencias")] <= 2
    problema += x[(dia, "Ciencias")] - x[(dia, "Matematicas")] <= 2

# Restricción adicional: la suma de horas en un día no puede ser mayor a 8
for dia in dias:
    problema += pulp.lpSum(x[(dia, materia)] for materia in materias) <= 8

# Resolver el problema
problema.solve()

# Imprimir resultados
print("Estado:", pulp.LpStatus[problema.status])

for dia in dias:
    print(f"Día {dia}:")
    for materia in materias:
        print(f"{materia}: {x[(dia, materia)].varValue} horas")
