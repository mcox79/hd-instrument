#!/usr/bin/env bash
# Periodic sky rsync-down watcher for hd-phase05.
# Runs every INTERVAL seconds; bounds worst-case data loss to ~INTERVAL wall.
# Exits cleanly when the cluster disappears (autostop fired, sky down, etc).
#
# Logs to /mnt/d/AI/hd-instrument/data/skypilot_watcher.log
set +e

CLUSTER=hd-phase05
SRC=~/sky_workdir/data
DST=/mnt/d/AI/hd-instrument/data/skypilot_results
LOG=/mnt/d/AI/hd-instrument/data/skypilot_watcher.log
INTERVAL=${INTERVAL:-300}   # 5 minutes default

mkdir -p "$(dirname "$LOG")" "$DST"
source /root/skyvenv/bin/activate

echo "===== watcher start $(date -u '+%Y-%m-%dT%H:%M:%SZ') cluster=$CLUSTER interval=${INTERVAL}s =====" >> "$LOG"

gone_count=0
while true; do
  ts=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

  # State extraction: grep cluster row, then extract one of the known statuses.
  state=$(sky status 2>/dev/null | grep -E "^${CLUSTER}[[:space:]]" \
            | grep -oE '\b(INIT|UP|STOPPED|TERMINATING|TERMINATED)\b' | head -1)

  if [ -z "$state" ]; then
    gone_count=$((gone_count + 1))
    echo "[$ts] cluster '$CLUSTER' not in sky status (gone_count=$gone_count)" >> "$LOG"
    # Tolerate 2 transient misses (sky api caching) before exiting
    if [ "$gone_count" -ge 3 ]; then
      echo "[$ts] cluster gone for 3 consecutive checks; exiting watcher" >> "$LOG"
      break
    fi
    sleep "$INTERVAL"
    continue
  fi
  gone_count=0

  echo "[$ts] state=$state" >> "$LOG"

  if [ "$state" = "UP" ]; then
    # Direct rsync over SSH; sky launch added an SSH config alias `hd-phase05`.
    # `sky rsync-down` was removed in SkyPilot 0.12; this is the supported path.
    echo "[$ts] rsync via SSH begin" >> "$LOG"
    rsync -av --partial \
      -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR" \
      "${CLUSTER}:~/sky_workdir/data/" "$DST/" >> "$LOG" 2>&1
    rc=$?
    if [ "$rc" -eq 0 ]; then
      bytes=$(du -sb "$DST" 2>/dev/null | awk '{print $1}')
      n_metrics=$(find "$DST" -name 'metrics.json' 2>/dev/null | wc -l)
      echo "[$ts] rsync ok (dst_total_bytes=$bytes, metrics.json count=$n_metrics)" >> "$LOG"
    else
      echo "[$ts] rsync failed rc=$rc (will retry next interval)" >> "$LOG"
    fi
  elif [ "$state" = "STOPPED" ] || [ "$state" = "TERMINATING" ] || [ "$state" = "TERMINATED" ]; then
    echo "[$ts] cluster $state; final rsync attempt then exit" >> "$LOG"
    rsync -av --partial \
      -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR" \
      "${CLUSTER}:~/sky_workdir/data/" "$DST/" >> "$LOG" 2>&1
    echo "[$ts] watcher exiting on terminal state=$state" >> "$LOG"
    break
  fi

  sleep "$INTERVAL"
done

echo "===== watcher end $(date -u '+%Y-%m-%dT%H:%M:%SZ') =====" >> "$LOG"
