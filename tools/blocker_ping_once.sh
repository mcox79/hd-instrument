#!/usr/bin/env bash
# blocker_ping_once.sh -- ONE-SHOT durable variant of blocker_ping_30min.sh.
#
# WHY ONE-SHOT: the original blocker_ping_30min.sh is an infinite while-true loop
# (session-bound; dies on compaction). For Windows scheduled-task durability the
# script must fire ONCE and exit; the scheduled-task RepetitionInterval handles
# the 30-min cadence. Cycle counter is derived from the count of existing
# notes/blocker_ping_to_all_*.md files + 1 (no state file; idempotent on count).
#
# Usage:  bash tools/blocker_ping_once.sh
# Invoked by Windows scheduled task hd_blocker_ping every 30 min (USER directive
# 2026-06-18 "your 30 minute reminder should survive compaction").
set -u
ROOT="/d/AI/hd-instrument"
cd "$ROOT" || { echo "BLOCKER-PING-ERROR: cannot cd $ROOT" >&2; exit 1; }

EXISTING=$(find notes -maxdepth 1 -name 'blocker_ping_to_all_*.md' 2>/dev/null | wc -l)
PING_COUNT=$((EXISTING + 1))
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
TS_FILE=$(date -u +"%Y%m%dT%H%M%SZ")
FNAME="notes/blocker_ping_to_all_${TS_FILE}_n${PING_COUNT}.md"

cat > "$FNAME" <<EOF
# BLOCKER PING ${PING_COUNT} -> ALL SESSIONS (USER-directed 30-min overnight cadence)

**From:** blocker_ping_once.sh via hd_blocker_ping scheduled task (USER directive 2026-06-18 "survives compaction")
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

This is the DURABLE variant: invoked by Windows scheduled task hd_blocker_ping (30-min cadence) -- survives session close + compaction + laptop sleep (StartWhenAvailable + AllowStartIfOnBatteries).

-- blocker_ping_once.sh (automated; one-shot)
EOF

echo "PING ${PING_COUNT} written: ${FNAME}"
exit 0
