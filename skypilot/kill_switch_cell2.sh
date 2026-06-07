#!/usr/bin/env bash
# Kill switch: prevent the launcher from spawning a SECOND cluster on failure.
# Once a single cluster is acquired, that's the only one we'll run.
# If anything kills it, we accept the loss; we do NOT auto-restart.
#
# This watches the launcher log for danger signals and kills the launcher
# process immediately upon detection.
set -uo pipefail

LOG=/mnt/d/AI/hd-instrument/data/cell2_smart_launch.log
KILL_LOG=/mnt/d/AI/hd-instrument/data/cell2_kill_switch.log
LOCK_PATH=/tmp/smart_launch_cell2.pid

echo "===== kill_switch start $(date -u '+%Y-%m-%dT%H:%M:%SZ') =====" | tee -a "$KILL_LOG"
echo "[kill_switch] watching ${LOG} for danger signals (will kill launcher on retry attempt)" | tee -a "$KILL_LOG"

# Wait for the launcher to acquire its FIRST cluster
FIRST_CLUSTER=""
while [ -z "$FIRST_CLUSTER" ]; do
  FIRST_CLUSTER=$(grep -oE "launching cluster=cell2wiki-[0-9]+" "$LOG" 2>/dev/null | head -1 | sed 's/launching cluster=//')
  if [ -z "$FIRST_CLUSTER" ]; then
    sleep 5
  fi
done
echo "[kill_switch] $(date -u '+%Y-%m-%dT%H:%M:%SZ') LOCKED to first acquired cluster: ${FIRST_CLUSTER}" | tee -a "$KILL_LOG"
echo "[kill_switch] any 'launching cluster=' line referencing a DIFFERENT cluster name will trigger immediate launcher kill" | tee -a "$KILL_LOG"

# Tail the log; kill launcher on any DANGER signal
tail -n +1 -F "$LOG" 2>/dev/null | while IFS= read -r line; do
  # Strip ANSI codes
  clean_line=$(echo "$line" | sed 's/\x1b\[[0-9;]*[a-zA-Z]//g')

  # DANGER signal 1: "launch genuinely failed" (hardened-launcher's only retry path)
  if echo "$clean_line" | grep -qE "launch genuinely failed|launch failed; cleanup \+ retry"; then
    echo "[kill_switch] $(date -u '+%Y-%m-%dT%H:%M:%SZ') DANGER: '${clean_line}'" | tee -a "$KILL_LOG"
    echo "[kill_switch] killing launcher and ANY new acquisition attempts" | tee -a "$KILL_LOG"
    LAUNCHER_PID=$(cat "$LOCK_PATH" 2>/dev/null || echo "")
    if [ -n "$LAUNCHER_PID" ]; then
      kill -KILL "$LAUNCHER_PID" 2>/dev/null || true
      pkill -KILL -P "$LAUNCHER_PID" 2>/dev/null || true
    fi
    pkill -KILL -f smart_launch_cell2 2>/dev/null || true
    # Also kill any sky launch processes that might restart
    pkill -KILL -f "sky.*launch.*cell2wiki" 2>/dev/null || true
    rm -f "$LOCK_PATH" 2>/dev/null || true
    echo "[kill_switch] $(date -u '+%Y-%m-%dT%H:%M:%SZ') launcher KILLED; exiting kill_switch" | tee -a "$KILL_LOG"
    exit 0
  fi

  # DANGER signal 2: "launching cluster=" with a name DIFFERENT from the first
  if echo "$clean_line" | grep -qE "launching cluster=cell2wiki-[0-9]+"; then
    NEW_CLUSTER=$(echo "$clean_line" | grep -oE "cell2wiki-[0-9]+" | head -1)
    if [ -n "$NEW_CLUSTER" ] && [ "$NEW_CLUSTER" != "$FIRST_CLUSTER" ]; then
      echo "[kill_switch] $(date -u '+%Y-%m-%dT%H:%M:%SZ') DANGER: launcher trying to acquire DIFFERENT cluster ${NEW_CLUSTER} (first was ${FIRST_CLUSTER})" | tee -a "$KILL_LOG"
      LAUNCHER_PID=$(cat "$LOCK_PATH" 2>/dev/null || echo "")
      if [ -n "$LAUNCHER_PID" ]; then
        kill -KILL "$LAUNCHER_PID" 2>/dev/null || true
        pkill -KILL -P "$LAUNCHER_PID" 2>/dev/null || true
      fi
      pkill -KILL -f smart_launch_cell2 2>/dev/null || true
      pkill -KILL -f "sky.*launch.*cell2wiki" 2>/dev/null || true
      # Also kill the new cluster that just acquired (don't leak it)
      source /root/skyvenv/bin/activate
      sky down -y "$NEW_CLUSTER" 2>&1 | tail -3 | tee -a "$KILL_LOG"
      rm -f "$LOCK_PATH" 2>/dev/null || true
      echo "[kill_switch] $(date -u '+%Y-%m-%dT%H:%M:%SZ') second cluster torn down + launcher killed; exiting" | tee -a "$KILL_LOG"
      exit 0
    fi
  fi

  # SUCCESS signal: "CELL-2 ACQUIRED + RAN" -> launcher will rsync + sky down naturally; we can exit too
  if echo "$clean_line" | grep -qE "CELL-2 ACQUIRED \+ RAN|smart launch end"; then
    echo "[kill_switch] $(date -u '+%Y-%m-%dT%H:%M:%SZ') job completed successfully; exiting kill_switch (no intervention needed)" | tee -a "$KILL_LOG"
    exit 0
  fi
done
