# TRUST-SWE adapter data

This directory defines the data contract for future LoRA training. It contains
no model weights and does not download Gemma.

## Unit of supervision

One record represents the state immediately before a tool decision:

- issue anchors and remaining budget;
- at most three candidate symbols/files;
- evidence supporting and contradicting the leader;
- observed reliability of graph, lexical, and runtime sensors;
- previous low-information actions;
- chosen next mode/tool;
- eventual localization and task outcome.

`trajectory.schema.json` validates the normalized record.

## Labels

Derive labels from observable traces:

- `informative`: the action removed a candidate, produced a reproduction, or
  located a gold-touched symbol;
- `redundant`: equivalent evidence was already present;
- `misleading`: the action strengthened an incorrect location;
- `failed_sensor`: empty/error/noisy result required a fallback;
- `terminal`: patch submission or justified decline.

Do not train on hidden test names or reference-patch text. Reference patches may
label touched locations for training tasks, but oracle content must not enter
model inputs or targets.

## Training sequence

1. SFT on successful state → next-action examples.
2. Preference pairs: informative action over redundant/misleading action from
   the same state.
3. End-to-end successful trajectories after routing metrics stabilize.
4. Optional RL using pass/fail plus bounded penalties for repeated actions and
   empty patches.

Keep adapter artifacts outside Git. Copy a completed PEFT directory into
`submission/adapters/<name>/` only when building a real submission.
