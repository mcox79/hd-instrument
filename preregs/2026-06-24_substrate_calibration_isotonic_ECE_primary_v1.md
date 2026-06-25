# Pre-registration: substrate_calibration_isotonic_ECE_primary_v1

**Date:** 2026-06-24
**Anchor:** substrate_calibration_isotonic_ECE_primary_v1
**Queue:** local_cpu_queue
**Lane:** 4 (substrate-product axis)
**N_DIM:** 2048 (smoke = full; audit regime preserved); **Seeds:** [7, 17, 23]; **M_TRIPLES:** 2000

## Scientific question

The prior cell (`substrate_confidence_calibration_isotonic_v1`) verdict = HARD_FAIL on `pearson_r` metric (r=0.131 against bar r >= 0.70). Skunkworks audit (`notes/skunkworks_cert_audit_5_HARDFAILS_2026-06-24.md` cell 3) caught two coupled errors:

1. **Wrong primary metric.** Pearson r between continuous confidence and binary correctness is mechanically Cramer-Rao-bounded at low base rates. Pencina-D'Agostino reclassification statistic gives `r_max ~ 2 * (AUC - 0.5) * sqrt(p * (1-p)) / sigma_score`. At measured base accuracy p ~ 0.09 and sigma_score ~ 0.30, r_max sits at ~0.10-0.20 for AUC at substrate's measured regime (~0.55). **r=0.70 was structurally infeasible at this regime regardless of calibrator.**

2. **The right metric was achieved chain-grade.** ECE landed at 0.017 in the prior cell -- a 27x reduction from raw 0.458. Isotonic calibration did EXACTLY what isotonic calibration does. The audit identified this as the load-bearing chain-grade-eligible finding suppressed by the wrong-primary framing.

**Question this cell answers:** with ECE as the pre-registered PRIMARY metric (the correct metric for calibration per Niculescu-Mizil-Caruana 2005 ICML and the broader calibration lit), does substrate's HRR cosine confidence calibrate to <= 0.05 ECE with >= 5x reduction over raw? If yes, the substrate calibration mechanism IS chain-grade and should be hdlab/-promoted for refuse-gate use.

## Pre-registered HARD bands (sacrosanct; on ECE)

PRIMARY METRIC: `ARM_ISOTONIC_REGRESSION` ECE mean across 3 seeds.
SECONDARY METRIC: pearson_r (reported with Cramer-Rao envelope; NOT gating).

- **HARD_PASS_CHAIN_GRADE**: `iso_ECE <= 0.05` AND `(raw_ECE / iso_ECE) >= 5.0` AND `iso_ECE_cv <= 0.30`. Substrate calibration is chain-grade-eligible on the correct metric; primitive lands in hdlab/.
- **MIDDLE_BAND**: `iso_ECE in (0.05, 0.10]` with reduction ratio >= 2.0. Good calibration but not chain-grade-tight.
- **HARD_FAIL**: `iso_ECE >= 0.15` OR reduction ratio `< 2.0`. Isotonic does not transfer at this regime.
- **SANITY**: `ARM_RAW_COSINE ECE in [0.30, 0.55]` (prior cell measured 0.458; band centers at audit baseline). If raw is OUT of this band, raw HRR substrate behavior has drifted vs the audit and the comparison is invalid.

## Apples-to-apples checklist (master bias)

- **Lane 4 declared** (substrate-product axis; calibration of substrate-emitted confidence).
- **ONE knob varies per arm = calibration method.** ALL arms share the same N_DIM, F_SPARSE, N_VALUES, M_TRIPLES, seeds, dev/test split (50/50, seed+1000 RNG). The only difference per arm is the calibration transform: identity (raw), isotonic (per-bin monotone), or temperature (single T sigmoid).
- **SINGLE primary metric** = ECE (10 equal-width bins). Pearson r retained as SECONDARY with Cramer-Rao envelope.
- **Pre-registered PRIMARY arm**: ARM_ISOTONIC_REGRESSION (the calibration mechanism with best lit-evidence for low-AUC tasks per Niculescu-Mizil-Caruana 2005).
- **Pre-registered SECONDARY**: pearson_r at the Cramer-Rao envelope. NOT a HARD-PASS gate.
- **Calibrator fit on DEV only** (50% split); evaluation on test (50% held-out); no leakage.
- **No transformer / LLM**: numpy + sklearn.isotonic.IsotonicRegression only.

## CONFOUND_AUDIT (per master bias checklist 2026-06-24)

- **F1 Fix #28 (Director over-claim)**: cell logs per-seed per-arm ECE + pearson_r; verdict_msg cites per-arm numerics; per-seed `cramer_rao_r_max_at_this_regime` logged as the load-bearing methodology evidence. Cert-owner re-derives from `per_unit`.
- **G3 below-threshold framing**: HP_ECE_MAX = 0.05 is industry-standard chain-grade for calibration (lit norm). NOT floor-hugging.
- **H1 capacity-respecting tier**: regime preserved from prior cell deliberately (M=2000 puts substrate in saturation where calibration is the discriminator; pre-smoke sweep in prior cell showed M=200 gives raw_r=0.42 which makes calibration trivial).
- **H2 saturated discriminator**: the prior cell's wrong-primary IS the saturated case (pearson_r unreachable by Cramer-Rao); this cell de-saturates by switching to the metric that has structural room.
- **H6 single-knob variation**: calibration method is the only knob.
- **K-corpus**: synthetic HRR concept triples; no encoder leakage; chance = 1/50 = 0.02; base accuracy ~0.09 is ~4.5x over chance.
- **No-padding**: 3 arms = control + primary + alternative-calibrator; each informative.

## Smoke evidence

Smoke = same regime as full (M=2000, 1 seed). Prior cell's smoke gave raw_r ~ 0.08 confirming audit regime; pre-smoke sweep documented M=200 -> raw_r=0.42 (too easy, calibration trivial), M=5000 -> raw_r=0.07 (similar to M=2000). **M=2000 is the audit-discriminating regime; preserved deliberately.**

Expected smoke metrics (matches prior cell's regime):
- raw_ECE ~ 0.46
- iso_ECE ~ 0.02 (chain-grade-eligible region)
- temp_ECE ~ 0.41 (temperature scaling doesn't fix systematic miscalibration)
- iso_pearson_r ~ 0.13 (at Cramer-Rao envelope; logged but not gating)

## Timeout estimate

- Per seed: M=2000 queries x ~1ms per HRR unbind + cosine vs 50 values ~ 2-5s.
- 3 arms (raw is no-op; iso fit O(M log M) ~ ms; temp fit grid ~ 100ms) ~ <1s extra per seed.
- Per-seed wall ~ 5s. 3 seeds ~ 15s.
- **timeout_s = 1200** (20 min budget). ~80x safety against measured wall; cell is CPU-light.

Below PROT-021's 14400s floor; below PROT-019 tier (no _n suffix); not GPU queue.

## REQUIRED_FIELDS

Cell emits: `verdict`, `verdict_msg`, `elapsed_s`, `summary`, `anchor_name`, `run_mode`, `n_seeds`, `detail`, `per_unit` (per-seed by_arm with `ece`, `pearson_r`, `n_test`, `accuracy_test`).

## D1 / D2 disciplines

- **D1 roofline**: cell is CPU-light; per-seed unit measurable in smoke; FULL scales linearly in seeds.
- **D2 atexit + per-seed checkpoint**: uses `_seed_checkpoint.write_partial_key` + `aggregate_partials` with `run_config` PROT-021 contamination guard (`{"run_mode": RUN_MODE, "N": N_DIM, "M": M_TRIPLES}` rejects smoke partials in FULL mode and vice-versa).

## Cramer-Rao envelope note (load-bearing)

The cell reports `cramer_rao_r_max_at_this_regime` per seed and the mean in the verdict_msg. This makes the pearson_r ceiling MECHANICALLY VISIBLE in metrics.json so future cert audits don't re-make the same wrong-primary error. Reference: Pencina M, D'Agostino R. "Overall C as a measure of discrimination in survival analysis: model specific population value and confidence interval estimation." Statist Med 2004; Niculescu-Mizil A, Caruana R. "Predicting good probabilities with supervised learning" ICML 2005 (low-base-rate ECE vs r decoupling).

## How the cell's verdict maps to the Wave A scientific decision

- HARD_PASS_CHAIN_GRADE: re-classify prior cell as `MEASURED_MECHANISM` on ECE axis (chain-grade-eligible was suppressed by wrong-primary). Promote isotonic-on-substrate-cosine to hdlab/ for refuse-gate calibration. Cell 3 audit upward-revision confirmed.
- MIDDLE_BAND: isotonic helps but not chain-grade-tight; needs larger M or per-class calibration.
- HARD_FAIL: rare given prior cell's 0.017 ECE; would indicate something drifted in substrate primitives.

Pre-reg complete. Cell + this prereg committed BEFORE dispatch.
