# PRE-REG: SVAMP-A WK-pair prior weight sweep -- exp_svamp_wk_pair_prior_v1

**Date:** 2026-06-22
**Author:** exp_dev
**Cell:** experiments/exp_svamp_wk_pair_prior_v1.py
**Anchor:** svamp_wk_pair_prior_v1
**Queue:** local_cpu_queue
**Wall estimate (full):** ~30 min (15 arms x ~2 min)

## Routing
Candidate A from `notes/research_svamp_mechanism_redesign_2x_drill_2026-06-22.md` (Research, 2x drill).
Diagnosis: prior cell `exp_svamp_math_wk_lex_cpu_v1` HARD_FAILed at acc_wk=0.3633 because the trained selector
ANTI-PREFERS WK-constant pairs (training labels are in-text-pair-dominated; WK pairs are never gold in the 580-item
train split). Fix: at INFERENCE time, add a fixed positive bias to selector score for any candidate pair containing
a WK constant. P(HARD_PASS), deflated by Research: 0.42.

## Configuration (CONFIG_VERSION)
- `WK_PRIOR_WEIGHTS = [0.0, 0.5, 1.0, 2.0, 3.0]` (5 arms; 0.0 is the discriminating control)
- `SEEDS = [1011, 1012, 1013]` (3 seeds, matching prior SVAMP cell)
- `N_TEST_FULL = 300` (SVAMP real test split; `corpus_provenance_real=True`)
- 580-item train, 300-item test
- 15 sub-runs total

## Pre-registered hard bands
- **HARD_PASS:** `max(mean acc_wk over weight sweep) >= 0.40` AND `(acc_intext_only at best weight) >= (acc_intext_only at w=0.0) - 0.02` (cost-of-bias side-check)
- **MIDDLE_BAND:** `max(mean acc_wk) in [0.38, 0.40)`, OR hit the 0.40 bar but in-text-only drop > 0.02
- **HARD_FAIL:** `max(mean acc_wk) < 0.38` across all 5 weights -> route Candidate D (joint pair+op training) per Research 2x drill
- **DISCRIMINATING CONTROL (required):** weight=0.0 arm at seed=1011 MUST reproduce `acc_wk=0.3633 +/- 0.002`. Failure -> verdict UNKNOWN (sweep instrumentation is not faithfully isolating the prior).

## Instrumentation (per_unit per weight x seed)
- `acc_wk` (overall test accuracy)
- `acc_intext_only` (acc on the 74.3% of test items solvable from in-text numbers alone)
- `acc_wk_required` (acc on the complement: items needing a WK constant)
- `selector_pair_acc`
- `n_wk_candidates_entering` (sum over test items of WK candidates in pool)
- `n_wk_candidates_selected` (count of test items where chosen pair includes a WK constant)
- `n_intext_only`, `n_wk_required`, `n_test_effective`, `n_train_labels`
- `wall_s`, `wk_prior_weight`, `seed`

## Honest surprises from smoke gate
- Smoke passes structurally (AST, selftest, 15 arms run, instrumentation populates).
- Discriminating control FAILS in smoke as expected (smoke=4 epochs/200 train/80 test; the 0.3633 reference requires 10 epochs/580 train/300 test). Will verify on full mode.
- Smoke shows `n_wk_candidates_selected` rises monotonically with weight (4 -> 15 across w=0 to w=3.0), confirming the prior IS firing.
- Smoke shows `acc_wk_required=0.0` for ALL arms (smoke n_wk_required=22; weight pushes selector to WK pairs but the OP-classifier / value-match still fails on those items). If this persists in full mode, Research's caveat (D1: "WK constant is right but operand noun is wrong / two-group sums") may dominate.

## Discriminating-regime CAN-fail signals
1. Pool pollution: lexical WK trigger fires on irrelevant nouns (e.g. "3 dog collars" -> legs_per_dog=4 enters).
2. Two-group structural limitation: "2 dogs, 3 cats, how many legs?" needs two WK-multiplied pairs summed; current pipeline picks one pair.
3. 25.7% WK-required item fraction may be insufficient to move the overall bar even if all WK items are corrected.

## Reply pointers
- Cell source: `experiments/exp_svamp_wk_pair_prior_v1.py`
- Metrics: `data/svamp_wk_pair_prior_v1/metrics.json` (post-run)
- Prereg: this file
