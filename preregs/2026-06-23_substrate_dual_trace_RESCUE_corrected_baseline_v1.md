# Prereg: substrate_dual_trace_RESCUE_corrected_baseline_v1

**Date pre-registered:** 2026-06-23
**Anchor:** substrate_dual_trace_RESCUE_corrected_baseline_v1
**Script:** experiments/exp_substrate_dual_trace_RESCUE_corrected_baseline_v1.py
**Queue:** overnight_queue (GPU; N_DIM=8192 matmul-bound)
**PROT-018:** no _n suffix; production N=8192 stated explicitly in script.

## Motivation

Skunkworks VET on v1 dual-trace cell returned MEASURED_MECHANISM instead of chain-grade.
Root cause: ARM_BASELINE in v1 used cf-RPE at SPARSE_BIPOLAR_F=0.02, NOT the fair_harness
pure rank-1 Hebbian at f=0.05. The corrected comparison with the TRUE fair_harness chain-
grade baseline (7.3065 BPC) has not been run. This cell runs it.

See: notes/skunkworks_to_all_LANDED_VET_dual_trace_sequential_neuromd_HARD_PASS_2026-06-23.md

## Three arms

1. ARM_FAIR_HARNESS_RANK1: pure rank-1 Hebbian W = sum outer(E_tgt, E_src) at f=0.05.
   Verbatim reproduction of fair_harness build_rank1_W_gpu (lines 349-367).
   SANITY: must reproduce 7.3065 +/- 0.05 BPC.

2. ARM_DUAL_TRACE_v1_REPLAY: exact dual-trace from v1 at f=0.02 (build_W_dual_trace verbatim).
   SANITY: must reproduce 7.2213 +/- 0.10 BPC.

3. ARM_DUAL_TRACE_AT_F005: dual-trace mechanism at f=0.05 (sparsity-axis control).
   Isolates: is dual-trace lift sparsity-dependent?

## Config

N_DIM=8192, N_TRAIN=100_000, N_HELD=20_000, VOCAB_CAP=4000, SEEDS=[7, 17, 23].
Matches v1 and fair_harness configs exactly for direct comparison.

## Pre-registered bands (IMMUTABLE)

- **CHAIN_GRADE_TIER_UP**: ARM_DUAL_TRACE_v1_REPLAY beats ARM_FAIR_HARNESS_RANK1 by >= +0.20 bits BPC.
  Outcome: Skunkworks rescue criterion satisfied; cert tier UP to chain-grade.

- **MEASURED_MECHANISM_CONFIRMED**: lift in [+0.05, +0.20) bits.
  Outcome: real but below chain-grade bar; consistent with Skunkworks MEASURED_MECHANISM verdict.

- **HARD_FAIL_RESCUE**: lift < +0.05 OR ARM_DUAL_TRACE_v1_REPLAY fails sanity gate (7.2213 +/- 0.10).
  Outcome: dual-trace has no benefit over TRUE baseline; routes to encoder-replacement diagnostic.

- CV across 3 seeds < 0.05 mandatory.

## Sanity gates

ARM_FAIR_HARNESS_RANK1 bpc_mean must be in [7.2565, 7.3565] (7.3065 +/- 0.05).
ARM_DUAL_TRACE_v1_REPLAY bpc_mean must be in [7.1213, 7.3213] (7.2213 +/- 0.10).
If either sanity gate fails: SANITY_FAIL verdict; routes back to exp_dev for diagnosis.

## Bonus sparsity-axis reading

ARM_DUAL_TRACE_AT_F005 vs ARM_DUAL_TRACE_v1_REPLAY:
- If AT_F005 is better (lower BPC) than v1_REPLAY: dual-trace benefits from f=0.05.
- If AT_F005 similar to v1_REPLAY: dual-trace mechanism is sparsity-independent.
- If AT_F005 worse: f=0.02 was the right sparsity for dual-trace.

## Timeout estimate

Reference: v1 full run elapsed_s=507.76s (3 seeds x 3 arms, GPU, same N config).
Rescue cell: 3 arms x 3 seeds = same structure.
Estimate: 507.76 * 1.50 safety margin = 762s.
Round up to nearest 300s: **timeout_s=900**.

Smoke wall time: 26.8s at N_DIM=512 N_TRAIN=2000 (1 seed, 3 arms, CPU).
FULL/smoke N ratio = 8192/512 = 16; FULL/smoke seed ratio = 3/1 = 3.
Formula: ceil(1.5 * 26.8 * 16^1.5 * 3) = ceil(1.5 * 26.8 * 64 * 3) = ceil(7741) = 7800s.
However, the GPU matmul at N=8192 is much faster than CPU at N=512; v1 reference (507s GPU)
is the tighter anchor. Using v1_reference * 1.5 = 762s, rounded to 900s.

Note: estimate is well under 7200s (2h) and 14400s (4h) limits.

## Sources

- experiments/exp_fair_harness_substrate_as_lm_v1.py lines 349-367 (build_rank1_W_gpu)
- experiments/exp_substrate_dual_trace_sequential_neuromod_LM_v1.py (dual-trace mechanism)
- data/exp_fair_harness_substrate_as_lm_v1/metrics.json (rank1 7.3065)
- data/exp_substrate_dual_trace_sequential_neuromd_LM_v1/metrics.json (dual 7.2213)
- notes/skunkworks_to_all_LANDED_VET_dual_trace_sequential_neuromod_HARD_PASS_2026-06-23.md

## N-suffix section

No _nN suffix. Production N = 8192. Rationale: matches fair_harness and v1 config for direct
comparison. The anchor name carries no N-suffix so PROT-018 N-suffix binding does not apply.
