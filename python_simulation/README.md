# Python Monte Carlo Option Pricing

A ScriptHut example demonstrating parallel Monte Carlo simulation in Python.

## What It Does

Prices a European call option using Monte Carlo simulation of geometric Brownian motion (GBM):

1. **Generate** — Creates N parallel pricing tasks + one aggregation task
2. **Price** — Each task simulates 500K GBM paths and estimates the option price
3. **Aggregate** — Combines all estimates with proper standard error calculation

## Quick Start

1. Register this repo as a git source in your **user-global** `~/.config/scripthut/scripthut.yaml` (once for all examples):

```yaml
sources:
  - name: scripthut-examples
    type: git
    url: git@github.com:thomaswiemann/scripthut-examples.git
    branch: main
```

2. The `python-booth` env group is defined in this repo’s `scripthut.yaml` (`module load python/booth/3.12`). ScriptHut overlays it when the source runs.

3. Sync and submit:

```bash
scripthut source sync scripthut-examples
scripthut workflow run python_simulation.json --source scripthut-examples --backend mercury
```

## Files

| File | Description |
|------|-------------|
| `.hut/workflows/python_simulation.json` | Entry point — launches the generator task |
| `generate_tasks.py` | Creates task JSON with fan-out/fan-in pattern |
| `price_option.py` | Monte Carlo GBM simulation (numpy) |
| `aggregate.py` | Combines estimates, computes mean and SE |

## Resource Usage

- **Per task:** 1 CPU, 1G memory, ~30–60s
- **Total:** ~0.15 CPU-hours for 10 tasks + aggregation

## ScriptHut Features Demonstrated

- **`generates_source`** — dynamic task generation on compute nodes
- **Wildcard dependencies** — `pricing.*` waits for all pricing tasks
- **`.` grouping** — task IDs `pricing.0`..`pricing.9` appear as a collapsible group in the UI
- **Named env groups** — tasks `include` `python-booth` for module loading
