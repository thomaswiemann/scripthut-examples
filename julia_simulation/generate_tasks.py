#!/usr/bin/env python3
"""
Task generator for Julia bootstrap regression pipeline.

Generates N parallel bootstrap tasks followed by one aggregation task.
Each bootstrap task resamples data, fits OLS, and saves coefficients.
The aggregation task computes bootstrap confidence intervals.

This script runs on a compute node (via generates_source), NOT on the
head node. It writes the task JSON to a file that ScriptHut reads back.

Usage:
    python generate_tasks.py [--count N] [--working-dir DIR] [--output FILE]
"""

import argparse
import json
import os


def generate_tasks(count: int, working_dir: str, partition: str, prefix: str = "") -> dict:
    """Generate bootstrap tasks with a fan-out/fan-in pattern."""
    tasks = []

    # Fan-out: N parallel bootstrap replications
    for i in range(count):
        tasks.append({
            "id": f"{prefix}bootstrap.{i}",
            "name": f"Bootstrap {i}",
            "command": f"julia bootstrap.jl {i} temp",
            "working_dir": working_dir,
            "partition": partition,
            "environment": "julia-112",
            "cpus": 1,
            "memory": "1G",
            "time_limit": "00:05:00",
        })

    # Fan-in: aggregate bootstrap results
    tasks.append({
        "id": f"{prefix}aggregate",
        "name": "Aggregate Results",
        "command": "julia aggregate.jl temp",
        "working_dir": working_dir,
        "partition": partition,
        "environment": "julia-112",
        "cpus": 1,
        "memory": "1G",
        "time_limit": "00:05:00",
        "deps": [f"{prefix}bootstrap.*"],
    })

    return {"tasks": tasks}


def main():
    parser = argparse.ArgumentParser(
        description="Generate Julia bootstrap tasks for ScriptHut"
    )
    parser.add_argument(
        "--count", "-n", type=int, default=5,
        help="Number of bootstrap tasks (default: 10)",
    )
    parser.add_argument(
        "--working-dir", "-d", type=str,
        default=os.path.dirname(os.path.abspath(__file__)),
        help="Working directory on the cluster (default: script directory)",
    )
    parser.add_argument(
        "--partition", "-p", type=str, default="standard",
        help="Slurm partition to use (default: standard)",
    )
    parser.add_argument(
        "--output", "-o", type=str, default=None,
        help="Write JSON to file instead of stdout (for generates_source)",
    )
    parser.add_argument(
        "--prefix", type=str, default="",
        help="Prefix for task IDs (e.g. 'julia.' to avoid collisions in combined runs)",
    )

    args = parser.parse_args()
    tasks = generate_tasks(args.count, args.working_dir, args.partition, args.prefix)

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(tasks, f, indent=2)
        print(f"Wrote {len(tasks['tasks'])} tasks to {args.output}")
    else:
        print(json.dumps(tasks, indent=2))


if __name__ == "__main__":
    main()
