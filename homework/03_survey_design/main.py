#!/usr/bin/env python3
import sys
from collections import deque


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

def augment(visited, sink):
    # start at sink node
    # walk back through predecessors
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

def isFeasible(graph, P):
    for j in range(1, P+1):
        for edge in graph.adj[f'P{j}']:
            if (edge.to == 'sink'):
                if (edge.flow > edge.upper):
                    return False
    return True

def getSolution(graph, C):
    result = [[] for i in range(C)]
    
    for i in range(C):
        for edge in graph.adj[f'C{i}']:
            # go over forward edges to product nodes with f(e)>0
            if (edge.to.startswith('P')):
                if (edge.flow > 0):
                    productIdx = int(edge.to[1:])
                    result[i].append(productIdx)
    
    for a in result:
        a.sort()
    
    return result

class Edge:
    def __init__(self, to: str, lower: int, upper: int, isForward: bool):
        self.to = to
        self.lower = lower
        self.flow = 0
        self.upper = upper
        self.rev = None  # point to the reverse Edge object
        self.originalLower = lower
        self.isForward = isForward


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

    def addEdge(self, u, v, lo, hi):
        # (node to idx, lower bound, upper bound, is forward)
        forward = Edge(v, lo, hi, True)
        backward = Edge(u, lo, hi, False)
        forward.rev = backward
        backward.rev = forward
        self.adj[u].append(forward)
        self.adj[v].append(backward)

    def removeEdge(self, u, v):
        forward = next(e for e in self.adj[u] if e.to == v and e.isForward)
        self.adj[u].remove(forward)
        self.adj[v].remove(forward.rev)

    # def getUnsaturatedEdges(self, node):
    #     for edge in self.adj[node]:
    #         if edge.upper - edge.flow > 0:
    #             yield edge.to, edge.upper - edge.flow, edge
    
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


def main():
    input_path = sys.argv[1]
    # input_path = "./homework/03_survey_design/instances/5.txt"
    output_path = sys.argv[2]
    # output_path = "./homework/03_survey_design/output1.txt"

    with open(input_path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # customers, products
    C, P = map(int, lines[0].split())

    lower = [0 for i in range(C)]
    upper = [0 for i in range(C)]
    CProducts = [[] for i in range(C)]

    for i in range(1, C + 1):
        # lower bound, upper bound, list of products
        CData = [int(a) for a in lines[i].split()]
        lower[i - 1] = CData[0]
        upper[i - 1] = CData[1]
        for j in range(2, len(CData)):
            CProducts[i - 1].append(CData[j])

    PDemands = [int(a) for a in lines[C + 1].split()]

    nodes = (
        ["source", "sink"]
        + [f"C{i}" for i in range(C)]
        + [f"P{j}" for j in range(1, P + 1)]
    )
    graph = Graph(nodes)

    # source -> each Ci
    for i in range(C):
        graph.addEdge("source", f"C{i}", lower[i], upper[i])

    # Ci -> Pj (only where customer has bought the product before)
    for i in range(C):
        for j in CProducts[i]:
            graph.addEdge(f"C{i}", f"P{j}", 0, 1)

    # each Pj -> sink
    for j in range(1, P + 1):
        cap = sum(1 for i in range(C) if j in CProducts[i])
        graph.addEdge(f"P{j}", "sink", PDemands[j - 1], cap)

    # find a feasible initial flow
    # theres a non 0 lower bound, and init flow has to be found
    if (sum(lower) != 0 or sum(PDemands) != 0):

        # 1) We add a circulation problem by adding an arc from t to s of infinite
        # capacity. Consequently, the Kirchhoff’s law applies to nodes s and t.
        # Therefore, a feasible circulation must satisfy:
        # l(e) ≤ f (e) ≤ u(e), e ∈ E(G)
        # SUM{e∈δ+(v)} f(e) − SUM{e∈δ-(v)} f(e) = 0, v ∈ V(G)
        graph.addEdge("sink", "source", 0, float("inf"))

        # 2) Substituting f(e) = f(e)′ + l(e), we obtain the transformed problem:
        # 0 ≤ f(e)′ ≤ u(e) − l(e),  e ∈ E(G)
        # SUM{e∈δ+(v)} f(e)′ − SUM{e∈δ-(v)} f(e)′ =
        #  SUM{e∈δ-(v)} l(e) - SUM{e∈δ+(v)} l(e) = b(v) (balance of a node v), v ∈ V(G)
        for node in graph.adj:
            for edge in graph.adj[node]:
                edge.lower = 0
                edge.upper -= edge.originalLower

        sourceBalance = 0
        sinkBalance = 0
        customerBalances = { f'C{i}' : 0 for i in range(C)}
        productBalances = { f'P{i}' : 0 for i in range(1, P+1)}
        
        for edge in graph.adj["source"]:
            if edge.isForward:
                sourceBalance -= edge.originalLower
                customerBalances[edge.to] += edge.originalLower
        for i in range(C):
            customerIdx = f'C{i}'
            for edge in graph.adj[customerIdx]:
                if edge.isForward:
                    customerBalances[customerIdx] -= edge.originalLower
                    productBalances[edge.to] += edge.originalLower
        for i in range(1, P+1):
            productIdx = f'P{i}'
            for edge in graph.adj[productIdx]:
                if edge.isForward:
                    productBalances[productIdx] -= edge.originalLower
                    sinkBalance += edge.originalLower

        # 3) This is a Feasible Flow with Balances and zero lower bounds because 
        # SUM{v∈ V(G)} b(v) = 0 (notice that l(e) appears twice in summation, 
        # once with a positive and once with a negative sign).
        if (sourceBalance + sinkBalance + sum(customerBalances.values()) + sum(productBalances.values()) != 0):
            with open(output_path, "w") as f:
                f.write("-1")
            return


        # 4) While solving this decision problem (i.e. adding s′, t′ and solving the
        # maximum flow problem with zero lower bounds) we obtain the initial
        # feasible circulation/flow or decide that it does not exist.

        graph.addNode("fakeSource")
        graph.addNode("fakeSink")

        graph.addEdge("source", "fakeSink", 0, -sourceBalance)
        graph.addEdge("fakeSource", "sink", 0, sinkBalance)

        for i in range(C):
            customerIdx = f'C{i}'
            balance = customerBalances[customerIdx]
            if (balance < 0):
                graph.addEdge(customerIdx, "fakeSink", 0, -balance)
            if (balance > 0):
                graph.addEdge("fakeSource", customerIdx, 0, balance)
        
        for i in range(1, P+1):
            productIdx = f'P{i}'
            balance = productBalances[productIdx]
            if (balance < 0):
                graph.addEdge(productIdx, "fakeSink", 0, -balance)
            if (balance > 0):
                graph.addEdge("fakeSource", productIdx, 0, balance)

        # Conclusion: finding of the initial flow with nonzero lower bounds can
        # be transformed to the Feasible Flow with Balances and zero lower
        # bounds which can be transformed to the Maximum Flow with zero lower bounds.

        # run max flow on auxiliary graph with lb = 0 and flow = 0
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

        # for node in graph.adj:
        #     for edge in graph.adj[node]:
        #         edge.lower = edge.originalLower
        #         edge.upper += edge.originalLower

    
    # run max flow on graph with an initial flow
    while True:
        augPath = bfs(graph=graph, source="source", sink="sink")
        if (not "sink" in augPath):
            # print("no augmenting path found")
            break
        else:
            # TODO remove
            # reconstruct path for debug
            # node = "sink"
            # while node is not None:
            #     pred, edge, bottleneck = augPath[node]
            #     print(f"{pred} -> {node} (bottleneck so far: {bottleneck})")
            #     node = pred
            # print()
            augment(augPath, "sink")
    
    if (isFeasible(graph, P)):
        solution = getSolution(graph, C)
        # for l in solution:
        #     print(l)
        
        with open(output_path, "w") as f:
            f.write("\n".join([" ".join([str(n) for n in item]) for item in solution]))
                
    else:
        with open(output_path, "w") as f:
            f.write("-1")



if __name__ == "__main__":
    main()
