---
name: repo_navigation
description: >-
  Reliability-aware repository navigation for choosing between exact, lexical,
  graph, and runtime evidence without repeating low-value exploration.
---

# repo_navigation

Use this skill when a target is not obvious or when graph and lexical evidence
disagree. The goal is not to maximize retrieval; it is to identify the smallest
next observation that can eliminate a candidate.

## When to use

- At task start, to extract exact issue anchors.
- When choosing whether graph lookup is trustworthy.
- After two low-information actions in the same navigation mode.
- Before escalating to the read-only analyzer.

## Resources

- `resources/tool_reliability.md` — observable trust and fallback signals.
- `resources/evidence_ledger.md` — compact in-context state contract.
- `resources/graph_tools.md` — graph query constraints and failure modes.
- `resources/workflow.md` — TRUST-SWE navigation loop.

Load with `load_skill_resource` (path relative to this skill directory).

## Scripts

- `scripts/repo_overview.sh` — prints top-level layout, git status, and recent commits.

Run with `run_skill_script` (arguments are passed to the script).
