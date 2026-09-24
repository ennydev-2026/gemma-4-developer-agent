#!/usr/bin/env python3
"""Summarize swegemma-style JSONL results for TRUST-SWE ablations."""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: expected a JSON object")
            rows.append(value)
    if not rows:
        raise ValueError(f"{path}: no result rows")
    return rows


def _mean(rows: Iterable[dict[str, Any]], key: str) -> float | None:
    values = [
        float(row[key])
        for row in rows
        if isinstance(row.get(key), (int, float))
    ]
    return round(statistics.fmean(values), 3) if values else None


def _error_category(row: dict[str, Any]) -> str:
    error = str(row.get("agent_error") or row.get("verify_error") or "").lower()
    if not error:
        return "none"
    if "budget" in error or "timeout" in error or "time " in error:
        return "budget"
    if "loop" in error or int(row.get("nudges") or 0) >= 3:
        return "loop"
    if "empty patch" in error:
        return "empty_patch"
    return "other"


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    resolved = sum(bool(row.get("resolved")) for row in rows)
    empty_patches = sum(int(row.get("patch_size") or 0) <= 0 for row in rows)
    submitted = sum(bool(row.get("patch_submitted")) for row in rows)
    errors = Counter(_error_category(row) for row in rows)

    by_repo_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        repo = str(row.get("repo") or "unknown")
        by_repo_rows[repo].append(row)

    by_repo = {}
    for repo, group in sorted(by_repo_rows.items()):
        repo_resolved = sum(bool(row.get("resolved")) for row in group)
        by_repo[repo] = {
            "tasks": len(group),
            "resolved": repo_resolved,
            "resolution_rate": round(repo_resolved / len(group), 4),
            "mean_agent_seconds": _mean(group, "agent_seconds"),
            "mean_tool_calls": _mean(group, "tool_calls"),
        }

    return {
        "tasks": total,
        "resolved": resolved,
        "resolution_rate": round(resolved / total, 4),
        "patch_submitted": submitted,
        "empty_patches": empty_patches,
        "mean_agent_seconds": _mean(rows, "agent_seconds"),
        "mean_tool_calls": _mean(rows, "tool_calls"),
        "mean_llm_turns": _mean(rows, "llm_turns"),
        "error_categories": dict(sorted(errors.items())),
        "by_repo": by_repo,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path, help="swegemma task_results.jsonl")
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()

    try:
        summary = summarize(load_jsonl(args.results))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    rendered = json.dumps(summary, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
