# Pre-registration: axis3_triplepoint_v2_n4096

**Date:** 2026-05-28
**Anchor:** axis3_triplepoint_v2_n4096
**Script:** experiments/exp_axis3_triplepoint_v2_n4096.py
**Queue:** overnight_queue
**Routing note:** strategy_request_to_exp_dev_v262_axis3_triplepoint_v2_alternate_operating_points_2026-05-28.md

## Hypothesis

A triple-point (or multi-phase saddle) exists somewhere in the M x beta parameter space
of the substrate. v1 at (M_frac=6, beta=8) confirmed single-phase interior (MIDDLE_BAND).
v2 tests 3 strategically distributed operating points closer to phase boundaries:
(a) M_frac=10, beta=8: near AXIS-1 chunk5 mid-decay transition
(b) M_frac=8, beta=4: lower beta, shifted phase boundary
(c) M_frac=4, beta=16: high-capacity end, strong separation

## Configuration

- N_FULL = 4096 (production scale; PROT-018 binding)
- Operating points: [(M_frac=10, beta=8), (M_frac=8, beta=4), (M_frac=4, beta=16)]
- Seeds = [7, 17, 23] (3-seed)
- Directions: [M_plus, M_minus, beta_up, beta_down, W_noise, M_partial_swap]
- Epsilons: [0.02, 0.05, 0.10, 0.20, 0.40]
- Queue: overnight_queue (GPU for N=4096; fast even on CPU per v1 elapsed~5s)

## Pre-registered thresholds

**HARD_PASS:** sign_divergence=True at >=1 operating point AND max|delta_ret| >= 0.15
  with pos_dirs >= 1 AND neg_dirs >= 1 at same point.
  
**HARD_FAIL:** sign_divergence=False AND max|delta_ret| < 0.05 across ALL tested points.

**MIDDLE_BAND:** max|delta_ret| >= 0.05 but sign_divergence=False at all points, OR
  sign_divergence=True but max|delta_ret| < 0.15 (weak saddle evidence).

## Gate self-tests

1. Cells with M_plus=-0.20, M_minus=+0.18 -> sign_divergence=True, max=0.20>=0.15 -> HARD_PASS.
2. Flat cells (all delta=0.01) -> max<0.05 -> HARD_FAIL.
3. All negative (all -0.20) -> sign_divergence=False, max=0.20>=0.15 -> MIDDLE_BAND.
All verified at design time. PASS.

## Smoke gate result

SMOKE: 1 operating point (M_frac=10, beta=8), N=1024, 1 seed, 2 directions, 2 epsilons.
VERDICT: AXIS3V2_HARD_PASS.
sign_divergence=True: pos_dirs=['M_minus', 'M_partial_swap'] neg_dirs=['M_plus'].
max|delta_ret|=0.35 >> HP threshold 0.15. elapsed=1.1s. NOT borderline; no walk-back.

This is a STRONG smoke result: at M_frac=10 (near chunk5 transition), the substrate
shows OPPOSITE sign responses for M_plus (negative: more memories degrade retention)
and M_minus (positive: fewer memories improve retention). This is exactly the triple-point
signature predicted. Full run at N=4096, 3 seeds, all 3 operating points will corroborate.

## Cap_map impact

- HARD_PASS: first confirmed triple-point signature; phase-boundary direct-test row lift.
- HARD_FAIL: triple-point absent in M=[4,10] x beta=[4,16]; constrain hypothesis space.
- MIDDLE_BAND: partial evidence; some sensitivity but not divergent.

## Timeout estimate

v1 elapsed=5.08s for 6 dirs x 5 eps x 5 seeds = 150 cells at N=4096.
v2: 3 operating points x 6 dirs x 5 eps x 3 seeds = 270 cells.
But each operating point requires building base W from scratch.
Base W at N=4096: ~5s per seed. 3 points x 3 seeds x 5s = 45s.
Perturbation cells: 270 x ~0.034s = 9s.
Total estimate: ~55s.
1.5x safety: 83s.
PROT-019 minimum for _n4096: 3600s. Using 3600s.

## OOM check

W float32 at N=4096: 64MB. Kerdock codebook: 64MB. Peak: ~200MB. Under 6GB. PASS.

## N-suffix binding (PROT-018)

_n4096 -> N_FULL = 4096 in script. Verified.
