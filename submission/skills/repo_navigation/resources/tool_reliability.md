# Tool reliability rubric

Assign trust from observable output, not from a tool's name.

| Sensor | High trust | Medium trust | Low trust / fallback |
| --- | --- | --- | --- |
| Exact path | File exists and issue names it | Inferred from module | Missing or unrelated |
| Lexical search | Unique source hit | Several plausible hits | Only tests/generated files or excessive noise |
| Graph | Exact symbol plus source agreement | Plausible one-hop relation | Empty, unrelated, repetitive, or missing relevant async code |
| Runtime | Reproduces requested behavior | Exercises nearby path | Setup failure unrelated to issue |
| Existing test | Fails for expected reason | Covers adjacent behavior | Does not collect or fails during environment setup |

## Switching policy

- Two low-information actions in one mode require a mode switch.
- A failed graph lookup is not evidence against the existence of code.
- A failed reproduction lowers runtime trust only when the failure is setup
  related; a behavioral failure is useful evidence.
- Exact source and targeted runtime evidence override graph ranking.
- Do not ask the analyzer to repeat evidence already gathered by the root.

## Escalation policy

Call the analyzer only with 2–5 named candidates and conflicting evidence.
Its output should reduce the candidate set or specify one lexical/runtime probe.
