"""
graph_routes.py - Route maker (Phase 3)

* Graph        : weighted, undirected, adjacency-list representation
* Dijkstra     : single-source shortest paths, O((V + E) log V) with a binary heap
* Nearest-Neighbour TSP approximation : O(k^2) over k stops
* Brute-force TSP (k <= 9) : used only to measure how good the approximation is
"""
import heapq
from itertools import permutations

INF = float("inf")


class Graph:
    def __init__(self):
        self.adj = {}

    def add_edge(self, u, v, w):
        self.adj.setdefault(u, []).append((v, w))
        self.adj.setdefault(v, []).append((u, w))

    @classmethod
    def from_dataset(cls, data):
        g = cls()
        for n in data["nodes"]:
            g.adj.setdefault(n, [])
        for u, v, w in data["edges"]:
            g.add_edge(u, v, w)
        return g


def dijkstra(graph, source):
    """Returns (dist, prev) dictionaries for every node reachable from source."""
    dist = {n: INF for n in graph.adj}
    prev = {n: None for n in graph.adj}
    dist[source] = 0
    heap = [(0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue                                  # stale heap entry
        for v, w in graph.adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v], prev[v] = nd, u
                heapq.heappush(heap, (nd, v))
    return dist, prev


def shortest_path(prev, source, target):
    path, node = [], target
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()
    return path if path and path[0] == source else []


def distance_matrix(graph, nodes):
    """Runs Dijkstra from every node in `nodes`. Returns (dist_matrix, prev_maps)."""
    matrix, prevs = {}, {}
    for s in nodes:
        d, p = dijkstra(graph, s)
        matrix[s] = {t: d[t] for t in nodes}
        prevs[s] = p
    return matrix, prevs


def nearest_neighbor_tour(depot, stops, matrix):
    """Greedy TSP: always drive to the closest unvisited stop, then return to depot."""
    unvisited, tour, cur, total = set(stops), [depot], depot, 0
    while unvisited:
        nxt = min(unvisited, key=lambda s: (matrix[cur][s], s))   # tie -> name
        total += matrix[cur][nxt]
        tour.append(nxt)
        unvisited.remove(nxt)
        cur = nxt
    total += matrix[cur][depot]
    tour.append(depot)
    return tour, total


def brute_force_tour(depot, stops, matrix):
    """Optimal tour by trying all k! orders. Only for k <= 9."""
    best, best_len = None, INF
    for perm in permutations(stops):
        route = [depot, *perm, depot]
        length = sum(matrix[a][b] for a, b in zip(route, route[1:]))
        if length < best_len:
            best, best_len = route, length
    return best, best_len


def expand_route(tour, prevs):
    """Replaces each leg of the tour by the actual road path found by Dijkstra."""
    full = [tour[0]]
    for a, b in zip(tour, tour[1:]):
        full.extend(shortest_path(prevs[a], a, b)[1:])
    return full
