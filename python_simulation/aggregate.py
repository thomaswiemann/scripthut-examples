#!/usr/bin/env python3
"""
Aggregate Monte Carlo pricing results from individual simulations.

Usage: python aggregate.py <input_dir>

Arguments:
  input_dir - Directory containing res_*.csv files from price_option.py

Output: results.csv in the current working directory
"""

import csv
import glob
import os
import sys


def main():
    if len(sys.argv) != 2:
        print("Usage: python aggregate.py <input_dir>", file=sys.stderr)
        sys.exit(1)

    input_dir = sys.argv[1]
    print("Aggregating pricing results")
    print(f"  Input directory: {input_dir}")

    files = sorted(glob.glob(os.path.join(input_dir, "res_*.csv")))
    print(f"  Found {len(files)} result files")

    if not files:
        print("No result files found!", file=sys.stderr)
        sys.exit(1)

    # Read all results
    prices = []
    ses = []
    for path in files:
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                prices.append(float(row["price"]))
                ses.append(float(row["se"]))

    n = len(prices)
    mean_price = sum(prices) / n
    # SE of the combined estimate (average of independent estimates)
    combined_se = (sum(s**2 for s in ses) / n**2) ** 0.5
    min_price = min(prices)
    max_price = max(prices)

    # Write summary
    with open("results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["n_simulations", "mean_price", "combined_se", "min_price", "max_price"])
        writer.writerow([n, f"{mean_price:.6f}", f"{combined_se:.6f}", f"{min_price:.6f}", f"{max_price:.6f}"])

    print(f"\nAggregated Results:")
    print(f"  Simulations:  {n}")
    print(f"  Mean price:   {mean_price:.4f}")
    print(f"  Combined SE:  {combined_se:.4f}")
    print(f"  Range:        [{min_price:.4f}, {max_price:.4f}]")
    print(f"\nResults saved to: results.csv")


if __name__ == "__main__":
    main()
