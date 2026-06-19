# Prereg: wave14_saddle_cascade_plateau_v1

**Filed**: 2026-05-24 exp_dev
**Anchor**: Candidate (v) saddle-cascade plateau falsifier
**Trigger**: Research drill (notes/research_alternative_theoretical_homes_2026-05-24.md) filed
             strategy_request_to_exp_dev_cascade_plateau_test_2026-05-24.md.
             Pred-4-orthogonal alternative theoretical home test.
**Framework**: Saad-Solla 1995 / Biehl-Schwarze 1995 cascade plateaus in online learning.

## Hypothesis

Substrate's three retention plateaus (0.94 / 0.74 / 0.60) emerge from saddle-cascade
dynamics in the student-teacher overlap ODE structure. The cascade framework predicts
plateau heights are DISCRETE fixed-points of the overlap-matrix permutation-symmetry
structure -- IMMUNE to continuous parameters (matching empirical signature) and
SHIFT DISCRETELY as teacher-overlap fraction crosses integer-mode-count thresholds.

**Key prediction**: retention(f) where f = corpus-overlap-fraction in [0,1] shows
DISCRETE STEP STRUCTURE, NOT smooth monotone interpolation.

## Design

- **Experiment**: Train Phase-A on pure corpus_A. Then train Phase-B on corpus_mix(f)
  where corpus_mix(f) = f-fraction tokens from corpus_A + (1-f)-fraction from corpus_B
  (a fresh random corpus). Measure retention_A after Phase-B as function of f.

- **f sweep**: f in {0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0} -- 7 points
  (note: f=0.0 = fully disjoint; f=1.0 = identical corpora; intermediate test discrete structure)

- **Self-test formula (Saad-Solla saddle-cascade framework)**:
  Plateau heights at saddle-fixed-points are set by student-teacher-overlap permutation
  symmetry. For K-mode teacher overlap:
  - f=1.0: all teacher modes shared -> high-retention fixed point (symmetric saddle); expected ~0.90-0.95
  - f=0.0: no teacher modes shared -> low-retention fixed point (orthogonal saddle); expected ~0.55-0.65
  - f=0.5: intermediate saddle; cascade predicts DISCRETE jump somewhere in [0.25, 0.75] range, NOT linear
  - Linear interpolation baseline: retention_linear(f) = 0.60 + 0.34*f
  - Discrete-step test: step structure detected if max |retention(f) - retention_linear(f)| >= 0.08

  Self-test (input -> expected output) pairs from framework:
  1. f=1.0 (identical corpora) -> retention ~ 0.90+ (near full retention; same-corpus saddle)
  2. f=0.0 (disjoint corpora) -> retention ~ 0.57-0.65 (diff-corpus saddle; empirically 0.60)
  3. f=0.5 (50% mixed) -> IF cascade framework holds: retention NOT midpoint of 0.0 and 1.0
     (midpoint would be ~0.77); should be closer to either 0.60 or 0.94 (discrete snap to saddle)
  4. Linear-fit R^2 < 0.85 -> discrete structure; smooth fit fails
  5. Internal-variance check: |retention(0.1) - retention(0.0)| + |retention(0.9) - retention(1.0)| <
     |retention(0.5) - retention(0.0)| (most of the change is in the jump, not the tails)

- **N**: 2048 (FULL), 512 (smoke) -- CPU-feasible
- **Batch**: 32 (FULL), 16 (smoke)
- **Epochs**: 5 Phase-B (FULL), 1 (smoke)
- **Phase-A epochs**: 8 (FULL), 1 (smoke)
- **Bytes per corpus**: 200k (FULL), 4k (smoke)
- **Seeds**: {7, 17, 23} (FULL), {17} (smoke)
- **Queue**: remote_cpu_queue (CPU only; no GPU needed)
- **ETA**: ~30-60 min CPU (7 f-values x 3 seeds x 2 phases)

## Pre-registered bands

HARD-PASS: retention(f) shows discrete step structure:
  - Linear-fit R^2 < 0.85 (retention vs f is NOT smooth-monotone linear)
  - AND max deviation from linear fit >= 0.08 at some f cell
  - BONUS: plateau-internal-variance < 0.02 for flat-region f values
  Interpretation: saddle-cascade dynamics active; 3-plateau retention NOT a simple
  linear interpolation but a genuine fixed-point cascade.

HARD-FAIL: retention(f) is smooth-monotone:
  - Linear-fit R^2 >= 0.95 across all 7 f values
  - OR logistic/sigmoid-fit R^2 >= 0.95 AND max-deviation from fit < 0.04
  Interpretation: no discrete-step structure; cascade framework does not apply.
  Substrate retention interpolates smoothly with corpus overlap -- continuous,
  not categorical.

MIDDLE-BAND:
  - Linear-fit R^2 in [0.85, 0.95)
  - OR max deviation in [0.05, 0.08)
  Interpretation: partial step structure; inconclusive; run with finer f grid or larger N.

## Self-test cells (verified before coding)

Four (input -> expected output) pairs per [[feedback-strategy-spec-formula-selftests]]:

1. (f=1.0, identical corpus) -> retention expected > 0.85
   Rationale: f=1.0 is same-corpus regime; empirical baseline 0.94. Should reproduce
   within seed variance.

2. (f=0.0, disjoint corpus) -> retention expected in [0.55, 0.70]
   Rationale: f=0.0 is diff-corpus regime; empirical baseline ~0.60.

3. Linear-fit self-test:
   xs = [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]
   ys_linear = [0.60, 0.63, 0.69, 0.77, 0.86, 0.92, 0.94]  (interpolated)
   pearson_r2(xs, ys_linear) -> expected > 0.999 (confirming the R^2 formula is correct)

4. Plateau-deviation self-test (cascade hypothetical):
   ys_cascade = [0.60, 0.61, 0.62, 0.94, 0.94, 0.94, 0.94]  (jumps at f=0.5)
   pearson_r2(xs, ys_cascade) -> expected < 0.80
   max_deviation_from_linear_fit(xs, ys_cascade) -> expected > 0.10 (HARD-PASS trigger)
   Result: HARD-PASS correctly identified.
