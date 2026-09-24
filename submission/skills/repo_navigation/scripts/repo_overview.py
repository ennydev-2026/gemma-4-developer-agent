#!/usr/bin/env python3
"""Print a bounded, read-only overview of the current task repository."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


WORKSPACE = Path("/workspace")
if not WORKSPACE.is_dir():
    WORKSPACE = Path(os.environ.get("WORKSPACE", ".")).resolve()


def run(*args: str) -> str:
    result = subprocess.run(
        args,
        cwd=WORKSPACE,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    return (result.stdout or result.stderr).strip()


print("=== workspace ===")
print(WORKSPACE)
print("\n=== git status -sb ===")
print(run("git", "status", "-sb") or "(clean or no git repository)")
print("\n=== recent commits ===")
print(run("git", "log", "-n", "5", "--oneline") or "(unavailable)")
print("\n=== directories (depth <= 2) ===")

shown = 0
for current, directories, _files in os.walk(WORKSPACE):
    relative = Path(current).relative_to(WORKSPACE)
    if relative.parts and relative.parts[0] == ".git":
        directories[:] = []
        continue
    depth = len(relative.parts)
    if depth > 2:
        directories[:] = []
        continue
    print("." if depth == 0 else f"./{relative.as_posix()}")
    directories[:] = sorted(
        name for name in directories if name not in {".git", "__pycache__"}
    )
    shown += 1
    if shown >= 40:
        break

print("\n=== Python project markers ===")
markers = ("pyproject.toml", "setup.cfg", "setup.py", "requirements.txt")
present = [name for name in markers if (WORKSPACE / name).is_file()]
print("\n".join(present) if present else "(none at repository root)")
