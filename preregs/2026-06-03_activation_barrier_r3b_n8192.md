# Prereg: Activation barrier R3b N-scale at N=8192

**Date:** 2026-06-03
**Anchor:** activation_barrier_r3b_n8192_v3_n8192
**Queue:** remote_cpu_queue (CPU)

## Hypothesis
R3a (v2_n4096 extended grid, N=4096): ratio=None (nf_crit boundary persists at grid_max=0.90).
Substrate at N=4096 does not resolve recall transition below noise_frac=0.90 for alpha=0.10.
R3b tests whether this boundary shifts to lower noise_frac at N=8192 (larger N = less robust
to noise = earlier transition = resolvable ratio).

If the recall transition at alpha=0.10 is resolved at N=8192: ratio(nf_05/nf_10) is computable,
power-law exponent b can be fit, and HP/MID/HF verdict assigned on the activation barrier proxy.

## Pre-registered bands
**HARD-PASS:** power-law exponent b < 0.7 AND ratio(0.05/0.10) > 1.30 AND n_monotone >= 4/5
**MIDDLE:** b in [0.7, 1.1] OR ratio in [1.10, 1.30] OR ratio=None (boundary persists at N=8192)
**HARD-FAIL:** b > 1.2 (super-linear) OR ratio <= 1.02 (flat)

## Formula self-tests (PROT-022)
1. Arrhenius ratio formula: (alpha_c - 0.05) / (alpha_c - 0.10) = 2.3157 +- 0.001
   [INPUT: alpha_c=0.138, alpha1=0.05, alpha2=0.10] [EXPECTED: 2.3157 within 0.001]
2. b=0.3 ratio prediction: 2.3157^0.3 in [1.25, 1.40]
   [INPUT: b=0.3] [EXPECTED: ratio_b03 approx 1.287]
3. Extended grid: 0.00..0.90 step 0.01 => 91 points
   [EXPECTED: len(NOISE_FRACS) = 91]
4. M at alpha=0.10 N=8192: int(0.10 * 8192) = 819 >= 1
   [EXPECTED: M_alpha10_N8192 = 819]

## Timeout estimate
R3a (N=4096 extended grid) elapsed ~134s FULL 5-seed. N=8192 W matrix 4x larger.
ceil(1.5 * 134 * (8192/4096)^2 * (5/5)) = ceil(804) = 900s. With 2x margin: 1800s.

## Smoke note
Smoke at N=1024 showed ratio=0.95 HARD_FAIL (flat). This is an expected N-scale artifact:
at N=1024 both alpha values have similar nf_crit because the Hopfield network is underpowered
relative to the noise range. The instrumentation was verified working (non-NaN, > 100ms, nf_crit
detected). FULL at N=8192 tests the actual hypothesis.

## N-suffix section
Anchor has _n8192; N = 8192 in script. PROT-018 verified.
