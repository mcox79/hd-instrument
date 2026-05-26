# Prereg: wave14_ib_plateau_test_v1

**Filed**: 2026-05-24 exp_dev
**Anchor**: Candidate (iv) IB phase-transition plateau falsifier
**Trigger**: Research drill (notes/research_alternative_theoretical_homes_2026-05-24.md) filed
             strategy_request_to_exp_dev_ib_plateau_test_2026-05-24.md.
             Pred-4-orthogonal alternative theoretical home test.
**Framework**: Tishby-Zaslavsky / Wu-Fischer-Tegmark 2020 IB phase-transition framework.

## Hypothesis

Substrate's three retention plateaus emerge from Information-Bottleneck phase transitions.
Wu-Fischer-Tegmark 2020 framework: IB Lagrangian shows DISCRETE phase transitions at
critical beta-values; each transition = onset-of-learning-a-new-class.

**Key prediction**: plateau-COUNT should track K (number of distinct training corpora).
K=1 corpus -> 1 plateau; K=2 corpora -> 2 plateaus; K=3 corpora -> 3 plateaus; etc.

## Design

- **Experiment**: Train substrate on K distinct corpora in sequence (stages).
  Measure retention at each stage's level after all K stages complete.
  Vary K in {1, 2, 3, 4, 5} and count the number of distinct retention-level plateaus.

- **K sweep**: K in {1, 2, 3, 4, 5} -- 5 levels
  Smoke: K in {1, 2, 3} -- 3 levels

- **Implementation**: For each K, train K sequential phases (A -> B -> C -> ... -> K-th).
  After all K phases, measure retention at each prior phase level.
  Report retention per stage as a function of K. IB framework predicts:
  - K=1: 1 distinct retention level (trivial -- no interference)
  - K=2: 2 distinct retention levels (A-level vs B-level separation)
  - K=3: 3 distinct retention levels (matching empirical 0.94/0.74/0.60)
  - K=4: 4 distinct levels (or plateau at 3 if substrate capacity is reached)
  - K=5: 4-5 distinct levels (similar)

- **Plateau counting**: retention values from all stages; count distinct clusters
  (within-cluster variance < 0.02). IB framework predicts count >= min(K, capacity_ceiling).

- **Self-test formula (Wu-Fischer-Tegmark 2020)**:
  Number of IB phase transitions = number of class-clusters in joint (X, Y) distribution.
  For K corpora: K corpus-types = K class-clusters; IB predicts K transitions.
  Self-test (input K, expected plateau-count) pairs:
  1. K=1 -> plateau_count = 1 (only one corpus, no differentiation)
  2. K=2 -> plateau_count = 2 (two corpora, two distinct retention levels)
  3. K=3 -> plateau_count = 3 (three corpora, three levels; matches empirical)
  4. K=5, retention values all equal (degenerate) -> plateau_count = 1 (worst case; not predicted by IB)

- **N**: 2048 (FULL), 512 (smoke)
- **Batch**: 32 (FULL), 16 (smoke)
- **Epochs per phase**: 5 (FULL), 1 (smoke)
- **Phase-A epochs**: 8 (FULL), 1 (smoke)
- **Bytes per corpus**: 200k (FULL), 4k (smoke)
- **Seeds**: {7, 17, 23} (FULL), {17} (smoke)
- **Queue**: remote_cpu_queue (CPU only; no GPU needed)
- **ETA**: ~40-80 min CPU (5 K-values x 3 seeds x up-to-5 phases)

## Pre-registered bands

HARD-PASS: plateau-count monotonically tracks K (Spearman rank-correlation >= 0.90):
  - plateau_count(K=1) <= plateau_count(K=2) <= plateau_count(K=3) <= ... <= plateau_count(K=5)
  - AND at least K=3 gives plateau_count >= 3 (validates the empirical 3-plateau observation)
  - BONUS: K=3 produces retention values within 0.03 of empirical 0.94/0.74/0.60
  -> IB phase-transition framework supported; substrate plateaus = class-cluster boundaries.

HARD-FAIL: plateau-count does NOT track K:
  - All K values give same plateau structure (plateau_count constant across K)
  - OR plateau-count is random/non-monotone (Spearman rank-correlation < 0.20)
  - OR retention is smooth-continuous across stages with no discrete-step structure
  -> IB framework does not apply.
  Rehab: candidate (v) cascade-plateau (separate test); or accept continuous interpretation.

MIDDLE-BAND:
  - Spearman rank-correlation in [0.20, 0.90)
  - OR plateau_count tracks K for some K values but not all
  -> Partial tracking; inconclusive.

## Self-test cells (verified before coding, per [[feedback-strategy-spec-formula-selftests]])

1. K=1 trivial case: train on 1 corpus, retention_A = 1 stage only -> plateau_count = 1
2. K=2: train A->B, measure retA and retB; if retA != retB (distinct levels) -> plateau_count >= 2
3. Plateau-counting algorithm test: values = [0.94, 0.93, 0.74, 0.73, 0.60, 0.61]
   -> cluster at 0.935 (var=0.0005), 0.735 (var=0.0005), 0.605 (var=0.0005)
   -> plateau_count = 3 (all within-cluster variance < 0.02)
4. Degenerate test: values = [0.70, 0.71, 0.70, 0.71, 0.70] -> plateau_count = 1
   (all within 0.02 of each other -> single cluster)
