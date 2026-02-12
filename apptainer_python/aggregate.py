#!/usr/bin/env python3
"""
Aggregate random walk simulation results.

Usage: python aggregate.py <input_dir>

Arguments:
  input_dir - Directory containing res_*.csv files from simulate.py

Output: results.csv in the current working directory
"""

import csv
import glob
import math
import os
import sys


def main():
    if len(sys.argv) != 2:
        print("Usage: python aggregate.py <input_dir>", file=sys.stderr)
        sys.exit(1)

    input_dir = sys.argv[1]
    print("Aggregating container simulation results")
    print(f"  Input directory: {input_dir}")

    files = sorted(glob.glob(os.path.join(input_dir, "res_*.csv")))

    # Retry up to 30s in case of NFS propagation delay
    import time
    retries = 0
    while not files and retries < 6:
        retries += 1
        print(f"  No files yet, retrying in 5s... (attempt {retries}/6)")
        time.sleep(5)
        files = sorted(glob.glob(os.path.join(input_dir, "res_*.csv")))

    print(f"  Found {len(files)} result files")

    if not files:
        print("No result files found!", file=sys.stderr)
        sys.exit(1)

    # Read all results
    fractions = []
    max_disps = []
    for path in files:
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                fractions.append(float(row["fraction_positive"]))
                max_disps.append(float(row["mean_max_displacement"]))

    n = len(fractions)
    mean_frac = sum(fractions) / n
    mean_disp = sum(max_disps) / n
    se_frac = (sum((x - mean_frac) ** 2 for x in fractions) / (n * (n - 1))) ** 0.5 if n > 1 else 0.0

    # Write summary
    with open("results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["n_simulations", "mean_fraction_positive", "se_fraction_positive", "mean_max_displacement"])
        writer.writerow([n, f"{mean_frac:.6f}", f"{se_frac:.6f}", f"{mean_disp:.4f}"])

    print(f"\nAggregated Results:")
    print(f"  Simulations:           {n}")
    print(f"  Mean fraction positive: {mean_frac:.4f} (SE: {se_frac:.4f})")
    print(f"  Mean max displacement:  {mean_disp:.2f}")
    print(f"  Expected fraction:      0.5000 (symmetric random walk)")
    print(f"\nResults saved to: results.csv")


if __name__ == "__main__":
    main()
