# Gemma 4 Developer Agent — competition starter

Starter repository for the Kaggle competition **[Google — The Gemma 4 Developer Agent Competition](https://www.kaggle.com/competitions/gemma-4-developer-agent)**.

Post-train **Gemma 4** into an autonomous software engineering agent that navigates real Python codebases and submits patches for SWE-Bench-style issues. Submissions are declarative **ADK Agent Config** trees packaged as `submission.zip` with `agent.yaml` at the archive root.

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
docs/STRATEGY.md
```

The competition dataset includes `sample_submission/`, `tasks.jsonl`, graphs, embeddings, and **HARNESS_README.md** for local evaluation with `swegemma` / `adk-eval-core` (install from the dataset, not this repo).

## Model and adapters

- **Required base model:** `gemma-4-31b-it-qat-w4a16-ct` for every `LlmAgent` and sub-agent.
- **Optional LoRA:** add `submission/adapters/<name>/` with `adapter_config.json` and `adapter_model.safetensors`, then set `adapter: <name>` on agents in YAML.
- This starter does **not** ship Gemma weights or placeholder LoRA files.

## Harness tools (root agent)

The evaluator exposes sandboxed tools only, including:

`run_command`, `submit_patch`, `get_status`, `read_file`, `edit_file`, `write_file`, `get_code_neighbors`, `search_similar_code`, `get_code_subgraph`, plus skill helpers `run_skill_script` and `load_skill_resource`.

See the competition page and **HARNESS_README.md** for signatures, budgets, and sandbox layout (`/workspace`, `/wheels`, etc.).

## Pack and submit

From the repo root:

```bash
chmod +x scripts/pack_submission.sh
make pack      # writes ./submission.zip
make verify    # asserts agent.yaml is at zip root
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

## Local development (high level)

1. Download the competition dataset from Kaggle (graphs, embeddings, snapshots, harness libraries).
2. Iterate on `submission/agent.yaml`, prompts, skills, and optional adapters.
3. Run the harness CLI described in **HARNESS_README.md** against `tasks.jsonl`.
4. `make pack` and upload.

Tuning ideas and ablation notes: [docs/STRATEGY.md](docs/STRATEGY.md).

## License

MIT — see [LICENSE](LICENSE).
