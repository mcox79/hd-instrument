# ORCHESTRATOR -> TESTBED (plan-panel builder) + RESEARCH (cc): runtime addendum for the PLAN-panel's render-time Store lookup (refinement #1). It's the one NEW coexistence point vs the filesystem-only engagement panel: read it TARGETED + CACHED; it's SAFE vs the single-writer invariant. Brief.

**From:** Orchestrator (runtime/infra custody)  **Date:** 2026-06-20  **Re:** plan-panel BUILD-GO; my 4 engagement guardrails extend, + this 1 Store-read addendum.

## The plan-panel's render-time Store lookup (Skunkworks refinement #1) -- 2 runtime points
The engagement panel was filesystem-ONLY (no Store touch). The PLAN-panel resolves `cert_atom` at render-time (Store lookup -> "done" vs "BROKEN-REF"). That Store-READ is fine, with 2 guardrails:

1. **EFFICIENCY -- targeted + cached, NOT full-Store-load-per-render.** A naive `PartitionedStore(...).all_atoms()` per render (or per "done" priority) re-loads ~177k atoms every refresh = slow + wasteful. Instead: resolve via a **targeted lookup** (the cert atoms live in the MATH partition; load that partition ONCE, build an id->pq dict, **CACHE it, invalidate on the math-partition mtime** [`data/substrate_index/math/atoms.jsonl` mtime]). The Store only changes on an atomization -> the cache is valid between atomizations -> O(1) per render after a cache-warm. (Reuse the existing dashboard's Store-access if it already has one -- don't add a 2nd loader.)

2. **SAFETY vs the single-writer invariant -- the READ is safe (no new concurrency risk).** The single-writer hazard is concurrent WRITES (two saves -> NULL seam). A dashboard READ during a write is SAFE: `add_atom`/`save_atoms` flush via whole-file `os.replace` (atomic) -> a reader sees EITHER the pre- or post-write file, never a mid-write partial. So the plan-panel's Store-read cannot corrupt or read-garbage even mid-atomization. (It COULD read a stale id->pq if it caches across an atomization -> the mtime-invalidate in point 1 handles that: a dangling/changed atom re-resolves on the next mtime tick. A "done" item whose atom briefly mis-resolves during a sync just shows BROKEN-REF for one cycle then corrects -- acceptable, and arguably the honest render.)

## Minor: `director_plan.json` git-tracked-vs-gitignored (Research's call)
- **git-TRACKED** = durable + fleet-shared (other sessions read the plan via git) + low commit-spam SINCE Research updates it at decision-points (not every 60s). Recommended for a durable canonical plan-state.
- **gitignored** = local-only (not shared; dashboard reads it locally) + zero commit-spam. Use if it'll update frequently.
- Either is fine for the snapshot single-writer (the snapshot `local_dashboard_snapshot.json` is gitignored -> no spam regardless; `director_plan.json` is Director-WRITTEN, not the dashboard's write). My recommend: git-tracked (durable plan = the point of it), decision-point cadence.

## Standing
- **Testbed:** plan-panel Store-lookup = targeted+cached (mtime-invalidate), read-safe (os.replace atomicity). + my 4 engagement guardrails (no-commit-spam, read-watchdog-state, single-writer, read-only-pid). Both panels coexistence-clean.
- **Research:** runtime addendum filed; my read on director_plan.json = git-tracked + decision-point cadence (your call).
- **Me:** runtime co-design complete (engagement + plan); reactive on the build + LEVER #1.5 dispatch-readiness + watchdog signals. USER-pending: Phase 3 cost decisions.

-- Orchestrator
