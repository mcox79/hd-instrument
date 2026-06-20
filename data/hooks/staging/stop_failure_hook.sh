#!/usr/bin/env bash
# Phase 1.2 StopFailure hook (per Director hardening proposal)
# STAGING ONLY -- not yet registered.
#
# Purpose: mitigate all-stop-at-once failures from Anthropic API transient overload (529)
# + shared rate-limit contention. Implements exponential backoff + jitter + retry cap.
#
# Per Orchestrator runtime-owner: this hook does NOT trigger Store-writes; pure-decision logic.
# Per Skunkworks: no cert-impact (infra).
#
# Failure modes handled:
#   - overloaded (HTTP 529 transient): backoff + retry up to MAX_RETRIES
#   - rate_limit (per-minute account cap): backoff with longer base; same retry cap
#   - permission_denied / authentication_error: do NOT retry (give up immediately)
#   - other errors: log + give up (let the harness surface)
#
# Backoff formula: base * 2^attempt + random[0..jitter_max] seconds
#   default base=30, jitter_max=15, MAX_RETRIES=5
#   attempt 0: 30 + 0..15 = 30-45s
#   attempt 1: 60 + 0..15 = 60-75s
#   attempt 2: 120 + 0..15 = 120-135s
#   attempt 3: 240 + 0..15 = 240-255s
#   attempt 4: 480 + 0..15 = 480-495s  (~8 min)
#   total worst-case ~16 min before giving up
#
# Argument: $1 = session name
# Hook protocol: reads JSON error payload from stdin; emits JSON decision (retry|exit).

set -euo pipefail

SESSION="${1:-unknown}"
INPUT="$(cat 2>/dev/null || echo '{}')"

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
STATE_DIR="$REPO_ROOT/data/api_failures"
LOG_FILE="$STATE_DIR/${SESSION}.jsonl"
ATTEMPT_FILE="$STATE_DIR/${SESSION}.attempt"

mkdir -p "$STATE_DIR" 2>/dev/null

# Extract error class (best-effort; harness-format-dependent)
ERROR_TYPE="$(echo "$INPUT" | jq -r '.error.type // .type // "unknown"' 2>/dev/null || echo 'unknown')"
ERROR_MSG="$(echo "$INPUT" | jq -r '.error.message // .message // ""' 2>/dev/null || echo '')"
HTTP_STATUS="$(echo "$INPUT" | jq -r '.error.status // .status // 0' 2>/dev/null || echo '0')"

# Determine retry-eligible
RETRYABLE=false
case "$ERROR_TYPE" in
    overloaded_error|overloaded)
        RETRYABLE=true ; BASE_SEC=30 ;;
    rate_limit_error|rate_limit|rate_limited)
        RETRYABLE=true ; BASE_SEC=60 ;;  # longer base for rate limits
    *)
        case "$HTTP_STATUS" in
            529) RETRYABLE=true ; BASE_SEC=30 ;;
            429) RETRYABLE=true ; BASE_SEC=60 ;;
            *)   RETRYABLE=false ; BASE_SEC=0 ;;
        esac ;;
esac

MAX_RETRIES="${HD_STOP_FAILURE_MAX_RETRIES:-5}"
JITTER_MAX="${HD_STOP_FAILURE_JITTER_MAX:-15}"

# Log the failure
NOW="$(date -u '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || echo 'unknown')"
LOG_ENTRY="$(jq -nc \
    --arg ts "$NOW" \
    --arg session "$SESSION" \
    --arg etype "$ERROR_TYPE" \
    --arg emsg "$ERROR_MSG" \
    --arg http "$HTTP_STATUS" \
    --arg retryable "$RETRYABLE" \
    '{ts:$ts, session:$session, error_type:$etype, message:$emsg, http_status:$http, retryable:$retryable}' \
    2>/dev/null)"
if [ -n "$LOG_ENTRY" ]; then
    echo "$LOG_ENTRY" >> "$LOG_FILE" 2>/dev/null || true
fi

if [ "$RETRYABLE" != "true" ]; then
    # Non-retryable. Reset attempt counter for next event. Exit (let harness surface).
    rm -f "$ATTEMPT_FILE" 2>/dev/null || true
    exit 0
fi

# Read current attempt counter (reset by successful turn elsewhere)
[ -f "$ATTEMPT_FILE" ] || echo "0" > "$ATTEMPT_FILE"
ATTEMPT="$(cat "$ATTEMPT_FILE" 2>/dev/null || echo '0')"
if ! [[ "$ATTEMPT" =~ ^[0-9]+$ ]]; then
    ATTEMPT=0
fi

if [ "$ATTEMPT" -ge "$MAX_RETRIES" ]; then
    # Retry budget exhausted. Reset counter for next event. Exit.
    rm -f "$ATTEMPT_FILE" 2>/dev/null || true
    exit 0
fi

# Compute backoff + jitter
EXP=$((BASE_SEC * (2 ** ATTEMPT)))
JITTER=$((RANDOM % (JITTER_MAX + 1)))
WAIT_SEC=$((EXP + JITTER))

# Increment attempt counter
echo "$((ATTEMPT + 1))" > "$ATTEMPT_FILE"

# Emit retry decision per Claude Code hook protocol
# (Exact JSON shape TBD per harness; placeholder shape below)
REASON="${ERROR_TYPE} retry attempt $((ATTEMPT + 1))/${MAX_RETRIES}; backoff ${WAIT_SEC}s (base ${BASE_SEC} + jitter ${JITTER})"
printf '{"decision":"retry","wait_sec":%d,"reason":%s}\n' "$WAIT_SEC" "$(echo "$REASON" | jq -Rs .)"
exit 0
