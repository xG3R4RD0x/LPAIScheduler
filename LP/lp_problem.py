import pulp


class LPProblem:
    def __init__(self, name):
        self.problem = pulp.LpProblem(name, pulp.LpMaximize)
        self.constraints = []

    def add_variable(self, name, low_bound=0, up_bound=1, cat=pulp.LpInteger):
        return pulp.LpVariable(name, low_bound, up_bound, cat=cat)

    def add_constraint(self, variable, expression, sense, rhs, name):
        constraint = pulp.LpConstraint(
            variable=variable,
            e=expression,
            sense=sense,
            rhs=rhs,
            name=name
        )
        self.constraints.append(constraint)
        self.problem.addConstraint(constraint)

    def set_objective(self, expression):
        self.problem += expression

    def solve(self):
        self.problem.solve()

    def get_status(self):
        return pulp.LpStatus[self.problem.status]

    def get_variable_value(self, variable):
        return variable.varValue


if __name__ == "__main__":
    lp_problem = LPProblem("MyLPProblem")

    # Example: Adding Variables
    x = lp_problem.add_variable("x")
    y = lp_problem.add_variable("y")

    # Example: Setting Objective
    lp_problem.set_objective(2 * x + 3 * y)

    # Example: Adding Constraints
    lp_problem.add_constraint(x, x + y, pulp.LpConstraintLE, 5, "Constraint1")
    lp_problem.add_constraint(
        y, x - 2 * y, pulp.LpConstraintGE, 2, "Constraint2")

    # Solve the problem
    lp_problem.solve()

    # Get the status
    status = lp_problem.get_status()
    print("Status:", status)

    # Get variable values
    x_value = lp_problem.get_variable_value(x)
    y_value = lp_problem.get_variable_value(y)
    print("x =", x_value)
    print("y =", y_value)
