#!/usr/bin/env bash
# Phase 1.1 Stop hook (per Director hardening proposal + Orchestrator runtime-spec + Skunkworks cert-integrity input)
# STAGING ONLY -- not yet registered. Builds in data/hooks/staging/ for USER+Orchestrator review.
#
# Purpose: prevent idle-one-by-one deaths by continuing the session when concrete work pending.
#
# CRITICAL safety guards (load-bearing per Orchestrator + the documented ~50min Stop-hook loop bug):
#   GUARD 1: stop_hook_active flag honored FIRST (loop prevention; the load-bearing safety gate)
#   GUARD 2: HARD_CAP continuation counter (per-session; prevents runaway)
#   GUARD 3: Concrete signal gate (only block on real pending work; not "always block")
#
# Skunkworks cert-integrity invariant: this hook does NOT trigger Store-writes (only decides
# session-continuation; the session itself follows the existing single-writer-window discipline).
# Auto-continue does NOT race the NULL-seam hazard.
#
# Coexistence with existing v5 notes_monitor.sh: this hook reads notes/ via a per-session
# `data/last_processed_<session>.timestamp` file the monitor does NOT touch -> no race.
#
# Usage (NOT YET REGISTERED): would be configured per-session in Claude Code settings as Stop hook.
# Argument: $1 = session name (skunkworks|research|exp_dev|testbed|orchestrator)
#
# Hook protocol: reads JSON from stdin; emits JSON decision OR exits 0.

set -euo pipefail

SESSION="${1:-}"
if [ -z "$SESSION" ]; then
    # No session arg; fail-safe to no-op stop (never block without session context)
    exit 0
fi

# === GUARD 1: stop_hook_active (load-bearing loop prevention) ===
# Read hook input JSON from stdin (Claude Code hook protocol)
INPUT="$(cat 2>/dev/null || echo '{}')"
STOP_HOOK_ACTIVE="$(echo "$INPUT" | jq -r '.stop_hook_active // false' 2>/dev/null || echo 'false')"
if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
    # If we are already inside a Stop-hook-triggered continuation, do NOT block again.
    # This is THE load-bearing gate against the documented ~50min loop bug.
    exit 0
fi

# === GUARD 2: HARD_CAP continuation counter (per-session runaway prevention) ===
REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"  # data/hooks/staging/.. = repo root
CONT_DIR="$REPO_ROOT/data/hook_state"
CONT_FILE="$CONT_DIR/stop_continuations_${SESSION}"
HARD_CAP="${HD_STOP_HOOK_HARD_CAP:-10}"   # default 10; overridable via env for testing

mkdir -p "$CONT_DIR" 2>/dev/null
if [ ! -f "$CONT_FILE" ]; then
    echo "0" > "$CONT_FILE"
fi
COUNT="$(cat "$CONT_FILE" 2>/dev/null || echo '0')"
if ! [[ "$COUNT" =~ ^[0-9]+$ ]]; then
    COUNT=0
fi

if [ "$COUNT" -ge "$HARD_CAP" ]; then
    # Cap reached. Let session truly stop. Reset counter for next real-USER-input cycle.
    # NOTE: continuation counter is reset by the session itself when it observes
    # a real USER-input (not a Stop-hook-triggered continuation). For staging,
    # the reset mechanism is TBD; the cap is the safety floor.
    exit 0
fi

# === GUARD 3: Concrete signal gate ===
# Only block (continue) if there is REAL pending work. Signals checked in order:
#   3a. Unread inbox notes for this session (newer than per-session last-processed timestamp)
#   3b. (future) Pending TODO marker
#   3c. (future) Cell-in-flight marker
TS_FILE="$REPO_ROOT/data/last_processed_${SESSION}.timestamp"
if [ ! -f "$TS_FILE" ]; then
    # First-run: epoch zero so existing notes don't count as unread.
    # (Adjust at install time: touch to current date so the hook starts from "fresh state".)
    touch -t 197001010001 "$TS_FILE" 2>/dev/null || true
fi

NOTES_DIR="$REPO_ROOT/notes"
HAVE_UNREAD=""
if [ -d "$NOTES_DIR" ]; then
    # Match same filter convention as v5 notes_monitor.sh (filenames containing
    # SESSION or to_all or _all_; exclude own-outgoing prefix)
    HAVE_UNREAD="$(find "$NOTES_DIR" -maxdepth 1 -name "*.md" -newer "$TS_FILE" \
        \( -iname "*${SESSION}*" -o -iname "*to_all*" -o -iname "*_all_*" \) \
        ! -iname "${SESSION}_*" \
        2>/dev/null | head -n 1)"
fi

if [ -n "$HAVE_UNREAD" ]; then
    # Concrete signal present: increment continuation counter + block.
    echo "$((COUNT + 1))" > "$CONT_FILE"
    # Compose JSON decision per Claude Code Stop-hook protocol
    REASON="New inbox items pending for ${SESSION} (>${TS_FILE} mtime); continuing triage. (continuation $((COUNT + 1))/${HARD_CAP})"
    printf '{"decision":"block","reason":%s}\n' "$(echo "$REASON" | jq -Rs .)"
    exit 0
fi

# No concrete signal: exit (true stop).
exit 0
