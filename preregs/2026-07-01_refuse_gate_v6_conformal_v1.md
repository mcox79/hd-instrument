# Pre-registration: refuse_gate_v6_conformal_v1

**Filed:** 2026-07-01
**Author:** exp_dev (Opus 4.7 1M, agent-spawn)
**Anchor:** substrate_refuse_gate_v6_conformal_v1 (three siblings, seeds 7/13/19)
**Milestone:** M3 M1.4 (refuse-gate closure; USER-locked)

## Cross-reference

**Research drill (load-bearing spec):** `notes/research_drill_M1_4_refuse_gate_conformal_mechanism_class_2026-07-01.md`

The drill diagnosed v3/v4/v5 all-HARD-FAIL as **distributional non-separability under streaming-history adaptive tau** (adaptive tau converges to running-mean noisy-confidence ~0.42, coincidentally matching FIXED tau=0.40; lift=0.000 or negative). Recommended fix mechanism class: **score-based split-conformal prediction**.

## Mechanism-class contrast with prior versions

| Version | Mechanism class | tau update rule | Result |
|---|---|---|---|
| v2 (CG reference) | Fixed threshold | tau = 0.40 (locked) | CG on OOD refuse; MB on adaptivity |
| v3 (HF) | Streaming-history adaptive | sliding-window / Kalman / EWMA percentiles | Adaptive tau -> running mean -> matches FIXED coincidentally |
| v4 (HF) | 2-sided sliding tau | percentile band from history | Same: streaming history is uninformative for regime detection |
| v5 (HF) | AC-meta streaming | context-conditioned bandit | Same failure mode; noisy stream provides no differential signal |
| **v6 (this cell)** | **Score-based split-conformal** | **tau = alpha-quantile of cal-set in-KB scores; static per run** | **PREDICTED HP by drill; d'=5.1 separable** |

Core distinction: v6 decouples the **calibration problem** (how substrate scores known items) from the **query problem** (is this item known?) via a small held-out calibration set. No streaming update; no history-tracking; no attempted regime detection from noisy score stream.

## Cell design

**Arms (4; mechanism_hash distinct; META_RULE_AF):**
- `ARM_FIXED_BASELINE`: tau=0.40 (v2 CG reproducer; positive control for baseline refuse mechanics)
- `ARM_CONFORMAL_10`: tau = P10 of cal-set in-KB max_sim scores (target alpha=0.10)
- `ARM_CONFORMAL_20`: tau = P20 of cal-set in-KB max_sim scores (target alpha=0.20)
- `ARM_CONFORMAL_REGIME`: tau = P10 recomputed per-regime via noise-matched synthetic cal set

**Calibration set:** 50 items (25 in-KB + 25 OOD), sampled from same distribution as query items at moderate noise regime (exchangeability requirement). Loaded ONCE at cell startup; quantiles computed once; tau fixed for the run.

**Regimes:** 3 (clean sigma=0.00, moderate sigma=0.15, heavy sigma=0.30 flip-frac)

**Bands:** 3 (in_kb, borderline, ood)

**Phase axes:** 4 arms x 3 regimes x 3 bands = 36 phase points per seed

**Substrate scale (both smoke AND full):** N=8192, V_C_per_cat=200 (V_C_IN=600), V_REL=256, FHRR bipolar encoding, numpy CPU backend. SMOKE at full-N satisfies **DISCRIMINATOR-MUST-SURVIVE-SCALE** (Check A path per Fix #C); numpy CPU makes full-N smoke cheap.

**Seeds:** 7, 13, 19 (3-seed FULL for cross-seed CG candidacy per META_RULE)

**Query counts:**
- FULL: 60 queries per (arm, regime, band) -> 4 x 3 x 3 x 60 = 2160 records/seed
- SMOKE: 20 queries per (arm, regime, band) -> 4 x 3 x 3 x 20 = 720 records/seed

**Backend:** `numpy.cpu` (cheap; not GPU-needed)

**Route:** `remote_cpu_queue` (numpy CPU per USER SMOKE-ONLY-local discipline 2026-07-01)

## Falsifiable predictions

From research drill sec "Falsifiable Predictions" + noise-floor V_REL sweep result:

- **HP-1:** ARM_CONFORMAL_10 or ARM_CONFORMAL_20 refuse-precision >= 0.82 at moderate regime + OOD band (baseline FIXED refuse-precision ~0.6667; 0.15 lift gate is the same discriminator used in v3/v4/v5).
- **HP-2:** Cal-set quantile(in-KB) - quantile(OOD) >= 0.30. Analytical prediction: noise floor sqrt(2 ln V_C / N) = sqrt(2 ln 600 / 8192) = 0.0395; in-KB max_sim ~ N(0.80, 0.15); OOD max_sim ~ N(0.04, 0.15); d' = (0.80-0.04)/0.15 = 5.1 SEPARABLE.
- **HP-3:** Refuse spread (P50_in_kb - P50_ood) on cal set >= 0.30 (diagnostic, printed at run start).

## Verdict gates

**PRE-REG-LOCKED (in evaluation order):**

1. **HARD_FAIL_POSITIVE_CONTROL** (broken-PC-before-structural-framing gate): FIXED baseline @ clean regime + OOD band `out_kb_refuse_rate < 0.85` -> baseline refuse mechanism broken; do NOT tier v6 conformal as any structural failure. Route: fix baseline first.
2. **HARD_FAIL_REGIME_COLLAPSE**: cal-set `refuse_spread = P50_in_kb - P50_ood < 1e-6` -> would falsify d'=5.1 analytical prediction (distributions genuinely overlap at N=8192, V_C=600).
3. **HARD_FAIL_CARDINALITY_BREACH**: `expected_n_units != observed_n_units` OR `expected_n_records != observed_n_records`.
4. **HARD_FAIL_ARMS_MECH_NOT_DISTINCT** (META_RULE_AF): fewer than 4 distinct mechanism_hash values across 4 arms.
5. **HARD_FAIL_ARMS_DECISION_NOT_DISTINCT**: fewer than 4 distinct aggregated decision_hash across 4 arms (mechanisms differ but produce identical decisions -> by-construction degenerate).
6. **HARD_PASS_CONFORMAL**: any CONFORMAL arm refuse_precision >= 0.82 at (moderate, ood) -> conformal calibration-set tau separates in-KB from OOD.
7. **MIDDLE_BAND_PARTIAL_CONFORMAL**: best conformal arm refuse_precision > FIXED refuse_precision at (moderate, ood) but < 0.82 HP floor.
8. **HARD_FAIL_NO_CONFORMAL_BEAT**: no conformal arm beats FIXED at (moderate, ood) -> cal set uninformative OR distributions genuinely overlap; d'=5.1 falsified.

## CARDINALITY_OK (META_RULE_H)

- `expected_n_units = 36` (both smoke and full)
- `expected_n_records = 2160` (full), `720` (smoke)
- Recorded in `run_one_seed_conformal` result; verified against observed; `HARD_FAIL_CARDINALITY_BREACH` if mismatch.

## DISCRIMINATOR_SURVIVES_SCALE (Fix #C, Check A path)

Smoke runs at `N=8192` (same as full); no scale extrapolation risk. Justified because numpy CPU cost at N=8192 is bounded (~few minutes per seed for the small 720-record grid).

## No silent except: discipline

- No `except: pass` blocks. All exceptions in `_substrate_refuse_gate_v6_conformal_v1_core` propagate; unknown arm / unknown regime / unknown band raise `ValueError`.
- Outer main() has import-crash sentinel + `_write_minimal_metrics` writer with try/except (records the exception into metrics.json rather than swallowing).

## Smoke fires discriminator

Smoke uses same 4 arms + same 3 regimes + same 3 bands as full (36-unit grid, 720 records). All HF gates active. The HP gate on refuse_precision at (moderate, ood) fires at smoke; if smoke returns HP the discriminator survives to full dispatch.

## Substrate-KB concept-query check (USER 2026-07-01 discipline)

Ran `bash tools/substrate_query.sh "conformal prediction calibration set score based refuse gate"` (cosine 0.40 top-1) and `bash tools/substrate_query.sh "refuse gate v2 v3 v4 v5 threshold history"` (cosine 0.31 top-1).

**Prior-work check:** Prior conformal-refuse-gate work exists as research drills only (`notes/exp_dev_handoff_research_substrate_confidence_continuous_3x_2026-06-10.md`, `notes/research_drill_negative_conformal_coverage_2x_2026-06-08.md`). NO prior chain-grade v6-conformal cell exists. This cell is genuinely novel implementation of the score-based split-conformal mechanism class recommended in the load-bearing research drill (2026-07-01).

## Required fields

- `verdict`, `verdict_msg`, `elapsed_s`, `summary`
- `anchor_name`, `run_mode`, `config_version`, `ts_iso`, `pid`, `backend`, `seed`, `n_seeds`
- `observed_n_units`, `expected_n_units`, `observed_n_records`, `expected_n_records`, `cardinality_ok`
- `per_arm_summary`, `arm_mechanism_hashes`, `arm_decision_hashes`, `n_distinct_mechanism_hashes`, `n_distinct_decision_hashes`
- `positive_control_check`, `cal_moderate_diagnostic`
- `hp_refuse_precision_by_arm`, `best_conformal_arm`, `best_conformal_hp_refuse_precision`, `fixed_hp_refuse_precision`
- `n_llm_calls == 0` (substrate-only assertion in main)

## Dispatch plan

- **Smoke** (SMOKE_MODE, 720 records/seed at N=8192): 3 seeds smoke via local_cpu_queue OR direct laptop (SMOKE-ONLY-local per USER 2026-07-01) prior to full dispatch.
- **Full** (FULL_MODE, 2160 records/seed at N=8192): 3 seeds full via `remote_cpu_queue` after smoke HARD_PASS, routed by Orchestrator (cell-author cannot push).
- **Timeout:** 1800s per seed (~10x safety margin over expected wall-clock; numpy CPU at N=8192 with 2160 records completes in <120s empirically).

## Notes on baseline PC discipline

The Broken-PC-before-structural-framing gate ensures that if the FIXED baseline is broken (e.g., positive control at clean+ood refuse_rate < 0.85), we do NOT tier the v6 conformal mechanism as a failure. Failure attribution requires a working baseline. This is the same PC discipline from v3/v4/v5 pre-regs.
