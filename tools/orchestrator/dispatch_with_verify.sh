#!/usr/bin/env bash
# Dispatch a cell to a remote queue + VERIFY it actually landed.
# Resilient to SSH transients (bounded retry budget); definitive answer.
#
# Usage:
#   bash tools/orchestrator/dispatch_with_verify.sh <queue> <name> <script> <prereg> <timeout_s>
#
# Returns:
#   exit 0 + "DISPATCH OK <name>" if entry confirmed in remote queue.json
#   exit 1 + "DISPATCH FAIL" with reason after MAX_ATTEMPTS

set -uo pipefail

if [ $# -lt 5 ]; then
    echo "Usage: $0 <queue> <name> <script> <prereg> <timeout_s>" >&2
    exit 2
fi

QUEUE="$1"
NAME="$2"
SCRIPT="$3"
PREREG="$4"
TIMEOUT="$5"

MAX_ATTEMPTS=5
BACKOFF_BASE=10  # seconds; multiplied by attempt number

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

verify_in_queue() {
    # Returns 0 if NAME found in remote queue.json, 1 otherwise
    local result
    result=$(ssh -o ConnectTimeout=15 -o BatchMode=yes marsh@home \
        "powershell -NoProfile -Command \"if (Test-Path 'C:/dev/hd-instrument/data/$QUEUE/queue.json') { Get-Content 'C:/dev/hd-instrument/data/$QUEUE/queue.json' -Raw | Select-String -SimpleMatch '$NAME' -Quiet } else { 'FALSE' }\"" 2>/dev/null | tr -d '[:space:]')
    if [ "$result" = "True" ]; then
        return 0
    fi
    return 1
}

for attempt in $(seq 1 $MAX_ATTEMPTS); do
    echo "[dispatch-verify] attempt $attempt/$MAX_ATTEMPTS"

    # Already there? (idempotency)
    if verify_in_queue; then
        echo "DISPATCH OK $NAME (already present in queue; idempotent)"
        exit 0
    fi

    # Call queue_add
    cd "$REPO_ROOT" || exit 1
    bash tools/orchestrator/queue_add.sh "$QUEUE" "$NAME" "$SCRIPT" "$PREREG" "$TIMEOUT" 2>&1 | tail -5

    # Post-verify (wait a beat for write to settle)
    sleep 3
    if verify_in_queue; then
        echo "DISPATCH OK $NAME (confirmed in remote queue.json)"
        exit 0
    fi

    # Failed; backoff
    if [ "$attempt" -lt $MAX_ATTEMPTS ]; then
        backoff=$((BACKOFF_BASE * attempt))
        echo "[dispatch-verify] not confirmed; backoff ${backoff}s before retry"
        sleep $backoff
    fi
done

echo "DISPATCH FAIL $NAME (after $MAX_ATTEMPTS attempts; SSH or queue-write transient persists)"
exit 1
