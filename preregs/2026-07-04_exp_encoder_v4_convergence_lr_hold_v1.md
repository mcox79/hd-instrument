# Pre-reg: Encoder v4 -- CONVERGENCE fix diagnostic (plateau-hold LR vs cosine-decay, paired, 2 seeds)

Date: 2026-07-04. Author: exp_dev. Status: PRE-REGISTERED before dispatch.
Core cell: `experiments/exp_encoder_v4_convergence_lr_hold_v1_core.py`
Per-seed wrappers (CHUNKED single-seed-per-cell): `experiments/exp_encoder_v4_convergence_lr_hold_v1_seed_7.py`, `..._seed_13.py`
Anchors: `encoder_v4_convergence_lr_hold_v1_seed7`, `..._seed13` (smoke suffix `_smoke` on each).
Parent cells (read-only imports, NOT edited): v3 (`exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py`), v3c (`exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_core.py`).

## Prior-work check (substrate concept-query, USER-locked 2026-07-01)

Query: "constant learning rate plateau hold versus cosine decay convergence fix declining training
trajectory retrieval headline metric" -> top hit cosine=0.2841 (this arc's own v3c/v3e prose,
expected self-similarity), all other hits <=0.27. NONE at cosine>0.30 for a distinct prior cell.
GENUINELY NOVEL: no prior cell in this lineage runs a paired LR-schedule (cosine-decay vs
constant-hold) comparison, nor gates plateau/decline on the `ret_agree10` trajectory instead of the
DENSE-Spearman-over-random proxy.

## Why this cell exists

v3e (FULL, seed=7, in_batch-RKD-only, nce_weight=0, steps=6000) landed HARD_FAIL DECLINE_CONTINUES
MEASURED@data/exp_encoder_v3e_decline_vs_plateau_v1_seed7/metrics.json: `final_block=0.9187
final_dense=0.6571 final_ret_agree10=0.2112 final_hi80_cos=0.8320 bestval_step=450 (7.5% into the
run) bestval_block_on_test=0.9015 bestval_ret_agree10=0.1920`, trend (on `dense_full`, the cheap
DENSE-Spearman-over-mostly-random proxy logged every 50 steps): `early_half_mean=0.6898 ->
late_half_mean=0.5671, early_minus_late=0.1228` (fired the HARD_FAIL; `final_block<=0.45` was NOT
what triggered it -- 0.9187 is nowhere near that ceiling).

VERIFIED@this session (direct read of the landed metrics.json above): the actual HEADLINE metrics
this arc is locked to (`hi80_cos`, `ret_agree10`) do NOT show the same decline the DENSE-proxy trend
does in this one data point -- FINAL `ret_agree10` (0.2112) is even slightly ABOVE bestval's
(0.1920), and FINAL `block_spearman` (0.9187) beats bestval's (0.9015) too. The DENSE proxy used for
both the trend-diagnostic AND the best-checkpoint SELECTION in the v3c/v3e lineage is measuring a
different quantity than the BLOCK-code headline metrics that actually matter for the 0.85 goal.

## What this cell answers

Two of the USER's three candidate convergence-fix levers are tested directly; the third is answered
analytically from existing evidence:

1. **Lever (a) -- constant/plateau-hold LR vs decay-to-0**: THE mechanism this cell adds. Two PAIRED
   arms (same seed/data/split/mining/objective/K, differing ONLY in LR schedule) in one process:
   `COSINE` (reproduces v3e's schedule exactly -- also the Gate-D positive-control reproduction arm)
   vs `PLATEAU` (linear warmup then HOLD CONSTANT at peak LR for the remainder).
2. **Lever (b) -- early-stop-at-VAL-plateau**: answered by the existing best-by-VAL-selection
   machinery (now selecting by `ret_agree10` on VAL, not the DENSE proxy) applied to BOTH arms; no
   separate arm needed.
3. **Lever (c) -- block-STE gradient vs RKD objective degrading geometry late**: answered empirically
   per arm by comparing the DENSE-proxy trend against a NEW per-checkpoint BLOCK-code Spearman trend
   (both logged at the same cadence): if DENSE declines while BLOCK-code stays flat/high (as v3e's
   one landed data point suggests), that is evidence the DEPLOYED (block-quantized) representation is
   NOT degrading the way the continuous readout is.

## Methodology fix this cell makes (composes with the USER-locked headline-metric rule)

Plateau/decline verdict AND best-checkpoint selection are now driven by the VAL-evaluated BLOCK-code
`ret_agree10` trajectory (the actual headline retrieval metric, computed via `v3._encode_hard_block`
+ `v3._semantic_unit` on a VAL subset every `HEADLINE_EVAL_EVERY` steps), NOT the cheap
DENSE-Spearman-over-random proxy the v3c/v3e lineage used. `dense_full` and a NEW `val_block_spearman`
are still logged per checkpoint (diagnostic transparency + the lever-(c) test above) but no longer
drive the verdict. Disjoint VAL(select)/TEST(report) split retained from v3e; FINAL-step is ALWAYS
the primary gated number, best-by-VAL-on-TEST is secondary context, per the LOCKED methodology this
session.

## Determinism pinning (coordinator mandate, 2026-07-04)

VET caught 2 reproducibility gaps the same day (BCT 0.989 local-preview vs 0.836 remote-official;
v3c 0.7336 (v3b) vs 0.6514 (v3c's own re-run at the same nominal config)), traced to torch-version
drift + no determinism pinning. This cell's `_pin_determinism(seed)` sets
`torch.use_deterministic_algorithms(True, warn_only=True)`, explicitly seeds torch/numpy/python RNGs,
fixes thread count, and sets `CUBLAS_WORKSPACE_CONFIG` for CUDA determinism; `torch.__version__` +
device + whether determinism actually took effect are recorded into `metrics.json["determinism"]`.
**The REMOTE-QUEUE OFFICIAL LANDING is the canonical number; local smoke/preview in this cell is a
MACHINERY gate only** -- stated explicitly in `metrics.json["canonical_source"]` and in every
verdict_msg.

## Compute architecture

Class (b) mixed-with-justification: GPU-batched matmul training loop (adapted from
`v3c._train_student_full`, itself GPU-batched, with the LR-schedule parameterized and the
best-selection/trend metric switched to `ret_agree10`), sequential-only in the outer per-arm/per-unit
eval loop (2 arms x <=7 units + 3 shared integrity units = 17 total, each a batched cleanup-argmax or
block-encode over the codebook). Storage strategy: no_storage/no_composition beyond the existing
bind/unbind/cleanup keyed-unit check (single-hop, not chained-retrieval composition).

## Functional requirements

| Requirement (plain English) | Existing primitive addressed by |
|---|---|
| Train in_batch-RKD-only student at NCE=0, two LR schedules | `_train_student_lrmode` (adapted from `v3c._train_student_full`, objective fixed to in_batch, `lr_mode` parameterized) |
| Test whether constant LR stops the decline | paired COSINE vs PLATEAU arms, same seed/data/mining |
| Select/gate on the metric that actually matters | best-checkpoint selection + trend diagnostic now driven by VAL `ret_agree10` (`_headline_eval`), not the DENSE proxy |
| Test whether block-STE or the objective itself degrades geometry | per-checkpoint `dense_full` vs `val_block_spearman` trend comparison (both logged; `_train_student_lrmode`) |
| Reproduce the known v3e result under a new (determinism-pinned) environment before trusting a fix claim | Gate-D positive control: `COSINE` arm vs `V3E_SEED7_FINAL_*` tolerance check |
| Verify the code stays a valid composable SBC code | `v3._keyed_unit`/shuffled-key (unchanged J=5 convention), per arm |

## Effective-vs-nominal parameter audit

Swept "parameter" is the LR schedule (categorical: cosine vs plateau), not a numeric sweep axis.
`sweep_alignment_verdict: N/A_categorical_arm_not_numeric_sweep`. Both arms see IDENTICAL batches
(same seed drives `_cluster_batch_idx` per arm, same initial weights via `torch.manual_seed(seed)`
inside `_make_student`) -- the ONLY thing that differs between arms is `cur_lr` at each step, so the
comparison is a true paired test (no confound).

## Bracket-includes-discriminating-band

Not a numeric sweep; N/A. The `ret_agree10` trend bands (`RET_PLATEAU_EARLY_MINUS_LATE_MAX=0.02`,
`RET_DECLINE_EARLY_MINUS_LATE_MIN=0.05`) bracket a genuine middle region (`[0.02, 0.05)` ->
AMBIGUOUS), so the discriminator is not by-construction saturated at either extreme.

## Signal-shape compatibility audit

`_train_student_lrmode`'s per-checkpoint `headline_eval_fn` closure (`v3._encode_hard_block` ->
`v3._semantic_unit`) returns the SAME dict shape `_semantic_unit` always has (`spearman_all`,
`ret_agree10`, `hi80_cos`, ...): SHAPE_MATCH, verified by the self-test's tiny synthetic run
(`_hl` closure), which asserts `"ret_agree10" in u and "hi80_cos" in u`.

## Positive-control reproduction (Gate D)

Two positive controls:
1. `v3._keyed_unit("RANDOM_BLOCK", "sbc", ..., J=5, ...)` -- SBC-lossless sanity (`acc_at1 >= 0.98`),
   same primitive/regime already validated in v3/v3b/v3c/v3e. `regime_extension_audit: SHAPE_MATCH`.
2. **NEW this cell**: the `COSINE` arm reproduces v3e seed=7's FULL run (same seed, same config,
   objective=in_batch, nce=0, K=128, steps=6000, batch=128) under a NEW (determinism-pinned)
   environment. Tolerance: `|final_block - 0.9187| <= 0.15`, `|final_ret_agree10 - 0.2112| <= 0.10`,
   `|final_hi80_cos - 0.8320| <= 0.15` (MEASURED@data/exp_encoder_v3e_decline_vs_plateau_v1_seed7/
   metrics.json). Wider tolerance than a bit-exact repro because this is a cross-environment check
   (torch version / determinism-pinning may have shifted numerics even for a "same" config) --
   `regime_extension_audit: SHAPE_DRIFT_with_documented_risk` (documented: possible torch-version
   drift between when v3e landed and when this cell runs). If outside tolerance:
   `COSINE_REPRODUCTION_OUTSIDE_TOLERANCE` MIDDLE_BAND (not an automatic HARD_FAIL of the whole cell,
   since the primary question is trend SHAPE not exact value -- but the fix-confirmed claim is
   withheld pending re-audit).

## CRLB / capacity-feasibility

`crlb_floor_computed=0.901` at K=128 (THEORETICAL@v2/v3/v3b/v3c/v3e prereg: `r_max = sigma_teacher /
sqrt(sigma_teacher^2 + 0.25/K)`, unchanged -- this cell changes only the LR schedule, not K).
`discriminator_reachability: True`.

## Pre-reg bands (HYPOTHESIZED, tagged; first trajectory-level instrumentation of `ret_agree10`)

- `RET_PLATEAU_EARLY_MINUS_LATE_MAX = 0.02` HYPOTHESIZED@this prereg.
- `RET_DECLINE_EARLY_MINUS_LATE_MIN = 0.05` HYPOTHESIZED@this prereg.
- `RET_FINAL_FLOOR_FOR_PLATEAU = 0.05` HYPOTHESIZED@this prereg (generous "still functioning" floor
  -- this cell's claim is about TREND SHAPE, not magnitude; v5 (K=256) is the magnitude question).
- `HI80_COS_FLOOR_FOR_NONCOLLAPSE = 0.50` HYPOTHESIZED@this prereg (v3e measured 0.832; generous
  collapse floor).
- `ALGEBRA_FLOOR = 0.90` (unchanged convention from v3/v3b/v3c/v3e).
- Combined verdict logic (see `_verdict_convergence`): HARD_PASS
  `CONVERGENCE_FIX_CONFIRMED` iff COSINE reproduces DECLINE shape (within Gate-D tolerance) AND
  PLATEAU shows PLATEAU shape AND PLATEAU's final `ret_agree10`/`hi80_cos` do not lose ground vs
  COSINE. HARD_FAIL `LR_SCHEDULE_DOES_NOT_FIX_DECLINE` iff BOTH arms show DECLINE. MIDDLE_BAND
  otherwise (reproduction-outside-tolerance, ambiguous trend, or COSINE unexpectedly not reproducing
  the DECLINE shape at all -- itself a finding, see docstring VERIFIED note about the metric mismatch).

## HP_SCOPE

Trend/floor bands apply to `{COSINE,PLATEAU}_BLOCK_LAST` VAL-`ret_agree10` trajectory only.
`{COSINE,PLATEAU}_*_BESTVAL` (on TEST) is comparison/context, NOT separately gated.
`RANDOM_BLOCK`/`CHARPOS`/`shuffled_key` are integrity-only.

## Cardinality

`EXPECTED_N_UNITS = 17` both run_modes (SMOKE=FULL code path): 2 arms x (semantic 4: DENSE/BLOCK x
LAST/BESTVAL + keyed 3: LAST J5, BESTVAL J5, shuffled-LAST J5) = 14, + shared integrity (RANDOM_BLOCK
semantic + RANDOM_BLOCK keyed posctrl + CHARPOS semantic) = 3. Total 17.

## Arms-must-differ exemption (META_RULE_AF)

`{mode}_DENSE_LAST` vs `{mode}_DENSE_BESTVAL` (and the BLOCK analog) for the SAME `lr_mode` are
EXEMPTED from the must-differ check ONLY when `best_step == steps` (the best-by-VAL checkpoint
legitimately coincides with the final checkpoint -- a data-dependent degenerate case observed in
smoke, not a bug) OR the no-eligible-point fallback fired. Cross-mode and cross-representation
(DENSE vs BLOCK) identity is still a hard failure. `arms_differ_exempted` logs which pairs were
exempted per run (empty list if none).

## Discriminator-survives-scale (option B, analytical justification)

Smoke (V_train=3000, 240 steps, `HEADLINE_EVAL_EVERY=40`) validates MACHINERY ONLY: both LR-mode arms
train end-to-end, the headline VAL trend/best-selection wiring runs on a real multi-point trajectory,
cardinality/integrity/algebra gates hold. SMOKE VERIFIED (2026-07-04, both seeds, local CPU):
seed_7 HARD_PASS `elapsed_s=78.4` (wall 84s), seed_13 HARD_PASS `elapsed_s=79.5` (wall 85s), both
well under the queue_add.py 180s smoke-gate cap; 17/17 units both seeds, `arms_differ_verified=True`.
One iteration during smoke-hardening: `min_step_for_best` is now floored at `warmup` (not just the
5%-of-steps fraction) -- caught because COSINE and PLATEAU's LR schedules are mathematically
IDENTICAL during warmup, so a "best" checkpoint landing inside warmup is bit-identical across arms
by construction (a legitimate degenerate case, not an implementation bug, but one META_RULE_AF should
not silently exempt without the fix -- excluding the warmup ramp from best-checkpoint eligibility is
principled: the model has not yet reached its target LR either). Post-fix, both smokes show
`arms_differ_verified=True` with no exemptions needed. COSINE/PLATEAU both called PLATEAU at smoke
scale (expected -- smoke's tiny V cannot reproduce the true coverage-ratio decline effect; a
`baseline_in_band`-style scale limitation, not a smoke-gate failure). The actual
plateau-vs-decline-under-plateau-hold-LR question needs the true 177899-concept corpus AND the full
6000-step budget -- that IS the FULL dispatch, and the REMOTE-QUEUE OFFICIAL LANDING (not local
smoke) is canonical per the coordinator note above.

## Substrate-too-robust-for-default-regime / baseline-in-band

CHARPOS `ret_agree10` in smoke: 0.24 (well within (0.05, 0.95)). RANDOM_BLOCK `spearman_all`=0.016
(near-zero, calibration floor intact).

## Cell-template mandatory fields (declared)

- `arms_differ_verified: True` (sha256 over all code matrices; verified live in smoke, with the
  documented exemption class above)
- `final_metrics_atomicity: tmp_replace`
- `except SystemExit: raise` before `except Exception` (no bare except, no `except BaseException`)
  -- grep-verified clean in the core module and both wrapper files.
- `cell_chunked: True`, `start_marker_written: True`, `crash_diagnostic_present: True`,
  `heartbeat_present: True`, `defensive_error_checking: passed_all_4_patterns`
- `calibration_check: default_ok_for_this_regime` (identical hyperparameters to the validated
  v3c/v3e lineage; only LR schedule, best-selection metric, and trend-diagnostic metric differ)
- `progress_logging: print_flush_true` (steps=6000 >= the 1800s/30min threshold for MANDATORY
  print-flush per canonical instruction file section 17)

## Timeout / dispatch estimate

v3e's own FULL run (ONE arm, 6000 steps, mining at V=160109, full eval battery) landed in 289.3s on
remote CUDA MEASURED@data/exp_encoder_v3e_decline_vs_plateau_v1_seed7/metrics.json. This cell trains
TWO arms (roughly 2x the training-step cost; mining is shared/one-time) plus a slightly larger eval
battery (17 vs 10 units) and a coarser-but-more-expensive-per-call headline eval (block-encode +
semantic_unit every 500 steps instead of a cheap dense-sign pass every 50). Estimated wall time:
~600-900s (10-15 min) per seed on GPU. Requested `--timeout 3600` (1 hour), a wide margin (4-6x
estimate) consistent with this lineage's GPU-is-fast track record and queue_add.py's own guidance
(estimates <=14400 need no additional justification).

## Composes with

- `T3/EXP_encoder_v3e_decline_vs_plateau_v1` (the DECLINE_CONTINUES result this cell tests a fix for).
- `notes/encoder_rescue_plan_converged_diagnosis_2026-07-04.md` (R1/R2 rescue-battery sequencing;
  this cell is a cheap lever-(a) test that can run BEFORE committing to the more expensive
  objective-family changes R2/R3/R4 if it succeeds, or rule out lever (a) cheaply if it doesn't).
- Sibling cell `experiments/exp_encoder_v5_k256_capacity_paired_v1_core.py` (problem 2 of the same
  v3e-exposed pair: code-capacity/K-resolution, kept as a SEPARATE cell so the K-sweep is not
  confounded with this cell's unvalidated LR-schedule change).

ASCII-only. No emojis. No em dashes.
