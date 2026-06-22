# p1 v2 -- LLM-class action-at-any-position pre-reg (sidecar to p1 v1)

**Date:** 2026-06-22
**Parent pre-reg:** [p1_action_at_any_position_phase_diagram_cell_prereg_2026-06-22.md](p1_action_at_any_position_phase_diagram_cell_prereg_2026-06-22.md) -- v1 mechanism / discriminator-regime / arms / corpus.
**Cell:** experiments/exp_p1_v2_action_at_any_position_LLM_class_v1.py (commit 69f129e4)
**Lane:** USER strategic vision -- substrate must survive operating-point shifts at LLM-class scale to credibly substitute for LLMs. v1 proved at N_DIM=16384; v2 verifies at N_DIM=65536 (4x scale).

## What changes from v1

| Knob | v1 (HARD_PASS, CERT 588) | v2 (this) |
|------|--------------------------|-----------|
| N_DIM | 16384 | 65536 (4x; LLM-class) |
| V_C  | 1024 -> 2048             | 4096 -> 8192 and 8192 |
| K_atoms | 200 | 500 (2.5x) |
| Implementation | numpy + explicit (N, N) W matrix | torch.cuda + IMPLICIT-W (low-rank: W never materialized) |
| Compute | local CPU | remote GPU (4060 Ti, 8 GB VRAM) |

The mechanism (VQ codebook + Hebbian binding + JL projection across N_DIM lift + 4-arm matrix per pair) is byte-identical to v1; only the SCALE and the GPU-friendly IMPLEMENTATION change.

## Pre-registered pairs (spawn prompt directive)

| Pair | P_0 | P_1 | Transform | Expected ratio |
|------|-----|-----|-----------|----------------|
| A_VC_lift | V_C=4096 N=65536 | V_C=8192 N=65536 | codebook-density lift at scale | >= 0.80 |
| B_NDIM_lift | V_C=8192 N=32768 | V_C=8192 N=65536 | substrate-dim lift to LLM-class | >= 0.80 |
| C_joint_lift | V_C=4096 N=32768 | V_C=8192 N=65536 | both lifted | >= 0.80 |

## HARD bands (locked from spawn prompt)

- **HARD_PASS:** ALL 3 pairs ratio (REPLAYED / WITHIN) >= 0.80 AND blank-sanity OK (BLANK <= 0.10) AND cv across 3 seeds <= 0.05 AND substrate-only gate preserved (n_llm_calls == 0).
- **HARD_FAIL:** ANY pair ratio < 0.50 OR blank-sanity broken OR cv > 0.10.
- **MIDDLE_BAND:** ratios in [0.50, 0.80) on at least one pair AND none below 0.50.

Note: the FAIL threshold is 0.50 (looser than v1's 0.20) because v2 is at LLM-class scale where partial portability is still informative. The PASS bar remains 0.80 (same as v1).

## Smoke gate evidence (this cycle, pre-dispatch)

- Local CPU --self-test: PASS (T1 WITHIN=1.000, T2 BLANK=0.100, T4 JL_drift=0.163, T5 implicit_vs_explicit max-abs-diff 1.75e-10)
- Local CPU smoke (HDLAB_EXP_NAME=..._smoke): HARD_PASS on tiny config (3 pairs ratios=1.0; mechanism + harness verified end-to-end)
- Remote GPU smoke (4060 Ti): HARD_PASS at smoke scale; gpu_util_mean=9.2% (expected for tiny smoke)
- Remote GPU single-seed FULL-config timing (Fix #3): 25s/seed total; per-pair wall ~8s each; gpu_util_mean=89.3% (well above Fix #24 50% bar); all 3 pairs HARD_PASS at single-seed scale (ratios=1.0, BLANK=0.0 across all pairs)

**Discriminator-regime check (Fix #16) at single-seed full scale:** WITHIN=1.0 (baseline OK), REPLAYED=1.0 ~ FRESH=1.0 (portability mechanism is real; data survived the transform), BLANK=0.0 (collapses; not artifact of key encoding). PASS.

## Dispatch parameters

- Queue: `overnight_queue` (GPU runner; routing-sanity gate requires `import torch` literal -> satisfied at line 80 of cell)
- Wall budget: 3600s (default; full-3-seed est ~2 min, headroom 60x; survives accidental restart)
- HDLAB_EXP_NAME: `p1_v2_action_at_any_position_LLM_class_v1`
- Runner stamps HDLAB_RUN_MODE=full by default; cell-side _smoke-suffix detect (TODO #6 resolution) routes any accidental smoke-entry to smoke mode.

## What this DOESN'T claim

- Does NOT certify N_DIM > 65536 (we only test up to 65536; >= 131072 needs a memory-mapped or sharded variant).
- Does NOT claim portability across ENCODER swaps (orthogonal axis; audit_core_C2_C3_whitened covers that).
- Does NOT claim portability across PROJECTION transforms (EXP_kv_learned_projection_v1 covers).
- Does NOT claim cross-DOMAIN portability.

This cell extends p1 v1's operating-point-shift portability claim from N_DIM=16384 to N_DIM=65536 (LLM-class), with K=500 atoms.

## SCHEMA-VET

Inherits SCHEMA-VET from parent v1 (same mechanism + arms + discriminator-regime). v2 is a SCALE extension, not a mechanism change. If HARD_PASS, Skunkworks ratifies as chain-grade extension of math::T3/EXP_p1_action_at_any_position_phase_diagram_v1 to LLM-class scale (proposed atom id: math::T3/EXP_p1_v2_action_at_any_position_LLM_class_v1).

-- Exp-Dev (Prover); cell-author dispatch cycle 2026-06-22
