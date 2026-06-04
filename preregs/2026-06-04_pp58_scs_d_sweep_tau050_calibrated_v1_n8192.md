# Prereg: pp58_scs_d_sweep_tau050_calibrated_v1_n8192

## Anchor
pp58_scs_d_sweep_tau050_calibrated_v1_n8192

## Priority
A (cycle 54: FLAG-1 interpretation-B companion to cycle-53 d-sweep@0.71; the scientifically-correct
SCS test -- substrate operating AT its real measured tau~0.71 via calibrated target=0.50)

## Scientific question
Cycle 50 established TAU_TARGET=0.50 -> tau_actual~0.71 at N=8192 (the substrate's actual operating
tau). Setting TAU_TARGET=0.71 instead overshoots to tau_actual~0.93 (cycle 52/53 FLAG 1). Here we sweep
the d range (via alpha = pattern count -> spike strength) at TAU_TARGET=0.50, and check whether SCS
gamma=(d + tau_actual/d)/(1+tau_actual), evaluated at measured tau_actual, agrees with empirical
isochoric-kappa3 gamma within 30%. Smoke confirmed calibration: tau_actual=0.7071 at N=256.

## Pre-registered bands
HARD-PASS: SCS formula matches (rel_err < 0.30) in >= 4/6 d-cells (mean over seeds).
MIDDLE: matches in 2-3/6 d-cells.
HARD-FAIL: matches in <= 1/6 d-cells.

## Formula self-tests (PROT-022)
1. SCS gamma(d=8, tau=0.50) = 8.0625/1.50 = 5.3750. [EXPECTED: 5.3750 +-0.001]
2. SCS gamma(d=2, tau=0) = 2.0. [EXPECTED: 2.0]
3. SCS gamma(d=1.5, tau=0) = 1.5. [EXPECTED: 1.5]
4. alpha_grid all < alpha_c=0.138. [EXPECTED: True for all]
5. 6 d-cells in full grid. [EXPECTED: 6]

## N-suffix binding (PROT-018)
anchor _n8192; production N = 8192. Script constant N = 8192.

## Timeout estimate
6 cells x asymmetric-W build/eigvalsh; ~2400s. PROT-019 floor for _n8192: timeout_s = 21600.

## Smoke gate
Smoke PASSED locally (N=256, 2 seeds): mechanics + instrumentation non-null verified; tau_actual=0.7071
confirms calibration; alpha sweep produces d-range (d 13.4 -> 4.9). Smoke verdict HARD_FAIL at N=256 is
expected small-scale behavior (gamma_emp inflated at tiny N), not an instrumentation fault.

## Queue
remote_cpu_queue (pure numpy; CPU).
