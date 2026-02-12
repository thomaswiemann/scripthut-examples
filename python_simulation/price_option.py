#!/usr/bin/env python3
"""
Monte Carlo pricing of a European call option via geometric Brownian motion.

Usage: python price_option.py <seed> <output_dir>

Arguments:
  seed       - Integer seed for reproducibility
  output_dir - Directory to write the result CSV

Output: <output_dir>/res_<seed>.csv

The simulation generates price paths under the risk-neutral measure:
  dS = r * S * dt + sigma * S * dW

and prices a European call with payoff max(S_T - K, 0).
"""

import csv
import os
import sys
import time

import numpy as np


def price_european_call(
    seed: int,
    n_paths: int = 500_000,
    n_steps: int = 100,
    S0: float = 100.0,
    K: float = 105.0,
    r: float = 0.05,
    sigma: float = 0.2,
    T: float = 1.0,
) -> dict:
    """Price a European call option using Monte Carlo simulation."""
    rng = np.random.default_rng(seed)
    dt = T / n_steps

    # Simulate GBM paths
    # log(S_t+1) = log(S_t) + (r - 0.5*sigma^2)*dt + sigma*sqrt(dt)*Z
    drift = (r - 0.5 * sigma**2) * dt
    vol = sigma * np.sqrt(dt)

    log_S = np.full(n_paths, np.log(S0))
    for _ in range(n_steps):
        Z = rng.standard_normal(n_paths)
        log_S += drift + vol * Z

    S_T = np.exp(log_S)

    # European call payoff: max(S_T - K, 0), discounted
    payoffs = np.maximum(S_T - K, 0.0)
    discount = np.exp(-r * T)
    price = discount * np.mean(payoffs)
    se = discount * np.std(payoffs) / np.sqrt(n_paths)

    return {
        "seed": seed,
        "price": price,
        "se": se,
        "n_paths": n_paths,
        "n_steps": n_steps,
        "S0": S0,
        "K": K,
        "r": r,
        "sigma": sigma,
        "T": T,
    }


def main():
    if len(sys.argv) != 3:
        print("Usage: python price_option.py <seed> <output_dir>", file=sys.stderr)
        sys.exit(1)

    seed = int(sys.argv[1])
    output_dir = sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)

    print(f"Pricing simulation {seed} started")
    print(f"  Hostname: {os.uname().nodename}")
    print(f"  Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    result = price_european_call(seed)

    output_file = os.path.join(output_dir, f"res_{seed}.csv")
    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=result.keys())
        writer.writeheader()
        writer.writerow(result)

    print(f"  Option price: {result['price']:.4f} (SE: {result['se']:.4f})")
    print(f"  Result saved to: {output_file}")
    print(f"Pricing simulation {seed} complete")


if __name__ == "__main__":
    main()
