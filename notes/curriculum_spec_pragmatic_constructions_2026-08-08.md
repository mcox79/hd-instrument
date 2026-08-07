# BUILD-READY SPEC: the pragmatic/discourse CONSTRUCTION curriculum (B-steer, USER-chosen)

**Filed:** 2026-08-08 by Director, synthesizing two report-only drills (D1 taxonomy a7071cbc + D2
mechanism a8efa0e7), both Director-VET'd (disk-grounded, live-typer-run, honest caveats). This
DEFINES THE NEED the USER asked for and is the build-ready plan for target (B): learn the
pragmatic/discourse constructions that convey goal MET/UNMET, taught graded-supervised.

## 0. THE MEASURABLE TARGET (D1 ran the live production typers, not memory)
- POLARITY organ (congruence_with_lexicon_fallback) on goal_bearing_modern_eval_v1 (44): **26/44
  abstain-or-wrong (59%)** = the direct "goal met/thwarted NOT via a valenced verb" gap. This is
  the number the curriculum must move.
- OWNER organ never-typed: 13/44 (subset, downstream of the same gap).
- 85 hand-curated items exist across 5 banks (goal_bearing 44 + real_text 10 + affect_state 12 +
  evaluative 13 + oov_psych 6). Auto-mined banks (~78) are NOT usable as-is (outcome-span = fixed
  sentence-window, not a verified resolution -> noise would masquerade as new types).

## 1. THE TAXONOMY (11 in-scope types + 1 out-of-scope; D1, verbatim examples in the drill)
A dialogue request/response (literal grant/refuse) | B idiomatic assent/dissent | C affect/evaluative
bridging (+ bystander-abstain) | D reciprocal/benefactive causal bridging | E concession/admission
speech-act | F result-state adjective/noun valence (+ false lexical cue) | G perspectival/goal-relative
valence (one event, owner-indexed sign) | H ToM/reverse-psychology (hidden goal, substitute agent) |
I negation-scope over the polarity verb | J polarity garden-path (false-cue-then-pivot) | K
numeric/graded-threshold (PARALLEL TRACK, magnitude cognition, register-locked to news/expository) ||
**L world-knowledge/object-dependent polarity = OUT OF SCOPE (unbounded long-tail, confirms the
B-steer on the larger 26-item gap -- independent re-confirmation, not repetition).**

## 2. THE GRADED LADDER (ordering = BINDING SCOPE / ToM-load; = child acquisition order, D1+D2 agree)
- **Tier 0 (control):** literal lexical-verb valence (already-solved ~18/44 + in-lexicon sanity). Regression only.
- **Tier 1:** I (negation-scope) + F (result-adjective) -- WITHIN-SENTENCE composition. Simplest.
- **Tier 2:** A (literal request/grant-refuse) + E (concession) -- first CROSS-TURN binding, explicit marker.
- **Tier 3:** B (idiomatic assent/dissent) -- same skeleton, conventionalized response (implicature).
- **Tier 4:** C (affect/evaluative bridging + bystander abstain) -- mentalizing-from-testimony + coref-to-right-referent.
- **Tier 5:** D (reciprocal/benefactive causal bridging) -- social SCRIPT over lexically-disjoint events.
- **Tier 6:** G (perspectival) -- hold >=2 agents' goals over the SAME event, owner-indexed sign.
- **Tier 7:** H (ToM/reverse-psychology) -- SECOND-ORDER mentalizing + substitute agent.
- **Tier 8 (hardest):** J (garden-path) -- SUPPRESS a salient recent false cue, re-resolve on a pivot.
- **Parallel:** K (numeric-threshold) -- separate magnitude competency, build/test independently.
Developmental grounding (D2): direct-request mastered earliest (~age 3-4), indirect ~age 6 tracking
false-belief timeline; ToM-load (not syntax) is the rate-limiter -> this ordering is brain-faithful.

## 3. THE LEARNING MECHANISM (D2, disk-grounded reuse -- the engine EXISTS)
- **Acquisition engine = hdlab/learner (MDL mdl_select).** Not a convenience borrow: usage-based
  construction acquisition (Tomasello/Goldberg type-frequency -> generalization) IS a compression
  argument, so MDL is the mechanism the acquisition literature converges on. A construction is
  "learned" (promoted from episodic memorization to productive rule) exactly when generalizing
  compresses the data better than memorizing exemplars.
- **Hypothesis class = gam plugin PRIMARY (graded log-odds features), ruleind SECONDARY** (crisp
  conjunctions); declare both as candidate_plugins, mdl_select auto-picks by compression. Rationale:
  pragmatic cues are GRADED (degrees of hedging/indirection), so ruleind's purity gate would discard
  60%-informative cues; gam keeps them.
- **Teaching signal (SUPPLIED = DATA, invariant-OK; EARNED = the recognition capacity):** graded
  supervised passages labeled with the NATURAL CONSEQUENCE (GOAL / OUTCOME_MET / OUTCOME_UNMET / NA
  -- the exact output shape the owned goal_typing/goal_owner organs already emit) + per-type STRUCTURAL
  TAGS (D1 per-type spec: negation_scope span; desired-vs-actual state; response_marker; idiom_gloss;
  referent + note_bystander; bridge_relation {reciprocity/rescue_by_helper/reward_for_effort/
  enabling_sacrifice}; per-owner label; hidden_goal; pivot_marker). KEY (D1): for hard types (D/H)
  supply the relation/hidden-goal tag AT TRAINING, so the learner learns the TEXTUAL CUES that predict
  it -- cue-recognition generalizes at test, NOT the label.
- **Can-fail gate:** (a) learn-time compression_ratio >= 1.0 (else stays honestly episodic, not
  overfit); (b) deploy-time self_improving_loop coherence-margin (gold-free) -- BUT re-validate on
  dialogue-turn-scale (sparse) content first (its docs flag it ties/over-adopts on sparse passages).

## 4. REUSE MAP per tier (merging D1 wired-status + D2 reuse-map; wire-don't-island)
- Tier 2 A: **REUSE+EXPAND** goal_typing.congruence_request_response (landed 2747fac9a today) -> feed
  graded examples through hdlab.learner to induce past the closed pattern list.
- Tier 4 C (affect-word): **REUSE** goal_owner_select.detect_affect_state_construction (wired, proven
  bystander guard) + verify_affect_state_bridging_production.py regression. Evaluative-quote sibling
  = an UNWIRED experiment cell to promote.
- Dialogue turns (Tiers 2-4): **REUSE** coreference_resolver (already tracks speaker/addressee/quote spans).
- Affect grounding: **REUSE** context_grounded_valence (certified).
- Situation-model/coherence: **REUSE** situation_model_accumulate/situation_reader (caveat: event
  recall ~0.32 tagger-limited -> a bottleneck for EVENT-dependent tiers; dialogue tiers sidestep it via coref).
- Tier 6 G (perspectival): **REUSE** goal_owner_select owner-indexed scoring (mostly there).
- Tier 5 D (benefactive/substitution): **GENUINELY-NEW small primitive** -- a benefactive tier between
  referent-match(MET) and referent-mismatch(UNMET), gated on theme-overlap (reuse entity_goal_themes)
  + benefactive syntax; shaped like _request_grant_verb_match.
- Concession (Tier 2 E): **EXPAND** goal_typing._cb_discourse_pole_cue (Kehler/Hobbs CONTRAST) from
  single-clause flip -> multi-turn refuse->grant state machine.
- Tier 7 H recursive ToM: **NO organ = the deep gap.** Defer to last (brain-faithful: age 6+). Honest.
- Anti-drift adoption: **REUSE** self_improving_loop (re-validate on sparse content).

## 5. THE FIRST BUILD = the CHEAP DECISIVE TEST (D2's proposal -- validate the PREMISE before scaling)
Author ~20-30 hand-labeled graded passages spanning Tier 1 (I/F) + Tier 2 (A/E) (D1: these are
gettable to N=20-30 with a single-corpus grep-and-verify pass; the literal markers are common). Run
them through hdlab.learner.registry.learn(candidate_plugins=["estimation","ruleind","gam"]) treating
the EXISTING hand pattern-list (congruence_request_response cues) as ONE feature among several.
- **HARD-PASS:** mdl_select picks a NON-episodic hypothesis (compression_ratio > 1.0) recovering
  >=80% of held-out MET/UNMET = the learner genuinely GENERALIZES past the closed pattern list => the
  graded-supervised-curriculum premise is real; scale to higher tiers.
- **HARD-FAIL:** stays KEEP_EPISODIC (compression_ratio <= 1.0) OR held-out == hand-list-only baseline
  => needs more data density / a different feature encoder, NOT "architecture wrong" (flat-result
  discipline: diagnose broken-experiment vs ceiling; run the anti-premature-HARD_FAIL triage).

## 6. ANTI-PREMATURE-HARD_FAIL PROTOCOL (carry forward, USER caution -- 2 over-reads caught this session)
Before any gate is a FAIL: foundation present? teaching-signal actually reached the learner
(features non-degenerate)? genuinely-new + non-degenerate held-out? fair (graded-supervised, not
vacuum) regime? Coverage-vs-accuracy always separated. VET positives AS HARD AS negatives.

## 7. HONEST REALITY (D1)
- Data-thin tiers: H/J/K are N=2 each -> need a DEDICATED mining pass (trickster/reversal narrative
  for H/J; news/expository for K) before they're real curriculum stages. Tier 4 C is the most
  scalable (25 items already + a generative substitution template).
- Overlaps: E/G share an item; A/B are one family (one detector, difficulty-split); F/I are both
  within-sentence (could be one easiest tier).
- Already-partially-wired != solved: A + C's affect-word flavor exist but fail on harder members.
- L (world-knowledge) stays out of scope (unbounded), re-confirmed on the 26-item gap.

## 8. BOTTOM LINE
The need is defined end-to-end: an 11-type taxonomy, an 8-tier binding-scope-graded ladder matching
child acquisition, a learning mechanism that is MOSTLY REUSE of owned organs (hdlab/learner MDL as the
proven acquisition engine; only benefactive-substitution is a new small primitive; recursive-ToM is
the deferred deep gap), a per-type supervised teaching-signal spec concrete enough to author, and a
cheap decisive FIRST test that validates the whole graded-supervised premise on Tiers 1-2 before any
scaling. Build order: FIRST TEST (Tiers 1-2 generalization-past-closed-list) -> if PASS, scale up the
ladder tier by tier, authoring data + reusing/expanding the mapped organs, recursive-ToM last.
