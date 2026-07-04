# Pre-reg: Encoder v5 -- K=128 vs K=256 code-capacity paired test (2 seeds)

Date: 2026-07-04. Author: exp_dev. Status: PRE-REGISTERED before dispatch.
Core cell: `experiments/exp_encoder_v5_k256_capacity_paired_v1_core.py`
Per-seed wrappers (CHUNKED single-seed-per-cell): `experiments/exp_encoder_v5_k256_capacity_paired_v1_seed_7.py`, `..._seed_13.py`
Anchors: `encoder_v5_k256_capacity_paired_v1_seed7`, `..._seed13` (smoke suffix `_smoke` on each).
Parent cells (read-only imports, NOT edited): v3, v3c (same as the whole lineage). `v3c._train_student_full` is reused VERBATIM (unmodified) -- `kb`/`blk_l` are already parameters, so no new training-loop code is needed for this cell.

## Prior-work check (substrate concept-query, USER-locked 2026-07-01)

Query: "K256 block code capacity paired comparison retrieval agreement trained encoder versus K128
code resolution ceiling" -> top hit cosine=0.2841 (this arc's own v3c/v3e prose, expected
self-similarity), the bypass-diagnostic cell's own prose at cosine=0.29 (expected -- same arc,
distinct cell: zero-training vs trained). NONE at cosine>0.30 for a distinct prior TRAINED cell.
GENUINELY NOVEL: no prior cell in this lineage trains a K=256 student and compares it against K=128
under matched conditions.

## Why this cell exists

v3e (FULL, seed=7, K=128) landed `final_ret_agree10=0.2112`, `final_hi80_cos=0.8320`
MEASURED@data/exp_encoder_v3e_decline_vs_plateau_v1_seed7/metrics.json -- weak retrieval despite
near-goal calibration. A zero-training bypass diagnostic (teacher-through-sparsifier,
`experiments/exp_encoder_teacher_sparsifier_bypass_v1_core.py`, commit e5a084fbe) suggested K=128
caps ~0.80 Spearman and K=256 reaches ~0.89 (+0.09) HYPOTHESIZED-CONTEXT@this session's spawn prompt
(cited by the coordinator, not independently re-verified from disk by this cell). This cell asks the
real question directly: does that analytical-ceiling gap survive into a GENUINELY TRAINED model's
retrieval quality?

## What this cell answers

Two PAIRED arms (same seed/data/split/mining/objective, differing ONLY in block-code resolution)
inside ONE process: `K128` (kb=128, blk_l=32, matches the whole prior lineage) vs `K256` (kb=256,
blk_l=16, the bypass-diagnostic's better arm). Both use the UNCHANGED cosine-decay-to-0 LR schedule
(v3e's schedule) -- deliberately kept SEPARATE from the sibling v4 cell's unvalidated plateau-hold LR
lever, so this K-sweep is not confounded by an unvalidated convergence fix. If K256 lifts
`ret_agree10` with no calibration regression, code resolution is a genuine, orthogonal lever from the
convergence question. If it does not, K is not the (or not the only) bottleneck.

Note on the 2%-sparsity tension (flagged, not blocking): K=256 (6.25% active) moves AWAY from
`director_plan.json`'s ~2%-sparsity encoder goal (k~82/N=4096), not toward it. This cell tests the
explicitly-requested K=128-vs-K=256 comparison (a resolution/capacity question); if K=256 lifts
retrieval, the strategic tradeoff (denser code needed for capacity vs the 2% goal) is a separate
USER/Research-level decision this cell surfaces but does not resolve.

## Compute architecture

Class (b) mixed-with-justification: GPU-batched matmul training loop (`v3c._train_student_full`,
REUSED VERBATIM, unmodified), sequential-only in the outer per-arm/per-unit eval loop (2 arms x 9
units + 1 shared CHARPOS = 19 total, each a batched cleanup-argmax or block-encode over the
codebook). Storage strategy: no_storage/no_composition beyond the existing bind/unbind/cleanup
keyed-unit check (single-hop).

## Functional requirements

| Requirement (plain English) | Existing primitive addressed by |
|---|---|
| Train in_batch-RKD-only student at NCE=0, two K values | `v3c._train_student_full` (REUSED UNMODIFIED, `kb`/`blk_l` parameterized) |
| Test whether finer code lifts retrieval under real training | paired K128 vs K256 arms, same seed/data/mining/LR schedule |
| Check the finer code did not break SBC composability | per-arm `v3._keyed_unit`/shuffled-key at EACH arm's own block partition (K256's blk_l=16 checked independently, not assumed to inherit K128's algebra floor) |
| Report the metric that actually matters | FINAL-step `ret_agree10`/`hi80_cos` delta is the PRIMARY gated comparison |
| Avoid confounding with the unvalidated LR-schedule fix | UNCHANGED cosine-decay LR (sibling v4 cell owns the LR-schedule question) |

## Effective-vs-nominal parameter audit

Swept "parameter" is K (categorical: 128 vs 256), not a numeric sweep axis over many values.
`sweep_alignment_verdict: N/A_categorical_arm_not_numeric_sweep`. Both arms see the SAME mined
positives/semi-hard candidates (teacher-cosine-derived, independent of block partition) and the SAME
initial batch sequence per-arm (via `seed`) -- the ONLY thing that differs is `kb`/`blk_l` (hence the
block-STE quantization granularity), so this is a true paired test of K alone.

## Bracket-includes-discriminating-band

Not a numeric sweep; N/A. `DELTA_RET_AGREE10_HARD_PASS_MIN=0.03` sits in a genuine middle region
(`(0, 0.03)` -> MIDDLE_BAND marginal-lift), so the discriminator brackets an uncertain zone rather
than being saturated at either extreme.

## Signal-shape compatibility audit

`v3c._train_student_full` (unmodified) -> this cell's eval/verdict code: SHAPE_MATCH, verified by
this cell's self-test (`_train_student_full` invoked at 2 distinct K values on tiny synthetic data,
asserting the returned `diag` dict and encoded-code shapes match expectations for BOTH K values).

## Positive-control reproduction (Gate D)

`v3._keyed_unit(f"{arm}_RANDOM_BLOCK", "sbc", ..., J=5, ...)` -- SBC-lossless sanity (`acc_at1 >=
0.98`) run PER ARM at that arm's own `kb`/`blk_l`, not just once at K=128. This is the SAME primitive
already validated in v3/v3b/v3c/v3e at K=128; for K=256 it is a genuine regime-extension check
(`regime_extension_audit: SHAPE_MATCH` for K128 -- identical regime; `SHAPE_DRIFT_with_documented_
risk` for K256 -- smaller blk_l=16 could plausibly reduce per-block SNR margin for bind/unbind, which
is exactly why this cell checks it explicitly per arm rather than assuming K128's floor transfers).
SMOKE VERIFIED (2026-07-04): both arms' RANDOM_BLOCK posctrl `acc_at1=1.0` at smoke scale, both seeds.

## CRLB / capacity-feasibility

`crlb_floor_computed`: K128 `r_max=0.901` (THEORETICAL@v2/v3/v3b/v3c/v3e, unchanged). K256
`r_max` computed via the SAME formula (`r_max = sigma_teacher / sqrt(sigma_teacher^2 + 0.25/K)`) with
`sigma_teacher` backed out from the K128 anchor (self-test asserts `_crlb_r_max(128)` reproduces
0.901 to 1e-3) -- K256's ceiling is on the SAME theoretical footing, not a fresh unrelated estimate.
`discriminator_reachability: True` (the `DELTA_RET_AGREE10_HARD_PASS_MIN=0.03` band is a retrieval-
agreement delta, not itself bounded by the Spearman-domain CRLB, but the underlying code-fidelity
ceiling genuinely rises from K128 to K256 per the formula, which is the physical basis for expecting
ANY positive delta to be possible).

## Pre-reg bands (HYPOTHESIZED, tagged)

- `DELTA_RET_AGREE10_HARD_PASS_MIN = 0.03` HYPOTHESIZED@this prereg -- the bypass diagnostic's +0.09
  figure is a DIFFERENT metric (Spearman) on an UNTRAINED path, not directly portable to a
  `ret_agree10` margin, so this band is a conservative, independently-chosen threshold rather than a
  reuse of that number.
- `DELTA_HI80_COS_REGRESSION_FLOOR = -0.02` HYPOTHESIZED@this prereg (K256 must not meaningfully cost
  semantic calibration even if retrieval improves).
- `ALGEBRA_FLOOR = 0.90` (unchanged convention from v3/v3b/v3c/v3e/v4), applied PER ARM.
- Verdict logic (see `_verdict_k_capacity`): HARD_PASS `K256_LIFTS_RETRIEVAL_CONFIRMED` iff delta_ret
  `>= 0.03` AND delta_hi80 `>= -0.02`. HARD_FAIL `K256_REGRESSES_CALIBRATION` iff delta_hi80 `<
  -0.02` (checked FIRST -- a calibration regression matters regardless of retrieval delta).
  HARD_FAIL `K256_DOES_NOT_LIFT_RETRIEVAL` iff delta_ret `<= 0`. MIDDLE_BAND `K256_MARGINAL_LIFT`
  otherwise (`0 < delta_ret < 0.03`). Per-arm `FALSE_WIN_ALGEBRA_LAST_STEP_{arm}` HARD_FAIL if EITHER
  arm's own keyed-roundtrip J=5 falls below `ALGEBRA_FLOOR` (checked before the retrieval comparison
  -- a K256 algebra break would itself be the headline finding, not silently ignored).

## HP_SCOPE

Delta bands apply to `{K128,K256}_BLOCK_LAST` FINAL-step only. `{K128,K256}_*_BESTVAL` (on TEST) is
comparison/context, NOT separately gated. `RANDOM_BLOCK`/`CHARPOS`/`shuffled_key` are integrity-only
(RANDOM_BLOCK and shuffled_key computed PER ARM since block partition differs; CHARPOS computed once
at a fixed K=128 reference, since it is a non-trained orthographic baseline unrelated to the trained
arm's K).

## Cardinality

`EXPECTED_N_UNITS = 19` both run_modes (SMOKE=FULL code path): 2 arms x (semantic 4:
DENSE/BLOCK x LAST/BESTVAL + semantic RANDOM_BLOCK(1, arm-specific) + keyed RANDOM_BLOCK posctrl(1) +
keyed LAST J5(1) + keyed BESTVAL J5(1) + shuffled-LAST J5(1)) = 2 x 9 = 18, + shared CHARPOS
semantic(1) = 19.

## Discriminator-survives-scale (option B, analytical justification)

Smoke (V_train=3000, 200 steps) validates MACHINERY ONLY: both K-resolution arms train end-to-end
with correctly-differing block partitions, per-arm RANDOM_BLOCK/algebra checks fire, cardinality
holds. SMOKE VERIFIED (2026-07-04, both seeds, local CPU): seed_7 HARD_PASS `elapsed_s=69.6` (wall
73s), seed_13 HARD_PASS `elapsed_s=72.2` (wall 78s), both well under the queue_add.py 180s smoke-gate
cap; 19/19 units both seeds, `arms_differ_verified=True`, no exemptions needed. Interesting (NOT
load-bearing, smoke-scale only): both smokes already show a positive `delta_ret` (seed7 +0.0945,
seed13 +0.0672) with near-zero `delta_hi80` -- consistent-direction with the bypass diagnostic's
prediction, but smoke's tiny V (3000 concepts) cannot reproduce the true near-neighbor coverage
effect that the FULL 177899-concept corpus tests; this is a promising machinery sanity check, NOT
evidence for the FULL verdict. The REMOTE-QUEUE OFFICIAL LANDING is canonical per the coordinator note.

## Substrate-too-robust-for-default-regime / baseline-in-band

CHARPOS `ret_agree10` in smoke: 0.2467 (seed7) / 0.2613 (seed13), well within (0.05, 0.95).
RANDOM_BLOCK `spearman_all` near-zero for both arms both seeds (calibration floor intact).

## Cell-template mandatory fields (declared)

- `arms_differ_verified: True` (sha256 over all code matrices, including per-arm RANDOM_BLOCK
  distinct-seed control codes; verified live in both smokes, no exemptions needed)
- `final_metrics_atomicity: tmp_replace` (inherited from `v3c._train_student_full` + `write_metrics`)
- `except SystemExit: raise` before `except Exception` (no bare except, no `except BaseException`)
  -- grep-verified clean in the core module and both wrapper files.
- `cell_chunked: True`, `start_marker_written: True`, `crash_diagnostic_present: True`,
  `heartbeat_present: True`, `defensive_error_checking: passed_all_4_patterns`
- `calibration_check: default_ok_for_this_regime` (identical hyperparameters to the validated
  v3c/v3e lineage; only `kb`/`blk_l` differ between arms)
- `progress_logging: print_flush_true` (steps=6000 >= the 1800s/30min threshold)

## Determinism pinning (coordinator mandate, 2026-07-04)

Identical to the sibling v4 cell: `torch.use_deterministic_algorithms(True, warn_only=True)`,
explicit torch/numpy/python RNG seeding, fixed thread count, `CUBLAS_WORKSPACE_CONFIG` for CUDA
determinism; `torch.__version__` + device recorded into `metrics.json["determinism"]`. **THE
REMOTE-QUEUE OFFICIAL LANDING IS THE CANONICAL NUMBER**; local smoke/preview is a MACHINERY gate only
(`metrics.json["canonical_source"]`).

## Timeout / dispatch estimate

v3e's own FULL run (ONE arm, K=128, 6000 steps, mining at V=160109, full eval battery) landed in
289.3s on remote CUDA MEASURED@data/exp_encoder_v3e_decline_vs_plateau_v1_seed7/metrics.json. This
cell trains TWO arms (roughly 2x the training-step cost; mining is shared/one-time) with a
similarly-sized eval battery (19 vs 10 units, but no coarser-headline-eval overhead like the sibling
v4 cell -- this cell reuses `v3c._train_student_full`'s existing cheap DENSE-proxy trajectory
logging unmodified). Estimated wall time: ~500-750s (8-13 min) per seed on GPU. Requested `--timeout
3600` (1 hour), a wide margin (5-7x estimate) consistent with this lineage's GPU-is-fast track record.

## Composes with

- `T3/EXP_encoder_v3e_decline_vs_plateau_v1` (the weak `ret_agree10=0.2112` result this cell tests a
  capacity-side fix for).
- `experiments/exp_encoder_teacher_sparsifier_bypass_v1_core.py` (the zero-training bypass diagnostic
  whose +0.09-Spearman prediction this cell tests under real training).
- Sibling cell `experiments/exp_encoder_v4_convergence_lr_hold_v1_core.py` (problem 1 of the same
  v3e-exposed pair: convergence/plateau, kept SEPARATE so this K-sweep is not confounded with v4's
  unvalidated LR-schedule change).
- `notes/encoder_rescue_plan_converged_diagnosis_2026-07-04.md` (R5 -- K=256 capacity-bound
  diagnostic, listed in the 5x rescue battery; this cell is the TRAINED version of that diagnostic).

ASCII-only. No emojis. No em dashes.
