# Pre-reg: edge_importance_stratified_replay_baseline_diagnostic_v2_proper_import_guard

**Date:** 2026-06-27
**Cell author:** exp_dev
**Anchor:** `edge_importance_stratified_replay_baseline_diagnostic_v2_proper_import_guard`
**Script:** `experiments/exp_edge_importance_stratified_replay_baseline_diagnostic_v2_proper_import_guard.py`
**Drill provenance:** `notes/research_drill_stratified_replay_HARD_FAIL_3x_2026-06-27.md`
**Lineage:** v1 (HARD_FAIL cardinality breach via v3 import-time side effect, 2026-06-27 07:04) -> v2_proper_import_guard (this cell; ROOT CAUSE fix)

## ROOT CAUSE FIX (Path A + Path B)

v1 failed because `exp_edge_importance_retrieval_trace_x_ultrametric_coreness_v3.py` had its full 6-arm main driver at MODULE SCOPE (no `if __name__ == "__main__":` guard). v1's `from ...v3 import setup_substrate_with_trace_and_clusters` triggered v3's full main loop at IMPORT TIME. Under the runner-set `HDLAB_EXP_NAME=v1_anchor` env, v3's main wrote 6 ARM partials (BASELINE_RANDOM_IMPORTANCE / TRACE_ONLY / ULTRAMETRIC_ONLY / 3x TRACE_X_CORENESS) into v1's output dir. v1's aggregator loaded the alien partials, breached META_RULE_H (got 6 vs expected 4), and HARD_FAIL'd in 2 ms total wall.

**Two fixes shipped in same commit before this cell ran:**

1. **Path A (load-bearing):** Wrap main drivers in `if __name__ == "__main__":` across ALL 11 `edge_importance_*` family cells:
   - `exp_edge_importance_retrieval_trace_x_ultrametric_coreness_v3.py` (PRIMARY)
   - `exp_edge_importance_retrieval_trace_x_ultrametric_coreness_v3p1_ULTRA_tuned.py`
   - `exp_edge_importance_v3p2_trace_only_with_D1_audit_v1.py`
   - `exp_edge_importance_v3p2_trace_only_with_D1_audit_v2_arm_count_fix.py`
   - `exp_edge_importance_v4_NREM_replay_modulated_trace.py`
   - `exp_edge_importance_v5_CFU_counterfactual_utility_v1.py`
   - `exp_edge_importance_v6_CFU_stronger_regime.py`
   - `exp_edge_importance_stratified_replay_baseline_diagnostic_v1.py`
   - `exp_edge_importance_stratified_replay_baseline_diagnostic_v2_arm_count_fix.py`
   - `exp_edge_importance_bound_pair_consolidation_v1.py`
   - `exp_edge_importance_bound_pair_consolidation_v2.py`
   - `exp_edge_importance_v3_D1_alternative_discriminators_v1.py`

2. **Path B (defense-in-depth):** `_seed_checkpoint._check_run_config` extended with new `run_config["anchor"]` key. When set, partials whose `body["config_version"]` ANCHOR= field mismatches (or `body["anchor_name"]` field mismatches) are REJECTED at PARTIAL-LOAD time, before any cardinality check fires. Self-test extended to 8 tests covering ANCHOR rejection via both `config_version` regex and `anchor_name` field; all 8 pass.

This v2_proper cell:
- Is a near-verbatim CLONE of v1 (same arms, same bands, same mechanism)
- Re-imports `setup_substrate_with_trace_and_clusters` from v3 (now SAFE per Path A)
- Passes `run_config["anchor"]=ANCHOR_NAME` (engages Path B at every partial load)
- Adds startup deviation-log scan: emits visibility line for any pre-existing alien partials
- Adds `_selftest_v3_import_is_side_effect_free()` at instrumentation time: scans out_dir before run_seed, halts if any pre-existing partial has mismatched ANCHOR
- Adds `META_RULE_H_NAMESET` sibling at verdict: `set(observed.arm_name) == DECLARED_ARM_NAMESET` (catches right-count-wrong-names case)
- Stamps `anchor_name` field in every per-seed partial for verdict-layer ANCHOR check

## Mechanism (unchanged from v1)

`STRATIFIED_REPLAY` -- bin atoms by |W|-decile (10 bins); sample equal replay-count per bin proportional to within-bin retrieval_trace_score; importance = stratified replay-event count.

Drill ANGLE 1 hypothesis (Cauchy-Schwarz): any sampling-count signal over substrate retrieval correlates with |W| because `<query, W_i>` is approximately proportional to `||W_i||` for uniformly-random queries. Stratified sampling by |W|-quantile should BREAK that correlation if the math holds.

## ARMS (4 mandatory; same as v1)

| Arm | Mechanism |
|---|---|
| `ARM_RAND_IMPORTANCE` | Random importance baseline (control rail) |
| `ARM_TRACE_ONLY` | v3.2 lineage; raw retrieval_trace_count (reproduce drill's cor=0.83 claim) |
| `ARM_STRATIFIED_REPLAY` | THE diagnostic; bin by |W|-decile, count replays per bin |
| `ARM_INVERSE_WEIGHTED_REPLAY` | Liu IS: count / ||a||^2 |

## CARDINALITY (META_RULE_H + NAMESET sibling)

- `EXPECTED_N_UNITS = len(SEEDS) * len(ARM_NAMES) = 3 * 4 = 12` (full); `1 * 4 = 4` (smoke)
- Per-seed: `len(arms) == 4` AND `set(arm_name) == DECLARED_ARM_NAMESET`
- HARD_FAIL on ANY breach (count OR nameset OR anchor mismatch)

## PRE-REG BANDS (LOCKED)

| Band | Condition |
|---|---|
| `DIAGNOSTIC_PASS_A` | `cor(STRATIFIED_REPLAY, |W|) < 0.30` (proves math holds) |
| `DIAGNOSTIC_PASS_B` | `cor(INVERSE_WEIGHTED, |W|) < 0.30` (Liu IS valid in HD) |
| `REPRODUCE_V4_TRACE_BIAS` | `cor(TRACE_ONLY, |W|) >= 0.70` (Cauchy-Schwarz prediction) |
| `HARD_PASS` | `(DIAGNOSTIC_PASS_A OR DIAGNOSTIC_PASS_B)` AND `REPRODUCE_V4_TRACE_BIAS` AND mechanism fires |
| `MIDDLE_BAND` | TRACE bias reproduced but neither STRATIFIED nor INVERSE clears 0.30 gate |
| `HARD_FAIL` | TRACE cor < 0.30 (SURPRISE_NEGATIVE) OR cardinality breach OR NAMESET breach OR ANCHOR breach OR caught exception |

**Smoke bias floor:** 0.50 (smoke trace correlates less; full-N predicted >= 0.70).

## DRILL PREDICTION (lit-scan calibration-deflated)

Most likely outcome: **MIDDLE_BAND** (`cor(STRATIFIED, |W|) in [0.30, 0.50]`). Stratification damps but does not break the bias because within-bin proposal-weighting by trace re-introduces |W| coupling. Drill's mathematical decomposition:

- `Var(||W||) = Var_between + Var_within` (10 bins; between ~89%, within ~11%)
- Stratification zeroes `Cov_between`; only `Cov_within` remains
- Predicted: `cor ≈ sqrt(0.008/0.075) × cor_within_trace ≈ 0.33 × 0.7 ≈ 0.23`

Honest expectation distribution:
- HARD_PASS: P ≈ 0.25-0.30
- MIDDLE_BAND: P ≈ 0.55
- HARD_FAIL surprise-negative: P ≈ 0.15

**Diagnostic value either way:** answers whether fairness violation is sampling-bias artifact (fixable via Liu IS / stratification) or deeper substrate property (requires v5 M-CFU counterfactual-utility per Mattar-Daw brain-replay literature).

## DISCIPLINES

- `META_RULE_H` cardinality_ok: per-seed expected arm count = 4
- `META_RULE_H_NAMESET` (NEW): observed arm-name set must equal declared
- `META_RULE_H_ANCHOR` (NEW; in `_seed_checkpoint`): partials with mismatched ANCHOR REJECTED at load
- `META_RULE_J` no-silent-except: setup + each arm wrapped in try/except + traceback
- `META_RULE_K` smoke fires discriminator: smoke must reproduce TRACE-bias (cor >= 0.5 at smoke)
- `META_RULE_L` band-floor strictly-above-floor
- `RULE_EXPERIMENT_CELLS_MUST_GUARD_MAIN_WITH___NAME___DUNDER` (NEW): all edge_importance_* family cells now guarded

## CONFIG

- N = 512, M_OLD = 600, M_RECENT = 400, M_TOTAL = 1000, alpha = 1.953 (HIGH-alpha discriminator regime per v3/v4 lineage)
- SEEDS: full = [7, 17, 23]; smoke = [7]
- N_BINS_STRATIFIED = 10, K_PER_BIN = 8, TOTAL_REPLAY_EVENTS = 80
- DIAGNOSTIC_COR_GATE = 0.30
- REPRODUCE_TRACE_BIAS_FLOOR: full = 0.70, smoke = 0.50

## DISPATCH

- PROT-020: numpy-only -> `remote_cpu_queue` (NOT gpu)
- Smoke wall (estimated): ~5-8 s (one seed, full-N substrate setup ~5 s + 4 arms ~0.5 s each)
- Full wall (estimated): ~20-30 s (3 seeds x ~7 s each)
- Per-experiment `--timeout` = 600 s (10x headroom for safety per dispatch-discipline)

## TIMEOUT JUSTIFICATION

Substrate setup ~5 s per seed; 4 arms ~0.5 s each; aggregation ~1 s. Total per seed ~8 s. 3 seeds * 8 s = 24 s expected. 600 s timeout = 25x headroom (matches v1's tier; covers any GC pauses on shared CPU).

## REQUIRED_FIELDS (top-level metrics.json)

- `verdict`, `verdict_msg`, `elapsed_s`, `summary` (runner-enforced)
- `anchor_name` (== `edge_importance_stratified_replay_baseline_diagnostic_v2_proper_import_guard`)
- `config_version`, `N`, `M_OLD`, `M_RECENT`, `alpha`, `n_seeds`, `run_mode`
- `n_bins_stratified`, `k_per_bin`, `total_replay_events`, `diagnostic_cor_gate`
- `expected_arm_nameset`, `v2_proper_import_guard` = True
- `per_seed`: list of `{seed, anchor_name, elapsed_s, trace_total, n_retrieved, n_unretrieved, arms}`
- Each arm: `{arm_name, cor_importance_magnitude, importance_min/max/mean, n_nonzero_atoms, atom_norms_min/max/mean, wall_s}`

ASCII-only. No emojis. No em-dashes.
