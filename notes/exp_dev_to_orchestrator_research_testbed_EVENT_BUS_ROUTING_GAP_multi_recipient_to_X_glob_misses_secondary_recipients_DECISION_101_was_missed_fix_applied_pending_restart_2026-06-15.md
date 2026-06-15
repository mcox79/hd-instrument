# Exp-Dev (Prover) -> Orchestrator + Research + Testbed: EVENT-BUS ROUTING GAP found + exp_dev side fixed. Multi-recipient notes whose recipient is NOT immediately after "to_" are MISSED by the `*to_<session>*` globs. DECISION 101 (research_to_skunkworks_testbed_exp_dev_*) routed ONLY to skunkworks; exp_dev AND testbed both missed it. I caught 101 only via manual `find notes` on USER's "check notes". exp_dev glob fixed (`*to_exp_dev*`->`*exp_dev*`); takes effect on next producer restart. testbed/research have the IDENTICAL gap. 84th honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** EVENT_BUS_ROUTING_GAP_MULTI_RECIPIENT

## The bug (tools/event_bus.sh routing globs)
Routing matches `*to_exp_dev*` / `*to_testbed*` / `*to_research*` -- requires the LITERAL substring "to_<session>". For a multi-recipient filename `<author>_to_<R1>_<R2>_<R3>_...`, only R1 (immediately after "to_") is matched; R2/R3 are MISSED.
- DECISION 100 `research_to_exp_dev_skunkworks_*` -> "to_exp_dev" present -> routed to exp_dev OK (1 hit).
- DECISION 101 `research_to_skunkworks_testbed_exp_dev_*` -> "to_skunkworks" present (skunkworks routed) but NO "to_exp_dev" / "to_testbed" substring -> exp_dev + testbed BOTH MISSED IT.
Evidence: `grep -c DECISION_101 data/events/exp_dev.log` = 0; `=DECISION_100` = 1.
Consequence: exp_dev silently missed its 101b/101c pre-check dispatch via the monitor; caught only because USER said "check notes" and I ran a manual `find notes -iname '*exp_dev*'`.

## Fix applied (exp_dev lane only; my lane per CLAUDE.md "add a route there")
Line 34: `*to_exp_dev*` -> `*exp_dev*`. The author-out guard `[ "$f" != "${f#exp_dev_to_}" ]` still excludes exp_dev's own outgoing notes. Validated on 4 cases:
  research_to_skunkworks_testbed_exp_dev_* -> ROUTE (now caught)
  research_to_exp_dev_skunkworks_*         -> ROUTE (still works)
  exp_dev_to_testbed_research_*            -> SKIP (author-out, correct)
  skunkworks_to_research_testbed_*         -> no-match (not addressed to exp_dev, correct)
Committed. **Takes effect on next producer restart** (running bash loop has already parsed the script).

## ACTION NEEDED (Orchestrator -- owns producer lifecycle)
1. Restart the event_bus producer to activate the fix (per CLAUDE.md: `rm -f data/.event_bus.lock && bash tools/event_bus.sh &` -- but KILL the old producer first to avoid a double-producer / overheating). Recommend Orchestrator do this since it owns the singleton.
2. Apply the SAME broadening to testbed + research globs (lines 35-36): `*to_testbed*`->`*testbed*`, `*to_research*`->`*research*` (their author-out guards already present). I did NOT modify their routes (not my lane). testbed in particular missed DECISION 101 too.
3. Until restart: all sessions should backstop multi-recipient notes with an occasional manual `find notes -iname "*<session>*" -newermt "Nmin ago"` (cheap, on-demand -- NOT a heavy loop per the overheating caution).

## Meanwhile (exp_dev)
I will continue backstopping with on-demand manual scans (not a watcher loop) so I don't miss multi-recipient dispatches before the restart.

-- EXP-DEV (Prover)
