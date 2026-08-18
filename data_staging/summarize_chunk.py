#!/usr/bin/env python3
"""
Compute OLS sufficient statistics for one slice of the staged dataset.

Usage: python summarize_chunk.py <chunk_index> <n_chunks> <output_dir>

Arguments:
  chunk_index - 0-based index of this chunk
  n_chunks    - Total number of chunks the data is split into
  output_dir  - Directory to write the partial result CSV

Output: <output_dir>/partial_<chunk_index>.csv

Reads observations.csv from the staged dataset directory, which ScriptHut
copied onto this cluster before the run and exposes as $DATA_DIR. The sums
below decompose exactly across chunks, so combining them in the aggregate
step gives the same fit as regressing on the full data at once.
"""

import csv
import os
import sys

DATA_FILE = "observations.csv"


def dataset_dir() -> str:
    """Locate the staged dataset, or explain what is missing and exit.

    ScriptHut sets DATA_DIR when the workflow declares exactly one dataset,
    and always sets DATA_<NAME>. Neither being present means the task is not
    running under a workflow that declared the data, so failing here beats
    reading whatever happens to sit in the working directory.
    """
    path = os.environ.get("DATA_DIR") or os.environ.get("DATA_EXAMPLE_PANEL")
    if not path:
        print(
            "Neither DATA_DIR nor DATA_EXAMPLE_PANEL is set. This task must run "
            "from a workflow whose JSON declares \"data\": [\"example-panel\"].",
            file=sys.stderr,
        )
        sys.exit(1)
    if not os.path.isdir(path):
        print(f"Staged dataset directory does not exist: {path}", file=sys.stderr)
        sys.exit(1)
    return path


def read_rows(path: str) -> list[tuple[float, float]]:
    with open(path, newline="") as f:
        return [(float(row["x"]), float(row["y"])) for row in csv.DictReader(f)]


def chunk_bounds(total: int, index: int, n_chunks: int) -> tuple[int, int]:
    """Split ``total`` rows into ``n_chunks`` contiguous, disjoint slices."""
    start = total * index // n_chunks
    stop = total * (index + 1) // n_chunks
    return start, stop


def main():
    if len(sys.argv) != 4:
        print(
            "Usage: python summarize_chunk.py <chunk_index> <n_chunks> <output_dir>",
            file=sys.stderr,
        )
        sys.exit(1)

    index = int(sys.argv[1])
    n_chunks = int(sys.argv[2])
    output_dir = sys.argv[3]
    if not 0 <= index < n_chunks:
        print(f"chunk_index {index} out of range for {n_chunks} chunks", file=sys.stderr)
        sys.exit(1)

    data_dir = dataset_dir()
    data_path = os.path.join(data_dir, DATA_FILE)

    print(f"Chunk {index} of {n_chunks} started")
    print(f"  Hostname: {os.uname().nodename}")
    print(f"  Dataset:  {data_dir}")

    rows = read_rows(data_path)
    start, stop = chunk_bounds(len(rows), index, n_chunks)
    mine = rows[start:stop]
    print(f"  Rows:     {start}..{stop - 1} ({len(mine)} of {len(rows)})")

    stats = {
        "chunk": index,
        "n": len(mine),
        "sum_x": sum(x for x, _ in mine),
        "sum_y": sum(y for _, y in mine),
        "sum_xx": sum(x * x for x, _ in mine),
        "sum_xy": sum(x * y for x, y in mine),
        "sum_yy": sum(y * y for _, y in mine),
    }

    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"partial_{index}.csv")
    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(stats))
        writer.writeheader()
        writer.writerow(stats)

    print(f"  Wrote {output_file}")
    print(f"Chunk {index} complete")


if __name__ == "__main__":
    main()
