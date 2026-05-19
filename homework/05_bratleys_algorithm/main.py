#!/usr/bin/env python3
import sys

class Solution:
  def __init__(self):
    self.schedule = []
    self.bestUB = None

def constructSchedule(N: int, solution: Solution, p: list, r: list):
  if (len(solution.schedule) < N):
    return [-1]
  
  time = 0
  schedule = [0 for i in range(N)]
  for taskIdx in solution.schedule:
    start = max(time, r[taskIdx])
    schedule[taskIdx-1] = start
    time = start + p[taskIdx]
  return schedule

def main():
  # instanceName = "public_5.txt"
  # input_path = "./homework/05_bratleys_algorithm/instances/" + instanceName
  # expected_output_path = "./homework/05_bratleys_algorithm/solutions/" + instanceName
  # output_path = "./homework/05_bratleys_algorithm/out-" + instanceName

  input_path = sys.argv[1]
  output_path = sys.argv[2]

  with open(input_path, "r") as f:
    lines = [line.strip() for line in f if line.strip()]

  # tasks
  N = int(lines[0])

  processingTimes = [0 for i in range(N+1)]
  releaseDates = [0 for i in range(N+1)]
  deadlines = [0 for i in range(N+1)]

  for lineIdx in range(1, N+1):
    # processing time, release date, deadline
    pi, ri, di = map(int, lines[lineIdx].split())
    
    processingTimes[lineIdx] = pi
    releaseDates[lineIdx] = ri
    deadlines[lineIdx] = di

  tasks = [i for i in range(1, N+1)]
  solution = Solution()
  branchAndBound([], tasks, 0, processingTimes, releaseDates, deadlines, solution)
  schedule = constructSchedule(N, solution, processingTimes, releaseDates)

  with open(output_path, "w") as f:
    f.write("\n".join(str(i) for i in schedule))


def branchAndBound(scheduled: list, unsheduled:list, c:int, p: list, r: list, d: list, solution: Solution):
  # if (c > solution.bestUB):
  #   return True

  if ((solution.bestUB is not None) and (c > solution.bestUB)):
    return True

  if (len(unsheduled) == 0):
    if ((solution.bestUB is None) or (c < solution.bestUB)):
      # print(f"found a solution with UB={c}, updating best solution with schedule={scheduled}")
      solution.schedule = scheduled
      solution.bestUB = c
    return True
  
  for taskIdx in unsheduled:
    if (max(c, r[taskIdx]) + p[taskIdx] > d[taskIdx]):
      return True
    
  LB = max(c, min(r[i] for i in unsheduled)) + sum(p[i] for i in unsheduled)
  if (solution.bestUB is None):
    UB = max(d[i] for i in unsheduled)
    if (LB > UB):
      return True
  else:
    if (LB >= solution.bestUB):
      return True
  
  continueBranching = True
  if (c <= min(r[i] for i in unsheduled)):
    continueBranching = False

  # if returns false, stop branching from current root, found partial optimal solution
  for i in range(len(unsheduled)):
    if (not branchAndBound(scheduled=scheduled + [unsheduled[i]],
                  unsheduled=unsheduled[:i] + unsheduled[i+1:],
                  c=max(c, r[unsheduled[i]]) + p[unsheduled[i]],
                  p=p, r=r, d=d, solution=solution)):
      return False
  
  return continueBranching

if __name__ == "__main__":
  main()
