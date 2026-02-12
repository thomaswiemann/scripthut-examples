# ScriptHut Examples

Example workflows for [ScriptHut](https://github.com/thomaswiemann/scripthut).

Each subdirectory contains a self-contained workflow with a `sflow.json` entry point. A root-level `sflow.json` runs all examples together.

## Examples

| Example | Description |
|---|---|
| [r_simulation](r_simulation/) | Monte Carlo regression simulation comparing OLS, Ridge, and Lasso |
| [python_simulation](python_simulation/) | Monte Carlo option pricing via Black-Scholes simulation |
| [julia_simulation](julia_simulation/) | Bootstrap estimation of OLS regression coefficients |
| [apptainer_python](apptainer_python/) | Containerized random walk simulation using Apptainer |

All examples use the same **fan-out/fan-in** pattern:
1. A **generator task** runs on a compute node and produces a task JSON (`generates_source`)
2. **N parallel tasks** run the simulation/compute (grouped via `.` separator)
3. An **aggregation task** collects results (depends on all parallel tasks via `*` wildcard)

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
    max_concurrent: 3
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
