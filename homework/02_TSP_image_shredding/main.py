#!/usr/bin/env python3
import sys
import gurobipy as g
import numpy

def find_subtours(edges, n):
    visited = [False] * n
    subtours = []

    for start in range(n):
        if not visited[start]:
            
            tour = []
            current = start

            while not visited[current]:
                visited[current] = True
                tour.append(current)

                for (i, j) in edges:
                    if i == current:
                        current = j
                        break

            subtours.append(tour)

    return subtours

def find_subtour(edges, n):
  visited = [False] * n

  # for each unvisited node, try starting a search
  # keep track of edges in a cycle along the way
  for start in range(n):
    if not visited[start]:
      
      cycle = []
      current = start

      # find edge in solution that begins in current node
      # set current as edge end node
      # if current is visited, search circled around and end cycle
      while not visited[current]:
        
        visited[current] = True
        cycle.append(current)
        
        for (i, j) in edges:
          if i == current:
            current = j
            break

      # length of cycle lesser than n indicates sub tour instead of hamiltonian cycle
      # return cycle to be added as a lazy constraint
      if len(cycle) < n:
        return cycle
    
    # no sub cycles detected
    return None

def my_callback(model, where):
  if where == g.GRB.Callback.MIPSOL:
    
    x = model._x
    n = model._n
    
    solution = model.cbGetSolution(x)
    edges = [(i, j) for i in range(n) for j in range(n) if round(solution[i, j]) == 1]
    
    subtours = find_subtours(edges, n)

    if len(subtours) > 1:
      shortest = min(subtours, key=len)

      model.cbLazy(
          g.quicksum(x[i, j] for i in shortest for j in shortest) <= len(shortest) - 1
      )

    # tour = find_subtour(edges, n)

    # if tour is not None:
    #   model.cbLazy(g.quicksum(x[i, j] for i in tour for j in tour) <= len(tour) - 1)


# n = # of stripes

# matrix c[n+1][n+1]
# c[i][j] = distance/edge cost from right side of stripe i to left side of stripe j
# n+1 idx is dummy stripe with each distance 0 to connect all vertices and transform the problem into a tsp

# matrix x[n+1][n+1]
# x[i][j] = 1 or 0 based on if the edge from node i to node j is present in the cycle
def main():
  input_path = sys.argv[1]
  # input_path = "./homework/02_TSP_image_shredding/instances/triangle.txt"
  output_path = sys.argv[2]
  # output_path = "./homework/02_TSP_image_shredding/output.txt"

  with open(input_path, "r") as f:
    lines = [line.strip() for line in f if line.strip()]

  n, w, h = map(int, lines[0].split())

  stripesList = []
  for line in lines[1:]:
    values = numpy.fromstring(line, dtype=int, sep=' ')
    stripe = values.reshape(h, w, 3)
    stripesList.append(stripe)

  stripes = numpy.stack(stripesList)

  rightColumns = stripes[:, :, -1, :]
  leftColumns  = stripes[:, :, 0, :]
  diff = numpy.abs(rightColumns[:, None] - leftColumns[None, :])
  c = diff.sum(axis=(2, 3))

  # add dummy stripe at index n
  # fill a n+1^2 matrix with zeroes and copy in the original from [0, 0] to [n, n]
  n_orig = c.shape[0]
  c_ext = numpy.zeros((n_orig + 1, n_orig + 1), dtype=c.dtype)
  c_ext[:n_orig, :n_orig] = c
  dummyNode = n_orig
  c = c_ext
  n += 1

  model = g.Model()
  model.Params.lazyConstraints = 1

  x = model.addVars(n, n, vtype=g.GRB.BINARY, name="x")
  
  model._x = x
  model._n = n
  
  for i in range(n):
    model.addConstr(x.sum(i, '*') == 1)
    model.addConstr(x.sum('*', i) == 1)
    model.addConstr(x[i, i] == 0)
  
  model.setObjective(
    g.quicksum(c[i, j] * x[i, j] for i in range(n) for j in range(n)),
    g.GRB.MINIMIZE
  )
  model.optimize(my_callback)

  edges = [(i, j) for i in range(n) for j in range(n) if round(x[i, j].X) == 1]
  successor = {i: j for (i, j) in edges}

  # get order of node indexes in the cycle
  order = []
  current = 0
  for i in range(n):
    order.append(current)
    current = successor[current]
  
  # slice the order list at the dummy stripe index and concatenate parts
  dummyIdx = order.index(dummyNode)
  finalOrder = order[dummyIdx + 1:] + order[:dummyIdx]

  with open(output_path, "w") as f:
    # f.write(" ".join(str(int(round(finalOrder[i]+1))) for i in range(len(finalOrder))))
    f.write(" ".join(str(i + 1) for i in finalOrder))

if __name__ == "__main__":
  main()
