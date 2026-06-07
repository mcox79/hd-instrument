#!/usr/bin/env bash
# safety_launch_all.sh -- orchestrator: fire all 4 safety processes for a cell.
#
# Usage: safety_launch_all.sh <path-to-cell-config.sh>
#
# Starts:
#   1. generic_smart_launch.sh   (foreground - this script's main)
#   2. generic_kill_switch.sh    (background)
#   3. generic_progress_rsync.sh (background)
#   4. generic_watchdog.sh       (background)
#
# All 4 background workers are killed when the smart launcher returns (success
# or failure) via TRAP. The state of each is logged.

set -uo pipefail

if [ -z "${1:-}" ]; then
    echo "ERROR: usage: $0 <path-to-cell-config.sh>" >&2
    exit 2
fi
CONFIG_FILE="$(realpath "$1")"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: config file not found: $CONFIG_FILE" >&2
    exit 2
fi
# shellcheck disable=SC1090
source "$CONFIG_FILE"

for required_var in CELL_NAME CLUSTER_PREFIX LAUNCHER_LOG KILL_SWITCH_LOG \
                   PROGRESS_RSYNC_LOG WATCHDOG_LOG LAUNCHER_LOCK_PATH; do
    if [ -z "${!required_var:-}" ]; then
        echo "ERROR: config $CONFIG_FILE missing required var: $required_var" >&2
        exit 2
    fi
done

SAFETY_DIR="$(dirname "$(realpath "$0")")"

echo "===== [${CELL_NAME}] safety_launch_all start $(date -u '+%Y-%m-%dT%H:%M:%SZ') ====="
echo "Config: $CONFIG_FILE"
echo "Safety scripts dir: $SAFETY_DIR"

# CRITICAL 2026-06-07: truncate ALL logs at orchestrator start. Without this,
# the kill_switch background worker reads stale "launch genuinely failed"
# messages from previous failed runs (left in $LAUNCHER_LOG) and immediately
# kills the new launcher within 1 sec. Rotate prior logs to .prev to preserve
# evidence.
for L in "$LAUNCHER_LOG" "$KILL_SWITCH_LOG" "$PROGRESS_RSYNC_LOG" "$WATCHDOG_LOG"; do
    if [ -f "$L" ]; then
        mv "$L" "${L}.prev"
    fi
    : > "$L"
done

# Track background workers so we can kill them on exit
BG_PIDS=()

# Fire kill_switch in background (waits for first cluster name to appear in log)
echo "[orch] firing kill_switch..."
nohup bash "$SAFETY_DIR/generic_kill_switch.sh" "$CONFIG_FILE" \
    > /tmp/${CLUSTER_PREFIX}_kill_switch_stdout.log 2>&1 &
KILL_SWITCH_PID=$!
BG_PIDS+=($KILL_SWITCH_PID)
echo "[orch] kill_switch PID=$KILL_SWITCH_PID"

# Fire watchdog in background (independent of cluster state; starts immediately)
echo "[orch] firing watchdog..."
nohup bash "$SAFETY_DIR/generic_watchdog.sh" "$CONFIG_FILE" \
    > /tmp/${CLUSTER_PREFIX}_watchdog_stdout.log 2>&1 &
WATCHDOG_PID=$!
BG_PIDS+=($WATCHDOG_PID)
echo "[orch] watchdog PID=$WATCHDOG_PID"

# Fire progress_rsync in background (waits for cluster UP before pulling)
echo "[orch] firing progress_rsync..."
nohup bash "$SAFETY_DIR/generic_progress_rsync.sh" "$CONFIG_FILE" \
    > /tmp/${CLUSTER_PREFIX}_progress_rsync_stdout.log 2>&1 &
RSYNC_PID=$!
BG_PIDS+=($RSYNC_PID)
echo "[orch] progress_rsync PID=$RSYNC_PID"

# Cleanup all background workers on exit
cleanup() {
    echo "[orch] cleanup: killing bg workers ${BG_PIDS[*]}"
    for p in "${BG_PIDS[@]}"; do
        kill "$p" 2>/dev/null || true
    done
    sleep 2
    for p in "${BG_PIDS[@]}"; do
        kill -KILL "$p" 2>/dev/null || true
    done
}
trap cleanup EXIT INT TERM

# Run the smart launcher in foreground (this blocks until job completes or fails)
echo "[orch] running smart launcher (foreground)..."
bash "$SAFETY_DIR/generic_smart_launch.sh" "$CONFIG_FILE"
LAUNCHER_RC=$?

echo "===== [${CELL_NAME}] safety_launch_all end $(date -u '+%Y-%m-%dT%H:%M:%SZ') (launcher_rc=$LAUNCHER_RC) ====="
exit $LAUNCHER_RC
