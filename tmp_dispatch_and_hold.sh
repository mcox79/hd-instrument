#!/bin/bash
# Dispatch + HOLD the WSL session alive by tailing logs until orchestrators complete.
# The PowerShell wsl bash invocation MUST block until orchestrators finish, otherwise
# WSL auto-shutdown kills everything.
set -e

SAFETY=/mnt/d/AI/hd-instrument/skypilot/safety/safety_launch_all.sh
DATA=/mnt/d/AI/hd-instrument/data
mkdir -p "$DATA"

echo "=== bundles ==="
test -d /root/cell3-ship/data/cell2_results || { echo "ERROR: cell3-ship not built"; exit 1; }
test -d /root/cell4-ship/data/cell2_results || { echo "ERROR: cell4-ship not built"; exit 1; }
echo "  cell3-ship: $(ls /root/cell3-ship/data/cell2_results/ | wc -l) shards"
echo "  cell4-ship: $(ls /root/cell4-ship/data/cell2_results/ | wc -l) shards"

echo ""
echo "=== Lambda instances (clean slate?) ==="
LAMBDA_KEY=$(grep -oP 'api_key\s*=\s*\K\S+' /root/.lambda_cloud/lambda_keys | head -1)
N_INST=$(curl -s -H "User-Agent: curl/7.81.0" -u "${LAMBDA_KEY}:" \
    https://cloud.lambdalabs.com/api/v1/instances | \
    python3 -c "import sys,json;print(len(json.load(sys.stdin).get('data',[])))")
echo "  current: $N_INST"
[ "$N_INST" = "0" ] || { echo "ERROR: pre-existing instances"; exit 1; }

echo ""
echo "=== launch CELL-3 SMOKE in background ==="
date -u '+%H:%M:%S'
nohup bash $SAFETY /mnt/d/AI/hd-instrument/skypilot/cell3/cell3_smoke_config.sh \
    > $DATA/cell3_smoke_orchestrator.log 2>&1 &
SMOKE_PID=$!
echo "  orchestrator PID: $SMOKE_PID"

echo ""
echo "=== sleep 60 sec to stagger CELL-4 (avoid GH200 race) ==="
sleep 60

echo "=== launch CELL-4 in background ==="
date -u '+%H:%M:%S'
nohup bash $SAFETY /mnt/d/AI/hd-instrument/skypilot/cell4/cell4_config.sh \
    > $DATA/cell4_orchestrator.log 2>&1 &
CELL4_PID=$!
echo "  orchestrator PID: $CELL4_PID"

echo ""
echo "===== HOLDING WSL SESSION ALIVE BY WAITING FOR ORCHESTRATORS ====="
echo "  This blocks until both orchestrators finish (~45-60 min)"
echo "  Logs:"
echo "    $DATA/cell3_smoke_smart_launch.log"
echo "    $DATA/cell4_smart_launch.log"
echo "    $DATA/cell3_smoke_watchdog.log"
echo "    $DATA/cell4_watchdog.log"

# Wait for BOTH orchestrators to terminate. This blocks the WSL session
# from auto-shutting down because there are active foreground children.
wait $SMOKE_PID
SMOKE_RC=$?
echo "===== CELL-3 SMOKE orchestrator finished rc=$SMOKE_RC at $(date -u '+%H:%M:%S') ====="

wait $CELL4_PID
CELL4_RC=$?
echo "===== CELL-4 orchestrator finished rc=$CELL4_RC at $(date -u '+%H:%M:%S') ====="

echo ""
echo "=== final state ==="
ls -la $DATA/cell3_smoke_results/ 2>&1 | head -10
ls -la $DATA/cell4_results/ 2>&1 | head -10
echo ""
echo "  smoke verdict:"
cat $DATA/cell3_smoke_results/metrics.json 2>&1 | python3 -m json.tool 2>&1 | head -20
echo "  cell4 verdict:"
cat $DATA/cell4_results/metrics.json 2>&1 | python3 -m json.tool 2>&1 | head -20
