# Julia Bootstrap Regression

A ScriptHut example demonstrating parallel bootstrap estimation in Julia.

## What It Does

Estimates bootstrap confidence intervals for OLS regression coefficients:

1. **Generate** — Creates N parallel bootstrap tasks + one aggregation task
2. **Bootstrap** — Each task resamples a simulated dataset (500K × 50) and fits OLS
3. **Aggregate** — Computes bootstrap confidence intervals (percentile method)

Uses only Julia stdlib — no package installation required.

## Quick Start

1. Register this repo as a git source in your **user-global** `~/.config/scripthut/scripthut.yaml` (once for all examples):

```yaml
sources:
  - name: scripthut-examples
    type: git
    url: git@github.com:thomaswiemann/scripthut-examples.git
    branch: main
```

2. Env groups `python-booth` (generator) and `julia-112` (compute) live in this repo’s `scripthut.yaml`.

3. Sync and submit:

```bash
scripthut source sync scripthut-examples
scripthut workflow run julia_simulation.json --source scripthut-examples --backend mercury
```

## Files

| File | Description |
|------|-------------|
| `.hut/workflows/julia_simulation.json` | Entry point — launches the generator task |
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
- **Mixed env groups** — generator includes `python-booth`, compute includes `julia-112`
