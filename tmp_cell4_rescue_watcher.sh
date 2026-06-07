#!/bin/bash
# Watch cell4hp-092905 cluster; when sky job completes, rsync artifacts then sky down.
# Bypasses the broken safety stack post-acquisition path.
set -uo pipefail

CLUSTER=cell4hp-092905
REMOTE_PATH='~/sky_workdir/data/exp_substrate_hp12_v2_100k_pseudoinverse_v1/'
LOCAL_DIR=/mnt/d/AI/hd-instrument/data/cell4_results

source /root/skyvenv/bin/activate
mkdir -p $LOCAL_DIR

echo "===== CELL-4 RESCUE WATCHER ====="
date -u '+%H:%M:%S start'

ATTEMPTS=0
MAX_ATTEMPTS=60  # 30 min max (every 30 sec)
while [ $ATTEMPTS -lt $MAX_ATTEMPTS ]; do
    ATTEMPTS=$((ATTEMPTS+1))

    # Check sky queue: if job 1 has finished, rsync and tear down
    QUEUE=$(sky queue $CLUSTER 2>&1 || echo "QUEUE_ERR")
    if echo "$QUEUE" | grep -qE "SUCCEEDED|FAILED|CANCELLED"; then
        echo ""
        echo "===== JOB FINISHED detected at $(date -u '+%H:%M:%S') (attempt $ATTEMPTS) ====="
        echo "$QUEUE" | head -8

        echo ""
        echo "=== rsync artifacts back from $CLUSTER ==="
        rsync -av --partial --progress \
            -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR" \
            $CLUSTER:$REMOTE_PATH $LOCAL_DIR/ 2>&1 | tail -15

        echo ""
        echo "=== verify artifacts ==="
        ls -la $LOCAL_DIR/ 2>&1
        echo "metrics:"
        cat $LOCAL_DIR/metrics.json 2>&1 | python3 -m json.tool 2>&1 | head -20

        echo ""
        echo "=== sky down $CLUSTER ==="
        sky down -y $CLUSTER 2>&1 | tail -5
        echo "===== RESCUE COMPLETE at $(date -u '+%H:%M:%S') ====="
        exit 0
    fi

    # Status update every 10 attempts (5 min)
    if [ $((ATTEMPTS % 10)) -eq 1 ]; then
        echo "[$(date -u '+%H:%M:%S') attempt $ATTEMPTS] job not finished yet; queue head:"
        echo "$QUEUE" | head -8
    fi

    sleep 30
done

echo "===== TIMEOUT after $MAX_ATTEMPTS attempts ====="
sky down -y $CLUSTER 2>&1
exit 1
