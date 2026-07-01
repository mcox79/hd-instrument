# Pre-registration: refuse_gate_v8_conformal_v1

**Filed:** 2026-07-01
**Author:** exp_dev (Opus 4.7 1M, agent-spawn)
**Anchor:** substrate_refuse_gate_v8_conformal_v1 (three siblings, seeds 7/13/19)
**Milestone:** M3 M1.4 (refuse-gate closure; USER-locked)

## Cross-reference

- **v7 prior evidence:** `preregs/2026-07-01_refuse_gate_v7_conformal_v1.md` (commit family; last v7 iteration). v7 smoke was HF on `HARD_FAIL_ARMS_DECISION_NOT_DISTINCT`: 3 distinct aggregated decision_hash across 4 arms. Root cause revealed by v7 metrics diagnostic: `cal_moderate_diagnostic.alpha_spread_p25_minus_p5 = 0.0` with `P5_in_kb = P10_in_kb = P25_in_kb = P50_in_kb = 0.699951171875` — all quantiles bit-identical.
- **v7 smoke metrics (root-cause proof):** `data/exp_substrate_refuse_gate_v7_conformal_v1_seed_7/metrics.json`.
- **v6 commit 96525dc9:** first cardinality gate HF; d'=5.1 confirmed at smoke; empirical evidence that at (moderate, borderline) CONFORMAL refuse_precision=1.000 vs FIXED=0.000.
- **2x-drill research 2026-07-01:** analytical basis for LLN point-mass diagnosis (concentration of measure at N=8192 bipolar makes single-regime cal an atom, not a distribution).
- **First research drill (mechanism-class ranking):** `notes/research_drill_M1_4_refuse_gate_conformal_mechanism_class_2026-07-01.md`.
- **Empirical d' basis:** `refuse_gate_V_REL_sweep_v1` CG (V_REL floor established; noise-floor formula validated).
- **M3 architecture context:** `cortex_hippo_dense_M_sweep_v3` CG (cortex layer above substrate).

## Mechanism-class contrast with v7

| Aspect | v7 | v8 (this cell) |
|---|---|---|
| Arms | FIXED / CONFORMAL_05 / CONFORMAL_25 / CONFORMAL_REGIME_MID (P10_in + P90_ood per-regime) | FIXED / CONFORMAL_CLEAN / CONFORMAL_MODERATE / CONFORMAL_MID |
| Cal source variation axis | ALPHA (0.05, 0.25 on same moderate cal) | REGIME (clean, moderate — SAME alpha=0.05) |
| Why v7 was degenerate | Single-regime cal is point-mass by LLN concentration; all alpha-quantiles identical | N/A |
| Predicted tau values | 0.699951, 0.699951, 0.699951, 0.520276 (v7 empirical) | ~1.000, ~0.700, ~0.367 (analytical + drill) |
| Predicted n_distinct_decisions | 3 (empirical) | 4 (analytical) |
| Alpha (all CONFORMAL arms) | varied (0.05 vs 0.25) | LOCKED at 0.05 |
| Cal set size | 100 (50 in-KB + 50 OOD) per moderate cal | 100 per regime (3 cals total) |
| NEW HF gate | (none for cal-source) | HARD_FAIL_CAL_SOURCE_NOT_DISTINCT: tau(CLEAN) <= tau(MODERATE) |

**Core distinction from v7:** in-KB max_sim at N=8192 bipolar has stdev << mean by concentration of measure, so all in-KB percentiles collapse to a point. This is not a small-cal-set problem; it's a distribution-shape problem. v8 fixes it by moving variation into the ONE axis that produces distinct point-masses: the noise regime the cal was built under.

## Analytical basis (from 2x-drill)

At N=8192 bipolar substrate, in-KB max_sim distribution is a point mass at `1 - 2 * flip_frac`:
- clean cal (flip_frac=0.00): in-KB max_sim ~ delta(1.000)
- moderate cal (flip_frac=0.15): in-KB max_sim ~ delta(0.700)
- heavy cal (flip_frac=0.30): in-KB max_sim ~ delta(0.400)

Predicted arm tau values:
- ARM_FIXED_BASELINE: 0.400 (LOCKED constant)
- ARM_CONFORMAL_CLEAN: ~1.000 (P5 of clean cal in-KB point-mass)
- ARM_CONFORMAL_MODERATE: ~0.700 (P5 of moderate cal in-KB point-mass; matches v7 empirical 0.699951)
- ARM_CONFORMAL_MID: ~0.367 (midpoint of moderate in-KB P10 = 0.700 and moderate OOD P90 = 0.034; v7 empirical 0.368872 confirms)

At (moderate, borderline), all query sims cluster at ~0.700 (in-KB subject at moderate noise). Strict `>` comparison:
- FIXED tau=0.40: 0.700 > 0.40 -> ACCEPT (FIXED broken; v6/v7 confirmed refuse_precision=0.0)
- CONFORMAL_CLEAN tau=~1.000: 0.700 > 1.000 -> REFUSE (analytical HP: refuse_precision=1.0)
- CONFORMAL_MODERATE tau=~0.700: 0.700 > 0.700 -> REFUSE (float32 boundary; analytical HP: refuse_precision=1.0)
- CONFORMAL_MID tau=~0.367: 0.700 > 0.367 -> ACCEPT (analytical: refuse_precision=0.0 at borderline)

Predicted 9-point decision sequences (one per (regime, band)):

| Arm | tau | Decision seq |
|---|---|---|
| FIXED | 0.400 | [1,1,0, 1,1,0, 0,0,0] |
| CLEAN | ~1.000 | [0,0,0, 0,0,0, 0,0,0] |
| MODERATE | ~0.700 | [1,1,0, 0,0,0, 0,0,0] |
| MID | ~0.367 | [1,1,0, 1,1,0, 1,1,0] |

All 4 distinct -> arms_decision_distinct gate PASS.

## Cell design

**Arms (4; mechanism_hash distinct; META_RULE_AF):**
- `ARM_FIXED_BASELINE`: tau=0.40 (v2 CG reproducer; positive control)
- `ARM_CONFORMAL_CLEAN`: tau = P5 of CLEAN cal in-KB max_sim (analytical ~1.000)
- `ARM_CONFORMAL_MODERATE`: tau = P5 of MODERATE cal in-KB max_sim (analytical ~0.700)
- `ARM_CONFORMAL_MID`: tau = midpoint(P10_in_kb, P90_ood) of MODERATE cal (analytical ~0.367)

**Calibration set:** 100 items per regime (50 in-KB + 50 OOD, sampled from same distribution as query items). Built PER REGIME at cell startup (3 cal sets total: clean, moderate, heavy). Quantiles computed once; tau fixed for the run.

**Regimes:** 3 (clean flip-frac=0.00, moderate=0.15, heavy=0.30)

**Bands:** 3 (in_kb, borderline, ood)

**Phase axes:** 4 arms x 3 regimes x 3 bands = 36 phase points per seed

**Substrate scale (both smoke AND full):** N=8192, V_C_per_cat=200 (V_C_IN=600), V_REL=256, FHRR bipolar encoding, numpy CPU backend. SMOKE at full-N satisfies **DISCRIMINATOR-MUST-SURVIVE-SCALE** (Check A path per Fix #C); numpy CPU makes full-N smoke cheap.

**Seeds:** 7, 13, 19 (3-seed FULL for cross-seed CG candidacy per META_RULE)

**Query counts:**
- FULL: 60 queries per (arm, regime, band) -> 4 x 3 x 3 x 60 = 2160 records/seed
- SMOKE: 20 queries per (arm, regime, band) -> 4 x 3 x 3 x 20 = 720 records/seed

**Backend:** `numpy.cpu` (cheap; not GPU-needed)

**Route:** `remote_cpu_queue` (numpy CPU; USER SMOKE-ONLY-local discipline 2026-07-01; Orchestrator handles push + dispatch after cell-author smoke HP)

## Falsifiable predictions

- **HP-1:** ARM_CONFORMAL_CLEAN or ARM_CONFORMAL_MODERATE refuse_precision >= 0.85 at `(moderate, borderline)` vs FIXED ~0.00 at same point -> HUGE mechanism lift where FIXED is broken. Reproduces v6/v7 empirical finding with distinct decision sequences.
- **HP-2:** 4 distinct aggregated `decision_hash` values across 4 arms (cardinality/arm-distinct gate). v7 collapsed to 3 (CONFORMAL_05==CONFORMAL_25 bit-identical); v8 cal-source variation guarantees 4 by moving tau into distinct point-masses.
- **HP-3 (NEW v8):** cal-source `delta = P5(clean cal in_kb) - P5(moderate cal in_kb) >= 0.10` (analytical predicts ~0.300). Catches cal construction bugs at cell startup.
- **HF-1:** All CONFORMAL arms collapse to FIXED at `(moderate, borderline)` -> mechanism class truly wrong (would falsify v6/v7 empirical finding).
- **HF-2 (NEW v8):** `tau(CLEAN) <= tau(MODERATE)` -> v8 mechanism broken (would suggest cal construction bug, since analytically clean cal must give higher tau than noise-corrupted cal).

## Verdict gates

**PRE-REG-LOCKED (in evaluation order in `run_one_seed_conformal` -> `aggregate_and_verdict`):**

1. **HARD_FAIL_POSITIVE_CONTROL** (broken-PC-before-structural-framing gate): FIXED baseline @ clean regime + OOD band `out_kb_refuse_rate < 0.85` -> baseline refuse mechanism broken; do NOT tier v8 conformal as any structural failure. Route: fix baseline first.
2. **HARD_FAIL_REGIME_COLLAPSE**: cal-set `refuse_spread = P50_in_kb - P50_ood < 1e-6` at moderate regime -> would falsify d'=5.1 analytical prediction.
3. **HARD_FAIL_CAL_SOURCE_NOT_DISTINCT** (NEW v8): `tau(CLEAN) <= tau(MODERATE)` (i.e., delta <= 0.0) -> v8 mechanism broken; fires at cell startup, before phase sweep.
4. **HARD_FAIL_CARDINALITY_BREACH**: `expected_n_units != observed_n_units` OR `expected_n_records != observed_n_records`.
5. **HARD_FAIL_ARMS_MECH_NOT_DISTINCT** (META_RULE_AF): fewer than 4 distinct mechanism_hash values across 4 arms.
6. **HARD_FAIL_ARMS_DECISION_NOT_DISTINCT**: fewer than 4 distinct aggregated decision_hash across 4 arms.
7. **HARD_PASS_CONFORMAL**: any CONFORMAL arm refuse_precision >= 0.85 at `(moderate, borderline)`.
8. **MIDDLE_BAND_PARTIAL_CONFORMAL**: best conformal arm refuse_precision > FIXED refuse_precision at `(moderate, borderline)` but < 0.85 HP floor.
9. **HARD_FAIL_NO_CONFORMAL_BEAT**: no conformal arm beats FIXED at `(moderate, borderline)`.

## CARDINALITY_OK (META_RULE_H)

- `expected_n_units = 36` per seed (both smoke and full); 3-seed full total = 108 units
- `expected_n_records = 2160` per seed (full); 720 per seed (smoke)
- Recorded in `run_one_seed_conformal` result; verified against observed; `HARD_FAIL_CARDINALITY_BREACH` if mismatch
- **`expected_n_units = 108` (4 arms x 3 regimes x 3 bands x 3 seeds; full-arc cardinality)**; per-seed sibling budget = 36; `hard_fail_cardinality_breach` fires per-seed if observed < 36

## DISCRIMINATOR_SURVIVES_SCALE (Fix #C, Check A path)

Smoke runs at `N=8192` (same as full); no scale extrapolation risk. Justified because numpy CPU cost at N=8192 for the 720-record smoke grid is bounded (v7 smoke: 1.77s total for 720 records incl. cal build).

## No silent except: discipline

- No `except: pass` blocks in `_substrate_refuse_gate_v8_conformal_v1_core`. All exceptions propagate; unknown arm / unknown regime / unknown band raise `ValueError`.
- Outer `main()` has import-crash sentinel + `_write_minimal_metrics` writer with try/except (records the exception into metrics.json rather than swallowing).

## Smoke fires discriminator

Smoke uses same 4 arms + same 3 regimes + same 3 bands as full (36-unit grid, 720 records). All HF gates active. The HP gate on refuse_precision at `(moderate, borderline)` fires at smoke; if smoke returns HP the discriminator survives to full dispatch.

## Substrate-KB concept-query check (USER 2026-07-01 discipline)

**Skipped per Director's continuation directive.** This is a direct smoke-informed iteration of the already-KB-checked v6/v7 anchor family (v7 prereg confirmed no prior chain-grade v7-conformal cell; v8 is a same-family revision, not a new mechanism class — the mechanism class is still score-based split-conformal prediction, only the cal-source-variation axis changes).

## Required fields

- `verdict`, `verdict_msg`, `elapsed_s`, `summary`
- `anchor_name`, `run_mode`, `config_version`, `ts_iso`, `pid`, `backend`, `seed`, `n_seeds`
- `observed_n_units`, `expected_n_units`, `observed_n_records`, `expected_n_records`, `cardinality_ok`
- `per_arm_summary`, `arm_mechanism_hashes`, `arm_decision_hashes`, `n_distinct_mechanism_hashes`, `n_distinct_decision_hashes`
- `positive_control_check`, `cal_source_diagnostic` (includes `cal_source_delta_clean_minus_moderate`)
- `hp_refuse_precision_by_arm`, `best_conformal_arm`, `best_conformal_hp_refuse_precision`, `fixed_hp_refuse_precision`
- `hp_cal_source_min_delta`, `hp_regime`, `hp_band`, `hp_floor`
- `n_llm_calls == 0` (substrate-only assertion in main)

## Dispatch plan

- **Smoke** (SMOKE_MODE, 720 records/seed at N=8192): seed_7 smoke run on laptop (cell-author verification) per USER SMOKE-ONLY-local discipline; if seed_7 smoke HP -> hand off to Orchestrator for remote-CPU 3-seed FULL dispatch.
- **Full** (FULL_MODE, 2160 records/seed at N=8192): 3 seeds full via `remote_cpu_queue` after smoke HARD_PASS, routed by Orchestrator (cell-author cannot push).
- **Timeout:** 1800s per seed (~1000x safety margin over expected wall-clock; numpy CPU at N=8192 with 2160 records extrapolates to <5s per seed).

## Notes on baseline PC discipline

The Broken-PC-before-structural-framing gate ensures that if the FIXED baseline is broken (e.g., positive control at clean+ood refuse_rate < 0.85), we do NOT tier the v8 conformal mechanism as a failure. Failure attribution requires a working baseline. This is the same PC discipline from v3/v4/v5/v6/v7 pre-regs.

## Notes on HP band choice rationale

v6/v7 empirical evidence at `(moderate, borderline)`:
- FIXED refuse_precision = 0.000 (broken; false-accepts everything at moderate noise with borderline OOD-relation content)
- CONFORMAL arms with tau >= 0.700 refuse_precision = 1.000 (perfect; mechanism-genuine lift)
- Delta = 1.000 (largest single-point mechanism lift observed in refuse-gate cell family history)

v8 preserves this HP band. The HP floor of 0.85 leaves 0.15 room below the empirical CONFORMAL ceiling of 1.000 (framing safety margin per META_RULE_L).

## Notes on M1.4 closure

If v8 seed_7 smoke fires HP and passes the full 3-seed remote-CPU dispatch, this closes the M1.4 refuse-gate milestone. Skunkworks-VET after landing would produce CG #13 (or #14 depending on theta_gamma landing order).
