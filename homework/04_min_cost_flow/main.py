#!/usr/bin/env python3
import sys
from collections import deque
import math

class Edge:
    def __init__(self, to: str, lower: int, upper: int, isForward: bool, cost: int):
        self.to = to
        self.lower = lower
        self.flow = 0
        self.upper = upper
        self.rev = None  # point to the reverse Edge object
        self.originalLower = lower
        self.isForward = isForward
        self.cost = cost

class Graph:
    def __init__(self, nodes):
        self.adj = {node: [] for node in nodes}
    
    def addNode(self, u):
        self.adj[u] = []
    
    def removeNode(self, u):
        # for each edge adjacent to u, 
        # remove the edge from adjacency lists of all neighbors of u
        for edge in self.adj[u]:
            neighbor = edge.to
            if (neighbor in self.adj):
                self.adj[neighbor] = [e for e in self.adj[neighbor] if e is not edge.rev]
        self.adj.pop(u)

    # helper for constructing a residual graph for min cost flow alg
    # no shadow rev edges required (Ford-Fulkerson is not used on res)
    def addArc(self, u, v, lo, hi, cost):
        arc = Edge(v, lo, hi, True, cost)
        arc.rev = None
        self.adj[u].append(arc)

    def addEdge(self, u, v, lo, hi, cost):
        # (node to idx, lower bound, upper bound, is forward)
        forward = Edge(v, lo, hi, True, cost)
        backward = Edge(u, lo, hi, False, cost)
        forward.rev = backward
        backward.rev = forward
        self.adj[u].append(forward)
        self.adj[v].append(backward)

    def removeEdge(self, u, v):
        forward = next(e for e in self.adj[u] if e.to == v and e.isForward)
        self.adj[u].remove(forward)
        self.adj[v].remove(forward.rev)
    
    # helper for Ford-Fulkerson finding augmenting paths
    def getUnsaturatedEdges(self, node):
        for edge in self.adj[node]:
            
            # by how mych can the flow increase when moving forwards
            # or by how can it be reduced when moving backwards
            if edge.isForward:
                residual = edge.upper - edge.flow
            else:
                residual = edge.rev.flow - edge.rev.lower
        
            if (residual > 0):
                yield edge.to, residual, edge

# bfs for Ford-Fulkerson max flow augmenting path finding
def bfs(graph, source, sink):
    # visited[nodeIdx] = (predecessorNodeIdx, edge, bottleneck)
    visited = {source: (None, None, float("inf"))}
    queue = deque([source])

    while queue:
        node = queue.popleft()
        currentBottleneck = visited[node][2]

        for neighbor, residualCap, edge in graph.getUnsaturatedEdges(node):
            if (neighbor not in visited and residualCap > 0):
                
                # bottleneck is the minimum from among the increases along the way
                bottleneck = min(currentBottleneck, residualCap)
                visited[neighbor] = (node, edge, bottleneck)
                
                if (neighbor == sink):
                    return visited
                queue.append(neighbor)

    return visited

# augment an augmenting path, for Ford-Fulkerson max flow alg
def augment(visited, sink):
    # start at sink node, walk back through predecessors
    # using visited[nodeIdx] = (predecessor idx, used edge, bottleneck)
    delta = visited[sink][2]
    node = sink
    
    while visited[node][0] is not None:
        pred, edge, bottleneck = visited[node]
        # increase on forward edges, decrease backward edges
        edge.flow += delta
        edge.rev.flow  -= delta
        node = pred
    
    return delta

# find a cycle with negative total cost, for Cycle canceling min cost flow alg
def findNegativeCycle(graph: Graph)->list[int]:
    N = len(graph.adj.keys())
    distances = {node: 0 for node in graph.adj}
    predecessor = {node: -1 for node in graph.adj}
    x = -1

    for _ in range(N):    
        x = -1
        for node in graph.adj.keys():
            for edge in graph.adj[node]:
                if edge.upper - edge.flow > 0:
                    if (distances[node] + edge.cost < distances[edge.to]):
                        distances[edge.to] = max(-float("inf"), distances[node] + edge.cost)
                        predecessor[edge.to] = node
                        x = edge.to
    if (x != -1):
        # walk back N steps, ensure on cycle
        for _ in range(N):
            x = predecessor[x]
        
        cycle = []
        v = x
        while True:
            cycle.append(v)
            v = predecessor[v]
            if v == x:
                break
        cycle.append(x)
        cycle.reverse()
        return cycle
 
# create a residual graph for min cost flow alg
def createResidualGraph(graph: Graph)->Graph:
    nodes = []
    for node in graph.adj.keys():
        nodes.append(node)
    residual = Graph(nodes)
    
    for node in graph.adj.keys():
        for edge in graph.adj[node]:
            if edge.isForward:
                # edge in E: new upper = old upper - old flow, new cost = old cost
                residual.addArc(node, edge.to, 0, edge.upper - edge.flow, edge.cost)
                # edge not in E: new upper = old flow - old lower, new cost = - old cost
                residual.addArc(edge.to, node, 0, edge.flow - edge.lower, -edge.cost)
    
    return residual

# cancel a negative cycle from residual graph and update both orig and res graphs
def cancelCycle(graph: Graph, residual: Graph, cycle: list):
    # find bottleneck in the cycle
    delta = float('inf')
    for k in range(len(cycle) - 1):
        u, v = cycle[k], cycle[k+1]
        
        for edge in residual.adj[u]:
            if edge.to == v:
                delta = min(delta, edge.upper - edge.flow)
                break
    
    # update original graph and residual graph
    for k in range(len(cycle) - 1):
        u, v = cycle[k], cycle[k+1]

        # update original graph
        # find each edge u->v from cycle in orig, if forward: add delta, subtract otherwise
        for original in graph.adj[u]:
            if original.to == v and original.isForward:
                original.flow += delta
                break
            elif original.to == v and not original.isForward:
                original.rev.flow -= delta
                break

        # update residual graph
        # forward edge from cycle -> subtract delta from up
        for res in residual.adj[u]:
            if res.to == v:
                res.upper -= delta
                break

        # reverse from edge from cycle -> add delta to up
        for res in residual.adj[v]:
            if res.to == u:
                res.upper += delta
                break

def main():
    # FIXME input public4, line 4, 19 check manually

    input_path = sys.argv[1]
    # input_path = "./homework/04_min_cost_flow/instances/public4.txt"
    output_path = sys.argv[2]
    # output_path = "./homework/04_min_cost_flow/output1.txt"

    with open(input_path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # players, frames
    N, P = map(int, lines[0].split())

    # load n times [x, y] per frame
    k_x = [0 for _ in range(N)]
    k_y = [0 for _ in range(N)]
    kp_x = [0 for _ in range(N)]
    kp_y = [0 for _ in range(N)]

    for i in range(1, P+1):
        if (i >= P):
            break

        kFrame = [int(a) for a in lines[i].split()]
        kpFrame = [int(a) for a in lines[i + 1].split()]
        
        idx = 0
        for j in range(2 * N):
            if (j % 2 == 0):
                k_x[idx] = kFrame[j]
                kp_x[idx] = kpFrame[j]
            else:
                k_y[idx] = kFrame[j]
                kp_y[idx] = kpFrame[j]
                idx += 1
        
        nodes = (
            ["source", "sink"]
            + [f"A{j}" for j in range(1, N+1)]
            + [f"B{k}" for k in range(1, N+1)]
        )
        graph = Graph(nodes)

        for j in range(1, N+1):
            graph.addEdge(u='source', v=f'A{j}', lo=1, hi=1, cost=0)
            graph.addEdge(u=f'B{j}', v='sink', lo=1, hi=1, cost=0)

        for j in range(1, N+1):
            fromIdx = f'A{j}'
            for k in range(1, N+1):
                toIdx = f'B{k}'
                d = math.dist((k_x[j-1], k_y[j-1]), (kp_x[k-1], kp_y[k-1]))
                graph.addEdge(fromIdx, toIdx, 0, 1, d)

        # find an initial feasible flow
        graph.addEdge("sink", "source", 0, float("inf"), 0)

        for node in graph.adj:
            for edge in graph.adj[node]:
                edge.lower = 0
                edge.upper -= edge.originalLower

        sourceBalance = 0
        sinkBalance = 0
        kBalances = { f'A{j}' : 0 for j in range(1, N+1)}
        kpBalances = { f'B{j}' : 0 for j in range(1, N+1)}
        
        for edge in graph.adj["source"]:
            if edge.isForward:
                sourceBalance -= edge.originalLower
                kBalances[edge.to] += edge.originalLower
        
        for j in range(1, N+1):
            kIndex = f'A{j}'
            for edge in graph.adj[kIndex]:
                if edge.isForward:
                    kBalances[kIndex] -= edge.originalLower
                    kpBalances[edge.to] += edge.originalLower
        for j in range(1, N+1):
            kpIndex = f'B{j}'
            for edge in graph.adj[kpIndex]:
                if edge.isForward:
                    kpBalances[kpIndex] -= edge.originalLower
                    sinkBalance += edge.originalLower

        # TODO remove
        # print(f"sourceBalance={sourceBalance}, sinkBalance={sinkBalance}")
        # print(f"kBalances={kBalances}")
        # print(f"kpBalances={kpBalances}")

        if (sourceBalance + sinkBalance + sum(kBalances.values()) + sum(kpBalances.values()) != 0):
            with open(output_path, "w") as f:
                f.write("-1")
            return

        graph.addNode("fakeSource")
        graph.addNode("fakeSink")

        graph.addEdge("source", "fakeSink", 0, -sourceBalance, 0)
        graph.addEdge("fakeSource", "sink", 0, sinkBalance, 0)

        for j in range(1, N+1):
            kIndex = f'A{j}'
            balance = kBalances[kIndex]
            if (balance < 0):
                graph.addEdge(kIndex, "fakeSink", 0, -balance, 0)
            if (balance > 0):
                graph.addEdge("fakeSource", kIndex, 0, balance, 0)

        for j in range(1, N+1):
            kpIndex = f'B{j}'
            balance = kpBalances[kpIndex]
            if (balance < 0):
                graph.addEdge(kpIndex, "fakeSink", 0, -balance, 0)
            if (balance > 0):
                graph.addEdge("fakeSource", kpIndex, 0, balance, 0)

        # run max flow on auxiliary graph with lb = 0 and flow = 0 and fake nodes added
        while True:
            augPath = bfs(graph=graph, source="fakeSource", sink="fakeSink")
            if "fakeSink" not in augPath:
                break
            augment(augPath, "fakeSink")

        # check feasibility - all fakeSource edges are saturated
        for edge in graph.adj["fakeSource"]:
            if edge.upper - edge.flow > 0:
                with open(output_path, "w") as f:
                    f.write("-1")
                return

        # restore flow value on original edges
        for node in graph.adj:
            for edge in graph.adj[node]:
                if edge.isForward:
                    edge.flow += edge.originalLower

        # remove fake nodes, remove sink source arc
        graph.removeNode("fakeSource")
        graph.removeNode("fakeSink")
        graph.removeEdge("sink", "source")

        # restore lower bounds
        for node in graph.adj:
            for edge in graph.adj[node]:
                if edge.isForward:
                    edge.lower = edge.originalLower
                    edge.upper += edge.originalLower
                else:
                    edge.upper += edge.rev.originalLower

        residual = createResidualGraph(graph)

        # run cycle canceling algorithm on graph with initial feasible flow and residual
        while True:
            # detect a negative cycle
            negativeCycle = findNegativeCycle(residual)
            
            # TODO remove
            # print(negativeCycle)
            
            if negativeCycle:
                # TODO remove
                # totalCost = sum(
                #     edge.cost
                #     for node in negativeCycle[:-1]
                #     for edge in residual.adj[node]
                #     if edge.to == negativeCycle[negativeCycle.index(node) + 1] and edge.isForward
                # )
                # print(f"cycle cost: {totalCost}")
                
                # if cycle is not None, cancel it, updating the graph
                cancelCycle(graph=graph, residual=residual, cycle=negativeCycle)
            else:
                break
        
        # TODO remove
        # for j in range(1, N+1):
        #     for edge in graph.adj[f'A{j}']:
        #         if edge.to.startswith('B') and edge.isForward:
        #             print(f"A{j}->{edge.to}: flow={edge.flow}")
        
        # extract assignment solution
        # find edges from Ai to Bj with flow=1, note the pairing of indexes
        assignment = [0] * (N + 1)
        for j in range(1, N+1):
            for edge in graph.adj[f'A{j}']:
                if edge.to.startswith('B') and edge.isForward and edge.flow == 1:
                    k = int(edge.to[1:])
                    assignment[j] = k
                    break

        # b = len(assignment) == len(set(assignment))
        # print(f"Pairing uniue for pair {i}: {b}")
        
        with open(output_path, "a") as f:
            if (i > 1):
                f.write('\n')
            f.write(' '.join(str(assignment[j]) for j in range(1, N+1)))

if __name__ == "__main__":
    main()
