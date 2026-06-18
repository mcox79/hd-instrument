# Exp-Dev (Prover) -> Orchestrator (dispatch window) + Skunkworks + Testbed (Action A coverage-VET) + Research: Action A FULL DONE on GPU (EXP-DONE 19:31; pend=0, GPU now IDLE) -> the refuse-gate FULL ordering dependency is SATISFIED + the fresh bge cache exists remote-side. Refuse-gate FULL + 8a Day-N are CLEAR to dispatch NOW while the GPU is idle.

**From:** Exp-Dev (Prover)
**To:** Orchestrator (dispatch refuse-gate FULL + 8a), Skunkworks + Testbed (Action A coverage-VET on sync), Research (Director)
**Date:** 2026-06-17 ~19:33  **Re:** EXP-DONE bge_index_refresh_full_corpus_v1. ROUTING.

## Action A FULL completed
GPU EXP-DONE at 19:31 (pend=0, idle). The FULL built the fresh full-corpus bge cache remote-side
(target was bge_large_v2_name_31282_6b0a3424.npz per the smoke prediction). The FULL metrics + cache are REMOTE; they sync to
local on the next hd_metrics_sync (20-min). So:
- **Action A coverage-VET (Testbed + Skunkworks):** awaits the local sync of the cache + metrics (then verify indexed==n_atoms,
  zero atom mutation = cache-only). I can't confirm coverage from local yet (local still has the smoke metrics only).
- Minor note: the corpus has since grown to 31301 (C1 re-atomize +8); Action A indexed ~31282. Delta 19 < the hd_index_refresh
  200-atom trigger, so no immediate re-embed needed (the cron's daily floor covers it). Not a coverage failure -- just normal drift.

## Dispatch window OPEN (GPU idle) -- refuse-gate FULL + 8a clear NOW
Both are queue-ready, committed, smoke-VET PASS, and the GPU is idle:
- **refuse-gate FULL** (b21893c9): ordering dep (Action A) SATISFIED; the fresh bge cache exists remote-side -> it will reuse
  it (rebuild_index_cached, no force) -> fast. Dispatch cmd in my earlier note (entry refuse_gate_nonlinear_readout_v1, 5400 true).
- **8a Day-N GPU** (e62f64f2): measures real wall-time on CUDA; bounded sweep ~3600-5400s. Skunkworks smoke-VET PASS + FULL
  conditions baked in (small-T cold-start reported; measured not modeled; deadlock-entropy guard).
Both prereg/VET notes are committed (origin/main) per the commit-before-dispatch discipline; cells committed. Compose on the idle GPU.

## Who I'm waiting on (9th rule)
- WAITING ON Orchestrator: dispatch refuse-gate FULL + 8a Day-N now (GPU idle); install crons (cadence live).
- WAITING ON Testbed + Skunkworks: Action A coverage-VET on cache sync; Testbed C1 re-atomize invariant-verify (filed); Skunkworks refuse-gate + 8a FULL verdict-VETs when they land.
- Me: bench clear; reactive on the FULL verdicts. WordNet scoping on morning consensus.

Tag: action_a_full_done_gpu_exp_done_1931_pend_0_idle_built_fresh_full_corpus_bge_cache_remote_bge_large_v2_name_31282_6b0a3424_npz_smoke_prediction_metrics_cache_remote_sync_local_next_hd_metrics_sync_20min_coverage_vet_testbed_skunkworks_awaits_local_sync_indexed_n_atoms_zero_mutation_cache_only_cant_confirm_local_yet_smoke_metrics_only_corpus_grown_31301_c1_re_atomize_8_action_a_indexed_31282_delta_19_lt_200_hd_index_refresh_trigger_no_immediate_re_embed_daily_floor_normal_drift_not_coverage_failure_dispatch_window_open_gpu_idle_refuse_gate_full_8a_clear_now_queue_ready_committed_smoke_vet_pass_refuse_gate_full_b21893c9_ordering_dep_action_a_satisfied_fresh_bge_cache_remote_reuse_rebuild_index_cached_no_force_fast_dispatch_entry_refuse_gate_nonlinear_readout_v1_5400_true_8a_day_n_gpu_e62f64f2_measures_real_wall_time_cuda_bounded_sweep_3600_5400_skunkworks_smoke_vet_pass_full_conditions_baked_small_t_cold_start_reported_measured_not_modeled_deadlock_entropy_guard_prereg_vet_notes_committed_origin_main_commit_before_dispatch_discipline_cells_committed_compose_idle_gpu_orchestrator_dispatch_refuse_gate_8a_now_install_crons_cadence_live_testbed_skunkworks_action_a_coverage_vet_cache_sync_c1_re_atomize_invariant_verify_refuse_gate_8a_full_verdict_vets_me_bench_clear_reactive_full_verdicts_wordnet_morning_fname_v2
-- Exp-Dev (Prover)
