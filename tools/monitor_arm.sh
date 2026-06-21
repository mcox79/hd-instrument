#!/usr/bin/env bash
# monitor_arm.sh -- standardized, self-healing wrapper around notes_monitor.sh
#
# WHY: the inner notes_monitor.sh runs forever but CAN crash. This wrapper re-runs
# the inner script on any non-zero exit, emitting a CRASH line as a wake-up signal.
#
# 2026-06-21 LEAK FIX (Orchestrator): kill priors on re-arm so re-arming doesn't leak.
# 2026-06-21 WINDOWLESS FIX (Orchestrator + USER): DON'T background the inner script
# (the prior `&` spawned a new bash subprocess that got its own console). Run inline
# instead -- the wrapper IS the only bash process; no new console.
#
# CANONICAL invocation pattern (every session, first action of session lifetime):
#   Monitor({
#     command: "cd /d/AI/hd-instrument && exec bash tools/monitor_arm.sh <role>",
#     persistent: true,
#     timeout_ms: 3600000,
#     description: "notes_monitor <role> (self-healing wrapper)"
#   })
#
# Usage:  bash tools/monitor_arm.sh <role>
#   <role> in: skunkworks | research | exp_dev | testbed | orchestrator
set -u
ROLE="${1:?usage: bash tools/monitor_arm.sh <role>}"
ROOT="/d/AI/hd-instrument"
cd "$ROOT" || { echo "MONITOR-ARM-FATAL: cannot cd $ROOT"; exit 1; }

SELF=$$
PARENT=$PPID

# === LEAK FIX disabled 2026-06-21 (USER popup-fix) ===
# The pgrep -f "...${ROLE}\b" pattern matched cross-role on Git Bash for Windows
# (\b word-boundary semantics differ from GNU pgrep), causing wrappers to kill
# each other's inner monitors -> tight crash-restart loop -> ~20 console flashes/min.
# Bash wrapper is now NON-canonical (Python port is canonical per CLAUDE.md);
# living with the leak is preferable to the kill-cascade for the few sessions
# still on bash until they re-arm Python.
killed=0

# === SIGTERM trap: kill all children before exiting ===
# Children inherit our process group on bash; pkill -P $$ kills direct descendants.
cleanup() {
  echo "MONITOR-ARM: SIGTERM received; killing ${ROLE} monitor tree (parent pid $SELF)"
  pkill -TERM -P "$SELF" 2>/dev/null
  exit 0
}
trap cleanup TERM INT

# Emit a startup line so the session sees the monitor armed.
echo "MONITOR-ARMED: notes_monitor for ${ROLE} (self-healing wrapper; sleep-20s; v5; leak+windowless-fix 2026-06-21)"

# === MAIN LOOP: run inner script INLINE (no `&`) so we don't spawn a new bash subprocess ===
# The inner script runs in OUR process (via direct bash invocation, same shell tree).
# No console window is allocated because we're already in one (the Monitor-tool's).
# When the inner script exits, control returns here + we restart.
restart_count=0
while true; do
  bash tools/notes_monitor.sh "$ROLE"
  rc=$?
  restart_count=$((restart_count + 1))
  echo "MONITOR-CRASH: notes_monitor ${ROLE} exited rc=${rc} (restart #${restart_count}); reloading in 60s (popup-rate cap 2026-06-21)"
  sleep 60
done
