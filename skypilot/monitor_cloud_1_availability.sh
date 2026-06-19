#!/usr/bin/env bash
# Parallel Lambda H100 availability + sky launch health poller.
# Polls every 5 min; writes single-line status to data/cloud_1_availability.log.
# Exits when H100 capacity returns (so the user knows sky launch will proceed).
set +e

LOG=/mnt/d/AI/hd-instrument/data/cloud_1_availability.log
INTERVAL=${INTERVAL:-300}   # 5 min default
MAX_CHECKS=${MAX_CHECKS:-72}  # 6h cap

mkdir -p "$(dirname "$LOG")"
echo "===== availability monitor start $(date -u '+%Y-%m-%dT%H:%M:%SZ') interval=${INTERVAL}s max_checks=${MAX_CHECKS} =====" >> "$LOG"

source /root/skyvenv/bin/activate 2>/dev/null

# Parse API key from /root/.lambda_cloud/lambda_keys
API_KEY=$(grep -oP 'api_key\s*=\s*\K\S+' /root/.lambda_cloud/lambda_keys 2>/dev/null | head -1)
if [ -z "$API_KEY" ]; then
  echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] ERROR: could not parse api_key from lambda_keys" >> "$LOG"
  exit 1
fi
echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] api key parsed (len=${#API_KEY})" >> "$LOG"

i=0
while [ "$i" -lt "$MAX_CHECKS" ]; do
  i=$((i + 1))
  ts=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

  # Sky cluster health
  cluster_line=$(sky status 2>/dev/null | grep -E '^cloud1quality(-[0-9]+)?[[:space:]]' | head -1)
  CLUSTER=$(echo "$cluster_line" | awk '{print $1}')
  state=$(echo "$cluster_line" | grep -oE '\b(INIT|UP|STOPPED|TERMINATING|TERMINATED)\b' | head -1)
  cluster_status="cluster=${CLUSTER:-NONE} state=${state:-NONE}"

  # Lambda H100 availability
  api_json=$(curl -s -u "${API_KEY}:" https://cloud.lambdalabs.com/api/v1/instance-types 2>/dev/null)
  avail_summary=$(python3 -c "
import json, sys
try:
    d = json.loads(sys.stdin.read())
    data = d.get('data', {})
    h100 = [k for k in data if 'h100' in k.lower()]
    out = []
    any_h100 = False
    for sku in h100:
        regs = [r['name'] for r in data[sku].get('regions_with_capacity_available', [])]
        if regs:
            any_h100 = True
            out.append(f'{sku}={regs}')
    if not any_h100:
        print('ZERO_H100')
    else:
        print('|'.join(out))
except Exception as e:
    print(f'ERR:{type(e).__name__}:{str(e)[:50]}')
" <<< "$api_json")

  echo "[${ts}] check=${i}/${MAX_CHECKS} ${cluster_status} h100=${avail_summary}" >> "$LOG"

  # Exit early on H100 available (sky launch will pick it up)
  if [ "${avail_summary}" != "ZERO_H100" ] && [[ "${avail_summary}" != ERR:* ]]; then
    echo "[${ts}] H100 AVAILABLE; sky --retry-until-up should acquire on next 30s cycle. Monitor exiting." >> "$LOG"
    break
  fi

  # Exit if cluster gone (sky launch ended; nothing more to monitor)
  if [ "${state}" = "TERMINATED" ] || [ "${state}" = "STOPPED" ]; then
    echo "[${ts}] cluster ${state}; sky launch ended. Monitor exiting." >> "$LOG"
    break
  fi

  sleep "${INTERVAL}"
done

echo "===== availability monitor end $(date -u '+%Y-%m-%dT%H:%M:%SZ') (total_checks=${i}) =====" >> "$LOG"
