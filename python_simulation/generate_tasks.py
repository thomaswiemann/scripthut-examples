#!/usr/bin/env python3
"""
Task generator for Python Monte Carlo option pricing pipeline.

Generates N parallel pricing tasks followed by one aggregation task.
Each pricing task estimates the price of a European call option using
Monte Carlo simulation of geometric Brownian motion.

This script runs on a compute node (via generates_source), NOT on the
head node. It writes the task JSON to a file that ScriptHut reads back.

Usage:
    python generate_tasks.py [--count N] [--working-dir DIR] [--output FILE]
"""

import argparse
import json
import os


def generate_tasks(count: int, working_dir: str, prefix: str = "", partition: str = None) -> dict:
    """Generate Monte Carlo pricing tasks with a fan-out/fan-in pattern."""
    tasks = []

    # Fan-out: N parallel pricing simulations
    for i in range(count):
        task = {
            "id": f"{prefix}pricing.{i}",
            "name": f"Pricing {i}",
            "command": f"python3 price_option.py {i} temp",
            "working_dir": working_dir,
            "environment": "python",
            "cpus": 1,
            "memory": "1G",
            "time_limit": "00:05:00",
        }
        if partition:
            task["partition"] = partition
        tasks.append(task)

    # Fan-in: aggregate all pricing estimates
    agg_task = {
        "id": f"{prefix}aggregate",
        "name": "Aggregate Results",
        "command": "python3 aggregate.py temp",
        "working_dir": working_dir,
        "environment": "python",
        "cpus": 1,
        "memory": "1G",
        "time_limit": "00:05:00",
        "deps": [f"{prefix}pricing.*"],
    }
    if partition:
        agg_task["partition"] = partition
    tasks.append(agg_task)

    return {"tasks": tasks}


def main():
    parser = argparse.ArgumentParser(
        description="Generate Monte Carlo pricing tasks for ScriptHut"
    )
    parser.add_argument(
        "--count", "-n", type=int, default=5,
        help="Number of pricing tasks (default: 5)",
    )
    parser.add_argument(
        "--working-dir", "-d", type=str,
        default=os.path.dirname(os.path.abspath(__file__)),
        help="Working directory on the cluster (default: script directory)",
    )
    parser.add_argument(
        "--partition", "-p", type=str, default=None,
        help="Slurm partition (omit to use cluster default)",
    )
    parser.add_argument(
        "--output", "-o", type=str, default=None,
        help="Write JSON to file instead of stdout (for generates_source)",
    )
    parser.add_argument(
        "--prefix", type=str, default="",
        help="Prefix for task IDs (e.g. 'python.' to avoid collisions in combined runs)",
    )

    args = parser.parse_args()
    tasks = generate_tasks(args.count, args.working_dir, args.prefix, args.partition)

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(tasks, f, indent=2)
        print(f"Wrote {len(tasks['tasks'])} tasks to {args.output}")
    else:
        print(json.dumps(tasks, indent=2))


if __name__ == "__main__":
    main()
