# R Simulation Example

A fan-out/fan-in simulation pipeline for testing ScriptHut on a Slurm cluster.

**What it does:** Runs N parallel simulations (drawing from a bivariate normal), then aggregates the results once all simulations complete.

**How it works:** Uses ScriptHut's **endogenous workflow** pattern — a static `r_simulation.json` defines a single generator task that runs on a compute node and produces the full task list. Nothing runs on the head node except `cat` and `sbatch`.

```
r_simulation.json
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
| `r_simulation.json` | Entry point — single generator task with `generates_source` |
| `generate_tasks.py` | Runs on compute node — produces the simulation task JSON |
| `gen_results.R` | Single simulation draw (runs N times in parallel) |
| `agg_results.R` | Aggregates all results into `results.csv` |

## Quick Start

### 1. Clone to your cluster

```bash
git clone git@github.com:thomaswiemann/scripthut-examples.git ~/Projects/scripthut-examples
```

### 2. Add project to `scripthut.yaml`

```yaml
projects:
  - name: scripthut-examples
    backend: mercury
    path: ~/Projects/scripthut-examples
```

### 3. Make sure the `R` and `python` environments are configured

```yaml
environments:
  - name: R
    extra_init: "module load R/4.5"           # adjust to your cluster
  - name: python
    extra_init: "module load python/3.12"      # adjust to your cluster
```

The generator task uses `python`, and the simulation tasks use `R`.

### 4. Start ScriptHut and run

```bash
scripthut
```

Open http://localhost:8000. You'll see `r_simulation` discovered automatically — click **Run** to submit.

ScriptHut will:
1. Read `r_simulation.json` (via `cat` on head node)
2. Submit the generator task via `sbatch`
3. When it completes, read the generated JSON and append `sim.*` + `aggregate` tasks to the run
4. Submit simulations, then aggregate when all sims finish

All logs go to `.scripthut/` inside the git repo.

## Customizing

Edit `r_simulation.json` to change the `--count`, `--partition`, or `--working-dir` flags passed to `generate_tasks.py`.

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
- **Named environments** — generator uses `python`, simulations use `R`

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
