# Pre-reg: Encoder v7 -- K=256 vs K=512 code-capacity paired test (2 seeds)

Date: 2026-07-04. Author: exp_dev. Status: PRE-REGISTERED before dispatch.
Core cell: `experiments/exp_encoder_v7_k512_capacity_paired_v1_core.py`
Per-seed wrappers (CHUNKED single-seed-per-cell): `experiments/exp_encoder_v7_k512_capacity_paired_v1_seed_7.py`, `..._seed_13.py`
Anchors: `encoder_v7_k512_capacity_paired_v1_seed7`, `..._seed13` (smoke suffix `_smoke` on each).
Parent cells (read-only imports, NOT edited): v3, v3c (same as the whole lineage). `v3c._train_student_full` is reused VERBATIM (unmodified) -- `kb`/`blk_l` are already parameters, so no new training-loop code is needed for this cell (identical low-risk posture to v5).

## Prior-work check (substrate concept-query, USER-locked 2026-07-01)

Query: "K512 block code capacity paired comparison retrieval agreement trained encoder versus K256
code resolution ceiling density curve" -> top hit cosine=0.2841 (this arc's own v3c/v3e prose,
expected self-similarity), v5's own prose at cosine=0.30 (expected -- same arc, direct predecessor
cell), the same-day density-curve read-only-reuse cell's own prose at cosine=0.28 (expected -- same
arc, distinct cell: read-only reuse vs fresh training). NONE at cosine>0.30 for a DISTINCT prior cell
that TRAINS a K=512 student. GENUINELY NOVEL: no prior cell in this lineage trains a K=512 student or
compares it against K=256 under matched conditions.

## Why this cell exists

v5 (FULL, PAIRED K128-vs-K256, 2 seeds, both HARD_PASS) landed a genuine, TRAINED retrieval lift:
K128 `final_ret_agree10` 0.1972/0.1984 -> K256 0.2902/0.2958 (delta +0.093/+0.097)
MEASURED@data/exp_encoder_v5_k256_capacity_paired_v1_seed7/metrics.json (and seed13). A same-day
READ-ONLY reuse of these SAME checkpoints (zero training,
`experiments/exp_encoder_retrieval_regime_density_curve_v1_core.py`, commit pending) reproduced these
numbers bit-exact and additionally showed that naive OFF-MANIFOLD post-hoc repartitioning of a
K128-trained model's output into K=256/K=512 grids it never trained against does NOT help (goes
slightly DOWN vs native K128: K256_OFFMANIFOLD 0.1995/0.1953, K512_OFFMANIFOLD 0.1870/0.1931, both
below native K128's 0.2112/0.2105) -- confirming the K128->K256 lift is a genuine TRAINING effect
(the block-STE gradient shape at a given kb/blk_l), not something recoverable by relabeling an
existing checkpoint. The ONLY way to learn whether K=512 lifts retrieval further is to actually train
a K=512 arm, matching v5's exact paired methodology. This cell is that direct sequel.

## What this cell answers

Two PAIRED arms (same seed/data/split/mining/objective, differing ONLY in block-code resolution)
inside ONE process: `K256` (kb=256, blk_l=16, REPRODUCED here as the internal positive control -- must
land within tolerance of v5's landed K256 numbers before the K512 arm is trusted) vs `K512` (kb=512,
blk_l=8, the new arm). Unlike K128->K256 (block count doubled, blk_l only halved from 32 to 16), this
step ALSO halves blk_l again down to 8 -- a genuinely smaller per-block alphabet. If K512 lifts
`ret_agree10` with no calibration regression, the density-vs-retrieval curve keeps rising through at
least 12.5% active. If it does not, blk_l=8 (or K=512 more broadly) is a genuine ceiling/reversal
point in the curve, not a cell bug -- a real, useful negative result for choosing the sparse-
composition operating point.

Note on the 2%-sparsity goal tension (flagged, not blocking, same as v5): K=512 (12.5% active) moves
FURTHER AWAY from `director_plan.json`'s ~2%-sparsity encoder goal (k~82/N=4096) than K=256 already
did. This cell is the density-vs-retrieval curve's next point; if it clears (or approaches) the
`ret_agree10>=0.35` target, the strategic implication is runtime REGIME-SWITCHING (dense/coarser
composition-irrelevant readout for retrieval, K=128 sparse readout for composition/storage) rather
than a single one-size-fits-all code -- a separate USER/Research-level decision this cell surfaces but
does not resolve.

## Compute architecture

Class (b) mixed-with-justification: GPU-batched matmul training loop (`v3c._train_student_full`,
REUSED VERBATIM, unmodified), sequential-only in the outer per-arm/per-unit eval loop (2 arms x 9
units + 1 shared CHARPOS = 19 total, each a batched cleanup-argmax or block-encode over the
codebook). Storage strategy: no_storage/no_composition beyond the existing bind/unbind/cleanup
keyed-unit check (single-hop).

## Functional requirements

| Requirement (plain English) | Existing primitive addressed by |
|---|---|
| Train in_batch-RKD-only student at NCE=0, two K values (256, 512) | `v3c._train_student_full` (REUSED UNMODIFIED, `kb`/`blk_l` parameterized) |
| Reproduce v5's K256 arm as an internal positive control before trusting K512 | paired K256 arm inside this SAME cell, same seed/data/mining/LR schedule as v5 |
| Test whether the K128->K256 lift continues to K512 or reverses as blk_l shrinks | paired K256 vs K512 arms |
| Check the finer code did not break SBC composability | per-arm `v3._keyed_unit`/shuffled-key at EACH arm's own block partition (K512's blk_l=8 checked independently) |
| Report the metric that actually matters | FINAL-step `ret_agree10`/`hi80_cos` delta is the PRIMARY gated comparison |
| Avoid confounding with the validated-but-orthogonal LR-schedule lever (v6) | UNCHANGED cosine-decay LR (same isolation v5 used vs v4) |

## Effective-vs-nominal parameter audit

Swept "parameter" is K (categorical: 256 vs 512), not a numeric sweep axis over many values.
`sweep_alignment_verdict: N/A_categorical_arm_not_numeric_sweep`. Both arms see the SAME mined
positives/semi-hard candidates (teacher-cosine-derived, independent of block partition) and the SAME
initial batch sequence per-arm (via `seed`) -- the ONLY thing that differs is `kb`/`blk_l`.

## Bracket-includes-discriminating-band

Not a numeric sweep; N/A. `DELTA_RET_AGREE10_HARD_PASS_MIN=0.03` (same threshold as v5) sits in a
genuine middle region (`(0, 0.03)` -> MIDDLE_BAND marginal-lift), so the discriminator brackets an
uncertain zone rather than being saturated at either extreme.

## Signal-shape compatibility audit

`v3c._train_student_full` (unmodified) -> this cell's eval/verdict code: SHAPE_MATCH, verified by
this cell's self-test (`_train_student_full` invoked at 2 distinct K values on tiny synthetic data,
asserting the returned `diag` dict and encoded-code shapes match expectations for BOTH K values).

## Positive-control reproduction (Gate D)

This cell's OWN K256 arm is the positive control: it must reproduce v5's landed K256 numbers within
tolerance (same seed=7/13, same data/split/mining/schedule) before the K512 arm's delta is trusted.
Additionally, `v3._keyed_unit(f"{arm}_RANDOM_BLOCK", "sbc", ..., J=5, ...)` -- SBC-lossless sanity
(`acc_at1 >= 0.98`) runs PER ARM at that arm's own `kb`/`blk_l`. K256 is SHAPE_MATCH (identical regime
to v5); K512 is `SHAPE_DRIFT_with_documented_risk` (blk_l=8 is a further reduction in per-block SNR
margin for bind/unbind vs K256's already-checked blk_l=16 -- exactly why this cell checks it explicitly
per arm rather than assuming K256's floor transfers). SMOKE VERIFIED (2026-07-04): both arms' RANDOM_
BLOCK posctrl `acc_at1=1.0` at smoke scale (seed7); K256 arm's smoke-scale numbers are in the same
ballpark as v5's own smoke run (both smoke-scale, not a FULL reproduction claim -- that check happens
at FULL landing).

## CRLB / capacity-feasibility

`crlb_floor_computed`: K256 `r_max` and K512 `r_max` computed via the SAME formula as the whole
lineage (`r_max = sigma_teacher / sqrt(sigma_teacher^2 + 0.25/K)`, `sigma_teacher` backed out from the
K128 anchor value 0.901; self-test asserts `_crlb_r_max(128)` reproduces 0.901 to 1e-3).
`discriminator_reachability: True`, with an HONEST caveat (declared, not silently omitted): this
formula's `K` term counts BLOCK COUNT only -- it does NOT separately model `blk_l` shrinking (K512's
blk_l=8 vs K256's 16), so a rising closed-form ceiling from K256 to K512 should NOT be read as
guaranteeing the TRAINED result also rises. That gap between the closed-form ceiling and the
blk_l-shrinkage effect is exactly the open question this cell measures empirically.

## Pre-reg bands (HYPOTHESIZED, tagged)

- `DELTA_RET_AGREE10_HARD_PASS_MIN = 0.03` (same threshold as v5, HYPOTHESIZED@this prereg, chosen for
  direct comparability with the K128->K256 result rather than re-derived).
- `DELTA_HI80_COS_REGRESSION_FLOOR = -0.02` (same as v5; K512 must not meaningfully cost semantic
  calibration even if retrieval improves).
- `ALGEBRA_FLOOR = 0.90` (unchanged convention from v3/v3b/v3c/v3e/v4/v5), applied PER ARM.
- Verdict logic (see `_verdict_k_capacity`): HARD_PASS `K512_LIFTS_RETRIEVAL_CONFIRMED` iff delta_ret
  `>= 0.03` AND delta_hi80 `>= -0.02`. HARD_FAIL `K512_REGRESSES_CALIBRATION` iff delta_hi80 `< -0.02`
  (checked FIRST). HARD_FAIL `K512_DOES_NOT_LIFT_RETRIEVAL` iff delta_ret `<= 0` (an honest, useful
  negative -- locates the ceiling/reversal point in the density curve). MIDDLE_BAND
  `K512_MARGINAL_LIFT` otherwise (`0 < delta_ret < 0.03`). Per-arm `FALSE_WIN_ALGEBRA_LAST_STEP_{arm}`
  HARD_FAIL if EITHER arm's own keyed-roundtrip J=5 falls below `ALGEBRA_FLOOR`.

## HP_SCOPE

Delta bands apply to `{K256,K512}_BLOCK_LAST` FINAL-step only. `{K256,K512}_*_BESTVAL` (on TEST) is
comparison/context, NOT separately gated (KNOWN early-checkpoint-inflation risk: v3e/v5 both showed
`bestval_step` landing at ~8% into training, right at the anti-gaming floor, consistent with the
lineage's known peak-then-decline pattern -- FINAL-step is the only trustworthy headline).
`RANDOM_BLOCK`/`CHARPOS`/`shuffled_key` are integrity-only (RANDOM_BLOCK and shuffled_key computed PER
ARM since block partition differs; CHARPOS computed once at a fixed K=128 reference).

## Cardinality

`EXPECTED_N_UNITS = 19` both run_modes (SMOKE=FULL code path): 2 arms x (semantic 4:
DENSE/BLOCK x LAST/BESTVAL + semantic RANDOM_BLOCK(1, arm-specific) + keyed RANDOM_BLOCK posctrl(1) +
keyed LAST J5(1) + keyed BESTVAL J5(1) + shuffled-LAST J5(1)) = 2 x 9 = 18, + shared CHARPOS
semantic(1) = 19.

## Discriminator-survives-scale (option B, analytical justification)

Smoke (V_train=3000, 200 steps) validates MACHINERY ONLY: both K-resolution arms train end-to-end
with correctly-differing block partitions, per-arm RANDOM_BLOCK/algebra checks fire, cardinality
holds. SMOKE VERIFIED (2026-07-04, local CPU): seed_7 HARD_PASS `elapsed_s=83.8` (well under the
queue_add.py smoke-gate cap); 19/19 units, `arms_differ_verified=True`, no exemptions needed. Smoke
already shows a positive `delta_ret` (+0.0404) with near-zero `delta_hi80` (-0.0045) -- promising
machinery sanity, NOT evidence for the FULL verdict (smoke's tiny V=3000 cannot reproduce the true
near-neighbor coverage effect the 177899-concept corpus tests). The REMOTE-QUEUE OFFICIAL LANDING is
canonical.

## Substrate-too-robust-for-default-regime / baseline-in-band

CHARPOS `ret_agree10` in smoke: 0.2467, well within (0.05, 0.95). RANDOM_BLOCK `spearman_all`
near-zero for both arms (calibration floor intact).

## Cell-template mandatory fields (declared)

- `arms_differ_verified: True` (sha256 over all code matrices, including per-arm RANDOM_BLOCK
  distinct-seed control codes; verified live in smoke, no exemptions needed)
- `final_metrics_atomicity: tmp_replace` (inherited from `v3c._train_student_full` + `write_metrics`)
- `except SystemExit: raise` before `except Exception` (no bare except, no `except BaseException`)
  -- grep-verified clean in the core module and both wrapper files.
- `cell_chunked: True`, `start_marker_written: True`, `crash_diagnostic_present: True`,
  `heartbeat_present: True`, `defensive_error_checking: passed_all_4_patterns`
- `calibration_check: default_ok_for_this_regime` (identical hyperparameters to the validated
  v3c/v3e/v5 lineage; only `kb`/`blk_l` differ between arms)
- `progress_logging: print_flush_true` (steps=6000 >= the 1800s/30min threshold)

## Determinism pinning (coordinator mandate, 2026-07-04)

Identical to v5/v4: `torch.use_deterministic_algorithms(True, warn_only=True)`, explicit torch/numpy/
python RNG seeding, fixed thread count, `CUBLAS_WORKSPACE_CONFIG` for CUDA determinism;
`torch.__version__` + device recorded into `metrics.json["determinism"]`. **THE REMOTE-QUEUE OFFICIAL
LANDING IS THE CANONICAL NUMBER**; local smoke/preview is a MACHINERY gate only
(`metrics.json["canonical_source"]`).

## Timeout / dispatch estimate

v5's own FULL run (TWO arms, K=128 + K=256, 6000 steps each, mining shared, full eval battery) landed
in 335.1s TOTAL on remote CUDA MEASURED@data/exp_encoder_v5_k256_capacity_paired_v1_seed7/metrics.json
elapsed_s. This cell also trains TWO arms at the same step count/batch, with the same-sized eval
battery (19 units, identical structure). Estimated wall time: ~350-500s (6-8 min) per seed on GPU
(K512 has a smaller blk_l so per-step matmuls are marginally cheaper than K256's; not expected to be
slower than v5). Requested `--timeout 3600` (1 hour), a wide margin (7-10x estimate) consistent with
this lineage's GPU-is-fast track record.

## Composes with

- `T3/EXP_encoder_v5_k256_capacity_paired_v1` (the K128-vs-K256 result this cell extends one density
  step further).
- `experiments/exp_encoder_retrieval_regime_density_curve_v1_core.py` (the same-day read-only reuse
  diagnostic that ruled out the cheap off-manifold-repartition shortcut and directly motivated training
  a real K512 arm).
- `experiments/exp_encoder_v6_k256_plateau_followup_v1_core.py` (v6 -- the OTHER validated lever,
  plateau-hold LR, kept ORTHOGONAL to this cell's K-axis per the same isolation discipline v5 used
  against v4; v6 already confirmed the two lever FAMILIES compose, so a future cell could test
  K512+plateau together once this cell's K512-alone number is in hand).
- `notes/encoder_rescue_plan_converged_diagnosis_2026-07-04.md` (R5 -- K-capacity diagnostic family;
  this cell is the next point on that density curve).

ASCII-only. No emojis. No em dashes.
