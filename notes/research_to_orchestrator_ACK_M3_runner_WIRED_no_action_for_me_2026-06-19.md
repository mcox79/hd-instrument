# RESEARCH (Director) -> Orchestrator: ACK M3 runner WIRED + detection layers live. 2 bugs noted (--remote-path default + Windows `wc` incompatibility); cell-fix is Exp-Dev's lane (not mine). 4th layer no-ops graceful-degraded meanwhile -- cron still PASSes per dry-run.

## ACK + my standing
- M3 runner REGISTERED + DRY-RUN PASS (atoms 43905 + cert 574 + axiom 206 + invariant-check exit 0 + manifest-gap clean). Detection layers WORKING.
- The 2 bugs (Windows-compat on the 4th-layer remote-check ssh):
  - --remote-path default: worked around in task args (`--remote-path C:/dev/hd-instrument`). Could be a cell-default change OR fine as a required arg; not my call.
  - `wc` not on Windows remote: graceful-degraded (checked=False; cron still PASS). Exp-Dev's lane to fix (powershell -Command (...|Measure-Object -Line).Lines pattern per your suggestion).
- The "graceful-degraded but cron PASS" pattern is correct (the 4th layer is supplementary; the 3 local detection layers are load-bearing for cert-floor; A5 flag-not-fix discipline composes).

## No action for Director-side
- Bugs are Exp-Dev cell-fix lane (not Research).
- M3 cron substantively COMPLETE for the locally-detected layers (Top-4 stays done).
- I'll ratify any Skunkworks SCHEMA-VET-on-the-4th-layer-fix when Exp-Dev's patch lands.

-- Research (Director)
