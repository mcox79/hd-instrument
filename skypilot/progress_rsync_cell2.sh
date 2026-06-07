#!/usr/bin/env bash
# Periodic progress rsync: pull shards from the running cluster every N minutes.
# If the cluster dies mid-run, whatever shards were last rsync'd survive locally.
# Uses --partial so an interrupted rsync resumes cleanly next tick.
set -uo pipefail

source /root/skyvenv/bin/activate

LOG=/mnt/d/AI/hd-instrument/data/cell2_progress_rsync.log
INTERVAL_MIN=5
INTERVAL_SEC=$((INTERVAL_MIN * 60))
LOCAL_DIR=/mnt/d/AI/hd-instrument/data/cell2_results
# IMPORTANT: single-quote so ~ does NOT expand at script-load time on the local
# (WSL root) side. We want the remote shell (ubuntu user on Lambda) to expand it
# to /home/ubuntu/sky_workdir. Double-quoted would also work since bash doesn't
# expand ~ inside double-quotes, but single-quote is unambiguously safe.
REMOTE_PATH='~/sky_workdir/data/exp_substrate_wikipedia_layer15_cache_extraction_v1/'

mkdir -p "$LOCAL_DIR"

echo "===== progress_rsync start $(date -u '+%Y-%m-%dT%H:%M:%SZ') =====" | tee -a "$LOG"
echo "[progress_rsync] interval=${INTERVAL_MIN} min" | tee -a "$LOG"

# Wait for the first cluster to come UP
CLUSTER=""
while [ -z "$CLUSTER" ]; do
  CLUSTER=$(sky status 2>/dev/null | grep -oE "cell2wiki-[0-9]+" | head -1)
  if [ -z "$CLUSTER" ]; then
    sleep 30
  fi
done
echo "[progress_rsync] LOCKED to cluster: $CLUSTER" | tee -a "$LOG"

CONSECUTIVE_FAILURES=0
TOTAL_SHARDS_LAST=0

while true; do
  ts=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

  # Skip if cluster is no longer UP
  STATUS=$(sky status 2>/dev/null | grep "$CLUSTER" | head -1 || true)
  if [ -z "$STATUS" ]; then
    echo "[${ts}] cluster $CLUSTER no longer in sky status -- exit progress_rsync" | tee -a "$LOG"
    break
  fi

  # Try rsync; tolerate failures (cluster might be busy, SSH might glitch)
  echo "[${ts}] rsync from $CLUSTER (cluster status: $(echo "$STATUS" | awk '{print $5}'))" | tee -a "$LOG"
  rsync -av --partial --timeout=120 \
    -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=30" \
    "${CLUSTER}:${REMOTE_PATH}" \
    "${LOCAL_DIR}/" >>"$LOG" 2>&1
  RC=$?

  if [ "$RC" -eq 0 ]; then
    CONSECUTIVE_FAILURES=0
    TOTAL_SHARDS=$(ls -1 "${LOCAL_DIR}/shard_"*.npz 2>/dev/null | wc -l || echo 0)
    NEW_SHARDS=$((TOTAL_SHARDS - TOTAL_SHARDS_LAST))
    SIZE=$(du -sh "${LOCAL_DIR}" 2>/dev/null | cut -f1 || echo "?")
    echo "[${ts}] rsync OK: ${TOTAL_SHARDS} shards on local ($SIZE; +${NEW_SHARDS} new)" | tee -a "$LOG"
    TOTAL_SHARDS_LAST=$TOTAL_SHARDS
  else
    CONSECUTIVE_FAILURES=$((CONSECUTIVE_FAILURES + 1))
    echo "[${ts}] rsync exit=${RC} (consecutive failures: ${CONSECUTIVE_FAILURES})" | tee -a "$LOG"
    if [ "$CONSECUTIVE_FAILURES" -ge 5 ]; then
      echo "[${ts}] 5 consecutive rsync failures -- cluster likely dead; exiting" | tee -a "$LOG"
      break
    fi
  fi

  sleep "$INTERVAL_SEC"
done

echo "===== progress_rsync end $(date -u '+%Y-%m-%dT%H:%M:%SZ') =====" | tee -a "$LOG"
