#!/usr/bin/env bash
# Smart launcher for 70B-Instruct NF4 follow-up.
#
# Dual-SKU polling (NF4 fits in any 1xGPU 80GB+):
#   priority 1: GH200:1 ($2.29/h; 96 GB; aarch64; uses _gh200 YAML with cu128 install)
#   priority 2: H100:1 SXM5 / PCIe ($3.29-4.29/h; 80 GB; x86; uses _h100x1 YAML with cu121)
#   NOT considered: A100 40 GB (tight for NF4 + activations; not worth the risk)
#   NOT considered: H100:2 SXM5 (overkill cost for NF4-only run)
#
# Same hardening as smart_launch_cell1.sh:
#   - PID-file lock /tmp/smart_launch_instruct.pid
#   - TRAP cleanup_on_exit
#   - Preflight gate on BOTH YAMLs
#   - SkyPilot-known region filter (avoid us-southeast-1 stale-catalog issue)
#   - sky api stop before first launch (flush stale catalog cache)
#   - Cluster-name-collision teardown before each launch
set -uo pipefail

source /root/skyvenv/bin/activate

# PID-file lock so duplicate smart_launch_instruct invocations REFUSE.
LOCKFILE=/tmp/smart_launch_instruct.pid
if [ -f "$LOCKFILE" ]; then
  OLD_PID=$(cat "$LOCKFILE" 2>/dev/null || echo "")
  if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
    echo "ERROR: another smart_launch_instruct.sh is already running (PID=$OLD_PID)."
    exit 1
  fi
fi
echo $$ > "$LOCKFILE"
cleanup_on_exit() {
  rm -f "$LOCKFILE"
  pkill -P $$ 2>/dev/null || true
}
trap cleanup_on_exit EXIT INT TERM

# Pre-flight gate on BOTH YAMLs.
EXPECTED_SCRIPT="exp_substrate_extraction_quality_70B_instruct_nf4_v1.py"
BUNDLE_PATH="/root/instruct-ship"
echo "[smart_launch_instruct] running pre-flight gate on BOTH YAMLs..."
for yaml in "${BUNDLE_PATH}/skypilot/instruct_70b_nf4_gh200.yaml" "${BUNDLE_PATH}/skypilot/instruct_70b_nf4_h100x1.yaml"; do
  if ! bash /mnt/d/AI/hd-instrument/skypilot/preflight_cloud_dispatch.sh \
        "$yaml" "$EXPECTED_SCRIPT" "$BUNDLE_PATH"; then
    echo "ERROR: preflight FAILED on $yaml; dispatch refused."
    exit 1
  fi
done

# SkyPilot API server cache flush: required if any catalog patches happened in
# this session. Idempotent + cheap.
echo "[smart_launch_instruct] flushing SkyPilot API server (catalog cache)..."
sky api stop 2>&1 | tail -3 || true

HF_TOKEN_VAL="$(cat /mnt/d/AI/hd-instrument/.hf_token)"
if [ -z "${HF_TOKEN_VAL}" ]; then
  echo "ERROR: HF token empty"; exit 1
fi

LOG=/mnt/d/AI/hd-instrument/data/instruct_smart_launch.log
mkdir -p "$(dirname "$LOG")"

echo "===== Instruct smart launch start $(date -u '+%Y-%m-%dT%H:%M:%SZ') =====" | tee -a "$LOG"
echo "HF_TOKEN length: ${#HF_TOKEN_VAL} chars; prefix: ${HF_TOKEN_VAL:0:5}..." | tee -a "$LOG"
echo "lock file: $LOCKFILE (PID $$)" | tee -a "$LOG"

API_KEY=$(grep -oP 'api_key\s*=\s*\K\S+' /root/.lambda_cloud/lambda_keys 2>/dev/null | head -1)
if [ -z "$API_KEY" ]; then
  echo "ERROR: could not parse Lambda API key" | tee -a "$LOG"
  exit 1
fi
echo "api key parsed (len=${#API_KEY})" | tee -a "$LOG"

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
    'us-east-1', 'us-east-2', 'us-east-3',
    'us-west-1', 'us-west-2', 'us-west-3',
    'us-south-1', 'us-south-2', 'us-south-3',
    'us-midwest-1', 'us-southeast-1',
    'asia-northeast-1', 'asia-northeast-2', 'asia-south-1',
    'australia-east-1', 'europe-central-1', 'europe-south-1', 'me-west-1',
}
data = d.get('data', {})
# Priority order: GH200 (cheap + single-GPU + big VRAM), then H100 (x86 fallback)
for sku in ['gpu_1x_gh200', 'gpu_1x_h100_sxm5', 'gpu_1x_h100_pcie']:
    regs_all = [r['name'] for r in data.get(sku, {}).get('regions_with_capacity_available', [])]
    regs = [r for r in regs_all if r in SKYPILOT_KNOWN_LAMBDA_REGIONS]
    if regs:
        print(f"{sku} {regs[0]}")
        sys.exit(0)
    elif regs_all:
        print(f"SKU {sku} has capacity in unknown-to-SkyPilot regions {regs_all}; skipping", file=sys.stderr)
sys.exit(1)
EOF
}

yaml_for_sku() {
  case "$1" in
    gpu_1x_gh200)         echo "skypilot/instruct_70b_nf4_gh200.yaml" ;;
    gpu_1x_h100_sxm5)     echo "skypilot/instruct_70b_nf4_h100x1.yaml" ;;
    gpu_1x_h100_pcie)     echo "skypilot/instruct_70b_nf4_h100x1.yaml" ;;
    *)                    echo "" ;;
  esac
}

gpus_for_sku() {
  case "$1" in
    gpu_1x_gh200)         echo "GH200:1" ;;
    gpu_1x_h100_sxm5)     echo "H100:1" ;;
    gpu_1x_h100_pcie)     echo "H100:1" ;;
    *)                    echo "" ;;
  esac
}

POLL_INTERVAL=15
MAX_ATTEMPTS=2880  # 12h max
attempt=0
CLUSTER_NAME=""

cd "$BUNDLE_PATH"

while [ "$attempt" -lt "$MAX_ATTEMPTS" ]; do
  attempt=$((attempt + 1))
  ts=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

  AVAIL=$(query_first_available 2>/dev/null || true)
  if [ -z "$AVAIL" ]; then
    if [ $((attempt % 20)) -eq 1 ]; then
      echo "[${ts}] attempt=${attempt}/${MAX_ATTEMPTS} no GH200/H100:1 capacity; polling every ${POLL_INTERVAL}s" | tee -a "$LOG"
    fi
    sleep "$POLL_INTERVAL"
    continue
  fi

  SKU=$(echo "$AVAIL" | awk '{print $1}')
  REGION=$(echo "$AVAIL" | awk '{print $2}')
  CLUSTER_NAME="instruct70b-$(date +%H%M%S)"
  YAML_FILE=$(yaml_for_sku "$SKU")
  GPUS_SPEC=$(gpus_for_sku "$SKU")

  if [ -z "$YAML_FILE" ] || [ -z "$GPUS_SPEC" ]; then
    echo "[${ts}] ERROR: unknown SKU '$SKU'; skipping" | tee -a "$LOG"
    sleep "$POLL_INTERVAL"
    continue
  fi

  echo "[${ts}] attempt=${attempt} CAPACITY DETECTED: sku=${SKU} region=${REGION} gpus=${GPUS_SPEC} yaml=${YAML_FILE}" | tee -a "$LOG"
  echo "[${ts}] launching cluster=${CLUSTER_NAME}" | tee -a "$LOG"

  EXISTING_CLUSTERS=$(sky status 2>/dev/null | grep -oE 'instruct70b-[0-9]+' | sort -u || true)
  if [ -n "$EXISTING_CLUSTERS" ]; then
    echo "[${ts}] WARN: existing instruct70b clusters in sky status; tearing down first" | tee -a "$LOG"
    echo "$EXISTING_CLUSTERS" | xargs -r sky down -y 2>&1 | tail -5 | tee -a "$LOG"
  fi

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
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] Instruct ACQUIRED + RAN on ${SKU} in ${REGION}" | tee -a "$LOG"
    break
  fi

  echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] launch failed; cleaning up + retrying" | tee -a "$LOG"
  sky down -y "$CLUSTER_NAME" 2>&1 | tee -a "$LOG" || true
  CLUSTER_NAME=""
  sleep "$POLL_INTERVAL"
done

if [ -z "$CLUSTER_NAME" ]; then
  echo "===== Instruct smart launch FAILED after ${MAX_ATTEMPTS} attempts $(date -u '+%Y-%m-%dT%H:%M:%SZ') =====" | tee -a "$LOG"
  exit 1
fi

# Post-acquisition: rsync + teardown + verify
echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] SCPing Instruct metrics back from ${CLUSTER_NAME}" | tee -a "$LOG"
LOCAL_DIR=/mnt/d/AI/hd-instrument/data/instruct_results
mkdir -p "${LOCAL_DIR}"
rsync -av --partial \
  -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR" \
  "${CLUSTER_NAME}:~/sky_workdir/data/exp_substrate_extraction_quality_70B_instruct_nf4_v1/" \
  "${LOCAL_DIR}/" 2>&1 | tee -a "$LOG" || true

echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] sky down ${CLUSTER_NAME}" | tee -a "$LOG"
sky down -y "${CLUSTER_NAME}" 2>&1 | tee -a "$LOG" || true

echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] verify no orphan Lambda instances" | tee -a "$LOG"
bash /mnt/d/AI/hd-instrument/skypilot/verify_no_lambda_instances.sh 2>&1 | tee -a "$LOG" || true

echo "===== Instruct smart launch end $(date -u '+%Y-%m-%dT%H:%M:%SZ') =====" | tee -a "$LOG"
exit 0
