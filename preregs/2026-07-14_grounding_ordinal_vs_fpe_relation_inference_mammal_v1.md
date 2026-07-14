# Pre-registration: ORDINAL-vs-FPE grounded-attribute encoding (relation inference, mammal arena)

- anchor_name: `grounding_ordinal_vs_fpe_relation_inference_mammal_v1`
- cell: `experiments/exp_grounding_ordinal_vs_fpe_relation_inference_mammal_v1.py`
- date: 2026-07-14
- queue: `remote_cpu_queue` (CPU-only; device forced cpu on remote_cpu)
- lineage: Thrust-B grounding, LEVER B (ordinal/comparison encoding) from
  `notes/research_grounding_topicB_synthesis_and_next_levers_2026-07-14.md`.
- reuses the arena + gate machinery of
  `experiments/exp_grounding_gated_fusion_relation_inference_mammal_v1.py`; swaps ONLY the grounded-
  attribute ENCODING from absolute FPE random-Fourier features to an ORDINAL thermometer/level code.

## Question (contract)
Does an ORDINAL (thermometer / level) encoding of the grounded attributes MATCH or BEAT the absolute
fractional-power (FPE) encoding on held-out-relation inference (same gated-fusion arena), at LOWER
encoding cost AND with MORE bundling-robustness, while carrying the same grounding signal?

## Ordinal scheme (glass-box)
THERMOMETER / LEVEL code: for each normalized attribute v in [0,1] and `ORDINAL_LEVELS=9` equally
spaced interior thresholds t_j, bit_j = 1[v >= t_j]. Each column is literally "is attribute k above
ordinal level j" -- a pure COMPARISON. NO absolute-value column is carried (strongest form of the
ordinal claim: comparisons alone, no calibrated magnitude). Rank / pairwise-comparison codes are
alternative ordinal schemes noted in the drill but NOT implemented here (thermometer is the cleanest
glass-box level code). Dim `5*9 = 45` is MATCHED to the FPE feature dim `5*(1+2*4) = 45` so the
head-to-head is a fair same-dimension comparison; the ONLY difference is ops per feature.

## Arms (8 geometric + POP)
- `RELATIONAL_ONLY` -- ablation baseline (anchor-compose bundle, no grounding). HP anchor.
- `GATED_ORDINAL` -- MECHANISM: convex gate (1-lam)*rel + lam*ordinal-grounded, lam learned on VAL.
- `GATED_FPE` -- REFERENCE: same gate over the FPE-grounded code (the existing recipe).
- `GROUNDED_ORDINAL_ONLY` -- ordinal grounded estimate only.
- `GROUNDED_FPE_ONLY` -- FPE grounded estimate only (reference standalone).
- `SCRAMBLE_ORDINAL` -- must-fail: ordinal gate over attributes SHUFFLED across entities (lam re-learned).
- `RANDOM_CODES` -- null.
- `ORACLE_ADDITIVE` -- positive control (held-out folded into the fit = ceiling).
- `BASELINE_POP` -- frequency incumbent (fit-independence sanity).

## Primary metric
Held-out RELATION inference filtered MRR (+ hits@{1,3,10}) rank-vs-all, KGE standard, degree-unbiased,
NO sampled-negative pool. PAIRED ablation on the SAME held-out-relation queries. Multi-seed.

## Pre-registered bands (BOTH; RELATIVE deltas; fractions fixed BEFORE run)
- `MATCH_TOL=0.03`, `HP_RECOVER_GAIN=0.10`, `SCR_ABS_MARGIN=0.05`, `SEED_CONSISTENCY_FRAC=0.75`,
  `MB_PARTIAL_GAIN=0.03`, `ORACLE_FIRE_RATIO=3.0`, `ORACLE_FIRE_ABS=0.05`, `REL_ABOVE_RANDOM_MIN=0.02`,
  `MIN_HELDOUT=15`, `ROBUST_MARGIN=0.03`.

HARD_PASS `ORDINAL_MATCHES_OR_BEATS_FPE` -- ALL of:
  (a) MATCH: mean `GROUNDED_ORDINAL_ONLY - GROUNDED_FPE_ONLY >= -MATCH_TOL` AND
             mean `GATED_ORDINAL - GATED_FPE >= -MATCH_TOL`.
  (b) RECOVER: mean `(GATED_ORDINAL - RELATIONAL) >= HP_RECOVER_GAIN`.
  (c) RIGHT-ATTRS: mean `(GATED_ORDINAL - SCRAMBLE_ORDINAL) >= SCR_ABS_MARGIN`.
  (d) CONSISTENCY: per-seed `(GATED_ORDINAL - RELATIONAL) > 0` in `>= SEED_CONSISTENCY_FRAC` of seeds.
  (e) ARENA VALID: ORACLE fires AND RELATIONAL above RANDOM AND not broken.
  Reported supporting diagnostics (NOT gating by themselves): `ordinal_cheaper` (by construction),
  `ordinal_more_bundling_robust` (bundling probe AUC).

MIDDLE_BAND `ORDINAL_GROUNDS_BUT_BELOW_FPE` -- mean `(GATED_ORDINAL - RELATIONAL) >= MB_PARTIAL_GAIN`
  AND arena valid, BUT the MATCH (a) fails (ordinal below FPE by > MATCH_TOL) OR scramble/consistency
  fails. Ordinal carries grounding but does not match the FPE recipe.

HARD_FAIL `ORDINAL_FAILS_TO_GROUND` -- mean `(GATED_ORDINAL - RELATIONAL) < MB_PARTIAL_GAIN` with
  ORACLE firing. The ordinal encoding fails to carry the grounding signal.

INCONCLUSIVE if ORACLE does not fire, `n_query < MIN_HELDOUT`, RELATIONAL at the RANDOM floor, or a null
  beats the relational baseline.

## Must-fail control
`SCRAMBLE_ORDINAL`: same ordinal-gate pipeline over attributes shuffled across entities (lambda
re-learned on VAL). Real ordinal attributes must beat shuffled through the gate
(`GATED_ORDINAL - SCRAMBLE_ORDINAL >= SCR_ABS_MARGIN`). RANDOM must stay at the ~1/N floor.

## Bundling-robustness probe (first-class DIAGNOSTIC, glass-box, matched-dim)
Classic bundle-capacity test: superpose (unit-sum) B distinct entities' grounded-attribute codes, then
test each member is still individually detectable (cosine to bundle beats every distractor). Sweep
`BUNDLE_DEPTHS=[1,2,4,8,16,24]`, `BUNDLE_N_DISTRACT=20`, `BUNDLE_N_TRIALS=60`. SAME member/distractor
draws per encoding. Report per-depth accuracy curve + AUC for ordinal and FPE. `ordinal_more_bundling_
robust = ordinal_auc >= fpe_auc + ROBUST_MARGIN`. REPORTED (informs the narrative), does NOT gate
HARD_PASS by itself (contract asks the check be INCLUDED; HARD_PASS is the arena match/beat).

## Encoding cost (THEORETICAL, by construction, glass-box)
`encoding_cost()` op accounting per entity at matched dim 45: ordinal = 45 compares, 0 mults, 0
transcendentals; FPE = 20 mults + 40 transcendentals (cos/sin RFF). `ordinal_cheaper=True` by
construction (no transcendentals, dims matched). THEORETICAL@`encoding_cost` in-cell.

## Compute architecture
class (b) sequential-CPU. Mammal taxonomy KG (N ~ 125). Per seed: 2 additive-KGE fits (ADDITIVE +
ORACLE) via `_kge_anchor1_fit` minibatch SGD + 3 closed-form ridge maps (ordinal/FPE/scramble) + 3
lambda grid-searches (11 pts) on tiny VAL cdist matrices + one cheap bundling probe. Seconds/seed on
CPU; GPU buys nothing. Storage SHARDED (each entity its own code; relations = per-TYPE additive
displacements; only bundle = per-ENTITY anchor mean + the diagnostic superposition probe). device
forced cpu on remote_cpu.

## SCHEMA-VET gate fields
- `cardinality_ok: true` -- EXPECTED_N_UNITS = n_seeds (FULL 8); each seed asserted to produce 8 arms
  + `>= DISTINCT_SIG_FLOOR (5)` distinct signatures; `< n_seeds` -> HARD_FAIL_CARDINALITY_BREACH.
- `arms_differ_verified: true` -- `_sig` per arm; floor 5. EXEMPT collapses (correct-by-construction):
  (GATED_ORDINAL==GROUNDED_ORDINAL_ONLY) at lam_ord=1; (GATED_FPE==GROUNDED_FPE_ONLY) at lam_fpe=1;
  (SCRAMBLE_ORDINAL==RELATIONAL_ONLY) at lam_scr=0. Min distinct = 5.
- `final_metrics_atomicity: tmp_replace`.
- `except SystemExit: raise` BEFORE `except Exception` (no BaseException / no bare except; grep-clean).
- `crlb_n/a`: match/recovery are RELATIVE deltas vs the MEASURED FPE reference + RELATIONAL; ORACLE=1.0
  saturates by construction and is used ONLY as the arena-answerable gate.
- `baseline_in_band: true` -- ORACLE must fire (>=3x RANDOM AND headroom >= 0.05); RANDOM near 1/N;
  RELATIONAL above RANDOM (guarded).
- discriminator survives scale: PAIRED delta on the SAME queries; planted self-test fires the ordinal
  mechanism deterministically (see MEASURED self-test below).
- `HP_SCOPE`: match/recovery gates apply to GATED_ORDINAL vs RELATIONAL / GATED_FPE / GROUNDED_*_ONLY.
  ORACLE = positive control; RANDOM/SCRAMBLE_ORDINAL = must-not-explain controls; GATED_FPE /
  GROUNDED_FPE_ONLY = the reference matched/beaten; POP = fit-independence sanity.
- `calibration_check: adaptive_with_discriminator_gate` -- every lambda is LEARNED ON VAL, never on
  test; split fractions + band fractions pre-registered, not tuned on real test queries.
- per-unit failure-class instrumentation (no bare except; per-seed `failure_class` recorded).
- `start_marker_written: true`, `crash_diagnostic_present: true` (CELL_CRASHED metrics + traceback),
  `defensive_error_checking: passed`.
- `cell_chunked: false` (multi-seed in one cell; seconds/seed; per-seed try/except records failures).
- `progress_logging: print_flush_true` (line-buffered stdout + per-seed/per-arm flush prints).
- Gate A `sweep_alignment_verdict: N/A` (no nominal-vs-effective sweep parameter).
- Gate B `discriminating_fraction`: single arena, not a saturation sweep; planted self-test lands in
  band (RELATIONAL 0.11, GATED_ORDINAL 0.54, GROUNDED 0.53, ORACLE 0.95 -- MEASURED below).
- Gate C `composition_edges`: attribute -> thermometer-feature -> ridge -> latent -> additive-score all
  SHAPE_MATCH (reuses proven fit_ridge + additive_scores primitives).
- Gate D `positive_control_arms`: ORACLE reproduces the arena ceiling AT THE TEST REGIME; the planted
  self-test reproduces the gated-fusion mechanism (ordinal channel) as an at-regime positive control.
- Gate E functional requirements: (1) encode grounded attribute -> ordinal_ground_features; (2) map to
  latent -> fit_ridge; (3) fuse with relational -> convex gate learned on VAL; (4) score held-out
  relation -> additive_scores + filtered_hits_from_scores. All mapped to reused CG primitives.
- Gate F.1 `real_code_path_exercised`: [fit_kge_anchor1, filtered_hits_from_scores, fit_ridge,
  ordinal_ground_features, fpe_ground_features, bundling_robustness_probe] -- the self-test CALLS the
  REAL objects on the planted arena.
- Gate F.2/F.3 `substrate_signature_checked`: fit_kge_anchor1 bound with BASE/portable kwargs only
  (train_edges, N, n_rel, k, device, seed, epochs).
- Gate F.4 `guard_baseline_validated`: RELATIONAL_ONLY validated above the RANDOM floor (eps=0.005)
  before it anchors the recovery delta.
- VALIDITY_PREFLIGHT_MODE=enforce: F.1-F.4 DECLARED; self-test PASSES under enforce (MEASURED below).

## Numbers (tagged)
- HP_RECOVER_GAIN=0.10, MATCH_TOL=0.03, SCR_ABS_MARGIN=0.05  HYPOTHESIZED@this-prereg (pre-registered
  band fractions; the 0.10 recovery bar mirrors the gated-fusion cell's proven recovery target).
- prior gated-fusion (absolute FPE) 8-seed FULL was MIDDLE_BAND; GROUNDED_ONLY 0.618 >> RELATIONAL 0.387
  MEASURED@d:/AI/hd-instrument/data/exp_grounding_improves_relation_inference_mammal_v1/metrics.json:
  gates.heldout_mrr.
- SELF-TEST (planted arena, enforce mode, EXIT 0) MEASURED@ self-test stdout 2026-07-14:
  heldout_mrr RELATIONAL=0.114 GATED_ORDINAL=0.539 GROUNDED_ORDINAL=0.528 GATED_FPE=0.570
  GROUNDED_FPE=0.579 SCRAMBLE_ORDINAL=0.443 RANDOM=0.034 ORACLE=0.949 POP=0.476; gain(ord-rel)=+0.425,
  dilution=-0.011, scr_margin=+0.097, lam_ord=0.6 lam_fpe=0.8; ordinal_cheaper=True;
  bundling ord_auc=0.376 fpe_auc=0.257 more_robust=True (ord_curve B2=0.73/B8=0.15 vs fpe B2=0.27/B8=0.07);
  vp_ok=True. (On the linear-friendly planted arena ordinal is ~0.03-0.04 BELOW FPE on the arena metric
  as expected; the self-test only requires the ordinal mechanism to FIRE, not to beat FPE -- that is the
  FULL-run question on real mammal attributes.)

## Configs
- FULL: seeds [7,13,17,23,29,31,37,41], k=16, epochs=300, n_neg=48, batch=1024.
- SMOKE (queue_add built-in gate): seeds [7,13,17], k=16, epochs=120.
- SELFTEST: planted KG, k=12, epochs=200.
- FULL timeout: 900s (measured self-test wall ~5s incl import; FULL ~40s; 900s is >20x safe margin).

## Dispatch
`bash tools/orchestrator/queue_add.sh remote_cpu_queue grounding_ordinal_vs_fpe_relation_inference_mammal_v1 experiments/exp_grounding_ordinal_vs_fpe_relation_inference_mammal_v1.py preregs/2026-07-14_grounding_ordinal_vs_fpe_relation_inference_mammal_v1.md 900`
