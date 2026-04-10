# ScriptHut Examples

Example workflows for [ScriptHut](https://github.com/thomaswiemann/scripthut).

Each subdirectory contains a self-contained workflow JSON alongside its scripts. A root-level `all_examples.json` runs all examples together.

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
- **Environment configuration** — `python`, `R`, `julia` mapped to `module load` in your config
- **Containerized tasks** — Apptainer example runs simulations inside a Docker-pulled container
- **Combined runs** — `all_examples.json` uses `--prefix` to namespace task IDs across examples

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

3. Make sure environments are configured (adapt to your cluster's `module avail`):

```yaml
environments:
  - name: python
    extra_init: "module load python/3.12"   # adjust to your module name
  - name: R
    extra_init: "module load R/4.5"         # e.g., R/4.5/4.5.3
  - name: julia
    extra_init: "module load julia/1.12"
```

4. Start ScriptHut — all workflow JSON files are discovered automatically!

## Task ID Prefixes

When running examples individually, task IDs are unprefixed (e.g., `sim.0`, `aggregate`). When running all examples together via `all_examples.json`, each generator receives a `--prefix` flag to avoid ID collisions:

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
├── all_examples.json               ← runs all examples together
├── .gitignore                      ← ignores .scripthut/
├── .scripthut/                     ← runtime artifacts (not tracked)
├── r_simulation/
│   ├── r_simulation.json           ← workflow (auto-discovered)
│   ├── generate_tasks.py
│   ├── gen_results.R
│   └── agg_results.R
├── python_simulation/
│   ├── python_simulation.json
│   ├── generate_tasks.py
│   ├── price_option.py
│   └── aggregate.py
├── julia_simulation/
│   ├── julia_simulation.json
│   ├── generate_tasks.py
│   ├── bootstrap.jl
│   └── aggregate.jl
├── bash_simulation/
│   ├── bash_diamond.json
│   └── simple_task.sh
└── apptainer_python/
    ├── apptainer_python.json
    ├── generate_tasks.py
    ├── simulate.py
    └── aggregate.py
```
