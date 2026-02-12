#!/usr/bin/env python3
"""
Monte Carlo simulation running inside an Apptainer container.

This script uses ONLY the Python standard library (no numpy) since it
runs inside a minimal python:3.12-slim container.

Usage: python simulate.py <seed> <output_dir>

Simulates a random walk and computes statistics. The math module and
random module provide enough for meaningful compute without numpy.
"""

import csv
import math
import os
import random
import sys
import time


def simulate_random_walk(seed: int, n_walks: int = 200_000, n_steps: int = 500) -> dict:
    """Simulate random walks and compute statistics.

    Each walk is a cumulative sum of N(0,1) increments.
    We compute the mean final position, fraction of positive endpoints,
    and the mean maximum displacement.
    """
    rng = random.Random(seed)

    final_positions = []
    max_displacements = []
    positive_count = 0

    for _ in range(n_walks):
        position = 0.0
        max_pos = 0.0

        for _ in range(n_steps):
            # Box-Muller transform for normal random variable
            u1 = rng.random()
            u2 = rng.random()
            z = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
            position += z
            max_pos = max(max_pos, abs(position))

        final_positions.append(position)
        max_displacements.append(max_pos)
        if position > 0:
            positive_count += 1

    # Compute statistics
    mean_final = sum(final_positions) / n_walks
    var_final = sum((x - mean_final) ** 2 for x in final_positions) / (n_walks - 1)
    mean_max_disp = sum(max_displacements) / n_walks
    fraction_positive = positive_count / n_walks

    return {
        "seed": seed,
        "mean_final_position": mean_final,
        "std_final_position": math.sqrt(var_final),
        "fraction_positive": fraction_positive,
        "mean_max_displacement": mean_max_disp,
        "n_walks": n_walks,
        "n_steps": n_steps,
    }


def main():
    if len(sys.argv) != 3:
        print("Usage: python simulate.py <seed> <output_dir>", file=sys.stderr)
        sys.exit(1)

    seed = int(sys.argv[1])
    output_dir = sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)

    print(f"Container simulation {seed} started")
    print(f"  Hostname: {os.uname().nodename}")
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    result = simulate_random_walk(seed)

    output_file = os.path.join(output_dir, f"res_{seed}.csv")
    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=result.keys())
        writer.writeheader()
        writer.writerow(result)

    print(f"  Mean final position: {result['mean_final_position']:.4f}")
    print(f"  Fraction positive:   {result['fraction_positive']:.4f}")
    print(f"  Mean max displacement: {result['mean_max_displacement']:.2f}")
    print(f"  Result saved to: {output_file}")
    print(f"Container simulation {seed} complete")


if __name__ == "__main__":
    main()
