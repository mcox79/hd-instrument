#!/usr/bin/env bash
# Build WSL-native ~/cell1-ship/ bundle for SkyPilot launch.
set -euo pipefail

SRC=/mnt/d/AI/hd-instrument
DST=/root/cell1-ship

echo "=== [1/4] cleaning ${DST} ==="
if [ -d "${DST}" ]; then
  rm -rf "${DST:?}"
fi
mkdir -p "${DST}/experiments" "${DST}/skypilot"

echo "=== [2/4] copying script + helper ==="
cp "${SRC}/experiments/exp_substrate_extraction_quality_70B_fp16_disambiguation_v1.py" \
   "${DST}/experiments/exp_substrate_extraction_quality_70B_fp16_disambiguation_v1.py"
cp "${SRC}/experiments/_seed_checkpoint.py" "${DST}/experiments/_seed_checkpoint.py"

echo "=== [3/4] copying root files + YAML ==="
cp "${SRC}/requirements_cloud.txt" "${DST}/requirements_cloud.txt"
cp "${SRC}/skypilot/cell1_70b_fp16.yaml" "${DST}/skypilot/cell1_70b_fp16.yaml"
cp "${SRC}/skypilot/cell1_70b_b200x1.yaml" "${DST}/skypilot/cell1_70b_b200x1.yaml"

echo "=== [4/4] verifying bundle ==="
find "${DST}" -type f -printf '%P  %s bytes\n' | sort
du -sh "${DST}"
find "${DST}" -type f | wc -l
echo "OK"
