# Prereg: wave14_rprime2_moe_K_sweep_v1

**Filed**: 2026-05-24 exp_dev
**Anchor**: R-PRIME-2 MoE M_c falsifier
**Source**: `notes/exp_dev_handoff_v193_queue_refill_2026-05-24.md` priority 1
**Spec**: `notes/research_R_PRIME_directions_2026-05-24.md` R-PRIME-2

## Hypothesis

If substrate retention is governed by per-expert capacity M_c (not global M_total), then K-sweep at fixed M_total should show retention(K) tracking f(M_total / K). Mixture-of-Experts framing: K disjoint expert sub-substrates each store M_total/K items.

## Design

- N=4096 substrate width
- M_total=4096 (fixed across sweep)
- K-sweep K in {2, 4, 8, 16} (4 points, monotone falsifier per R-PRIME-2 spec)
- 5 seeds: [7, 17, 23, 31, 41]
- Hadamard gating via random sign-vector projection -> argmax assignment
- Per-expert N_k = N/K, M_per_expert = M_total/K
- BSC capacity rule-of-thumb prediction: 1 - (M_per_expert) / (N_k / 4)

## Falsifier bands (pre-registered)

- **HARD-PASS — MoE row 🔬 -> 🟢 implicit-expert allocation supported**: retention monotone-non-decreasing in K (tol 0.02) AND lift = retention(K=16) - retention(K=2) >= 0.20 AND MoE-prediction tracking max_residual <= 0.10.
- **HARD-FAIL — MoE-on-substrate REJECTED**: lift < 0.05 (5 pp) AND max_dev_from_mean < 0.03 (3 pp).
- **MIDDLE**: any intermediate; report bands.

## Smoke result (smoke scale N=1024, M_total=256, K in {2,4}, 1 seed)

`MOE_KSWEEP_HARD_FAIL_REJECTED` at smoke scale (retention flat at 0.897 for both K=2 and K=4). Expected at smoke (M=256 too low load to see expert advantage). FULL at M_total=4096 is the hypothesis test.

## Self-test

`verdict self-test passed (4/4 cases)`.

## Queue

`queue=overnight_queue name=wave14_rprime2_moe_K_sweep_v1 script=experiments/exp_wave14_rprime2_moe_K_sweep_v1.py prereg=preregs/2026-05-24_wave14_rprime2_moe_K_sweep_v1.md timeout=5400`
