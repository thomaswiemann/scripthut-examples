# Julia Bootstrap Regression

A ScriptHut example demonstrating parallel bootstrap estimation in Julia.

## What It Does

Estimates bootstrap confidence intervals for OLS regression coefficients:

1. **Generate** — Creates N parallel bootstrap tasks + one aggregation task
2. **Bootstrap** — Each task resamples a simulated dataset (500K × 50) and fits OLS
3. **Aggregate** — Computes bootstrap confidence intervals (percentile method)

Uses only Julia stdlib — no package installation required.

## Quick Start

1. Add this workflow to your `scripthut.yaml`:

```yaml
workflows:
  - name: julia-bootstrap
    backend: mercury
    command: "cat ~/Projects/scripthut-examples/julia_simulation/sflow.json"
```

2. Make sure the environments are configured:

```yaml
environments:
  - name: python-booth
    extra_init: "module load python/booth/3.12"
  - name: julia-112
    extra_init: "module load julia/1.12"
```

3. Launch the workflow from the ScriptHut UI.

## Files

| File | Description |
|------|-------------|
| `sflow.json` | Entry point — launches the generator task |
| `generate_tasks.py` | Creates task JSON with fan-out/fan-in pattern |
| `bootstrap.jl` | Bootstrap OLS on simulated data (stdlib only) |
| `aggregate.jl` | Computes 95% CIs via percentile method |

## Resource Usage

- **Per task:** 1 CPU, 1G memory, ~30–60s
- **Total:** ~0.15 CPU-hours for 10 tasks + aggregation

## ScriptHut Features Demonstrated

- **`generates_source`** — dynamic task generation on compute nodes
- **Wildcard dependencies** — `bootstrap.*` waits for all bootstrap tasks
- **`.` grouping** — task IDs `bootstrap.0`..`bootstrap.9` appear as a collapsible group
- **Mixed environments** — generator uses `python-booth`, compute uses `julia-112`
