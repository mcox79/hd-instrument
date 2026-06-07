#!/usr/bin/env bash
# generic_watchdog.sh -- emit comprehensive state log every 30 sec.
#
# REQUIRES: $1 = path to cell config (exports CELL_NAME, CLUSTER_PREFIX,
#   LAUNCHER_LOG, LAUNCHER_LOCK_PATH, WATCHDOG_LOG, WATCHDOG_STATE_JSON,
#   HOURLY_RATE_USD).
#
# Independent of any SSH connection -- uses Lambda API direct probe + sky status.
# If launcher SSH drops, watchdog still reports cluster state correctly.

set -uo pipefail

if [ -z "${1:-}" ]; then
    echo "ERROR: usage: $0 <path-to-cell-config.sh>" >&2
    exit 2
fi
CONFIG_FILE="$1"
# shellcheck disable=SC1090
source "$CONFIG_FILE"

for required_var in CELL_NAME CLUSTER_PREFIX LAUNCHER_LOG LAUNCHER_LOCK_PATH \
                   WATCHDOG_LOG WATCHDOG_STATE_JSON HOURLY_RATE_USD; do
    if [ -z "${!required_var:-}" ]; then
        echo "ERROR: watchdog needs $required_var in config" >&2
        exit 2
    fi
done

INTERVAL="${WATCHDOG_INTERVAL_SEC:-30}"
LAMBDA_API_KEY=$(grep -oP 'api_key\s*=\s*\K\S+' /root/.lambda_cloud/lambda_keys 2>/dev/null | head -1)

source /root/skyvenv/bin/activate

mkdir -p "$(dirname "$WATCHDOG_LOG")"
echo "===== [${CELL_NAME}] watchdog start $(date -u '+%Y-%m-%dT%H:%M:%SZ') =====" | tee -a "$WATCHDOG_LOG"
echo "[watchdog] PID=$$; interval=${INTERVAL}s; log=${WATCHDOG_LOG}" | tee -a "$WATCHDOG_LOG"

START_EPOCH=$(date -u '+%s')

while true; do
    ts=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
    ts_epoch=$(date -u '+%s')
    uptime=$((ts_epoch - START_EPOCH))

    LAMBDA_JSON=$(curl -sS --max-time 10 -H "User-Agent: curl/7.81.0" -u "${LAMBDA_API_KEY}:" \
        https://cloud.lambdalabs.com/api/v1/instances 2>/dev/null || echo '{"data":[]}')
    N_INST=$(echo "$LAMBDA_JSON" | python3 -c "import sys, json; d=json.load(sys.stdin); print(len(d.get('data',[])))" 2>/dev/null || echo "?")
    INST_SUMMARY=$(echo "$LAMBDA_JSON" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for i in d.get('data', []):
    print(f\"  - id={i.get('id','?')[:12]} type={i.get('instance_type', {}).get('name', '?')} status={i.get('status','?')} region={i.get('region', {}).get('name', '?')} ip={i.get('ip', 'n/a')}\")" 2>/dev/null)

    SKY_CLUSTERS=$(sky status 2>/dev/null | grep -oE "${CLUSTER_PREFIX}-[0-9]+" | sort -u)

    LAUNCHER_PID=$(cat "$LAUNCHER_LOCK_PATH" 2>/dev/null || echo "")
    LAUNCHER_STATE="DEAD"
    if [ -n "$LAUNCHER_PID" ] && kill -0 "$LAUNCHER_PID" 2>/dev/null; then
        LAUNCHER_STATE="ALIVE (PID=$LAUNCHER_PID)"
    fi

    LATEST_HEARTBEAT=$(grep -E "extracted=|shard.*flushed|step.*loss=|train|VERDICT" "$LAUNCHER_LOG" 2>/dev/null | tail -1 | sed 's/\x1b\[[0-9;]*[a-zA-Z]//g' | cut -c -250)

    SSH_DROPS=$(grep -c "sky launch exit code: 255" "$LAUNCHER_LOG" 2>/dev/null | head -1)
    SSH_DROPS=${SSH_DROPS:-0}

    COST_HOURS=$(echo "scale=4; $uptime / 3600" | bc 2>/dev/null || echo "?")
    COST_USD=$(echo "scale=2; $COST_HOURS * $HOURLY_RATE_USD" | bc 2>/dev/null || echo "?")

    {
        echo "=== [${ts}] watchdog tick (uptime=${uptime}s; cum_cost=\$${COST_USD}; ssh_drops=${SSH_DROPS}) ==="
        echo "Lambda instances: ${N_INST}"
        echo "${INST_SUMMARY}"
        echo "sky clusters: $(echo "$SKY_CLUSTERS" | tr '\n' ' ')"
        echo "launcher: ${LAUNCHER_STATE}"
        echo "latest heartbeat:"
        echo "  ${LATEST_HEARTBEAT}"
    } | tee -a "$WATCHDOG_LOG"

    # Write JSON state for programmatic consumers
    python3 - <<PYEOF > "$WATCHDOG_STATE_JSON" 2>/dev/null || true
import json
state = {
    "cell_name": "${CELL_NAME}",
    "ts": "${ts}",
    "uptime_s": ${uptime},
    "lambda_instance_count": "${N_INST}",
    "sky_clusters": "$(echo $SKY_CLUSTERS | tr '\n' ',')".rstrip(','),
    "launcher_state": "${LAUNCHER_STATE}",
    "ssh_drops_total": ${SSH_DROPS},
    "cum_cost_usd": "${COST_USD}",
    "hourly_rate_usd": "${HOURLY_RATE_USD}",
    "latest_heartbeat": """${LATEST_HEARTBEAT}""",
}
print(json.dumps(state, indent=2))
PYEOF

    sleep "$INTERVAL"
done
