# Pre-registration: selfplay_b1_exog_predictive_anchor_v1 (B1+EXOG)

Filed by: exp_dev. Date: 2026-07-09. Cell:
`experiments/exp_selfplay_b1_exog_predictive_anchor_v1.py`. Status: SMOKE CLEAR, pre-registered for FULL.

## Question
Does adding an EXOGENOUS predictive anchor -- where BOTH self-play halves must independently PREDICT the
REAL ingest data (reconstruct each referent's real char-trigram content through the code bottleneck via a
per-branch `W_pred` decoder, precision-weighted) -- break the shared-upstream self-grounding blind spot that
internal decorrelation (B1 cross-fit, DG pattern separation) could NOT?

## Trigger / on-disk grounding (Fix#28, Read not assumed)
- DG (representation-level) fix landed HARD_FAIL(a): `DG_XFIT corr(failmask)=0.377`, `grounding=0.589`,
  `improve(B1-DG)=0.015`. MEASURED@`data/exp_selfplay_dg_pattern_separation_xfit_v1/metrics.json:gates`
  (`dg_failmask_corr`, `dg_grounding`, `dg_improvement_over_b1`). B1 cross-fit floor `corr=0.393`. Naive
  mirror `corr=0.788`.
- 5x negative drill (`notes/research_dg_selfgrounding_5x_remaining_internal_angles_2026-07-09.md`) closed
  angles A-D: internal methods decorrelate NOISE not the shared BIAS; exogenous ground truth is the only
  remaining known lever. B1+EXOG design + honest partial bound:
  `notes/research_exogenous_referent_grounding_predictive_coding_2026-07-09.md`.

## STAGE 1 (bias-vs-noise pre-check) -- COMPLETED
Script `experiments/analyze_dg_biasnoise_stage1_v1.py` regenerated the DG_XFIT per-referent masks at the
EXACT FULL config (the landed metrics.json persisted only aggregate rates + a mask digest, NOT the
per-referent boolean arrays; eval set is deterministic across seeds so the regenerated masks are faithful --
per-seed grounding [0.569,0.582,0.593,0.589,0.570] reproduces the landed 0.589).
MEASURED@`data/exp_analyze_dg_biasnoise_stage1_v1/metrics.json`:
- co-failure concentration ratio = **3.023**, permutation-null z = **10.41** (top-decile referents co-fail
  0.661 vs population-avg 0.219; null ratio 2.592 +- 0.041) -> co-failures are a REAL structured
  hard-referent subpopulation, NOT uniform noise (z >> 3.0).
- cross-seed co-failure phi-corr = **0.080** (the direct analog of the program's failmask_corr, across
  seeds) -> modest recurrence (below the 0.15 clean-bias bar; attenuated by single-seed Bernoulli noise).
- cofail-set Jaccard = 0.164.
- Verdict: **AMBIGUOUS_MIDDLE, leaning BIAS**. Crucially NEITHER noise condition is met (z=10.41 >> 1.0 AND
  phi=0.08 > 0.05), so the exogenous pivot is NOT contraindicated; the shared-bias structure is real but
  modest-magnitude -- itself consistent with the drill's modest P_deflated=0.25 for a B1+EXOG HARD_PASS.
- Instrument note (HONEST): the drill's originally-specified top-decile Jaccard (>=0.40 bias / <0.15 noise)
  is mis-specified for the discrete-ties reality (per-seed hardness is only 0/1/2, so "top decile" is decided
  by random tie-break among many co-failers -> artificially deflated, diagnostic-only = 0.065). The
  concentration-ratio permutation z-score + cross-seed phi-corr are the statistically valid replacements.

## STAGE 2 arms (3)
- `B0_mirror` (MUST-FAIL control): tied encoder, info-access asymmetry only. Predicted HIGH corr (~0.77).
- `B1_crossfit` (CONTRAST FLOOR, MUST reproduce ~0.39): separate enc, disjoint-fold cross-fit, no anchor.
- `B1_EXOG` (TREATMENT): B1 cross-fit + per-branch `W_pred` anchor reconstructing the SAME real content
  target, precision-weighted (reuses `hdlab.predictive_coding.residual_magnitude`/`proportional_gate`
  VERBATIM as the Rao-Ballard write-strength gate; self-test verifies elementwise equivalence).

## Discriminators
1. `failure_mask_corr` (reused verbatim): corr(1-speaker_correct, 1-listener_correct); `grounding_acc` =
   mean(listener_correct) = joint game success.
2. CAUSAL-PERTURBATION SCREEN (Prediction C, normalized directional-sensitivity ratio): swap real content
   x (grounded) vs swap neighbor-aggregate g (relation-only), each normalized by input-space delta ->
   sensitivity_content / sensitivity_relation. Causal grounding => >= 2x. B1 reported as non-grounded
   contrast. Telemetry-sensitive (self-test: content-encoder ratio 1390, relation-encoder ratio 0.009).
3. TRANSITIVE-SPREAD COMPANION (reuses snowball `label_propagation`, DIAGNOSTIC not a gate): retains the
   validated graph-smooth-attribute near-decay signature over frozen codes (regression/retention check).

## Pre-registered bands (BOTH; LOCKED PROSPECTIVE)
- **HARD_PASS** (exogenous anchor breaks the shared-bias blind spot):
  `B1_EXOG corr <= 0.20` AND `grounding >= 0.50` AND `(B1 corr - EXOG corr) >= 0.10` AND
  `perturb_ratio >= 2.0` AND B0 fires (`corr >= 0.40`, in failure band) AND B1 reproduces (`corr in
  [0.30,0.50]`) AND all codes non-degenerate (entropy >= 1.0 bit) AND anchor fired (recon gain >= 0.03).
- **HARD_FAIL(a)** -- PASSIVE exogenous anchor INSUFFICIENT -> REDIRECT to ACTIVE-INTERVENTION:
  `EXOG corr >= 0.35` (no material improvement over DG's 0.377) OR `perturb_ratio < 1.3` (no causal
  grounding), WHILE grounding retained (>= 0.50). The honest bound: passive prediction alone may be
  insufficient; active inference is the missing ingredient (Pezzulo et al. 2023).
- **HARD_FAIL(b)** -- anchor DESTROYS grounding: `EXOG grounding < 0.40`. Fix = lower `lambda_exog`.
- **MIDDLE_BAND**: EXOG corr in (0.20,0.35] with grounding >= 0.50, OR perturb_ratio in [1.3,2.0).
- **SATURATION_VACUOUS**: B0 corr < 0.40 OR B0 failure-rate degenerate.
- **CODE_COLLAPSE_VOID** / **ANCHOR_INERT_VOID**: entropy < 1.0 bit / anchor recon not > untrained.

## HONEST FRAMING (mandatory)
Tests the PARTIAL exogenous anchor (PASSIVE prediction of real data). Full referential grounding is NOT
expected (lit P~0.12: Pezzulo/Parr/Cisek/Clark/Friston 2023 argue passive prediction is insufficient for
"genuine understanding", active embodied intervention is the missing ingredient; Coelho Mollo & Milliere
2023 teleosemantic condition unmet). Realistic win = "materially decorrelates where internal could not +
shows causal movement." A HARD_FAIL(a) is a valuable pre-registered DIAGNOSTIC (redirect to
active-intervention), NOT a dead end. Do NOT frame any pass as "grounding solved." The active-intervention
ceiling is flagged as scope. P_deflated(HARD_PASS)=0.25 CITED@research_exogenous_referent note.

## SMOKE result (CLEAR -- machinery gates all pass; MEASURED@ smoke metrics.json)
MEASURED@`data/exp_selfplay_b1_exog_predictive_anchor_v1_smoke/metrics.json` (3 seeds, n=1237, 205.6s):
- B0 corr=0.792 fires=True (spk_fail=0.368 lis_fail=0.390 in band) -> assert_discriminator_fires PASS.
- B1 corr=0.327 reproduces=True (in [0.30,0.50]) -> contrast floor PASS.
- B1_EXOG corr=0.366, grounding=0.439, improve(B1-EXOG)=-0.039; perturb_ratio EXOG=3.78 / B1=3.73;
  anchor_fired=True gain=0.225; codes_ok=True (entropy ~2.8-3.3); arms differ; 0 unit failures.
- Smoke verdict MIDDLE_BAND reflects the SCIENCE preview (at smoke scale the anchor did NOT decorrelate
  corr below B1, and the referential game alone already yields perturb_ratio ~3.7). This is a genuine
  leaning-negative preview consistent with P~0.25, NOT a machinery fault. The corr<=0.20 HARD_PASS decision
  is a FULL-scale question (smoke n=1237/80ep grounding 0.44 vs FULL n=7065/220ep grounding 0.59). No
  saturation (B0-B1 gap 0.79->0.33 is large -> discriminator exercised); discriminator survives scale via
  full-branch parity, mechanism-ratio fixed (lambda_exog=0.5).

## SCHEMA-VET fields
- `cell_chunked`: false (single cell; per-seed loop with write_partial checkpointing + heartbeat).
- `start_marker_written`: true. `crash_diagnostic_present`: true (except SystemExit: raise BEFORE except
  Exception; NOT BaseException; grep-clean of bare except). `heartbeat_present`: true.
  `defensive_error_checking`: passed_all_4_patterns.
- `final_metrics_atomicity`: tmp_replace (write_metrics -> os.replace).
- `arms_differ_verified`: true (3 mask-pairs hashed per seed; all differ).
- `cardinality_ok`: true (EXPECTED_N_UNITS = 3 arms * n_seeds; verdict emits
  HARD_FAIL_CARDINALITY_BREACH if short).
- `baseline_in_band`: true (B0 fail rates in [0.05,0.95]).
- `crlb_n/a`: discriminator = failure-mask CORRELATION vs within-cell MUST-FAIL control (B0) + normalized
  directional-sensitivity RATIO; reachability by construction (B0 fires high; treatment in [0,corr(B0)];
  HP corr<=0.20 w/ margin>=0.10 inside; ratio gate 2.0 with planted-encoder self-test proving sensitivity).
- `calibration_check`: adaptive_with_discriminator_gate (lambda_exog/K/tau fixed per profile; anti-collapse
  + B0-fires + baseline-in-band + anchor-fires + perturb-sensitivity recomputed per run).
- `progress_logging`: print_flush_true (line-buffered + per-(seed,arm) heartbeat; FULL timeout_s >= 1800).
- `multi_seed_smoke`: true (3 seeds).
- Compute architecture: (c) mixed sequential-CPU with justification (shallow linear ProjHeads + linear
  W_pred decoders; cost is the sequential self-play training loop). Storage strategy: no_storage.
- HP_SCOPE: {decorrelation -> B1_EXOG; screen-fires -> B0; contrast-reproduce -> B1_crossfit; anti-collapse
  -> ALL; anchor-fires + perturb-ratio -> B1_EXOG (B1 ratio reported as contrast)}.

## Number tags
- DG residual corr 0.377, B1 0.393, mirror 0.788: MEASURED@`data/exp_selfplay_dg_pattern_separation_xfit_v1/metrics.json`.
- Stage-1 concentration ratio 3.023 / z 10.41 / phi 0.080: MEASURED@`data/exp_analyze_dg_biasnoise_stage1_v1/metrics.json`.
- Smoke numbers: MEASURED@`data/exp_selfplay_b1_exog_predictive_anchor_v1_smoke/metrics.json`.
- HARD_PASS bands (corr<=0.20, ratio>=2.0, margin>=0.10): HYPOTHESIZED@this prereg (from the exogenous
  drill's falsifiable table + the task discriminator definition).
- P(HARD_PASS)=0.25, P(full grounding)=0.12: CITED@`research_exogenous_referent_grounding_predictive_coding_2026-07-09.md`.

## Dispatch
FULL -> `remote_cpu_queue` (CPU cell; small linear nets + numpy; no GPU-batching mandate). ETA ~40-55 min
(smoke 205.6s at reduced scale; DG-cell FULL analog 1513s for 15 units; B1_EXOG adds anchor + perturbation +
companion). Timeout 9000s.
