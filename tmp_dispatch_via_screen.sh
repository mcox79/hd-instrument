#!/bin/bash
# Dispatch CELL-3 SMOKE + CELL-4 via DETACHED SCREEN SESSIONS.
# Screen sessions survive parent terminal closure (unlike nohup in WSL).
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
echo "=== verifying NO existing Lambda instances ==="
LAMBDA_KEY=$(grep -oP 'api_key\s*=\s*\K\S+' /root/.lambda_cloud/lambda_keys | head -1)
N_INST=$(curl -s -H "User-Agent: curl/7.81.0" -u "${LAMBDA_KEY}:" \
    https://cloud.lambdalabs.com/api/v1/instances | \
    python3 -c "import sys,json;print(len(json.load(sys.stdin).get('data',[])))")
echo "  current Lambda instances: $N_INST"
if [ "$N_INST" != "0" ]; then
    echo "  WARN: pre-existing instances! aborting"
    exit 1
fi

echo ""
echo "=== checking for previous screen sessions ==="
screen -ls 2>&1 | grep -E 'cell3sm|cell4hp' && {
    echo "  WARN: previous screen sessions exist; killing"
    screen -ls 2>&1 | grep -E 'cell3sm|cell4hp' | awk '{print $1}' | xargs -I{} screen -S {} -X quit 2>/dev/null
    sleep 1
}

echo ""
echo "=== STEP A: launch CELL-3 SMOKE in detached screen 'cell3sm' ==="
date -u '+%H:%M:%S start cell3sm'
screen -dmS cell3sm bash $SAFETY /mnt/d/AI/hd-instrument/skypilot/cell3/cell3_smoke_config.sh
sleep 2
echo "  screen status:"
screen -ls 2>&1 | grep cell3sm || echo "  WARN: not found in screen list"

echo ""
echo "=== sleeping 60 sec to stagger CELL-4 ==="
sleep 60

echo ""
echo "=== STEP B: launch CELL-4 in detached screen 'cell4hp' ==="
date -u '+%H:%M:%S start cell4hp'
screen -dmS cell4hp bash $SAFETY /mnt/d/AI/hd-instrument/skypilot/cell4/cell4_config.sh
sleep 2
echo "  screen status:"
screen -ls 2>&1 | grep cell4hp || echo "  WARN: not found in screen list"

echo ""
echo "=== DISPATCH COMPLETE ==="
echo ""
echo "Sessions live:"
screen -ls 2>&1 | head -10
echo ""
echo "Processes:"
ps -ef | grep -E 'safety_launch|generic_' | grep -v grep | head -15
echo ""
echo "To attach to a session:"
echo "  screen -r cell3sm"
echo "  screen -r cell4hp"
echo ""
echo "To monitor without attaching:"
echo "  tail -F $DATA/cell3_smoke_smart_launch.log"
echo "  tail -F $DATA/cell4_smart_launch.log"
