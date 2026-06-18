# BLOCKER PING 34 -> ALL SESSIONS (USER-directed 30-min overnight cadence)

**From:** blocker_ping_once.sh via hd_blocker_ping scheduled task (USER directive 2026-06-18 "survives compaction")
**To:** ALL sessions (Research, Skunkworks, Exp-Dev, Testbed, Orchestrator)
**Date:** 2026-06-18T22:25:37Z
**Ping #:** 34

## Question (verbatim USER directive)

"Is there anything holding you up from progressing?"

## Response protocol

Each session: file notes/<session>_to_all_blocker_ping_34_<STATUS>.md within 10 minutes where STATUS is:
- CLEAR (no blockers; actively progressing or reactively standing)
- BLOCKED (something is holding you up; name it specifically)
- WAITING (waiting on a specific session or USER; name them)

Format: 1-3 lines. Be concrete + actionable. Honest.

## Why this cadence

Per USER directive 2026-06-18 ~01:05 as part of the overnight 12-hour plan: "an extremely solid reminder, every 30 minutes, that pings all sessions asking if there is anything holding them up from progressing". Composes with the USER-DIRECTED IMPERATIVE on communications + process (blocker-visible-immediately rule).

This is the DURABLE variant: invoked by Windows scheduled task hd_blocker_ping (30-min cadence) -- survives session close + compaction + laptop sleep (StartWhenAvailable + AllowStartIfOnBatteries).

-- blocker_ping_once.sh (automated; one-shot)
