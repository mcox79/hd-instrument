#!/bin/bash
# Dispatch CELL-COLBERT via safety stack; HOLD WSL alive via `wait` until done.
# Per `feedback_wsl_distro_auto_shutdown.md`: PowerShell `wsl bash <script>` must
# block for the full duration; otherwise WSL's ~60-sec vmIdleTimeout kills nohup'd children.
set -e

SAFETY=/mnt/d/AI/hd-instrument/skypilot/safety/safety_launch_all.sh
DATA=/mnt/d/AI/hd-instrument/data
mkdir -p "$DATA"

echo "=== verifying bundle ==="
test -d /root/cell_colbert-ship || { echo "ERROR: cell_colbert-ship not built; run build first"; exit 1; }
test -f /root/cell_colbert-ship/skypilot/cell_colbert_hotpot_h100.yaml || { echo "ERROR: YAML missing in bundle"; exit 1; }
test -f /root/cell_colbert-ship/experiments/exp_colbert_v2_hotpot_distractor_v1.py || { echo "ERROR: script missing"; exit 1; }
echo "  bundle: $(du -sh /root/cell_colbert-ship 2>&1 | cut -f1)"

echo ""
echo "=== verifying NO existing Lambda instances ==="
LAMBDA_KEY=$(grep -oP 'api_key\s*=\s*\K\S+' /root/.lambda_cloud/lambda_keys | head -1)
N_INST=$(curl -s -H "User-Agent: curl/7.81.0" -u "${LAMBDA_KEY}:" \
    https://cloud.lambdalabs.com/api/v1/instances | \
    python3 -c "import sys,json;print(len(json.load(sys.stdin).get('data',[])))")
echo "  current: $N_INST"
if [ "$N_INST" != "0" ]; then
    echo "  WARN: pre-existing instances! checking if they're ours..."
    curl -s -H "User-Agent: curl/7.81.0" -u "${LAMBDA_KEY}:" \
        https://cloud.lambdalabs.com/api/v1/instances | python3 -m json.tool | head -15
fi

echo ""
echo "=== launch CELL-COLBERT in background ==="
date -u '+%H:%M:%S'
nohup bash $SAFETY /mnt/d/AI/hd-instrument/skypilot/cell_colbert/cell_colbert_config.sh \
    > $DATA/cell_colbert_orchestrator.log 2>&1 &
ORCH_PID=$!
echo "  orchestrator PID: $ORCH_PID"

echo ""
echo "===== HOLDING WSL ALIVE BY WAITING FOR ORCHESTRATOR (~30 min) ====="
echo "  Logs:"
echo "    $DATA/cell_colbert_smart_launch.log"
echo "    $DATA/cell_colbert_watchdog.log"
echo "    $DATA/cell_colbert_progress_rsync.log"
echo "    $DATA/cell_colbert_state.json"

# wait blocks here; WSL stays alive throughout
wait $ORCH_PID
RC=$?
echo "===== CELL-COLBERT orchestrator finished rc=$RC at $(date -u '+%H:%M:%S') ====="

echo ""
echo "=== final state ==="
ls -la $DATA/cell_colbert_results/ 2>&1 | head -10
echo ""
echo "  verdict:"
cat $DATA/cell_colbert_results/metrics.json 2>&1 | python3 -m json.tool 2>&1 | head -25
