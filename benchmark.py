"""
benchmark.py - Performance testing (Phase 4)

Measures the runtime of every major step for growing input sizes and saves
  outputs/runtime_chart.png   and   outputs/benchmark_results.csv
Each timing is the median of 3 runs.
"""
import csv
import random
import statistics
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from data_gen import make_dataset
from sorting import merge_sort, quick_sort, insertion_sort
from knapsack import knapsack_dp, knapsack_brute_force, knapsack_greedy
from graph_routes import (Graph, distance_matrix, nearest_neighbor_tour,
                          brute_force_tour)


def timed(fn, *args, repeat=3):
    runs = []
    for _ in range(repeat):
        t0 = time.perf_counter()
        out = fn(*args)
        runs.append(time.perf_counter() - t0)
    return statistics.median(runs), out


def main():
    sizes = [50, 100, 200, 400, 800, 1600, 3200]

    # ---- 1. major steps of the pipeline vs. number of parcels -------------
    rows = []
    for n in sizes:
        customers = max(12, n // 5)
        data = make_dataset(n, customers, capacity=200, seed=n)
        g = Graph.from_dataset(data)
        stops = [f"C{i}" for i in range(1, min(customers, 100) + 1)]
        ts, parcels = timed(merge_sort, data["parcels"])
        tk, (val, chosen, _) = timed(knapsack_dp, parcels, data["capacity_kg"])
        td, (matrix, _) = timed(distance_matrix, g, ["D"] + stops)
        tn, (_, length) = timed(nearest_neighbor_tour, "D", stops, matrix)
        rows.append([n, customers, len(stops), ts, tk, td, tn])
        print(f"n={n:<5} sort={ts*1e3:8.2f}ms  knapsack={tk*1e3:9.2f}ms  "
              f"dijkstra={td*1e3:8.2f}ms  tsp_nn={tn*1e3:7.2f}ms")

    with open("outputs/benchmark_results.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["parcels", "customers", "stops", "sort_s", "knapsack_s",
                    "dijkstra_s", "tsp_nn_s"])
        w.writerows(rows)

    # ---- 2. sorting algorithms compared ----------------------------------
    sort_sizes = [100, 200, 400, 800, 1600]
    sort_res = {"Merge Sort": [], "Quick Sort": [], "Insertion Sort": []}
    for n in sort_sizes:
        ps = make_dataset(n, 20, 50, seed=n + 1)["parcels"]
        for name, fn in [("Merge Sort", merge_sort), ("Quick Sort", quick_sort),
                         ("Insertion Sort", insertion_sort)]:
            sort_res[name].append(timed(fn, ps)[0])

    # ---- 3. knapsack: DP vs brute force vs greedy ------------------------
    ks_sizes = [8, 10, 12, 14, 16, 18]
    dp_t, bf_t, gr_t, gr_gap = [], [], [], []
    for n in ks_sizes:
        ps = make_dataset(n, 8, 50, seed=n + 2)["parcels"]
        cap = sum(p["weight"] for p in ps) // 2
        t1, (v_dp, _, _) = timed(knapsack_dp, ps, cap)
        t2, (v_bf, _) = timed(knapsack_brute_force, ps, cap, repeat=1)
        t3, (v_gr, _) = timed(knapsack_greedy, ps, cap)
        assert v_dp == v_bf, "DP result must equal brute force"
        dp_t.append(t1); bf_t.append(t2); gr_t.append(t3)
        gr_gap.append(100 * (v_dp - v_gr) / v_dp)

    # ---- 4. quality of the Nearest-Neighbour approximation ---------------
    ratios = []
    for seed in range(40):
        d = make_dataset(1, 12, 10, seed=1000 + seed)
        g = Graph.from_dataset(d)
        stops = random.Random(seed).sample([f"C{i}" for i in range(1, 13)], 7)
        m, _ = distance_matrix(g, ["D"] + stops)
        _, nn = nearest_neighbor_tour("D", stops, m)
        _, opt = brute_force_tour("D", stops, m)
        ratios.append(nn / opt)
    avg_ratio, worst_ratio = statistics.mean(ratios), max(ratios)
    exact = sum(1 for r in ratios if abs(r - 1) < 1e-9)
    print(f"\nNN tour vs optimal over 40 instances (7 stops): average ratio "
          f"{avg_ratio:.3f}, worst {worst_ratio:.3f}, optimal in {exact}/40")
    print("Knapsack greedy value gap vs DP (%):", [round(x, 1) for x in gr_gap])

    # ---- charts -----------------------------------------------------------
    fig, ax = plt.subplots(2, 2, figsize=(13, 9))
    ns = [r[0] for r in rows]
    for idx, label in [(3, "Merge Sort"), (4, "Knapsack DP"),
                       (5, "Dijkstra (all stops)"), (6, "Nearest-Neighbour TSP")]:
        ax[0][0].plot(ns, [r[idx] * 1e3 for r in rows], marker="o", label=label)
    ax[0][0].set(title="Pipeline steps vs. number of parcels",
                 xlabel="Parcels (n)", ylabel="Runtime (ms, log scale)", yscale="log")
    ax[0][0].legend(); ax[0][0].grid(alpha=.3)

    for name, ts_ in sort_res.items():
        ax[0][1].plot(sort_sizes, [t * 1e3 for t in ts_], marker="o", label=name)
    ax[0][1].set(title="Sorting algorithms compared",
                 xlabel="Parcels (n)", ylabel="Runtime (ms)")
    ax[0][1].legend(); ax[0][1].grid(alpha=.3)

    ax[1][0].plot(ks_sizes, [t * 1e3 for t in bf_t], marker="o", label="Brute force O(2^n)")
    ax[1][0].plot(ks_sizes, [t * 1e3 for t in dp_t], marker="o", label="DP O(nW)")
    ax[1][0].plot(ks_sizes, [t * 1e3 for t in gr_t], marker="o", label="Greedy (not always optimal)")
    ax[1][0].set(title="Knapsack: DP vs brute force vs greedy",
                 xlabel="Parcels (n)", ylabel="Runtime (ms, log scale)", yscale="log")
    ax[1][0].legend(); ax[1][0].grid(alpha=.3)

    ax[1][1].hist(ratios, bins=10, color="#4c78a8", edgecolor="white")
    ax[1][1].axvline(avg_ratio, color="red", ls="--", label=f"average = {avg_ratio:.3f}")
    ax[1][1].set(title="Nearest-Neighbour tour length / optimal (40 tests)",
                 xlabel="Approximation ratio", ylabel="Number of tests")
    ax[1][1].legend()

    fig.suptitle("Mini-Courier Planner - Runtime and Quality Results", fontsize=14)
    fig.tight_layout()
    fig.savefig("outputs/runtime_chart.png", dpi=130)
    print("Saved outputs/runtime_chart.png and outputs/benchmark_results.csv")


if __name__ == "__main__":
    main()
