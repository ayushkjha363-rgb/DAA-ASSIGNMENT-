"""
knapsack.py - Optimal box filling (Phase 2, part 2)

0/1 Knapsack by Dynamic Programming.
  items    : parcels (weight = kg, value = priority score)
  capacity : maximum load of the courier vehicle (kg)
  Time  : O(n * W)      Space : O(n * W)  (full table kept so the chosen
                                           parcels can be traced back)
Brute force and greedy versions are provided for comparison / verification.
"""
from itertools import combinations


def knapsack_dp(parcels, capacity):
    n = len(parcels)
    # dp[i][w] = best value using the first i parcels with capacity w
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        wt, val = parcels[i - 1]["weight"], parcels[i - 1]["value"]
        for w in range(capacity + 1):
            dp[i][w] = dp[i - 1][w]                       # skip parcel i
            if wt <= w and dp[i - 1][w - wt] + val > dp[i][w]:
                dp[i][w] = dp[i - 1][w - wt] + val        # take parcel i
    # trace back which parcels were taken
    chosen, w = [], capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            chosen.append(parcels[i - 1])
            w -= parcels[i - 1]["weight"]
    chosen.reverse()
    return dp[n][capacity], chosen, dp


def knapsack_brute_force(parcels, capacity):
    """O(2^n) - checks every subset. Only usable for n <= ~20."""
    best_val, best_set = 0, []
    for r in range(len(parcels) + 1):
        for combo in combinations(parcels, r):
            wt = sum(p["weight"] for p in combo)
            val = sum(p["value"] for p in combo)
            if wt <= capacity and val > best_val:
                best_val, best_set = val, list(combo)
    return best_val, best_set


def knapsack_greedy(parcels, capacity):
    """Value/weight greedy - fast O(n log n) but NOT always optimal."""
    total_w = total_v = 0
    chosen = []
    for p in sorted(parcels, key=lambda p: p["value"] / p["weight"], reverse=True):
        if total_w + p["weight"] <= capacity:
            chosen.append(p); total_w += p["weight"]; total_v += p["value"]
    return total_v, chosen


def print_dp_table(parcels, dp, capacity, max_cols=21):
    """Pretty-print the DP table (evidence for the report)."""
    cols = min(capacity, max_cols - 1)
    print("DP table  (rows = parcels considered, columns = capacity in kg)")
    print("      " + "".join(f"{w:>4}" for w in range(cols + 1)))
    for i, row in enumerate(dp):
        label = "none" if i == 0 else parcels[i - 1]["id"]
        print(f"{label:>6}" + "".join(f"{v:>4}" for v in row[:cols + 1]))
