#!/usr/bin/env bash
# Build WSL-native ~/hd-ship/ bundle for SkyPilot launch.
# Bypasses WSL2 /mnt/d 9P stat-walk stall that killed previous launches.
#
# Run from inside WSL Ubuntu:
#   bash /mnt/d/AI/hd-instrument/skypilot/build_hd_ship.sh
set -euo pipefail

SRC=/mnt/d/AI/hd-instrument
DST=/root/hd-ship

echo "=== [1/4] cleaning ${DST} ==="
if [ -d "${DST}" ]; then
  rm -rf "${DST:?}"
fi
mkdir -p "${DST}/experiments" "${DST}/testbed/llm_integration" "${DST}/skypilot"

echo "=== [2/4] copying Y+ anchor scripts (5) + helper ==="
# Phase 0.5 v2 Y+ scope (per research_routing_v359_phase05_v2_FINAL_y_plus):
#   - Probe training + validation (waves 1-2)
#   - Y+ dual-observable drift (wave 3a: A1 kappa_3 + A2 BBP)
#   - Y+ dual-primitive deletion cert (wave 3b: B1 PP-46 + B2 PP-56)
#   - Y+ depth-defensive refusal cert (wave 3c: C1 depth-3 + C2 depth-4)
# Phase 0.5b distillation is DEFERRED per Y+ spec section 11; ships separately.
for f in \
  exp_phase05_probe_training_v1.py \
  exp_phase05_probe_validation_v1.py \
  exp_tier7_mvp_hyperprobe_llama31_drift_v2_y_plus_dual_observable.py \
  exp_tier7_mvp_hyperprobe_llama31_deletion_cert_v2_y_plus_dual_primitive.py \
  exp_tier7_mvp_hyperprobe_llama31_refusal_cert_v2_y_plus_depth_defensive.py \
  _seed_checkpoint.py
do
  cp "${SRC}/experiments/${f}" "${DST}/experiments/${f}"
done

echo "=== [3/4] copying testbed package (5) + root files (2) ==="
cp "${SRC}/testbed/__init__.py"                              "${DST}/testbed/__init__.py"
# api.py is transitively required: testbed/__init__.py imports from testbed.api
# (AuditReport, DeletionCertificate, MemoryBackend, RetrievalResult). The 2026-06-03
# hd-brain FAILED_SETUP was caused by this file missing from the bundle.
cp "${SRC}/testbed/api.py"                                   "${DST}/testbed/api.py"
cp "${SRC}/testbed/llm_integration/__init__.py"              "${DST}/testbed/llm_integration/__init__.py"
cp "${SRC}/testbed/llm_integration/hyperprobe_encoder.py"    "${DST}/testbed/llm_integration/hyperprobe_encoder.py"
cp "${SRC}/testbed/llm_integration/substrate_audit.py"       "${DST}/testbed/llm_integration/substrate_audit.py"
cp "${SRC}/requirements_cloud.txt"                            "${DST}/requirements_cloud.txt"
cp "${SRC}/skypilot/phase05.yaml"                             "${DST}/skypilot/phase05.yaml"

echo "=== [4/4] verifying bundle ==="
echo "--- tree ---"
find "${DST}" -type f -printf '%P  %s bytes\n' | sort
echo "--- size ---"
du -sh "${DST}"
echo "--- files ---"
find "${DST}" -type f | wc -l
echo "OK"
