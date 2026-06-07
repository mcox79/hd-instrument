#!/usr/bin/env bash
# generic_kill_switch.sh -- prevent the launcher from spawning a SECOND cluster.
#
# REQUIRES: $1 = path to cell config (exports CLUSTER_PREFIX, LAUNCHER_LOG,
#   KILL_SWITCH_LOG, LAUNCHER_LOCK_PATH).
#
# Watches the launcher log for danger signals (any 2nd cluster acquisition OR
# 'launch genuinely failed' message). Kills launcher PID + lock + sky launch
# subproc + tears down any second cluster that slipped through.

set -uo pipefail

if [ -z "${1:-}" ]; then
    echo "ERROR: usage: $0 <path-to-cell-config.sh>" >&2
    exit 2
fi
CONFIG_FILE="$1"
# shellcheck disable=SC1090
source "$CONFIG_FILE"

for required_var in CELL_NAME CLUSTER_PREFIX LAUNCHER_LOG KILL_SWITCH_LOG LAUNCHER_LOCK_PATH; do
    if [ -z "${!required_var:-}" ]; then
        echo "ERROR: kill_switch needs $required_var in config" >&2
        exit 2
    fi
done

source /root/skyvenv/bin/activate

mkdir -p "$(dirname "$KILL_SWITCH_LOG")"
echo "===== [${CELL_NAME}] kill_switch start $(date -u '+%Y-%m-%dT%H:%M:%SZ') =====" | tee -a "$KILL_SWITCH_LOG"

# Wait for the launcher's first acquired cluster
FIRST_CLUSTER=""
while [ -z "$FIRST_CLUSTER" ]; do
    FIRST_CLUSTER=$(grep -oE "launching cluster=${CLUSTER_PREFIX}-[0-9]+" "$LAUNCHER_LOG" 2>/dev/null | head -1 | sed 's/launching cluster=//')
    [ -z "$FIRST_CLUSTER" ] && sleep 5
done
echo "[kill_switch] $(date -u '+%Y-%m-%dT%H:%M:%SZ') LOCKED to first cluster: ${FIRST_CLUSTER}" | tee -a "$KILL_SWITCH_LOG"
echo "[kill_switch] any 'launching cluster=' for a DIFFERENT name will trigger immediate launcher kill" | tee -a "$KILL_SWITCH_LOG"

# 2026-06-07 BUG FIX: was `tail -n +1` which reads the log from line 1,
# including STALE "launch genuinely failed" strings from previous failed
# runs, triggering immediate kill of the new launcher. Now `tail -n 0 -F`
# reads only NEW lines appended after the kill_switch starts.
tail -n 0 -F "$LAUNCHER_LOG" 2>/dev/null | while IFS= read -r line; do
    clean_line=$(echo "$line" | sed 's/\x1b\[[0-9;]*[a-zA-Z]//g')

    # Danger 1: launcher signals genuine failure (about to teardown + retry from scratch)
    if echo "$clean_line" | grep -qE "launch genuinely failed|launch failed; cleanup \+ retry"; then
        echo "[kill_switch] $(date -u '+%Y-%m-%dT%H:%M:%SZ') DANGER: '${clean_line}'" | tee -a "$KILL_SWITCH_LOG"
        LAUNCHER_PID=$(cat "$LAUNCHER_LOCK_PATH" 2>/dev/null || echo "")
        if [ -n "$LAUNCHER_PID" ]; then
            kill -KILL "$LAUNCHER_PID" 2>/dev/null || true
            pkill -KILL -P "$LAUNCHER_PID" 2>/dev/null || true
        fi
        pkill -KILL -f "generic_smart_launch.sh.*${CLUSTER_PREFIX}" 2>/dev/null || true
        pkill -KILL -f "sky.*launch.*${CLUSTER_PREFIX}" 2>/dev/null || true
        rm -f "$LAUNCHER_LOCK_PATH" 2>/dev/null || true
        echo "[kill_switch] $(date -u '+%Y-%m-%dT%H:%M:%SZ') launcher KILLED; exiting" | tee -a "$KILL_SWITCH_LOG"
        exit 0
    fi

    # Danger 2: a NEW cluster name appears in the log (different from FIRST_CLUSTER)
    if echo "$clean_line" | grep -qE "launching cluster=${CLUSTER_PREFIX}-[0-9]+"; then
        NEW_CLUSTER=$(echo "$clean_line" | grep -oE "${CLUSTER_PREFIX}-[0-9]+" | head -1)
        if [ -n "$NEW_CLUSTER" ] && [ "$NEW_CLUSTER" != "$FIRST_CLUSTER" ]; then
            echo "[kill_switch] $(date -u '+%Y-%m-%dT%H:%M:%SZ') DANGER: 2nd cluster ${NEW_CLUSTER} (first was ${FIRST_CLUSTER})" | tee -a "$KILL_SWITCH_LOG"
            LAUNCHER_PID=$(cat "$LAUNCHER_LOCK_PATH" 2>/dev/null || echo "")
            if [ -n "$LAUNCHER_PID" ]; then
                kill -KILL "$LAUNCHER_PID" 2>/dev/null || true
                pkill -KILL -P "$LAUNCHER_PID" 2>/dev/null || true
            fi
            pkill -KILL -f "generic_smart_launch.sh.*${CLUSTER_PREFIX}" 2>/dev/null || true
            pkill -KILL -f "sky.*launch.*${CLUSTER_PREFIX}" 2>/dev/null || true
            sky down -y "$NEW_CLUSTER" 2>&1 | tail -3 | tee -a "$KILL_SWITCH_LOG"
            rm -f "$LAUNCHER_LOCK_PATH" 2>/dev/null || true
            echo "[kill_switch] $(date -u '+%Y-%m-%dT%H:%M:%SZ') 2nd cluster torn down + launcher killed; exiting" | tee -a "$KILL_SWITCH_LOG"
            exit 0
        fi
    fi

    # Success signal -- launcher will rsync + sky down naturally; we exit too
    if echo "$clean_line" | grep -qE "ACQUIRED \+ RAN|smart launch end"; then
        echo "[kill_switch] $(date -u '+%Y-%m-%dT%H:%M:%SZ') job completed; exiting (no intervention needed)" | tee -a "$KILL_SWITCH_LOG"
        exit 0
    fi
done
