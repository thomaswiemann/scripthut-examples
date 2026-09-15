# Apptainer Containerized Simulation

A ScriptHut example demonstrating Slurm tasks that set `image:`. ScriptHut
runs each simulation command inside the image via Apptainer.

## What It Does

Runs a random walk simulation inside a public Python container:

1. **Ensure** — pull the image once onto the backend (CLI, not part of submit)
2. **Generate** — creates task JSON (`generates_source`)
3. **Simulate** — each task sets `image: python:3.12-slim`; ScriptHut wraps
   the command in `apptainer exec`
4. **Aggregate** — combines results on the host with system Python
   (`python-booth`)

The simulation uses only Python stdlib (no numpy) — a minimal,
self-contained image is enough.

## Quick Start

1. Register this repo as a git source in your **user-global**
   `~/.config/scripthut/scripthut.yaml` (once for all examples):

```yaml
sources:
  - name: scripthut-examples
    type: git
    url: git@github.com:thomaswiemann/scripthut-examples.git
    branch: main
```

2. Pull the image once per cluster (submitting never pulls):

```bash
scripthut image ensure python:3.12-slim --backend mercury
```

3. Sync and submit:

```bash
scripthut source sync scripthut-examples
scripthut workflow run apptainer_python.json \
  --source scripthut-examples --backend mercury
```

The `python-booth` env group (generator + aggregator) is defined in this
repo’s `scripthut.yaml`. Simulation tasks do not include it — the image
provides Python.

## Files

| File | Description |
|------|-------------|
| `.hut/workflows/apptainer_python.json` | Entry point — launches the generator task |
| `generate_tasks.py` | Creates task JSON with `image:` on each sim task |
| `simulate.py` | Random walk simulation (stdlib only, runs in the image) |
| `aggregate.py` | Combines results (runs outside the image) |

## How Containerization Works

- Image URI: `python:3.12-slim` (Docker Hub). ScriptHut pulls it to the
  backend’s `image_dir` (default `~/scripthut-images/`) as a `.sif`.
- Each simulation task names that URI in `image:`. ScriptHut wraps
  `command` in `apptainer exec`; do not put `apptainer` in the command.
- Pulling is a separate step (`scripthut image ensure`). A missing image
  fails at submit and names the ensure command to run.
- Aggregation stays on the host (`python-booth`) to show mixed
  container / bare-node tasks in one DAG.

## Resource Usage

- **Generator:** 1 CPU, 2G memory
- **Per sim task:** 1 CPU, 2G memory, ~30–60s
- **Total:** ~0.05 CPU-hours for 5 tasks + aggregation

## ScriptHut Features Demonstrated

- **`image:`** — Slurm tasks run inside a container via Apptainer
- **`scripthut image ensure`** — one-time pull, separate from submit
- **`generates_source`** — dynamic task generation on compute nodes
- **Wildcard dependencies** — `sim.*` waits for all simulation tasks
- **`.` grouping** — task IDs `sim.0`..`sim.4` in a collapsible group
- **Mixed execution** — sim tasks use the image; aggregator uses `python-booth`
