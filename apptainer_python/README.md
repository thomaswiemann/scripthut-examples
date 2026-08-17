# Apptainer Containerized Simulation

A ScriptHut example demonstrating containerized workflows using Apptainer (Singularity).

## What It Does

Runs a random walk simulation inside a Python container:

1. **Generate** — Pulls the container image (cached) and creates task JSON
2. **Simulate** — Each task runs inside `python:3.12-slim` container via `apptainer exec`
3. **Aggregate** — Combines results (runs outside the container with system Python)

The simulation uses only Python stdlib (no numpy) — demonstrating that the
container is a minimal, self-contained environment.

## Quick Start

1. Register this repo as a git source in your **user-global** `~/.config/scripthut/scripthut.yaml` (once for all examples):

```yaml
sources:
  - name: scripthut-examples
    type: git
    url: git@github.com:thomaswiemann/scripthut-examples.git
    branch: main
```

2. The `python-booth` env group (generator + aggregator) is defined in this repo’s `scripthut.yaml`. Simulation tasks do not include it — the container provides Python.

3. Sync and submit:

```bash
scripthut source sync scripthut-examples
scripthut workflow run apptainer_python.json --source scripthut-examples --backend mercury
```

## Files

| File | Description |
|------|-------------|
| `.hut/workflows/apptainer_python.json` | Entry point — launches the generator task |
| `generate_tasks.py` | Pulls container, creates task JSON |
| `simulate.py` | Random walk simulation (stdlib only, runs in container) |
| `aggregate.py` | Combines results (runs outside container) |

## How Containerization Works

The generator task:

1. Pulls `docker://python:3.12-slim` → `~/.cache/scripthut/containers/python312-slim.sif`
2. Caches the `.sif` so subsequent runs skip the pull
3. Generates tasks with `apptainer exec <sif_path> python3 simulate.py ...`

Simulation tasks don't need a ScriptHut env group — the container provides everything.

## Resource Usage

- **Generator:** 1 CPU, 2G memory (container pull needs extra)
- **Per sim task:** 1 CPU, 2G memory, ~30–60s
- **Total:** ~0.05 CPU-hours for 5 tasks + aggregation

## ScriptHut Features Demonstrated

- **`generates_source`** — dynamic task generation on compute nodes
- **Wildcard dependencies** — `sim.*` waits for all simulation tasks
- **`.` grouping** — task IDs `sim.0`..`sim.4` in a collapsible group
- **Mixed execution** — sim tasks use Apptainer, aggregator uses `python-booth`
- **Container caching** — generator pulls once, tasks reuse the cached `.sif`
