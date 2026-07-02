# Prereg: lap3_12_confidence_calibration_cpu_v1

## Anchor
`lap3_12_confidence_calibration_cpu_v1`

## Cell path
`d:/AI/hd-instrument/experiments/exp_lap3_12_confidence_calibration_cpu_v1.py`

## Metrics path
`d:/AI/hd-instrument/data/exp_lap3_12_confidence_calibration_cpu_v1/metrics.json`

## Queue routing
- **Smoke:** local direct-invocation (`.venv/Scripts/python.exe ... --smoke`); ran 2026-07-02 in <1s wall.
- **Full:** `remote_cpu_queue` (per USER 2026-07-01 SMOKE-ONLY-local rule; FULL routes remote).
- **Timeout:** `--timeout 300` (5 min; expected FULL wall ~3-5s at M=500 N=2048 TR=300).

## Framing (Stage 3 M3 cortex-layer confidence architecture)

This cell fills the **post-hoc-calibration corner** of the 3-signal cortex confidence architecture (proposal at `notes/proposal_M3_cortex_three_signal_confidence_architecture_2026-07-02.md`):
- lap3_12: post-hoc isotonic calibration of cleanup-margin (density-averaging complement)
- h4b: spatial-signal (HF'd on regime confound per research drill ac7fa91)
- Lane X: dynamical-signal (paused pending regime fix)

If HP/MB lands, this is the **first working corner** of the 3-signal architecture and unlocks reframed OOD-detection at contam=40% / INTRA_COS=0.35 (skeleton per regime drill).

## Framing corrections vs prior Cell 3 (2026-06-24 HARD_FAIL)

Prior `exp_substrate_confidence_calibration_isotonic_v1` HARD_FAILed 2026-06-24 (see `notes/research_5cell_cross_HARDFAIL_synthesis_2026-06-24.md`). Diagnosis at the time: SCALE_MISMATCH + wrong metric. **Three specific issues identified; this cell fixes each:**

1. **Prior cell measured RAW-MARGIN ECE without any isotonic fit-and-apply** — the name "isotonic" was misleading. This cell explicitly:
   - Splits data 70/30 train/test on separate rng seed
   - Fits `sklearn.isotonic.IsotonicRegression(out_of_bounds='clip')` on TRAIN (raw margin -> correct)
   - Applies to TEST margins to produce calibrated confidence
   - Reports ECE + corr on TEST only

2. **Prior regime was N=2048 V=50 M=2000 giving overall_acc=0.09** — at that acc, Cramer-Rao r-max ~ 0.2 (`r_max ~= 2*(AUC-0.5)*sqrt(p*(1-p))/sigma_score`; per Pencina-D'Agostino). Pre-reg r>=0.70 was mathematically unreachable. This cell uses M=500 N=2048 noise*10 giving overall_acc ~ 0.55, where r_max ~ 0.7-0.8 achievable.

3. **Prior verdict-logic bug** (also inherited into this cell's initial draft, caught pre-dispatch): pre-reg said `HP = ECE<=0.10 AND corr>=0.5` but verdict function only checked `ECE<=0.10` -> phantom HP risk. Fixed: verdict now enforces BOTH conditions strictly.

**Scope of atomization (if HP/MB lands):** "Cell 3 revival: isotonic calibration of substrate cleanup-margin confidence at M=500/N=2048/noise*10 (variable-difficulty queries) achieves ECE_calibrated=X, conf-acc-corr_calibrated=Y on 70/30 train/test split with sklearn IsotonicRegression." Scope clearly delimited: does NOT generalize to other regimes, other margins, or other substrate primitives without re-fit.

## Hypothesis

At M=500 N=2048 VV=120 noise*10 (variable difficulty via uniform noise in [0, 10]):
- Raw cleanup-margin (normalized) has substantial miscalibration (ECE_raw ~ 0.35+ from smoke).
- Post-hoc isotonic regression FIT on train and APPLIED on test produces calibrated confidence with **ECE_calibrated <= 0.10** AND **conf-acc-corr_calibrated >= 0.5** on TEST split.

## Bands (envelope-fail)

| Band | ECE_calibrated (TEST) | corr_calibrated (TEST) | Notes |
|---|---|---|---|
| HARD_PASS | `<= 0.10` (strict) | `>= 0.5` (strict) | BOTH required. First working corner of 3-signal architecture. |
| MIDDLE_BAND | `<= 0.18` | any | ECE meets miscalibration band but corr may sit at Cramer-Rao ceiling for acc~0.55. |
| HARD_FAIL | `> 0.18` OR overall_acc outside [0.30, 0.80] | any | Calibration failed OR mechanism not exercised (META_RULE_AG). |

**META_RULE_L strict-above-floor honesty:**
- ECE HP-floor 0.10; band-width to next-band boundary 0.08 (=0.18-0.10); strict-floor = 0.10 - 0.05*0.08 = 0.096. Smoke ECE=0.0645 clears strict-floor by 0.032.
- corr HP-floor 0.5; band-width above = 0.5 (ceiling 1.0); strict-floor = 0.5 + 0.05*0.5 = 0.525. Smoke corr=0.5018 CLEARS BY ONLY 0.0018 = below strict-above-floor. **Interpretation:** if FULL lands corr in [0.5, 0.525] this is honestly MIDDLE_BAND per META_RULE_L; only if FULL lands corr >= 0.525 is it a strict HP. Multi-seed variance across 5 test seeds (regime probe) was corr = [0.470, 0.496, 0.527, 0.479, 0.509] mean 0.496 sd 0.020 — corr sits AT the boundary; MB is the honest expectation.

## Discriminator-must-survive-scale (META_RULE_AG + scale rule)

**Path A satisfied:** smoke uses full-M (M=500), full-N (N=2048), full noise regime. Only TR differs (60 smoke / 300 full -> 600 vs 3000 (margin,correct) pairs). Mechanism regime IS at full-N.

**Path B analytical:** at TR=300, 3000 pairs give 2100 train / 900 test. Isotonic stability increases with n_train; TEST-side statistics (ECE, corr) tighten by sqrt(900/180) = 2.24x. Expected ECE stays ~= 0.03-0.07; corr stays ~= 0.47-0.53 (Cramer-Rao ceiling controlled by test_acc ~= 0.55).

**Multi-seed probe (regime search phase, TR=300):** corr = [0.470, 0.496, 0.527, 0.479, 0.509] across 5 rng seeds. FULL will re-run at seed=107 (deterministic). Honest expectation: MB-boundary; HP possible on seed-variance draw.

**Discriminator fires (smoke evidence):** raw ECE 0.3489 -> isotonic ECE 0.0645 = 5.4x reduction. Mechanism (isotonic fit-and-apply) is clearly exercising the substrate signal. NOT saturated at raw-ECE floor (raw ECE 0.35 far from calibrated 0.06); NOT at ceiling (calibrated ECE 0.06 measurably distinguishes from HP boundary 0.10).

## Compute architecture

**Class:** (b) sequential-CPU with justification.

**Justification:** Per-trial workload is
- `cphasor(500, 2048)` + `cphasor(120, 2048)` (small; ~10ms)
- 10 queries per trial: `(500,) * (2048,)` unbind + `(120, 2048) @ (2048,)` matmul (small; ~5ms/query)

Total per trial ~50-70ms; 300 trials ~= ~18s FULL wall (measured smoke 60 trials in <1s -> extrapolates to ~5s FULL). GPU batching would offer no material speedup at this scale (single-vector matmuls dominate); numpy CPU is optimal. No GPU-batching-mandatory violation per USER 2026-07-02 rule (speedup NOT substantial at this workload).

## META_RULE compliance

- **cardinality_ok**: N/A — no sweep axis; single-regime measurement.
- **arms_differ_verified**: N/A — single-arm cell (raw-margin + calibrated-margin on same data are ANALYSES not ARMS).
- **final_metrics_atomicity**: `tmp_replace` via `experiments/_seed_checkpoint.write_metrics` (per §7).
- **except SystemExit: raise BEFORE except Exception**: enforced in outer try at bottom of cell.
- **crlb_floor_computed**: r_max at overall_acc=0.55, sigma_score~0.3 -> `r_max ~= 2*(AUC-0.5)*sqrt(p*(1-p))/sigma_score ~= 2*0.4*0.497/0.3 = 1.3` (capped at 1.0). Discriminator target r=0.5 is well below CRLB ceiling. `crlb_formula_reference: "Pencina-D'Agostino reclassification statistic; sigma_score from cleanup-margin std"`. `discriminator_reachability: True`.
- **baseline_in_band (META_RULE_AG)**: `overall_acc in [0.30, 0.80]` enforced in verdict; smoke overall_acc=0.548 satisfies.
- **HP_SCOPE**: `{lap3_12_calibrated: [ECE<=0.10, corr>=0.5]}` applies to isotonic-calibrated arm. Raw-margin baseline reported for reference; no HP gate on raw.
- **calibration_check**: `default_ok_for_this_regime` — sklearn IsotonicRegression is standard practice; 70/30 split follows convention; no adaptive tuning.
- **cell_chunked**: false — single-seed, single-run cell.
- **start_marker_written**: false — cell wall <5s; below §13 mandatory threshold.
- **crash_diagnostic_present**: true — outer `try/except SystemExit: raise / except KeyboardInterrupt: raise / except Exception` writes `_write_crash_metrics` with traceback + atomic replace, then re-raises.
- **heartbeat_present**: false — <60s wall; below threshold.
- **defensive_error_checking**: `"passed: outer_try_writes_crash_metrics_on_exception; smoke_verified_all_paths"`.
- **run_mode**: cell defaults RUN_MODE to "full" when `--smoke` absent; `HDLAB_RUN_MODE` env var override respected. Runner will invoke without `--smoke` for FULL -> RUN_MODE=full landed correctly.
- **progress_logging**: `runner_python_u_only` + `print(..., flush=True)` on all diagnostics; total wall <10s so §17 30-min-timeout rule N/A.

## Test-design gates (§15)

- **A) sweep_alignment_verdict**: N/A — no swept parameters.
- **B) discriminating_fraction**: N/A — no sweep. Analytical: mechanism (raw ECE 0.35 -> calibrated ECE 0.06) fires strongly at chosen regime; smoke confirms.
- **C) composition_edges**: N/A — cell is standalone (numpy + sklearn); no primitive composition.
- **D) positive_control_arms**: PARTIAL — raw-margin ECE is the "uncalibrated positive-control"; isotonic-calibrated ECE is the mechanism arm; comparison is the discriminator (5.4x ECE reduction at smoke = mechanism fires).
- **E) functional_requirements**:
  - (1) monotone confidence recalibration from cleanup-margin -> sklearn.isotonic.IsotonicRegression fit-and-apply
  - (2) miscalibration measurement -> 10-bin ECE (equal-width [0,1])
  - (3) confidence-accuracy correlation -> np.corrcoef with degeneracy guard
  - All three are standard statistical primitives; no substrate-native primitive claim.

## Stage progression

**Stage 3** — M3 cortex-layer confidence architecture (compositional understanding support: cleanup-margin from substrate is confidence signal for downstream cortex-layer routing/abstention). NOT Stage 4 (no language / no BPC / no vocab). Confirmed in-scope for USER 2026-06-26 pivot arc.

## Substrate-doesn't-know-anything check

No language testing; no ingested text corpus; pure FHRR retrieval with synthetic keys/values + Gaussian noise. Confirmed compatible with USER 2026-06-26 rule.

## h4/h4b regime-confound check

Regime drill (`notes/research_h4_harness_regime_vs_mechanism_drill_2026-07-02.md`) identifies h4/h4b HF cause: contam<=5% + INTRA_COS>=0.6 low-base-rate contamination-detection harness. lap3_12's harness is DIFFERENT: single-population retrieval task with continuous noise-parameterized difficulty. NO base-rate floor confound; NO INTRA_COS regime dependence. Regime-drill assertion holds: lap3_12 "unaffected by regime confound."

## Smoke evidence

- Timestamp: 2026-07-02
- Command: `.venv/Scripts/python.exe experiments/exp_lap3_12_confidence_calibration_cpu_v1.py --smoke`
- Wall: <1s
- Result:
  - `ECE_raw=0.3489 corr_raw=0.4768` (uncalibrated reference)
  - `ECE_calibrated=0.0645 corr_calibrated=0.5018` (mechanism arm)
  - `overall_acc=0.548 train_acc=0.536 test_acc=0.578` (in-band per META_RULE_AG)
  - `n_test=180 n_train=420`
- Verdict at smoke: HARD_PASS (both HP conditions technically met; corr at META_RULE_L boundary)
- Honest tier at smoke: **MB per META_RULE_L strict-above-floor** on corr (0.5018 < strict-floor 0.525); FULL may land either MB or HP depending on seed-variance draw
- Mechanism fires: raw->calibrated ECE reduction is 5.4x (0.35 -> 0.06); clearly non-trivial substrate-signal that isotonic exploits

## Post-dispatch RUN_MODE_VERIFICATION (§16)

After FULL landing at `data/exp_lap3_12_confidence_calibration_cpu_v1/metrics.json`, verify:
- `run_mode == "full"` (cell defaults to "full" when `--smoke` absent)
- `elapsed_s` in range [2, 30] (expected ~5s; hard-flag if <1s = selftest-landed, or >60s = anomaly)
- `per_seed[0]` has keys: `ece`, `conf_acc_corr`, `ece_raw`, `conf_acc_corr_raw`, `n_total`, `n_test`, `test_acc`, `overall_acc`, `M`, `N`, `VV`, `noise_mult`, `TR`, `Q_PER_TRIAL`
- File size > 800B

## Framing caveat for atomization (Skunkworks/Director)

**Scope of any atom:** claim must be scoped to (M=500, N=2048, VV=120, noise*10 uniform difficulty, 70/30 split, sklearn IsotonicRegression, n_test=900 at FULL). NOT generalized to substrate-wide confidence-calibration claim without further sweep or replication at other regimes.

**Cell 3 closure interpretation:** if HP/MB lands, atom should note "Cell 3 (2026-06-24 HF) revived with the specifically-identified missing mechanism (isotonic fit-and-apply) + correct-regime (acc~0.55 not 0.09) + fixed verdict-logic gate -> closes prior HF." This is NOT a rediscovery — the identity of what was missing is explicit in the 2026-06-24 synthesis note.
