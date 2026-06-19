#!/bin/bash
# Dispatch CELL-3 SMOKE + CELL-4 in PARALLEL via safety_launch_all.sh orchestrator.
# Each runs in its own nohup background process with its own log + safety stack.
set -e
SAFETY=/mnt/d/AI/hd-instrument/skypilot/safety/safety_launch_all.sh
DATA=/mnt/d/AI/hd-instrument/data
mkdir -p "$DATA"

echo "=== verifying bundles are ready ==="
test -d /root/cell3-ship/data/cell2_results || { echo "ERROR: cell3-ship not built"; exit 1; }
test -d /root/cell4-ship/data/cell2_results || { echo "ERROR: cell4-ship not built"; exit 1; }
echo "  cell3-ship: $(ls /root/cell3-ship/data/cell2_results/ | wc -l) shards, $(du -sh /root/cell3-ship 2>&1 | cut -f1)"
echo "  cell4-ship: $(ls /root/cell4-ship/data/cell2_results/ | wc -l) shards, $(du -sh /root/cell4-ship 2>&1 | cut -f1)"

echo ""
echo "=== verifying NO existing Lambda instances (clean slate) ==="
LAMBDA_KEY=$(grep -oP 'api_key\s*=\s*\K\S+' /root/.lambda_cloud/lambda_keys | head -1)
N_INST=$(curl -s -H "User-Agent: curl/7.81.0" -u "${LAMBDA_KEY}:" \
    https://cloud.lambdalabs.com/api/v1/instances | \
    python3 -c "import sys,json;print(len(json.load(sys.stdin).get('data',[])))")
echo "  current Lambda instances: $N_INST"
if [ "$N_INST" != "0" ]; then
    echo "  WARN: pre-existing instances present; check whether intentional before dispatching"
fi

echo ""
echo "=== STEP A: launch CELL-3 SMOKE (cell3sm-XXXXXX) ==="
date -u '+%H:%M:%S'
nohup bash $SAFETY /mnt/d/AI/hd-instrument/skypilot/cell3/cell3_smoke_config.sh \
    > $DATA/cell3_smoke_orchestrator.log 2>&1 &
SMOKE_PID=$!
echo "  PID: $SMOKE_PID"
echo "  orchestrator log: $DATA/cell3_smoke_orchestrator.log"
echo "  launcher log: $DATA/cell3_smoke_smart_launch.log"
echo "  watchdog log: $DATA/cell3_smoke_watchdog.log"

# Stagger 60 sec so CELL-3 SMOKE acquires its SKU and Lambda updates capacity
# before CELL-4 polls. Without this both race for the same GH200 in us-east-3.
echo ""
echo "=== sleeping 60 sec to stagger CELL-4 launch (avoid GH200 race) ==="
sleep 60

echo ""
echo "=== STEP B: launch CELL-4 (cell4hp-XXXXXX) ==="
date -u '+%H:%M:%S'
nohup bash $SAFETY /mnt/d/AI/hd-instrument/skypilot/cell4/cell4_config.sh \
    > $DATA/cell4_orchestrator.log 2>&1 &
CELL4_PID=$!
echo "  PID: $CELL4_PID"
echo "  orchestrator log: $DATA/cell4_orchestrator.log"
echo "  launcher log: $DATA/cell4_smart_launch.log"
echo "  watchdog log: $DATA/cell4_watchdog.log"

echo ""
echo "=== both orchestrators started; safety stack now monitoring ==="
echo "to watch:"
echo "  tail -F $DATA/cell3_smoke_smart_launch.log"
echo "  tail -F $DATA/cell4_smart_launch.log"
echo "  tail -F $DATA/cell3_smoke_watchdog.log"
echo "  tail -F $DATA/cell4_watchdog.log"
echo "to inspect state JSON:"
echo "  cat $DATA/cell3_smoke_state.json"
echo "  cat $DATA/cell4_state.json"

ps -ef | grep -E "safety_launch_all|generic_smart_launch|generic_watchdog|generic_kill_switch|generic_progress_rsync" | grep -v grep
