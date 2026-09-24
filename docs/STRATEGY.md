# Strategy notes — Gemma 4 Developer Agent

This document captures a practical roadmap for improving the baseline in `submission/`. It is not prescriptive; the hidden test set rewards **reliable patching**, not prompt length.

## Evaluation objective

- **Metric:** fraction of instances where your submitted patch passes the issue’s verification tests (SWE-Bench-style pass/fail).
- **Budget:** 12 hours total for all tasks in a run (sandbox setup counts; validation time does not).
- **Output:** `submit_patch()` → unified `git diff` against the task baseline in `/workspace`.

Optimize for **first-patch pass rate** under the time cap, not perfect analysis prose.

## Graph-first localization

The dataset ships AST call graphs and 256-d embeddings per symbol. On multi-thousand-line repos, linear search wastes turns.

Suggested loop (also encoded in `prompts/system.md`):

1. `search_similar_code` with 2–4 query variants (error text, API names, stack symbols).
2. `get_code_subgraph` on the top 3–8 nodes to see call chains.
3. `get_code_neighbors` with `edge_type: calls` to expand one hop at a time.
4. `read_file` with tight line ranges on nodes that appear in both semantic hits and graph paths.

Ablate: disable graph tools in a forked config and measure turn count / timeout rate on 10 training tasks.

## Sub-agent: `code_analyzer`

The optional read-only analyzer (`sub_agents/code_analyzer.yaml`) trades extra model calls for better localization when the root agent loops.

- Use when the root agent has run ≥3 tool rounds without a failing test repro.
- Keep analyzer outputs structured (hypothesis / evidence / plan / verify).
- Consider lowering `max_output_tokens` in a separate `configs/sampling_analyzer.yaml` if traces balloon.

## Skills

`skills/repo_navigation` demonstrates the ADK skill layout (`SKILL.md`, `scripts/`, `resources/`).

Ideas for additional skills (not included by default):

- `pytest_focus` — scripts that map failing tests to modules via `git grep` / `pytest --collect-only`.
- `dependency_wheels` — notes on offline `pip` using `/wheels` from the dataset.

## Fine-tuning and LoRA

Competition rules allow multiple LoRA adapters under `submission/adapters/<name>/`:

- **main_lora** on the root coder agent for tool-use and patch formatting.
- **tool_lora** on read-only sub-agents for retrieval-heavy behavior.

Train on the public `tasks.jsonl` trajectories you collect from harness runs (tool traces + successful patches). Do not commit weights to git; add them locally before `make pack`.

## `eval_config.yaml`

Tune `per_task_timeout_seconds` and `max_turns_per_task` after profiling on the training split. Aggressive timeouts free budget for hard tasks but increase `NO_PATCH` submissions.

Align keys with **HARNESS_README.md** when the dataset schema differs from this starter.

## Checklist before upload

- [ ] `model: gemma-4-31b-it-qat-w4a16-ct` on every agent YAML.
- [ ] `make verify` passes (`agent.yaml` at zip root).
- [ ] No path traversal in skill scripts; they run in the competition container.
- [ ] Adapters are real safetensors + config, not placeholders.
- [ ] Prompts fit within compaction limits (monitor `get_status()`).
