# Compact evidence ledger

Keep this state in the model context. Never write it into `/workspace`.

```text
ANCHORS: exact issue facts
MODE: exact | lexical | graph | runtime | patch | verify
CANDIDATES:
  1. symbol/path — confidence — supporting fact
  2. symbol/path — confidence — supporting fact
  3. symbol/path — confidence — supporting fact
ALTERNATIVE: credible competing cause
TOOL_TRUST: graph=?, lexical=?, runtime=?
TRIED: calls that added no information
NEXT: one discriminating action
PATCH: none | edited files
VERIFY: not-run | reproduced | focused-test-pass
```

## Update rules

- Keep no more than three candidates.
- Confidence may rise only from a concrete source, graph edge, or runtime result.
- Record a contradictory observation instead of silently discarding it.
- Remove stale source observations after editing that source.
- Never claim success from an intended tool call; require an actual tool result.
- On low budget, collapse the ledger to leading cause, patch, and verification.
