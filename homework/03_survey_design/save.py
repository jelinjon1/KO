#!/usr/bin/env python3
import sys
from collections import deque

            # TODO remove
            # print(f"  edge {node}->{edge.to} | isForward={edge.isForward} | "
            #       f"flow={edge.flow if edge.isForward else edge.rev.flow} | "
            #       f"lower={edge.lower if edge.isForward else edge.rev.lower} | "
            #       f"upper={edge.upper if edge.isForward else edge.rev.upper} | "
            #       f"residual={residual}")

def bfs(graph, source, sink):
    # visited[node] = (predecessor, is_forward, bottleneck)
    visited = {source: (None, None, float("inf"))}
    queue = deque([source])

    while queue:
        node = queue.popleft()
        current_bottleneck = visited[node][2]

        for neighbor, residual_cap, edge in graph.residual_edges(node):
            if neighbor not in visited and residual_cap > 0:
                bottleneck = min(current_bottleneck, residual_cap)
                visited[neighbor] = (node, edge, bottleneck)
                if neighbor == sink:
                    return visited  # found it, stop early
                queue.append(neighbor)

    return visited  # sink not reached -> no augmenting path

def augment(visited, sink):
    # walk back through predecessors
    delta = visited[sink][2]
    node = sink
    while visited[node][0] is not None:
        pred, edge, _ = visited[node]
        edge.cap -= delta        # reduce forward residual
        edge.rev.cap += delta    # increase backward residual
        node = pred
    return delta

def is_feasible(graph, P, PDemands):
    for j in range(1, P+1):
        for edge in graph.adj[f'P{j}']:
            if edge.to == 'sink':
                flow = edge.rev.cap  # flow sent on this edge
                if flow < PDemands[j-1]:
                    return False
    return True

def extract_solution(graph, C, P):
    result = [[] for _ in range(C)]
    
    for i in range(C):
        for edge in graph.adj[f'C{i}']:
            # only look at forward edges to P nodes
            if edge.to.startswith('P'):
                original_cap = edge.rev.cap  # how much flow was sent = backward residual
                if original_cap > 0:
                    product_idx = int(edge.to[1:])
                    result[i].append(product_idx)
    
    return result

class Edge:
    def __init__(self, to, cap, lower=0):
        self.to = to
        self.cap = cap  # residual capacity
        self.lower = lower  # just for reference/reconstruction
        self.rev = None  # will point to the reverse Edge object
    def __str__(self):
        return f"cap: {self.cap}"


class Graph:
    def __init__(self, nodes):
        self.adj = {node: [] for node in nodes}

    def add_edge(self, u, v, lo, hi):
        forward = Edge(v, hi - lo)  # residual cap starts at hi - lo
        backward = Edge(u, 0)  # reverse edge starts with 0 residual
        forward.rev = backward
        backward.rev = forward
        self.adj[u].append(forward)
        self.adj[v].append(backward)

    def residual_edges(self, node):
        for edge in self.adj[node]:
            if edge.cap > 0:
                yield edge.to, edge.cap, edge


def main():
    # input_path = sys.argv[1]
    input_path = "./homework/03_survey_design/instances/1.txt"
    # output_path = sys.argv[2]
    output_path = "./homework/03_survey_design/output1.txt"

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

    # edges = []
    nodes = (
        ["source", "sink"]
        + [f"C{i}" for i in range(C)]
        + [f"P{j}" for j in range(1, P + 1)]
    )
    graph = Graph(nodes)

    # source -> each Ci
    for i in range(C):
        graph.add_edge("source", f"C{i}", lower[i], upper[i])

    # Ci -> Pj (only where customer has bought the product before)
    for i in range(C):
        for j in CProducts[i]:
            graph.add_edge(f"C{i}", f"P{j}", 0, 1)

    # each Pj -> sink
    for j in range(1, P + 1):
        cap = sum(1 for i in range(C) if j in CProducts[i])
        graph.add_edge(f"P{j}", "sink", PDemands[j - 1], cap)

    while True:
        APath = bfs(graph=graph, source="source", sink="sink")
        if (not "sink" in APath):
            print("No augmenting path was found")
            break
        else:
            # reconstruct path for debug
            node = "sink"
            while node is not None:
                pred, edge, bottleneck = APath[node]
                print(f"{pred} -> {node} (bottleneck so far: {bottleneck})")
                node = pred
            print()
        
            augment(APath, "sink")
    
    if (is_feasible(graph=graph, P=P, PDemands=PDemands)):
        print(extract_solution(graph=graph, C=C, P=P))
    else:
        print("-1")
        



if __name__ == "__main__":
    main()
