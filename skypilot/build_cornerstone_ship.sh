#!/usr/bin/env bash
# Build WSL-native ~/cornerstone-ship/ bundle for SkyPilot launch.
# Bypasses WSL2 /mnt/d 9P stat-walk stall that killed prior launches.
#
# Run from WSL Ubuntu:
#   bash /mnt/d/AI/hd-instrument/skypilot/build_cornerstone_ship.sh
set -euo pipefail

SRC=/mnt/d/AI/hd-instrument
DST=/root/cornerstone-ship

echo "=== [1/4] cleaning ${DST} ==="
if [ -d "${DST}" ]; then
  rm -rf "${DST:?}"
fi
mkdir -p "${DST}/experiments" "${DST}/testbed/llm_integration" "${DST}/skypilot"

echo "=== [2/4] copying cornerstone + reused phase05 scripts ==="
# Cornerstone-specific:
#   - C1 post-processor (reads probe_validation metrics, applies HP=0.85 gate)
#   - C2+C3 unified audit script (Llama loaded once, per-cell isolated)
#   - aggregate (reads 3 cell metrics, emits batch verdict)
# Reused from phase05 (unchanged):
#   - probe_training_v1 (Algorithm 1 Hyperprobe MLP training)
#   - probe_validation_v1 (held-out cos_sim measurement)
#   - _seed_checkpoint (write_metrics, get_output_dir, resumable_seeds)
for f in \
  exp_phase05_probe_training_v1.py \
  exp_phase05_probe_validation_v1.py \
  exp_cornerstone_c1_replication_postprocess_v1.py \
  exp_cornerstone_c2_c3_audit_llama_3_1_8b_v1.py \
  exp_cornerstone_aggregate_v1.py \
  _seed_checkpoint.py
do
  cp "${SRC}/experiments/${f}" "${DST}/experiments/${f}"
done

echo "=== [3/4] copying testbed package + root files ==="
# testbed/api.py is transitively required: testbed/__init__.py imports from it
# (AuditReport, DeletionCertificate, MemoryBackend, RetrievalResult). The
# 2026-06-03 hd-brain FAILED_SETUP was caused by this file missing.
cp "${SRC}/testbed/__init__.py"                              "${DST}/testbed/__init__.py"
cp "${SRC}/testbed/api.py"                                   "${DST}/testbed/api.py"
cp "${SRC}/testbed/llm_integration/__init__.py"              "${DST}/testbed/llm_integration/__init__.py"
cp "${SRC}/testbed/llm_integration/hyperprobe_encoder.py"    "${DST}/testbed/llm_integration/hyperprobe_encoder.py"
cp "${SRC}/testbed/llm_integration/substrate_audit.py"       "${DST}/testbed/llm_integration/substrate_audit.py"
cp "${SRC}/requirements_cloud.txt"                            "${DST}/requirements_cloud.txt"
cp "${SRC}/skypilot/cornerstone.yaml"                         "${DST}/skypilot/cornerstone.yaml"

echo "=== [4/4] verifying bundle ==="
echo "--- tree ---"
find "${DST}" -type f -printf '%P  %s bytes\n' | sort
echo "--- size ---"
du -sh "${DST}"
echo "--- files ---"
find "${DST}" -type f | wc -l
echo "OK"
