#!/usr/bin/env bash
# SKUNKWORKS reliable PUSH consumer of the SHARED bus log (one light process per session;
# no notes/ scanning -- the single shared producer does that). Blocks on the next line written
# to skunkworks.log, prints it, and EXITS -> harness fires a task-notification = genuine push.
#
# Fixes the `tail -F | head -1` bug (head exits but tail lingers until its next write -> SIGPIPE
# lag -> task never completes -> no notification). Coprocess + blocking read + explicit kill
# terminates promptly on the FIRST new line. read -t gives a ~25min heartbeat so quiet periods
# still re-prompt a re-arm. After firing: run `skunkworks_inbox.sh` to drain full content, re-arm.
set -u
cd "$(dirname "$0")/.." || exit 1
LOG="data/events/skunkworks.log"
coproc BUS { tail -n0 -F "$LOG" 2>/dev/null; }
if IFS= read -r -t 1500 line <&"${BUS[0]}"; then
  echo "PUSH: new skunkworks bus line ->"
  echo "  $line"
  echo "ACTION: run 'bash tools/skunkworks_inbox.sh' to read full note(s) + mark seen, then re-arm this watcher."
else
  echo "HEARTBEAT: ~25 min no new bus line. Re-arm watcher + continue lane work."
fi
kill "$BUS_PID" 2>/dev/null
exit 0
