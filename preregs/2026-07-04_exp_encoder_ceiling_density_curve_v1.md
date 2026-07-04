# Pre-reg: Code-CEILING density curve (zero training), K=128..4096 at fixed N=4096

Date: 2026-07-04. Author: exp_dev. Status: PRE-REGISTERED before dispatch.
Core cell (single-file, no chunking, no seed wrappers -- deterministic given a fixed seed, zero
training, a crash costs nothing to retry): `experiments/exp_encoder_ceiling_density_curve_v1_core.py`
Anchor: `encoder_ceiling_density_curve_v1` (smoke suffix `_smoke`).
Parent cells (read-only import, NOT edited): `exp_encoder_migration_step1b_v3_..._core.py` (v3,
quantizer/eval-unit machinery) and `exp_encoder_teacher_sparsifier_bypass_v1_core.py` (bypass_v1,
fixed-lift helpers reused verbatim: `_make_ortho_isometric`, `_make_random_gaussian`,
`_verify_isometry`, `_FrozenLinearEncoder`).

## Prior-work check (substrate concept-query, USER-locked 2026-07-01)

Query: "retrieval density curve block count K phase diagram active sparsity code ceiling algebra
roundtrip coarse semantic hi80" -> top hit cosine=0.2483 (generic sparse-Hopfield/compressed-sensing
literature notes, not an arc cell), next hits 0.2471/0.2441/0.2402/0.2393 (same family). NONE at
cosine>0.30. GENUINELY NOVEL: no prior cell maps the FIXED-total-width (N=4096) K-density ceiling
curve across all four axes (retrieval + coarse-semantic + algebra + sparsity) in one place.

## Why this cell exists

USER spotted a non-monotonic pattern in landed data: RAW_CONTINUOUS (fully dense, float,
MEASURED@data/exp_encoder_retrieval_regime_density_curve_v1/metrics.json) `ret_agree10`=0.169 <
TRAINED K128-block (3.1%)=0.20 < TRAINED K256-block (6.25%)=0.29 -- there is a PEAK somewhere on the
density axis between K128 and fully-dense that has not been mapped. The sibling bypass_v1 cell
already measured the zero-training CEILING at K128/K256 (0.43/0.55, at a DIFFERENT total width
per-K, MEASURED@data/exp_encoder_teacher_sparsifier_bypass_v1/metrics.json), establishing retrieval
is training-fidelity-bound not code-bound at K128 (ceiling 0.43 > 0.35 target). This cell extends
that ceiling to the FULL K-density axis (128/256/512/1024/2048/4096) AT A FIXED TOTAL WIDTH (matching
the TRAINED curve's own regime, N=4096 constant, only block-count/blk_l varies) -- answering (1)
does the ceiling itself PEAK or keep climbing past K256, and (2) at what K does keyed@J5 SBC
algebra first degrade below ~0.95 (the complementary axis neither v7 [[training, not ceiling]] nor
bypass_v1 [[only K128/256]] covers).

Coordinator-approved 2026-07-04 as the complementary lane to v7 (K512 trained-curve, in flight) and
the separately-routed student-capacity/training-gap probe -- this cell does NOT retrain anything and
does NOT duplicate either.

## Design

Fixed (non-learned) linear lifts from teacher-dim (1024) to a FIXED N_DIM=4096 continuous space
(`ORTHO_ISOMETRIC`: QR-orthonormal, W.T@W=I exactly, zero info loss pre-quantization -- the CODE-
CAPACITY CEILING; `RANDOM_GAUSSIAN`: untrained-network proxy, kept for parity with bypass_v1). BOTH
lifts share the SAME out_dim=4096 regardless of K -- unlike bypass_v1 (which varied total width
K128@4096 vs K256@8192), this cell holds width FIXED and re-quantizes the SAME continuous lift at
six different (kb, blk_l) pairs, all tiling N_DIM=4096 exactly: K in {128/blk_l32, 256/blk_l16,
512/blk_l8, 1024/blk_l4, 2048/blk_l2, 4096/blk_l1}. K=4096/blk_l=1 is the DENSE-SIGN endpoint
(block-argmax degenerates to per-dimension sign quantization); the UN-quantized lift output itself
(`RAW_ISOMETRIC`) is the DENSE-FLOAT endpoint.

Reuses `v3._encode_hard_block` (quantizer), `v3._semantic_unit` (retrieval/coarse-semantic), and
`v3._keyed_unit` (algebra, J=5, `algebra="sbc"`) VERBATIM -- no reimplementation, no risk of a
subtly-different quantizer/eval producing an apples-to-oranges number vs the landed v5/v6/v7/bypass_v1
cells.

## Verdict semantics

DIAGNOSTIC (no HARD_PASS/HARD_FAIL bar), same precedent as bypass_v1 and the sibling density_curve
cell: `verdict: "DIAGNOSTIC_COMPLETE"`. Reported per-K in `ceiling_curve[]`: `K`, `blk_l`,
`active_pct` (=100*K/4096, exact by construction), `ret_agree10`, `hi80_cos`, `hi80_calib_err`,
`spearman_all`, `keyed_j5_acc_at1`, `keyed_j5_snr_margin`. Plus `raw_isometric`/`raw_random` (the
dense-float endpoint) and `charpos` (fixed K=128 reference control).

Two questions this pre-reg commits to answering explicitly in the completion report (coordinator ask):
1. Does `ceiling_curve[].ret_agree10` PEAK at some K<4096 or keep RISING through K=4096? (bounds
   max-achievable retrieval at ANY density if it plateaus; if it keeps rising, the sparsity-vs-
   retrieval tradeoff is reframed.)
2. At what K does `keyed_j5_acc_at1` FIRST drop below 0.95 (evaluated against the FULL n_test=17790
   candidate pool, not smoke's n_test=800 -- smoke already shows acc_at1=1.0 at ALL K including
   K=4096, but snr_margin_mean monotonically shrinks 0.268->0.138 from K128->K4096, so degradation at
   the much larger FULL candidate pool is plausible and the reason this axis needs the FULL run, not
   just smoke, to answer).

## Compute architecture

Class (a) batched (all matmuls; no sequential loops); zero training (no optimizer, no gradient
steps, no checkpoints). Storage strategy: no_storage/no_composition beyond the keyed-unit integrity
check (single-hop bind/unbind, not chained composition).

## Functional requirements

| Requirement (plain English) | Existing primitive addressed by |
|---|---|
| Measure the zero-training ceiling at 6 K's sharing ONE total width | fixed isometric/random lift (out_dim=4096 constant) + `v3._encode_hard_block` (reused verbatim) |
| Confirm this reproduces bypass_v1's K128/K256 ceiling before trusting new K's | internal consistency check vs MEASURED@data/exp_encoder_teacher_sparsifier_bypass_v1/metrics.json (ortho_k128=0.4295, ortho_k256=0.5486) |
| Measure algebra ceiling (does bigger K break SBC bind/unbind) at every K | `v3._keyed_unit` (J=5, sbc), one call per K, INCLUDING the blk_l=1 edge case (verified in self-test: bind/unbind degenerates to elementwise sign-multiply via length-1 circular convolution, algebraically sound, not a crash risk) |
| Report sparsity cost of the peak | `active_pct = 100*K/N_DIM`, exact by construction |

## Effective-vs-nominal parameter audit / bracket / signal-shape

Categorical K-sweep (6 values), not a numeric-continuous sweep; `sweep_alignment_verdict:
N/A_categorical_arm_not_numeric_sweep`. All 6 K's share the SAME `in_dim=1024 -> out_dim=4096` lift
(built ONCE per lift-type); only `(kb, blk_l)` passed to `_encode_hard_block` differs, and
`kb*blk_l==4096` is asserted at import time for all 6 (self-test re-checks defensively). Signal-shape
(Gate C): teacher embeddings [n,1024] -> `_FrozenLinearEncoder` [n,4096] -> `v3._encode_hard_block`
[n,4096] (reshaped internally per-K to [n,kb,blk_l]): SHAPE_MATCH, verified live (27/27 units landed
in self-test smoke drive with correct per-K shapes).

## Positive control / integrity (Gate D-adjacent)

This cell's OWN K128/K256 ORTHO arms are the positive control: MUST reproduce bypass_v1's landed
K128=0.4295/K256=0.5486 `ret_agree10` (within tolerance, same seed=7, same `_encode_hard_block` path,
same FULL n_test/n_pairs formula) before the NEW K512/1024/2048/4096 points are trusted. Declared
here; checked in the completion report against the landed FULL metrics.json (not assumed).
`RANDOM_BLOCK_K{kb}` (fully random per-K control, no teacher info) is the calibration floor at every
K; `CHARPOS` (fixed K=128 reference) is the cross-cell baseline-in-band check.

## CRLB / capacity-feasibility

`crlb_n_a`: declared explicitly (not silently omitted) -- zero-training linear-algebra diagnostic;
the learned-map CRLB formula does not govern a fixed isometric/random lift.

## Baseline-in-band

SMOKE VERIFIED (2026-07-04): CHARPOS `ret_agree10`=0.1886 (within (0.05,0.95)); all 6
`RANDOM_BLOCK_K{kb}` spearman near-zero (0.0006 to 0.0133, calibration floor intact at every K).

## Cell-template mandatory fields (declared)

- `arms_differ_verified: True` (sha256 over all 22 code matrices incl. per-K RANDOM_BLOCK; verified
  live in smoke, no exemptions needed)
- `final_metrics_atomicity: tmp_replace`
- `except SystemExit: raise` before `except Exception` (no bare except, no `except BaseException`)
  -- grep-verified clean.
- `cell_chunked: False` (single deterministic pass, zero training, a crash costs nothing to retry),
  `start_marker_written: True`, `crash_diagnostic_present: True`, `heartbeat_present: True`,
  `defensive_error_checking: passed_all_4_patterns`
- `calibration_check: default_ok_for_this_regime` (reuses the SAME `_encode_hard_block`/`_keyed_unit`
  channels validated throughout this lineage; only kb/blk_l vary, always tiling N_DIM=4096)
- `progress_logging: print_flush_true`

## Discriminator-survives-scale

N/A in the usual training sense -- no training to saturate; the SAME closed-form computation runs
identically at smoke (local 43905-concept cache, n_test=800) and full (177899-concept cache,
n_test=17790) scale, differing only in V/n_pairs/n_trials. SMOKE=FULL code path by construction.
SMOKE VERIFIED (2026-07-04, `.venv`, CPU, self-test): 27/27 units, `cardinality_ok=true`,
`arms_differ_verified=true`, `unit_failures=[]`, elapsed=17.9s. Illustrative smoke-scale numbers
(NOT the certified FULL answer -- smoke's tiny V=800 does not stress capacity, so the smoke curve is
monotonically RISING through K=4096 with no peak; this is EXPECTED per bypass_v1's own smoke-vs-FULL
gap and is exactly why the FULL landing, not smoke, answers the peak-location question):
`ORTHO_K128=0.5958, K256=0.6752, K512=0.7521, K1024=0.8052, K2048=0.8491, K4096=0.8550`;
`RAW_ISOMETRIC=1.0000` (trivial by construction -- isometry preserves inner-product ranking exactly
pre-quantization); keyed J5 `acc_at1=1.0` at ALL 6 K's at smoke scale (n_test=800), but
`snr_margin_mean` monotonically shrinks `0.2676 (K128) -> 0.2508 -> 0.2191 -> 0.2054 -> 0.1523 ->
0.1379 (K4096)` -- margin erosion visible even though accuracy hasn't broken yet at this small
candidate pool; the FULL run's much larger n_test=17790 candidate pool is the real test of whether
this erosion crosses the acc_at1<0.95 line at some K.

## Timeout / dispatch estimate

Zero training; cost is 2 lifts (built once) + 6 quantize passes + 27 eval units (21 semantic + 6
keyed) at V up to 177899, n_test up to 17790, n_pairs up to 400000. Sibling bypass_v1's comparable
FULL run (SAME regime, 8 units) MEASURED 138.26s on CPU
(MEASURED@data/exp_encoder_teacher_sparsifier_bypass_v1/metrics.json:elapsed_s). Scaling linearly by
unit count (27/8 x 138.26s = 466.7s) plus a small per-K overhead (6 quantize passes vs bypass_v1's 4,
negligible relative to eval cost): estimated 470-600s. Formula:
`timeout_s = ceil(1.5 * 466.7) = 701`. Requesting `--timeout 1800` (>3x estimate), matching
bypass_v1's own revised margin (remote-CPU-speed never independently benchmarked against this
laptop's smoke timing).

## Dispatch target

`remote_cpu_queue` (idle at author time; GPU queue is running the v7 K512 FULL trained-curve pair --
this cell has zero use for a GPU, per the SAME device='cpu'-pinned-by-default convention as
bypass_v1, avoiding any device-mismatch class of bug).

## Composes with

- `experiments/exp_encoder_teacher_sparsifier_bypass_v1_core.py` (K128/K256 ceiling this cell
  reproduces as positive control, then extends to K512/1024/2048/4096).
- `experiments/exp_encoder_retrieval_regime_density_curve_v1_core.py` (RAW_CONTINUOUS/DENSE_SIGN
  TRAINED dense-endpoint numbers this cell's `raw_isometric`/K4096-ceiling numbers bound from above).
- `experiments/exp_encoder_v5_k256_capacity_paired_v1_core.py` /
  `exp_encoder_v6_k256_plateau_followup_v1_core.py` / `exp_encoder_v7_k512_capacity_paired_v1_core.py`
  (the TRAINED half of the same K-density curve; this cell supplies the CEILING half only, no new
  training).
- `notes/encoder_rescue_plan_converged_diagnosis_2026-07-04.md` (R5 K-capacity diagnostic family).

ASCII-only. No emojis. No em dashes.
