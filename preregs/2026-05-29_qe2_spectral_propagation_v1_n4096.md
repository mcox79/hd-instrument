# Pre-registration: qe2_spectral_propagation_v1_n4096

**Date**: 2026-05-29
**Anchor**: qe2_spectral_propagation_v1_n4096
**Script**: experiments/exp_qe2_spectral_propagation_v1_n4096.py
**Queue**: remote_cpu_queue
**Trigger**: QE-2 Option-1 HARD_FAIL (softmax saturation = argmax-bottleneck deferred not avoided)
**Falsification source**: notes/qe2_option1_falsification_analysis_v278_2026-05-29.md

## Scientific hypothesis

Option-3 (spectral propagation) avoids softmax saturation by propagating
substrate's internal continuous spectral state through depth-d chain
operations with NO softmax and NO intermediate argmax:

  s_1 = M * q               (factbase readout of query, N-dim)
  s_{t+1} = M * (s_t / ||s_t||)   (normalized spectral propagation)
  Final decode: argmax(entity_atoms @ s_d)

P(smoke HARD_PASS at d=50) = 0.25-0.35 (carries Option-1's remaining mass;
adjusted post-Option-1 HARD_FAIL per falsification analysis).

No prior empirical anchor for spectral propagation in this configuration.
Calibration-probe policy applies: bands are pre-registered at +-50% of
theoretical prediction. Theoretical prediction from research note section d:
spectral propagation should outperform chained-cleanup at d >= 25 IF
eigenvalue near-degeneracy is not dominant. If eigenvalue near-degeneracy
IS dominant (Entry 152 Agent G mechanism), Option-3 will HARD_FAIL in a
diagnostic way.

## N-suffix

_n4096 suffix -> production N = 4096 (PROT-018 binding).
N_FULL = 4096 confirmed in script.

## Pre-registered thresholds (envelope-fail-bands; NO ex-post threshold setting)

Same gating thresholds as Option-1 (same scientific question, same hypothesis
about the d=50 cliff):

| Depth | HARD_PASS (>=) | MIDDLE_BAND | HARD_FAIL (<=) |
|-------|---------------|-------------|----------------|
| d=10  | 0.92          | 0.75-0.92   | 0.75           |
| d=25  | 0.80          | 0.50-0.80   | 0.50           |
| d=50  | 0.65          | 0.35-0.65   | 0.35           |
| d=100 | 0.50          | 0.25-0.50   | 0.25           |

**Gating depth**: d=50 (primary). HARD_PASS requires acc >= 0.65 at d=50.
HARD_FAIL requires acc <= 0.35 at d=50.

Spectral must outperform chained-cleanup baseline at d >= 25 to be non-trivial.

## Middle-band outcome plan

If MIDDLE_BAND at d=50 (acc in 0.35-0.65):
- Inspect norm_collapse_rate at each depth. If norm_collapse_rate > 0.1
  at large d, the zero-norm mechanism is suppressing accuracy.
- If norm_collapse_rate is low, check whether performance is improving
  or flat across depths -- flat suggests eigenvalue degeneracy.
- Route to Strategy with diagnostic results; do NOT ship FULL without
  understanding the mechanism.

## HARD_PASS action

If smoke HARD_PASS (d=50 acc >= 0.65):
- Ship FULL multi-seed (5 seeds, N=4096) to GPU for confirmation.
- Cap-map QE-2 row update: multi-hop cliff partially escaped via spectral path.
- Product narrative: substrate coherent multi-hop via spectral propagation.

## HARD_FAIL action

If HARD_FAIL (d=50 acc <= 0.35):
- Both Option-1 (top-K soft mixture) and Option-3 (spectral propagation) have failed.
- Coherent multi-hop closes as a research direction.
- Multi-hop story locks at depth 25-50 at 22-40% accuracy (chained-cleanup).
- Route verdict to Strategy with mechanism diagnosis:
  - Was it eigenvalue degeneracy? (flat accuracy profile, low norm_collapse_rate)
  - Was it norm collapse? (high norm_collapse_rate at depth > 25)
  - Was it spectral drift? (accuracy declining linearly, not plateauing)
- Close cap_map QE-2 row with HARD_FAIL + 2-option exhausted.

## Walk-back gate

Smoke effect size is unknown (first run of Option-3). If smoke d=50 acc
is borderline (within 20% of 0.65 = in 0.52-0.78 range), double
planned FULL sample size before shipping FULL.

## Timeout estimate

Spectral propagation cheaper than Option-1 (no top-K/softmax/mix step).
Option-1 wall time estimate: ~600s. Spectral estimate: ~400-500s.
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
- Spectral: NO softmax, NO intermediate argmax
- Baseline: chained-cleanup (argmax at every hop)

## Formula self-tests (per PROT-019)

1. N_FULL == 4096 (PROT-018)
2. Unit-norm: ||s_t / ||s_t|||| == 1.0 (verified in instrumentation self-test)
3. s2 dtype == float32 (no sign_quantize in spectral path)
4. Verdict self-test: 4 cases (HARD_PASS/HARD_FAIL/MIDDLE_BAND/INCONCLUSIVE) pass
5. Per-seed runner produces spectral/cleanup/norm_collapse_rate keys with non-null values
6. Filter: k_entities=20 > depth=5 at smoke scale (valid trial generation)

All self-tests confirmed passing before ship (run: python --self-test, exit 0).
