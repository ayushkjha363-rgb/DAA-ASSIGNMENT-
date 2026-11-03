"""
data_gen.py - Dataset design + generator (Phase 1)

Dataset (JSON) format
---------------------
{
  "depot": "D",                       # start / end of every trip
  "capacity_kg": 20,                  # vehicle load limit (integer kg)
  "speed_kmph": 30,                   # used to estimate arrival times
  "nodes": ["D", "C1", ...],          # depot + customer locations
  "edges": [["D","C1",4], ...],       # undirected roads, weight = km
  "parcels": [
     {"id":"P01","dest":"C3","weight":4,   # kg (integer, needed by the DP table)
      "deadline":6,                        # hours from dispatch
      "priority":3,                        # 1 = normal, 2 = express, 3 = urgent
      "value":34}                          # = 10*priority + urgency bonus
  ]
}
value = 10 * priority + max(0, 24 - deadline) // 4   (urgent + early => more valuable)
The road graph is NOT complete, so Dijkstra is genuinely needed to find routes.
"""
import json
import random
import sys


def make_dataset(n_parcels, n_customers, capacity, seed=1, max_deadline=24):
    rnd = random.Random(seed)
    customers = [f"C{i}" for i in range(1, n_customers + 1)]
    nodes = ["D"] + customers
    edges, seen = [], set()

    def add(u, v):
        if u != v and (u, v) not in seen and (v, u) not in seen:
            seen.add((u, v))
            edges.append([u, v, rnd.randint(1, 20)])

    # random spanning tree guarantees the graph is connected ...
    order = nodes[:]
    rnd.shuffle(order)
    for i in range(1, len(order)):
        add(order[i], order[rnd.randrange(i)])
    # ... extra roads make alternative (shorter) routes possible
    for _ in range(n_customers * 2):
        add(rnd.choice(nodes), rnd.choice(nodes))

    parcels = []
    for i in range(1, n_parcels + 1):
        priority = rnd.choice([1, 1, 2, 2, 3])
        deadline = rnd.randint(2, max_deadline)
        parcels.append({
            "id": f"P{i:02d}" if n_parcels < 100 else f"P{i:04d}",
            "dest": rnd.choice(customers),
            "weight": rnd.randint(1, 9),
            "deadline": deadline,
            "priority": priority,
            "value": 10 * priority + max(0, 24 - deadline) // 4,
        })
    return {"depot": "D", "capacity_kg": capacity, "speed_kmph": 30,
            "nodes": nodes, "edges": edges, "parcels": parcels}


def save(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=1)


if __name__ == "__main__":
    save(make_dataset(10, 7, 20, seed=7), "data/small_dataset.json")
    save(make_dataset(200, 60, 100, seed=11), "data/large_dataset.json")
    print("Created data/small_dataset.json and data/large_dataset.json")
