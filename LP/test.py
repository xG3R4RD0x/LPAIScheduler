import pulp

# Crear un problema de programación lineal para la planificación de estudio
problema = pulp.LpProblem("PlanificacionEstudio", pulp.LpMaximize)

# Definir las variables de decisión (horas de estudio por materia y día)
dias = range(1, 31)  # Número de días en el mes
materias = ["Matematicas", "Historia", "Ciencias"]
horas_por_dia = 8

x = pulp.LpVariable.dicts("Horas", [(dia, materia, hora) for dia in dias for materia in materias for hora in range(1, horas_por_dia + 1)],
                          lowBound=0, upBound=1, cat=pulp.LpInteger)

# Definir la función objetivo (maximizar el tiempo total de estudio, si lo deseas)
problema += pulp.lpSum(x[(dia, materia, hora)]
                       for dia in dias for materia in materias for hora in range(1, horas_por_dia + 1))

# Restricción de disponibilidad de tiempo (por ejemplo, 30 horas en total en el mes)
problema += pulp.lpSum(x[(dia, materia, hora)]
                       for dia in dias for materia in materias for hora in range(1, horas_por_dia + 1)) <= 30 * horas_por_dia

# Restricción de partes por materia (por ejemplo, máximo 8 horas por día para cada materia)
for materia in materias:
    for dia in dias:
        problema += pulp.lpSum(x[(dia, materia, hora)]
                               for hora in range(1, horas_por_dia + 1)) <= horas_por_dia

# Restricciones de equidad en la distribución (diferencia máxima de 2 horas)
for dia in dias:
    for materia1 in materias:
        for materia2 in materias:
            if materia1 != materia2:
                for hora in range(1, horas_por_dia + 1):
                    problema += x[(dia, materia1, hora)] - \
                        x[(dia, materia2, hora)] <= 2
                    problema += x[(dia, materia2, hora)] - \
                        x[(dia, materia1, hora)] <= 2

# Restricción para dividir cada día en 8 horas y asignar a cada hora su respectiva hora de estudio
for dia in dias:
    problema += pulp.lpSum(x[(dia, materia, hora)]
                           for materia in materias for hora in range(1, horas_por_dia + 1)) == horas_por_dia

# Restricción de número total de horas por materia
horas_por_materia = {"Matematicas": 80, "Historia": 60, "Ciencias": 70}
for materia in materias:
    problema += pulp.lpSum(x[(dia, materia, hora)] for dia in dias for hora in range(
        1, horas_por_dia + 1)) == horas_por_materia[materia]

# Restricción para no estudiar dos horas seguidas la misma materia
for dia in dias:
    for materia in materias:
        for hora in range(1, horas_por_dia):
            problema += x[(dia, materia, hora)] + \
                x[(dia, materia, hora + 1)] <= 1

# Resolver el problema
problema.solve()

# Imprimir resultados
print("Estado:", pulp.LpStatus[problema.status])

# Crear una tabla para el horario semanal
horario_semanal = {}
for dia in dias:
    horario_semanal[dia] = {materia: [hora for hora in range(
        1, horas_por_dia + 1) if x[(dia, materia, hora)].varValue == 1] for materia in materias}

# Imprimir el horario semanal en forma de tabla
print("\nHorario Semanal:")
print("Día\tMateria\tHoras Asignadas")
for dia in dias:
    for materia in materias:
        horas_asignadas = ", ".join(map(str, horario_semanal[dia][materia]))
        print(f"{dia}\t{materia}\t{horas_asignadas}")
