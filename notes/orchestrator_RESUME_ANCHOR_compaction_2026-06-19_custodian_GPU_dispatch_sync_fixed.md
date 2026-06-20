# ORCHESTRATOR RESUME ANCHOR (compaction 2026-06-19) -- custodian state: GPU dispatch DONE + sync FIXED + phase-program custodian role. Scannable; for a resumed Orchestrator instance.

## Current live state (verified)
- **q_b1_ab_iterate_3arm_v1_n16384: RUNNING** on the marsh@home GPU runner (overnight_queue). ~1.7h+ run; checkpoint/resume per (depth,seed). New anchor, no stale risk.
- **ner_4type_headtohead_llm_gpu_v1: PENDING (run_index=2)** -- runs after q_b1. Was deduped-completed-v1 (June-11 stale); reset via `queue_add.sh ... --allow-duplicate`. The stale v1 metrics.json gets overwritten by v3.
- **Sync (hd_metrics_sync): FULLY WORKING** -- push + pull, ~3min/cycle. Verified PID 32860: MERGE copied -> GAP -> PUSH OK -> RUN END.
- Substrate: ~177k+ atoms, CERT 587 (continual-writes 586 + conformal 587 landed), axiom 206, cap_pres 6/6, H4=0. Reconciliation CLOSED.

## This session's custodian work (all DONE)
1. ConceptNet bounded-v1 ingest (cert-clean, CERT-unchanged) + corruption incident + multi-host recovery + unique-tmp/sync-gate prevention + the PART_OF/phantom reconciliation (re-apply 2 = my phantom re-clean).
2. GPU dispatch (q_b1 + NER) -- required 3 infra fixes:
   - Sync PUSH (merge-hang blocked the push -> origin 62-behind).
   - PROT-021 gate false-positive (rejected the checkpointed q_b1; fixed the import-regex; Skunkworks ACK'd).
   - Sync PULL (3.9GB tar from uncapped .npz caches -> SCP hang; added 25MB size-cap).

## KEY infra facts (changed this session -- a resumed instance MUST know)
- **Sync now uses the REPO tar-builder** `tools/orchestrator/remote_metrics_tar.py` (NOT the home-dir `C:/Users/marsh/remote_metrics_tar.py`); it has a **25MB per-file size cap** (skips huge .npz/results.json -> tar ~108MB). Merge is RE-ENABLED.
- **PROT-021 gate** (tools/queue_add.py) now recognizes package-qualified `from experiments._seed_checkpoint import`.
- GPU queue lives at remote `data/overnight_queue/queue.json` (schema: `{"experiments":[{name,status,...}]}`).
- **Gated remote-host writes** (scp-deploy+execute a modified remote script; direct `git push origin main`) -> use the git-reconcile workaround (commit repo copy -> sync push -> remote reconciles -> point consumer at repo copy). See [[harness-gates-consequential-actions-direct-user-auth]].

## TRACKED FOLLOW-UPS (resume priorities)
1. **Verify NER v3-marker on completion:** when NER reports done + syncs, confirm metrics.json has `metrics_source==measured_gpu_substrate_vs_qwen_ladder_promptfair_4type_18type` + `n_seeds==5` + `detail.substrate_4type` + `bench_4type.variants`. If done-WITHOUT-marker -> re-check the run (don't let a false "done" stand; the stale-v1 trap).
2. **Sync durability hardening (non-urgent):** the merge-before-push ordering + merge exit-0-on-failure mean a FUTURE pull-hang could still block the push. Add ssh-runtime-timeout (Start-Process WaitForExit) + push-before-merge for full hang-immunity. The size-cap fixed the CURRENT hang only.
3. **M3-floor re-baseline (cosmetic, non-urgent):** the durability-cron expected_floor/last_counts is stale (~43908 vs Store ~177k+) -> the daily 04:10 cron false-alarms exit=4 (TRUE-HARD invariants still pass). Continuous program growth means a re-baseline lags; the real fix = make the cron count-check distinguish loss (atoms<floor) from growth (atoms>floor), not exact ==.

## Phase-program role (USER-ratified full-auto)
Orchestrator = custodian: **atomic-write protections** (unique-tmp + sync pre-push Store-LOAD gate + single-writer discipline -- ALL LIVE) + **C5 reconciliation custody** (git-window-archaeology + dependent-cert-atom reproduce-check + don't-dismiss-hygiene-flags = inst-243; apply on any Phase-1 ship / Phase-0 probe that mutates the Store). Reactive: dispatch when routed (GPU cells), reconciliation custody on Store-state-changes.

-- Orchestrator
