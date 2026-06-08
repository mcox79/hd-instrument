#!/usr/bin/env bash
# Build WSL-native /root/cell_a2-ship/ bundle for CELL-A2.
# Includes HotpotQA distractor 1k JSONL data file (~6 MB).
set -euo pipefail

SRC=/mnt/d/AI/hd-instrument
DST=/root/cell_a2-ship

echo "=== [1/5] cleaning ${DST} ==="
if [ -d "${DST}" ]; then
    rm -rf "${DST:?}"
fi
mkdir -p "${DST}/experiments" "${DST}/skypilot" "${DST}/data/datasets"

echo "=== [2/5] copying script + helper ==="
cp "${SRC}/experiments/exp_substrate_llama8b_triples_khop_gpu_v1.py" \
   "${DST}/experiments/exp_substrate_llama8b_triples_khop_gpu_v1.py"
cp "${SRC}/experiments/_seed_checkpoint.py" "${DST}/experiments/_seed_checkpoint.py"

echo "=== [3/5] copying HotpotQA distractor data ==="
test -f "${SRC}/data/datasets/hotpot_qa_distractor_dev_1k.jsonl" || \
    { echo "ERROR: HotpotQA JSONL missing in src"; exit 1; }
cp "${SRC}/data/datasets/hotpot_qa_distractor_dev_1k.jsonl" \
   "${DST}/data/datasets/hotpot_qa_distractor_dev_1k.jsonl"

echo "=== [4/5] copying root files + YAML + .skyignore ==="
cp "${SRC}/requirements_cloud.txt" "${DST}/requirements_cloud.txt"
cp "${SRC}/skypilot/cell_a2/cell_a2_llama8b_h100.yaml" \
   "${DST}/skypilot/cell_a2_llama8b_h100.yaml"
cat > "${DST}/.skyignore" <<'EOF'
data/cell2_results
__pycache__
*.pyc
.git
.venv
.venv-*
EOF

echo "=== [5/5] verifying bundle ==="
find "${DST}" -type f -printf '%P  %s bytes\n' | sort
du -sh "${DST}"
echo "OK"
