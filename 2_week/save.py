import gurobipy as g

# Example input
S = [100, 50, 50, 50, 20, 20, 10]
n = len(S)

model = g.Model()
x = model.addVars(n, vtype=g.GRB.BINARY)

# minimalizovat rozdil mezi majetky?
# array vlastnictvi xi = 0 => S1, xi = 1 => S2
sum1 = sum(S[i] * x[i] for i in range(n))

model.addConstr(sum1 >= sum(S)/2)
model.setObjective(sum1, sense=g.GRB.MINIMIZE)
model.optimize()

l1 = [S[i] for i in range(n) if x[i].x > 0.5]
l2 = [S[i] for i in range(n) if x[i].x < 0.5]
print(sum(S)/2)
print(sum(l1), l1)
print(sum(l2), l2)

# TODO: implement the model and find the solution