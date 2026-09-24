---
name: repo_navigation
description: >-
  Repository navigation helpers for SWE-Bench-style tasks — quick tree summaries,
  git context, and notes on graph tool usage.
---

# repo_navigation

Use this skill when you need a fast mental model of an unfamiliar repository.

## When to use

- At the start of a task, before deep reading.
- After `search_similar_code` returns many candidates and you need to prioritize files.
- When graph neighbor lists are long and you want a human-readable map.

## Resources

- `resources/graph_tools.md` — cheat sheet for `get_code_neighbors` / `get_code_subgraph`.
- `resources/workflow.md` — recommended navigation loop.

Load with `load_skill_resource` (path relative to this skill directory).

## Scripts

- `scripts/repo_overview.sh` — prints top-level layout, git status, and recent commits.

Run with `run_skill_script` (arguments are passed to the script).
