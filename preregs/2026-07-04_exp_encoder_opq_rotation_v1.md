# Pre-reg: OPQ-style learned rotation before block-argmax (2026-07-04)

Date: 2026-07-04. Author: exp_dev. Status: PRE-REGISTERED before FULL dispatch (self-test
+ smoke PASSED locally, both seeds).
Core cell: `experiments/exp_encoder_opq_rotation_v1_core.py`
Per-seed wrappers (CHUNKED single-seed-per-cell): `experiments/exp_encoder_opq_rotation_v1_seed_7.py`, `..._seed_13.py`
Anchors: `encoder_opq_rotation_v1_seed7`, `..._seed13` (smoke suffix `_smoke` on each).
Parent cells (read-only imports, NOT edited):
  v3 (`exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py`),
  v3c (`exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_core.py`),
  v3e (`exp_encoder_v3e_decline_vs_plateau_v1_core.py` -- reuses `_trend_diagnostic` verbatim).

## Prior-work check (substrate concept-query, USER-locked 2026-07-01)

Query: "OPQ learned rotation orthogonal transform before block quantizer retrieval code
utilization gap" -> top hit cosine=0.3545 (WordNet 'transformation' dictionary entry).
Next: 'utilization' (WordNet, cosine=0.3398). Third hit cosine=0.334, source_class=note,
`notes/research_drill_sparse_w_alternatives_3x_2026-06-07.md` -- a DIFFERENT context
(Walsh-Hadamard rotation preconditioning a pseudoinverse-derived sparse-W matrix for
QuaRot/QuIP#-style WEIGHT quantization, not an encoder-output BLOCK-ARGMAX RETRIEVAL
code). Remaining hits <=0.326 (WordNet 'quantization'/'conventionalization'). NONE at
cosine>0.30 for a DISTINCT prior CELL applying a learned/data-adapted rotation to this
encoder's block-argmax code. GENUINELY NOVEL: the existing bypass diagnostic (its own
prior-work check found top hit cosine=0.2612) tested only DATA-INDEPENDENT random
rotations (ORTHO_K128 isometric-random, RANDOM_K128 Gaussian-random); this cell is the
first to test a genuinely DATA-ADAPTED (eigenvalue-allocation / OPQ-style) rotation.

## Three convergent evidence lines motivating this cell

1. **Skunkworks HARD_FAIL closure of the KL-RANK objective-family swap** (commit
   7f116800d, MEASURED@data/exp_encoder_objective_swap_kl_rank_v1_seed7/metrics.json +
   `..._seed13/metrics.json`): ret_agree10=0.2229/0.2193, delta-vs-MSE +0.0117/+0.0089
   (mean +0.010), ~9x smaller than K256's verified +0.093. PROVES the retrieval ceiling
   at fixed K=128 is a CODE/QUANTIZATION-STRUCTURE bound, not a training-objective bound.
2. **Cardinality drill** (`notes/research_drill_encoder_cardinality_capacity_ceiling_
   0.85_reachability_2026-07-04.md`): Rank 2 lever (P_deflated=0.45, rotation-only
   variant) is "learned rotation before block-selection (OPQ-style)" -- our block-WTA
   structure IS mathematically Product Quantization; PQ's well-documented subspace-
   independence tax is exactly what a rotation fixes cheaply (Ge, He, Sun, "Optimized
   Product Quantization", CVPR 2013 / TPAMI 2014).
3. **Bypass diagnostic** (MEASURED@data/exp_encoder_teacher_sparsifier_bypass_v1/
   metrics.json): at ZERO training, ORTHO_K128 ret_agree10=0.4295 vs the TRAINED
   student's ret_agree10~0.21 -- roughly HALF the code's own zero-training ceiling is
   left on the table by training. A code-UTILIZATION gap, distinct from a code-CAPACITY
   gap.

**Caveat the bypass diagnostic does NOT already answer:** its ORTHO_K128/RANDOM_K128
arms are BOTH data-INDEPENDENT random lifts (isometry_vs_random_gap_k128=0.0276
MEASURED -- a small gap between two flavors of random projection). Neither is a
DATA-ADAPTED rotation. This cell tests whether adapting the rotation to the trained
student's OWN variance structure closes materially more of the gap than a generic
random rotation does.

## Hypothesis

The trained student's D=4096 output is highly anisotropic (a distillation target derived
from a rank<=1024 BGE teacher via an MLP almost certainly concentrates variance unevenly
across 4096 raw output coordinates). The existing code's blocks are CONTIGUOUS RAW-INDEX
ranges [0:32],[32:64],... -- axis-aligned to whatever the MLP's output neurons happen to
be, not to the student's own variance structure. A rotation that REDISTRIBUTES variance
evenly across all K=128 blocks before the hard per-block argmax should let more blocks
compete informatively -> higher ret_agree10 at the SAME K=128/3.125% sparsity, same
width, same runtime.

## Mechanism chosen (ONE, well-justified -- not diluting across many under-tested
variants per "no padding experiments")

**Non-parametric OPQ / eigenvalue-allocation rotation** (Ge, He, Sun, CVPR 2013 -- the
paper's own cheaper closed-form alternative to full iterative/joint optimization):
PCA-eigendecompose the (already fully-trained) student's own raw continuous output on a
held-out VAL split (uncentered second-moment matrix -- the quantity that actually drives
per-block hard-argmax competition, which operates on raw magnitude not mean-removed
spread), then greedily assign the D principal directions (descending eigenvalue) to the
K=128 blocks via a capacity-constrained min-heap load-balance (LPT-style bin-balancing:
each direction goes to whichever block currently has the lowest running eigenvalue-sum,
until that block's L=32 slots are full). The resulting R [D,D] is EXACTLY orthonormal (a
column-reordering of an eigh-orthonormal basis), zero information loss, zero added
density.

### Why post-hoc/alternating, not jointly-backprop-trained (task permitted either)

On reflection, a jointly-trained rotation is NOT ruled out mathematically: `v3._block_ste`'s
forward pass computes `softmax(zb.abs()/TAU_GUMBEL, dim=-1)` PER BLOCK, which is NOT
rotation-invariant (depends on which raw coordinates fall in which fixed-width block) --
so a rotation inserted before `_block_ste` and trained end-to-end WOULD receive a genuine
non-zero gradient (correcting an initial, mistaken "dead-gradient" intuition that only
holds for a pure Gram-matrix/cosine loss on the UNQUANTIZED continuous vector, which is
not what happens here since the STE quantization sits inside the training loop). The
post-hoc/alternating variant was chosen instead for practical reasons: (a) it is ITSELF a
separately-published OPQ method, not a lesser fallback; (b) zero new training-loop code --
reuses `v3c._train_student_full` VERBATIM, unmodified, at the proven config (lowest risk
of a new training-loop bug); (c) needs only ONE training run (not a two-arm paired
training), roughly HALF the GPU compute of the sibling KL-RANK cell; (d) gives the
CLEANEST possible pairing -- BASELINE and ROTATION arms share IDENTICAL trained weights
(zero training-noise confound), arguably MORE rigorous than a jointly co-adapted variant
(which would confound "does rotation help" with "does joint training find a different,
possibly-better combination"). A jointly-trained variant remains a well-motivated
follow-up if this lever is inconclusive.

## Paired-trials design (mandatory per feedback_paired_trials_mandatory_for_arm_
comparison_discriminators_2026-07-04)

BASELINE_BLOCK_LAST and ROTATION_BLOCK_LAST are computed from the SAME trained student
(literally identical weights) -- the strongest possible pairing: zero training-noise
confound between arms. The only difference is whether R (fit from that SAME student's
own VAL-split dense output) is applied before the hard block-argmax. Same holds for the
`_BESTVAL` pair (both computed from the SAME reloaded best-VAL checkpoint, with a
freshly-refit R appropriate to that checkpoint's own geometry).

## Compute architecture

Class (b) mixed-with-justification: GPU-batched matmul training loop (`v3c._train_
student_full`, unmodified, itself GPU-batched). The rotation-fit step (`torch.linalg.
eigh` on a [4096,4096] uncentered second-moment matrix) runs on CPU (float64, for
numerical stability of the eigendecomposition regardless of training device) -- a
one-time, cheap-relative-to-training cost (twice per seed: LAST + BESTVAL). Eval loop is
sequential-only (15 units, each a batched cleanup-argmax over the codebook). Storage
strategy: no_storage/no_composition beyond the existing bind/unbind/cleanup keyed-unit
check (single-hop).

## Functional requirements

| Requirement (plain English) | Existing primitive addressed by |
|---|---|
| Train the BASELINE (in-batch RKD, NCE off) reproducing the known ~0.21 control | `v3c._train_student_full(objective="in_batch", nce_weight=0.0)`, REUSED VERBATIM (not copied) |
| Fit a data-adapted rotation from the trained student's own geometry | `_fit_np_opq_rotation` (new; NP-OPQ eigenvalue-allocation, self-test-verified to balance a skewed synthetic spectrum) |
| Apply the rotation before the SAME hard block-argmax quantizer | `_encode_hard_block_rotated` (new; self-test-verified R=Identity reproduces `v3._encode_hard_block` EXACTLY) |
| Report a non-cherry-picked "official" number per arm | FINAL-step (post-loop) student is PRIMARY; best-by-VAL-on-TEST is SECONDARY context |
| Report the actual retrieval-relevant metric, not buried | `v3._semantic_unit`'s `ret_agree10`/`hi80_cos` promoted to `recovery{}` top level, both arms |
| Verify the rotated code stays a valid composable SBC code (the key risk) | `v3._keyed_unit`/shuffled-key J=5, BOTH arms, LOUDLY gated (`ROTATION_BREAKS_ALGEBRA`) |
| Prevent held-set doubling as both selector/rotation-fit-source and reported number | 3-way split (VAL for training-selection AND rotation-fitting, never used for reported numbers; TEST for all reported numbers) |

## Effective-vs-nominal parameter audit

Swept params: none (2 fixed arms -- BASELINE vs ROTATION -- no sweep axis).
`sweep_alignment_verdict: N/A_no_sweep_axis`.

## Bracket-includes-discriminating-band

Not a sweep cell; N/A. The verdict bands bracket a genuine 3-way split (HARD_PASS
>=0.35, HARD_FAIL <=0.25, MIDDLE_BAND in between) that is not by-construction saturated
at either extreme (0.21 measured control sits inside the HARD_FAIL zone by construction;
0.43-0.48 zero-training ceiling sits above the HARD_PASS floor).

## Signal-shape compatibility audit

`train_diag["dense_traj"]` (from `v3c._train_student_full`, IDENTICAL shape to the
whole lineage's convention) -> `v3e._trend_diagnostic` (expects exactly that shape):
SHAPE_MATCH, self-test-verified (`trend3["sufficient"] is True` on a real trajectory
produced by the reused, unmodified training function).

## Positive-control reproduction (Gate D)

Two positive controls, both self-test-verified:
1. `v3._keyed_unit("RANDOM_BLOCK", "sbc", ..., J=5, ...)`: SBC-lossless sanity check
   (acc_at1>=0.98 required), SAME primitive/regime already validated throughout
   v3/v3b/v3c/v3e/objswap_kl. `regime_extension_audit: SHAPE_MATCH` (no regime change).
2. **BASELINE_BLOCK_LAST's ret_agree10 vs the cited prior** (objswap_kl's live MSE
   control, seed7/13 mean ~0.2129 -- MEASURED@data/exp_encoder_objective_swap_kl_rank_v1_
   seed7/metrics.json + `..._seed13/metrics.json`): tolerance 0.10. Because this cell
   trains its OWN fresh student (not reusing a checkpoint -- none survived past the prior
   cell's own artifact lifetime locally), reproducing the SAME ~0.21 ballpark under the
   IDENTICAL config is the load-bearing sanity check that the reused
   `v3c._train_student_full` call (objective="in_batch", nce_weight=0.0, FULL_STEPS=6000,
   FULL_BATCH=128) is wired correctly and this run's BASELINE is a fair, in-family
   reproduction before trusting the ROTATION comparison built on top of it.
   `baseline_repro_within_tolerance` field reports this live.

## CRLB / capacity-feasibility

`crlb_floor_computed=0.901` at K=128 (THEORETICAL@v2/v3/v3b/v3c/v3e/objswap_kl prereg:
`r_max = sigma_teacher / sqrt(sigma_teacher^2 + 0.25/K)`, unchanged -- a rotation is an
exact isometry of the pre-quantization space; it re-labels which continuous coordinate
feeds each block without changing the channel's information-theoretic ceiling).
`discriminator_reachability: True` -- the HARD_PASS floor for `ret_agree10` (0.35) sits
below the code's own MEASURED zero-training ceiling (~0.43-0.48 at true full
N=177899, MEASURED@data/exp_encoder_teacher_sparsifier_bypass_v1/metrics.json), so the
target is reachable in principle without any code-width change.

## Pre-reg bands (HYPOTHESIZED, tagged)

- `ROTATION_RET_AGREE10_HARD_PASS = 0.35` HYPOTHESIZED@task spawn prompt.
- `ROTATION_RET_AGREE10_HARD_FAIL_CEILING = 0.25` HYPOTHESIZED@this prereg (no material
  movement vs BASELINE's measured ~0.21-0.213).
- `ROTATION_HI80_COS_HARD_PASS = 0.82` HYPOTHESIZED@task spawn prompt ("calibrated not
  overshooting"); `ROTATION_HI80_COS_HARD_FAIL_FLOOR = 0.75` HYPOTHESIZED@this prereg.
- `ALGEBRA_FLOOR = 0.90` (unchanged lineage convention; task spawn: ">=0.90"). Checked on
  BOTH arms; ROTATION's algebra-break is its OWN loud, distinct HARD_FAIL branch
  (`ROTATION_BREAKS_ALGEBRA`), evaluated BEFORE any retrieval-lift interpretation, per
  task instruction to "flag it loudly."
- `BASELINE_REPRO_TOLERANCE = 0.10` (Gate D reproduction check vs cited prior ~0.2129).

## HP_SCOPE

HARD_PASS/HARD_FAIL retrieval+cos bands apply to `ROTATION_BLOCK_LAST` ONLY (the arm
under test). `BASELINE_BLOCK_LAST` is the live control/reproduction -- gated on algebra
(`ALGEBRA_FLOOR`, "the run itself is suspect if the control's own algebra broke") and
`baseline_in_band`, but NOT separately HARD_PASS/HARD_FAIL gated on `ret_agree10`.
`*_BESTVAL` units (both arms) are comparison/context, NOT separately gated. `DENSE_LAST`/
`DENSE_BESTVAL` are diagnostic context (rotation-invariant-adjacent reference point --
note: sign-quantized DENSE is NOT literally rotation-invariant since `sign()` is
nonlinear/basis-dependent; only the fully-continuous pre-sign cosine similarity is exactly
rotation-invariant). `RANDOM_BLOCK`/`CHARPOS`/`shuffled_key` are integrity-only.

## Cardinality

`EXPECTED_N_UNITS = 15` both run_modes (SMOKE=FULL code path): semantic (8: {BASELINE,
ROTATION} x {LAST,BESTVAL} BLOCK = 4, + DENSE{LAST,BESTVAL} = 2, + RANDOM_BLOCK +
CHARPOS = 2) + keyed (7: RANDOM_BLOCK posctrl (1) + {BASELINE,ROTATION} x {LAST,BESTVAL}
keyed (4) + {BASELINE,ROTATION} LAST-shuffled (2)). `cardinality_ok` gates HARD_FAIL if
`len(per_unit) < expected`. SMOKE VERIFIED (2026-07-04): both seeds landed 15/15 units.

## Discriminator-survives-scale

**Retrieval-lift question: option (B) analytical justification** (same as the whole v3
lineage) -- smoke's tiny V_train=3000/VAL_CAP=200 cannot reproduce the true near-neighbor
coverage effect that makes the UNROTATED code's ret_agree10 sit at ~0.21 at V~178k; smoke
validates MACHINERY ONLY for that question (both arms train/fit/encode end-to-end,
3-way split partitions correctly, headline fields populate). SMOKE VERIFIED (both
seeds): seed7 elapsed=80.4s ROTATION ret_agree10=0.4912 vs BASELINE=0.5222 (lift=-0.031,
NOT expected to be meaningful at this tiny/degenerate scale); seed13 elapsed=98.5s
ROTATION=0.4902 vs BASELINE=0.5173 (lift=-0.027). Both smoke's `hi80_cos` for ROTATION
dropped sharply vs BASELINE (0.33 vs 0.81 seed7; 0.27 vs 0.81 seed13) -- CONSISTENT with
the documented caveat below, not a red flag for FULL.

**Allocation-mechanism question: option (C) discriminator-preview**, via self-test on
pure-synthetic data with n_samples >> D (well-posed PCA regime, unlike smoke's n_val=200
<< D=4096): a deliberately skewed synthetic eigenvalue spectrum (8 huge + 56 tiny
eigenvalues, D=64/K=8/L=8) asserts `balance_improvement_ratio > 2.0` -- PASSED
(self-test), proving the greedy eigenvalue-allocation algorithm itself balances variance
correctly at ANY scale, decoupled from the FULL-only retrieval-lift question.

**Explicit caveat (why smoke's rotation quality is NOT diagnostic of FULL):** SMOKE's
`VAL_CAP=200` is FAR BELOW `N_DIM_DEFAULT=4096` -- the uncentered second-moment matrix M
is at most rank-200 out of 4096, meaning the PCA fit at smoke is degenerate/low-rank by
construction (`well_posed_pca: False`, MEASURED both seeds' smoke metrics.json). FULL's
`VAL_CAP=5000 > N_DIM_DEFAULT=4096` gives a full-rank, statistically well-posed second-
moment estimate -- a fundamentally different (better-conditioned) regime. Smoke's poor
`hi80_cos`/near-flat `ret_agree10` for ROTATION is the EXPECTED signature of an
underdetermined PCA fit on 200 samples in 4096 dimensions, not evidence about whether the
mechanism helps at FULL scale.

## Substrate-too-robust-for-default-regime / baseline-in-band

CHARPOS `ret_agree10` in smoke: seed7=0.24, seed13=0.2853 (well within (0.05,0.95)).
RANDOM_BLOCK `spearman_all` ~0.015-0.016 (near-zero, calibration floor intact).

## Cell-template mandatory fields (declared)

- `arms_differ_verified: True` (sha256 over all 8 code matrices; verified live in smoke
  both seeds -- would raise `META_RULE_AF_VIOLATION` if any two matched; this doubles as
  the THREE-DISCIPLINE-PATTERNS #2 "smoke must fire the discriminator" check -- BASELINE
  and ROTATION codes MUST differ since R != I)
- `final_metrics_atomicity: tmp_replace`
- `except SystemExit: raise` before `except Exception` (no bare except, no
  `except BaseException`) -- grep-verified clean in the core module and both wrapper
  files (BLOCK_DISPATCH gate passed).
- `cell_chunked: True`, `start_marker_written: True`, `crash_diagnostic_present: True`,
  `heartbeat_present: True`, `defensive_error_checking: passed_all_4_patterns`
- `calibration_check: default_ok_for_this_regime` (identical hyperparameters to the
  validated v3/v3c/v3e/objswap_kl lineage; only the post-hoc rotation differs)
- `progress_logging: print_flush_true` (every 200 steps + every dense-eval point + every
  unit + every rotation-fit)

## Timeout / dispatch estimate

v3e's single-arm (`in_batch`, NCE-off, 6000 steps, full 177899-concept cache) FULL run
landed in 284.7s on remote CUDA (MEASURED@data/exp_encoder_v3e_decline_vs_plateau_v1_
seed13/metrics.json:elapsed_s). This cell trains ONE arm (same config, same steps) plus
TWO rotation-fits (`torch.linalg.eigh` on a [4096,4096] float64 matrix, CPU, run twice:
LAST + BESTVAL) plus 15-unit eval overhead (vs v3e's fewer units). Estimate: mining
(~60s, one-time) + training (~285s) + 2x rotation-fit (~30-60s each, ~90-120s combined)
+ eval overhead (15 units, moderate increase over single-arm baseline, ~60s) ~= 500-550s
(~9 min). Requested `--timeout 1800` (30 min), ~3.3x safety margin for remote GPU
contention (matches the lineage's convention of requesting generous margin when other
jobs may share the GPU).

## Composes with

- `data/exp_encoder_objective_swap_kl_rank_v1_seed7/13` (the HARD_FAIL closure this
  cell's BASELINE arm reproduces as a live control, and whose "escalate to K=256 or an
  OPQ-style rotation" recommendation this cell directly answers).
- `notes/research_drill_encoder_cardinality_capacity_ceiling_0.85_reachability_2026-07-04.md`
  (Rank 2 lever this cell operationalizes).
- `data/exp_encoder_teacher_sparsifier_bypass_v1` (the zero-training ceiling / code-
  utilization-gap framing this cell tests against, at the TRAINED-student level).
- Distinct lane from the concurrently-in-flight v4 (`exp_encoder_v4_convergence_lr_hold_
  v1_*`, LR-schedule convergence fix) and v5 (`exp_encoder_v5_k256_capacity_paired_v1_*`,
  K=128 vs K=256 code-capacity) cells -- no shared files edited, distinct anchor/
  artifact-dir/prereg.

ASCII-only. No emojis. No em dashes.
