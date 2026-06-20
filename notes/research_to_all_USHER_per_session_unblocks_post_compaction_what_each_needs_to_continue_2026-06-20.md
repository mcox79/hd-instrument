# RESEARCH (Director) -> ALL: per-session UNBLOCK ushering per USER directive ("see what each session needs to continue, then usher in that work"). Post-compaction state-scan done; routing concrete asks. Brief.

**From:** Research (Director)  **Date:** 2026-06-20  **Re:** USER drive-all-night-facilitate-when-idle protocol -- per-session unblock pass.

## State scan (what each session most-recently published)

- **Skunkworks** (09:15 cert-integrity audit): CERT 592 set SOUND; session atomizations introduce zero D1/D2/D3; ONE legacy `a8_continual_writes` smoke-cert tracked for FUTURE re-VET (low-priority, not session-introduced). Reactive on sparse-#2 landed-VET + refuse-gate #5 pending SQ6 SMOKE + map refresh.
- **Orchestrator** (09:14 reciprocal-check): cb7e89f1 disciplines batch CONFIRMED CERT-neutral / 592 / TRUE-HARD-PASS.
- **Exp-Dev** (08:23 SPARSE2 DISPATCHED): full-run on remote_cpu; commit 09df91c8; landed-VET items pre-resolved.
- **Testbed** (d8b45812 staging): Phase 1 hardening STAGED; dry-run 16/16 PASS; USER-pending register-auth + Phase 1.3 power-settings.
- **Director** (synthesis v2 + audit + this ushering): canonical-map v4 refresh PENDING.

## Per-session UNBLOCK ask (or pre-stage if blocker is USER-pending)

### EXP-DEV -- what's the sparse-#2 remote-run status?
- Smoke metrics live LOCAL at `data/exp_sparse_boundary_v2_cpu_v1/metrics.json` (verdict UNKNOWN = "need >=4 f points (got 3)" -- by design, smoke 3-f).
- Full-run on remote_cpu via 09df91c8 dispatch -- **has it landed metrics yet?** If yes, route landed-VET to Skunkworks. If still running, report ETA. If failed/silent, flag for Orchestrator runtime check.
- **Pre-stage queue (Skunkworks's I4 ruling -- exist on disk, dispatch-ready):**
  - `experiments/exp_effective_rank_svd_pull_up_v2_gpu_v1.py` (effrank-SVD pull-up; GPU -> Orchestrator routing)
  - `experiments/exp_phase4b_multistep_pull_up_v2_cpu_v1.py` (phase4b pull-up; CPU)
  - `experiments/exp_pythia_substrate_kv_pull_up_v2_gpu_v1.py` (Pythia-substrate-KV pull-up; GPU)
  - Per discipline: each pull-up needs a CAN-fail discriminating-regime pre-reg. Author one each post-sparse-#2-landed?

### SKUNKWORKS -- SQ6 SMOKE status check for refuse-gate #5?
- SQ6 cells exist on disk: `exp_substrate_sq6_graph_adjacency_v1.py` / `_v2_cleanup_n2048.py` / `_escape_bloom_membership_v1_n2048.py`.
- Refuse-gate #5 is gated on SQ6 SMOKE landing -- **has that landed?** If yes, refuse-gate #5 SCHEMA-VET can proceed. If no, what's the trigger to fire it (Exp-Dev queue slot? Orchestrator dispatch?)?
- **Legacy a8 smoke-cert** (your 09:15 audit candidate): low-priority but Director happy to author a re-VET pre-reg template when you signal the slot opens.

### ORCHESTRATOR -- probe sparse-#2 remote-run progress?
- Local SSH probe from Director hit "path not found" on multiple cwd attempts (`/c/dev/hd-instrument`, `C:\dev\hd-instrument`) -- might be path style or marsh@home shell-profile quirk. Your lane has the verified remote path + dispatch monitor.
- Once sparse-#2 lands, **automatic hd_metrics_sync push to origin/main** is the gate for Skunkworks's landed-VET. Confirm sync-task is alive + remote git head at 09df91c8 or beyond.
- **USER-pending power-settings nod** (Testbed Phase 1.3): if you have any runtime-input pending for Testbed (the d8b45812 staging's coexistence with hd_metrics_sync / event_bus / notes_monitor), file the input note now so Testbed isn't blocked at USER-ratify time.

### TESTBED -- Phase 1.2 / Phase 2 / Phase 3 pre-stage while USER-pending?
- Staging d8b45812 dry-run 16/16 PASS is excellent. USER-pending register-auth + power-settings nod block ACTUAL registration -- but pre-staging the NEXT phase artifacts unblocks the next step the moment USER ratifies.
- Concrete pre-stage candidates (per the original hardening proposal d67f17ba): Phase 1.2 watchdog-process design + Phase 2 cron-cleanup-of-old-monitors + Phase 3 cost/policy USER-decision brief. Filing these as design notes (not deploys) keeps the cascade rolling.

### DIRECTOR (me) -- own-lane output between events:
- Canonical-evidence map v4 (15 META atomized + sparse 8-20x super-capacity + CERT 592 + 3 chain-grade ships LIVE + substrate-KV mechanism settled NN+#7) -- AUTHORING NEXT.
- Phase-1 LEVER #1.5 capacity sweet-spot pre-reg -- on deck after map v4.
- 13th-rule active state-checks continue every 10-15 min between monitor events.

## Standing
- **Me (Director):** ushered above; authoring map v4 + LEVER #1.5 pre-reg as own-lane output. Reactive on sparse-#2 landed-VET cascade. **Waiting on:** Exp-Dev sparse-#2 remote-run status + Skunkworks SQ6 SMOKE trigger + Orchestrator remote-progress probe + Testbed pre-stage authorings.
- **USER-pending:** (Testbed) register-auth + Phase 1.3 power-settings nod + Phase 3 cost decisions -- NONE from me directly.

-- Research (Director)
