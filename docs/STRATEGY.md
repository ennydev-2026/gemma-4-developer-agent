# TRUST-SWE strategy

TRUST-SWE stands for **Tool-Reliability and Uncertainty-aware Search &
Testing**. Its central claim is narrower than "graphs help coding agents":

> Under a fixed inference budget, a local SWE agent resolves more issues when
> it estimates tool reliability from observable evidence and changes navigation
> mode instead of trusting empty, noisy, or incomplete retrieval.

The competition score remains binary test resolution. Reliability reasoning is
useful only if it improves held-out resolution rate or preserves it at lower
cost.

## Why this formulation

Graph-guided localization, hypothesis testing, ledgers, and adaptive budgets
already exist independently. The competition also exposes graph tools directly.
The open question is how a small local model should act when those tools are
imperfect.

The public harness analysis reports failure modes worth reproducing against the
downloaded official version:

- `search_similar_code` resolves a code symbol before using its stored vector;
- natural-language queries can return an empty result silently;
- graph coverage may omit relevant definitions, including async code;
- missing or damaged graph/embedding artifacts can yield empty or noisy output.

These observations are hypotheses until verified against the exact package
version used for an experiment.

## Policy implemented in the starter

The root prompt keeps a compact in-context state:

- exact issue anchors;
- up to three candidate locations;
- leading and alternative causes;
- trust for graph, lexical, and runtime evidence;
- low-information actions that must not be repeated;
- the next discriminating probe.

It chooses among four modes:

1. **Exact:** issue-supplied paths, symbols, errors, or flags.
2. **Lexical:** targeted grep and bounded file reads.
3. **Graph:** exact symbol lookup followed by one-hop expansion.
4. **Runtime:** minimal reproduction or focused test.

Two low-information actions force a mode change. Exact source and targeted
runtime evidence override graph ranking.

## Analyzer escalation

`code_analyzer` is read-only and deliberately lacks shell and editing tools. It
is useful only when:

- exact and lexical/graph localization still leave 2–5 candidates;
- no candidate has high confidence;
- enough budget remains to use its answer.

The analyzer returns ranked targets, graph trust, a contradiction, and one next
probe. `skip_summarization: true` prevents exploration traces from consuming
root context.

## Evaluation protocol

Use both:

- leave-one-repository-out folds;
- chronological development/validation splits inside each repository.

Never evaluate a task after its reference patch or oracle-derived trajectory
was used for training.

Minimum comparison:

| Variant | Purpose |
| --- | --- |
| lexical-only | establishes performance without graph tools |
| graph-first | measures unconditional graph dependence |
| trust-prompt | current reliability-aware prompt, no adapter |
| trust-router-lora | learned mode/tool choice |
| trust-full | router plus conditional analyzer |

Report:

- resolution rate and confidence interval;
- localization Recall@5 where gold locations are available;
- mean/p90 agent seconds, tool calls, and turns;
- empty-patch, budget, loop, and regression failures;
- recovery rate after an empty/noisy graph result;
- results by repository and task category.

Do not promote a component because of aggregate training performance. Require a
gain in multiple held-out folds without exhausting the 12-hour budget.

## Adapter plan

Collect real harness trajectories first. Build examples for:

- graph useful;
- graph unavailable or misleading;
- exact symbol absent;
- lexical fallback successful;
- runtime probe discriminating two causes;
- premature editing and repeated-action failures.

Training order:

1. SFT for compact evidence-state updates and next-mode selection.
2. Preference tuning between informative and wasteful next actions.
3. SFT for end-to-end repair after routing behavior is stable.
4. RL only if sparse pass/fail reward improves held-out tasks consistently.

Store real PEFT artifacts in `submission/adapters/<name>/` only for packaging.
Never commit model weights or placeholder adapter files.

## Budget policy

`eval_config.yaml` starts with six minutes, 40 tools, and 80 turns per task.
These are safe initial constraints, not established optima. Tune from
target-model traces and account for evaluator concurrency before changing them.

Within a task:

- check status at phase changes;
- avoid full-suite tests;
- stop exploring when fewer than five calls or roughly one minute remain;
- submit the best evidence-backed patch rather than timing out with no diff.

## Prior-art boundary

The paper must compare directly with LocAgent/RepoGraph for graph navigation,
CogniGent for graph-guided hypotheses, InspectCoder for active diagnosis, and
budget/context systems such as EET or SWE-MeM. The proposed contribution is not
any one component; it is calibrated routing between imperfect tools under a
hard local-agent budget.

## Submission checklist

- [ ] Official compiler validates every YAML and include.
- [ ] Every agent uses `gemma-4-31b-it-qat-w4a16-ct`.
- [ ] `evaluation:` keys match the downloaded harness version.
- [ ] Symbol-only graph queries and lexical fallbacks are present.
- [ ] Analyzer remains read-only and conditionally invoked.
- [ ] `make verify` places `agent.yaml` at zip root and omits `.gitkeep`.
- [ ] Included adapters contain real config and safetensors files.
- [ ] Held-out ablations support every claimed improvement.
