#!/usr/bin/env python3
"""
Task generator for R simulation pipeline.

Generates N parallel simulation tasks followed by one aggregation task.
The aggregation task uses wildcard dependencies ("sim-*") to wait for
all simulations to complete before running.

This script runs on a compute node (via generates_source), NOT on the
head node. It writes the task JSON to a file that ScriptHut reads back.

Usage:
    python generate_tasks.py [--count N] [--working-dir DIR] [--output FILE]

Example sflow.json entry point:
    {
      "tasks": [{
        "id": "generate",
        "command": "python generate_tasks.py --count 5 --output ~/.cache/scripthut/sources/r-sim.json",
        "generates_source": "~/.cache/scripthut/sources/r-sim.json"
      }]
    }
"""

import argparse
import json
import os


def generate_tasks(count: int, working_dir: str, partition: str) -> dict:
    """Generate simulation tasks with a fan-out/fan-in pattern."""
    tasks = []

    # Fan-out: N parallel simulation tasks
    for i in range(count):
        tasks.append({
            "id": f"sim-{i}",
            "name": f"Simulation {i}",
            "command": f"module load R/4.5/4.5.1 && Rscript --vanilla gen_results.R {i} temp",
            "working_dir": working_dir,
            "partition": partition,
            "cpus": 1,
            "memory": "1G",
            "time_limit": "00:05:00",
        })

    # Fan-in: aggregate all simulation results
    tasks.append({
        "id": "aggregate",
        "name": "Aggregate Results",
        "command": "module load R/4.5/4.5.1 && Rscript --vanilla agg_results.R temp",
        "working_dir": working_dir,
        "partition": partition,
        "cpus": 1,
        "memory": "1G",
        "time_limit": "00:05:00",
        "deps": ["sim-*"],  # Wildcard: waits for ALL sim-* tasks
    })

    return {"tasks": tasks}


def main():
    parser = argparse.ArgumentParser(
        description="Generate R simulation tasks for ScriptHut"
    )
    parser.add_argument(
        "--count", "-n", type=int, default=5,
        help="Number of simulation tasks (default: 5)",
    )
    parser.add_argument(
        "--working-dir", "-d", type=str, default=os.getcwd(),
        help="Working directory on the cluster (default: current directory)",
    )
    parser.add_argument(
        "--partition", "-p", type=str, default="standard",
        help="Slurm partition to use (default: standard)",
    )
    parser.add_argument(
        "--output", "-o", type=str, default=None,
        help="Write JSON to file instead of stdout (for generates_source)",
    )

    args = parser.parse_args()
    tasks = generate_tasks(args.count, args.working_dir, args.partition)

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(tasks, f, indent=2)
        print(f"Wrote {len(tasks['tasks'])} tasks to {args.output}")
    else:
        print(json.dumps(tasks, indent=2))


if __name__ == "__main__":
    main()

