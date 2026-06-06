#!/usr/bin/env bash
# Smart launcher for CELL-1: 70B fp16 disambiguation on Lambda H100:2 SXM5.
#
# Differs from smart_launch_cloud_1.sh:
#   - Targets ONLY gpu_2x_h100_sxm5 (only Lambda SKU with >80 GB combined VRAM
#     that fits 70B at fp16; GH200 has 96 GB but unified-memory offload is slow)
#   - Single SKU; cycles regions via YAML any_of + sky --retry-until-up
#   - Same hardening (PID lock + TRAP cleanup + preflight gate)
#
# Pre-flight gate REQUIRED (Bug A + Bug B defense per
# [[cloud-dispatch-pre-flight-checklist]]).
set -uo pipefail

source /root/skyvenv/bin/activate

# PID-file lock so duplicate invocations REFUSE to start (Bug B defense).
LOCKFILE=/tmp/smart_launch_cell1.pid
if [ -f "$LOCKFILE" ]; then
  OLD_PID=$(cat "$LOCKFILE" 2>/dev/null || echo "")
  if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
    echo "ERROR: another smart_launch_cell1.sh is already running (PID=$OLD_PID)."
    exit 1
  fi
fi
echo $$ > "$LOCKFILE"
cleanup_on_exit() {
  rm -f "$LOCKFILE"
  pkill -P $$ 2>/dev/null || true
}
trap cleanup_on_exit EXIT INT TERM

# Pre-flight gate (mandatory; both Bug A + Bug B defense).
EXPECTED_SCRIPT="exp_substrate_extraction_quality_70B_fp16_disambiguation_v1.py"
BUNDLE_PATH="/root/cell1-ship"
YAML_FOR_PREFLIGHT="${BUNDLE_PATH}/skypilot/cell1_70b_fp16.yaml"
echo "[smart_launch_cell1] running pre-flight gate..."
if ! bash /mnt/d/AI/hd-instrument/skypilot/preflight_cloud_dispatch.sh \
      "$YAML_FOR_PREFLIGHT" "$EXPECTED_SCRIPT" "$BUNDLE_PATH"; then
  echo "ERROR: preflight FAILED; dispatch refused."
  exit 1
fi

HF_TOKEN_VAL="$(cat /mnt/d/AI/hd-instrument/.hf_token)"
if [ -z "${HF_TOKEN_VAL}" ]; then
  echo "ERROR: HF token empty"; exit 1
fi

LOG=/mnt/d/AI/hd-instrument/data/cell1_smart_launch.log
mkdir -p "$(dirname "$LOG")"

echo "===== CELL-1 smart launch start $(date -u '+%Y-%m-%dT%H:%M:%SZ') =====" | tee -a "$LOG"
echo "HF_TOKEN length: ${#HF_TOKEN_VAL} chars; prefix: ${HF_TOKEN_VAL:0:5}..." | tee -a "$LOG"
echo "lock file: $LOCKFILE (PID $$)" | tee -a "$LOG"
echo "yaml: $YAML_FOR_PREFLIGHT" | tee -a "$LOG"

cd "$BUNDLE_PATH"
CLUSTER_NAME="cell170b-$(date +%H%M%S)"
echo "cluster name: ${CLUSTER_NAME}" | tee -a "$LOG"

# sky launch with --retry-until-up (multi-region YAML any_of will cycle).
sky launch \
    -c "$CLUSTER_NAME" \
    -y \
    --retry-until-up \
    --down \
    -i 30 \
    --env HF_TOKEN="${HF_TOKEN_VAL}" \
    skypilot/cell1_70b_fp16.yaml 2>&1 | tee -a "$LOG"

EXIT_CODE=${PIPESTATUS[0]}
echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] sky launch exit code: ${EXIT_CODE}" | tee -a "$LOG"

if [ "${EXIT_CODE}" -eq 0 ]; then
  echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] SCPing CELL-1 metrics back" | tee -a "$LOG"
  LOCAL_DIR=/mnt/d/AI/hd-instrument/data/cell1_results
  mkdir -p "${LOCAL_DIR}"
  rsync -av --partial \
    -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR" \
    "${CLUSTER_NAME}:~/sky_workdir/data/exp_substrate_extraction_quality_70B_fp16_disambiguation_v1/" \
    "${LOCAL_DIR}/" 2>&1 | tee -a "$LOG" || \
    echo "  [warn] final rsync returned non-zero" | tee -a "$LOG"
fi

echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] sky down ${CLUSTER_NAME} (belt-and-suspenders)" | tee -a "$LOG"
sky down -y "${CLUSTER_NAME}" 2>&1 | tee -a "$LOG" || true

echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] verify no orphan Lambda instances" | tee -a "$LOG"
bash /mnt/d/AI/hd-instrument/skypilot/verify_no_lambda_instances.sh 2>&1 | tee -a "$LOG" || true

echo "===== CELL-1 smart launch end $(date -u '+%Y-%m-%dT%H:%M:%SZ') =====" | tee -a "$LOG"
exit ${EXIT_CODE}
