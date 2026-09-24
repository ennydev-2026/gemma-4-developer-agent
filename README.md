# TRUST-SWE — Gemma 4 Developer Agent

Reliability-aware starter for the Kaggle competition **[Google — The Gemma 4 Developer Agent Competition](https://www.kaggle.com/competitions/gemma-4-developer-agent)**.

**TRUST-SWE** (Tool-Reliability and Uncertainty-aware Search & Testing)
treats graph, lexical, and runtime tools as fallible sensors. It switches
navigation modes when evidence is empty, noisy, or contradictory instead of
blindly following a graph-first policy.

The submission is a declarative ADK-style tree packaged as `submission.zip`
with `agent.yaml` at the archive root.

## Prizes and timeline

| Track | Pool |
| --- | --- |
| **Developer Agent (this repo)** | **$65,000** (1st $37k · 2nd $18k · 3rd $10k) |
| **Optional research paper** | **$35,000** ([paper track](https://www.kaggle.com/competitions/gemma-4-developer-agent)) |

**Total:** $100,000

| Milestone | Date (UTC) |
| --- | --- |
| Start | September 23, 2026 |
| Optional paper deadline | November 12, 2026 |
| Entry / team merger deadline | November 25, 2026 |
| **Final submission** | **December 2, 2026** |

Accept the competition rules on Kaggle before the entry deadline.

## Repository layout

```
submission/                 # Upload contents of this folder (via pack script)
├── agent.yaml              # REQUIRED — model gemma-4-31b-it-qat-w4a16-ct only
├── eval_config.yaml        # Optional per-task limits / harness overrides
├── configs/sampling.yaml   # Generation params (!include from agent.yaml)
├── prompts/
├── sub_agents/
├── adapters/               # Place real LoRA dirs here (no fake weights in git)
└── skills/repo_navigation/
README.md
LICENSE                   # MIT
Makefile
scripts/pack_submission.sh
scripts/validate_submission.py
scripts/summarize_results.py
docs/STRATEGY.md
```

The competition dataset includes `sample_submission/`, `tasks.jsonl`, graphs, embeddings, and **HARNESS_README.md** for local evaluation with `swegemma` / `adk-eval-core` (install from the dataset, not this repo).

## Model and adapters

- **Required base model:** `gemma-4-31b-it-qat-w4a16-ct` for every `LlmAgent` and sub-agent.
- **Optional LoRA:** add `submission/adapters/<name>/` with `adapter_config.json` and `adapter_model.safetensors`, then set `adapter: <name>` on agents in YAML.
- This starter does **not** ship Gemma weights or placeholder LoRA files.

## Harness tools (root agent)

The evaluator exposes sandboxed tools only, including:

`run_command`, `submit_patch`, `get_status`, `read_file`, `edit_file`,
`write_file`, `get_code_neighbors`, `search_similar_code`, and
`get_code_subgraph`.

See the competition page and **HARNESS_README.md** for signatures, budgets, and sandbox layout (`/workspace`, `/wheels`, etc.).

Important: in the released harness, `search_similar_code` should be queried
with a resolvable function/class/module symbol, not a natural-language sentence.
TRUST-SWE cross-checks graph output against source and falls back to lexical
search when graph evidence is unreliable.

## Pack and submit

From the repo root:

```bash
python3 -m pip install -r requirements-dev.txt
make validate  # local schema and policy preflight
make pack      # writes ./submission.zip
make verify    # rebuilds and inspects archive layout
```

Upload `submission.zip` on the Kaggle competition **Submit Predictions** page.

The zip **must** look like:

```
submission.zip
├── agent.yaml
├── eval_config.yaml
├── configs/...
└── ...
```

Not `submission/agent.yaml` nested inside an extra directory.
`adapters/.gitkeep` is retained in Git but intentionally excluded from the zip.

## Local development (high level)

1. Download the competition dataset from Kaggle (graphs, embeddings, snapshots, harness libraries).
2. Validate the submission with the official `adk_submission` compiler from the dataset; the local validator is a fast preflight, not a replacement.
3. Run lexical-only, fixed graph-first, and TRUST-SWE variants on held-out tasks.
4. Summarize harness JSONL with `python3 scripts/summarize_results.py task_results.jsonl`.
5. Add real LoRA adapters only after held-out prompt ablations are stable.
6. `make verify` and upload.

Research hypothesis, routing policy, and ablations:
[docs/STRATEGY.md](docs/STRATEGY.md). Literature boundary:
[docs/PRIOR_ART.md](docs/PRIOR_ART.md). Experiment conventions:
[experiments/README.md](experiments/README.md). Adapter data contract:
[training/README.md](training/README.md).

## License

MIT — see [LICENSE](LICENSE).
