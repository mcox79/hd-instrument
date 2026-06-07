#!/usr/bin/env bash
# Periodic sky rsync-down watcher for cornerstone-* clusters.
# Runs every INTERVAL seconds; bounds worst-case data loss to ~INTERVAL wall.
# Exits cleanly when the cluster disappears (autostop fired, sky down, etc).
#
# Auto-detects the current cornerstone-* cluster name from sky status so it
# survives launcher's HHMMSS suffix scheme.
#
# Logs to /mnt/d/AI/hd-instrument/data/cornerstone_watcher.log
set +e

DST=/mnt/d/AI/hd-instrument/data/cornerstone_results
LOG=/mnt/d/AI/hd-instrument/data/cornerstone_watcher.log
INTERVAL=${INTERVAL:-300}   # 5 minutes default

mkdir -p "$(dirname "$LOG")" "$DST"
source /root/skyvenv/bin/activate

echo "===== watcher start $(date -u '+%Y-%m-%dT%H:%M:%SZ') interval=${INTERVAL}s =====" >> "$LOG"

gone_count=0
while true; do
  ts=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

  # Find the active cornerstone-* cluster (handles HHMMSS-suffixed names).
  cluster_line=$(sky status 2>/dev/null | grep -E '^cornerstone(-[0-9]+)?[[:space:]]' | head -1)
  CLUSTER=$(echo "$cluster_line" | awk '{print $1}')
  state=$(echo "$cluster_line" | grep -oE '\b(INIT|UP|STOPPED|TERMINATING|TERMINATED)\b' | head -1)

  if [ -z "$CLUSTER" ] || [ -z "$state" ]; then
    gone_count=$((gone_count + 1))
    echo "[$ts] no cornerstone cluster in sky status (gone_count=$gone_count)" >> "$LOG"
    if [ "$gone_count" -ge 3 ]; then
      echo "[$ts] cluster gone for 3 consecutive checks; exiting watcher" >> "$LOG"
      break
    fi
    sleep "$INTERVAL"
    continue
  fi
  gone_count=0

  echo "[$ts] cluster=$CLUSTER state=$state" >> "$LOG"

  if [ "$state" = "UP" ]; then
    echo "[$ts] rsync via SSH begin (cluster=$CLUSTER)" >> "$LOG"
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
