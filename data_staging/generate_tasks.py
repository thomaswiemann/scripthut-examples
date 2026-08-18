#!/usr/bin/env python3
"""
Task generator for the data staging example.

Generates N parallel chunk tasks followed by one aggregation task. Each
chunk task reads its slice of the staged dataset and writes OLS sufficient
statistics; the aggregation task pools them into a single fit.

This script runs on a compute node (via generates_source), NOT on the head
node. By the time it runs, ScriptHut has already staged the dataset, so it
can read $DATA_DIR to report what it found — a cheap check that the copy
arrived before any real work is scheduled.

Usage:
    python generate_tasks.py [--count N] [--working-dir DIR] [--output FILE]
"""

import argparse
import csv
import json
import os
import sys

DATA_FILE = "observations.csv"


def describe_dataset() -> None:
    """Report the staged dataset, or fail before generating unusable tasks."""
    data_dir = os.environ.get("DATA_DIR") or os.environ.get("DATA_EXAMPLE_PANEL")
    if not data_dir:
        print(
            "Neither DATA_DIR nor DATA_EXAMPLE_PANEL is set. Add "
            '"data": ["example-panel"] to the workflow JSON.',
            file=sys.stderr,
        )
        sys.exit(1)

    path = os.path.join(data_dir, DATA_FILE)
    if not os.path.isfile(path):
        print(f"Staged dataset is missing {DATA_FILE}: {path}", file=sys.stderr)
        sys.exit(1)

    with open(path, newline="") as f:
        n_rows = sum(1 for _ in csv.DictReader(f))

    print(f"Staged dataset: {data_dir}")
    print(f"  {DATA_FILE}: {n_rows} rows")


def generate_tasks(count: int, working_dir: str, partition: str, prefix: str = "") -> dict:
    """Generate chunk tasks with a fan-out/fan-in pattern."""
    tasks = []

    # Fan-out: each chunk summarizes a disjoint slice of the staged rows.
    for i in range(count):
        tasks.append({
            "id": f"{prefix}chunk.{i}",
            "name": f"Summarize chunk {i}",
            "command": f"python3 summarize_chunk.py {i} {count} temp",
            "working_dir": working_dir,
            "partition": partition,
            "env": [{"include": ["python-booth"]}],
            "cpus": 1,
            "memory": "1G",
            "time_limit": "00:05:00",
        })

    # Fan-in: pool the sufficient statistics into one fit.
    tasks.append({
        "id": f"{prefix}aggregate",
        "name": "Pool chunk statistics",
        "command": "python3 aggregate.py temp",
        "working_dir": working_dir,
        "partition": partition,
        "env": [{"include": ["python-booth"]}],
        "cpus": 1,
        "memory": "1G",
        "time_limit": "00:05:00",
        "deps": [f"{prefix}chunk.*"],
    })

    return {"tasks": tasks}


def main():
    parser = argparse.ArgumentParser(
        description="Generate data staging tasks for ScriptHut"
    )
    parser.add_argument(
        "--count", "-n", type=int, default=4,
        help="Number of chunk tasks (default: 4)",
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
        help="Prefix for task IDs (e.g. 'data.' to avoid collisions in combined runs)",
    )

    args = parser.parse_args()
    if args.count < 1:
        parser.error("--count must be at least 1")

    describe_dataset()
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
