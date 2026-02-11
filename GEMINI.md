# ScriptHut Examples — Development Guide

## Overview

This repository contains example workflows for [ScriptHut](https://github.com/thomaswiemann/scripthut). Each subdirectory is a self-contained example with its own `sflow.json` entry point.

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

### General Principles

- Examples should be **self-contained** — no shared code between examples
- Examples should demonstrate **real compute load** so users can see ScriptHut managing actual work
- All runtime artifacts go in `.scripthut/` (gitignored)
- Use `generates_source` for dynamic task generation (endogenous workflows)
