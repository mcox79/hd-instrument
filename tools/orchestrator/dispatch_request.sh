#!/usr/bin/env bash
# Author a dispatch manifest + commit + push to trigger remote consumer.
# Usage:
#   bash tools/orchestrator/dispatch_request.sh <queue> <name> <script> <prereg> <timeout_s> [skip_smoke]
#
# Writes data/dispatch_requests/<name>.json then commits + pushes.
# hd_dispatch_consumer on remote picks up within ~60s.

set -euo pipefail

if [ $# -lt 5 ]; then
    echo "Usage: $0 <queue> <name> <script> <prereg> <timeout_s> [skip_smoke]" >&2
    exit 2
fi

QUEUE="$1"
NAME="$2"
SCRIPT="$3"
PREREG="$4"
TIMEOUT="$5"
SKIP_SMOKE="${6:-false}"

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

REQ_DIR="data/dispatch_requests"
mkdir -p "$REQ_DIR"
MANIFEST="$REQ_DIR/${NAME}.json"

# Guard: prereg + script MUST be git-tracked + on origin/main; otherwise
# the remote consumer won't see them on its git pull -> dispatch silently
# gate-fails (per Skunkworks 18:29 ratify). Fail loud at dispatch-time.
for f in "$SCRIPT" "$PREREG"; do
    if [ ! -f "$f" ]; then
        echo "[dispatch-request] FAIL: $f does not exist locally" >&2
        exit 3
    fi
    if ! git ls-files --error-unmatch "$f" >/dev/null 2>&1; then
        # Untracked: auto-stage + commit + push (logged clearly per Skunkworks's
        # "auto-stage clearly logged" condition)
        echo "[dispatch-request] AUTO-STAGE: $f (untracked; staging before dispatch)"
        git add "$f"
        git commit -m "dispatch-request auto-stage: $f" 2>&1 | tail -2
        git push origin HEAD:main 2>&1 | tail -2
    else
        # Tracked: ensure it's pushed (not only in local index)
        if ! git diff origin/main -- "$f" --quiet 2>/dev/null; then
            echo "[dispatch-request] AUTO-PUSH: $f (tracked but ahead of origin)"
            git push origin HEAD:main 2>&1 | tail -2
        fi
    fi
done

# Local --self-test gate: catch python syntax errors + obvious cell-side bugs
# BEFORE pushing the manifest (so we don't waste a remote round-trip).
# Skip if HDLAB_SKIP_LOCAL_SELFTEST=1.
if [ -z "${HDLAB_SKIP_LOCAL_SELFTEST:-}" ]; then
    PYTHON_EXE=".venv/Scripts/python.exe"
    if [ ! -x "$PYTHON_EXE" ]; then
        PYTHON_EXE="python"
    fi
    # TIMEOUT_SELFTEST env override (default 120s; raised from 60s after A4 N=2048
    # cell legitimately took 73s and was killed; Skunkworks AFFIRMed 2026-06-18).
    # Per-cell override: HDLAB_SELFTEST_TIMEOUT=300 bash tools/orchestrator/dispatch_request.sh ...
    SELFTEST_TIMEOUT="${HDLAB_SELFTEST_TIMEOUT:-120}"
    echo "[dispatch-request] running local --self-test on $SCRIPT (timeout ${SELFTEST_TIMEOUT}s)..."
    set +e
    timeout "$SELFTEST_TIMEOUT" "$PYTHON_EXE" "$SCRIPT" --self-test >/tmp/selftest.log 2>&1
    SELFTEST_RC=$?
    set -e
    if [ "$SELFTEST_RC" -ne 0 ]; then
        if [ "$SELFTEST_RC" -eq 124 ]; then
            echo "[dispatch-request] FAIL: local --self-test TIMED OUT after ${SELFTEST_TIMEOUT}s (exit 124)" >&2
            echo "[dispatch-request] if the cell genuinely needs longer, retry with HDLAB_SELFTEST_TIMEOUT=300 (or higher)" >&2
        else
            echo "[dispatch-request] FAIL: local --self-test failed (exit $SELFTEST_RC)" >&2
        fi
        echo "[dispatch-request] last 20 lines of self-test output:" >&2
        tail -20 /tmp/selftest.log >&2
        echo "[dispatch-request] fix the cell + retry; manifest NOT pushed" >&2
        exit 5
    fi
    echo "[dispatch-request] local --self-test PASS"
fi

cat > "$MANIFEST" <<EOF
{
  "queue": "$QUEUE",
  "name": "$NAME",
  "script": "$SCRIPT",
  "prereg": "$PREREG",
  "timeout_s": $TIMEOUT,
  "skip_smoke": $SKIP_SMOKE,
  "authored_utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

echo "[dispatch-request] wrote $MANIFEST"

git add "$MANIFEST"
git commit -m "dispatch-request: $NAME -> $QUEUE" 2>&1 | tail -3
git push origin HEAD:main 2>&1 | tail -3

echo "[dispatch-request] DONE: manifest pushed; hd_dispatch_consumer on remote will process within ~60s"
echo "[dispatch-request] tracking:"
echo "   processed -> data/dispatch_requests/processed/${NAME}.json"
echo "   failed    -> data/dispatch_requests/failed/${NAME}.json"
