#!/usr/bin/env bash
# Quick repository snapshot for /workspace (competition sandbox).
set -euo pipefail
cd /workspace 2>/dev/null || cd "${WORKSPACE:-.}"

echo "=== pwd ==="
pwd
echo
echo "=== git status -sb ==="
git status -sb 2>/dev/null || echo "(no git repo)"
echo
echo "=== recent commits ==="
git log -n 5 --oneline 2>/dev/null || true
echo
echo "=== top-level (maxdepth 2) ==="
find . -maxdepth 2 -type d ! -path './.git*' 2>/dev/null | head -40
echo
echo "=== python project markers ==="
ls -1 pyproject.toml setup.cfg setup.py requirements.txt 2>/dev/null || true
