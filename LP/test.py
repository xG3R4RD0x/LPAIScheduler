import pulp
# Crea una instancia de un problema de minimización
prob = pulp.LpProblem("MiProblema", pulp.LpMinimize)
# Variables
x = pulp.LpVariable("x", lowBound=0)  # Variable x >= 0
y = pulp.LpVariable("y", lowBound=0)  # Variable y >= 0
# Función objetivo
prob += 2*x + 3*y

# Restricciones
prob += x + y <= 4
prob += 2*x + y >= 2
# Resolver el problema
prob.solve()
# Obtener el estado de la solución
estado = pulp.LpStatus[prob.status]

# Obtener los valores de las variables
valor_x = x.varValue
valor_y = y.varValue

# Obtener el valor óptimo de la función objetivo
valor_optimo = pulp.value(prob.objective)

print(valor_optimo)
