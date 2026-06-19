#!/usr/bin/env bash
# generic_progress_rsync.sh -- pull cell output from cluster every 5 min.
#
# REQUIRES: $1 = path to cell config (exports CELL_NAME, CLUSTER_PREFIX,
#   REMOTE_OUTPUT_PATH, LOCAL_RESULTS_DIR, PROGRESS_RSYNC_LOG).
#
# Uses --partial so an interrupted transfer resumes cleanly on next tick.
# IMPORTANT: REMOTE_OUTPUT_PATH should be SINGLE-QUOTED in the config so ~
# expands on the SSH-remote side (under the ubuntu user's home), NOT locally
# (where ~ would expand to /root). Cell-2 v3 hit this bug.

set -uo pipefail

if [ -z "${1:-}" ]; then
    echo "ERROR: usage: $0 <path-to-cell-config.sh>" >&2
    exit 2
fi
CONFIG_FILE="$1"
# shellcheck disable=SC1090
source "$CONFIG_FILE"

for required_var in CELL_NAME CLUSTER_PREFIX REMOTE_OUTPUT_PATH LOCAL_RESULTS_DIR PROGRESS_RSYNC_LOG; do
    if [ -z "${!required_var:-}" ]; then
        echo "ERROR: progress_rsync needs $required_var in config" >&2
        exit 2
    fi
done

INTERVAL_MIN="${PROGRESS_RSYNC_INTERVAL_MIN:-5}"
INTERVAL_SEC=$((INTERVAL_MIN * 60))
MAX_CONSEC_FAIL="${PROGRESS_RSYNC_MAX_FAIL:-5}"

source /root/skyvenv/bin/activate

mkdir -p "$LOCAL_RESULTS_DIR"
mkdir -p "$(dirname "$PROGRESS_RSYNC_LOG")"

echo "===== [${CELL_NAME}] progress_rsync start $(date -u '+%Y-%m-%dT%H:%M:%SZ') =====" | tee -a "$PROGRESS_RSYNC_LOG"
echo "[progress_rsync] interval=${INTERVAL_MIN} min; max_consec_fail=${MAX_CONSEC_FAIL}" | tee -a "$PROGRESS_RSYNC_LOG"

# Wait for the launcher's cluster to come UP
CLUSTER=""
while [ -z "$CLUSTER" ]; do
    CLUSTER=$(sky status 2>/dev/null | grep -oE "${CLUSTER_PREFIX}-[0-9]+" | head -1)
    [ -z "$CLUSTER" ] && sleep 30
done
echo "[progress_rsync] LOCKED to cluster: $CLUSTER" | tee -a "$PROGRESS_RSYNC_LOG"

CONSEC=0
N_PREV=0
# Count whatever output files / shards may already be locally
shopt -s nullglob
while true; do
    ts=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

    STATUS_LINE=$(sky status 2>/dev/null | grep "$CLUSTER" | head -1 || true)
    if [ -z "$STATUS_LINE" ]; then
        echo "[${ts}] cluster $CLUSTER no longer in sky status -- exit progress_rsync" | tee -a "$PROGRESS_RSYNC_LOG"
        break
    fi

    echo "[${ts}] rsync from $CLUSTER" | tee -a "$PROGRESS_RSYNC_LOG"
    rsync -av --partial --timeout=120 \
        -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=30" \
        "${CLUSTER}:${REMOTE_OUTPUT_PATH}" \
        "${LOCAL_RESULTS_DIR}/" >> "$PROGRESS_RSYNC_LOG" 2>&1
    RC=$?

    if [ "$RC" -eq 0 ]; then
        CONSEC=0
        N_NOW=$(find "$LOCAL_RESULTS_DIR" -maxdepth 2 -type f 2>/dev/null | wc -l)
        DELTA=$((N_NOW - N_PREV))
        SIZE=$(du -sh "$LOCAL_RESULTS_DIR" 2>/dev/null | cut -f1 || echo "?")
        echo "[${ts}] rsync OK: ${N_NOW} files local (${SIZE}; +${DELTA} since last tick)" | tee -a "$PROGRESS_RSYNC_LOG"
        N_PREV=$N_NOW
    else
        CONSEC=$((CONSEC + 1))
        echo "[${ts}] rsync exit=${RC} (consec_fail=${CONSEC})" | tee -a "$PROGRESS_RSYNC_LOG"
        if [ "$CONSEC" -ge "$MAX_CONSEC_FAIL" ]; then
            echo "[${ts}] ${MAX_CONSEC_FAIL} consecutive failures -- cluster likely dead; exit" | tee -a "$PROGRESS_RSYNC_LOG"
            break
        fi
    fi

    sleep "$INTERVAL_SEC"
done

echo "===== [${CELL_NAME}] progress_rsync end $(date -u '+%Y-%m-%dT%H:%M:%SZ') =====" | tee -a "$PROGRESS_RSYNC_LOG"
