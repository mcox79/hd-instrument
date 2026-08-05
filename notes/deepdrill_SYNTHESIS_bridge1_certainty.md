# Deep-drill SYNTHESIS — implementation-certainty ruling for BRIDGE-1 / C-AB

Date: 2026-08-05. Director synthesis of three LIVE-VERIFIED brain-foundation drills (USER: "do a deepdrill
on the brain foundation of this so we're certain we're implementing correctly"):
- notes/deepdrill_sense_disambiguation_cues.md (drill 1, commit 46f7d8497)
- notes/deepdrill_compositional_affect_grounding.md (drill 2, commit 047240f50)
- notes/deepdrill_situation_model_recurrence.md (drill 3, commit 31bb765df)
Reconciled against the BRIDGE-1 empirical HARD_PASS (commit 96e8e8404, differential grounding 0.967).

## Ruling in one line
BRIDGE-1's governor/frame SENSE-SELECTION is brain-faithful and correct AS A FIRST STAGE (verified), but
it is NECESSARY-NOT-SUFFICIENT: appraisal must condition on the ASSEMBLED EVENT (predicate+args+goal) plus
a TOP-DOWN SITUATION/DISCOURSE bias, not the governor token alone. The current 0.967 is real but on the
LOCAL-GOVERNOR-SUFFICIENT subset; on the TARGET subset (goal/affect/implicit/irony) a governor-only reader
is predicted to be systematically WRONG-DIRECTION, not merely weaker.

## What all three drills VERIFIED (converging, live-checked)
- SENSE-SELECTION via the governing predicate is a real, early, dedicated neural mechanism (LIFG
  unification/Hagoort; LATL minimal composition/Bemis-Pylkkanen; McRae thematic fit) -> BRIDGE-1's stage-1
  shape is RIGHT. [drill 1 + 2]
- Governor/frame is the correct PRIMARY LOCAL cue but one of FOUR ranked cues; it must actively OVERRIDE an
  always-on dominance/frequency default, and it CANNOT see cross-clause context. [drill 1]
- APPRAISAL/valence is computed over the assembled EVENT scored on GOAL-CONGRUENCE (Scherer/Lazarus/Barrett,
  verified), which a governor TOKEN structurally cannot carry; coercion is bidirectional. -> condition on
  the composed event (reuse Component-3), not the governor token. [drill 2]
- DISCOURSE/situation context is CO-EQUAL and often DOMINANT: the Nieuwland & Van Berkum "peanut-in-love"
  result (verified, PubMed 16839284) shows discourse INVERTS the local reading. For our target constructions
  (implicit dread, irony, goal-conditioned affect) the local clause is ~always neutral by design, so the
  discourse-decisive fraction approaches 100% THERE. [drill 3]
- Predictive-coding architecture: a local-only module computes a DIFFERENT quantity (raw signal vs residual
  after top-down explaining-away) -> you cannot bolt the loop on later without rebuilding the interface;
  design the top-down bias PORT now. [drill 3]

## The three corrections to BRIDGE-1 / C-AB (this is the certainty answer)
1. TWO-STAGE, EVENT-CONDITIONED (drill 2): governor -> selects the word's sense-FRAME (stage 1, local,
   governor-conditioned, KEEP the current mechanism) -> Component-3 ASSEMBLES the event (predicate + filled
   arg roles + goal-relation) -> appraisal is scored over the EVENT -> valuation. "BRIDGE-1's fix and
   Component-3 are ONE build." Do NOT collapse to governor->appraisal-dims.
2. TOP-DOWN SITUATION-BIAS PORT FROM DAY ONE (drill 3): build the interface to accept a top-down bias input
   (even stubbed/coarse), wired to the existing Component-5 organs (AccumulateRegister / GoalOutcomeRegister)
   and the situation model. Co-design, do NOT sequence "local now, discourse later" (it would be
   wrong-direction on the target subset AND require an interface rebuild).
3. DOMINANCE-DEFAULT + BIASED COMPETITION (drill 1): represent the always-on default sense that context must
   OVERRIDE, and combine cues by biased competition with a suppressed-but-not-erased loser residual (not hard
   serial gating). This also gives the graded/uncertainty signal C-D/C-E need.

## Reconciliation with the BRIDGE-1 empirical HARD_PASS
BRIDGE-1 v1 (0.967) is a VALID stage-1 sense-selection result on the local-governor-sufficient subset -- KEEP
it as stage 1. It is NOT "BRIDGE-1 complete." All three drills predict it FAILS on: (a) governor-matched /
event-differing pairs ("hit the deadline" non-harm vs "hit the wall" harm) [drill 2], and (b) discourse-
decisive / override pairs (peanut-in-love; goal-conditioned affect) [drill 3]. Those are exactly the target
cases -> confirm empirically before building more (below).

## Immediate can-fail CONFIRMATION test (measure, don't just theorize)
Run current BRIDGE-1 on: (i) governor-matched/event-differing minimal pairs (same governor, opposite
event-valence), (ii) discourse-decisive minimal pairs (local-neutral, prior-sentence sets the reading).
- EXPECTED (confirms the ruling): governor-only at/below majority baseline on both subsets (wrong-direction),
  while it still passes the local-sufficient subset.
- SURPRISE (would relax the ruling): governor-only already handles them -> governor implicitly encodes enough
  event/goal info; re-check item construction.
Scramble control: shuffle discourse/predicate pairing -> any situation-bias gain must collapse.

## Confidence
Drill Ps (deflated): sense-cue architecture 0.65; two-stage event-conditioning 0.62; situation-loop-from-day-
one 0.65. Convergent across independent literatures + one decisive reversal datum (peanut-in-love). Treat as
high-confidence DIRECTION; the confirmation test converts it to substrate-measured.

## Corrected build order (updates PLAN v3 -> v3.1)
BRIDGE-1 stage-1 (DONE, keep) -> CONFIRM test (does it fail on event-differing/discourse pairs?) ->
BRIDGE-1/C-AB v2 = two-stage governor->Component-3 event-assembly->event-conditioned appraisal + a stubbed
situation-bias PORT (wired to Component-5 organs) + dominance-default biased-competition -> C-C valence ->
C-D affect+PREDICTION (now the situation-bias port's real source) -> C-E-DETECT ACC -> BRIDGE-2 + C-E irony
-> wire OOV frames -> C-F goal-owner -> backbone-matched assembly.
Note: BRIDGE-1 + Component-3 + the Component-5 situation organs are now understood as ONE integrated build,
not separable phases (drills 2+3 converge on this).
