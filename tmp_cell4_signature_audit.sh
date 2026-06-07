#!/bin/bash
# CELL-4 signature audit per the lesson learned 2026-06-07.
# For every `def func(...)` in the script, list ALL call sites and visually
# verify the calling conventions match.
set -e
SCRIPT=/mnt/d/AI/hd-instrument/experiments/exp_substrate_hp12_v2_100k_pseudoinverse_v1.py

echo "=== function definitions ==="
grep -nP '^def \w+\(' "$SCRIPT" | head -30
echo ""

# For each function, list call sites
for FUNC in pca_whiten_fit pca_whiten_apply random_orthogonal pseudoinverse_write \
            deterministic_hash_to_int consistent_hash_fragment build_substrate \
            evaluate_retrieval load_cell2_passages; do
    echo "=== $FUNC ==="
    DEF=$(grep -nP "^def ${FUNC}\(" "$SCRIPT")
    echo "  def:  $DEF"
    grep -nP "\b${FUNC}\(" "$SCRIPT" | grep -v "^.*:def " | sed 's/^/  call: /' | head -10
    echo ""
done

echo "=== self-test PASS verification ==="
/root/skyvenv/bin/python3 "$SCRIPT" --self-test 2>&1 | tail -3
