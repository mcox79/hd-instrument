# Pre-registration: Encoder Migration Step 1b v4 -- Joint Reverify + NCE Relock Curriculum

**Date:** 2026-07-07
**Author:** exp_dev (cell author/prover)
**Anchor:** `encoder_migration_step1b_v4_joint_reverify_relock_v1`
**Cell:** `experiments/exp_encoder_migration_step1b_v4_joint_reverify_relock_v1_core.py`
**Wrappers (CHUNKED single-seed-per-cell):**
  `experiments/exp_encoder_migration_step1b_v4_joint_reverify_relock_v1_seed_7.py`
  `experiments/exp_encoder_migration_step1b_v4_joint_reverify_relock_v1_seed_13.py`

## Trigger and dispatch task

Director (Research) dispatched an exp_dev cycle to resolve the encoder's
semantic-vs-keyed-algebra trade-off (Stage-2 blocker), per
`notes/research_encoder_nce_margin_tradeoff_2x_drill_2026-07-06.md`'s Rank-1
lever: reuse the already-trained v3c NCE=0 checkpoints, then a short terminal
NCE-relock fine-tune to recover keyed algebra without destroying the NCE=0
semantic fidelity.

## PRE-DISPATCH FINDING that reshaped this cell's scope (MANDATORY disclosure)

Before authoring, exp_dev re-verified the drill's premise against the FULL
per_unit data (not just verdict_msg) of all 5 already-landed v3c FULL seeds
(`data/exp_encoder_migration_step1b_v3c_paired_rkd_only_seed_{7,13,23,29,31}/metrics.json`).

**MEASURED@those 5 files:** the INBATCH-RKD-only arm (nce_weight=0, same MLP
student, same K=128 block-argmax SBC code) ALREADY jointly clears both bars,
5/5 seeds:

| seed | INBATCH_BLOCK spearman | INBATCH_BLOCK keyed@J5 acc1 |
|---|---|---|
| 7  | 0.8969 | 1.0000 |
| 13 | 0.8865 | 1.0000 |
| 23 | 0.8522 | 1.0000 |
| 29 | 0.8968 | 1.0000 |
| 31 | 0.8963 | 1.0000 |

This was masked by two things: (1) the v3c cell's own `_verdict_full_paired`
short-circuits on `GLOBAL_BLOCK`'s keyed gate FIRST (which genuinely fails,
0.03-0.32) before ever reaching `INBATCH_BLOCK`'s keyed gate (which passes);
(2) the 2026-07-06 drill explicitly flagged INBATCH_BLOCK's keyed acc@1 as
"never reached/reported... Flag as inference, not an on-disk-verified number"
and guessed (incorrectly) it was "likely equally or more degraded" than
GLOBAL's. The data was already on disk and already correct; nobody had read
past the short-circuited verdict_msg.

**ONE VERIFICATION GAP remains:** the v3c cell computed a `shuffled_key`
negative control (proves the code isn't a degenerate always-decodes-the-same-
thing artifact) only for `GLOBAL_BLOCK`, never for `INBATCH_BLOCK`. This cell's
Phase 1 closes that gap using the EXISTING checkpoint (no retraining).

This changes the cell's job: it is no longer "does the relock recipe work" in
isolation -- it is "(a) confirm/complete the verification of an already-landed
win on INBATCH, and (b) test the drill's literal relock recipe on the arm that
genuinely still fails (GLOBAL)." Both phases reuse existing checkpoints; ZERO
new training is required for phase 1, and phase 2's training budget is a
small fraction of the original v3c FULL run (182.1s wall for both arms over
1800 steps; this cell trains GLOBAL alone for at most 450 steps).

## Compute architecture

Class: **(a) batched-GPU** for FULL (all torch matmul ops on the full 177899-
concept teacher cache, batch=128 relock training, chunked cleanup argmax).
Class: **(b) sequential-CPU** for smoke (self-contained synthetic bootstrap,
tiny V=400, n_dim=256; deliberately CPU to keep local smoke fast and
GPU-independent per the RESOURCE RULE that local is smoke-only).
Storage strategy: **no_storage / no_composition beyond single-hop keyed
bind-unbind** (the `_keyed_unit` bind/unbind roundtrip is the SAME single-hop
SBC composability test used throughout the v2/v3/v3b/v3c lineage; not a
chained/multi-hop composition, so the sharded-storage mandate for
compositional cells does not apply here).

## Functional requirements

| Requirement | Existing chain-grade primitive |
|---|---|
| Verify an existing arm's algebra claim is not a degenerate artifact | `v3._keyed_unit(..., shuffled_key=True)` (already-proven negative control, used for GLOBAL_BLOCK in v3c; extended here to INBATCH_BLOCK) |
| Reproduce a prior arm's semantic/keyed numbers from its saved checkpoint | `v3._encode_hard_block` + `v3._semantic_unit` + `v3._keyed_unit`, applied to a RELOADED `_ckpt_best_*.pt` (new use: prior cells never reloaded a checkpoint for pure re-verification) |
| Reintroduce a margin-inducing loss term on top of a converged/near-converged checkpoint for a short schedule | NEW: `_run_relock` (this cell), adapted from `v3c._train_student_full`'s loop body, parameterized on LR (v3c hardcodes `v3.LR`) and warm-started from an externally-supplied `state_dict` (v3c's own resume format requires `{opt, gen_state, step, dense_traj, best_score, ...}` which the read-only source best-checkpoint does not have) |

## Prior-work check (substrate-KB concept-query, USER-locked 2026-07-01)

Query: "NCE curriculum sequenced contrastive loss margin decodability keyed
algebra semantic tradeoff encoder" -> top hit cosine=0.249 ('ability to change
sequence', WordNet), all other hits <=0.2412. NONE at cosine>0.30 in the
substrate-KB atom index (expected: that index is a WordNet/note-prose lexical
index, not a code-history index). **The real prior-work check for this cell
is the on-disk encoder-lineage re-derivation above.**

**Adjacent-lineage flag (not litigated by this cell, surfaced for Director):**
a separate, later lineage (`exp_encoder_v11_gsbc_graded_sparse_v1`,
`exp_encoder_v12_gsbc_gwta_expansion_v1`, `exp_encoder_gsbc_gradedcode_retrieval_v1`;
all dated 2026-07-05, BEFORE the 2026-07-06 drill) uses a DIFFERENT code
family (graded Sparse-Block-Code + circular-conv binding, FlyHash-style
expansion) and ALSO lands HARD_PASS jointly clearing retrieval
(ret_agree10 0.31-0.68) and algebra (keyed@J5=1.000) at the same full-scale
teacher cache (n_train=160109). That lineage's own verdict flags "Next:
density dial + full-M=177899 composition VET" as still open. This cell does
not re-analyze GSBC; the finding is reported to Director as a second,
independent signal that the semantic-vs-algebra trade-off is more tractable
than the 2026-07-06 drill's framing suggested.

## Design (2 phases, per seed)

**Phase 1 -- REVERIFY (pure eval, no training):** reload the existing
`_ckpt_best_INBATCH.pt` from the ALREADY-LANDED v3c FULL run for this seed
(`data/substrate_concept_encoder_v1b_v3c_full_paired_seed{N}/`), reproduce the
held-out split identically (same seed, same `np.random.default_rng` +
permutation logic as v3c), recompute `INBATCH_BLOCK` codes, and run:
dense spearman reproduction, keyed@J5 real-key reproduction, keyed@J5
shuffled-key control (the missing gap).

**Phase 2 -- RELOCK (short training, GLOBAL arm only):** reload the existing
`_ckpt_best_GLOBAL.pt` (same source directory), reintroduce
`nce_weight=0.5` (MEASURED@v2/v3b: the constant weight known to deliver
keyed acc@1~1.0 given enough steps) at a REDUCED learning rate
(`RELOCK_LR_FULL=2e-4`, 0.2x of `v3.LR=1e-3`; HYPOTHESIZED@QAT literature,
Krishnamoorthi arXiv:1806.08342, reduced-LR post-hoc fine-tune avoids
"catastrophic disruption") for `RELOCK_STEPS_FULL=450` steps
(THEORETICAL: 0.25 * v3c's ACTUAL trained schedule, `v3.MID_STEPS=1800` --
this matches the 2026-07-06 drill's own "25% of original = no longer short"
HARD_FAIL ceiling, RESCALED from the drill's illustrative 40,000-step
assumption, which does not match the true 1800-step schedule this checkpoint
was actually trained under). Eval every 25 steps (18 points), tracking dense
spearman and keyed@J5 (real key) at each point; a shuffled-key control is run
once at the final relock step.

## Bands (falsifiable predictions)

**REVERIFY gate (Phase 1, INBATCH_BLOCK):**
- HARD_PASS: dense spearman >= 0.82 AND keyed@J5 (real) >= 0.90 AND
  shuffled@J5 <= 0.10 (no leak)
- Integrity override: shuffled@J5 > 0.10 -> HARD_FAIL regardless of other numbers

**RELOCK gate (Phase 2, GLOBAL_BLOCK), rescaled to the ACTUAL 1800-step schedule:**
- HARD_PASS: exists an eval step S <= 450 where keyed@J5(S) >= 0.90 AND
  dense(S) >= 0.70, AND keyed@J5 does not relapse below (crossing_value - 0.05)
  for any later observed step through 450, AND the shuffled-key control at the
  FINAL relock step stays <= 0.10 (no leak)
- HARD_FAIL: keyed@J5 never reaches >= 0.70 through step 450 (the recipe needs
  longer than "short and monitored" to work), OR dense < 0.60 at the step
  keyed@J5 first clears 0.90 (recovery only by destroying the semantic gain)
- MIDDLE_BAND: partial signal (max keyed@J5 in [0.70,0.90) with final dense
  >= 0.65), neither clean pass nor clean fail

**Vacuous-target guard (this cell's `baseline_in_band` variant, META_RULE_AG):**
GLOBAL_BLOCK_START (pre-relock) keyed@J5 MUST be < 0.5, else the relock
experiment target is not genuinely failing and the test is vacuous
(MEASURED@v3c per-seed data: 0.03-0.32, comfortably below 0.5).

**Overall cell verdict (combines both phases):**
- If REVERIFY passes -> HARD_PASS, headline "ALREADY_JOINT_SOLVED_VIA_INBATCH",
  RELOCK result reported as a secondary finding on the separately-failing arm
- Elif RELOCK passes -> HARD_PASS, headline "RELOCK_RECOVERS_GLOBAL_JOINT"
- Elif either shows partial signal -> MIDDLE_BAND
- Else -> HARD_FAIL, "JOINT_REQUIREMENT_NOT_MET_EITHER_ARM"

## CRLB / capacity-feasibility

`crlb_floor_computed = 0.901` at K=128 (r_max = sigma_teacher /
sqrt(sigma_teacher^2 + 0.25/K); THEORETICAL, CITED@v2/v3/v3b/v3c prereg
lineage, unchanged -- this cell changes only nce_weight/lr/step-budget for a
fine-tune phase, not the code family or K).
`discriminator_reachability: true` -- HARD_PASS bands (0.82 dense, 0.90 keyed)
are both already ACHIEVED at least once in this exact code family (v3c
INBATCH_BLOCK), so they are empirically, not just theoretically, reachable.

## Cardinality

`EXPECTED_N_UNITS = 9` per seed run: semantic::INBATCH_BLOCK_REVERIFY,
keyed::INBATCH_BLOCK_REVERIFY::J5, shuffled_key::INBATCH_BLOCK_REVERIFY::J5,
semantic::GLOBAL_BLOCK_START, keyed::GLOBAL_BLOCK_START::J5,
semantic::GLOBAL_BLOCK_RELOCKED, keyed::GLOBAL_BLOCK_RELOCKED::J5,
shuffled_key::GLOBAL_BLOCK_RELOCKED::J5, keyed::RANDOM_BLOCK::J5 (SBC
lossless-prior sanity, matches v3c's `posc["acc_at1"] < 0.98` style gate)
= 3 semantic + 4 keyed(real-key) + 2 shuffled-key = 9. Verdict logic
HARD_FAILs on `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H` if
`len(per_unit) < 9`.

**Caught by smoke (2026-07-07):** an earlier draft of the cell declared
`EXPECTED_N_UNITS = 10` (an arithmetic slip in the tally comment, not a
missing/broken unit -- self-test's own fake-unit fixtures already used 9
correctly the whole time). Local smoke's cardinality gate correctly
HARD_FAILed `9/10` before any FULL dispatch was attempted; fixed to the true
count (9) and smoke re-run to confirm HARD_PASS.

## Cell-template checklist (self-verified before dispatch)

- [x] `arms_differ_verified`: sha256 over 4 code arms (INBATCH_BLOCK_REVERIFY,
  GLOBAL_BLOCK_START, GLOBAL_BLOCK_RELOCKED, RANDOM_BLOCK)
- [x] `final_metrics_atomicity: tmp_replace` (metrics + relock checkpoint both
  os.replace)
- [x] `except SystemExit: raise` / `except KeyboardInterrupt: raise` BEFORE
  `except Exception` (grep-verified: no bare `except:` or `except BaseException`)
- [x] `crlb_floor_computed` + `discriminator_reachability` declared
- [x] `baseline_in_band` variant (GLOBAL_BLOCK_START keyed < 0.5) gated in
  verdict logic
- [x] discriminator-survives-scale: option (B) analytical, same precedent as
  v3/v3b/v3c (smoke's synthetic V cannot reproduce the real discriminator)
- [x] HARD_PASS strictly-above-floor bands (0.82/0.90/0.70/0.90, not
  at-floor `>=`)
- [x] `cardinality_ok` gate wired into verdict logic (META_RULE_H)
- [x] per-unit failure-class instrumentation via `_run_unit` wrapper
  (RuntimeError/ValueError/IndexError, no bare except)
- [x] `calibration_check: "default_ok_for_this_regime"` (identical
  hyperparameters inherited from validated v3/v3b/v3c lineage; only the
  relock phase's nce_weight/lr/step-budget are new, pre-registered changes)
- [x] all numbers in cell/prereg comments tagged MEASURED@/HYPOTHESIZED@/
  THEORETICAL@/CITED@/VERIFIED@
- [x] `cell_chunked: true` (per-seed wrappers seed_7.py / seed_13.py; a
  runner-death loses one seed only)
- [x] `start_marker_written`, `crash_diagnostic_present`, `heartbeat_present`,
  `defensive_error_checking: passed_all_4_patterns`
- [x] `progress_logging: print_flush_true` (this cell's `--timeout` will be
  well under 1800s, but flush=True is used throughout regardless)

## Self-test (local, .venv, CPU, synthetic)

`python experiments/exp_encoder_migration_step1b_v4_joint_reverify_relock_v1_core.py --self-test`
Covers: relock LR schedule; trajectory crossing/stability analysis (stable,
unstable, never-crosses cases); end-to-end relock training on an EXTERNALLY
loaded state dict (not v3c's own resume format) with a weight-change
assertion (catches a no-op training loop); in_batch objective path;
land_idx-required-for-global guard; checkpoint/resume growth; all 6 verdict
bands (already-solved, relock-recovers, shuffled-key-leak,
vacuous-relock-target, neither-arm-passes, cardinality-breach).
Result: PASS, elapsed 66.33s (measured 2026-07-07 on .venv/Scripts/python.exe).

## Smoke (local, self-contained synthetic bootstrap; machinery-only)

`python experiments/exp_encoder_migration_step1b_v4_joint_reverify_relock_v1_seed_7.py --smoke`
Builds tiny synthetic "existing checkpoints" via `v3c._train_student_full`
(the SAME helper v3c's own self-test uses) at nce=0 for 20 steps on V=400,
n_dim=256 synthetic data -- no external file dependency, no GPU, no real
corpus. Exercises: checkpoint-load-from-external-state-dict, Phase 1 reverify
eval, Phase 2 relock training + eval, shuffled-key control, verdict logic.
Per DISCRIMINATOR-MUST-SURVIVE-SCALE option (B) (same precedent as v3/v3b/v3c
prereg): smoke's synthetic V cannot reproduce the real semantic/algebra
discriminator; it validates MACHINERY ONLY. Result recorded in the exp_dev
completion report (this file is updated post-smoke if the result changes the
dispatch decision).

## Dispatch plan

FULL -> `overnight_queue` (GPU), 2 seeds (7, 13; matches the v3c "chunked
single-seed-per-cell, 2-seed minimum for chain-grade promotability" precedent
established in this same lineage after Skunkworks flagged v3b's single-seed
NCE finding as MM_STANDARD not chain-grade). `--timeout` computed from
measured smoke wall time via the standard formula, generously padded for the
FULL corpus's larger teacher-cache load + mining overhead (see completion
report for the actual computed value). NOT a full GPU-day: the total relock
training budget across both arms combined is at most 450 steps (vs. the
original v3c FULL's 1800 steps x 2 arms = 3600 step-equivalents), and Phase 1
is pure evaluation (zero training steps).

If HARD_PASS on `ALREADY_JOINT_SOLVED_VIA_INBATCH` (expected outcome per the
pre-dispatch finding above): recommend Director route this to Skunkworks for
a landed-VET re-tier of the existing v3c 5-seed cells (the underlying win was
already measured 2026-07-04; this cell only adds the missing negative
control), NOT a request for further GPU cells on this specific question.

If RELOCK also clears HARD_PASS on GLOBAL: recommend escalating to the
remaining 3 seeds (23, 29, 31) for a full 5-seed chain-grade replicate,
matching v3c's own precedent.

If neither phase passes cleanly (MIDDLE_BAND or HARD_FAIL): report honestly;
per the 2x-drill's own decision table, escalate to Rank 2 (rank-aware/
anisotropic loss reweighting, ScaNN-style) stacked on the ALREADY-CONFIRMED
INBATCH win, not a repeat of this recipe at a longer budget (that would
reproduce the corruption dynamic this cell exists to avoid).

ASCII-only. No emojis. No em dashes.
