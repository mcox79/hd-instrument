#!/usr/bin/env bash
# Build WSL-native ~/cell5-ship/ bundle for SkyPilot launch.
set -euo pipefail

SRC=/mnt/d/AI/hd-instrument
DST=/root/cell5-ship

echo "=== [1/5] cleaning ${DST} ==="
if [ -d "${DST}" ]; then
  rm -rf "${DST:?}"
fi
mkdir -p "${DST}/experiments" "${DST}/skypilot" "${DST}/data/cell5_teacher"

echo "=== [2/5] copying script + helper ==="
cp "${SRC}/experiments/exp_substrate_cascade_distillation_fd_smoke_v1.py" \
   "${DST}/experiments/exp_substrate_cascade_distillation_fd_smoke_v1.py"
cp "${SRC}/experiments/_seed_checkpoint.py" "${DST}/experiments/_seed_checkpoint.py"

echo "=== [3/5] copying runner-prepared teacher data (CRITICAL!) ==="
if [ ! -f "${SRC}/data/cell5_teacher/prompts.jsonl" ]; then
  echo "ERROR: ${SRC}/data/cell5_teacher/prompts.jsonl missing"
  echo "Run teacher inference first: python experiments/cell5_teacher_inference_local.py --full"
  exit 1
fi
if [ ! -f "${SRC}/data/cell5_teacher/responses.jsonl" ]; then
  echo "ERROR: ${SRC}/data/cell5_teacher/responses.jsonl missing"
  exit 1
fi
cp "${SRC}/data/cell5_teacher/prompts.jsonl" "${DST}/data/cell5_teacher/prompts.jsonl"
cp "${SRC}/data/cell5_teacher/responses.jsonl" "${DST}/data/cell5_teacher/responses.jsonl"
if [ -f "${SRC}/data/cell5_teacher/manifest.json" ]; then
  cp "${SRC}/data/cell5_teacher/manifest.json" "${DST}/data/cell5_teacher/manifest.json"
fi

echo "=== [4/5] copying root files + YAML ==="
cp "${SRC}/requirements_cloud.txt" "${DST}/requirements_cloud.txt"
cp "${SRC}/skypilot/cell5_distillation_h100.yaml" "${DST}/skypilot/cell5_distillation_h100.yaml"

echo "=== [5/5] verifying bundle ==="
find "${DST}" -type f -printf '%P  %s bytes\n' | sort
du -sh "${DST}"
N_PROMPTS=$(wc -l < "${DST}/data/cell5_teacher/prompts.jsonl")
N_RESPONSES=$(wc -l < "${DST}/data/cell5_teacher/responses.jsonl")
echo "prompts.jsonl=${N_PROMPTS} lines  responses.jsonl=${N_RESPONSES} lines"
if [ "${N_RESPONSES}" -lt 100 ]; then
  echo "WARNING: responses.jsonl has only ${N_RESPONSES} lines; CELL-5 needs >= 100 to be meaningful"
fi
echo "OK"
