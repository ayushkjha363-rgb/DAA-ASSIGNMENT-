# Mini-Courier Planner
**Course:** Design & Analysis of Algorithms (ETCCDA302) - Capstone Assignment
**Name / Roll No.:** _<fill in>_  **Faculty:** Dr. Shweta Agarwal

Given a list of parcels and a road network, the program (1) sorts parcels by urgency,
(2) chooses the most valuable set that fits in the vehicle, (3) finds shortest roads
between all stops and (4) builds an ordered delivery route.

## How to run (Python 3.8+, no packages needed except matplotlib for charts)
```
python data_gen.py                               # (re)creates the sample datasets in data/
python main.py                                   # small dataset, shows the DP table
python main.py --data data/large_dataset.json    # 200 parcels, 60 customers
python main.py --data your_file.json             # any unseen dataset, same JSON format
python benchmark.py                              # runtime tests -> outputs/runtime_chart.png
pip install matplotlib                           # only if benchmark.py reports it missing
```

## Files
| File | Purpose |
|---|---|
| `data_gen.py` | Dataset format + random dataset generator |
| `sorting.py` | Merge Sort (used), Quick Sort and Insertion Sort (comparison) |
| `knapsack.py` | 0/1 Knapsack DP (used), brute force and greedy (verification) |
| `graph_routes.py` | Graph, Dijkstra, Nearest-Neighbour TSP, brute-force TSP |
| `planner.py` | Joins all steps into one pipeline and times each step |
| `main.py` | Command-line demo / output trace |
| `benchmark.py` | Performance tests and charts |
| `data/` | `small_dataset.json` (10 parcels), `large_dataset.json` (200 parcels) |
| `outputs/` | `sample_run_small.txt`, `sample_run_large.txt`, `runtime_chart.png`, `benchmark_results.csv`, `benchmark_output.txt` |

---
## Phase 1 - Problem design and planning
**Problem.** One vehicle leaves the depot `D`, must deliver parcels to customers and return.
It can carry `capacity_kg`. Not every parcel fits, so we choose the best subset and the best route.

**Data design.**
* Parcel: `id, dest, weight (integer kg), deadline (hours), priority (1-3), value`
  where `value = 10*priority + max(0, 24-deadline)//4` (urgent and early-deadline parcels are worth more).
* Graph: undirected, weighted (km), stored as an **adjacency list**. It is *not* a complete graph,
  so the shortest road between two customers must be computed, not just looked up.

**Algorithm pipeline and why each was chosen**

| Step | Algorithm | Reason | Complexity |
|---|---|---|---|
| Prioritise | Merge Sort | Guaranteed O(n log n), stable (equal parcels keep order) | O(n log n) time, O(n) space |
| Choose parcels | 0/1 Knapsack DP | Each parcel is taken whole or not at all; DP gives the *optimal* answer | O(nW) time, O(nW) space |
| Shortest roads | Dijkstra (binary heap) | Road lengths are non-negative | O((V+E) log V) per source |
| Visiting order | Nearest-Neighbour TSP | Exact TSP is NP-hard; NN is a fast approximation | O(k^2) for k stops |

```
parcels -> Merge Sort -> Knapsack DP -> stops -> Dijkstra from depot+stops
        -> distance matrix -> Nearest-Neighbour tour -> expand legs with Dijkstra paths -> route
```

## Phase 2 - Package prioritisation and box filling
Parcels are sorted by (deadline, -priority, weight). The sorted list is fed to the knapsack DP.
`dp[i][w]` = best value using the first `i` parcels with capacity `w`:
`dp[i][w] = max(dp[i-1][w], dp[i-1][w-wt_i] + val_i)`. The chosen parcels are traced back through the table.

**Result on `small_dataset.json` (capacity 20 kg):** selected P01, P06, P02, P03 - load 19/20 kg, value 99
(full table printed in `outputs/sample_run_small.txt`). DP result is checked against brute force in `benchmark.py`
(the assertion passes for every test).

## Phase 3 - Route maker and graph processing
Dijkstra is run from the depot and from every stop to build a distance matrix of real road distances.
Nearest-Neighbour then repeatedly visits the closest unvisited stop and returns to the depot.
Each leg is expanded into the actual road path (some legs pass through other towns or the depot).

**Small dataset:** order `D -> C3 -> C4 -> C5 -> D`, 38 km, identical to the brute-force optimum (ratio 1.00).
**Large dataset:** 36 stops, 337 km, arrival time of every stop and a list of late parcels are reported.

## Phase 4 - Performance testing and optimisation
Measured with `time.perf_counter()`, median of 3 runs (see `outputs/runtime_chart.png`).

| Parcels | Merge Sort | Knapsack DP | Dijkstra (all stops) | NN-TSP |
|---|---|---|---|---|
| 50 | 0.06 ms | 0.84 ms | 0.09 ms | 0.01 ms |
| 400 | 0.67 ms | 6.13 ms | 4.64 ms | 0.28 ms |
| 1600 | 3.11 ms | 22.86 ms | 25.82 ms | 0.42 ms |
| 3200 | 6.61 ms | 46.02 ms | 56.87 ms | 0.43 ms |

(Customers = n/5; at most 100 stops are used for Dijkstra/TSP, which is why NN-TSP flattens out.)

**Observations**
* Merge Sort grows slightly faster than linear (n log n); Insertion Sort is far slower at 1600 parcels (about 89 ms vs about 3 ms).
* Knapsack DP grows linearly with n for a fixed capacity; brute force doubles for every extra parcel and is
  already ~160 ms at 18 parcels while DP takes ~0.04 ms. Greedy is fastest but was 0-8 % worse in value.
* Dijkstra dominates at large sizes because it runs once per stop on a growing graph.
* Over 40 random 7-stop instances Nearest-Neighbour averaged **1.06x** the optimal length (worst 1.21x, optimal in 10/40).

**Correctness tests:** DP equals brute force (n = 8-18); NN tour compared with exact tour (40 cases);
small dataset traced by hand; larger dataset runs without error.

**Possible improvements**
1. Add 2-opt local search after Nearest-Neighbour to shorten the tour.
2. Cache Dijkstra results between trips, or stop each run early once all stops are reached.
3. Use a 1-D DP array (O(W) space) when the DP table is not needed for display.
4. Make deadlines part of the route choice (e.g. visit urgent stops first) - the large dataset shows 3 late parcels.
5. Support several vehicles / repeated trips for the parcels left over.

## Phase 5 - Result explanation
The pipeline turns an unordered pile of parcels into a trip plan: urgent parcels are considered first, the
vehicle is filled with the highest-value parcels that fit (value 99 from 19 kg on the small set), and a road route
is produced with distance and arrival times. Limitations: one vehicle, one trip, a greedy route that is not
guaranteed optimal, and deadlines are only *checked* (not enforced) when building the route.
Output traces are in `outputs/sample_run_small.txt` and `outputs/sample_run_large.txt`.

## Viva quick notes
* Why Merge Sort? Worst case n log n and stable. Quick Sort can degrade to n^2; Insertion Sort is n^2.
* Why DP not greedy? Greedy by value/weight can miss the best combination; DP is exact for integer weights.
* Why Dijkstra? Single-source shortest paths with non-negative weights. Negative edges would need Bellman-Ford.
* Why is NN only an approximation? It never looks ahead, so an early cheap choice can force a long return trip.
