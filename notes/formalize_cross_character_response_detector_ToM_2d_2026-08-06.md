# FORMALIZE spec: cross-character RESPONSE detector (= ToM build / Plot-Units cross-character-links ADOPT / #5 op G)

**Filed:** 2026-08-06 by Director, full-auto push. Build-ready spec for the DOMINANT remaining lever on the
coverage tail. Written per the 2b lesson (do the hard/over-fire-risky build RIGHT: formalize + pre-VET +
strong guards FIRST, do not rush) and USER's "wall -> deep brain-fidelity audit." Sits in the UNIFIED
engine (2a-part-1, dc111492b), so a win here moves BOTH the polarity AND owner numbers.

## Why this is the lever (Director-probed, disk-verified)
Of the 15 remaining owner-never-typed items, the largest cluster is CROSS-CHARACTER RESPONSE: the
goal-holder's goal is directed at / depends on another agent, and THAT agent's response verb determines
met/unmet. Congruence currently abstains (NONE) on all of them because its channels (class-registry,
verb-recurrence, referent-recurrence, occurrence-gate) are all SAME-ENTITY; none reads a second agent's
response to the protagonist's goal.

## Deep brain-fidelity audit (SHAPE + POSITION + METRIC)
- BRAIN: mentalizing network (TPJ / mPFC / precuneus) represents a second agent's action as
  satisfying/blocking the protagonist's goal (multi-agent ToM). Plot-Units names this exactly: REQUEST
  (honored/denied), vicarious ENABLEMENT (+/M), vicarious MOTIVATION (-/M). METRIC: goal met/unmet read
  off the OTHER agent's response, not the protagonist's own act.
- OURS: SHAPE gap -- every congruence channel is same-entity (protagonist's own verb/referent). POSITION:
  belongs in congruence_decision as a new channel, entity-aware (goal-holder vs responder). METRIC: same
  MET/UNMET, but sourced from a cross-entity response. This is op G on the #5 roadmap + the KEEP-OURS/
  ADOPT verdict's single real ADOPT (notes/research_plot_units_comparison_adoption_2026-08-06.md).

## Mechanism (reuse-heavy, glass-box)
1. The goal is directed at / about another agent or that agent's action (goal-holder G, responder R, R != G).
   Reuse find_desired_state (goal + referent) + the goal-holder resolution (2a-part-1 subject / 2a-part-2
   speaker-attribution).
2. Detect R's RESPONSE verb in a later sentence, classed:
   - ACCEPT/GRANT class -> MET: accept, take (accept sense), agree, consent, admit, grant, allow, promise,
     yield, relent.
   - REFUSE/DENY class -> UNMET: refuse, decline, reject, deny, forbid, "won't"/"will not" + response verb.
   Occurrence-gated (reuse _verb_negated_before) so "did not refuse" flips correctly.
3. Bind the resulting MET/UNMET to the goal-holder G (cross-entity binding -- reuse GoalOutcomeRegister's
   per-entity register; this is the owner-attribution cross-entity pattern sized at 3b675d281).

## Pre-VET (Director, response-verb -> gold polarity mapping validated)
- lw_laurie_proposal_rejected: Jo REFUSES -> UNMET (gold unmet) OK
- lw_jo_editor_dashwood: "We'll TAKE it" (accept) -> MET (gold met) OK
- agg_anne_diana_bosom_friend: Diana AGREES -> MET (gold met) OK
- lw_jo_mr_laurence_confront: he ADMITS/concedes -> MET (gold met) OK
- ts_tom_whitewash_fence: Ben volunteers ("let me whitewash") -> MET but NOT a clean response verb
  (implicit acceptance) -> likely NOT caught by v1; report, defer.
Predicted clean recovery: 3-4 (laurie, dashwood, diana, jo_mr_laurence). Both numbers (polarity + owner
via 2a-part-1).

## THE CRITICAL RISK: OVER-FIRE (this is why it's formalized, not rushed)
accept/take/agree/admit are COMMON verbs (take esp. is a light verb). A naive class-match will over-fire
massively (every "take"/"agree" -> spurious MET). This is the 2b failure profile. MANDATORY guards:
- Fire ONLY when there is an OPEN goal directed at/about the responder (has_open_goal + goal-referent
  overlaps the responder or the responder is the goal's addressee). NOT a bare response-verb scan.
- Fire ONLY on the responder R != goal-holder G (genuine cross-entity), and R must be the response
  sentence's subject (respect the model's binding -- the 2b subject-binding lesson).
- Occurrence-gate every match.
- Strict-ADD: only when same-entity channels type nothing (byte-identical fallback).

## Can-fail gate
- HARD-PASS: >= +3 newly-correct (polarity AND, via 2a-part-1, owner) with CORRECT polarity+owner, ZERO
  regression across full-44 (both numbers) + the 48/48 + 12/12 fair instruments byte-identical + cert
  220/3. Witness in verification/ (tracing=False).
- HARD-FAIL: < +2, OR any over-fire on the NOISE light-verb bank (reuse the 8-verb bank), OR any
  regression, OR the response channel fires without an open directed goal (the over-fire guard failed),
  OR cert drops. On HARD-FAIL run the deep brain-fidelity audit.
- MIDDLE/PARTIAL: +2 with zero regression = bankable (competency-library norm).

## Reuse map (wire-don't-island)
find_desired_state + goal-holder resolution (2a-part-1/2); congruence_decision (new channel);
_verb_negated_before (occurrence-gate); GoalOutcomeRegister per-entity (cross-entity bind); the goal-
directedness / addressee logic from the evaluative/affect bridges (they already gate on addressee==entity).
Response-verb classes = SUPPLY (small lexical class, invariant-OK as data; flag for later lexical_similarity
de-supply like MONEY_CLASS).

## Non-goals / deferred
- ts_whitewash (implicit acceptance, no clean response verb) -> v2.
- Grounding-tail (liniment/spoil), threshold (chen), reported-outcome (carle) -> separate detectors.
- 2a-part-2 speaker-attribution (+1 woodman) -> cheap add-on, batch later.

## Bottom line
Highest-yield remaining lever (~+3-4, both numbers), = the ToM build + the one real Plot-Units adopt +
#5 op G. Mechanism clean; the make-or-break is the OVER-FIRE guards (open-directed-goal + responder-subject
+ occurrence-gate + strict-ADD). Dispatch next cycle with these guards mandatory; Director pre-VETs the
over-fire on the NOISE bank + VETs recovered items against this prediction.
