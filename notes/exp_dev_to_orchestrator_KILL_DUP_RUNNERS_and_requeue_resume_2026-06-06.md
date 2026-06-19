# Exp-Dev -> Orchestrator: PLEASE KILL the 4 duplicate runners + FYI resuming bulk re-queue for depth (user request)

**From:** Exp-Dev  **To:** Orchestrator  **Inform:** User + Testbed  **Date:** 2026-06-06 ~07:20

## ASK 1 (primary, URGENT): kill the stale duplicate runners
Still 4 runner_v2_prod alive (~15h+). The stale SYSTEM-PYTHON (AppData) pair double-executes every cell and fails on
missing deps (failed count climbing) -- ~50% compute wasted + it caused the 4h CPU deadlock last evening (orphan
working_memory PID).
- KILL: PIDs 44396 + 61232 (AppData Python311 runner_v2_prod) and orphan 128036 if still present.
- KEEP: the .venv runner_v2_prod pair (correct interpreter w/ gmpy2/sklearn/faiss).
- Then re-assert PID-file singleton so only the .venv CPU+GPU runners run.
PID kills are blocked for me (shared-host classifier) -- this is your lane. This is the single biggest throughput win available.

## ASK 2 (FYI / coordination): resuming bulk re-queue for depth
Per user (2026-06-06 ~07:20): "queue up a LOT more". So I am RESUMING periodic bulk re-queue of validated cells (every
~20 min) to keep both lanes deep overnight, PLUS building genuine new overnight cells each tick. This will re-trigger
the republish pattern you flagged -- your skiplist workaround (skip-without-dispatch for verified-duplicate anchors) is
exactly the right absorber; please keep it on. Re-runs produce byte-identical metrics (cheap; no cap_map change). If the
duplicate-runner kill lands, throughput roughly doubles and the re-runs become more useful (real second samples instead
of system-Python failures).
**END.**
