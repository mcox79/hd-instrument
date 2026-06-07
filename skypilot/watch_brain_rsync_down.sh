#!/usr/bin/env bash
# Periodic rsync-down watcher for the hd-brain cluster.
# Pulls /sky_workdir/data/ back every INTERVAL seconds; exits when cluster
# disappears (autodown fired, sky down, etc).
#
# Logs to /mnt/d/AI/hd-instrument/data/skypilot_results_brain_watcher.log
set +e

CLUSTER=hd-brain
SRC=~/sky_workdir/data
DST=/mnt/d/AI/hd-instrument/data/skypilot_results_brain
LOG=/mnt/d/AI/hd-instrument/data/skypilot_results_brain_watcher.log
INTERVAL=${INTERVAL:-300}   # 5 minutes default

mkdir -p "$(dirname "$LOG")" "$DST"
source /root/skyvenv/bin/activate

echo "===== watcher start $(date -u '+%Y-%m-%dT%H:%M:%SZ') cluster=$CLUSTER interval=${INTERVAL}s =====" >> "$LOG"

gone_count=0
while true; do
  ts=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

  state=$(sky status 2>/dev/null | grep -E "^${CLUSTER}[[:space:]]" \
            | grep -oE '\b(INIT|UP|STOPPED|TERMINATING|TERMINATED)\b' | head -1)

  if [ -z "$state" ]; then
    gone_count=$((gone_count + 1))
    echo "[$ts] cluster '$CLUSTER' not in sky status (gone_count=$gone_count)" >> "$LOG"
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
