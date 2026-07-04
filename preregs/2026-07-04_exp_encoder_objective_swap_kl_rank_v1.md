# Pre-reg: Encoder objective-family swap -- MSE-RKD (control) vs KL-RANK (2026-07-04)

Date: 2026-07-04. Author: exp_dev. Status: PRE-REGISTERED before FULL dispatch (smoke PASSED
locally, both seeds).
Core cell: `experiments/exp_encoder_objective_swap_kl_rank_v1_core.py`
Per-seed wrappers (CHUNKED single-seed-per-cell): `experiments/exp_encoder_objective_swap_kl_rank_v1_seed_7.py`, `..._seed_13.py`
Anchors: `encoder_objective_swap_kl_rank_v1_seed7`, `..._seed13` (smoke suffix `_smoke` on each).
Parent cells (read-only imports, NOT edited):
  v3 (`exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py`),
  v3c (`exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_core.py`),
  v3e (`exp_encoder_v3e_decline_vs_plateau_v1_core.py` -- reuses `_trend_diagnostic` verbatim).

## Prior-work check (substrate concept-query, USER-locked 2026-07-01)

Query: "objective family swap KL divergence rank-aware distillation loss softmax similarity
distribution retrieval agreement encoder" -> top hit cosine=0.3604, entity is an AUDIT-LOG
MIA-detection method ("KL divergence of observed [retrieval] score distribution from expected
[calibrated]", `notes/research_drill_substrate_evaluation_methodology_5x_chain1_drill3_2026-06-07.md`)
-- KL used there for anomaly/attack DETECTION over query logs, a DIFFERENT domain from a
distillation TRAINING objective. Remaining hits <=0.3564 (a pretest prereg's generic "reference
distribution" field; WordNet lexical entries for "distribution"/"distribution_agreement"). NONE at
cosine>0.30 for a DISTINCT prior CELL testing a KL/rank-aware distillation objective for this
encoder. GENUINELY NOVEL.

## Three convergent evidence lines motivating this cell

1. **seed_13's own trajectory analysis** (v3e HARD_FAIL, `verdict_msg`
   MEASURED@data/exp_encoder_v3e_decline_vs_plateau_v1_seed13/metrics.json): "removing NCE only
   SLOWED the in_batch collapse; the true asymptote likely requires an objective-family change
   (KL/PKT-style swap), not a longer NCE-off run" [final_block=0.9144 (TEST spearman, mostly-random
   pairs) final_ret_agree10=0.2105 early_minus_late=0.1243 (still declining)].
2. **Metric drill** (`notes/research_drill_encoder_target_metric_coarse_cosine_vs_fine_retrieval_2026-07-04.md`):
   the real downstream goal is RETRIEVAL (`ret_agree10`), currently 0.21 vs a proposed target
   >=0.35; the K=128 code's own zero-training ceiling is ~0.478
   MEASURED@data/exp_encoder_teacher_sparsifier_bypass_v1_selftest/metrics.json (true 177899-cache,
   n_test=800) -- the 0.21-vs-0.48 gap is a TRAINING problem, not a code-capacity problem.
3. **Cardinality drill** (`notes/research_drill_encoder_cardinality_capacity_ceiling_0.85_reachability_2026-07-04.md`):
   top-ranked structural lever (Rank 1, P_deflated=0.50) is a "rank-aware / anisotropic
   quantization loss" (direct analog: Guo et al. ScaNN, arXiv:1908.10396, VERIFIED via fetch in
   that drill); code-widening (K=256, Rank 3) is a real but SECOND-ORDER lever, not the first pull.

## Hypothesis

The current MSE-RKD objective (`l_rkd = mean((S_cos - T_cos)^2)` over off-diagonal in-batch pairs)
matches BULK pairwise geometry (hi80_cos=0.828, near the 0.85 coarse target) but does NOT optimize
NEAR-NEIGHBOR RANKING (weak ret_agree10=0.21) and does not converge (declines post-floor). A
rank-aware / distributional objective that directly targets "which of my batch-mates am I closest
to" should lift ret_agree10 without sacrificing coarse calibration or algebra.

## Objective chosen (ONE, well-justified)

**KL-RANK**: a temperature-scaled, in-batch, off-diagonal SOFTMAX-KL distillation loss
(CompRess/PKT-style relational-KD: Koohpayegani et al. "CompRess", NeurIPS 2020; Passalis & Tefas
"Probabilistic Knowledge Transfer", ECCV 2018). Per batch: convert both the teacher's and the
student's in-batch cosine-similarity ROW (self-position masked) into a softmax probability
distribution at temperature `TAU_KL=0.10`, then minimize `KL(teacher_row || student_row)` averaged
over rows. LISTWISE and rank-sensitive by construction (softmax concentrates mass on the highest-
similarity neighbors, the same regime ret_agree10 measures), vs. the MSE branch's magnitude-
regression that weights near and far pairs equally. Reuses the SAME [batch x batch] similarity
matrices the MSE control already computes -- zero extra forward passes. `TAU_KL=0.10` HYPOTHESIZED@
this prereg (softer than the existing `TAU_NCE=0.07` since this loss carries a full ~127-way row
distribution, not a 1-vs-many classification); not swept this cell -- a temperature sweep is a
cheap, well-scoped follow-up IF this cell lands MIDDLE_BAND. Only one new arm is tested (not 1-2
diluted variants) per "no padding experiments" -- a focused, well-instrumented single lever first.

## Paired-trials design (mandatory per feedback_paired_trials_mandatory_for_arm_comparison_discriminators_2026-07-04)

Both arms trained by the SAME local function `_train_student_full_swap`, differing ONLY in the
`loss_family` branch that computes `l_rkd`. Both arms receive the IDENTICAL `seed` (->identical
`_make_student` init) and consume the shared RNG (`gen`) in the IDENTICAL order (batch sampling ->
semi-hard negatives -> fallback negatives; the loss-family branch adds NO extra random draws), so
both arms see the token-for-token IDENTICAL batch/negative sequence. The MSE branch is asserted (in
self-test) to reproduce `v3c._train_student_full`'s `objective="in_batch"` formula to <1e-4 on
`rkd_last`/`loss_last` AND at the per-parameter WEIGHT level (`torch.allclose(atol=1e-4)`) on tiny
synthetic data with matched seeds -- this proves the copy is faithful BEFORE trusting the KL branch
sits fairly alongside it (guards against a copy-paste bug masquerading as an "objective effect").

## Compute architecture

Class (b) mixed-with-justification: GPU-batched matmul training loop (near-verbatim copy of
`v3c._train_student_full`, itself GPU-batched; the KL branch reuses the SAME [batch x batch]
similarity matrices, zero extra forward passes), sequential-only in the outer per-arm/per-J eval
loop (17 units total, each a batched cleanup-argmax over the codebook). Storage strategy:
no_storage/no_composition beyond the existing bind/unbind/cleanup keyed-unit check (single-hop).

## Functional requirements

| Requirement (plain English) | Existing primitive addressed by |
|---|---|
| Train the MSE-RKD control at NCE=0, matching v3e's config exactly | `_train_student_full_swap(loss_family="mse_rkd")`, self-test-verified equivalent to `v3c._train_student_full(objective="in_batch")` |
| Train the KL-RANK arm at IDENTICAL everything-else | `_train_student_full_swap(loss_family="kl_rank")`, same seed/mining/split/batch-sequence |
| Report a non-cherry-picked "official" number per arm | LAST-step (post-loop) student, no selection |
| Report the actual retrieval-relevant metric, not buried | `v3._semantic_unit`'s `ret_agree10`/`hi80_cos` promoted to `recovery{}` top level, both arms |
| Detect whether KL_RANK converges (plateau) vs still declines | `v3e._trend_diagnostic` (reused verbatim) on the KL arm's `dense_traj` |
| Verify the KL-trained code stays a valid composable SBC code | `v3._keyed_unit`/shuffled-key J=5, per arm |
| Prevent held-set doubling as both selector and reported number | 3-way split (VAL for selection, TEST for all reported numbers) |

## Effective-vs-nominal parameter audit

Swept params: none (2 fixed-config arms, no sweep axis). `sweep_alignment_verdict: N/A_no_sweep_axis`.

## Bracket-includes-discriminating-band

Not a sweep cell; N/A. The verdict bands bracket a genuine 3-way split
(HARD_PASS >=0.35, HARD_FAIL <=0.25, MIDDLE_BAND in between) that is not by-construction saturated
at either extreme (0.21 measured control sits inside the HARD_FAIL zone by construction; 0.478
zero-training ceiling sits above the HARD_PASS floor).

## Signal-shape compatibility audit

`_train_student_full_swap`'s `dense_traj` list (`{step, dense_full, dense_quick, rkd, final}` dicts,
identical shape to `v3c._train_student_full`'s) -> `v3e._trend_diagnostic` (expects exactly that
shape): SHAPE_MATCH, verified by self-test asserting `trend["sufficient"] is True` on a real
`dense_traj` produced by the new training function.

## Positive-control reproduction (Gate D)

Two positive controls, both self-test-verified:
1. `v3._keyed_unit("RANDOM_BLOCK", "sbc", ..., J=5, ...)`: SBC-lossless sanity check (acc_at1>=0.98
   required), SAME primitive/regime already validated at this exact K=128/N=4096 config throughout
   v3/v3b/v3c/v3e. `regime_extension_audit: SHAPE_MATCH` (no regime change).
2. **`_train_student_full_swap(loss_family="mse_rkd")` vs `v3c._train_student_full(objective=
   "in_batch")`**: the CONTROL objective itself must reproduce the parent lineage's known formula,
   not just be cited -- verified in self-test to <1e-4 on `rkd_last`/`loss_last` AND full
   per-parameter weight match (`torch.allclose`) on matched synthetic seed/data. This is the
   Gate-D discipline applied to the NEW cell's own control arm (not just an external citation).

## CRLB / capacity-feasibility

`crlb_floor_computed=0.901` at K=128 (THEORETICAL@v2/v3/v3b/v3c/v3e prereg: `r_max = sigma_teacher /
sqrt(sigma_teacher^2 + 0.25/K)`, unchanged -- the loss FAMILY does not change the K=128/N=4096
quantization channel's information ceiling). `discriminator_reachability: True` -- the HARD_PASS
floor for `ret_agree10` (0.35) sits below the code's own MEASURED zero-training ceiling (~0.478 at
true full N=177899, MEASURED@data/exp_encoder_teacher_sparsifier_bypass_v1_selftest/metrics.json),
so the target is reachable in principle without any code-width change.

## Pre-reg bands (HYPOTHESIZED, tagged)

- `KL_RET_AGREE10_HARD_PASS = 0.35` HYPOTHESIZED@task spawn prompt (materially closes at least half
  the gap from MSE's measured 0.2105 toward the K=128 zero-training ceiling of ~0.478).
- `KL_RET_AGREE10_HARD_FAIL_CEILING = 0.25` HYPOTHESIZED@this prereg (no material movement vs the
  MSE control's measured ~0.2105).
- `KL_HI80_COS_HARD_PASS = 0.82` HYPOTHESIZED@task spawn prompt ("must not regress below ~0.82");
  `KL_HI80_COS_HARD_FAIL_FLOOR = 0.75` HYPOTHESIZED@this prereg (material regression on the coarse
  metric that is otherwise nearly closed at 0.828-0.857 MEASURED@v3e).
- `ALGEBRA_FLOOR = 0.90` (unchanged lineage convention; task spawn: "must stay ~1.0").
- `PLATEAU_EARLY_MINUS_LATE_MAX = 0.03` / `DECLINE_EARLY_MINUS_LATE_MIN = 0.10` (reused verbatim
  from v3e's own validated trend bands).

## HP_SCOPE

HARD_PASS/HARD_FAIL trend+retrieval+cos bands apply to `KL_BLOCK_LAST` ONLY (the arm under test).
`MSE_BLOCK_LAST` is the live control/reproduction -- it IS gated on algebra (`ALGEBRA_FLOOR`,
"the run itself is suspect if the control's own algebra broke") and on `baseline_in_band`, but is
NOT separately HARD_PASS/HARD_FAIL gated on `ret_agree10` (its role is to reproduce the KNOWN
decline as a live-in-this-run control, not to be judged for the swap question). `*_BESTVAL` units
(both arms) are comparison/context, NOT separately gated. `RANDOM_BLOCK`/`CHARPOS`/`shuffled_key`
are integrity-only (positive control / calibration baseline / negative control).

## Cardinality

`EXPECTED_N_UNITS = 17` both run_modes (SMOKE=FULL code path): semantic(10: {MSE,KL} x {DENSE,
BLOCK} x {LAST,BESTVAL}=8, + RANDOM_BLOCK + CHARPOS) + keyed(7: RANDOM_BLOCK posctrl J5, {MSE,KL} x
{LAST,BESTVAL} keyed J5 = 4, {MSE,KL} LAST-shuffled J5 = 2). `cardinality_ok` gates HARD_FAIL if
`len(per_unit) < expected`.

## Discriminator-survives-scale (option B, analytical justification)

Smoke (V_train=3000, 200 steps, dense_eval_every=20, local 43905-concept cache) validates MACHINERY
ONLY: both loss families train end-to-end, 3-way split partitions correctly, trend-slope runs on a
real multi-point trajectory, headline `ret_agree10`/`hi80_cos` fields populate for BOTH arms,
arms-differ hash check fires (codes are NOT bit-identical between MSE and KL arms). SMOKE VERIFIED
(2026-07-04): seed_7 HARD_PASS elapsed=91.2s (MSE ret_agree10=0.5222, KL ret_agree10=0.4003 at
tiny V=3000+3-way-split-with-only-600-TEST scale -- the objective-family DISCRIMINATOR itself is
not expected to show at this tiny scale; both loss families comfortably out-train the small V, and
the true divergence (MSE decline vs KL plateau) is a coverage-ratio effect that only manifests at
V~160k, matching the EXACT same analytical argument the v3/v3c/v3e lineage has used throughout: at
smoke's V_train=3000/batch=32, in-batch pairwise coverage per step is ~3.4% (32*31/2 / (3000*2999/2)),
nowhere near the ~0.32% coverage at FULL V~160k/batch=128 that drives the MSE objective's scale-
collapse -- so smoke CANNOT and does not need to reproduce the plateau-vs-decline discriminator,
only prove the machinery (both loss families train, eval fires, trend-diagnostic runs, units
populate, arms differ). seed_13 smoke run in parallel (same expectation).

## Substrate-too-robust-for-default-regime / baseline-in-band

CHARPOS `ret_agree10` in smoke: seed_7=0.24 (well within (0.05,0.95)). RANDOM_BLOCK `spearman_all`
~0.016 (near-zero, as expected -- calibration floor intact).

## Cell-template mandatory fields (declared)

- `arms_differ_verified: True` (sha256 over all 10 code matrices; verified live in smoke -- would
  raise `META_RULE_AF_VIOLATION` if any two matched)
- `final_metrics_atomicity: tmp_replace` (inherited pattern + this cell's own `write_metrics`/
  checkpoint `os.replace`)
- `except SystemExit: raise` before `except Exception` (no bare except, no `except BaseException`)
  -- grep-verified clean in the core module and both wrapper files (BLOCK_DISPATCH gate passed).
- `cell_chunked: True`, `start_marker_written: True`, `crash_diagnostic_present: True`,
  `heartbeat_present: True`, `defensive_error_checking: passed_all_4_patterns`
- `calibration_check: default_ok_for_this_regime` (identical hyperparameters to the validated
  v3/v3c/v3e lineage; only the RKD loss FORMULA + TAU_KL differ)
- `progress_logging: print_flush_true` (every 200 steps + every dense-eval point + every unit)

## Timeout / dispatch estimate

v3e's single-arm (`in_batch`, NCE-off, 6000 steps, full 177899-concept cache) FULL run landed in
284.7s on remote CUDA (MEASURED@data/exp_encoder_v3e_decline_vs_plateau_v1_seed13/metrics.json:
elapsed_s). This cell trains TWO arms (MSE_RKD + KL_RANK) sharing ONE mining pass (mining is the
dominant one-time cost, ~30-60s at full scale per the v3/v3c lineage's own mining-chunk logs) at the
SAME per-step cost (KL branch reuses the same [batch x batch] matrices, no extra forward pass).
Estimate: mining (~60s, one-time) + 2x training (~2 x 285s = 570s) + eval overhead (17 units,
~2x the single-arm 10-unit overhead, small fraction of total) ~= 700-900s (12-15 min) per seed.
Requested `--timeout 2400` (40 min), ~2.7-3.4x safety margin for remote GPU contention (matches the
lineage's own convention of requesting generous margin when other jobs may share the GPU).

## Composes with

- `T3/EXP_encoder_v3e_decline_vs_plateau_v1_seed_7/13` (the DECLINE_CONTINUES verdict this cell's
  MSE_RKD control arm reproduces live, and whose diagnosis this cell directly answers).
- `notes/research_drill_encoder_target_metric_coarse_cosine_vs_fine_retrieval_2026-07-04.md` (the
  ret_agree10 HARD-PASS/HARD-FAIL bands this prereg's `KL_RET_AGREE10_*` constants are drawn from).
- `notes/research_drill_encoder_cardinality_capacity_ceiling_0.85_reachability_2026-07-04.md`
  (Rank 1 lever this cell operationalizes; Ranks 2-3 remain the escalation path on HARD_FAIL).
- Distinct lane from the concurrently-in-flight v4 (`exp_encoder_v4_convergence_lr_hold_v1_*`,
  LR-schedule convergence fix) and v5 (`exp_encoder_v5_k256_capacity_paired_v1_*`, K=128 vs K=256
  code-capacity) cells -- no shared files edited, distinct anchor/artifact-dir/prereg.

ASCII-only. No emojis. No em dashes.
