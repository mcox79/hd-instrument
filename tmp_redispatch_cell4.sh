#!/bin/bash
# Rebuild cell4-ship with fixed script + redispatch CELL-4.
# Holds WSL alive while CELL-4 runs (~10-15 min including setup).
set -e

SAFETY=/mnt/d/AI/hd-instrument/skypilot/safety/safety_launch_all.sh
DATA=/mnt/d/AI/hd-instrument/data

echo "=== rebuild cell4-ship with fixed script ==="
bash /mnt/d/AI/hd-instrument/skypilot/cell4/build_cell4_ship.sh 2>&1 | tail -10
echo ""

echo "=== confirm CELL-3 SMOKE still healthy ==="
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
echo "===== HOLDING WSL ALIVE FOR CELL-4 ====="
wait $CELL4_PID
CELL4_RC=$?
echo "===== CELL-4 finished rc=$CELL4_RC at $(date -u '+%H:%M:%S') ====="

echo ""
echo "=== CELL-4 results ==="
ls -la $DATA/cell4_results/ 2>&1 | head -10
echo ""
echo "  verdict:"
cat $DATA/cell4_results/metrics.json 2>&1 | python3 -m json.tool 2>&1 | head -25
