# Pre-reg: Encoder v3e -- DECLINE-vs-PLATEAU diagnostic (in_batch-RKD-only, NCE off, LONGER run, 2 seeds)

Date: 2026-07-04. Author: exp_dev. Status: PRE-REGISTERED before dispatch.
Core cell: `experiments/exp_encoder_v3e_decline_vs_plateau_v1_core.py`
Per-seed wrappers (CHUNKED single-seed-per-cell): `experiments/exp_encoder_v3e_decline_vs_plateau_v1_seed_7.py`, `..._seed_13.py`
Anchors: `encoder_v3e_decline_vs_plateau_v1_seed7`, `..._seed13` (smoke suffix `_smoke` on each).
Parent cells (read-only imports, NOT edited): v3 (`exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py`), v3c (`exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_core.py`).

## Prior-work check (substrate concept-query, USER-locked 2026-07-01)

Query: "longer training decline plateau trajectory in-batch objective contrastive removed cosine to
gold retrieval agreement headline metric" -> top hit cosine=0.2841 (this arc's own v3c/v3b prose,
expected self-similarity), all other hits <=0.26. NONE at cosine>0.30 for a distinct prior cell.
GENUINELY NOVEL: no prior cell in this lineage runs a 6000-step trajectory with a trend-slope
verdict or promotes ret_agree10/hi80_cos to headline status.

## Why this cell exists (VET refutation of v3c's 0.89 headline)

v3c's seed_7/seed_13 (batch=128, steps=1800, nce=0, full 177899-concept cache) reported
IN_BATCH-RKD-only BLOCK(best-by-held)=0.897/0.887, apparently at/above the 0.85 target. A
Skunkworks VET REFUTED this as the certified number, on four grounds (VERIFIED@this session):

1. **Best-ckpt inflation**: seed_7's in_batch DENSE trajectory declines from its post-floor peak
   (0.876@step450) to 0.759@step1800 (FINAL) -- a ~13% drop
   MEASURED@data/exp_encoder_migration_step1b_v3c_paired_rkd_only_seed_7/metrics.json:recovery.inbatch_traj.
   v3c's own `peak_decline` flag is miscalibrated (counts the untrained-network step-0 spike,
   ~0.956, as "the peak," so its own HARD_PASS branch requiring `not peak_decline` is unreachable
   by construction).
2. **Not reproducible** at the nominally-same config: v3b's NCE_ZERO (global, batch=128, steps=1800)
   landed FINAL DENSE=0.7336 vs v3c's independent re-run at the same nominal config landing FINAL
   DENSE=0.6514 (GLOBAL arm) -- an 11% gap.
3. **Confounded** improvement: v2->v3c moved steps (40000->1800), batch, AND best-of-13-checkpoints
   selection simultaneously; in_batch is already declining within the 1800-step budget.
4. **Wrong headline metric**: v3c's gate metric is Spearman over 400k mostly-random held pairs;
   ret_agree10 (the closer analog to the actual "0.85 semantic" goal) swings 0.15-0.67 across
   seed_7/seed_13's own arms and was never surfaced as a headline number.

GLOBAL (landmark) stays DROPPED (independently confirmed broken: keyed_roundtrip J=5 =
0.133/0.317 << 0.90 in both v3c seeds -- FALSE_WIN_ALGEBRA_GLOBAL).

## What this cell answers

Does in_batch-RKD-only PLATEAU at a usable level given a LONGER training budget (VET-specified
4000-6000 steps; this cell uses 6000, the upper end), or does it keep DECLINING toward v2's 0.368
collapse floor? This decides whether removing NCE genuinely FIXES the in_batch objective's
late-training behavior, or merely SLOWS its collapse (a temporary reprieve, not a fix).

## Design (VET-mandated + retained methodology fixes)

- **STEPS=6000** (was 1800), **DENSE_EVAL_EVERY=50** (was 150) -- ~120 trajectory points, enough
  for a genuine linear-fit trend estimate (not a peak-vs-final anecdote).
- **FINAL-step numbers ALWAYS reported** as the PRIMARY (gated) number -- LAST-step requires no
  selection, so by construction it cannot be a cherry-picked spike. best-by-VAL (selected on VAL,
  reloaded, then encoded+scored FRESH on TEST) is SECONDARY context only.
- **HEADLINE METRICS PROMOTED** (VET's explicit instruction): `ret_agree10` and a cosine-to-gold
  metric (`hi80_cos`/`hi80_teacher_mean`/`hi80_calib_err` -- mean code-pair cosine restricted to
  pairs whose TEACHER cosine is itself >=0.80, i.e. "genuinely gold-similar pairs", exactly the
  regime the 0.85 target is stated in) are top-level `recovery{}` fields, co-equal with (not
  instead of) the existing Spearman number. These fields already existed inside v3's
  `_semantic_unit` but were never promoted out of `per_unit` in any prior cell this lineage.
- **3-way split retained from the (cancelled, never-dispatched) v3d design**: held pool (17790
  concepts at FULL, HELD_FRAC=0.10 capped at FULL_HELD_CAP=20000, unchanged from v3/v3c) splits
  into VAL (5000, used ONLY for checkpoint-trajectory logging + best-ckpt selection) and TEST
  (12790, NEVER seen during training or selection; every reported number is on TEST). Fixes the
  "validation set doubles as the reported test number" leakage class
  (`feedback_held_out_test_methodology_required_for_macro_F1_claims_USER_LOCKED_11th_methodology_rule`).
- **TREND-SLOPE verdict (new)**: linear fit of `dense_full` vs step over all post-anti-gaming-floor
  eval points (`min_step_for_best = 0.05*steps = 300`), plus an early-half-vs-late-half mean
  comparison (`early_minus_late`). Decides PLATEAU_CONFIRMED / DECLINE_CONTINUES / AMBIGUOUS_TREND,
  mapped onto the pipeline's canonical verdict enum as HARD_PASS/HARD_FAIL/MIDDLE_BAND
  respectively (`verdict_msg` carries the real semantic label).
- **Algebra suite SIMPLIFIED** back to v3c's original single-J=5 convention (keyed + shuffled-key
  only; the 6-point J-grid from the cancelled v3d design is dropped here -- not what VET asked for,
  and per-run cost matters more now that steps are 3.3x longer).
- **TWO SEEDS** (7, 13 -- matching v3c's own seeds for direct before/after comparability). The
  trajectory-SHAPE question is expected to be less seed-sensitive than a single point estimate;
  more seeds are a cheap follow-up if the 2-seed read is ambiguous.

## Compute architecture

Class (b) mixed-with-justification: GPU-batched matmul training loop (reused verbatim from
`v3c._train_student_full`, itself GPU-batched), sequential-only in the outer per-J/per-arm eval
loop (small, <=10 units total, each a batched cleanup-argmax over the codebook). Storage strategy:
no_storage/no_composition beyond the existing bind/unbind/cleanup keyed-unit check (single-hop,
not a chained-retrieval composition).

## Functional requirements

| Requirement (plain English) | Existing primitive addressed by |
|---|---|
| Train in_batch-RKD-only student at NCE=0, longer budget | `v3c._train_student_full` (reused, objective="in_batch") |
| Report a non-cherry-picked "official" number | LAST-step (post-loop) student, no selection |
| Report the actual 0.85-relevant metric, not buried | `v3._semantic_unit`'s `ret_agree10`/`hi80_cos` promoted to `recovery{}` top level |
| Detect whether recovery is real or an artifact of stopping early | new `_trend_diagnostic` (linear fit + early/late means) |
| Prevent held-set doubling as both selector and reported number | 3-way split (VAL for selection, TEST for all reported numbers) |
| Verify the code stays a valid composable SBC code | `v3._keyed_unit`/shuffled-key (unchanged J=5 convention) |

## Effective-vs-nominal parameter audit

Swept params: none (single fixed config; this is a longer-horizon replicate of v3c's config, not a
sweep). `sweep_alignment_verdict: N/A_no_sweep_axis`.

## Bracket-includes-discriminating-band

Not a sweep cell; N/A. The trend-slope bands (`PLATEAU_EARLY_MINUS_LATE_MAX=0.03`,
`DECLINE_EARLY_MINUS_LATE_MIN=0.10`) bracket a genuinely uncertain middle region
(`[0.03, 0.10)` -> AMBIGUOUS_TREND), so the discriminator itself is not by-construction saturated
at either extreme.

## Signal-shape compatibility audit

`v3c._train_student_full` (dense_traj list of `{step, dense_full, dense_quick, rkd, final}` dicts)
-> this cell's `_trend_diagnostic` (expects exactly that list-of-dict shape): SHAPE_MATCH (verified
by the self-test's tiny synthetic run, which asserts `trend["sufficient"] is True` on a real
`dense_traj` produced by `v3c._train_student_full`).

## Positive-control reproduction (Gate D)

`v3._keyed_unit("RANDOM_BLOCK", "sbc", ..., J=5, ...)` is the SBC-lossless sanity check
(`acc_at1 >= 0.98` required); this is the SAME primitive, SAME regime (K=128/N=4096 block code),
already validated at this exact config in v3/v3b/v3c (tolerance: reproduce >=0.98, matches prior
`acc_at1=1.0` MEASURED@v3c seed_7/seed_13 metrics.json). `regime_extension_audit: SHAPE_MATCH`
(identical K/N/block_l, no regime change).

## CRLB / capacity-feasibility

`crlb_floor_computed=0.901` at K=128 (THEORETICAL@v2/v3/v3b/v3c prereg: `r_max = sigma_teacher /
sqrt(sigma_teacher^2 + 0.25/K)`, unchanged -- this cell changes only step count, eval cadence, split
methodology, and verdict semantics, not the K=128/N=4096 quantization channel).
`discriminator_reachability: True` (HP_floor bands sit below the theoretical ceiling: e.g. the
PLATEAU floor `final_block>=0.50` is well below 0.901).

## Pre-reg bands (HYPOTHESIZED, tagged)

- `PLATEAU_EARLY_MINUS_LATE_MAX = 0.03` HYPOTHESIZED@this prereg (post-floor trajectory
  essentially flat).
- `DECLINE_EARLY_MINUS_LATE_MIN = 0.10` HYPOTHESIZED@this prereg (clearly still declining).
- `PLATEAU_FINAL_BLOCK_FLOOR = 0.50` HYPOTHESIZED@this prereg, informed by seed_7's own LAST-step
  DENSE=0.7587 MEASURED@data/exp_encoder_migration_step1b_v3c_paired_rkd_only_seed_7/metrics.json:recovery.inbatch_traj[-1].dense_full
  (BLOCK at LAST-step has never been measured before this cell; a floor comfortably below that
  DENSE analog, and comfortably above v2's 0.368 CITED@notes/encoder_rescue_plan_converged_diagnosis_2026-07-04.md
  collapse floor, is the discriminating middle ground).
- `DECLINE_FINAL_BLOCK_CEILING = 0.45` HYPOTHESIZED@this prereg (approaching v2's 0.368 floor).
- `ALGEBRA_FLOOR = 0.90` (unchanged convention from v3/v3b/v3c).

## HP_SCOPE

Trend-slope + final-value bands apply ONLY to `INBATCH_BLOCK_LAST`. `INBATCH_*_BESTVAL` (on TEST)
is comparison/context, NOT separately gated. `RANDOM_BLOCK`/`CHARPOS`/`shuffled_key` are
integrity-only (positive control / calibration baseline / negative control).

## Cardinality

`EXPECTED_N_UNITS = 10` both run_modes (SMOKE=FULL code path): semantic(6: LAST+BESTVAL x
{DENSE,BLOCK}, RANDOM_BLOCK, CHARPOS) + keyed(4: RANDOM_BLOCK-posctrl J5, LAST J5,
BESTVAL-cmp J5, LAST-shuffled J5). `cardinality_ok` gates HARD_FAIL if `len(per_unit) < expected`.

## Discriminator-survives-scale (option B, analytical justification)

Smoke (V_train=3000, 200 steps, dense_eval_every=20) validates MACHINERY ONLY: in_batch trains
end-to-end at the longer relative step count, 3-way split partitions correctly, best-by-VAL
selection + reload-on-TEST fire, the trend-slope diagnostic runs on a real multi-point trajectory
(>=10 points), headline `ret_agree10`/`hi80_cos` fields populate. SMOKE VERIFIED (2026-07-04):
seed_7 HARD_PASS elapsed=36.9s, seed_13 HARD_PASS elapsed=38.1s, both with
`trend_sufficient=True`, `n_trend_points=10`, all 10 units present, arms differ. The actual
plateau-vs-decline question needs the true 177899-concept corpus AND the full 6000-step budget --
that IS the FULL dispatch; smoke's tiny V and step count cannot reproduce genuine coverage-ratio
or long-horizon convergence effects.

## Substrate-too-robust-for-default-regime / baseline-in-band

CHARPOS `ret_agree10` in smoke: seed_7=0.24, seed_13=0.2853 (well within (0.05,0.95)).
RANDOM_BLOCK `spearman_all` ~0.015-0.016 (near-zero, as expected -- calibration floor intact).

## Cell-template mandatory fields (declared)

- `arms_differ_verified: True` (sha256 over all code matrices; verified live in both smokes)
- `final_metrics_atomicity: tmp_replace` (inherited from `v3c._train_student_full` + this cell's
  own `write_metrics`/checkpoint `os.replace`)
- `except SystemExit: raise` before `except Exception` (no bare except, no `except BaseException`)
  -- grep-verified clean in both the core module and both wrapper files.
- `cell_chunked: True`, `start_marker_written: True`, `crash_diagnostic_present: True`,
  `heartbeat_present: True`, `defensive_error_checking: passed_all_4_patterns`
- `calibration_check: default_ok_for_this_regime` (identical hyperparameters to the validated v3c
  lineage; only step count, eval cadence, split methodology, headline-metric promotion, and
  verdict semantics differ)

## Timeout / dispatch estimate

v3c's own FULL run (1800 steps, 13 eval points, 10 units) landed in 182s (seed_7) /
275s (seed_13) on remote CUDA. This cell's FULL run is ~3.3x the steps (6000 vs 1800) and ~9x the
eval-point count (~120 vs 13); training cost scales roughly linearly with steps, eval cost is a
small fraction of total wall time per prior evidence. Estimated wall time: ~700-1000s (12-17 min)
per seed. Requested `--timeout 1800` (30 min), generous margin for GPU contention from the
concurrently-running v3c seed_23/29/31 replicate jobs.

## Composes with

- `T3/EXP_v3c_full_paired_rkd_only_seed_7/13` (the refuted 0.89 headline this cell re-examines
  under corrected methodology).
- `notes/encoder_rescue_plan_converged_diagnosis_2026-07-04.md` (v2's 0.368 collapse floor, the
  "bad" reference this cell's DECLINE_FINAL_BLOCK_CEILING is anchored against).

ASCII-only. No emojis. No em dashes.
