#!/usr/bin/env bash
# Build WSL-native /root/cell3-ship/ bundle for SkyPilot launch.
# IMPORTANT: includes CELL-2 v3 cache shards (21 GB!) as training data.
set -euo pipefail

SRC=/mnt/d/AI/hd-instrument
DST=/root/cell3-ship

echo "=== [1/5] cleaning ${DST} ==="
if [ -d "${DST}" ]; then
    rm -rf "${DST:?}"
fi
mkdir -p "${DST}/experiments" "${DST}/skypilot" "${DST}/data/cell2_results"

echo "=== [2/5] copying script + helper ==="
cp "${SRC}/experiments/exp_substrate_cell3_distilled_22M_student_v1.py" \
   "${DST}/experiments/exp_substrate_cell3_distilled_22M_student_v1.py"
cp "${SRC}/experiments/_seed_checkpoint.py" "${DST}/experiments/_seed_checkpoint.py"

echo "=== [3/5] copying CELL-2 v3 cache shards (CRITICAL training data; ~21 GB) ==="
if [ ! -d "${SRC}/data/cell2_results" ]; then
    echo "ERROR: ${SRC}/data/cell2_results/ missing -- need CELL-2 v3 cache"
    exit 1
fi
N_SHARDS=$(ls "${SRC}/data/cell2_results/shard_"*.npz 2>/dev/null | wc -l)
if [ "$N_SHARDS" -lt 100 ]; then
    echo "ERROR: only ${N_SHARDS} shards in CELL-2 cache; need many more"
    exit 1
fi
echo "  copying ${N_SHARDS} shards..."
cp -r "${SRC}/data/cell2_results/"shard_*.npz "${DST}/data/cell2_results/"
if [ -f "${SRC}/data/cell2_results/metrics.json" ]; then
    cp "${SRC}/data/cell2_results/metrics.json" "${DST}/data/cell2_results/metrics.json"
fi

echo "=== [4/5] copying root files + YAML ==="
cp "${SRC}/requirements_cloud.txt" "${DST}/requirements_cloud.txt"
cp "${SRC}/skypilot/cell3/cell3_distillation_h100.yaml" \
   "${DST}/skypilot/cell3_distillation_h100.yaml"

echo "=== [5/5] verifying bundle ==="
find "${DST}" -maxdepth 3 -type f -printf '%P  %s bytes\n' | sort | head -20
echo "..."
echo "Total shards in bundle:"
ls "${DST}/data/cell2_results/"shard_*.npz 2>/dev/null | wc -l
du -sh "${DST}"
echo "OK"
