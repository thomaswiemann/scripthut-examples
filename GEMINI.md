# ScriptHut Examples — Development Guide

## Overview

This repository contains example workflows for [ScriptHut](https://github.com/thomaswiemann/scripthut). Each subdirectory is a self-contained example with its own `sflow.json` entry point. A root-level `sflow.json` runs all examples together.

## Examples

| Directory | Language | Theme | Environment |
|-----------|----------|-------|-------------|
| `r_simulation/` | R | Monte Carlo regression (OLS, Ridge, Lasso) | `r-451` |
| `python_simulation/` | Python | Monte Carlo option pricing (Black-Scholes) | `python-booth` |
| `julia_simulation/` | Julia | Bootstrap OLS regression | `julia-112` |
| `apptainer_python/` | Python + Apptainer | Containerized random walk simulation | (system) |

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
- `sflow.json` — ScriptHut entry point (auto-discovered)
- `README.md` — standalone documentation with quick-start instructions
- Source scripts referenced by the workflow

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
