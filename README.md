# ScriptHut Examples

Example workflows for [ScriptHut](https://github.com/tlamadon/scripthut) 0.12+.

Each example is a self-contained directory of scripts. Workflow entry points live in `.hut/workflows/*.json` (ScriptHut’s default discovery glob). A combined workflow (`.hut/workflows/all.json`) runs every generator together with prefixed task IDs.

## Examples

| Example | Language | Workflow file | Description |
|---|---|---|---|
| [bash_simulation](bash_simulation/) | Bash | `bash_diamond.json` | Static diamond DAG (no generator) |
| [r_simulation](r_simulation/) | R | `r_simulation.json` | Monte Carlo regression (OLS, Ridge, Lasso) |
| [python_simulation](python_simulation/) | Python | `python_simulation.json` | Monte Carlo option pricing (Black-Scholes) |
| [julia_simulation](julia_simulation/) | Julia | `julia_simulation.json` | Bootstrap OLS regression |
| [apptainer_python](apptainer_python/) | Python + Apptainer | `apptainer_python.json` | Containerized random walk simulation |
| [data_staging](data_staging/) | Python | `data_staging.json` | Stage a local dataset onto the backend, then fan out over it |

`data_staging` additionally needs a one-time `datasets:` entry in your user-global config, because it starts from a directory on your machine rather than generating its data on the cluster. See its [README](data_staging/README.md).

All compute examples (except the bash diamond) use the same **fan-out/fan-in** pattern:

1. A **generator task** runs on a compute node and produces a task JSON (`generates_source`)
2. **N parallel tasks** run the simulation/compute (grouped via `.` separator)
3. An **aggregation task** collects results (depends on all parallel tasks via `*` wildcard)

### ScriptHut Features Demonstrated

- **Endogenous workflows** — `generates_source` lets a task produce the workflow dynamically
- **Wildcard dependencies** — `sim.*`, `pricing.*`, `bootstrap.*` fan-in patterns
- **Task grouping** — dot-separated IDs (`sim.0`, `sim.1`) for collapsible UI groups
- **Environment configuration** — `env_groups` (`r-453`, `python-booth`, `julia-112`) for module loading
- **Containerized tasks** — Apptainer example runs simulations inside a Docker-pulled container
- **Combined runs** — `all.json` uses `--prefix` to namespace task IDs across examples
- **Data staging** — `data:` copies a local directory onto the backend on first use (under its `dataset_dir`, `~/scripthut-data` by default), keyed by a content hash so later runs reuse it

## Usage

Module-load groups live in this repo’s [`scripthut.yaml`](scripthut.yaml). ScriptHut overlays them when the source is run — do not copy them into your user-global config.

1. Add a **git source** to your user-global config (`~/.config/scripthut/scripthut.yaml`):

```yaml
sources:
  - name: scripthut-examples
    type: git
    url: git@github.com:thomaswiemann/scripthut-examples.git
    branch: main
```

The default `workflows_glob` (`.hut/workflows/*.json`) matches this repo. Pick the backend at run time (`--backend mercury`).

2. Sync and list discovered workflows:

```bash
scripthut source sync scripthut-examples
scripthut source view scripthut-examples
```

3. Submit a workflow:

```bash
scripthut workflow run bash_diamond.json --source scripthut-examples --backend mercury
scripthut workflow run python_simulation.json --source scripthut-examples --backend mercury
```

Until these files are on `origin/main`, either push a branch and set `branch:` to it, or clone the repo on the cluster and use a `type: path` source.

## Task ID Prefixes

When running examples individually, task IDs are unprefixed (e.g., `sim.0`, `aggregate`). When running all examples together via `all.json`, each generator receives a `--prefix` flag to avoid ID collisions:

| Example | Prefix | Task IDs |
|---|---|---|
| R simulation | `r.` | `r.sim.0`, `r.aggregate` |
| Python simulation | `py.` | `py.pricing.0`, `py.aggregate` |
| Julia simulation | `jl.` | `jl.bootstrap.0`, `jl.aggregate` |
| Apptainer | `apt.` | `apt.sim.0`, `apt.aggregate` |

## Project Structure

ScriptHut discovers `.hut/workflows/*.json` from the git source. Runtime artifacts stay inside `.scripthut/` at the repository root (gitignored).

```
scripthut-examples/
├── scripthut.yaml          ← project-local env_groups (no backends)
├── .hut/workflows/         ← discovered entry points
│   ├── all.json
│   ├── bash_diamond.json
│   ├── python_simulation.json
│   ├── r_simulation.json
│   ├── julia_simulation.json
│   ├── apptainer_python.json
│   └── data_staging.json
├── .scripthut/             ← runtime artifacts (not tracked)
├── bash_simulation/
├── r_simulation/
├── python_simulation/
├── julia_simulation/
├── apptainer_python/
└── data_staging/           ← includes sample_data/ (committed, 1.4 KB)
```
