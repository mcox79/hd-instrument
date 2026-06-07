#!/usr/bin/env bash
# Build WSL-native /root/cell4-ship/ bundle for CELL-4.
# CELL-4 only needs FIRST 100K facts from CELL-2 cache (the script reads first 10 shards).
set -euo pipefail

SRC=/mnt/d/AI/hd-instrument
DST=/root/cell4-ship
N_SHARDS_NEEDED=15   # 10 shards = 100K + 5 buffer for dedup over-collect

echo "=== [1/5] cleaning ${DST} ==="
if [ -d "${DST}" ]; then
    rm -rf "${DST:?}"
fi
mkdir -p "${DST}/experiments" "${DST}/skypilot" "${DST}/data/cell2_results"

echo "=== [2/5] copying script + helper ==="
cp "${SRC}/experiments/exp_substrate_hp12_v2_100k_pseudoinverse_v1.py" \
   "${DST}/experiments/exp_substrate_hp12_v2_100k_pseudoinverse_v1.py"
cp "${SRC}/experiments/_seed_checkpoint.py" "${DST}/experiments/_seed_checkpoint.py"

echo "=== [3/5] copying first ${N_SHARDS_NEEDED} CELL-2 v3 shards (~600 MB; need 100K facts) ==="
if [ ! -d "${SRC}/data/cell2_results" ]; then
    echo "ERROR: ${SRC}/data/cell2_results/ missing"
    exit 1
fi
ls "${SRC}/data/cell2_results/"shard_*.npz | sort | head -n "${N_SHARDS_NEEDED}" | \
    xargs -I{} cp {} "${DST}/data/cell2_results/"
if [ -f "${SRC}/data/cell2_results/metrics.json" ]; then
    cp "${SRC}/data/cell2_results/metrics.json" "${DST}/data/cell2_results/metrics.json"
fi

echo "=== [4/5] copying root files + YAML ==="
cp "${SRC}/requirements_cloud.txt" "${DST}/requirements_cloud.txt"
cp "${SRC}/skypilot/cell4/cell4_hp12_v2_h100.yaml" \
   "${DST}/skypilot/cell4_hp12_v2_h100.yaml"

echo "=== [5/5] verifying bundle ==="
find "${DST}" -type f -printf '%P  %s bytes\n' | sort
echo "shards in bundle:"
ls "${DST}/data/cell2_results/"shard_*.npz 2>/dev/null | wc -l
du -sh "${DST}"
echo "OK"
