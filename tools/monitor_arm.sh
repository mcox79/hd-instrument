#!/usr/bin/env bash
# monitor_arm.sh -- standardized, self-healing wrapper around notes_monitor.sh
#
# WHY: the inner notes_monitor.sh runs forever but CAN crash (set -u undefined var on
# unexpected input, find/sort errors on weird filenames, FS hiccup). Without a wrapper
# a single crash silently stops monitor delivery for the session -- sessions go dark
# without realizing it. This wrapper re-runs the inner script on any non-zero exit,
# emitting a CRASH line as a wake-up signal so the session knows it happened.
#
# 2026-06-21 LEAK FIX (Orchestrator caught): every Monitor-tool re-arm spawned a NEW
# wrapper without killing prior ones. 5 sessions x several re-arms today = 36 orphaned
# bash processes each polling notes/ every 20s = thermal load (same class as the
# 2026-06-12 incident). Now kill priors on arm + SIGTERM-trap for clean child shutdown.
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

# === LEAK FIX: kill any prior monitor_arm/notes_monitor processes for THIS role ===
# Match by command-line pattern (role-scoped); exclude self ($SELF) + own parent shell.
# Best-effort: silent if ps unavailable or no matches.
killed=0
if command -v ps >/dev/null 2>&1; then
  for pid in $(ps -ef 2>/dev/null \
        | grep -E "(monitor_arm\.sh ${ROLE}|notes_monitor\.sh ${ROLE})( |\$)" \
        | grep -v "grep -E" \
        | awk -v self="$SELF" -v parent="$PPID" '$2 != self && $2 != parent {print $2}'); do
    kill -TERM "$pid" 2>/dev/null && killed=$((killed + 1))
  done
fi
if [ "$killed" -gt 0 ]; then
  echo "MONITOR-ARM: killed ${killed} prior ${ROLE} bash process(es) before re-arm (leak fix)"
  sleep 1  # give them time to exit cleanly
fi

# === SIGTERM trap: propagate to inner script + its children so TaskStop kills the tree ===
cleanup() {
  echo "MONITOR-ARM: SIGTERM received; shutting down ${ROLE} monitor tree (pid $SELF)"
  # Kill our process group (negative pid). On Git Bash, $$ is the bash PID + we may
  # not have setsid; fall back to killing direct children.
  if [ -n "${INNER_PID:-}" ]; then
    kill -TERM "$INNER_PID" 2>/dev/null
  fi
  pkill -TERM -P "$SELF" 2>/dev/null
  exit 0
}
trap cleanup TERM INT

# Emit a startup line so the session sees the monitor armed (test signal it works).
echo "MONITOR-ARMED: notes_monitor for ${ROLE} (self-healing wrapper; sleep-20s; v5; leak-fix 2026-06-21)"

restart_count=0
while true; do
  bash tools/notes_monitor.sh "$ROLE" &
  INNER_PID=$!
  wait "$INNER_PID"
  rc=$?
  unset INNER_PID
  restart_count=$((restart_count + 1))
  # Emit a CRASH line as a wake-up signal so the session realizes + can investigate.
  echo "MONITOR-CRASH: notes_monitor ${ROLE} exited rc=${rc} (restart #${restart_count}); reloading in 5s"
  sleep 5
done
