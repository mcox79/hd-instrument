#!/usr/bin/env bash
# blocker_ping_30min.sh -- USER-directed overnight blocker ping (2026-06-18).
#
# Every 30 minutes, write a notes/blocker_ping_*.md file asking ALL sessions
# whether anything is holding them up. v5 monitors catch via _all_ filter.
# Sessions respond by filing notes/<session>_to_all_blocker_ping_ACK_<status>.md.
#
# Usage:  bash tools/blocker_ping_30min.sh
# Run via Bash run_in_background (overnight 12h plan; ~24 pings).
# Stop with TaskStop.
set -u
ROOT="/d/AI/hd-instrument"
cd "$ROOT" || { echo "BLOCKER-PING-ERROR: cannot cd $ROOT"; exit 1; }

PING_COUNT=0
while true; do
  PING_COUNT=$((PING_COUNT + 1))
  TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  TS_FILE=$(date -u +"%Y%m%dT%H%M%SZ")
  FNAME="notes/blocker_ping_to_all_${TS_FILE}_n${PING_COUNT}.md"

  cat > "$FNAME" <<EOF
# BLOCKER PING ${PING_COUNT} -> ALL SESSIONS (USER-directed 30-min overnight cadence)

**From:** blocker_ping_30min.sh (USER directive 2026-06-18 ~01:05)
**To:** ALL sessions (Research, Skunkworks, Exp-Dev, Testbed, Orchestrator)
**Date:** ${TS}
**Ping #:** ${PING_COUNT}

## Question (verbatim USER directive)

"Is there anything holding you up from progressing?"

## Response protocol

Each session: file notes/<session>_to_all_blocker_ping_${PING_COUNT}_<STATUS>.md within 10 minutes where STATUS is:
- CLEAR (no blockers; actively progressing or reactively standing)
- BLOCKED (something is holding you up; name it specifically)
- WAITING (waiting on a specific session or USER; name them)

Format: 1-3 lines. Be concrete + actionable. Honest.

## Why this cadence

Per USER directive 2026-06-18 ~01:05 as part of the overnight 12-hour plan: "an extremely solid reminder, every 30 minutes, that pings all sessions asking if there is anything holding them up from progressing". Composes with the USER-DIRECTED IMPERATIVE on communications + process (blocker-visible-immediately rule).

-- blocker_ping_30min.sh (automated)
EOF

  echo "PING ${PING_COUNT} written: ${FNAME}"

  # Sleep 30 min
  sleep 1800
done
