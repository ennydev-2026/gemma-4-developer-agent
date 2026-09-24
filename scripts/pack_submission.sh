#!/usr/bin/env bash
# Build submission.zip with agent.yaml at the archive root (Kaggle requirement).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SUBMISSION_DIR="${ROOT}/submission"
OUT_ZIP="${ROOT}/submission.zip"
VALIDATOR="${ROOT}/scripts/validate_submission.py"

verify_only=false
if [[ "${1:-}" == "--verify-only" ]]; then
  verify_only=true
fi

python3 "${VALIDATOR}" "${SUBMISSION_DIR}" --strict

if [[ "${verify_only}" == "false" ]]; then
  if [[ ! -f "${SUBMISSION_DIR}/agent.yaml" ]]; then
    echo "error: missing ${SUBMISSION_DIR}/agent.yaml" >&2
    exit 1
  fi
  rm -f "${OUT_ZIP}"
  # .gitkeep preserves the empty adapters directory in Git but is not an
  # accepted submission artifact. Directory entries are retained by zip.
  (cd "${SUBMISSION_DIR}" && zip -qr "${OUT_ZIP}" . -x '*/.gitkeep' '.gitkeep')
  echo "wrote ${OUT_ZIP}"
fi

if [[ ! -f "${OUT_ZIP}" ]]; then
  echo "error: ${OUT_ZIP} not found (run without --verify-only first)" >&2
  exit 1
fi

# agent.yaml must be at zip root (not nested under submission/)
if ! unzip -l "${OUT_ZIP}" | awk '{print $4}' | grep -qx 'agent.yaml'; then
  echo "error: agent.yaml is not at the root of ${OUT_ZIP}" >&2
  unzip -l "${OUT_ZIP}" >&2
  exit 1
fi

if unzip -Z1 "${OUT_ZIP}" | grep -Eq '(^|/)\.gitkeep$|^submission/'; then
  echo "error: archive contains repository-only or nested submission paths" >&2
  unzip -Z1 "${OUT_ZIP}" >&2
  exit 1
fi

echo "ok: agent.yaml at zip root"
unzip -l "${OUT_ZIP}"
