# Pre-reg: continuous_output_multi_hop_v1_n4096

**Date:** 2026-05-30
**Anchor:** continuous_output_multi_hop_v1_n4096
**Script:** experiments/exp_continuous_output_multi_hop_v1_n4096.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** Multi-hop Path B (state-domain continuous propagation)

## Hypothesis

Keeping the substrate response continuous (no argmax) across hops
preserves enough analogue information that coherent paths of depth
>= 3 retrieve at accuracy >= 0.65 at N=4096, M=256 (well below the
M=2048 continuous-output degradation point from F-batch
CONT_ENV_MIDDLE_BAND).

## Pre-registered bands

| Outcome      | Condition                                                              |
|--------------|------------------------------------------------------------------------|
| HARD_PASS    | accuracy >= 0.65 at depth >= 3 in >=3/5 seeds at SOME depth in {3,4,5} |
| HARD_FAIL    | accuracy <= 0.20 at every depth in {2,3,4,5} in >=3/5 seeds            |
| MIDDLE_BAND  | otherwise                                                              |

## Calibration

Op D superposition was MIDDLE_BAND at similar M. The continuous-output
mechanism is mathematically distinct; no prior empirical anchor for this
specific propagation rule, so HARD_FAIL is set to the noise-dominated
floor (<= 0.20). HARD_PASS at 0.65 leaves margin above MIDDLE_BAND
without claiming substrate-quality argmax accuracy at depth.

## Self-test

`_instrumentation_selftest()`:
- N == 4096 (PROT-018).
- compute_verdict returns HARD_PASS / HARD_FAIL on synthetic cells.
- Forward pass at N=1024, M=32, depth=2 confirms accuracy is non-null,
  n_paths >= 1 (relation-graph closed correctness verified by selftest).

## Timeout estimate

smoke_wall_s ~ 0.07s at N_SMOKE=1024 depth in {2,3}. FULL N=4096 depths
{2,3,4,5} 5 seeds 80 paths. scaling_exp=1.5. Estimated wall ~ 600s.
Budget 21600s per PROT-019 _n4096 floor and user spec.
**timeout_s = 21600**

## Production config

N=4096, M=256, depths=[2,3,4,5], seeds=[7,17,23,31,41], n_paths=80.

## N-suffix binding

_n4096 -> production N = 4096 (PROT-018).
