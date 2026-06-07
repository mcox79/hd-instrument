#!/usr/bin/env bash
# Watchdog: emit comprehensive state every 30 seconds to a structured log.
# Captures Lambda API state, sky status, cluster's recent activity, cost estimate.
# Runs independently of the launcher; survives if launcher SSH drops.
set -uo pipefail

source /root/skyvenv/bin/activate

LOG=/mnt/d/AI/hd-instrument/data/cell2_watchdog.log
STATE_FILE=/mnt/d/AI/hd-instrument/data/cell2_state.json
INTERVAL=30
LAMBDA_API_KEY=$(grep -oP 'api_key\s*=\s*\K\S+' /root/.lambda_cloud/lambda_keys 2>/dev/null | head -1)

echo "===== watchdog start $(date -u '+%Y-%m-%dT%H:%M:%SZ') =====" | tee -a "$LOG"
echo "[watchdog] PID=$$; interval=${INTERVAL}s; log=${LOG}" | tee -a "$LOG"

START_TIME=$(date -u '+%s')

while true; do
  ts=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
  ts_epoch=$(date -u '+%s')
  uptime=$((ts_epoch - START_TIME))

  # 1. Lambda API direct probe
  LAMBDA_JSON=$(curl -sS --max-time 10 -u "${LAMBDA_API_KEY}:" \
    https://cloud.lambdalabs.com/api/v1/instances 2>/dev/null || echo '{"data":[]}')
  N_INST=$(echo "$LAMBDA_JSON" | python3 -c "import sys, json; d=json.load(sys.stdin); print(len(d.get('data',[])))" 2>/dev/null || echo "?")
  INST_SUMMARY=$(echo "$LAMBDA_JSON" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for i in d.get('data', []):
    print(f\"  - id={i.get('id','?')[:12]} type={i.get('instance_type', {}).get('name', '?')} status={i.get('status','?')} region={i.get('region', {}).get('name', '?')} ip={i.get('ip', 'n/a')}\")
" 2>/dev/null)

  # 2. sky status
  SKY_STATUS=$(sky status 2>/dev/null | grep -E "cell2wiki-[0-9]+|No existing" | head -5)
  SKY_CLUSTERS=$(sky status 2>/dev/null | grep -oE "cell2wiki-[0-9]+" | sort -u)

  # 3. Launcher process state
  LAUNCHER_PID=$(pgrep -f smart_launch_cell2.sh | head -1 || echo "")
  LAUNCHER_STATE="DEAD"
  if [ -n "$LAUNCHER_PID" ] && kill -0 "$LAUNCHER_PID" 2>/dev/null; then
    LAUNCHER_STATE="ALIVE (PID=$LAUNCHER_PID)"
  fi

  # 4. Cluster job state (only if a cluster exists)
  JOB_INFO=""
  if [ -n "$SKY_CLUSTERS" ]; then
    for cl in $SKY_CLUSTERS; do
      JOB_INFO+=" $cl:"
      JOB_INFO+=$(sky queue "$cl" --skip-finished 2>/dev/null | grep -E "RUNNING|PENDING" | head -1 | awk '{print $1"="$4}' || echo "no-job")
    done
  fi

  # 5. Latest cluster log line (if accessible)
  LATEST_HEARTBEAT=$(grep -E "extracted=|shard.*flushed" /mnt/d/AI/hd-instrument/data/cell2_smart_launch.log 2>/dev/null | tail -1 | sed 's/\x1b\[[0-9;]*[a-zA-Z]//g' | cut -c -200)

  # 6. Cumulative cost estimate (GH200 = $2.29/h)
  COST_HOURS=$(echo "scale=4; $uptime / 3600" | bc 2>/dev/null || echo "?")
  COST_USD=$(echo "scale=2; $COST_HOURS * 2.29" | bc 2>/dev/null || echo "?")

  # 7. SSH disconnect count today
  SSH_DROPS=$(grep -c "sky launch exit code: 255" /mnt/d/AI/hd-instrument/data/cell2_smart_launch.log 2>/dev/null || echo 0)

  # Emit structured block
  cat <<EOF | tee -a "$LOG"
=== [${ts}] watchdog tick (uptime=${uptime}s; cum_cost=\$${COST_USD}; ssh_drops_total=${SSH_DROPS}) ===
Lambda instances: ${N_INST}
${INST_SUMMARY}
sky clusters: $(echo "$SKY_CLUSTERS" | tr '\n' ' ')
sky job state:${JOB_INFO}
launcher: ${LAUNCHER_STATE}
latest extraction:
  ${LATEST_HEARTBEAT}
EOF

  # JSON state file for programmatic consumers
  python3 <<PYEOF > "$STATE_FILE" 2>/dev/null || true
import json
state = {
    "ts": "${ts}",
    "uptime_s": ${uptime},
    "lambda_instance_count": "${N_INST}",
    "sky_clusters": "$(echo $SKY_CLUSTERS | tr '\n' ',')".rstrip(','),
    "launcher_state": "${LAUNCHER_STATE}",
    "ssh_drops_total": ${SSH_DROPS},
    "cum_cost_usd": "${COST_USD}",
    "latest_heartbeat": """${LATEST_HEARTBEAT}""",
}
print(json.dumps(state, indent=2))
PYEOF

  sleep "$INTERVAL"
done
