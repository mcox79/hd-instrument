#!/bin/bash
# Dispatch CELL-4 alone (CELL-3 SMOKE is already running).
# Hold WSL session alive while CELL-4 completes.
set -e
SAFETY=/mnt/d/AI/hd-instrument/skypilot/safety/safety_launch_all.sh
DATA=/mnt/d/AI/hd-instrument/data
mkdir -p "$DATA"

echo "=== check CELL-3 SMOKE is still running ==="
source /root/skyvenv/bin/activate
sky status 2>&1 | head -10

echo ""
echo "=== launch CELL-4 ==="
date -u '+%H:%M:%S'
nohup bash $SAFETY /mnt/d/AI/hd-instrument/skypilot/cell4/cell4_config.sh \
    > $DATA/cell4_orchestrator.log 2>&1 &
CELL4_PID=$!
echo "  orchestrator PID: $CELL4_PID"

echo ""
echo "===== HOLDING WSL SESSION ALIVE FOR CELL-4 (~20-25 min) ====="
wait $CELL4_PID
CELL4_RC=$?
echo "===== CELL-4 orchestrator finished rc=$CELL4_RC at $(date -u '+%H:%M:%S') ====="

echo ""
echo "=== CELL-4 final state ==="
ls -la $DATA/cell4_results/ 2>&1 | head -10
echo ""
echo "  cell4 verdict:"
cat $DATA/cell4_results/metrics.json 2>&1 | python3 -m json.tool 2>&1 | head -20
