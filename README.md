# ScriptHut Examples

Example workflows for [ScriptHut](https://github.com/thomaswiemann/scripthut).

Each subdirectory contains a self-contained workflow with a `sflow.json` entry point. A root-level `sflow.json` runs all examples together.

## Examples

| Example | Language | Description |
|---|---|---|
| [r_simulation](r_simulation/) | R | Monte Carlo regression (OLS, Ridge, Lasso) |
| [python_simulation](python_simulation/) | Python | Monte Carlo option pricing (Black-Scholes) |
| [julia_simulation](julia_simulation/) | Julia | Bootstrap OLS regression |
| [apptainer_python](apptainer_python/) | Python + Apptainer | Containerized random walk simulation |

All examples use the same **fan-out/fan-in** pattern:
1. A **generator task** runs on a compute node and produces a task JSON (`generates_source`)
2. **N parallel tasks** run the simulation/compute (grouped via `.` separator)
3. An **aggregation task** collects results (depends on all parallel tasks via `*` wildcard)

### ScriptHut Features Demonstrated

- **Endogenous workflows** — `generates_source` lets a task produce the workflow dynamically
- **Wildcard dependencies** — `sim.*`, `pricing.*`, `bootstrap.*` fan-in patterns
- **Task grouping** — dot-separated IDs (`sim.0`, `sim.1`) for collapsible UI groups
- **Environment configuration** — `r-451`, `python-booth`, `julia-112` for module loading
- **Containerized tasks** — Apptainer example runs simulations inside a Docker-pulled container
- **Combined runs** — master `sflow.json` uses `--prefix` to namespace task IDs across examples

## Usage

1. Clone this repo to your cluster:

```bash
git clone git@github.com:thomaswiemann/scripthut-examples.git ~/scripthut-examples
```

2. Add a project to your `scripthut.yaml`:

```yaml
projects:
  - name: scripthut-examples
    backend: mercury
    path: ~/Projects/scripthut-examples
    description: "Example ScriptHut workflows"
```

3. Make sure environments are configured:

```yaml
environments:
  - name: python-booth
    extra_init: "module load python/booth/3.12"
  - name: r-451
    extra_init: "module load R/4.5/4.5.1"
  - name: julia-112
    extra_init: "module load julia/1.12"
```

4. Start ScriptHut — all `sflow.json` files are discovered automatically!

## Task ID Prefixes

When running examples individually, task IDs are unprefixed (e.g., `sim.0`, `aggregate`). When running all examples together via the master `sflow.json`, each generator receives a `--prefix` flag to avoid ID collisions:

| Example | Prefix | Task IDs |
|---|---|---|
| R simulation | `r.` | `r.sim.0`, `r.aggregate` |
| Python simulation | `py.` | `py.pricing.0`, `py.aggregate` |
| Julia simulation | `jl.` | `jl.bootstrap.0`, `jl.aggregate` |
| Apptainer | `apt.` | `apt.sim.0`, `apt.aggregate` |

## Project Structure

ScriptHut is **git-aware** — workflows are discovered via `git ls-files` and all runtime artifacts stay inside `.scripthut/` at the repository root. This directory is gitignored.

```
scripthut-examples/
├── sflow.json              ← master: runs all examples
├── .gitignore              ← ignores .scripthut/
├── .scripthut/             ← runtime artifacts (not tracked)
├── r_simulation/
│   ├── sflow.json          ← entry point (auto-discovered)
│   ├── generate_tasks.py
│   ├── gen_results.R
│   └── agg_results.R
├── python_simulation/
│   ├── sflow.json
│   ├── generate_tasks.py
│   ├── price_option.py
│   └── aggregate.py
├── julia_simulation/
│   ├── sflow.json
│   ├── generate_tasks.py
│   ├── bootstrap.jl
│   └── aggregate.jl
└── apptainer_python/
    ├── sflow.json
    ├── generate_tasks.py
    ├── simulate.py
    └── aggregate.py
```
