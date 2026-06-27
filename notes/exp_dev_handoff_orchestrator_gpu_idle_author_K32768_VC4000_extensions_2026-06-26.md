# exp_dev hand-off — orchestrator: GPU IDLE — author K=32768 + V_C=4000 extensions

**Filed-by:** Orchestrator (Opus 4.7 1M)
**Date:** 2026-06-26
**Trigger:** USER 2026-06-26: "why is the remote cpu and remote gpu idle?" Orchestrator dispatched 8 cells to remote_cpu_queue (fully loaded). GPU runner is alive + idle because NO existing torch.cuda cell is undispatched.

## Pause state

Check `data/orchestrator_paused.flag` before dispatching. Pause flag absent at file-time.

## Backlog GPU cells to author

Per `notes/exp_dev_handoff_research_remote_routing_correction_phase_diagram_buildout_2026-06-26.md` Section "REMOTE_GPU candidates", these cells need authoring (none exist yet at the required regime):

1. **`phase_diagram_working_memory_multibank_K_extension_to_32768_v1`**
   - Extends `exp_phase_diagram_working_memory_multibank_K_extension_to_16384_v1.py` (completed today MIDDLE_BAND with by-construction-saturation at K=16384 MULTI_128x)
   - Add K=32768 [MULTI_256x, MULTI_512x] phase points
   - Inherit Fix #24 GPU mandate (torch.cuda; fp16 storage; gpu_util sampling)
   - Cost estimate: 8-10 GPU-hr
   - Discriminator: per the v1 MIDDLE_BAND landed today (1.0000 saturation at K=16384), need HARDER regime — increase FEATURE_OVERLAP_FRAC from 0.20 to 0.40 OR drop CUE_COS from 0.70 to 0.50 to escape by-construction-saturation
   - Queue: overnight_queue via `bash tools/orchestrator/queue_add.sh`

2. **`phase_diagram_multihop_depth_at_production_V_C_4000_v1`**
   - Extends `exp_phase_diagram_multihop_depth_at_production_V_C_2000_v1.py` (completed today SANITY_BREACH but with 5HOP=0.995 / 7HOP=0.982 / 10HOP=0.972 / 15HOP=0.958 — by-construction-saturation at V_C=2000)
   - Push V_C → 4000 to find the true depth cliff
   - GPU mandate per phase-diagram convention
   - Cost: 6-8 GPU-hr

3. **`phase_diagram_capacity_sweep_N16384_V_C_variable_v1`** (third item from routing-correction handoff)
   - V_C ∈ {2000, 4000, 8000} at N=16384
   - Multi-arm capacity-sweep on GPU; torch.cuda + batched matmul
   - Cost: 8-10 GPU-hr

## Cells already dispatched this cycle (do not re-dispatch)

remote_cpu_queue (8 pending or in-flight):
1. cortex_E_tensor_RETEST_fairness_v2 (timeout 18000s; 5h; Wave 1.6 ANCHOR 1)
2. cortex_E_tensor_separate_importance_v1 (14400s; 4h)
3. substrate_anisotropy_mimo_waterfill_v1 (14400s; 4h; in-flight now)
4. substrate_anisotropy_dg_pattern_separation_prewrite_v1 (14400s; 4h)
5. topk_composition_refuse_gate_v1 (10800s; 3h)
6. topk_composition_engineered_ambiguity_v1 (10800s; 3h)
7. pc_cleanup_attractor_v1 (10800s; 3h)
8. pc_cleanup_deeper_chains_v1 (10800s; 3h)
9. soft_topK_cleanup_distribution_preserving_v1 (10800s; 3h)
10. gap1_multihop_ldpc_rts_bidirectional_v1 (14400s; 4h)

## Latent verdicts to pull (GPU work landed today not yet surfaced to laptop)

These all completed on remote earlier today + need verdict pull + atomization:
- `phase_diagram_multihop_depth_extension_via_partition_oracle_v1` → CHAIN_GRADE_DEPTH_EXTENDS (chain-grade at depth=5/7/10/15 with PART_5HOP=0.9650 / PART_7HOP=0.8817 / PART_10HOP=0.8567 / PART_15HOP=0.8083)
- `phase_diagram_working_memory_multibank_K_extension_to_16384_v1` → MIDDLE_BAND (chain-grade at K=8192 MULTI_128x; saturated arms identified per Fix #28 caveat)
- `phase_diagram_multihop_depth_at_production_V_C_2000_v1` → SANITY_BREACH (numerical: BASELINE=0.9617 out of band; production V_C=2000 depth holds 5HOP=0.995 / 7HOP=0.982 / 10HOP=0.972 / 15HOP=0.958 — likely by-construction-saturation; needs Skunkworks tiering)

Pull via `scp marsh@home:C:/dev/hd-instrument/data/exp_<NAME>/metrics.json data/exp_<NAME>/` then `python tools/peek_arm_metrics.py <NAME>` per Fix #28 + route to Skunkworks for cert tier.

## Contract

- All new GPU cells: Fix #24 mandate (torch.cuda; gpu_util_p50 >= 50% in smoke; nvidia-smi sampling per arm)
- Substrate-only-decode gate; per-seed cv ≤ 0.05 for chain-grade; default tier MIDDLE per Fix #28
- text8 / BPC / next-token-prediction NOT relevant (USER 2026-06-26 pivot in force)
- Pre-reg HARDER regime parameters explicitly (escape by-construction-saturation observed in v1 cells)

## Autonomy declaration

exp_dev owns cell authoring + smoke + dispatch. Does NOT own: language-prediction evals; bypass of Fix #24 GPU-util check; relaxation of pre-reg bands.

---
-- Orchestrator (Opus 4.7-1M)
