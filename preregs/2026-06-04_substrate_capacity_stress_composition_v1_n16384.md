# Prereg: substrate_capacity_stress_composition_v1_n16384

## Anchor
substrate_capacity_stress_composition_v1_n16384

## Priority
A (Research redirect routing_redirect_depth_to_capacity_stress_test; the genuinely-informative next
PP-12/Q-A3 experiment -- locates the composition capacity boundary; depth-ladder now STOPPED)

## Scientific question
At N=16384 fixed, L=50 fixed, sweep inner-layer load M/N in {0.03,0.06,0.09,0.12,0.15,0.18,0.21}
(spans below/at/above classical alpha_c=0.138). Does composition fidelity stay EXACT-1.0000 below
alpha_c and degrade above it (classical Hopfield), or stay EXACT throughout (modern-Hopfield class)?

## Pre-registered bands
HARD-PASS: EXACT (>=0.9999) at M/N<=0.12 AND degrades (<0.9999) at M/N>=0.15; 5/5 seeds.
MIDDLE: degradation present but boundary far from alpha_c, or 3-4/5 seeds.
HARD-FAIL: EXACT at ALL M/N incl 0.21 (no classical boundary -> modern-Hopfield class OR composition
not loading the stored bank) -- still informative about substrate algebraic class.

## Formula self-tests (PROT-022)
1. M_c = round(0.138*16384) = 2261. 2. MN grid spans alpha_c. 3. L=50 chain roundtrip exact.
4. GPU mem > 0 after W build. [ALL in script _selftest]

## N-suffix binding (PROT-018)
anchor _n16384; production N=16384. 5 seeds (PROT-021).

## Timeout
7 M/N cells x 5 seeds x L=50 composition at N=16384; ~35 min est. PROT-019 floor: 21600s.

## Smoke gate
--skip-smoke: no local CUDA. Remote --self-test gates M_c + chain + GPU mem. GPU template (assert cuda,
device=cuda, batched matmul) per mandate.

## Queue
overnight_queue (GPU required).
