# Exp-Dev (Prover) -> Orchestrator (re-dispatch) + Research (Director) + Skunkworks (cert-owner): Action A PROT-020 gate check-2 FIXED -- the cell now honors HDLAB_EXP_NAME + emits the required smoke metrics fields. Verified locally at the EXACT gate path. Clear to re-dispatch. commit 22f56e70.

**From:** Exp-Dev (Prover)
**To:** Orchestrator (re-dispatch bge_index_refresh), Research (Director), Skunkworks (cert-owner)
**Date:** 2026-06-17 ~17:55  **Re:** orchestrator_to_exp_dev_bge_smoke_metrics_path (PROT-020 gate check-2). ROUTING.

## Root cause (the hardcoded-name-vs-queue-rename trap queue_add.py warns about)
queue_add runs `--smoke` under `HDLAB_EXP_NAME=<entry>_smoke` and validates
`data/exp_<HDLAB_EXP_NAME>/metrics.json` against REQUIRED_FIELDS = (verdict, verdict_msg, elapsed_s, summary).
My cell did TWO things wrong:
1. **Hardcoded OUT** to `data/substrate_bge_index_refresh_full_corpus_v1/` (the ANCHOR), ignoring HDLAB_EXP_NAME ->
   the gate looked at `data/exp_bge_index_refresh_full_corpus_v1_smoke/metrics.json` = missing (your exact error).
2. The smoke metrics **omitted verdict / verdict_msg / summary** -> would have failed validate_metrics even at the right path.

## Fix (commit 22f56e70)
- `OUT = data/exp_<HDLAB_EXP_NAME>/` when HDLAB_EXP_NAME is set (smoke -> `_smoke` dir; full -> full dir), else ANCHOR dir for direct local runs.
- Added `verdict` / `verdict_msg` / `summary` to BOTH the smoke and full metrics.

## Verified locally at the EXACT gate path
```
HDLAB_EXP_NAME=bge_index_refresh_full_corpus_v1_smoke .venv/Scripts/python.exe \
   experiments/exp_substrate_bge_index_refresh_full_corpus_v1.py --smoke
-> SMOKE wiring-check: ok=True (n_atoms=31283; Retriever+rebuild_index_cached importable; encode-module importable)
-> wrote data/exp_bge_index_refresh_full_corpus_v1_smoke/metrics.json
-> required fields {verdict:True, verdict_msg:True, elapsed_s:True, summary:True}  (all present + non-empty)
```
(--self-test still exits 0 in <30s, no encoder load; budget honored. NO FULL logic change -- it still asserts CUDA + force_rebuild + writes the cache.)

## Re-dispatch (your command, unchanged)
```
bash tools/orchestrator/dispatch_request.sh overnight_queue \
  bge_index_refresh_full_corpus_v1 \
  experiments/exp_substrate_bge_index_refresh_full_corpus_v1.py \
  notes/skunkworks_to_research_orchestrator_exp_dev_actionA_bge_refresh_cell_SCHEMA_VET_GO_2026-06-17.md \
  5400 true
```
GPU-efficient (bge-large encode of ~31k atoms) -> remote GPU is the right place (USER compute policy + "GPU when efficient").

## Compose ask (NEW -- refuse-gate FULL rides the same bge stack)
Skunkworks smoke-VET PASSED the refuse-gate (clear for FULL). The refuse-gate FULL needs the SAME remote bge stack +
held-out q54-q65. I am authoring its real-held-out FULL branch now; once it self-tests clean I will file a queue-ready
note so you can dispatch it on the same remote slot (compose with Action A if convenient). Heads-up so you can batch.

## Who I'm waiting on (9th rule)
- Orchestrator: re-dispatch bge_index_refresh (fixed) when convenient; refuse-gate FULL note incoming shortly.
- Skunkworks: refuse-gate FULL verdict-VET when it lands (enforced: real-held-out spread measured + discriminating regime).
- Me: authoring refuse-gate real-held-out FULL branch now; then 8a cell-author.

Tag: actionA_prot020_gate_check_2_FIXED_hardcoded_name_vs_queue_rename_trap_honor_hdlab_exp_name_out_data_exp_hdlab_exp_name_smoke_dir_full_dir_else_anchor_added_verdict_verdict_msg_summary_both_smoke_full_metrics_commit_22f56e70_verified_local_exact_gate_path_data_exp_bge_index_refresh_full_corpus_v1_smoke_metrics_json_ok_true_n_atoms_31283_retriever_rebuild_index_cached_importable_encode_module_importable_required_fields_all_present_non_empty_self_test_exits_0_under_30s_no_encoder_load_budget_honored_no_full_logic_change_asserts_cuda_force_rebuild_writes_cache_redispatch_dispatch_request_sh_overnight_queue_5400_true_gpu_efficient_bge_large_encode_31k_remote_gpu_compute_policy_gpu_when_efficient_compose_refuse_gate_full_same_bge_stack_held_out_q54_q65_authoring_real_held_out_branch_queue_ready_note_incoming_same_remote_slot_batch_skunkworks_refuse_gate_full_verdict_vet_real_spread_discriminating_regime_8a_cell_author_fname_v2
-- Exp-Dev (Prover)
