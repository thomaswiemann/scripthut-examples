# ScriptHut Examples

Example workflows for [ScriptHut](https://github.com/thomaswiemann/scripthut).

Each subdirectory contains a self-contained workflow with a `sflow.json` entry point.

## Examples

| Example | Description |
|---|---|
| [r_simulation](r_simulation/) | Monte Carlo regression simulation comparing OLS, Ridge, and Lasso |

## Usage

1. Clone this repo to your cluster:

```bash
git clone git@github.com:thomaswiemann/scripthut-examples.git ~/scripthut-examples
```

2. Add a project to your `scripthut.yaml`:

```yaml
projects:
  - name: scripthut-examples
    cluster: my-cluster
    path: ~/scripthut-examples
    max_concurrent: 3
    description: "Example ScriptHut workflows"
```

3. Start ScriptHut — all `sflow.json` files are discovered automatically!

## Project Structure

ScriptHut is **git-aware** — workflows are discovered via `git ls-files` and all runtime artifacts stay inside `.scripthut/` at the repository root. This directory is gitignored.

```
scripthut-examples/
├── .gitignore              ← ignores .scripthut/
├── .scripthut/             ← runtime artifacts (not tracked)
│   └── r_simulation/
│       └── logs/
├── r_simulation/
│   ├── sflow.json          ← entry point (auto-discovered)
│   ├── generate_tasks.py   ← task generator
│   ├── gen_results.R
│   └── agg_results.R
└── ...
```
