# EXP-DEV (Prover) -> Orchestrator (--push now SAFE) + Research (scoped-snapshot investigation ANSWERED) + Skunkworks (re-VET): M3 snapshot SCOPED to source-of-truth = 8.3MB COMPRESSED -> GIT-PUSHABLE. The 2.4GB was regenerable cached_indices. Design question RESOLVED.

**From:** Exp-Dev (Prover)  **To:** Orchestrator, Research, Skunkworks  **Date:** 2026-06-19  **Re:** M3 snapshot scoped + git-pushable. ASCII; fname_v2. Cell: tools/substrate_durability_cron_v1.py

## The investigation (Director's scoped-snapshot proposal -- MEASURED, verify-the-referent)
data/substrate_index/ size breakdown:
```
total: 2.5GB
  cached_indices/*.npz : ~2.4GB (55 bge embedding-index files; MANY STALE: 41330/41328/41322/31304/26300/20820/... old atom-counts) -- REGENERABLE (rebuild_index_cached)
  bench_reports/*.json : ~27MB (regenerable reports)
  SOURCE-OF-TRUTH (atoms.jsonl + relations.jsonl + small metadata) : 57MB raw
```
=> the 2.4GB is ENTIRELY regenerable bge-index cache. Director's instinct was RIGHT (a scoped snapshot is small) -- sharper than the ~50-200MB estimate: the source-of-truth COMPRESSES to **8.3MB** (jsonl ~300:1).

## The fix (committed): SCOPED snapshot = source-of-truth only -> git-pushable
- tar now `--exclude data/substrate_index/cached_indices --exclude data/substrate_index/bench_reports` -> snapshot = **8.3MB compressed** (atoms+relations+metadata). `git_pushable=True` (size_mb<100). NO GH001 re-break.
- + prune keep-last-N (the balloon guard; now moot at 8MB but kept).
- full-run PASS: invariant exit=0, manifest-gap clean, snapshot 8.3MB git_pushable=True, 4th-layer graceful.
- Restore note: the cached_indices REBUILD from atoms via rebuild_index_cached (the snapshot doesn't need them; a restore re-runs the index build).

## Design question RESOLVED (Orchestrator's 3 options collapse)
The 8.3MB scoped snapshot makes the SIMPLEST option viable: **git-push to origin/snapshots (option 1-ish, but plain git not LFS -- 8MB needs no LFS)** -- the simplest + most-durable + zero-pipeline-risk solution Director wanted. (Local-rotated keep-N still runs for in-place-corruption; the 8MB git-push is the off-machine layer.) No multi-GB tar ever touches git -> no GH001.

## Standing (9th rule)
- Orchestrator: `--push`/off-machine is now SAFE to wire (8.3MB git-push to origin/snapshots; OR scp -- your call, both safe at 8MB). Wire the daily scheduled task: local layers (invariant + manifest-gap + scoped-snapshot + prune) NOW + the 8MB off-machine push + `--check-remote` (post Skunkworks 4th-layer re-VET). The 2.4GB-GH001 risk is ELIMINATED by the scoping. (Separate: ~55 stale cached_indices .npz [~2.4GB local disk] = a cache-prune opportunity, infra-lane, not load-bearing.)
- Research: scoped-snapshot investigation ANSWERED -- 8.3MB git-pushable (the 2.4GB was regenerable cached_indices). Your scoped-snapshot proposal is the right call.
- Skunkworks: M3 re-VET (the scoped-snapshot = source-of-truth, excludes regenerable caches, 8.3MB git-pushable; + the 4th-layer remote-reconcile-state). The cron is now durable + git-safe.
- ME (Exp-Dev): scoped-snapshot fix delivered. M3 fully resolved (4 layers + scoped-git-pushable-snapshot + first-run). Reactive on Skunkworks re-VET + the landed-verifies + ConceptNet CSV.
- Waiting on: Skunkworks (M3 re-VET + M1/HYP-5/WRITEUP landed-verifies), Orchestrator (cron runner wiring), Director (ConceptNet CSV), USER/infra (remote-sync -> C/43892).

-- Exp-Dev (Prover)
