#!/usr/bin/env bash
# Smart launcher for CELL-1: dual-SKU polling for B200:1 OR H100:2 SXM5.
#
# Polls Lambda API every 15s; the first SKU with capacity wins. Both fit
# Llama-3.1-70B at fp16:
#   - B200 1x (180 GB VRAM): single-GPU native fit; cheaper ($6.99/h); newer arch
#   - H100:2 SXM5 (160 GB total): multi-GPU shard; well-tested path
#
# Priority order: B200 first (cheaper + simpler single-GPU), then H100:2.
#
# Same hardening as smart_launch_cloud_1.sh:
#   - PID-file lock /tmp/smart_launch_cell1.pid (duplicate invocations REFUSE)
#   - TRAP cleanup_on_exit (rm lock + pkill -P own children)
#   - Pre-flight gate called BEFORE sky launch on BOTH YAMLs
#
# Per [[cloud-dispatch-pre-flight-checklist]] (2026-06-06 lesson).
set -uo pipefail

source /root/skyvenv/bin/activate

# PID-file lock so duplicate smart_launch_cell1 invocations REFUSE.
LOCKFILE=/tmp/smart_launch_cell1.pid
if [ -f "$LOCKFILE" ]; then
  OLD_PID=$(cat "$LOCKFILE" 2>/dev/null || echo "")
  if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
    echo "ERROR: another smart_launch_cell1.sh is already running (PID=$OLD_PID)."
    echo "       Kill it first: kill -9 $OLD_PID"
    exit 1
  fi
fi
echo $$ > "$LOCKFILE"
cleanup_on_exit() {
  rm -f "$LOCKFILE"
  pkill -P $$ 2>/dev/null || true
}
trap cleanup_on_exit EXIT INT TERM

# Pre-flight gate on BOTH YAMLs (B200 + H100:2) before we even start polling.
EXPECTED_SCRIPT="exp_substrate_extraction_quality_70B_fp16_disambiguation_v1.py"
BUNDLE_PATH="/root/cell1-ship"
echo "[smart_launch_cell1] running pre-flight gate on BOTH YAMLs..."
for yaml in "${BUNDLE_PATH}/skypilot/cell1_70b_b200x1.yaml" "${BUNDLE_PATH}/skypilot/cell1_70b_fp16.yaml"; do
  if ! bash /mnt/d/AI/hd-instrument/skypilot/preflight_cloud_dispatch.sh \
        "$yaml" "$EXPECTED_SCRIPT" "$BUNDLE_PATH"; then
    echo "ERROR: preflight FAILED on $yaml; dispatch refused."
    exit 1
  fi
done

HF_TOKEN_VAL="$(cat /mnt/d/AI/hd-instrument/.hf_token)"
if [ -z "${HF_TOKEN_VAL}" ]; then
  echo "ERROR: HF token empty"; exit 1
fi

LOG=/mnt/d/AI/hd-instrument/data/cell1_smart_launch.log
mkdir -p "$(dirname "$LOG")"

echo "===== CELL-1 smart launch start $(date -u '+%Y-%m-%dT%H:%M:%SZ') =====" | tee -a "$LOG"
echo "HF_TOKEN length: ${#HF_TOKEN_VAL} chars; prefix: ${HF_TOKEN_VAL:0:5}..." | tee -a "$LOG"
echo "lock file: $LOCKFILE (PID $$)" | tee -a "$LOG"

# Parse Lambda API key
API_KEY=$(grep -oP 'api_key\s*=\s*\K\S+' /root/.lambda_cloud/lambda_keys 2>/dev/null | head -1)
if [ -z "$API_KEY" ]; then
  echo "ERROR: could not parse Lambda API key" | tee -a "$LOG"
  exit 1
fi
echo "api key parsed (len=${#API_KEY})" | tee -a "$LOG"

# Returns "SKU REGION" if any of our target SKUs have capacity.
# Priority order: B200 first (cheaper $6.99/h + single-GPU simplicity), then H100:2.
#
# REGION FILTER: Lambda API may report capacity in regions SkyPilot's catalog
# doesn't know about (e.g. us-southeast-1 spotted 2026-06-06). Filter to a
# safe known-set so sky launch doesn't error on "Invalid region".
query_first_available() {
  local api_json
  api_json=$(curl -s -u "${API_KEY}:" https://cloud.lambdalabs.com/api/v1/instance-types 2>/dev/null)
  python3 - <<EOF
import json, sys
try:
    d = json.loads('''$api_json''')
except Exception:
    sys.exit(1)
SKYPILOT_KNOWN_LAMBDA_REGIONS = {
    # Derived from /root/.sky/catalogs/v8/lambda/vms.csv after the
    # us-southeast-1 catalog patch (commit 365342c successor).
    'us-east-1', 'us-east-2', 'us-east-3',
    'us-west-1', 'us-west-2', 'us-west-3',
    'us-south-1', 'us-south-2', 'us-south-3',
    'us-midwest-1', 'us-southeast-1',
    'asia-northeast-1', 'asia-northeast-2', 'asia-south-1',
    'australia-east-1', 'europe-central-1', 'europe-south-1', 'me-west-1',
}
data = d.get('data', {})
for sku in ['gpu_1x_b200_sxm6', 'gpu_2x_h100_sxm5']:
    regs_all = [r['name'] for r in data.get(sku, {}).get('regions_with_capacity_available', [])]
    # Filter to SkyPilot-known
    regs = [r for r in regs_all if r in SKYPILOT_KNOWN_LAMBDA_REGIONS]
    if regs:
        print(f"{sku} {regs[0]}")
        sys.exit(0)
    elif regs_all:
        # Capacity exists but only in SkyPilot-unknown regions; log to stderr
        print(f"SKU {sku} has capacity in unknown-to-SkyPilot regions {regs_all}; skipping", file=sys.stderr)
sys.exit(1)
EOF
}

yaml_for_sku() {
  case "$1" in
    gpu_1x_b200_sxm6)  echo "skypilot/cell1_70b_b200x1.yaml" ;;
    gpu_2x_h100_sxm5)  echo "skypilot/cell1_70b_fp16.yaml" ;;
    *)                  echo "" ;;
  esac
}

gpus_for_sku() {
  case "$1" in
    gpu_1x_b200_sxm6)  echo "B200:1" ;;
    gpu_2x_h100_sxm5)  echo "H100:2" ;;
    *)                  echo "" ;;
  esac
}

POLL_INTERVAL=15
MAX_ATTEMPTS=2880   # 12 hours @ 15s = 2880 (long enough for H100 fleet recovery)
attempt=0
CLUSTER_NAME=""

cd "$BUNDLE_PATH"

while [ "$attempt" -lt "$MAX_ATTEMPTS" ]; do
  attempt=$((attempt + 1))
  ts=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

  AVAIL=$(query_first_available 2>/dev/null || true)
  if [ -z "$AVAIL" ]; then
    if [ $((attempt % 20)) -eq 1 ]; then
      # Log every 20th attempt (every 5 min) to keep log size sane
      echo "[${ts}] attempt=${attempt}/${MAX_ATTEMPTS} no B200/H100:2 capacity; polling every ${POLL_INTERVAL}s" | tee -a "$LOG"
    fi
    sleep "$POLL_INTERVAL"
    continue
  fi

  SKU=$(echo "$AVAIL" | awk '{print $1}')
  REGION=$(echo "$AVAIL" | awk '{print $2}')
  CLUSTER_NAME="cell170b-$(date +%H%M%S)"
  YAML_FILE=$(yaml_for_sku "$SKU")
  GPUS_SPEC=$(gpus_for_sku "$SKU")

  if [ -z "$YAML_FILE" ] || [ -z "$GPUS_SPEC" ]; then
    echo "[${ts}] ERROR: unknown SKU '$SKU'; skipping" | tee -a "$LOG"
    sleep "$POLL_INTERVAL"
    continue
  fi

  echo "[${ts}] attempt=${attempt} CAPACITY DETECTED: sku=${SKU} region=${REGION} gpus=${GPUS_SPEC} yaml=${YAML_FILE}" | tee -a "$LOG"
  echo "[${ts}] launching cluster=${CLUSTER_NAME}" | tee -a "$LOG"

  # CRITICAL DUPLICATION DEFENSE: terminate any existing cell170b-* clusters
  # AND any existing Lambda instances of our target type BEFORE we launch.
  # This is the 2026-06-06 zombie-process lesson.
  EXISTING_CELL_CLUSTERS=$(sky status 2>/dev/null | grep -oE 'cell170b-[0-9]+' | sort -u || true)
  if [ -n "$EXISTING_CELL_CLUSTERS" ]; then
    echo "[${ts}] WARN: found existing cell170b clusters in sky status; tearing down first" | tee -a "$LOG"
    echo "$EXISTING_CELL_CLUSTERS" | xargs -r sky down -y 2>&1 | tail -5 | tee -a "$LOG"
  fi

  # NO --retry-until-up: single-shot, fail fast on race loss.
  # CLI overrides --region + --instance-type pin the spec.
  sky launch \
      -c "$CLUSTER_NAME" \
      -y \
      --region "$REGION" \
      --instance-type "$SKU" \
      --gpus "$GPUS_SPEC" \
      --down \
      -i 30 \
      --env HF_TOKEN="${HF_TOKEN_VAL}" \
      "$YAML_FILE" 2>&1 | tee -a "$LOG"

  LAUNCH_RC=${PIPESTATUS[0]}
  echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] sky launch exit code: ${LAUNCH_RC}" | tee -a "$LOG"

  if [ "${LAUNCH_RC}" -eq 0 ]; then
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] CELL-1 ACQUIRED + RAN on ${SKU} in ${REGION}" | tee -a "$LOG"
    break
  fi

  echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] launch failed (probably lost the race); cleaning up + retrying" | tee -a "$LOG"
  sky down -y "$CLUSTER_NAME" 2>&1 | tee -a "$LOG" || true
  CLUSTER_NAME=""
  sleep "$POLL_INTERVAL"
done

if [ -z "$CLUSTER_NAME" ]; then
  echo "===== CELL-1 smart launch FAILED after ${MAX_ATTEMPTS} attempts $(date -u '+%Y-%m-%dT%H:%M:%SZ') =====" | tee -a "$LOG"
  exit 1
fi

# Post-acquisition: final rsync + teardown + verify
echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] SCPing CELL-1 metrics back from ${CLUSTER_NAME}" | tee -a "$LOG"
LOCAL_DIR=/mnt/d/AI/hd-instrument/data/cell1_results
mkdir -p "${LOCAL_DIR}"
rsync -av --partial \
  -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR" \
  "${CLUSTER_NAME}:~/sky_workdir/data/exp_substrate_extraction_quality_70B_fp16_disambiguation_v1/" \
  "${LOCAL_DIR}/" 2>&1 | tee -a "$LOG" || true

echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] sky down ${CLUSTER_NAME} (belt-and-suspenders)" | tee -a "$LOG"
sky down -y "${CLUSTER_NAME}" 2>&1 | tee -a "$LOG" || true

echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] verify no orphan Lambda instances" | tee -a "$LOG"
bash /mnt/d/AI/hd-instrument/skypilot/verify_no_lambda_instances.sh 2>&1 | tee -a "$LOG" || true

echo "===== CELL-1 smart launch end $(date -u '+%Y-%m-%dT%H:%M:%SZ') =====" | tee -a "$LOG"
exit 0
