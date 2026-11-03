"""
sorting.py - Parcel prioritisation (Phase 2, part 1)

Merge Sort is the algorithm used by the planner:
  * Time  : O(n log n) in best, average AND worst case
  * Space : O(n) auxiliary
  * Stable: parcels with identical keys keep their original relative order
Quick Sort and Insertion Sort are included only for the benchmark comparison.
"""
import random


def parcel_key(p):
    """Earliest deadline first; ties -> higher priority first; then lighter first."""
    return (p["deadline"], -p["priority"], p["weight"])


def merge_sort(items, key=parcel_key):
    if len(items) <= 1:
        return list(items)
    mid = len(items) // 2
    left = merge_sort(items[:mid], key)
    right = merge_sort(items[mid:], key)
    merged, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):      # <= keeps the sort stable
            merged.append(left[i]); i += 1
        else:
            merged.append(right[j]); j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def quick_sort(items, key=parcel_key):
    """Randomised-pivot Quick Sort: O(n log n) average, O(n^2) worst case."""
    if len(items) <= 1:
        return list(items)
    pivot = key(random.choice(items))
    less = [x for x in items if key(x) < pivot]
    equal = [x for x in items if key(x) == pivot]
    more = [x for x in items if key(x) > pivot]
    return quick_sort(less, key) + equal + quick_sort(more, key)


def insertion_sort(items, key=parcel_key):
    """O(n^2) worst/average, O(n) best. Fine for tiny inputs only."""
    arr = list(items)
    for i in range(1, len(arr)):
        cur, j = arr[i], i - 1
        while j >= 0 and key(arr[j]) > key(cur):
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = cur
    return arr
