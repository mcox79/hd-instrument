# Prereg: pp58_scs_tau_actual_d8_v1_n8192

## Anchor
pp58_scs_tau_actual_d8_v1_n8192

## Priority
A (cycle 52 PP-58 SCS R1 rescue; cheapest path to CONFIRM or RETIRE substrate-physics SCS framework)

## Scientific question
Cycle 50 (SCS tau_target=0.50 sweep) found ratio=1.416 -- the first close fit -- with measured
tau_actual=0.71 (41% overshoot from target). R1 rescue: build the controlled-asymmetry W TARGETING
tau=0.71 so the substrate operates in the tau~0.71 regime, and check whether SCS formula
gamma=(d + tau_actual/d)/(1+tau_actual), evaluated at the measured tau_actual, agrees with the
empirical isochoric-kappa3 gamma within 30%.

## Pre-registered bands
HARD-PASS: ratio in [0.85, 1.18] OR match_30% >= 0.6 (formula within 30% on >= 3/5 seeds).
MIDDLE: ratio in [0.5, 2.0] but match_30% < 0.6.
HARD-FAIL: ratio < 0.5 OR ratio > 2.0.

## Formula self-tests (PROT-022)
1. SCS gamma(d=8, tau=0.71) = (8 + 0.71/8)/(1+0.71) = 8.08875/1.71 = 4.7303. [EXPECTED: 4.7303 +-0.001]
2. SCS gamma(d=8, tau=0) = 8.0. [EXPECTED: 8.0]
3. SCS gamma(d=1, tau=0) = 1.0. [EXPECTED: 1.0]
4. M = int(0.05 * 8192) = 409. [EXPECTED: 409]

## N-suffix binding (PROT-018)
anchor _n8192; production N = 8192. Script constant N = 8192.

## Timeout estimate
Similar to tau=0.50 test (~9000s). PROT-019 floor for _n8192 anchors: timeout_s = 21600.

## Smoke gate
Smoke PASSED locally (N=256, 2 seeds): mechanics + instrumentation non-null verified. Smoke verdict
HARD_FAIL at N=256 is expected small-scale behavior (not an instrumentation fault); full-N regime differs.

## Known design caveat (surfaced to orchestrator)
Build with tau_target=0.71 OVERSHOOTS: smoke measured tau_actual=0.93 at N=256 (target 0.71). The
substrate therefore operates ABOVE 0.71, not AT 0.71. gamma_SCS is still evaluated at the measured
tau_actual per spec. If the orchestrator intended the substrate to operate AT tau_actual=0.71, that
requires calibrating tau_target ~0.50 (which reproduces cycle 50 unchanged). Flagged in shipped report.

## Queue
remote_cpu_queue (pure numpy; CPU).
