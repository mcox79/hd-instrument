#!/usr/bin/env bash
# Build WSL-native /root/cell_colbert-ship/ bundle for CELL-COLBERT.
# Small bundle (no big cache shards needed; HotpotQA + ColBERT-v2 are downloaded in setup).
set -euo pipefail

SRC=/mnt/d/AI/hd-instrument
DST=/root/cell_colbert-ship

echo "=== [1/4] cleaning ${DST} ==="
if [ -d "${DST}" ]; then
    rm -rf "${DST:?}"
fi
mkdir -p "${DST}/experiments" "${DST}/skypilot"

echo "=== [2/4] copying script + helper ==="
cp "${SRC}/experiments/exp_colbert_v2_hotpot_distractor_v1.py" \
   "${DST}/experiments/exp_colbert_v2_hotpot_distractor_v1.py"
cp "${SRC}/experiments/_seed_checkpoint.py" "${DST}/experiments/_seed_checkpoint.py"

echo "=== [3/4] copying root files + YAML + .skyignore ==="
cp "${SRC}/requirements_cloud.txt" "${DST}/requirements_cloud.txt"
cp "${SRC}/skypilot/cell_colbert/cell_colbert_hotpot_h100.yaml" \
   "${DST}/skypilot/cell_colbert_hotpot_h100.yaml"
# Minimal .skyignore so only relevant files upload (bundle is small anyway)
cat > "${DST}/.skyignore" <<'EOF'
data/cell2_results
__pycache__
*.pyc
.git
.venv
.venv-*
EOF

echo "=== [4/4] verifying bundle ==="
find "${DST}" -type f -printf '%P  %s bytes\n' | sort
du -sh "${DST}"
echo "OK"
