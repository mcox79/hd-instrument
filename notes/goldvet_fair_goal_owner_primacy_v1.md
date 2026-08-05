# Gold-VET: 20 new primacy-trap rows in experiments/data/goal_owner_fair_v1.jsonl
(`trap_type: "primacy"`, exp_c5_fair_goal_owner_primacy_v1)

**Author:** exp_dev (cell-author role). **Status:** self-VET complete (mechanical + structural +
manual read); FLAGGED for independent Skunkworks (AUDIT-ONLY role) confirmation before treated as
canonical, per task contract point 5 (same discipline as the v1 bank's own gold-VET).

## Rule (c): triple-check gold before treating a bank as load-bearing

### Pass 1 -- mechanical lexicon-collision check (scratch generation+verification script)
Every one of the 20 new rows was checked against the REAL lexicons this pipeline's typer depends on
(`exp_self_extension_grounded_realprose_v1.V2_DESIRE` / `V2_OUTCOME_UNMET` / `V2_OUTCOME_MET`,
reused bit-identical):
- S1 and S3 (the two D-filler sentences) MUST NOT carry ANY V2_DESIRE / V2_OUTCOME_UNMET /
  V2_OUTCOME_MET trigger (no cross-contamination that would spuriously type the foil).
- S1 and S3 MUST name the foil; MUST NOT name the owner (the first-mention / nearest-subject trap
  by construction).
- S2 MUST name the owner; MUST NOT name the foil; explicit_psych rows MUST carry a V2_DESIRE
  trigger, action_implied rows MUST NOT; S2 MUST NOT carry an OUTCOME trigger.
- S4 MUST name NEITHER owner nor foil (pronoun-only); MUST carry EXACTLY the declared polarity's
  trigger (unmet xor met); MUST NOT carry a V2_DESIRE trigger.
- Mention count MUST be foil=2 (S1+S3), owner=1 (S2) EXACTLY -- the structural cause of the
  majority-baseline trap.
- owner and foil MUST be same-gender.

Since S2 and S4 REUSE the core bank's own already-vetted goal/outcome sentences VERBATIM (only S1
and S3, entirely new short filler sentences, needed fresh lexicon checking), the collision-risk
surface was much smaller than the original 42-row bank build. Result: **0/20 problems on the first
draft** (script re-run, disk-verified 2026-08-05) -- no fix cycle was needed, unlike the original
bank's 8/42 first-draft defects.

### Pass 2 -- structural gold-VET (this cell's self-test, re-derived independently)
Re-derives the FOUR-WAY trap property from the SAME resolvers/baselines the harness scores with
(not hand-typed twice): for all 20 items, `GeneralRecencyEntityResolver`'s naive whole-passage
resolution, the first-mention baseline, the nearest-subject baseline, AND the majority-class
baseline ALL land on the FOIL, never the OWNER. **20/20 pass on all four baselines simultaneously**
(self-test 1/5, `experiments/exp_c5_fair_goal_owner_primacy_v1.py --self-test`, disk-verified
2026-08-05). This is the operational definition of "genuine four-way (primacy+subject+recency+
majority) trap" -- an item where any ONE of the four baselines happened to land on the owner would
not close the confound the task brief names.

### Pass 3 -- leakage guard + mention-count-by-construction
Every item's foil is named EXACTLY twice (S1, S3) and owner EXACTLY once (S2) -- self-test 2/5,
disk-verified. This is what mechanically FORCES the majority-baseline trap (not a coincidence of
this particular bank; it is the designed structural cause). S4 never names either entity (pronoun-
only), so the trap cannot be won by a naive substring/name-match heuristic either.

### Pass 4 -- manual read (this session, all 20 new items read end-to-end)
Confirmed for every item: (a) S2 (the goal sentence) and S4 (the outcome sentence) are REUSED
VERBATIM from the core bank's own already-manually-verified items (see
notes/goldvet_fair_goal_owner_bank_v1.md Pass 4) -- the causal tie between P's goal and the outcome
clause was already hand-verified there, and copying the sentence text unchanged preserves that
verification exactly (no re-authoring risk); (b) the two NEW filler sentences (S1, S3) describe a
genuinely unrelated action for the foil (no shared vocabulary with the goal/outcome, confirmed
against the lexicon check in Pass 1 and a manual read for near-miss vocabulary -- e.g. "hurried",
"walked", "strode", "returned", "went", "came", "turned", none of which appear in V2_DESIRE/
V2_OUTCOME_UNMET/V2_OUTCOME_MET); (c) gender pairing is correct throughout (reusing the core bank's
already-verified owner/foil pairs, so no new gender-matching risk was introduced).

### Pass 5 -- honest-gap confirmation (not a defect, a designed probe)
All 8 action_implied items were confirmed (self-test 4/5) to NEVER type a GOAL event under the
current lexicon typer -- mirroring the same confirmed gap on the core bank (10/10 there). Their
outcome IS still typed (valid trigger), so the system's honest 0/8 score on them here is a real,
reportable finding, structurally identical to the core bank's 0/10.

## Items flagged as uncertain
None. All 20 new items passed all 5 passes with no residual uncertainty (0/20 problems on the
first draft, disk-verified). Reusing the core bank's own already-vetted S2/S4 sentences verbatim
removed the highest-risk part of authoring a new bank (novel lexicon-collision-prone content); the
only genuinely new text (the D-filler S1/S3 sentences) was deliberately kept simple and generic
(location + motion verbs only) to minimize collision risk, and the mechanical check confirms none
occurred.

## What Skunkworks should independently re-check
1. Re-run `experiments/exp_c5_fair_goal_owner_primacy_v1.py --self-test` fresh (all 5 checks must
   pass, including the 20/20 four-way-genuine-trap structural check) -- do not trust this report's
   numbers alone.
2. Spot-read a random subset of the 20 new items directly against the bank JSONL (`trap_type ==
   "primacy"` rows) for the "D-filler sentences are genuinely content-free / unrelated" property
   (Pass 4 above is the one most dependent on human judgment, least mechanically enforced).
3. Confirm the validity-gate arithmetic in `aggregate()`
   (experiments/exp_c5_fair_goal_owner_primacy_v1.py) matches the pre-reg's stated gates (all four
   baselines <0.5, cardinality==20, all_four_way_trap==True, scramble collapse >=50% relative) --
   these gates judge the INSTRUMENT, not the pipeline, and are the load-bearing claim.
4. Confirm the DISK-VERIFIED result: `data/exp_c5_fair_goal_owner_primacy_v1/metrics.json` ->
   verdict=INSTRUMENT_VALID_FULLY_FAIR_PRIMACY_TRAP, all four baselines=0.0,
   system_accuracy_primacy=0.6, system_scrambled_accuracy_primacy=0.0 (non-vacuous collapse),
   explicit=1.0, action_implied=0.0, deterministic across 3 seeds.
