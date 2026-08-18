#!/usr/bin/env python3
"""
Combine per-chunk sufficient statistics into a single OLS fit.

Usage: python aggregate.py <input_dir>

Arguments:
  input_dir - Directory containing partial_*.csv from summarize_chunk.py

Output: results.csv in the current working directory

Summing the per-chunk statistics reproduces the totals over the whole
dataset, so the slope and intercept here are exactly what fitting on all
rows at once would give — the split into chunks changes nothing but where
the arithmetic happened.
"""

import csv
import glob
import os
import sys

FIELDS = ("n", "sum_x", "sum_y", "sum_xx", "sum_xy", "sum_yy")


def main():
    if len(sys.argv) != 2:
        print("Usage: python aggregate.py <input_dir>", file=sys.stderr)
        sys.exit(1)

    input_dir = sys.argv[1]
    print("Aggregating chunk statistics")
    print(f"  Input directory: {input_dir}")

    files = sorted(glob.glob(os.path.join(input_dir, "partial_*.csv")))
    print(f"  Found {len(files)} partial files")
    if not files:
        print("No partial files found!", file=sys.stderr)
        sys.exit(1)

    totals = dict.fromkeys(FIELDS, 0.0)
    for path in files:
        with open(path, newline="") as f:
            for row in csv.DictReader(f):
                for key in FIELDS:
                    totals[key] += float(row[key])

    n = totals["n"]
    if n < 2:
        print(f"Need at least 2 observations, got {n:.0f}", file=sys.stderr)
        sys.exit(1)

    denom = n * totals["sum_xx"] - totals["sum_x"] ** 2
    if denom == 0:
        print("x has no variation; slope is undefined", file=sys.stderr)
        sys.exit(1)

    slope = (n * totals["sum_xy"] - totals["sum_x"] * totals["sum_y"]) / denom
    intercept = (totals["sum_y"] - slope * totals["sum_x"]) / n

    # For an OLS fit with an intercept, the residual sum of squares reduces
    # to this identity in the sufficient statistics.
    sse = totals["sum_yy"] - intercept * totals["sum_y"] - slope * totals["sum_xy"]
    sst = totals["sum_yy"] - totals["sum_y"] ** 2 / n
    r2 = 1 - sse / sst if sst > 0 else float("nan")

    with open("results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["n_obs", "n_chunks", "intercept", "slope", "r_squared"])
        writer.writerow(
            [int(n), len(files), f"{intercept:.6f}", f"{slope:.6f}", f"{r2:.6f}"]
        )

    print("\nPooled OLS fit (y = intercept + slope * x):")
    print(f"  Observations: {int(n)} across {len(files)} chunks")
    print(f"  Intercept:    {intercept:.4f}")
    print(f"  Slope:        {slope:.4f}")
    print(f"  R-squared:    {r2:.4f}")
    print("\nResults saved to: results.csv")


if __name__ == "__main__":
    main()
