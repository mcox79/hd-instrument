# Pre-reg: Encoder v8 -- minimum-density paired test (K256 control vs K372/9.09%-active), 2 seeds

Date: 2026-07-04. Author: exp_dev. Status: PRE-REGISTERED before dispatch.
Core cell: `experiments/exp_encoder_v8_k372_mindensity_paired_v1_core.py`
Per-seed wrappers (CHUNKED single-seed-per-cell): `..._seed_7.py`, `..._seed_13.py`
Anchors: `encoder_v8_k372_mindensity_paired_v1_seed7`, `..._seed13` (smoke suffix `_smoke`).
Parent cells (read-only imports, NOT edited): v3, v3c (same lineage as v5/v7). `v3c._train_student_full`
reused VERBATIM (unmodified; kb/blk_l already parameters), identical low-risk posture to v5/v7.

## Prior-work check (substrate concept-query, USER-locked 2026-07-01)

Query: "minimum density block code trained encoder retrieval agreement 0.35 target intermediate K
sparsity crossing paired" -> top hits are this arc's own v5/v7/density-curve prose (expected self-
similarity, same lineage), all cosine<=0.30 for any DISTINCT prior cell training an intermediate-
density (non-power-of-2-blk_l) arm. NONE at cosine>0.30. GENUINELY NOVEL: no prior cell trains a
blk_l=11 / 9.09%-active student or searches for the minimum density that clears 0.35; v5 (K128/K256)
and v7 (K256/K512) only touch power-of-2 blk_l.

## Why this cell exists

The TRAINED density-vs-retrieval curve is now monotone-RISING (v5/v7, both HARD_PASS, VET'd):
K128 (3.125%) ret_agree10 ~0.197/0.198 -> K256 (6.25%) ~0.290/0.296 -> K512 (12.5%) ~0.414/0.415
(MEASURED@data/exp_encoder_v5_..._seed7/metrics.json and data/exp_encoder_v7_..._seed7/metrics.json).
K256 (0.29) is BELOW the 0.35 retrieval target; K512 (0.414) is ABOVE it. Linear interpolation in
density places the 0.35 crossing at ~9.3% active
(THEORETICAL@(0.35-0.29)/(0.414-0.29)*(0.125-0.0625)+0.0625). This cell trains ONE intermediate-
density arm at that predicted crossing to find the MINIMUM density (minimum sparsity cost) that
clears 0.35 -- i.e. "can we hit the retrieval target at a code SPARSER than K512's 12.5%, and how
sparse."

## Tiling reality (why K=372, not a round 384)

A block code's active density is exactly 1/blk_l; total width = kb*blk_l. N_DIM=4096=2^12 has ONLY
power-of-2 divisors, so the ONLY block counts tiling 4096 exactly are 128/256/512/1024 (densities
3.125/6.25/12.5/25%). There is NO block count in [320,448] that tiles 4096 -- an intermediate density
REQUIRES a non-4096 width. So this cell uses PER-ARM widths:
- K256 control: kb=256, blk_l=16, width=4096, 6.250% active (EXACT v5 regime; Gate-D positive control).
- K372 new:     kb=372, blk_l=11, width=4092, 9.091% active. blk_l=11 is the integer per-block alphabet
  whose density 1/11=9.09% sits at the predicted crossing; kb=372 -> width 4092, within 4 dims (0.1%)
  of 4096 so the student's MLP output width is materially identical to K256/K512's for capacity
  comparability. blk_l=11 is LARGER than K512's already-validated blk_l=8, so per-block binding SNR is
  HIGHER than K512's -- SBC algebra expected at least as safe (checked per arm, not assumed).

## What this cell answers

PRIMARY (gated): does K372_BLOCK_LAST FINAL-step ret_agree10 clear the 0.35 target?
- HARD_PASS `MINDENSITY_CLEARS_TARGET` iff `new_ret >= 0.35` AND `delta_hi80 >= -0.02`.
- MIDDLE_BAND `MINDENSITY_BELOW_TARGET` iff `new_ret < 0.35` (still no calibration regression) -- a
  useful lower bound locating the crossing between 9.09% and 12.5%.
- HARD_FAIL `MINDENSITY_REGRESSES_CALIBRATION` iff `delta_hi80 < -0.02` (checked FIRST).
- Per-arm HARD_FAIL `FALSE_WIN_ALGEBRA_LAST_STEP_{arm}` if either arm's keyed J=5 < 0.90.

## Compute architecture

Class (b) mixed: GPU-batched matmul training loop (`v3c._train_student_full`, REUSED VERBATIM),
sequential only in the outer per-arm/per-unit eval loop (2 arms x 9 units + shared CHARPOS = 19).
Storage: no_storage/no_composition beyond the single-hop keyed bind/unbind/cleanup integrity check.

## Functional requirements

| Requirement (plain English) | Existing primitive addressed by |
|---|---|
| Train in_batch-RKD-only student at NCE=0, two densities (6.25%, 9.09%) at PER-ARM widths | `v3c._train_student_full` (REUSED UNMODIFIED, kb/blk_l/width parameterized) |
| Reproduce v5's K256 arm as an internal positive control before trusting K372 | paired K256 arm, same seed/data/mining/LR schedule as v5 |
| Find whether 9.09% active clears 0.35 (sparser than K512's 12.5%) | K372 new arm, FINAL-step ret_agree10 vs 0.35 |
| Check the finer/intermediate code did not break SBC composability | per-arm `v3._keyed_unit`/shuffled-key at EACH arm's own block partition (blk_l=11 checked independently) |
| Avoid confounding with the orthogonal LR-schedule lever (v6) | UNCHANGED cosine-decay LR (same isolation v5/v7 used) |

## Effective-vs-nominal parameter audit

`sweep_alignment_verdict: N/A_categorical_arm_not_numeric_sweep`. Two categorical arms differing ONLY
in (kb, blk_l, width). Both see the SAME mined positives/semi-hard candidates (teacher-cosine-derived,
width-independent) and the SAME initial batch sequence per seed. The metric ret_agree10 is computed on
the held set and is width-robust (cosine over the arm's own code space), so the 4-dim width difference
(4096 vs 4092) does not bias the comparison.

## Bracket-includes-discriminating-band

Not a numeric sweep; N/A for the 0.30-fraction gate. The single gated threshold (0.35) sits between the
two flanking TRAINED points (K256 0.29 below, K512 0.414 above), so the discriminator brackets a
genuinely uncertain zone (the crossing) rather than being saturated at either extreme.

## Signal-shape compatibility audit

`v3c._train_student_full` (unmodified) -> this cell's eval/verdict code: SHAPE_MATCH, verified by
self-test (`_train_student_full` invoked at TWO DIFFERENT widths 256 and 252 on tiny synthetic data,
asserting returned diag dict + encoded-code shapes for both widths). SHAPE_DRIFT note: blk_l=11 is a
new per-block alphabet not previously trained in this lineage; the per-arm algebra check
(`FALSE_WIN_ALGEBRA_LAST_STEP_K372`) is the documented-risk guard.

## Positive-control reproduction (Gate D)

The K256 control arm IS the positive control: same seed=7/13, same data/split/mining/schedule as v5 --
its own K256 numbers must land within tolerance of v5's landed K256 (0.290/0.296) before the K372
delta is trusted. Additionally `v3._keyed_unit(f"{arm}_RANDOM_BLOCK", ...)` SBC-lossless posctrl
(`acc_at1 >= 0.98`) runs PER ARM. K256 is SHAPE_MATCH (identical regime to v5); K372 is
`SHAPE_DRIFT_with_documented_risk` (blk_l=11 new alphabet; checked explicitly per arm). SMOKE VERIFIED
(2026-07-04): both arms' RANDOM_BLOCK posctrl `acc_at1=1.0` and BLOCK_LAST keyed J5 `acc_at1=1.0`,
shuffled-key leak 0.0 at smoke scale (seed7); K256 arm's smoke numbers match v7's own K256 smoke arm
(both smoke-scale machinery, not a FULL repro claim -- that check is at FULL landing).

## CRLB / capacity-feasibility

`crlb_floor_computed`: per-arm r_max via the SAME formula/anchor as the whole lineage (r_max =
sigma_teacher/sqrt(sigma_teacher^2 + 0.25/K), sigma_teacher from the K=128 anchor 0.901; self-test
asserts `_crlb_r_max(128)` reproduces 0.901 and `_crlb_r_max(372) > _crlb_r_max(256)`).
`discriminator_reachability: True`, with the SAME honest caveat as v7 (this formula's K counts block
COUNT only, does not separately model blk_l; the empirical FINAL-step result, not the closed form, is
the answer). The 0.35 target is well below every arm's CRLB ceiling, so it is reachable in principle.

## Pre-reg bands (HYPOTHESIZED, tagged)

- `RET_AGREE10_TARGET = 0.35` (HYPOTHESIZED@this prereg; the USER/coordinator retrieval target the
  trained curve approaches from below).
- `DELTA_HI80_COS_REGRESSION_FLOOR = -0.02` (same as v5/v7; the sparser 9.09% code must not
  meaningfully cost semantic calibration vs the K256 control).
- `ALGEBRA_FLOOR = 0.90` (unchanged lineage convention), applied PER ARM.

## HP_SCOPE

The target-clearing gate applies to `K372_BLOCK_LAST` FINAL-step only. `{arm}_*_BESTVAL` (on TEST) is
context, NOT separately gated (KNOWN early-checkpoint-inflation risk per v3e/v5's ~8%-into-training
bestval_step findings). `RANDOM_BLOCK`/`CHARPOS`/`shuffled_key` are integrity-only (RANDOM_BLOCK and
shuffled_key computed PER ARM since block partition/width differ; CHARPOS computed once at the K=128 /
N_DIM_REF=4096 reference).

## Cardinality

`EXPECTED_N_UNITS = 19` both run_modes (SMOKE=FULL code path): 2 arms x (semantic 4:
DENSE/BLOCK x LAST/BESTVAL + semantic RANDOM_BLOCK(1, arm-specific) + keyed RANDOM_BLOCK posctrl(1) +
keyed LAST J5(1) + keyed BESTVAL J5(1) + shuffled-LAST J5(1)) = 2 x 9 = 18, + shared CHARPOS
semantic(1) = 19. SMOKE VERIFIED: 19/19 units, cardinality_ok=true.

## Discriminator-survives-scale (option B, analytical)

Smoke (V_train=3000, 200 steps) validates MACHINERY ONLY: both arms train end-to-end at DIFFERENT
widths (4096 + 4092) with correctly-differing block partitions, per-arm RANDOM_BLOCK/algebra checks
fire, cardinality holds. SMOKE VERIFIED (2026-07-04, local CPU): seed_7 HARD_PASS `elapsed_s=99.2`;
19/19 units, `arms_differ_verified=True`, no exemptions; K372 BLOCK keyed J5 acc_at1=1.0 (algebra safe
at blk_l=11 as predicted). Smoke's tiny V=3000 cannot reproduce the true near-neighbor coverage effect
the 177899-concept corpus tests, so the "does 9.09% clear 0.35" question is a FULL-only question. The
REMOTE-QUEUE OFFICIAL LANDING is canonical.

## Substrate-too-robust-for-default-regime / baseline-in-band

CHARPOS `ret_agree10` in smoke: 0.2467, well within (0.05, 0.95). RANDOM_BLOCK `spearman_all` near-zero
for both arms (calibration floor intact at both widths).

## Cell-template mandatory fields (declared)

- `arms_differ_verified: True` (sha256 over all code matrices incl. per-arm RANDOM_BLOCK; verified live
  in smoke, no exemptions needed)
- `final_metrics_atomicity: tmp_replace` (inherited from v3c._train_student_full + write_metrics)
- `except SystemExit: raise` before `except Exception` (no bare except, no `except BaseException`) --
  grep-verified clean in the core module and both wrappers.
- `cell_chunked: True`, `start_marker_written: True`, `crash_diagnostic_present: True`,
  `heartbeat_present: True`, `defensive_error_checking: passed_all_4_patterns`
- `calibration_check: default_ok_for_this_regime` (identical hyperparameters to v5/v7; only
  kb/blk_l/width differ between arms)
- `progress_logging: print_flush_true` (steps=6000 >= the 1800s/30min threshold)

## Determinism pinning

Identical to v5/v7: `torch.use_deterministic_algorithms(True, warn_only=True)`, explicit
torch/numpy/python RNG seeding, fixed thread count, `CUBLAS_WORKSPACE_CONFIG`; `torch.__version__` +
device recorded into `metrics.json["determinism"]`. THE REMOTE-QUEUE OFFICIAL LANDING IS THE CANONICAL
NUMBER; local smoke is a MACHINERY gate only (`metrics.json["canonical_source"]`).

## Timeout / dispatch estimate

v7's FULL run (TWO arms, K256+K512, 6000 steps each, 19-unit eval battery) landed in 338-345s on remote
CUDA (MEASURED@data/exp_encoder_v7_..._seed7/metrics.json:elapsed_s ~338.5). This cell trains TWO arms
at the same step count/batch/eval-battery (K372's blk_l=11 gives marginally cheaper per-step matmuls
than K512's, not slower than v7). Estimate ~350-400s per seed on GPU. Formula: `ceil(1.5 * 400) = 600`.
Requested `--timeout 3600` (1 hour, ~9x estimate), matching v7's margin, consistent with this lineage's
GPU-is-fast track record.

## Dispatch target

`overnight_queue` (GPU) -- real GPU training job (torch+cuda, satisfies the GPU-routing gate). Queues
BEHIND the priority lever-B probe (encoder_v6_annealed_ste_fidelity_k128_v1, coordinator-confirmed
queued 2026-07-04) so it backfills the GPU without front-running the priority. Two per-seed dispatches
(chunked; runner death loses one seed only).

## Composes with

- `T3/EXP_encoder_v5_k256_capacity_paired_v1` (K256 control reproduces this) and the v7 K512 arm (the
  above-target flank); this cell finds the crossing between them.
- `experiments/exp_encoder_ceiling_density_curve_v1_core.py` (the zero-training CEILING curve at the
  same densities; this cell supplies the TRAINED intermediate point the ceiling curve cannot).
- `notes/encoder_rescue_plan_converged_diagnosis_2026-07-04.md` (R5 K-capacity diagnostic family).

ASCII-only. No emojis. No em dashes.
