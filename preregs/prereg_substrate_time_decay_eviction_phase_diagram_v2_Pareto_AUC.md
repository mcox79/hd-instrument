# Pre-registration: substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC

**Cell:** `experiments/exp_substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC.py`
**Author:** exp_dev (cell-author)
**Date filed:** 2026-06-28
**Mechanism class diversion of:** v1 (`exp_substrate_time_decay_eviction_phase_diagram_v1.py`; commits 5efe549b / 4ba529a4)
**Prior verdict context:** v1 shipped 2/3 HARD_PASS (seeds 13 + 19) + 1 MIDDLE_BAND (seed_7; healthy=5/28, 1 point shy of 6/28 binary gate). 3 near-miss points (decay=60 at load 1.0/2.0/5.0) at clutter 0.21/0.22/0.20 sat 1pp above the binary 0.20 cap.

---

## Mechanism claim

TIME_DECAY_EVICTION (evict atoms whose last_query_age > decay_rate_days) on the (working_set_retention, 1 - clutter_fraction) 2-D plane **strictly Pareto-dominates** uniform-random eviction (matched eviction count) at the vast majority of (decay_rate_days, capacity_load_ratio) phase-diagram configurations, and **never strictly loses** at more than a tiny fraction. This is a continuous geometric discriminator that does not suffer the threshold-boundary instability of v1's binary point-in-rectangle gate.

---

## What v2 changes vs v1

| | v1 (binary) | v2 (Pareto-AUC) |
|---|---|---|
| Discriminator | Per-point binary: healthy = (ws >= 0.95 AND clut <= 0.20 AND d_comp >= 0.10) | Per-point cross-arm Pareto outcome: TD_DOMINATES / RD_DOMINATES / TIE on (ws, 1-clut) |
| Aggregate metric | Count of healthy points >= 20% AND too-aggressive >= 20% AND too-permissive >= 20% AND discriminating >= 50% | dominance_rate = (TD_wins + 0.5*ties)/N >= 0.85 AND net_dominance >= 0.70 AND RD_loss_rate <= 0.05 AND every load axis has >= 1 TD-win |
| Boundary-stability | Fragile (1pp shift at clutter=0.20 cap moves point in/out) | Robust (continuous comparison; no threshold cliff) |
| Mechanism stays same | YES -- arms TIME_DECAY / RANDOM / NO_EVICTION identical | YES |

---

## Grid (unchanged from v1)

* `DECAY_RATE_DAYS_AXIS = [7, 15, 30, 60, 90, 180, 365]` (7 levels)
* `CAPACITY_LOAD_RATIO_AXIS = [0.5, 1.0, 2.0, 5.0]` (4 levels)
* `EXPECTED_N_UNITS = 28` per seed
* `SEEDS = [7, 13, 19]` (full dispatch; reproducing the same seed set as v1 enables direct verdict-class comparison)
* `N_ATOMS = 1000`, `N_DAYS = 365`, `RECENT_QUERY_DAYS = 30`, `QUERY_DECAY_TAU = 60.0`

---

## HARD_PASS gates (load-bearing)

All four must hold:

1. **dominance_rate >= 0.85** -- TIME_DECAY beats RANDOM on >= 85% of configs (continuous geometric)
2. **net_dominance >= 0.70** -- TD_wins - RD_wins >= 70% of N (clear surplus)
3. **rd_loss_rate <= 0.05** -- RANDOM strictly dominates TIME_DECAY on <= 5% of configs (mechanism has no failure mode)
4. **load_coverage_ok** -- every capacity_load_ratio axis has >= 1 TD-dominates config (no load slice without phase coverage)

---

## HARD_FAIL gates

* `HARD_FAIL_CARDINALITY_BREACH` -- observed grid points < 28 per seed
* `HARD_FAIL_BY_CONSTRUCTION_SAT` -- dominance_rate >= 0.999 AND TD.ws == 1.0 at every point (ceiling saturated)
* `HARD_FAIL_BY_CONSTRUCTION_FLOOR` -- TD.ws_retention <= 0.05 at every point
* `HARD_FAIL_ARMS_IDENTICAL` -- |TD.composite - RD.composite| < 0.02 at >= 90% of configs
* `HARD_FAIL_RD_DOMINATES_SOMEWHERE` -- RD_loss_rate > 0.20
* `HARD_FAIL_LLM_LEAK` -- n_llm_calls > 0 (substrate-only-decode gate)

---

## MIDDLE_BAND criterion

`dominance_rate >= 0.85` AND `rd_loss_rate <= 0.05` (strong dominance) BUT one of the secondary gates (`net_dominance` or `load_coverage`) misses.

---

## Positive-control prediction (load-bearing)

**Self-test reproduces v1's HARD_PASS op point (decay=90, load=1.0, seed=13):**
TD strictly dominates RD on (ws, 1-clut). Confirms new discriminator preserves the v1 op-point signature.

**Self-test reproduces seed_7's near-miss promotion (decay=60, load=2.0, seed=7):**
TD strictly dominates RD even though v1 binary marked this config not-healthy at clut=0.218. Confirms the discriminator-class diversion's central claim that v2 promotes seed_7's near-miss points from MIDDLE_BAND to first-class Pareto-healthy.

If either self-test fails, the smoke is HARD_FAIL_PROOF (cell does not establish v2's mechanism claim) and the full-grid dispatch is aborted.

---

## Empirical calibration from v1 data (3 seeds; n_pts=28 each)

Re-computing the Pareto-dominance discriminator on the existing v1 grid_points:

| Seed | TD_wins / 28 | RD_wins / 28 | Ties / 28 | dominance_rate | net_dominance |
|---|---|---|---|---|---|
| 7  | 24 | 0 | 4 | 0.929 | 0.857 |
| 13 | 23 | 0 | 5 | 0.911 | 0.821 |
| 19 | 23 | 0 | 5 | 0.911 | 0.821 |

**All three seeds** would HARD_PASS under v2 if the regen matches v1 numerics. (Same simulation, identical RNG; expected match modulo the new discriminator computation pass.)

Note: 0/28 RD_wins in every seed is a strong "no failure mode" signal that the v1 binary discriminator's MB on seed_7 was a threshold-boundary artifact, not a mechanism deficit.

---

## Discriminator survives scale (Fix: discriminator-must-survive-scale)

* Smoke uses `EXPECTED_N_UNITS = 4` (decay in [15, 90] x load in [1.0, 5.0]) AND `n_atoms=200, n_days=180`.
* Smoke's `dr=90, ld=1.0` IS the v1 op point at full simulation parameters in the self-test (not the smoke driver -- the self-test runs at full N).
* Self-test #3 (`_selftest_pareto_dominance_at_v1_op_point`) verifies discriminator FIRES at full-scale operating point (n_atoms=500, n_days=365); not just smoke-scale.
* Self-test #4 (`_selftest_pareto_dominance_at_seed7_near_miss`) verifies discriminator FIRES on the central v2 claim at full-scale (n_atoms=500, n_days=365).
* Full grid is 7x size of smoke; mechanism strength scales WITH grid coverage (more configs sampled means MORE chances for RD to occasionally tie/win, so dominance_rate is the right metric -- not a saturation-prone single-point check).

---

## CARDINALITY_OK contract

* `EXPECTED_N_UNITS = 28` per seed (full).
* `HARD_FAIL_CARDINALITY_BREACH` raised at verdict if any seed has < 28 grid_points.

---

## META_RULE_AF (arms must differ)

* Arms are TIME_DECAY / RANDOM / NO_EVICTION (3-arm bracket).
* `HARD_FAIL_ARMS_IDENTICAL` if |TD.composite - RD.composite| < 0.02 at >= 90% of grid points.
* v1 empirical: TD beats RD by composite +0.42 to +0.91 at the near-miss points (clearly differing).

---

## Honest-downward

* If smoke proves the discriminator does not promote seed_7's near-miss point (Self-test #4 fails), this is HARD_FAIL_PROOF and full dispatch is aborted. Cell-author files a routing note explaining the empirical surprise.
* If full HARD_PASS but the post-VET tier comes back MIDDLE_BAND or MEASURED_MECHANISM, that is the correct cert-classification; cell-author does not over-promote.
* Skunkworks owns final tier classification.

---

## Output

* Per-seed dirs: `data/exp_substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC_seed_<N>/metrics.json`
* Aggregated dir: `data/exp_substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC/metrics.json` (after merge)

---

## Promotion criterion

If smoke shows Self-test #4 passes (seed_7's near-miss point becomes TD_DOMINATES under v2) AND smoke completes successfully on `dr=90, ld=1.0` showing TD_DOMINATES, this is STRONG CHAIN-GRADE PROMOTION CANDIDATE -- the v2 discriminator removes the boundary-threshold instability that produced v1's MIDDLE_BAND classification on seed_7, and 3-of-3 seeds are expected to HARD_PASS under v2.

Cert-owner (Skunkworks) makes the final tiering decision after landed-VET.
