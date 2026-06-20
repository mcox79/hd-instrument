#!/usr/bin/env bash
# monitor_arm.sh -- standardized, self-healing wrapper around notes_monitor.sh
#
# WHY: the inner notes_monitor.sh runs forever but CAN crash (set -u undefined var on
# unexpected input, find/sort errors on weird filenames, FS hiccup). Without a wrapper
# a single crash silently stops monitor delivery for the session -- sessions go dark
# without realizing it. This wrapper re-runs the inner script on any non-zero exit,
# emitting a CRASH line as a wake-up signal so the session knows it happened.
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

# Emit a startup line so the session sees the monitor armed (test signal it works).
echo "MONITOR-ARMED: notes_monitor for ${ROLE} (self-healing wrapper; sleep-20s; v5)"

restart_count=0
while true; do
  bash tools/notes_monitor.sh "$ROLE"
  rc=$?
  restart_count=$((restart_count + 1))
  # Emit a CRASH line as a wake-up signal so the session realizes + can investigate.
  echo "MONITOR-CRASH: notes_monitor ${ROLE} exited rc=${rc} (restart #${restart_count}); reloading in 5s"
  sleep 5
done
