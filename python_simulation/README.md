# Python Monte Carlo Option Pricing

A ScriptHut example demonstrating parallel Monte Carlo simulation in Python.

## What It Does

Prices a European call option using Monte Carlo simulation of geometric Brownian motion (GBM):

1. **Generate** — Creates N parallel pricing tasks + one aggregation task
2. **Price** — Each task simulates 500K GBM paths and estimates the option price
3. **Aggregate** — Combines all estimates with proper standard error calculation

## Quick Start

1. Add this workflow to your `scripthut.yaml`:

```yaml
workflows:
  - name: python-pricing
    backend: mercury
    command: "cat ~/Projects/scripthut-examples/python_simulation/sflow.json"
    max_concurrent: 3
```

2. Make sure the `python-booth` environment is configured:

```yaml
environments:
  - name: python-booth
    extra_init: "module load python/booth/3.12"
```

3. Launch the workflow from the ScriptHut UI.

## Files

| File | Description |
|------|-------------|
| `sflow.json` | Entry point — launches the generator task |
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
- **Named environments** — tasks reference `python-booth` for module loading
