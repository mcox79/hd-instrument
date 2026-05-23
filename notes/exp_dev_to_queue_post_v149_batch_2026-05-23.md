# Exp Dev -> Queue: Strategy 09:35 v149 P3 + P4 + P5 shipped

**Sender**: Experiment Dev
**Date**: 2026-05-23 ~09:50 EDT
**Topic**: 3 new experiments ready for queue pickup — Strategy 09:35 v149 P3 (N=1M) + P4 (multi-component order param) + P5 (Bet A 5-seed)
**Trigger**: User "check now" + Strategy 09:35 post-v149 priorities

## Headline finding (smoke)

**Sub-K-region order parameter SUB_REGION_STABLE at smoke** — 2/3 regions
seed-consistent (normal=0.957, longer=0.895, resonance=0.849; threshold 0.85).
Gap 2 FULL ORDER_PARAM_NONE refuted global q_overlap, but sub-K decomposition
reveals stability. If FULL ratifies, substrate-physics gains MULTI-COMPONENT
order parameter structure (Parisi-like multi-region q decomposition).

## What landed

1. `experiments/exp_wave14_order_param_sub_K_region_v1.py` (Strategy 09:35 P4)
   - Prereg: `preregs/2026-05-23_wave14_order_param_sub_K_region_v1.md`
   - q_overlap restricted to sub-K regions: K_RESONANCE_BROAD (900-1500), normal (100-500), longer (2000+).
   - Smoke verdict: ORDER_PARAM_SUB_REGION_STABLE 2/3 regions stable
   - Verdicts: SUB_REGION_STABLE / HIERARCHICAL (3+ plateaus) / GLOBAL_NONE_CONFIRMED
   - Expected ~30 GPU-min FULL at N=16384, 5 seeds.

2. `experiments/exp_wave14_substrate_N1048576_v1.py` (Strategy 09:35 P3)
   - Prereg: `preregs/2026-05-23_wave14_substrate_N1048576_v1.md`
   - Backward-smoother readout at N=1048576 K=100 depth=50 n_trials=10.
   - Smoke verdict (N=65536): N1M_SCALES acc=1.000 (gates clean; FULL at N=1M)
   - Verdicts: N1M_SCALES (>=0.5) / N1M_PARTIAL / N1M_KILLED
   - Expected ~60-120 GPU-min FULL at N=1M (16x V2.D scope).

3. `experiments/exp_wave14_betA_continual_edit_N65536_5seed_v1.py` (Strategy 09:35 P5)
   - Prereg: `preregs/2026-05-23_wave14_betA_continual_edit_N65536_5seed_v1.md`
   - Wraps existing betA_continual_edit pattern with 5-seed loop, n_edits=100.
   - Smoke verdict (N=4096): BETA_5SEED_KILLED kept_acc=0.040 (EXPECTED — M_init=N capacity-limited; same as cycle 132)
   - Verdicts: BETA_5SEED_PASS / PARTIAL / KILLED
   - Expected ~60-120 GPU-min FULL at N=65536 (likely KILLED, 5-seed confirms reproducibility)

## Local gate

- Self-tests: PASSED for all 3
- Smokes: PASSED with valid metrics.json for all 3
- ASCII-only output per [[feedback_ascii_only_in_scripts]]

## Queue request

Add to overnight_queue:
- name=wave14_order_param_sub_K_region_v1 script=experiments/exp_wave14_order_param_sub_K_region_v1.py prereg=preregs/2026-05-23_wave14_order_param_sub_K_region_v1.md timeout=2400
- name=wave14_substrate_N1048576_v1 script=experiments/exp_wave14_substrate_N1048576_v1.py prereg=preregs/2026-05-23_wave14_substrate_N1048576_v1.md timeout=7200
- name=wave14_betA_continual_edit_N65536_5seed_v1 script=experiments/exp_wave14_betA_continual_edit_N65536_5seed_v1.py prereg=preregs/2026-05-23_wave14_betA_continual_edit_N65536_5seed_v1.md timeout=7200

## Strategy 09:35 status summary

- **P1 Bet Z.5 Phase 1**: NOT shipped (long impl, deferred per leverage)
- **P2 Observability V2 Kovacs + avalanche**: shipped at 09:04 commit `9d4a04e`; awaiting queue pickup
- **P3 N=1M substrate**: shipped now
- **P4 Multi-component order parameter**: shipped now (smoke SUB_REGION_STABLE)
- **P5 Bet A 5-seed**: shipped now

## Per [[feedback-sessions-self-coordinate]]

File-routing only.

EOF marker.
