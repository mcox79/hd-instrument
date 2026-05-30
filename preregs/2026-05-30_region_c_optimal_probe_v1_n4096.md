# Pre-registration: region_c_optimal_probe_v1_n4096

**Date:** 2026-05-30
**Anchor:** region_c_optimal_probe_v1_n4096
**Script:** experiments/exp_region_c_optimal_probe_v1_n4096.py
**Queue:** overnight_queue
**Timeout:** 21600s

## Hypothesis

Region C (beta > beta_c, M < M_c) provides substantially better
killer-feature characteristics than standard Region A (beta < beta_c,
M < M_c) on the 6-metric battery. If true, Region C is substrate's
"best" region and product positioning shifts toward high-beta operation.

## Configuration

- N: 4096 (PROT-018 binding)
- 8 cells (4 Region C, 4 Region A) matched on M_frac:
  - C: (beta=16,  M_frac=0.5), (beta=32, M_frac=1), (beta=64,  M_frac=2),
       (beta=128, M_frac=4)
  - A: (beta=4,   M_frac=0.5), (beta=8,  M_frac=1), (beta=10,  M_frac=2),
       (beta=10,  M_frac=4)
- M_frac is fraction-of-N (consistent with Anchor 3 grid). M = M_frac * N.
- Seeds: [7, 17, 23, 31, 41] (5)
- Per-cell-seed checkpoint (8 * 5 = 40 cell-seeds; key = seed int)
- Smoke at N=1024, all 8 cells, seed=17

## 6-metric battery (shared with Anchor 3 via experiments/_metric_battery.py)

1. `above_thresh_frac` -- KF-1 hallucination detection. Lower better.
2. `max_iso`           -- KF-2 edit isolation. Lower better.
3. `retention`         -- argmax retrieval accuracy. Higher better.
4. `edit_then_retrieve`-- edit-then-retrieve accuracy. Higher better.
5. `retrieval_latency_ns` -- ns per query. Lower better.
6. `kf1_sharpness`     -- max_stored_conf / mean_neg_conf. Higher better.

Single substrate setup per cell; all 6 metrics consume the same W.

## Pre-registered bands

**HARD_PASS:** Region C provides >= 2x improvement on AT LEAST 2 metrics
compared to matched Region A cell (same M_frac), in >= 3/5 seeds.
Improvement ratio computed in the "better" direction per metric.

**HARD_FAIL:** Region C is statistically indistinguishable from Region A
on ALL 6 metrics (ratio within [1/1.2, 1.2]) across ALL seeds. No
optimal-region signal.

**MIDDLE_BAND:** Region C wins on 1 metric, or shows 1.2x-2x advantage on
1-2 metrics.

## Smoke result

Wall: 8.58s. N=1024, 8 cells, seed=17. Every cell ret=1.000, hallu=0.000,
max_iso=0.000, etr=1.000 -- at smoke scale M is small enough that the
substrate is saturated-perfect on all retrieval/edit metrics. Latency
varies 98-173 us; sharpness varies 0-1258. No region-C dominance signal
at smoke (as expected: phase separation requires N=4096).

Effect size at smoke is uninformative for the HP question (smoke is
flat); the FULL run at N=4096 is where the comparison lives. Walk-back
gate: NOT triggered (smoke is not "borderline near hard-pass" -- smoke
just doesn't exercise the phase regime). FULL config keeps 5 seeds.

## Timeout estimate

- smoke_wall_s = 8.58 (CPU smoke, 8 cells x 1 seed)
- FULL_N / smoke_N = 4
- FULL_seeds / smoke_seeds = 5
- scaling_exp = 1.5 (matrix + softmax dominant)
- formula: ceil(1.5 * 8.58 * 4^1.5 * 5) = ceil(515) = 515s nominal.
- Larger M cells (M_frac=4 -> M=16384) cost more; conservative re-estimate
  ~ 2000-4000s.
- PROT-019 _n4096 floor: 14400s. User spec adopts 21600s (50% headroom
  over PROT-019 floor).
- Final: timeout_s = 21600s.

## Formula self-tests (verified at module import)

1. N == 4096 (PROT-018 binding) -- PASS
2. M @ M_frac=0.5 N=4096: 2048 -- PASS
3. M @ M_frac=4   N=4096: 16384 -- PASS
4. OOM at FULL (M=16384): ~400 MB -- under 6 GB -- PASS
5. improvement_ratio formulas: higher-better C=0.9/A=0.1 -> 9.0 -- PASS
6. improvement_ratio formulas: lower-better  C=0.01/A=0.1 -> 10.0 -- PASS
7. Verdict gates: HARD_PASS / HARD_FAIL_INDIST / MIDDLE_BAND all
   reachable -- PASS
8. 8-cell symmetry: 4 Region C + 4 Region A -- PASS

## Anchor-name binding

`_n4096` suffix -> N_FULL = 4096 enforced via module-level assertion.
queue_add.py exit-6 validator will re-verify.

## Notes

Anchor 2 of the 3-anchor phase-region characterization batch (2026-05-30).
Shares experiments/_metric_battery.py with Anchor 3 to ensure metric
comparability.
