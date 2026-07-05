# Pre-reg: Encoder v9 -- minimum-density PIN (K256 control vs K455/11.11%-active), 2 seeds

Date: 2026-07-04. Author: exp_dev. Status: PRE-REGISTERED before dispatch.
Core cell: `experiments/exp_encoder_v9_k455_mindensity_paired_v1_core.py`
Per-seed wrappers (CHUNKED single-seed-per-cell): `..._seed_7.py`, `..._seed_13.py`
Anchors: `encoder_v9_k455_mindensity_paired_v1_seed7`, `..._seed13` (smoke suffix `_smoke`).
Parent cells (read-only imports, NOT edited): v3, v3c (same lineage as v5/v7/v8). `v3c._train_student_full`
reused VERBATIM (unmodified; kb/blk_l already parameters), identical low-risk posture to v5/v7/v8.

## Prior-work check (substrate concept-query, USER-locked 2026-07-01)

Query: "minimum density block code trained encoder retrieval agreement 0.35 target intermediate K
sparsity crossing operating point 11 percent active" -> top cosine=0.2754 (phase-portrait operating-point
note) + 0.252 (pc-sparsity prereg); NONE at cosine>0.30 for any DISTINCT prior cell training an
11.11%-active (blk_l=9) student. GENUINELY NOVEL: no prior cell trains a blk_l=9 student or pins the
0.35 crossing above 9.09%; v5/v7 touch power-of-2 blk_l only, v8 touched blk_l=11 (9.09%). This cell is
the sparser-than-K512 operating-point pin between v8's 9.09% and K512's 12.5%.

## Why this cell exists

The TRAINED density-vs-retrieval curve is now four landed points (FINAL-step, all VET'd):
- K128 (3.125%) 0.197 (v5 seed7) MEASURED@data/exp_encoder_v5_k256_capacity_paired_v1_seed7
- K256 (6.250%) 0.290/0.296 (v5/v8, HARD_PASS) MEASURED@data/exp_encoder_v5_..._seed7 + v8 seed7/13
- K372 (9.091%) 0.335/0.344 (v8, 2 seeds, MIDDLE_BAND -- JUST under 0.35) MEASURED@data/exp_encoder_v8_k372_mindensity_paired_v1_seed7/metrics.json + seed13
- K512 (12.5%)  0.414 (v7 seed7, HARD_PASS) MEASURED@data/exp_encoder_v7_k512_capacity_paired_v1_seed7

K372 (0.340 mean) is JUST below the 0.35 target; K512 (0.414) is above it -> the crossing is between
9.091% and 12.5%. Local slope over that segment = (0.414-0.340)/(0.125-0.09091) = 2.17 ret per unit
density (THEORETICAL), placing the crossing at ~9.55% active. This cell trains ONE intermediate arm at
11.11% active (blk_l=9) -- the sparsest integer-block-length code in the coordinator's 10.5-11% operating
band -- to CONFIRM that a code SPARSER than K512's 12.5% robustly clears 0.35, pinning the minimum-density
fallback OPERATING POINT for the USER's decision.

## Why K455/blk_l=9 (11.11%), not blk_l=10 (10.0%)

Integer blk_l constrains density to 1/blk_l, so the only feasible densities near the 10.5-11% band are
1/10=10.0% and 1/9=11.11% (no integer blk_l gives 10.7%). At the ~9.55% predicted crossing:
- blk_l=10 (10.0%): predicted ret = 0.340 + (0.10-0.09091)*2.17 = ~0.360 (THEORETICAL). Margin only 0.010
  above 0.35 -- given the ~0.005 landed seed spread, a MIDDLE_BAND (not-clear) outcome is a real risk.
- blk_l=9 (11.11%): predicted ret = 0.340 + (0.1111-0.09091)*2.17 = ~0.384 (THEORETICAL). Margin ~0.034
  -- a ROBUST clear. An OPERATING POINT should have margin (not sit at the cliff edge), so 11.11% is the
  right pin for a trustworthy min-density fallback. Confirms "the 0.35 crossing is at/below 11.11%."

## Tiling reality (why K=455)

A block code's active density is exactly 1/blk_l; total width = kb*blk_l. N_DIM=4096=2^12 has ONLY
power-of-2 divisors, so no block count tiles 4096 at an intermediate density -> PER-ARM widths:
- K256 control: kb=256, blk_l=16, width=4096, 6.250% active (EXACT v5/v8 regime; Gate-D positive control).
- K455 new:     kb=455, blk_l=9, width=4095, 11.111% active. kb=455 -> width 4095, within 1 dim (0.02%)
  of 4096 so the student MLP output width is materially identical to K256/K512's for capacity
  comparability. blk_l=9 is LARGER than K512's already-validated blk_l=8, so per-block binding SNR is
  HIGHER than K512's -- SBC algebra expected at least as safe (checked per arm, not assumed).

## What this cell answers

PRIMARY (gated): does K455_BLOCK_LAST FINAL-step ret_agree10 clear the 0.35 target?
- HARD_PASS `MINDENSITY_CLEARS_TARGET` iff `new_ret >= 0.35` AND `delta_hi80 >= -0.02` -- pins the
  min-density crossing to (9.091%, 11.111%]; the retrieval target is reachable at a code SPARSER than
  K512's 12.5%.
- MIDDLE_BAND `MINDENSITY_BELOW_TARGET` iff `new_ret < 0.35` (no calibration regression) -- locates the
  crossing above 11.11% (a useful lower bound).
- HARD_FAIL `MINDENSITY_REGRESSES_CALIBRATION` iff `delta_hi80 < -0.02` (checked FIRST).
- Per-arm HARD_FAIL `FALSE_WIN_ALGEBRA_LAST_STEP_{arm}` if either arm's keyed J=5 < 0.90.

## Compute architecture

Class (b) mixed: GPU-batched matmul training loop (`v3c._train_student_full`, REUSED VERBATIM),
sequential only in the outer per-arm/per-unit eval loop (2 arms x 9 units + shared CHARPOS = 19).
Storage: no_storage/no_composition beyond the single-hop keyed bind/unbind/cleanup integrity check.

## Functional requirements

| Requirement (plain English) | Existing primitive addressed by |
|---|---|
| Train in_batch-RKD-only student at NCE=0, two densities (6.25%, 11.11%) at PER-ARM widths | `v3c._train_student_full` (REUSED UNMODIFIED, kb/blk_l/width parameterized) |
| Reproduce v5/v8's K256 arm as an internal positive control before trusting K455 | paired K256 arm, same seed/data/mining/LR schedule as v5/v8 |
| Confirm 11.11% active clears 0.35 (sparser than K512's 12.5%) | K455 new arm, FINAL-step ret_agree10 vs 0.35 |
| Check the finer/intermediate code did not break SBC composability | per-arm `v3._keyed_unit`/shuffled-key at EACH arm's own block partition (blk_l=9 checked independently) |
| Avoid confounding with the orthogonal LR-schedule lever (v6) | UNCHANGED cosine-decay LR (same isolation v5/v7/v8 used) |

## Effective-vs-nominal parameter audit

`sweep_alignment_verdict: N/A_categorical_arm_not_numeric_sweep`. Two categorical arms differing ONLY in
(kb, blk_l, width). Both see the SAME mined positives/semi-hard candidates (teacher-cosine-derived,
width-independent) and the SAME initial batch sequence per seed. ret_agree10 is computed on the held set
in the arm's own code space (width-robust), so the 1-dim width difference (4096 vs 4095) does not bias
the comparison.

## Bracket-includes-discriminating-band

Not a numeric sweep; N/A for the 0.30-fraction gate. The single gated threshold (0.35) sits between the
flanking TRAINED points (v8's K372 0.340 just below, K512 0.414 above), so the discriminator brackets a
genuinely uncertain zone (the crossing), not a saturated extreme.

## Signal-shape compatibility audit

`v3c._train_student_full` (unmodified) -> this cell's eval/verdict code: SHAPE_MATCH, verified by
self-test (`_train_student_full` invoked at TWO DIFFERENT widths 256 and 252 on tiny synthetic data,
asserting returned diag + encoded-code shapes for both). SHAPE_DRIFT note: blk_l=9 is a new per-block
alphabet not previously trained in this lineage; the per-arm algebra check
(`FALSE_WIN_ALGEBRA_LAST_STEP_K455`) is the documented-risk guard.

## Positive-control reproduction (Gate D)

The K256 control arm IS the positive control: same seed=7/13, same data/split/mining/schedule as v5/v8 --
its own K256 numbers must land within tolerance of v5/v8's landed K256 (0.290/0.296) before the K455
delta is trusted. Additionally `v3._keyed_unit(f"{arm}_RANDOM_BLOCK", ...)` SBC-lossless posctrl
(`acc_at1 >= 0.98`) runs PER ARM. K256 is SHAPE_MATCH (identical regime to v5/v8); K455 is
`SHAPE_DRIFT_with_documented_risk` (blk_l=9 new alphabet; checked explicitly per arm).

## CRLB / capacity-feasibility

`crlb_floor_computed`: per-arm r_max via the SAME formula/anchor as the whole lineage (r_max =
sigma_teacher/sqrt(sigma_teacher^2 + 0.25/K), sigma_teacher from the K=128 anchor 0.901; self-test asserts
`_crlb_r_max(128)` reproduces 0.901 and `_crlb_r_max(455) > _crlb_r_max(256)`). `discriminator_reachability:
True`, SAME honest caveat as v7/v8 (formula's K counts block COUNT only, does not separately model blk_l;
the empirical FINAL-step result is the answer). The 0.35 target is well below every arm's CRLB ceiling.

## Pre-reg bands (HYPOTHESIZED, tagged)

- `RET_AGREE10_TARGET = 0.35` (HYPOTHESIZED@this prereg; the USER/coordinator retrieval target).
- `DELTA_HI80_COS_REGRESSION_FLOOR = -0.02` (same as v5/v7/v8; the sparser 11.11% code must not
  meaningfully cost semantic calibration vs the K256 control).
- `ALGEBRA_FLOOR = 0.90` (unchanged lineage convention), applied PER ARM.
- Predicted K455 FINAL ret_agree10 ~0.384 (THEORETICAL@interp), robust-clear (margin 0.034 above 0.35).

## HP_SCOPE

The target-clearing gate applies to `K455_BLOCK_LAST` FINAL-step only. `{arm}_*_BESTVAL` (on TEST) is
context, NOT separately gated (known early-checkpoint-inflation risk). `RANDOM_BLOCK`/`CHARPOS`/`shuffled_key`
are integrity-only (RANDOM_BLOCK and shuffled_key computed PER ARM since block partition/width differ;
CHARPOS computed once at the K=128 / N_DIM_REF=4096 reference).

## Cardinality

`EXPECTED_N_UNITS = 19` both run_modes (SMOKE=FULL code path): 2 arms x (semantic 4: DENSE/BLOCK x
LAST/BESTVAL + semantic RANDOM_BLOCK(1, arm-specific) + keyed RANDOM_BLOCK posctrl(1) + keyed LAST J5(1) +
keyed BESTVAL J5(1) + shuffled-LAST J5(1)) = 2 x 9 = 18, + shared CHARPOS semantic(1) = 19.

## Discriminator-survives-scale (option B, analytical)

Smoke (V_train=3000, 200 steps) validates MACHINERY ONLY: both arms train end-to-end at DIFFERENT widths
(4096 + 4095) with correctly-differing block partitions, per-arm RANDOM_BLOCK/algebra checks fire,
cardinality holds. Smoke's tiny V cannot reproduce the true near-neighbor coverage the 177899-concept
corpus tests, so "does 11.11% clear 0.35" is a FULL-only question. The REMOTE-QUEUE OFFICIAL LANDING is
canonical.

## Substrate-too-robust-for-default-regime / baseline-in-band

`baseline_in_band`: CHARPOS `ret_agree10` in (0.05, 0.95) verified at smoke. RANDOM_BLOCK `spearman_all`
near-zero for both arms (calibration floor intact at both widths).

## Cell-template mandatory fields (declared)

- `arms_differ_verified: True` (sha256 over all code matrices incl. per-arm RANDOM_BLOCK)
- `final_metrics_atomicity: tmp_replace` (inherited from v3c._train_student_full + write_metrics)
- `except SystemExit: raise` before `except Exception` (no bare except, no `except BaseException`) --
  grep-verified clean in the core module and both wrappers.
- `cell_chunked: True`, `start_marker_written: True`, `crash_diagnostic_present: True`,
  `heartbeat_present: True`, `defensive_error_checking: passed_all_4_patterns`
- `calibration_check: default_ok_for_this_regime` (identical hyperparameters to v5/v7/v8; only kb/blk_l/
  width differ between arms)
- `progress_logging: print_flush_true` (steps=6000)

## Determinism pinning

Identical to v5/v7/v8: `torch.use_deterministic_algorithms(True, warn_only=True)`, explicit
torch/numpy/python RNG seeding, fixed thread count, `CUBLAS_WORKSPACE_CONFIG`; `torch.__version__` + device
recorded into `metrics.json["determinism"]`. THE REMOTE-QUEUE OFFICIAL LANDING IS THE CANONICAL NUMBER;
local smoke is a MACHINERY gate only.

## Timeout / dispatch estimate

v8's FULL run (TWO arms, K256+K372, 6000 steps each, 19-unit battery) is the direct analog. v7 landed
338-345s; v8 comparable. K455's blk_l=9 gives marginally cheaper per-step matmuls than K512's blk_l=8, not
slower than v7/v8. Estimate ~350-400s per seed on GPU. `--timeout 3600` (1 hour, ~9x estimate), matching
v7/v8's margin. No `_n<N>` suffix so PROT-019 tiered floor does not apply; well under the PROT-021 14400s
checkpoint threshold (and the cell imports `_seed_checkpoint` anyway).

## Dispatch target

`overnight_queue` (GPU) -- real GPU training job (torch+cuda, satisfies the GPU-routing gate). Two per-seed
dispatches (chunked; runner death loses one seed only). Fills the currently-idle GPU per coordinator
PRIORITY-2 (2026-07-04).

## Composes with

- `T3/EXP_encoder_v5_k256_capacity_paired_v1` (K256 control reproduces this), the v7 K512 arm (above-target
  flank), and v8's K372 (the just-below flank); this cell pins the crossing to (9.091%, 11.111%].
- The regime-switch encoder work (dense-VALUE readout): this cell fixes the sparse-KEY density operating
  point that pairs with the calibrated dense value.

ASCII-only. No emojis. No em dashes.
