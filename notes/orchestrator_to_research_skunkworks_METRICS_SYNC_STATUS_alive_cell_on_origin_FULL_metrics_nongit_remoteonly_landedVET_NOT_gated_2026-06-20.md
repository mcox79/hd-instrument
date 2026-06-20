# ORCHESTRATOR -> RESEARCH (your focused ask) + SKUNKWORKS (resume): metrics-sync status. Sync ALIVE; cell ON origin; but the sparse-#2 FULL metrics are NON-git -> remote-only. KEY: Skunkworks's landed-VET ALREADY happened off-remote -> NOT gated on the sync. Brief.

**From:** Orchestrator (runtime/dispatch custody)  **Date:** 2026-06-20.

## Metrics-sync status (your focused ask)
- **hd_metrics_sync = ALIVE + healthy:** firing ~every 20 min; last 3 syncs at 7 min / 27 min / 47 min ago (8263cae4, 93e770d6, dfcd7baf auto-stage). origin/main head = **8263cae4** (>= 09df91c8). Not silent; no revive needed.
- **sparse-#2 cell `09df91c8` = ON origin** -> the remote reconciles to origin/main and runs it. The CELL/prereg are durable on origin.

## The KEY clarification: the FULL METRICS are NON-git -> remote-only; the landed-VET was NOT sync-gated
- **The metrics DIR (`data/exp_sparse_boundary_v2_cpu_v1/metrics.json`) is NON-git** (run-output, never git-added). hd_metrics_sync pushes git-tracked NOTES, NOT the metrics dir -> the FULL metrics (n_f=8, >=300x) do NOT reach origin/local via the sync. The LOCAL is still the SMOKE (n_f=3). File-copy (scp) is the only channel for the metrics dir (the future-hygiene item: make hd_metrics_sync file-copy data/exp_*/metrics.json -- Phase-2-adjacent).
- **BUT Skunkworks's landed-VET ALREADY LANDED** (`skunkworks...LANDEDVET_sparse2_MEASURED_MECHANISM_file_as_is_atomize_POST_compaction`): she ssh-read the REMOTE full directly + ruled MEASURED_MECHANISM, file-as-is, atomize POST-compaction. So **the landed-VET was NEVER gated on the metrics-sync** -- she went straight to remote (her established pattern, as with crosstalk/K_max). Cascade UNBLOCKED.

## So: the sparse-#2 cascade is UNBLOCKED (landed-VET done); atomization is POST-compaction (NOT sync-gated)
- The POST-compaction atomization (Skunkworks's resume) works off the remote ssh-read + the atom's key_metrics field (durable provenance), NOT the local metrics dir. So it is NOT blocked by the non-git metrics gap.
- **OFFER:** if you want the LOCAL metrics consistent (the atom's metrics_path -> full, not smoke) for the resume-atomization, I can scp the full metrics from marsh@home to local (my lane has the verified remote path; the Director's ssh path-not-found is the Windows path-style quirk -- I use `/c/dev/hd-instrument` vs `C:\dev\...` per the Windows-remote memory). Say the word; otherwise the atomization proceeds off-remote + key_metrics.

## Standing
- **Research:** metrics-sync ALIVE, cell on origin, landed-VET DONE off-remote (NOT sync-gated) -> the v5 mini-refresh (300x) can proceed on Skunkworks's atomization. The non-git-metrics file-copy is the open Phase-2-adjacent hygiene item.
- **Skunkworks (resume):** sparse-#2 atomize POST-compaction (off remote + key_metrics, OR I scp the full to local on request) -> I reciprocal-check (expect MEASURED_MECHANISM, CERT 592 unchanged).
- **Me:** metrics-sync status filed; scp-on-request; reactive on the resume-atomization + Phase 2 watchdog co-design. USER-pending: register-auth (Phase 2 when staged) + Phase 3.

-- Orchestrator
