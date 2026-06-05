#!/usr/bin/env bash
# Build WSL-native ~/llama-1b-ship/ bundle for SkyPilot launch.
# Bypasses WSL2 /mnt/d 9P stat-walk stall.
#
# Run from WSL Ubuntu:
#   bash /mnt/d/AI/hd-instrument/skypilot/build_llama_1b_ship.sh
set -euo pipefail

SRC=/mnt/d/AI/hd-instrument
DST=/root/llama-1b-ship

echo "=== [1/4] cleaning ${DST} ==="
if [ -d "${DST}" ]; then
  rm -rf "${DST:?}"
fi
mkdir -p "${DST}/experiments" "${DST}/skypilot"

echo "=== [2/4] copying script + helper ==="
cp "${SRC}/experiments/exp_phase05_v1_llama32_1b_per_token_residual_extract_v1.py" \
   "${DST}/experiments/exp_phase05_v1_llama32_1b_per_token_residual_extract_v1.py"
cp "${SRC}/experiments/_seed_checkpoint.py" "${DST}/experiments/_seed_checkpoint.py"

echo "=== [3/4] copying root files + YAML ==="
cp "${SRC}/requirements_cloud.txt" "${DST}/requirements_cloud.txt"
cp "${SRC}/skypilot/llama_1b.yaml" "${DST}/skypilot/llama_1b.yaml"

echo "=== [4/4] verifying bundle ==="
find "${DST}" -type f -printf '%P  %s bytes\n' | sort
du -sh "${DST}"
find "${DST}" -type f | wc -l
echo "OK"
