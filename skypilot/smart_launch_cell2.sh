#!/usr/bin/env bash
# Smart launcher for CELL-2 Wikipedia layer-15 cache extraction.
#
# Target SKU: GH200 1x (user explicit; cheapest viable; proven via CLOUD-1b + 70B-Instruct).
# Region cycling via SkyPilot-known set. PID lock + TRAP + preflight gate + sky api stop.
set -uo pipefail

source /root/skyvenv/bin/activate

LOCKFILE=/tmp/smart_launch_cell2.pid
if [ -f "$LOCKFILE" ]; then
  OLD_PID=$(cat "$LOCKFILE" 2>/dev/null || echo "")
  if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
    echo "ERROR: another smart_launch_cell2.sh is already running (PID=$OLD_PID)."
    exit 1
  fi
fi
echo $$ > "$LOCKFILE"
cleanup_on_exit() {
  rm -f "$LOCKFILE"
  pkill -P $$ 2>/dev/null || true
}
trap cleanup_on_exit EXIT INT TERM

EXPECTED_SCRIPT="exp_substrate_wikipedia_layer15_cache_extraction_v1.py"
BUNDLE_PATH="/root/cell2-ship"
echo "[smart_launch_cell2] running pre-flight gate..."
if ! bash /mnt/d/AI/hd-instrument/skypilot/preflight_cloud_dispatch.sh \
      "${BUNDLE_PATH}/skypilot/cell2_wiki_gh200.yaml" "$EXPECTED_SCRIPT" "$BUNDLE_PATH"; then
  echo "ERROR: preflight FAILED; dispatch refused."
  exit 1
fi

echo "[smart_launch_cell2] flushing SkyPilot API server (catalog cache)..."
sky api stop 2>&1 | tail -3 || true

HF_TOKEN_VAL="$(cat /mnt/d/AI/hd-instrument/.hf_token)"
if [ -z "${HF_TOKEN_VAL}" ]; then
  echo "ERROR: HF token empty"; exit 1
fi

LOG=/mnt/d/AI/hd-instrument/data/cell2_smart_launch.log
mkdir -p "$(dirname "$LOG")"

echo "===== CELL-2 smart launch start $(date -u '+%Y-%m-%dT%H:%M:%SZ') =====" | tee -a "$LOG"
echo "HF_TOKEN length: ${#HF_TOKEN_VAL} chars; prefix: ${HF_TOKEN_VAL:0:5}..." | tee -a "$LOG"
echo "lock file: $LOCKFILE (PID $$)" | tee -a "$LOG"

API_KEY=$(grep -oP 'api_key\s*=\s*\K\S+' /root/.lambda_cloud/lambda_keys 2>/dev/null | head -1)
if [ -z "$API_KEY" ]; then
  echo "ERROR: could not parse Lambda API key" | tee -a "$LOG"
  exit 1
fi
echo "api key parsed (len=${#API_KEY})" | tee -a "$LOG"

# Poll Lambda API for GH200 1x capacity (SkyPilot-known regions only)
query_first_available() {
  local api_json
  api_json=$(curl -s -u "${API_KEY}:" https://cloud.lambdalabs.com/api/v1/instance-types 2>/dev/null)
  python3 - <<EOF
import json, sys
try:
    d = json.loads('''$api_json''')
except Exception:
    sys.exit(1)
SK = {
    'us-east-1', 'us-east-2', 'us-east-3',
    'us-west-1', 'us-west-2', 'us-west-3',
    'us-south-1', 'us-south-2', 'us-south-3',
    'us-midwest-1', 'us-southeast-1',
    'asia-northeast-1', 'asia-northeast-2', 'asia-south-1',
    'australia-east-1', 'europe-central-1', 'europe-south-1', 'me-west-1',
}
data = d.get('data', {})
sku = 'gpu_1x_gh200'
regs_all = [r['name'] for r in data.get(sku, {}).get('regions_with_capacity_available', [])]
regs = [r for r in regs_all if r in SK]
if regs:
    print(f"{sku} {regs[0]}")
    sys.exit(0)
elif regs_all:
    print(f"SKU {sku} has capacity in unknown-to-SkyPilot regions {regs_all}; skipping", file=sys.stderr)
sys.exit(1)
EOF
}

POLL_INTERVAL=15
MAX_ATTEMPTS=2880   # 12h
attempt=0
CLUSTER_NAME=""

cd "$BUNDLE_PATH"

while [ "$attempt" -lt "$MAX_ATTEMPTS" ]; do
  attempt=$((attempt + 1))
  ts=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

  AVAIL=$(query_first_available 2>/dev/null || true)
  if [ -z "$AVAIL" ]; then
    if [ $((attempt % 20)) -eq 1 ]; then
      echo "[${ts}] attempt=${attempt}/${MAX_ATTEMPTS} no GH200 capacity; polling every ${POLL_INTERVAL}s" | tee -a "$LOG"
    fi
    sleep "$POLL_INTERVAL"
    continue
  fi

  SKU=$(echo "$AVAIL" | awk '{print $1}')
  REGION=$(echo "$AVAIL" | awk '{print $2}')
  CLUSTER_NAME="cell2wiki-$(date +%H%M%S)"

  echo "[${ts}] attempt=${attempt} CAPACITY DETECTED: sku=${SKU} region=${REGION}" | tee -a "$LOG"
  echo "[${ts}] launching cluster=${CLUSTER_NAME}" | tee -a "$LOG"

  EXISTING_CLUSTERS=$(sky status 2>/dev/null | grep -oE 'cell2wiki-[0-9]+' | sort -u || true)
  if [ -n "$EXISTING_CLUSTERS" ]; then
    echo "[${ts}] WARN: existing cell2wiki clusters; tearing down" | tee -a "$LOG"
    echo "$EXISTING_CLUSTERS" | xargs -r sky down -y 2>&1 | tail -5 | tee -a "$LOG"
  fi

  sky launch \
      -c "$CLUSTER_NAME" \
      -y \
      --region "$REGION" \
      --instance-type "$SKU" \
      --gpus "GH200:1" \
      --down \
      -i 30 \
      --env HF_TOKEN="${HF_TOKEN_VAL}" \
      "skypilot/cell2_wiki_gh200.yaml" 2>&1 | tee -a "$LOG"

  LAUNCH_RC=${PIPESTATUS[0]}
  echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] sky launch exit code: ${LAUNCH_RC}" | tee -a "$LOG"

  # HARDENING (2026-06-07): sky launch streams logs over SSH. If SSH drops mid-run,
  # sky launch exits non-zero even though the workload keeps running. NEVER teardown
  # the cluster on a non-zero exit -- first verify if the cluster is still UP and
  # the job still progressing. Reattach with sky logs --follow as many times as
  # needed until the job truly finishes.
  if [ "${LAUNCH_RC}" -ne 0 ]; then
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] sky launch exit non-zero; checking cluster + job status before any teardown" | tee -a "$LOG"

    REATTACH_RETRIES=0
    while [ "$REATTACH_RETRIES" -lt 200 ]; do  # ~200 SSH retries; covers many hours
      if sky status "$CLUSTER_NAME" 2>/dev/null | grep -qE "UP|INIT"; then
        echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] cluster ${CLUSTER_NAME} still UP -- reattaching via sky logs --follow (retry ${REATTACH_RETRIES})" | tee -a "$LOG"
        # Reattach to the latest job's log stream; blocks until job ends
        sky logs "$CLUSTER_NAME" 2>&1 | tee -a "$LOG"
        REATTACH_RC=${PIPESTATUS[0]}
        echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] sky logs exit: ${REATTACH_RC}" | tee -a "$LOG"

        # Verify job actually finished (queue is empty of RUNNING jobs)
        if sky queue "$CLUSTER_NAME" --skip-finished 2>/dev/null | grep -qE "RUNNING|PENDING"; then
          echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] job still running after sky logs returned -- SSH dropped again; retrying" | tee -a "$LOG"
          REATTACH_RETRIES=$((REATTACH_RETRIES + 1))
          sleep 15
          continue
        fi
        # Job is truly done; treat as success path
        LAUNCH_RC=0
        echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] job complete on ${CLUSTER_NAME} after ${REATTACH_RETRIES} reattach(es)" | tee -a "$LOG"
        break
      else
        echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] cluster ${CLUSTER_NAME} no longer UP -- genuine cluster failure; will retry from scratch" | tee -a "$LOG"
        break
      fi
    done
  fi

  if [ "${LAUNCH_RC}" -eq 0 ]; then
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] CELL-2 ACQUIRED + RAN on ${SKU} in ${REGION}" | tee -a "$LOG"
    break
  fi

  # Genuine cluster-level failure (cluster down + can't reattach). Only path that
  # tears down the cluster.
  echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] launch genuinely failed (cluster dead); cleanup + retry from scratch" | tee -a "$LOG"
  sky down -y "$CLUSTER_NAME" 2>&1 | tee -a "$LOG" || true
  CLUSTER_NAME=""
  sleep "$POLL_INTERVAL"
done

if [ -z "$CLUSTER_NAME" ]; then
  echo "===== CELL-2 smart launch FAILED after ${MAX_ATTEMPTS} attempts $(date -u '+%Y-%m-%dT%H:%M:%SZ') =====" | tee -a "$LOG"
  exit 1
fi

# Post-acquisition: rsync (large: ~26 GB shards) + teardown + verify
echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] SCPing CELL-2 metrics + shards back from ${CLUSTER_NAME}" | tee -a "$LOG"
LOCAL_DIR=/mnt/d/AI/hd-instrument/data/cell2_results
mkdir -p "${LOCAL_DIR}"
rsync -av --partial --progress \
  -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR" \
  "${CLUSTER_NAME}:~/sky_workdir/data/exp_substrate_wikipedia_layer15_cache_extraction_v1/" \
  "${LOCAL_DIR}/" 2>&1 | tee -a "$LOG" || true

echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] sky down ${CLUSTER_NAME}" | tee -a "$LOG"
sky down -y "${CLUSTER_NAME}" 2>&1 | tee -a "$LOG" || true

bash /mnt/d/AI/hd-instrument/skypilot/verify_no_lambda_instances.sh 2>&1 | tee -a "$LOG" || true

echo "===== CELL-2 smart launch end $(date -u '+%Y-%m-%dT%H:%M:%SZ') =====" | tee -a "$LOG"
exit 0
