"""
main.py - Mini-Courier Planner (command-line demo)

Usage:
    python main.py                                   # small dataset
    python main.py --data data/large_dataset.json    # larger dataset
    python main.py --data my_unseen_data.json        # any dataset in the same format
"""
import argparse
import os

from planner import load_dataset, plan
from knapsack import print_dp_table


def show(data, r, show_table):
    cap = data["capacity_kg"]
    line = "=" * 72
    print(line, "\n MINI-COURIER PLANNER\n", line, sep="")
    print(f"Parcels: {len(data['parcels'])}   Locations: {len(data['nodes'])}   "
          f"Roads: {len(data['edges'])}   Vehicle capacity: {cap} kg\n")

    print("STEP 1 - Parcels sorted by deadline (then priority)  [Merge Sort]")
    print(f"{'ID':<7}{'Dest':<6}{'kg':>3}{'Deadline':>10}{'Prio':>6}{'Value':>7}")
    shown = r["sorted"][:15]
    for p in shown:
        print(f"{p['id']:<7}{p['dest']:<6}{p['weight']:>3}{p['deadline']:>9}h{p['priority']:>6}{p['value']:>7}")
    if len(r["sorted"]) > len(shown):
        print(f"... ({len(r['sorted']) - len(shown)} more)")

    print("\nSTEP 2 - Best set of parcels for this trip  [0/1 Knapsack DP]")
    if show_table and len(data["parcels"]) <= 12:
        print_dp_table(r["sorted"], r["dp_table"], cap)
        print()
    for p in r["chosen"]:
        print(f"  {p['id']}  -> {p['dest']:<4} {p['weight']} kg  value {p['value']}")
    print(f"  Load: {r['load']}/{cap} kg   Total value: {r['best_value']}   "
          f"Parcels left for later trips: {len(data['parcels']) - len(r['chosen'])}")

    print("\nSTEP 3 - Delivery route  [Dijkstra + Nearest-Neighbour TSP]")
    print(f"  Stops to visit : {', '.join(r['stops'])}")
    print(f"  Visiting order : {' -> '.join(r['tour'])}")
    print(f"  Road route     : {' -> '.join(r['full_route'])}")
    print(f"  Total distance : {r['length']} km")
    if r["optimal_length"] is not None:
        ratio = r["length"] / r["optimal_length"] if r["optimal_length"] else 1
        print(f"  Optimal (brute force): {r['optimal_length']} km  "
              f"-> approximation ratio {ratio:.2f}")
    print("  Arrival times  : " + ", ".join(
        f"{s} {t:.1f}h" for s, t in r["arrivals"].items()))
    if r["late"]:
        print("  WARNING late parcels: " + ", ".join(
            f"{p['id']} (due {p['deadline']}h)" for p in r["late"]))
    else:
        print("  All selected parcels arrive before their deadlines.")

    print("\nRUNTIME OF MAJOR STEPS")
    for k, v in r["timings"].items():
        print(f"  {k:<10}{v * 1000:>10.3f} ms")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Mini-Courier Planner")
    ap.add_argument("--data", default="data/small_dataset.json")
    ap.add_argument("--no-table", action="store_true", help="hide the DP table")
    args = ap.parse_args()
    data = load_dataset(args.data)
    show(data, plan(data), not args.no_table)
