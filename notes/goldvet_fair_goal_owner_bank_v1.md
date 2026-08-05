# Gold-VET: experiments/data/goal_owner_fair_v1.jsonl (exp_c5_fair_goal_owner_v1)

**Author:** exp_dev (cell-author role). **Status:** self-VET complete (mechanical + structural + manual
read); FLAGGED for independent Skunkworks (AUDIT-ONLY role) confirmation before treated as canonical,
per task contract point 5.

## Rule (c): triple-check gold before treating a bank as load-bearing

### Pass 1 -- mechanical lexicon-collision check (scratch generation+verification script)
Every one of the 42 rows was checked against the REAL lexicons this pipeline's typer depends on
(`exp_self_extension_grounded_realprose_v1.V2_DESIRE` / `V2_OUTCOME_UNMET` / `V2_OUTCOME_MET`,
reused bit-identical, not re-typed by hand):
- explicit_psych items: S1 MUST carry a V2_DESIRE trigger; action_implied items: S1 MUST NOT.
- S1 MUST NOT accidentally carry an OUTCOME trigger (would corrupt event-slot count).
- S2 (distractor) MUST NOT carry ANY V2_DESIRE or V2_OUTCOME trigger (no cross-contamination that
  would spuriously type the foil as a goal-holder or outcome-bearer).
- S3 MUST carry EXACTLY the declared polarity's trigger (unmet xor met), and MUST NOT carry a
  V2_DESIRE trigger (would spuriously re-open a goal at the outcome sentence).
- owner and foil MUST be same-gender (GENDER lexicon, reused bit-identical) -- the trap must not be
  solvable by gender alone.

First draft: 8/42 problems found and fixed (accidental collisions: "reach"/"finish"/"safe" desire-
lexicon hits inside outcome sentences; "down" outcome-lexicon hits inside action-implied goal
sentences). Final bank: **0/42 problems** (script re-run, disk-verified).

### Pass 2 -- structural gold-VET (this cell's self-test, re-derived independently)
Re-derives the trap property from the SAME resolver the harness scores with (not hand-typed twice,
so this catches authoring bugs the hand-written `foil` field alone would miss): for all 28 core
items, `GeneralRecencyEntityResolver`'s naive whole-passage resolution at the outcome slot lands on
the FOIL, never the OWNER. **28/28 pass** (self-test 1/6, `experiments/exp_c5_fair_goal_owner_v1.py
--self-test`, disk-verified 2026-08-05). This is the operational definition of "genuine recency
trap" -- an item where naive recency happens to land on the owner would not be discriminating.

### Pass 3 -- leakage guard
Every core item has a real foil (not a single-entity item where "resolution" is vacuous); majority-
class baseline is computed structurally from the text (name-occurrence counts), never hand-set, so
it cannot leak the answer. Twins (no-distractor controls) are single-entity by design and are scored
separately (not folded into the divergent-subset capability number).

### Pass 4 -- manual read (this session, all 28 core items read end-to-end)
Confirmed for every item: (a) the outcome clause is CAUSALLY tied to the OWNER's stated/implied goal
(e.g. "wanted to be warned in time about the ice" -> "went down through the ice" is P's own
consequence, not a generic weather/scene sentence); (b) S3 never names either P or D explicitly
(pronoun-only, so a naive substring/name-match heuristic cannot win by luck); (c) the foil's action
in S2 is genuinely unrelated to the goal (no shared outcome vocabulary); (d) gender pairing is
correct throughout (e.g. t08 sid(m)/laurie(m), t20 ann(f)/jo(f)). No item found to need revision at
this pass.

### Pass 5 -- honest-gap confirmation (not a defect, a designed probe)
All 10 action_implied items were confirmed (self-test 5/6) to NEVER type a GOAL event under the
current lexicon typer -- this is the intended probe of the generative-goal-inference gap named in
notes/DRILL_SYNTHESIS_goal_owner_brain_and_fairness.md (Part B), not a bank defect. Their outcome
IS still typed (they carry a valid V2_OUTCOME trigger), so they remain part of the divergent subset
and the system's honest 0/10 score on them is a real, reportable finding.

## Items flagged as uncertain
None. All 28 core + 14 twin items passed all 5 passes with no residual uncertainty. (Per the task
brief's own instruction: "a smaller fully-clean bank beats a larger noisy one" -- if any item had
failed pass 2 or pass 4, it would have been dropped rather than kept with a caveat; none did.)

## What Skunkworks should independently re-check
1. Re-run `experiments/exp_c5_fair_goal_owner_v1.py --self-test` fresh (all 6 checks must pass,
   including the 28/28 genuine-trap structural check) -- do not trust this report's numbers alone.
2. Spot-read a random subset of core items directly against the bank JSONL (not this note) for the
   causal-tie and pronoun-only-S3 properties (passes 4/5 above are the ones most dependent on human
   judgment, least mechanically enforced).
3. Confirm the validity-gate arithmetic in `aggregate()` (experiments/exp_c5_fair_goal_owner_v1.py)
   matches the pre-reg's stated gates (recency_floor<0.5, ceiling>=0.9, scramble collapse >=50%
   relative) -- these gates judge the INSTRUMENT, not the pipeline, and are the load-bearing claim.
