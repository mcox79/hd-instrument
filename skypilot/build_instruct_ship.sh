#!/usr/bin/env bash
# Build WSL-native ~/instruct-ship/ bundle for SkyPilot launch.
set -euo pipefail

SRC=/mnt/d/AI/hd-instrument
DST=/root/instruct-ship

echo "=== [1/4] cleaning ${DST} ==="
if [ -d "${DST}" ]; then
  rm -rf "${DST:?}"
fi
mkdir -p "${DST}/experiments" "${DST}/skypilot"

echo "=== [2/4] copying script + helper ==="
cp "${SRC}/experiments/exp_substrate_extraction_quality_70B_instruct_nf4_v1.py" \
   "${DST}/experiments/exp_substrate_extraction_quality_70B_instruct_nf4_v1.py"
cp "${SRC}/experiments/_seed_checkpoint.py" "${DST}/experiments/_seed_checkpoint.py"

echo "=== [3/4] copying root files + YAMLs ==="
cp "${SRC}/requirements_cloud.txt" "${DST}/requirements_cloud.txt"
cp "${SRC}/skypilot/instruct_70b_nf4_gh200.yaml" "${DST}/skypilot/instruct_70b_nf4_gh200.yaml"
cp "${SRC}/skypilot/instruct_70b_nf4_h100x1.yaml" "${DST}/skypilot/instruct_70b_nf4_h100x1.yaml"

echo "=== [4/4] verifying bundle ==="
find "${DST}" -type f -printf '%P  %s bytes\n' | sort
du -sh "${DST}"
find "${DST}" -type f | wc -l
echo "OK"
