#!/bin/bash
# Tier 2 clean-room rerun: generate n=2 bare-model outputs per task prompt.
# BEFORE running: 1) update MODEL to the current model id (check `claude --help` /
# official docs — do NOT trust this file's default across months);
# 2) rerun the zero-injection probe (ask the clean room what section headers it sees).
set -euo pipefail
MODEL="claude-opus-4-8"   # <- verify current id before reuse
OUT="outputs-rerun"
mkdir -p "${OUT}"
cd /tmp   # clean cwd: no project CLAUDE.md above
for p in "$(dirname "$0")"/prompts/p*.txt; do
  base=$(basename "${p}" .txt)
  for n in 1 2; do
    command claude --print --setting-sources "" --model "${MODEL}" \
      --no-session-persistence "$(cat "${p}")" \
      > "$(dirname "$0")/${OUT}/${base}_${n}.txt" 2>&1
    echo "done ${base}_${n}"
  done
done
