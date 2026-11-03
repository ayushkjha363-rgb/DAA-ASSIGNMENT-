"""
planner.py - Integrates all algorithms into one pipeline.

  parcels --Merge Sort--> prioritised list
          --0/1 Knapsack DP--> parcels for this trip
          --Dijkstra (from depot + each stop)--> distance matrix
          --Nearest-Neighbour TSP--> visiting order
          --expand with Dijkstra paths--> full road route
"""
import json
import time

from sorting import merge_sort
from knapsack import knapsack_dp
from graph_routes import (Graph, distance_matrix, nearest_neighbor_tour,
                          brute_force_tour, expand_route)


def load_dataset(path):
    with open(path) as f:
        return json.load(f)


def plan(data, with_optimal_check=True):
    t = {}
    depot, capacity = data["depot"], data["capacity_kg"]

    t0 = time.perf_counter()
    sorted_parcels = merge_sort(data["parcels"])
    t["sorting"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    best_value, chosen, dp = knapsack_dp(sorted_parcels, capacity)
    t["knapsack"] = time.perf_counter() - t0

    stops = sorted({p["dest"] for p in chosen})
    graph = Graph.from_dataset(data)

    t0 = time.perf_counter()
    matrix, prevs = distance_matrix(graph, [depot] + stops)
    t["dijkstra"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    tour, length = nearest_neighbor_tour(depot, stops, matrix)
    t["tsp_nn"] = time.perf_counter() - t0

    full_route = expand_route(tour, prevs)

    # arrival time at each stop (hours) and deadline check
    speed, clock, arrivals = data.get("speed_kmph", 30), 0.0, {}
    for a, b in zip(tour, tour[1:]):
        clock += matrix[a][b] / speed
        arrivals.setdefault(b, clock)
    late = [p for p in chosen if arrivals[p["dest"]] > p["deadline"]]

    result = {
        "sorted": sorted_parcels, "dp_table": dp, "best_value": best_value,
        "chosen": chosen, "load": sum(p["weight"] for p in chosen),
        "stops": stops, "matrix": matrix, "tour": tour, "length": length,
        "full_route": full_route, "arrivals": arrivals, "late": late,
        "timings": t, "optimal_length": None,
    }
    if with_optimal_check and 0 < len(stops) <= 8:
        _, result["optimal_length"] = brute_force_tour(depot, stops, matrix)
    return result
