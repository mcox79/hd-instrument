# Prereg: pp58_scs_d_sweep_tau_actual_v1_n8192

## Anchor
pp58_scs_d_sweep_tau_actual_v1_n8192

## Priority
A (cycle 53 item B: complements pp58_scs_tau_actual_d8 -- full d range at substrate actual tau)

## Scientific question
Across a range of spike strengths d (swept via alpha = pattern count), does the SCS formula
gamma=(d + tau_actual/d)/(1+tau_actual), evaluated at measured tau_actual, agree with the empirical
isochoric-kappa3 gamma within 30% in a majority of cells? Substrate built with controlled asymmetry
at TAU_TARGET=0.71 (same convention as item A).

## Pre-registered bands
HARD-PASS: SCS formula matches (rel_err < 0.30) in >= 4/6 d-cells (mean over seeds).
MIDDLE: matches in 2-3/6 d-cells.
HARD-FAIL: matches in <= 1/6 d-cells.

## Formula self-tests (PROT-022)
1. SCS gamma(d=8, tau=0.71) = 8.08875/1.71 = 4.7303. [EXPECTED: 4.7303 +-0.001]
2. SCS gamma(d=2, tau=0) = 2.0. [EXPECTED: 2.0]
3. SCS gamma(d=1.5, tau=0) = 1.5. [EXPECTED: 1.5]
4. alpha_grid all < alpha_c=0.138. [EXPECTED: True for all]
5. 6 d-cells in full grid. [EXPECTED: 6]

## N-suffix binding (PROT-018)
anchor _n8192; production N = 8192. Script constant N = 8192.

## Timeout estimate
6 cells x asymmetric-W build/eigvalsh; ~2400s. PROT-019 floor for _n8192: timeout_s = 21600.

## Smoke gate
Smoke PASSED locally (N=256, 2 seeds): mechanics + instrumentation non-null verified; alpha sweep
produces a d-range (d 5.8 -> 2.9). Smoke verdict HARD_FAIL at N=256 is expected small-scale behavior
(gamma_emp inflated at tiny N), not an instrumentation fault.

## Known design caveat (same as item A; surfaced to orchestrator)
d is a MEASURED quantity (leading/bulk eigenvalue ratio of W), not a free knob -- "sweep d in
{2,4,6,8,10,12}" is realized by sweeping alpha so achieved d spans a range (reported per cell). Build
at TAU_TARGET=0.71 OVERSHOOTS to tau_actual~0.93 (smoke). Convention matches item A; if orchestrator
resolves FLAG 1 toward calibrated tau_target~0.50, the same change applies to both A and B.

## Queue
remote_cpu_queue (pure numpy; CPU).
