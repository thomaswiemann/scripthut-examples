# R Simulation Example

A fan-out/fan-in simulation pipeline for testing ScriptHut on a Slurm cluster.

**What it does:** Runs N parallel simulations (drawing from a bivariate normal), then aggregates the results once all simulations complete.

**How it works:** Uses ScriptHut's **endogenous workflow** pattern — a static `.hut/workflows/r_simulation.json` defines a single generator task that runs on a compute node and produces the full task list. Nothing runs on the head node except scheduler commands and file reads.

```
.hut/workflows/r_simulation.json
  └── generate (runs on compute node, writes task JSON)
        ├── sim.0 ──┐
        ├── sim.1 ──┤
        ├── sim.2 ──┼──▶ aggregate
        ├── sim.3 ──┤
        └── sim.4 ──┘
```

## Files

| File | Purpose |
|---|---|
| `.hut/workflows/r_simulation.json` | Entry point — single generator task with `generates_source` |
| `generate_tasks.py` | Runs on compute node — produces the simulation task JSON |
| `gen_results.R` | Single simulation draw (runs N times in parallel) |
| `agg_results.R` | Aggregates all results into `results.csv` |

## Quick Start

### 1. Register the git source (once)

In your user-global `~/.config/scripthut/scripthut.yaml`:

```yaml
sources:
  - name: scripthut-examples
    type: git
    url: git@github.com:thomaswiemann/scripthut-examples.git
    branch: main
```

### 2. Env groups

`r-453` and `python-booth` are defined in this repo’s `scripthut.yaml`. The generator uses `python-booth`; simulation and aggregate tasks use `r-453`.

### 3. Sync and run

```bash
scripthut source sync scripthut-examples
scripthut workflow run r_simulation.json --source scripthut-examples --backend mercury
```

ScriptHut will:

1. Discover `.hut/workflows/r_simulation.json` from the git source
2. Clone the repo on the backend and submit the generator via `sbatch`
3. When it completes, read the generated JSON and append `sim.*` + `aggregate` tasks
4. Submit simulations, then aggregate when all sims finish

All logs go to `.scripthut/` inside the git clone.

## Customizing

Edit `.hut/workflows/r_simulation.json` to change the `--count`, `--partition`, or `--working-dir` flags passed to `generate_tasks.py`.

```bash
# Preview what the generator produces locally
python generate_tasks.py --count 3

# Write to a file (like the generator task does on the cluster)
python generate_tasks.py --count 10 --output /tmp/tasks.json
```

## ScriptHut Features Demonstrated

- **`generates_source`** — dynamic task generation on compute nodes
- **Wildcard dependencies** — `sim.*` waits for all simulation tasks
- **`.` grouping** — task IDs `sim.0`..`sim.9` appear as a collapsible group in the UI
- **Named env groups** — generator includes `python-booth`, simulations include `r-453`

## Testing Locally (without Slurm)

```bash
cd r_simulation
mkdir -p temp
Rscript --vanilla gen_results.R 0 temp
Rscript --vanilla gen_results.R 1 temp
Rscript --vanilla gen_results.R 2 temp
Rscript --vanilla agg_results.R temp
cat results.csv
```
