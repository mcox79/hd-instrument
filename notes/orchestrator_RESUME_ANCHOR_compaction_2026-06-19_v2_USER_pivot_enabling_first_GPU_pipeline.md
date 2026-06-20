# ORCHESTRATOR RESUME ANCHOR v2 (compaction 2026-06-19 ~21:00) -- supersedes the earlier v1 anchor. Custodian state after a long active session: q_b1 588 cascade + architecture apply + value-coverage onboarding + d300-d500 + pythia-KV + the USER PIVOT. Scannable.

## USER PIVOT (most important -- happened ~20:45)
- **USER HALTED the vs-LLM head-to-heads** ("are we doing head to head comparisons with LLMs? I really don't think that's useful. Let's just keep improving substrate."). sentiment/textclass/math-vs-LLM = HALTED (confirmed DONE: none pending; my queue_add attempts deduped to stale-completed so never ran; NOTHING pulled; atoms STAY LEGACY).
- **NEW sequence (USER):** certify the experiment backlog -> prioritize the TRULY-ENABLING (composition / storage-capacity / KG / continual-learning-drift / regime-Phase0 / Phase-1 ships) -> THEN new. DROP vs-LLM positioning. Glass-box-LLM CONTINUES (pythia-KV etc. = substrate memory system, KEEP).
- **POS** (vs-HMM, NOT vs-LLM) = KEEP low-priority; dispatch to remote_cpu_queue (5400s) on Exp-Dev re-confirm + bandwidth past the enabling tier. HELD now.
- My go-forward: dispatch ENABLING-capability cells only; skip vs-LLM.

## Current live state (verified ~21:00)
- Store: **177223 atoms / CERT 589 / capint_integrated 492 / loads clean**. (d300-d500 -> CERT 590 atomize PENDING Exp-Dev.)
- GPU: **pythia_substrate_kv_pull_up_v2_gpu_v1 RUNNING** (~27 partials; metrics not yet). Marker on landing = `measured_gpu_pythia2p8b_substrate_kv_sweep_noise` (verify BEFORE verdict-VET).
- Sync: FUNCTIONAL (origin drains on fast-merge cycles; ahead~12 normal between-cycle). Skunkworks COMPACTING (cert-VETs resume next session); enabling sequence GREENLIT.

## This session's custodian work (all DONE + durable on origin)
1. q_b1: HARD_PASS -> A/B swap (CERT 588, my LOAD-gate PASS) -> I4/I5 2-field fix (my light gate PASS) -> Skunkworks re-VET INTEGRATION-PASS@491. Closed.
2. Architecture Track-A apply 457->490 (33 atoms): full-revert of a bad first attempt (I independently verified clean, I1 preserved) -> corrected apply (my LOAD-gate PASS, commit-durable 6427306d, on origin). The hp12/kappa3/combo3 disposition churn = resolved.
3. phase4b CERT 589 (value-coverage pull-up #1, local-CPU; my LOAD-gate PASS).
4. d300-d500 (q_b1_ab_depth_extent, GPU): dispatched -> ran -> **CLIFF_BEYOND_d500** (marker-verified) -> Skunkworks VET -> scale_point -> CERT 590 atomize PENDING.
5. NER v3: root-caused = NOT a crash but a `git reset --hard origin/main` CLOBBER on the remote (consumer reconcile restored committed-old v1 over the fresh v3). Recovery = Exp-Dev reconstruct-from-log.
6. hp12 hygiene: CSP id-pin = SINGLE-exp_ `T3/EXP_hp12_v2_crypto_2048_gmpy2_latency_v1` (CERT/MIDDLE_BAND). Doubled-exp_ (T3/EXP_exp_*) = 7 INERT SMOKE/ARCHIVE leftovers (no cert-integrity issue); cleanup = Skunkworks's call.

## KEY infra facts (a resumed instance MUST know)
- **Sync slow-merge:** the remote tar-build merge slows to >10min DURING GPU runs (IO contention) -> some cycles get TERMINATED at the PT10M ExecutionTimeLimit before the push -> origin lags, then drains on the next fast cycle. INTERMITTENT, not systematic. push-before-merge reorder = the durable fix but DEFERRED (only if MANY consecutive terminations / origin fails to drain over a sustained window). Backup: `local_metrics_sync.ps1.bak_2026-06-19_preReorder`. (I disabled+reverted the merge once; it's NORMAL/enabled now, verified IDENTICAL to backup.)
- **Remote de-risked:** marsh@home disk 984GB free, GPU runner heartbeat alive, FB15k-237 staged (for the eventual KG dispatch), pythia-2.8b + Qwen2.5-{0.5/1.5/3}B-Instruct cached.
- **Dispatch:** `queue_add.sh <overnight_queue|remote_cpu_queue|local_cpu_queue> <name> <script> <prereg> <timeout>` (GPU/remote-CPU SCP+SSH to marsh@home; local = direct). PROT-018(N matches _n)/019(n>=8192 ->timeout>=21600)/020(GPU needs torch)/021(timeout>=14400 needs _seed_checkpoint). COMMIT cell+prereg to origin FIRST (remote reconciles to origin/main). NEW anchor = no stale trap; RE-USED anchor -> verify STATUS+metrics-marker (the NER/sentiment stale-completed trap; reset with --allow-duplicate if completed-but-needs-rerun).

## Pending / reactive (resume priorities)
- pythia-KV landing -> marker-verify -> Exp-Dev/Skunkworks verdict-VET.
- d300-d500 CERT-590 atomize (Exp-Dev) -> my light LOAD-gate if asked.
- CSP first-ship landed-VET = C1 state-change custody (Phase-1 ship gate; hp12 pin = single-exp_ CERT; baseline 9 atoms locked by Skunkworks).
- Enabling-capability GPU dispatches (effective-rank-SVD / neurogenesis / graceful-overload / drift-detection / KG-fb15k237 / Phase-0c) as Exp-Dev builds + commits them -> dispatch (enabling-first; remote-readiness pre-check for KG=FB15k-237 already cleared).
- POS dispatch (remote_cpu_queue, 5400) on Exp-Dev re-confirm + bandwidth.
- Skunkworks cert-VETs resume next session (their compaction).

-- Orchestrator
