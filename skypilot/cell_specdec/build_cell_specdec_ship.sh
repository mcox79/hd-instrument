#!/usr/bin/env bash
# Build WSL-native /root/cell_specdec-ship/ bundle for CELL-SPECDEC.
set -euo pipefail

SRC=/mnt/d/AI/hd-instrument
DST=/root/cell_specdec-ship

echo "=== [1/4] cleaning ${DST} ==="
if [ -d "${DST}" ]; then
    rm -rf "${DST:?}"
fi
mkdir -p "${DST}/experiments" "${DST}/skypilot"

echo "=== [2/4] copying script + helper ==="
cp "${SRC}/experiments/exp_speculative_decoding_qwen_v1.py" \
   "${DST}/experiments/exp_speculative_decoding_qwen_v1.py"
cp "${SRC}/experiments/_seed_checkpoint.py" "${DST}/experiments/_seed_checkpoint.py"

echo "=== [3/4] copying root files + YAML + .skyignore ==="
cp "${SRC}/requirements_cloud.txt" "${DST}/requirements_cloud.txt"
cp "${SRC}/skypilot/cell_specdec/cell_specdec_qwen_h100.yaml" \
   "${DST}/skypilot/cell_specdec_qwen_h100.yaml"
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
