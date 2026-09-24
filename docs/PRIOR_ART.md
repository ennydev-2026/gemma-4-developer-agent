# Prior-art boundary

TRUST-SWE does not claim novelty for code graphs, explicit hypotheses,
trajectory memory, dynamic debugging, or adaptive budgets in isolation.

Relevant comparisons:

- [LocAgent](https://aclanthology.org/2025.acl-long.426/) — graph-guided
  multi-hop code localization.
- [RepoGraph](https://arxiv.org/abs/2410.14684) — repository graph augmentation
  for multiple SWE frameworks.
- [CogniGent](https://arxiv.org/abs/2601.12522) — multiple root-cause
  hypotheses, causal reasoning, call-graph traversal, and confidence pruning.
- [InspectCoder](https://arxiv.org/abs/2510.18327) — active dynamic analysis
  and inspector/coder agents.
- [SWE-MeM](https://arxiv.org/abs/2606.28434) — learned adaptive memory
  management for long-horizon coding agents.
- [SWE-Pruner](https://arxiv.org/abs/2601.16746) — adaptive context pruning.
- [SWE-Replay](https://arxiv.org/abs/2601.22129) — efficient test-time scaling.

The testable contribution proposed here is **reliability-aware routing among
imperfect code sensors under a fixed local-agent budget**:

1. identify observable silent-failure signals for each tool;
2. calibrate trust from trace outcomes;
3. switch between exact, lexical, graph, and runtime evidence;
4. optimize held-out resolution per unit of inference cost.

This remains a research hypothesis, not an established novelty claim. A paper
must conduct a broader literature review and demonstrate the distinction with
controlled ablations.
