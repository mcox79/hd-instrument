# Pre-reg: Encoder v6 -- does plateau-hold LR add lift ON TOP of K=256? (1 seed, cheap follow-up)

Date: 2026-07-04. Author: exp_dev. Status: PRE-REGISTERED before dispatch.
Core cell: `experiments/exp_encoder_v6_k256_plateau_followup_v1_core.py`
Wrapper (single seed for this first pass; CHUNKED convention still applies if a seed_13 replicate
is added later): `experiments/exp_encoder_v6_k256_plateau_followup_v1_seed_7.py`
Anchor: `encoder_v6_k256_plateau_followup_v1_seed7` (smoke suffix `_smoke`).
Parent cells (read-only imports, NOT edited): v3, v3c (lineage standard), and
`exp_encoder_v4_convergence_lr_hold_v1_core` (imports `_train_student_lrmode`/`_reload_best_student`
only; this cell's OWN `data/substrate_concept_encoder_v6_k256_plateau*` artifact dirs never collide
with v4's `data/substrate_concept_encoder_v4_convergence*`).

## Prior-work check (substrate concept-query, USER-locked 2026-07-01)

Query: "plateau hold learning rate additional lift on top of K256 block code ceiling effect combined
levers retrieval agreement" -> top hit cosine=0.2841 (this arc's own prose; the v4/v5 sibling cells'
own prose at cosine=0.27-0.29, expected -- same arc, related-but-distinct cells). NONE at cosine>0.30
for a distinct prior cell testing THIS composition. GENUINELY NOVEL: no prior cell trains a K=256
model under plateau-hold LR.

## Why this cell exists

Both sibling cells this session landed positive results at K=128's operating point (v4: PLATEAU beats
COSINE by +0.02 to +0.03 ret_agree10 across both seeds, once a Gate-D verdict bug was fixed; v5: K=256
beats K=128 by +0.093 ret_agree10 at seed7, HARD_PASS). This cell asks the natural next question: at
the NEW (K=256) operating point, does the plateau-hold lift PERSIST, or does K=256 already capture
most of the fixable headroom (a ceiling effect that would make the LR lever moot once K is fixed)?

## What this cell answers

TWO PAIRED ARMS, BOTH at K=256 (kb=256, blk_l=16), same seed/data/split/mining/objective, differing
ONLY in LR schedule: `K256_COSINE` (Gate-D positive control, reproduces v5 seed7's K256 arm) vs
`K256_PLATEAU` (the new question). Isolates the LR-mode question at K=256 specifically -- does NOT
re-litigate the K question (v5 already answered it).

## Compute architecture

Class (b) mixed-with-justification: GPU-batched matmul training loop
(`exp_encoder_v4_convergence_lr_hold_v1_core._train_student_lrmode`, REUSED UNMODIFIED -- already
parameterizes both `kb`/`blk_l` and `lr_mode`), sequential-only in the outer per-arm/per-unit eval
loop (17 units total). Storage strategy: no_storage/no_composition beyond the existing keyed-unit
check.

## Functional requirements

| Requirement (plain English) | Existing primitive addressed by |
|---|---|
| Train K=256 student under two LR schedules | `_train_student_lrmode` (REUSED from v4, unmodified) |
| Isolate the LR question from the already-answered K question | BOTH arms fixed at kb=256/blk_l=16 |
| Reproduce v5's K256 result under this cell's own split/environment before trusting a delta | Gate-D check vs `V5_SEED7_K256_FINAL_*` |
| Detect a ceiling effect (LR lever stops mattering once K is fixed) | `PLATEAU_ADDS_NO_LIFT_AT_K256` HARD_FAIL branch |

## Effective-vs-nominal parameter audit

Swept "parameter" is LR schedule (categorical), K is HELD FIXED at 256 for both arms.
`sweep_alignment_verdict: N/A_categorical_arm_not_numeric_sweep`. Both arms see IDENTICAL batches
(same seed) -- true paired test of LR schedule alone, at the K=256 operating point.

## Bracket-includes-discriminating-band / Signal-shape / Positive-control (Gate D)

`DELTA_RET_AGREE10_HARD_PASS_MIN=0.02` sits in a genuine middle region (`(0, 0.02)` -> MIDDLE_BAND),
matching v4's own observed +0.02-0.03 cross-seed lift at K=128 (informs this band's magnitude).
Gate D: `K256_COSINE` vs v5 seed7's landed K256 arm (`spearman=0.9482`, `ret_agree10=0.2902`,
`hi80_cos=0.8298` MEASURED@data/exp_encoder_v5_k256_capacity_paired_v1_seed7/metrics.json:
recovery.K256.final), tolerance identical to v4's Gate-D check (block/hi80 <=+-0.15, ret <=+-0.10).
`regime_extension_audit: SHAPE_MATCH` (same K, same split methodology as v5's own; only the LR
schedule of the COSINE-labeled arm here is identical to v5's single schedule, so an exact bit-match
is plausible given determinism pinning, same as v4's COSINE arm bit-matched v3e).

## CRLB / capacity-feasibility

`crlb_floor_computed=0.9466` at K=256 (THEORETICAL, same formula/anchor as v5; unchanged by LR
schedule). `discriminator_reachability: True`.

## Pre-reg bands (HYPOTHESIZED, tagged)

- `DELTA_RET_AGREE10_HARD_PASS_MIN = 0.02` HYPOTHESIZED@this prereg (matches v4's observed cross-seed
  LR-lift magnitude at K=128).
- `DELTA_HI80_COS_REGRESSION_FLOOR = -0.02` HYPOTHESIZED@this prereg (same convention as v4/v5).
- `ALGEBRA_FLOOR = 0.90` (unchanged lineage convention).
- Verdict: HARD_PASS `PLATEAU_ADDS_LIFT_AT_K256` iff delta_ret `>= 0.02` and no calibration
  regression. HARD_FAIL `PLATEAU_ADDS_NO_LIFT_AT_K256` iff delta_ret `<= 0` (ceiling-effect finding).
  MIDDLE_BAND `PLATEAU_MARGINAL_AT_K256` otherwise.

## HP_SCOPE

Delta band applies to `K256_{COSINE,PLATEAU}_BLOCK_LAST` FINAL only. `*_BESTVAL` is context.
`RANDOM_BLOCK`/`CHARPOS`/`shuffled_key` are integrity-only.

## Cardinality

`EXPECTED_N_UNITS = 17` both run_modes (same composition as the v4 sibling cell: 2 arms x
(semantic 4 + keyed 3) + shared integrity 3 = 17).

## Discriminator-survives-scale (option B)

Smoke (V_train=3000, 240 steps) validates MACHINERY ONLY. SMOKE VERIFIED (2026-07-04, seed_7, local
CPU): HARD_PASS, `elapsed_s=90.1` (wall 101s, under the 180s smoke-gate cap), 17/17 units,
`arms_differ_verified=True`. The actual ceiling-effect question needs the true 177899-concept corpus
-- REMOTE-QUEUE OFFICIAL LANDING is canonical per the coordinator note (determinism pinning identical
to v4/v5).

## Scope note: single seed for this first pass

Unlike v4/v5 (2 seeds each), this cell ships seed=7 ONLY for the first pass -- it is a cheap,
narrowly-scoped follow-up chaining from two ALREADY 2-seed-replicated findings (v4's LR-lift and v5's
K-lift), not a new primary claim. A seed_13 replicate is a cheap addition if this seed's read is
ambiguous or surprising (same convention v3c itself used to justify starting scope; per
`feedback_paired_trials_mandatory_for_arm_comparison_discriminators_2026-07-04`, the LOAD-BEARING
pairing requirement -- same seed/data for the two arms being compared -- is satisfied within this
single run; what a 2nd seed would add is cross-seed ROBUSTNESS of the delta, not the pairing itself).

## Cell-template mandatory fields (declared)

`arms_differ_verified: True` (with exemption logging for the same warmup-region degenerate case
documented in v4), `final_metrics_atomicity: tmp_replace`, `except SystemExit: raise` before
`except Exception` (grep-verified clean), `cell_chunked: True`, `start_marker_written: True`,
`crash_diagnostic_present: True`, `heartbeat_present: True`,
`defensive_error_checking: passed_all_4_patterns`, `calibration_check: default_ok_for_this_regime`,
`progress_logging: print_flush_true`.

## Timeout / dispatch estimate

v5's own FULL run (2 arms, K=128 and K=256, 6000 steps each) landed in 335-340s on remote CUDA
MEASURED@data/exp_encoder_v5_k256_capacity_paired_v1_seed7/metrics.json. v4's own FULL run (2 arms,
headline-eval overhead) landed in ~285s. This cell combines v5's per-arm K=256 training cost with
v4's headline-eval overhead for 2 arms -- estimated wall time ~350-450s (6-8 min). Requested
`--timeout 3600` (1 hour), a wide margin consistent with this lineage's GPU-is-fast track record.

## Composes with

- `T3/EXP_encoder_v4_convergence_lr_hold_v1` (the LR-lift-at-K128 finding this cell tests for
  persistence at K=256).
- `T3/EXP_encoder_v5_k256_capacity_paired_v1` (the K-lift finding this cell holds fixed as the new
  operating point; Gate-D reference).

ASCII-only. No emojis. No em dashes.
