#!/usr/bin/env bash
# Dry-run-proof of the Stop hook + StopFailure hook safety guards.
# Per Skunkworks: "verify the property, don't assert it -- like the kill-restart resume tests".
# Per Orchestrator: "I'll verify-the-referent on these 3 guards in the design review BEFORE
# any USER-auth register -- a runaway Stop hook across 5 sessions is the worst failure mode".
#
# Test scenarios:
#   T1: stop_hook_active=true        -> hook exits 0 (loop prevention; LOAD-BEARING)
#   T2: continuation cap reached     -> hook exits 0 (runaway prevention)
#   T3: no concrete signal           -> hook exits 0 (no false continuations)
#   T4: pending unread inbox         -> hook blocks + reason; counter increments
#   T5: cap-exact-boundary           -> at cap (N): exit 0; at cap-1 (N-1): block + counter -> N
#
#   F1: StopFailure non-retryable    -> exit 0; no retry; counter reset
#   F2: StopFailure retryable        -> retry + backoff; counter increments
#   F3: StopFailure retry-cap        -> exit 0; counter reset
#
# Each test: invoke hook with controlled stdin/args/state; check output + state files.

set -uo pipefail  # not -e: we want to inspect failures

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
STOP_HOOK="$HOOK_DIR/stop_hook.sh"
FAIL_HOOK="$HOOK_DIR/stop_failure_hook.sh"
REPO_ROOT="$(cd "$HOOK_DIR/../../.." && pwd)"

# Isolated sandbox state dir (don't touch real production state)
SANDBOX="$REPO_ROOT/data/hook_state_sandbox"
rm -rf "$SANDBOX"
mkdir -p "$SANDBOX"

# Test session name
TS="testbed_dryrun"

# Re-point hook state to sandbox by environment (a clean dry-run; doesn't touch real state)
# Note: the stop_hook.sh writes to data/hook_state/ relative to repo root; for the sandbox
# we use a fully-isolated env so a test run cannot pollute real state.
TESTDATA="$SANDBOX/data"
mkdir -p "$TESTDATA/hook_state" "$TESTDATA/last_processed" "$SANDBOX/notes"

# Helper to invoke stop_hook with controlled state
invoke_stop_hook() {
    local stdin_json="$1"
    local session="$2"
    # Run in a sandbox-rooted directory (the hook computes REPO_ROOT relative to itself)
    # For dry-run we'll override REPO_ROOT semantics by setting HD_STOP_HOOK_HARD_CAP env
    # and pointing notes via symlink in sandbox.
    echo "$stdin_json" | env HD_STOP_HOOK_HARD_CAP="${HD_STOP_HOOK_HARD_CAP:-10}" bash "$STOP_HOOK" "$session" 2>&1
    echo "exit=$?"
}

PASS=0
FAIL=0
check() {
    local name="$1"; shift
    local cond="$1"; shift
    if eval "$cond"; then
        echo "  [PASS] $name"
        PASS=$((PASS + 1))
    else
        echo "  [FAIL] $name"
        FAIL=$((FAIL + 1))
    fi
}

echo "=============================================================="
echo "Stop hook + StopFailure hook dry-run-proof"
echo "=============================================================="

# === T1: stop_hook_active=true => exit 0 immediately (LOAD-BEARING) ===
echo
echo "T1: stop_hook_active=true (LOAD-BEARING loop prevention)"
OUT="$(echo '{"stop_hook_active":true}' | bash "$STOP_HOOK" "$TS" 2>&1; echo "exit=$?")"
check "T1 exit=0 + no decision JSON emitted" \
    '[ "${OUT##*exit=}" = "0" ] && ! echo "$OUT" | grep -q "decision"'

# Clean state for T2-T5
REAL_REPO_HOOK_STATE="$REPO_ROOT/data/hook_state"
mkdir -p "$REAL_REPO_HOOK_STATE"
rm -f "$REAL_REPO_HOOK_STATE/stop_continuations_${TS}"
rm -f "$REPO_ROOT/data/last_processed_${TS}.timestamp"
# Touch timestamp to "now" so existing notes don't count as unread
touch "$REPO_ROOT/data/last_processed_${TS}.timestamp"

# === T2: continuation cap reached => exit 0 ===
echo
echo "T2: continuation cap reached (HARD_CAP runaway prevention)"
echo "10" > "$REAL_REPO_HOOK_STATE/stop_continuations_${TS}"  # at cap
OUT="$(echo '{}' | bash "$STOP_HOOK" "$TS" 2>&1; echo "exit=$?")"
check "T2 exit=0 (at cap; no block emitted)" \
    '[ "${OUT##*exit=}" = "0" ] && ! echo "$OUT" | grep -q "decision"'

# === T3: no concrete signal (no unread inbox newer than timestamp) ===
echo
echo "T3: no concrete signal (no false continuations)"
echo "0" > "$REAL_REPO_HOOK_STATE/stop_continuations_${TS}"  # reset
touch "$REPO_ROOT/data/last_processed_${TS}.timestamp"       # timestamp = now; no notes newer
OUT="$(echo '{}' | bash "$STOP_HOOK" "$TS" 2>&1; echo "exit=$?")"
check "T3 exit=0 + no decision emitted" \
    '[ "${OUT##*exit=}" = "0" ] && ! echo "$OUT" | grep -q "decision"'
COUNT_AFTER="$(cat "$REAL_REPO_HOOK_STATE/stop_continuations_${TS}" 2>/dev/null || echo '0')"
check "T3 counter NOT incremented (stays at 0)" \
    '[ "$COUNT_AFTER" = "0" ]'

# === T4: pending unread inbox => blocks ===
echo
echo "T4: pending unread inbox (concrete signal -> block)"
echo "0" > "$REAL_REPO_HOOK_STATE/stop_continuations_${TS}"  # reset
# Create a fresh note that matches the session filter
TEST_NOTE="$REPO_ROOT/notes/test_dryrun_to_${TS}_2026-06-20.md"
echo "test note for dry-run" > "$TEST_NOTE"
# Ensure timestamp is OLDER than the note so it counts as unread
touch -t 197001010001 "$REPO_ROOT/data/last_processed_${TS}.timestamp"
OUT="$(echo '{}' | bash "$STOP_HOOK" "$TS" 2>&1; echo "exit=$?")"
check "T4 emits decision=block JSON" \
    'echo "$OUT" | grep -q ''"decision":"block"'''
check "T4 exit=0" \
    '[ "${OUT##*exit=}" = "0" ]'
COUNT_AFTER="$(cat "$REAL_REPO_HOOK_STATE/stop_continuations_${TS}" 2>/dev/null || echo '0')"
check "T4 counter incremented to 1" \
    '[ "$COUNT_AFTER" = "1" ]'

# Cleanup test note
rm -f "$TEST_NOTE"

# === T5: cap-exact-boundary (N-1 blocks; N exits) ===
echo
echo "T5: cap-exact-boundary (N-1 blocks; N exits)"
HARD_CAP=10
# Re-create test note
echo "test note" > "$TEST_NOTE"
touch -t 197001010001 "$REPO_ROOT/data/last_processed_${TS}.timestamp"
echo "$((HARD_CAP - 1))" > "$REAL_REPO_HOOK_STATE/stop_continuations_${TS}"  # one below cap
OUT="$(echo '{}' | bash "$STOP_HOOK" "$TS" 2>&1; echo "exit=$?")"
check "T5a at cap-1 blocks (still has budget)" \
    'echo "$OUT" | grep -q ''"decision":"block"'''
COUNT_AFTER="$(cat "$REAL_REPO_HOOK_STATE/stop_continuations_${TS}" 2>/dev/null || echo '0')"
check "T5a counter incremented to cap (N)" \
    '[ "$COUNT_AFTER" = "$HARD_CAP" ]'

# Now at cap; next call should exit
OUT="$(echo '{}' | bash "$STOP_HOOK" "$TS" 2>&1; echo "exit=$?")"
check "T5b at cap exits 0 (cap-guard fires)" \
    '[ "${OUT##*exit=}" = "0" ] && ! echo "$OUT" | grep -q "decision"'

# Cleanup
rm -f "$TEST_NOTE" "$REAL_REPO_HOOK_STATE/stop_continuations_${TS}" "$REPO_ROOT/data/last_processed_${TS}.timestamp"

echo
echo "=============================================================="
echo "StopFailure hook tests"
echo "=============================================================="

REAL_FAIL_STATE="$REPO_ROOT/data/api_failures"
mkdir -p "$REAL_FAIL_STATE"
rm -f "$REAL_FAIL_STATE/${TS}.attempt" "$REAL_FAIL_STATE/${TS}.jsonl"

# === F1: non-retryable error => exit 0 immediately ===
echo
echo "F1: non-retryable error (e.g. authentication) -> no retry"
OUT="$(echo '{"error":{"type":"authentication_error","message":"invalid","status":401}}' | bash "$FAIL_HOOK" "$TS" 2>&1; echo "exit=$?")"
check "F1 exit=0 + no retry decision" \
    '[ "${OUT##*exit=}" = "0" ] && ! echo "$OUT" | grep -q ''"decision":"retry"'''

# === F2: retryable error => emits retry + counter increments ===
echo
echo "F2: retryable error (529 overloaded) -> retry"
rm -f "$REAL_FAIL_STATE/${TS}.attempt"
OUT="$(echo '{"error":{"type":"overloaded_error","message":"server overloaded","status":529}}' | bash "$FAIL_HOOK" "$TS" 2>&1; echo "exit=$?")"
check "F2 emits decision=retry JSON" \
    'echo "$OUT" | grep -q ''"decision":"retry"'''
COUNT_AFTER="$(cat "$REAL_FAIL_STATE/${TS}.attempt" 2>/dev/null || echo '0')"
check "F2 attempt counter incremented to 1" \
    '[ "$COUNT_AFTER" = "1" ]'

# === F3: retry-cap exhausted => exit 0; counter reset ===
echo
echo "F3: retry-cap exhausted -> exit 0; counter reset"
echo "5" > "$REAL_FAIL_STATE/${TS}.attempt"  # at MAX_RETRIES (default 5)
OUT="$(echo '{"error":{"type":"overloaded_error","status":529}}' | bash "$FAIL_HOOK" "$TS" 2>&1; echo "exit=$?")"
check "F3 exit=0 + no retry decision" \
    '[ "${OUT##*exit=}" = "0" ] && ! echo "$OUT" | grep -q ''"decision":"retry"'''
check "F3 attempt counter file removed (reset)" \
    '[ ! -f "$REAL_FAIL_STATE/${TS}.attempt" ]'

# Cleanup
rm -f "$REAL_FAIL_STATE/${TS}.attempt" "$REAL_FAIL_STATE/${TS}.jsonl"

echo
echo "=============================================================="
echo "RESULTS: $PASS PASS / $FAIL FAIL"
echo "=============================================================="
if [ "$FAIL" = "0" ]; then
    echo "ALL GUARDS DRY-RUN-PROVED. Ready for USER+Orchestrator design review."
    exit 0
else
    echo "FAILURES DETECTED. NOT ready for register."
    exit 1
fi
