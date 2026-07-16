# Pre-reg: ingest-gate combination-rule head-to-head race (v1)

Cell: `experiments/exp_ingest_gate_combination_rule_race_v1.py`
Anchor: `ingest_gate_combination_rule_race_v1`
Date: 2026-07-16. Author: exp_dev. Source: Director task + quantum drill
`notes/research_consolidation_gate_quantitative_signals_2026-07-16.md`.

## Question
Does being EXACTLY like the brain (Friston precision-weighted decomposition) fix v4's coarse surprise? v4
(`exp_ingest_gate_deconfound_within_relation_derivability_v1`, MEASURED DECONF_AUC=0.545 ~chance) found flat
raw-surprise does NOT separate within-relation DERIVABLE vs UNDERIVABLE once the r* row is trained. Race the brain's
combination FORM against a learned combiner and a calibrated hybrid, plus honesty reference arms.

## Arms (revision-score per held-out r* candidate; higher = underivable = needs structural revision)
- ARM_FLAT      = raw_PE                              (v4 baseline; reproduces ~chance)
- ARM_SCHEMAFIT = (1 - schema_fit)                    (REFERENCE; schema_fit = reachability rank-pct, a DIFFERENT
                                                       computation than the derivable label -> non-vacuous)
- ARM_BRAIN     = raw_PE * (1 - schema_fit)           (brain FORM, FIXED unit weights, NO fitting)
- ARM_HYBRID    = sigma(w . [fast_track, slow_track]) (brain 2-track FORM, CALIBRATED weights; isolates form vs weights)
- ARM_LEARNED   = sigma(w . [raw_PE, schema_fit, recurrence, fast_track, slow_track]) (free features, substrate learns)
fast_track = raw_PE*schema_fit, slow_track = raw_PE*(1-schema_fit). Learned/hybrid fit on a DISJOINT calib split,
scored on a held-out test split (generalization). schema_fit / derivability oracle both from base-train (non-r*) edges.

## Metric
DECONF_AUC[arm] = AUC(revision-score; UNDERIVABLE vs DERIVABLE), both held-out r*, SAME trained row. Chance = 0.50
(self-checked by RANDLABEL). Primary = test split (fair generalization); deconf_full reported as train-contaminated ref.

## Bands (HYPOTHESIZED@this-file; measured at smoke/full)
- HP_DECONF_MIN = 0.65 (an arm "works"; strict +0.15 above chance). HF_DECONF_MAX = 0.58 (collapse ~chance).
- DECISIVE_MARGIN = 0.05 (learned decisively beats brain). TIE_EPS = 0.02.
- SCHEMAFIT_LEAK_MAX = 0.95 (schema_fit near-copies label -> race vacuous, DEMOTE).
- PRECHECK_DIFF_MIN = 0.10 (consolidation-benefit tertile differentiation; drill HARD bands top>=0.90/bot<=0.50 reported).

## Verdict tiers (head-to-head)
- BRAIN_FORM_WORKS: harness-valid AND brain>=0.65 AND brain>=max(flat,schemafit)-TIE AND NOT learned_beats_brain
  AND brain>schemafit+TIE => being exactly like the brain works. ROUTE TO VET.
- SCHEMAFIT_CARRIES: schemafit>=0.65, flat ~chance, brain<=schemafit+TIE => the fix is schema_fit structural signal;
  the surprise*schema interaction is inert.
- LEARNED_BEATS_BRAIN: learned>=0.65 AND learned>brain+0.05 => brain FORM incomplete, weights matter.
- DECOMPOSITION_NO_SIGNAL: brain/hybrid/learned all <=0.58 => schema-conditioning does not fix v4.
- SCHEMAFIT_LEAK / MIDDLE_BAND / INCONCLUSIVE_harness as above.

## Cheap pre-check (discriminator-fires; ZERO extra fits -- reuses trained-row foundation as "full re-fit",
untrained-row as "before", TransE-mean fold-in as "fast-track"): does schema_fit TERTILE differentiate consolidation
benefit? ratio = fast_gain/refit_gain per tertile; gate = (high - low) >= 0.10.

## Harness-valid controls (reuse v4 verbatim)
CONF_AUC (untrained-row confound) >= 0.70; POSCTRL (corrupt-r* vs in-train-r*) >= 0.75; RANDLABEL in [0.40,0.60];
r* MRR >= 0.30 (row trained); infer_mrr >= 0.40 and in (0.05,0.95) (foundation strong, in band); class balance >= 0.20.

## Compute architecture
Sequential-CPU, justified: cell IS 2 AdditiveKGMap SGD fits per seed (the substrate primitive being validated),
each < ~40s; all arm scoring / logreg / tertile / routing is cheap numpy post-processing on cached tensors. No GPU
batching win (small-N sequential SGD). storage = no_storage (in-memory coords). Wall: smoke 46s (MEASURED); full ~200-250s.

## SCHEMA-VET items
arms_differ_verified (5 arm-score vectors hash-distinct); final_metrics_atomicity=tmp_replace; except SystemExit
before Exception (no BaseException); crlb_n/a (rank statistic, RANDLABEL self-calibrates chance); baseline_in_band
(infer_mrr 0.05<mrr<0.95 + strong); discriminator survives scale (3-seed smoke fires arm spread + harness valid,
full confirms); HARD_PASS strictly above chance+band; cardinality_ok (EXPECTED_N_UNITS=n_seeds); per-unit status;
calibration_check=adaptive (TAU/PRECISION_MIN/SURPRISE_FLOOR OURS to calibrate per drill Part-B, logged); real_code_path
(self_test builds AdditiveKGMap + gen_composed_arena + derivability_labels + race_seed + logreg at N~16); deterministic
(fixed int seeds, np default_rng, logreg zero-init; no hash()-seed / list(set())); progress_logging=print_flush_true.

## MEASURED smoke (N=300, 3 seeds, 46s, harness_valid=True)
DECONF_AUC[test]: flat=0.473 schemafit=0.761 brain=0.497 hybrid=0.664 learned=0.580. precheck_diff=0.097 (fires=False,
marginal). CONF=0.980 POSCTRL=0.997 RAND=0.465 infer_mrr=0.715 rstar_mrr=0.949. Verdict SCHEMAFIT_CARRIES_the_fix:
being exactly like the brain (fixed-weight multiplicative decomposition) UNDERPERFORMS a plain schema_fit reading; the
surprise-mixing collapses the clean schema signal to chance. FULL dispatched for scale-confirmation before VET.
