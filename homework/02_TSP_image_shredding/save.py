#!/usr/bin/env python3
import sys
import gurobipy as g
import numpy

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

      # length of cycle lesser than n indicates sub cycle
      # return cycle to for lazy contraint addition
      if len(cycle) < n:
        return cycle
    
    # no subcycles detected
    return None

def my_callback(model, where):
  if where == g.GRB.Callback.MIPSOL:
    
    x = model._x
    n = model._n
    
    solution = model.cbGetSolution(x)
    edges = [(i, j) for i in range(n) for j in range(n) if solution[i, j] == 1]
    
    tour = find_subtour(edges, n)

    if tour is not None:
      model.cbLazy(g.quicksum(x[i, j] for i in tour for j in tour) <= len(tour) - 1)


# n = # of stripes

# matrix c[n+1][n+1]
# c[i][j] = distance from right side of stripe i to left side of stripe j
# c[0][j] dummy stripe to transform the problem into a traveling salesman problem, each distance is 0 to connect all vertices equally
# the image is then decided as beginning at the right side of dummy stripe and ending at left side of dummy stripe (hamiltonian cycle)
  
# matrix x[n+1][n+1] ?
# x[i][j] = 1 or 0 based on if the edge is present in the cycles
def main():
  # input_path = sys.argv[0]
  input_path = "./homework/02_TSP_image_shredding/instances/triangle.txt"
  # output_path = sys.argv[1]
  output_path = "./homework/02_TSP_image_shredding/hello.txt"

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

  n_orig = c.shape[0]
  c_ext = numpy.zeros((n_orig + 1, n_orig + 1), dtype=c.dtype)
  c_ext[:n_orig, :n_orig] = c
  dummyIdx = n_orig
  c = c_ext
  n += 1


  model = g.Model()
  model.Params.lazyConstraints = 1

  x = model.addVars(n, n, vtype=g.GRB.BINARY, name="x")
  
  model._x = x
  model._n = n
  
  # diagonal = 0
  for i in range(n):
    model.addConstr(x.sum(i, '*') == 1)
    model.addConstr(x.sum('*', i) == 1)
    # diagonal += x[i, i]
  
  model.setObjective(
    g.quicksum(c[i, j] * x[i, j] for i in range(n) for j in range(n)),
    g.GRB.MINIMIZE
  )
  model.optimize(my_callback)

  edges = [(i, j) for i in range(n) for j in range(n) if x[i, j].X == 1]
  successors = {i: j for (i, j) in edges}
  
  # get order of node ids in the cycle
  order = []
  current = 0
  for i in range(n):
    order.append(current)
    current = successors[current]
  
  
  # find edge with maximal distance between nodes in a cycle  and save the index
  # assume the edge connects leftmost and rightmost stripes of the original image
  # save the index
  # maxCost = -1
  # seamIndex = 0
  # for i in range(n):
  #   nodeFromIdx = order[i]
  #   nodeToIdx = order[(i + 1) % n]

  #   if c[nodeFromIdx, nodeToIdx] > maxCost:
  #     maxCost = c[nodeFromIdx, nodeToIdx]
  #     seamIndex = i
  
  # slice order list from the seam index to end of list, and start of list to seam index 
  # and concatenate parts to produce actual order of the stripes
  # finalOrder = order[seamIndex + 1:] + order[:seamIndex + 1]
  dummy_index = order.index(dummyIdx)
  finalOrder = order[dummy_index + 1:] + order[:dummy_index]


  with open(output_path, "w") as f:
    f.write(str(int(round(model.ObjVal))) + "\n")
    f.write("dummy idx: " + str(dummyIdx) + "\n")
    f.write("order : " + str(order) + "\n")
    f.write(" ".join(str(int(round(finalOrder[i]))) for i in range(len(finalOrder))))

if __name__ == "__main__":
  main()
