#!/usr/bin/env python3
"""
Task generator for Apptainer containerized simulation pipeline.

This generator:
1. Pulls/builds the container image (if not already cached)
2. Generates N parallel simulation tasks that run inside the container
3. Generates one aggregation task (runs outside the container)

The container image is cached at ~/.cache/scripthut/containers/ so it
is only pulled once. All simulation tasks reference the cached .sif file.

Usage:
    python generate_tasks.py [--count N] [--working-dir DIR] [--output FILE]
"""

import argparse
import json
import os
import subprocess
import sys


SIF_CACHE_DIR = os.path.expanduser("~/.cache/scripthut/containers")
SIF_NAME = "python312-slim.sif"
DOCKER_IMAGE = "docker://python:3.12-slim"


def ensure_container(sif_path: str) -> None:
    """Pull the container image if not already cached."""
    if os.path.exists(sif_path):
        print(f"Container already cached at {sif_path}")
        return

    os.makedirs(os.path.dirname(sif_path), exist_ok=True)
    print(f"Pulling container: {DOCKER_IMAGE}")
    print(f"  Saving to: {sif_path}")

    result = subprocess.run(
        ["apptainer", "pull", sif_path, DOCKER_IMAGE],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"Failed to pull container: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    print(f"Container ready ({os.path.getsize(sif_path) / 1e6:.1f} MB)")


def generate_tasks(count: int, working_dir: str, partition: str, sif_path: str, prefix: str = "") -> dict:
    """Generate containerized simulation tasks."""
    tasks = []

    # Fan-out: N parallel simulations inside the container
    for i in range(count):
        tasks.append({
            "id": f"{prefix}sim.{i}",
            "name": f"Simulation {i}",
            "command": (
                f"env -u PYTHONHOME -u PYTHONPATH "
                f"apptainer exec {sif_path} python3 simulate.py {i} temp"
            ),
            "working_dir": working_dir,
            "partition": partition,
            "cpus": 1,
            "memory": "2G",
            "time_limit": "00:05:00",
        })

    # Fan-in: aggregate results (no container needed — just reads CSVs)
    tasks.append({
        "id": f"{prefix}aggregate",
        "name": "Aggregate Results",
        "command": "python3 aggregate.py temp",
        "working_dir": working_dir,
        "partition": partition,
        "environment": "python-booth",
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

    # Pull container first (only once)
    sif_path = os.path.join(SIF_CACHE_DIR, SIF_NAME)
    ensure_container(sif_path)

    tasks = generate_tasks(args.count, args.working_dir, args.partition, sif_path, args.prefix)

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(tasks, f, indent=2)
        print(f"Wrote {len(tasks['tasks'])} tasks to {args.output}")
    else:
        print(json.dumps(tasks, indent=2))


if __name__ == "__main__":
    main()
