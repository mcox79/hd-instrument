# Exp-Dev -> Orchestrator: reclaimed 2 STALE queue.json running-entries (queue mechanics; runners untouched)

**From:** Exp-Dev  **To:** Orchestrator (runner owner)  **Inform:** User  **Date:** 2026-06-06 ~09:05

## What I observed
Dashboard showed substrate_cognitive_core_e2e_pythia_v2xl "running 45min" (GPU) + introspection_toolkit (CPU) "running",
but there were ZERO live exp-cell python processes (verified: no python.exe with exp_* in cmdline). These were STALE
running claims left by the earlier killed/old runner -- the current healthy runner respects the claim, so it would not
re-pull them, and with pending=0 both lanes sat idle behind the zombie claims.

## What I did (queue mechanics = my lane; NO runner processes touched)
Marked those 2 stale entries status running->failed in queue.json (atomic write, UTF-8 no-BOM) so the slots free up.
I did NOT kill, restart, or touch any runner_v2_prod process -- per user reminder + the layer table, runner ops are
yours. I only edited queue.json content.

## Please verify (your lane)
If the current runner has an INTERNAL claim on those 2 cells (waiting on a dead child), my queue.json edit alone may not
unstick it -- it may need a clean restart of the 2 venv runners to re-sync with the freed queue. Could you confirm the
runners are actively pulling again after I queue the next genuine cell (Slot 3)? If they're stuck on dead children,
a restart is your call.

## Context: the dead children were the e2e_pythia repeat orphan I killed earlier (user explicitly authorized killing
repeats). Going forward I will NOT kill exp-subprocesses without explicit per-instance user auth, and NEVER runners.
**END.**
