# Pre-reg: mechanism_composition_v1_n4096

**Date:** 2026-05-30
**Anchor:** mechanism_composition_v1_n4096
**Script:** experiments/exp_mechanism_composition_v1_n4096.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** user msg 2026-05-30 next-1-2-week priorities ("if mechanisms make different errors, composing them should give error-correction")

## Hypothesis

The 3 multi-hop mechanisms (B continuous-output, D Bayesian, E spectral)
have different failure modes. Composing them in the BOUNDARY regime
(M=2048; where individual paths begin to degrade) should yield
error-correction at depth 5.

We test 3 composition designs:
- Composition A "intersection": all 3 top-1 must agree (selective)
- Composition B "weighted vote": softmax-weighted vote sum (always decides)
- Composition C "consensus check": 2-of-3 agreement on top-1 (selective)

## Pre-registered bands

| Outcome      | Condition                                                                |
|--------------|--------------------------------------------------------------------------|
| HARD_PASS    | at depth 5, at least one composition design improves accuracy by >=10% (absolute) over best individual mechanism in >=3/5 seeds AND Composition C inconclusive-rate <= 15% |
| HARD_FAIL    | all 3 composition designs perform WORSE than the best individual mechanism at every depth (composition introduces noise) |
| MIDDLE_BAND  | otherwise                                                                |

## Calibration

P(HP) estimate: 0.30-0.40. Composition can help only when mechanism
errors are sufficiently uncorrelated; substrate's shared
codebook + W structure means errors are likely correlated, which
counter-pulls. Per lit-scan calibration penalty, P deflated from
gut-feel 0.55 -> 0.40.

## Self-test

- N == 4096 (PROT-018); M_FULL == 2048 (boundary regime).
- DEPTHS_FULL == [3, 4, 5].
- decide_composition_A({1,0,0}, {1,0,0}, {1,0,0}) -> pick 0, ok=True
  (all agree) AND ({1,0,0}, {0,1,0}, {0,0,1}) -> ok=False (disagree).
- decide_composition_C({1,0,0}, {0,1,0}, {1,0,0}) -> pick 0 (B+E agree).
- decide_composition_B with strongly-agreeing scores picks 0.
- Forward pass at smoke (N=1024, M=256, d=3, K=8) shows accB/D/E and
  compA/B/C all bounded in [0, 1].

## Timeout estimate

smoke_wall_s = 0.45s. FULL: 3 depths x 5 seeds = 15 cells. Each cell
runs 40 queries, each query scores 50 candidates under 3 mechanisms.
Mechanism E (spectral, top-K signatures across depth hops) is the
heaviest. At N=4096 single-spectral-query ≈ 20-50 ms; 50 candidates *
40 queries * 3 mechanisms = 6000 path-scores per cell. Estimated
60-120s per cell. Total ~1800-3000s.
scaling_exp = 1.5. `ceil(1.5 * 0.45 * 4^1.5 * 5 * 15) = 405s` for the
ratio formula but doesn't capture per-query work scaling -- use direct
estimate. **timeout_s = 14400** (safety margin).

## Production config

N=4096, M=2048, depths=[3, 4, 5], seeds=[7,17,23,31,41],
K_candidates=50, n_queries=40, beta=4.0, top_k_sig=16.

## N-suffix binding

_n4096 -> production N = 4096 (PROT-018).
