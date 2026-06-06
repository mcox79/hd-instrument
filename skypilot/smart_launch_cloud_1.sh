#!/usr/bin/env bash
# Smart launcher for CLOUD-1: polls Lambda API directly for H100 capacity,
# then targets sky launch with --region + --instance-type CLI overrides so
# we go DIRECTLY to where capacity is (no blind cycling, no race vs other
# claimants who get there before SkyPilot's slow optimizer rotates).
#
# Replaces launch_cloud_1.sh (which uses --retry-until-up's blind cycle).
#
# Loop until acquisition or 60-min max:
#   1. Query Lambda API for first available (SKU, region) -- prefer PCIe (cheaper)
#   2. If none: sleep 15s, retry
#   3. If found: sky launch -y --region X --instance-type Y skypilot/cloud_1_quality_binding.yaml
#   4. If launch succeeds -> do final rsync + sky down + verify; exit 0
#   5. If launch fails (lost the race): clean up cluster + back to step 1
#
# Logs to data/cloud_1_smart_launch.log.
#
# Run from WSL Ubuntu:
#   bash /mnt/d/AI/hd-instrument/skypilot/smart_launch_cloud_1.sh
set -uo pipefail

source /root/skyvenv/bin/activate

HF_TOKEN_VAL="$(cat /mnt/d/AI/hd-instrument/.hf_token)"
if [ -z "${HF_TOKEN_VAL}" ]; then
  echo "ERROR: HF token at /mnt/d/AI/hd-instrument/.hf_token is empty"
  exit 1
fi

LOG=/mnt/d/AI/hd-instrument/data/cloud_1_smart_launch.log
mkdir -p "$(dirname "$LOG")"

echo "===== smart launch start $(date -u '+%Y-%m-%dT%H:%M:%SZ') =====" | tee -a "$LOG"
echo "HF_TOKEN length: ${#HF_TOKEN_VAL} chars; prefix: ${HF_TOKEN_VAL:0:5}..." | tee -a "$LOG"

# Parse API key once
API_KEY=$(grep -oP 'api_key\s*=\s*\K\S+' /root/.lambda_cloud/lambda_keys 2>/dev/null | head -1)
if [ -z "$API_KEY" ]; then
  echo "ERROR: could not parse api_key from /root/.lambda_cloud/lambda_keys" | tee -a "$LOG"
  exit 1
fi
echo "api key parsed (len=${#API_KEY})" | tee -a "$LOG"

# Returns "SKU REGION" on stdout if any H100 capacity available.
# Prefers PCIe (cheaper); falls back to SXM5. First region in the list wins.
query_first_available() {
  local api_json
  api_json=$(curl -s -u "${API_KEY}:" https://cloud.lambdalabs.com/api/v1/instance-types 2>/dev/null)
  python3 - <<EOF
import json, sys
try:
    d = json.loads('''$api_json''')
except Exception:
    sys.exit(1)
data = d.get('data', {})
for sku in ['gpu_1x_h100_pcie', 'gpu_1x_h100_sxm5']:
    regs = [r['name'] for r in data.get(sku, {}).get('regions_with_capacity_available', [])]
    if regs:
        print(f"{sku} {regs[0]}")
        sys.exit(0)
sys.exit(1)
EOF
}

POLL_INTERVAL=15
MAX_ATTEMPTS=240   # 60 min @ 15s = 240
attempt=0
CLUSTER_NAME=""

while [ "$attempt" -lt "$MAX_ATTEMPTS" ]; do
  attempt=$((attempt + 1))
  ts=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

  AVAIL=$(query_first_available 2>/dev/null || true)
  if [ -z "$AVAIL" ]; then
    echo "[${ts}] attempt=${attempt}/${MAX_ATTEMPTS} no H100 capacity; sleeping ${POLL_INTERVAL}s" | tee -a "$LOG"
    sleep "$POLL_INTERVAL"
    continue
  fi

  SKU=$(echo "$AVAIL" | awk '{print $1}')
  REGION=$(echo "$AVAIL" | awk '{print $2}')
  CLUSTER_NAME="cloud1quality-$(date +%H%M%S)"

  echo "[${ts}] attempt=${attempt} CAPACITY DETECTED: sku=${SKU} region=${REGION}" | tee -a "$LOG"
  echo "[${ts}] launching cluster=${CLUSTER_NAME} with --region ${REGION} --instance-type ${SKU}" | tee -a "$LOG"

  cd /root/cloud-1-ship
  # NO --retry-until-up: single-shot, fail fast on race loss.
  # CLI overrides --region + --instance-type pin the spec, bypassing YAML any_of optimizer cycle.
  sky launch \
      -c "$CLUSTER_NAME" \
      -y \
      --region "$REGION" \
      --instance-type "$SKU" \
      --gpus H100:1 \
      --down \
      -i 30 \
      --env HF_TOKEN="${HF_TOKEN_VAL}" \
      skypilot/cloud_1_smart.yaml 2>&1 | tee -a "$LOG"

  LAUNCH_RC=${PIPESTATUS[0]}
  echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] sky launch exit code: ${LAUNCH_RC}" | tee -a "$LOG"

  if [ "${LAUNCH_RC}" -eq 0 ]; then
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] ACQUIRED + RAN successfully" | tee -a "$LOG"
    break
  fi

  echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] launch failed (probably lost the race); cleaning up cluster + retrying" | tee -a "$LOG"
  sky down -y "$CLUSTER_NAME" 2>&1 | tee -a "$LOG" || true
  CLUSTER_NAME=""
  sleep "$POLL_INTERVAL"
done

if [ -z "$CLUSTER_NAME" ]; then
  echo "===== smart launch FAILED to acquire after ${MAX_ATTEMPTS} attempts ($(date -u '+%Y-%m-%dT%H:%M:%SZ')) =====" | tee -a "$LOG"
  exit 1
fi

# Post-acquisition: final rsync + teardown + verify
echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] SCPing results back from ${CLUSTER_NAME}" | tee -a "$LOG"
LOCAL_DIR=/mnt/d/AI/hd-instrument/data/cloud_1_results
mkdir -p "${LOCAL_DIR}"
rsync -av --partial \
  -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR" \
  "${CLUSTER_NAME}:~/sky_workdir/data/exp_substrate_extraction_quality_7B_vs_70B_v1/" \
  "${LOCAL_DIR}/" 2>&1 | tee -a "$LOG" || \
  echo "  [warn] final rsync returned non-zero; will retry via watcher" | tee -a "$LOG"

echo "" | tee -a "$LOG"
echo "=== NEXT STEP (run from Windows PowerShell): laptop -> marsh@home ===" | tee -a "$LOG"
cat <<MARSHEOF | tee -a "$LOG"
ssh marsh@home "if not exist C:\dev\hd-instrument\data\exp_substrate_extraction_quality_7B_vs_70B_v1 mkdir C:\dev\hd-instrument\data\exp_substrate_extraction_quality_7B_vs_70B_v1"
scp D:\AI\hd-instrument\data\cloud_1_results\metrics.json \
    "marsh@home:C:/dev/hd-instrument/data/exp_substrate_extraction_quality_7B_vs_70B_v1/"
MARSHEOF

echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] sky down ${CLUSTER_NAME} (belt-and-suspenders)" | tee -a "$LOG"
sky down -y "${CLUSTER_NAME}" 2>&1 | tee -a "$LOG" || \
  echo "  [warn] sky down returned non-zero" | tee -a "$LOG"

echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] verify no orphan Lambda instances" | tee -a "$LOG"
bash /mnt/d/AI/hd-instrument/skypilot/verify_no_lambda_instances.sh 2>&1 | tee -a "$LOG" || \
  echo "  [warn] verify_no_lambda_instances.sh returned non-zero" | tee -a "$LOG"

echo "===== smart launch end $(date -u '+%Y-%m-%dT%H:%M:%SZ') =====" | tee -a "$LOG"
exit 0
