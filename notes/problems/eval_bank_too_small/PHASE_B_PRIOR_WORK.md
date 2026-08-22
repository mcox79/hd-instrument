# PHASE B prior-work check — the mechanism is ALREADY BUILT (do NOT re-build it)

**Done 2026-08-22 at the owner's explicit instruction ("make sure the other component isn't already
built first"), BEFORE any Phase-B build.** Stayed at the existence/aggregate-verdict level; did NOT
run the organ on the eval items or read per-item MET/UNMET output (that would contaminate the bank,
which is not yet frozen). Deep diagnostic is deferred to post-freeze.

## What already exists (query counts quoted, per the two-archives rule)

| component | status | evidence |
|---|---|---|
| goal-**owner** resolution | BUILT, partially works | `hdlab/goal_owner_select.py`; `goal owner` = 19 cells / 17 landed, incl. `exp_c5_fair_goal_owner_primacy_v1` INSTRUMENT_VALID, `exp_c5_primacy_trap_endtoend_promoted_organ_v1` |
| goal **typing** (desiderative/aspectual) | BUILT | `goal typing` = 10 landed, incl. `exp_c5_generative_goal_typing_action_frame_v1` HARD_PASS, `exp_c5_desiderative_aspectual_partition_goal_typing_v1` MIDDLE_BAND |
| outcome-**valence** typing (goal-relative) | BUILT, **HARD_FAIL on open vocab** | `verb_lexical_similarity` + congruence; `exp_consequence_learning_loop_oov_outcome_verb_valence_v1` = **HARD_FAIL**; `goal-outcome` = 20 cells / 17 landed |
| situation-model / causal integration | prior work exists | `situation model` = 43 cells / 37 landed |

## The reframe for Phase B

**Phase B is NOT a greenfield build. It is: diagnose why the existing outcome-valence organ
HARD_FAILs, and fix the binding sub-component brain-foundationally.** The organ that scores 0.4722
(below the 0.6389 floor) on the bank IS this already-built mechanism. Building a "new" goal-outcome
comprehension mechanism would repeat `exp_consequence_learning_loop_oov_outcome_verb_valence_v1`.

## Leading hypothesis (pending post-freeze diagnosis — NOT a conclusion)

The failing piece is **open-vocabulary outcome-valence typing**: deciding whether an outcome verb the
system was never handed (`croak`, `apoptose`, ...) satisfies or thwarts the goal. This is meaning-
bound, and the project's Phase-1 bottleneck is exactly "thin meaning supply." So the likely root
cause is not the goal-outcome wiring but the meaning channel feeding it. Phase B must first
DISSOCIATE: is the failure in (a) owner resolution, (b) goal typing, or (c) outcome-valence meaning
supply? — then fix the one that binds, on the FROZEN bank, per the measurement bar.

## Contamination discipline

The deep read of the HARD_FAIL's per-item analysis, and any run of the organ against the new bank,
happens ONLY after `goal_bearing_modern_eval_v2.jsonl` is frozen. Until then this file stays at the
"what exists / what its aggregate verdict was" level.
