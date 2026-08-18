# ScriptHut Examples — agent instructions

## Overview

This repository contains example workflows for [ScriptHut](https://github.com/thomaswiemann/scripthut) 0.12+. Each subdirectory holds the scripts for one example. Workflow entry points live in `.hut/workflows/<name>.json` (ScriptHut’s default discovery glob). `.hut/workflows/all.json` runs every generator together with prefixed task IDs.

## Examples

| Directory | Language | Workflow file | Theme | Env group |
|-----------|----------|---------------|-------|-----------|
| `bash_simulation/` | Bash | `bash_diamond.json` | Static diamond DAG | (none) |
| `r_simulation/` | R | `r_simulation.json` | Monte Carlo regression (OLS, Ridge, Lasso) | `r-453` (sims); `python-booth` (generator) |
| `python_simulation/` | Python | `python_simulation.json` | Monte Carlo option pricing (Black-Scholes) | `python-booth` |
| `julia_simulation/` | Julia | `julia_simulation.json` | Bootstrap OLS regression | `julia-112` (compute); `python-booth` (generator) |
| `apptainer_python/` | Python + Apptainer | `apptainer_python.json` | Containerized random walk simulation | `python-booth` (generator + aggregate) |
| `data_staging/` | Python | `data_staging.json` | Stage a local dataset onto the backend, then pool OLS statistics | `python-booth` |

Env groups are defined in the repo-root `scripthut.yaml` and referenced from task JSON as `"env": [{"include": ["python-booth"]}]`. Do not use the legacy `"environment"` string field.

## Conventions

### Discussions

All design discussions live in `.discussions/` as Markdown files. Before making
non-trivial changes, create a discussion file to document the rationale:

```
.discussions/
  YYYY-MM-DD_topic-slug.md
```

Discussion files should include:
- **Context** — what problem or gap motivates the change
- **Options considered** — alternatives with trade-offs
- **Decision** — what was chosen and why

### Example Structure

Each example lives in its own directory and must contain:
- A matching `.hut/workflows/<name>.json` entry point
- `README.md` — standalone documentation with quick-start instructions
- Source scripts referenced by the workflow

The generate task in a per-example workflow must set `working_dir` to that example directory so commands like `python3 generate_tasks.py` resolve after a git-source clone.

### Task ID Conventions

- Use **`.`** as a group separator: `sim.0`, `pricing.3`, `bootstrap.5`
- The UI groups tasks by the prefix before the last `.` (collapsible sections)
- Use **`*` wildcards** in dependencies: `sim.*`, `pricing.*`, `bootstrap.*`
- Standalone tasks (no group) use a flat name: `aggregate`, `generate`

### General Principles

- Examples should be **self-contained** — no shared code between examples
- Examples should demonstrate **real compute load** so users can see ScriptHut managing actual work
- All runtime artifacts go in `.scripthut/` (gitignored)
- Use `generates_source` for dynamic task generation (endogenous workflows)
- Keep resource usage modest: **1 CPU, 1G memory, ≤5 min** per task
- Named runtimes are `env_groups` in `scripthut.yaml`, included from task `env:` — never `environment:` / `env_vars:`

### Data staging

`data_staging/` is the one example that consumes data instead of generating it.
Points worth preserving if it is edited:

- It is **excluded from `all.json`** on purpose. `data:` is a top-level workflow
  key, so folding it in would make every example unrunnable for anyone who has
  not configured the dataset.
- The dataset is declared **user-global** (`datasets:` is rejected in a
  project `scripthut.yaml`), so the README must keep telling users to edit
  `path` for their own clone.
- Where data lands is per-cluster: the backend's `dataset_dir`, defaulting to
  `~/scripthut-data` like `clone_dir`. The example runs with no extra config;
  the README points at scratch only as the advice for larger data.
- `$DATA_<NAME>` is set for every dataset (here `$DATA_EXAMPLE_PANEL`);
  `$DATA_DIR` is the conditional one, set only when the workflow uses exactly
  one dataset. These are deliberately not `SCRIPTHUT_`-prefixed: that namespace
  cannot be set by env rules and is stripped from cache keys.
- `sample_data/` stays small. It is committed only so the example runs straight
  after a clone.
