#!/usr/bin/env bash
# Build WSL-native ~/cell2-ship/ bundle for SkyPilot launch.
set -euo pipefail

SRC=/mnt/d/AI/hd-instrument
DST=/root/cell2-ship

echo "=== [1/4] cleaning ${DST} ==="
if [ -d "${DST}" ]; then
  rm -rf "${DST:?}"
fi
mkdir -p "${DST}/experiments" "${DST}/skypilot"

echo "=== [2/4] copying script + helper ==="
cp "${SRC}/experiments/exp_substrate_wikipedia_layer15_cache_extraction_v1.py" \
   "${DST}/experiments/exp_substrate_wikipedia_layer15_cache_extraction_v1.py"
cp "${SRC}/experiments/_seed_checkpoint.py" "${DST}/experiments/_seed_checkpoint.py"

echo "=== [3/4] copying root files + YAML ==="
cp "${SRC}/requirements_cloud.txt" "${DST}/requirements_cloud.txt"
cp "${SRC}/skypilot/cell2_wiki_gh200.yaml" "${DST}/skypilot/cell2_wiki_gh200.yaml"

echo "=== [4/4] verifying bundle ==="
find "${DST}" -type f -printf '%P  %s bytes\n' | sort
du -sh "${DST}"
find "${DST}" -type f | wc -l
echo "OK"
