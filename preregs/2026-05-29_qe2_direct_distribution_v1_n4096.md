# Pre-registration: qe2_direct_distribution_v1_n4096

**Date**: 2026-05-29
**Anchor**: qe2_direct_distribution_v1_n4096
**Script**: experiments/exp_qe2_direct_distribution_v1_n4096.py
**Queue**: remote_cpu_queue
**Trigger**: QE-2 Option-1 HARD_FAIL (softmax saturation = argmax-bottleneck deferred not avoided); Option-2 is parallel test alongside Option-3.
**Falsification source**: notes/qe2_option1_falsification_analysis_v278_2026-05-29.md
**Research source**: notes/research_coherent_multihop_qe2_v278_2026-05-29.md section c Option 2

## Scientific hypothesis

Option-2 (direct distribution propagation) propagates the FULL N-dim distribution
without normalization and without softmax. The score vector s_t carries raw
magnitude information through depth d, with a CONSTANT SCALAR damping factor
(1/sqrt(N)) per hop applied solely for numerical stability:

  s_1 = M * (entity_atoms[start_idx] * relation_atoms[rel_idxs[0]]) * damp
  For t = 1 .. depth-1:
    s_{t+1} = M * (s_t * relation_atoms[rel_idxs[t]]) * damp  -- NO normalization
  Final decode: argmax(entity_atoms @ s_d)

Key contrast with Option-3 (normalized spectral propagation):
- Option-3 normalizes ||s_t|| = 1 at each step (projects onto unit sphere;
  destroys magnitude information).
- Option-2 scales s_t by constant 1/sqrt(N) per step (constant scalar rescale;
  preserves DISTRIBUTION SHAPE, only the absolute scale is rescaled).

Argmax outcome is invariant under positive scalar scaling, so damping factor
does not alter the codeword competition.

P(smoke HARD_PASS at d=50) = 0.30-0.40 (research note section a P_deflated=0.34;
unchanged post-Option-1 since Option-1 falsification mechanism does not apply).

## N-suffix

_n4096 suffix -> production N = 4096 (PROT-018 binding).
N_FULL = 4096 confirmed in script.

## Pre-registered thresholds (envelope-fail-bands; NO ex-post threshold setting)

Same gating thresholds as Option-1/Option-3 (same scientific question, same
hypothesis about the d=50 cliff):

| Depth | HARD_PASS (>=) | MIDDLE_BAND | HARD_FAIL (<=) |
|-------|---------------|-------------|----------------|
| d=10  | 0.92          | 0.75-0.92   | 0.75           |
| d=25  | 0.80          | 0.50-0.80   | 0.50           |
| d=50  | 0.65          | 0.35-0.65   | 0.35           |
| d=100 | 0.50          | 0.25-0.50   | 0.25           |

**Gating depth**: d=50 (primary). HARD_PASS requires acc >= 0.65 at d=50.
HARD_FAIL requires acc <= 0.35 at d=50.

Direct distribution must outperform chained-cleanup baseline at d >= 25 to be
non-trivial.

## Numerical stability monitoring

The experiment tracks two diagnostics per (seed, depth):
- overflow_rate: fraction of trials where ||s_t|| exceeds 1e30 or contains NaN/Inf.
  If overflow_rate > 0.1 at any depth, the damping factor is insufficient.
- max_magnitude_log10: log10 of max |s_d| observed (diagnostic for spectral drift).
  Expected range: -2 to +2 with damp=1/sqrt(N). Drift outside [-10, +10]
  suggests spectral instability.

If overflow_rate > 0.1 at any depth, ROUTE TO STRATEGY before shipping FULL --
the damping schedule needs adjustment (likely 1/N or adaptive).

## Middle-band outcome plan

If MIDDLE_BAND at d=50 (acc in 0.35-0.65):
- Compare with Option-3 spectral propagation (parallel test); if Option-3
  outperforms, the normalization is doing useful work.
- Inspect overflow_rate and max_magnitude_log10 at each depth.
- Route to Strategy with diagnostic results; do NOT ship FULL without
  understanding the mechanism.

## HARD_PASS action

If smoke HARD_PASS (d=50 acc >= 0.65):
- Coherent multi-hop is RESCUED via direct distribution propagation.
- Ship FULL multi-seed (5 seeds, N=4096) to GPU for confirmation.
- Cap-map QE-2 row update: multi-hop cliff escaped via direct distribution.
- Product narrative: substrate coherent multi-hop via direct propagation.

## HARD_FAIL action

If HARD_FAIL (d=50 acc <= 0.35):
- Check Option-3 (parallel) result. If Option-3 also HARD_FAIL, then 2/3
  coherent multi-hop paths exhausted (Option-1 already HARD_FAIL).
- Coherent multi-hop closes as a research direction.
- Multi-hop story locks at depth 25-50 at 22-40% accuracy (chained-cleanup).
- Route verdict to Strategy with mechanism diagnosis:
  - Was it spectral drift? (high max_magnitude_log10, accuracy declining)
  - Was it overflow? (high overflow_rate)
  - Was it eigenvalue near-degeneracy? (low overflow_rate, flat profile)

## Walk-back gate

Smoke effect size is unknown (first run of Option-2). If smoke d=50 acc
is borderline (within 20% of 0.65 = in 0.52-0.78 range), double
planned FULL sample size before shipping FULL.

## Timeout estimate

Direct distribution same cost as Option-3 (M @ s per hop, no top-K/softmax overhead).
Wall time estimate: ~400-500s.
Formula: 1.5 * 500s * (4096/4096)^1.0 * (3/3) = 750s. Safety x4: 3000s.
PROT-019 floor for _n4096 = 14400s.
**timeout_s = 14400**

## Config

- N = 4096 (production N, PROT-018 binding)
- K_ENTITIES = 100 codewords
- K_REL = 20 relation atoms
- NUM_FACTS = 100 triples in factbase
- HOP_DEPTHS = [5, 10, 25, 50, 100]
- N_TRIALS_SMOKE = 20 per (seed, depth)
- SEEDS = [17, 23, 31] (3 seeds)
- damp = 1/sqrt(N) = 1/64 ~ 0.015625 per hop
- Direct: NO softmax, NO intermediate argmax, NO normalization
- Baseline: chained-cleanup (argmax at every hop)

## Formula self-tests (per PROT-019)

1. N_FULL == 4096 (PROT-018)
2. Damping invariance: argmax outcome same under positive scalar scaling
   (verified in instrumentation self-test)
3. s2 dtype == float32 (no sign_quantize in direct path)
4. Verdict self-test: 4 cases (HARD_PASS/HARD_FAIL/MIDDLE_BAND/INCONCLUSIVE) pass
5. Per-seed runner produces direct/cleanup/overflow_rate/max_magnitude_log10 keys
6. Filter: k_entities=20 > depth=5 at smoke scale (valid trial generation)
7. Overflow guard: function returns False on NaN/Inf or |s|.max() > 1e30

All self-tests confirmed passing before ship (run: python --self-test, exit 0).

## Note on parallel testing with Option-3

This anchor ships alongside qe2_spectral_propagation_v1_n4096 (Option-3) in the
same CPU queue. Both test the SAME scientific question (does substrate's
continuous internal layer escape softmax-saturation argmax-bottleneck?) via
DIFFERENT propagation schemes:
- Option-2: direct distribution (full magnitude + constant damping)
- Option-3: normalized spectral state (unit-norm projection)

If either HARD_PASS at d=50 acc >= 0.65, coherent multi-hop is rescued.
If both HARD_FAIL, coherent multi-hop closes definitively (2/3 paths exhausted
with Option-1 already stalled by softmax-saturation analog).
