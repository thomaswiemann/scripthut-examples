#!/usr/bin/env python3
"""
Task generator for the Apptainer containerized simulation pipeline.

Simulation tasks set ``image:`` to a public Docker Hub URI. ScriptHut runs
each command inside that image via ``apptainer exec`` after a one-time

    scripthut image ensure python:3.12-slim --backend <b>

The generator itself does not pull or invoke Apptainer — submitting never
pulls, and hand-rolling ``apptainer pull`` inside a task re-implements the
image cache.

Usage:
    python3 generate_tasks.py [--count N] [--working-dir DIR] [--output FILE]
"""

import argparse
import json
import os


# Public Docker Hub image. ScriptHut adds the docker:// transport on pull.
IMAGE = "python:3.12-slim"


def generate_tasks(
    count: int, working_dir: str, partition: str, prefix: str = ""
) -> dict:
    """Generate containerized simulation tasks."""
    tasks = []

    # Fan-out: N parallel simulations inside the image
    for i in range(count):
        tasks.append({
            "id": f"{prefix}sim.{i}",
            "name": f"Simulation {i}",
            "command": f"python3 simulate.py {i} temp",
            "image": IMAGE,
            "working_dir": working_dir,
            "partition": partition,
            "cpus": 1,
            "memory": "2G",
            "time_limit": "00:05:00",
        })

    # Fan-in: aggregate results (host Python via env group — not the image)
    tasks.append({
        "id": f"{prefix}aggregate",
        "name": "Aggregate Results",
        "command": "python3 aggregate.py temp",
        "working_dir": working_dir,
        "partition": partition,
        "env": [{"include": ["python-booth"]}],
        "cpus": 1,
        "memory": "1G",
        "time_limit": "00:05:00",
        "deps": [f"{prefix}sim.*"],
    })

    return {"tasks": tasks}


def main():
    parser = argparse.ArgumentParser(
        description="Generate Apptainer containerized tasks for ScriptHut"
    )
    parser.add_argument(
        "--count", "-n", type=int, default=5,
        help="Number of simulation tasks (default: 5)",
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
        help="Prefix for task IDs (e.g. 'apptainer.' to avoid collisions in combined runs)",
    )

    args = parser.parse_args()

    tasks = generate_tasks(
        args.count, args.working_dir, args.partition, args.prefix
    )

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(tasks, f, indent=2)
        print(f"Wrote {len(tasks['tasks'])} tasks to {args.output}")
        print(f"Sim tasks use image: {IMAGE}")
    else:
        print(json.dumps(tasks, indent=2))


if __name__ == "__main__":
    main()
