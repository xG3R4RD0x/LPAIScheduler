import pulp


class Constraint:
    def __init__(self, problem):
        self.problem = problem
        self.variables = []  # Almacena las variables involucradas en la restricción
        self.coeficients = []  # Almacena los coeficientes de las variables
        self.operator = None  # Puede ser "<=", ">=" o "=="
        self.value = None  # value del lado derecho de la restricción

    def add_variable(self, variable, coeficient=1):

        # Agrega una variable a la restricción con un coeficiente opcional.

        self.variables.append(variable)
        self.coeficientes.append(coeficient)

    def set_operator(self, operator):

        # Establece el operator de la restricción ("<=", ">=" o "==").
        self.operator = operator

    def set_value(self, value):

        # Establece el value del lado derecho de la restricción.

        self.value = value

    def add_to_problem(self):

        # Agrega la restricción al problem de programación lineal.

        if self.operator == "<=":
            self.problem += pulp.lpSum([self.coeficients[i] * self.variables[i]
                                        for i in range(len(self.variables))]) <= self.value
        elif self.operator == ">=":
            self.problem += pulp.lpSum([self.coeficients[i] * self.variables[i]
                                        for i in range(len(self.variables))]) >= self.value
        elif self.operator == "==":
            self.problem += pulp.lpSum([self.coeficients[i] * self.variables[i]
                                        for i in range(len(self.variables))]) == self.value
