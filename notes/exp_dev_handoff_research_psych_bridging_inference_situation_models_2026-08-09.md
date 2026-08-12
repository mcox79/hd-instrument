# exp_dev hand-off — research: psych bridging/causal/preclusion inference for the situation-model chaining step

**Filed-by:** research sub-agent, 2026-08-09.
**Trigger:** `notes/research_psych_bridging_inference_situation_models_2026-08-09.md` — director+USER-
requested drill answering which psych mechanism should compute the goal-relevant RESULT of a literal
outcome event with no surface cue ("wanted to knock out a guy" / "I walked away" => preclusion => goal
failed; "wanted to know why" / "I talked about it" => means-end => goal met). Finding: `hdlab/goal_outcome_relation.py`
(built earlier the same session, "Direction-B fork-A") already targets these two relations
(INSTANTIATES/means-end, CONTRADICTS/preclusion) but implements them via hand-authored lexical pools +
an exact WordNet-MWE dictionary lookup — not via the situation-model bundle
(`hdlab/situation_model_accumulate.py::AccumulateRegister`/`CausalLinkRegister`) or the concept-relation
organs (`hdlab/quality_relation.py` opposition, `hdlab/lexical_similarity.py::concept_similarity`) this
drill's brief named. The psych literature (Suh & Trabasso 1993 for the ACHIEVE leg; GraphPlan mutex /
causal-link-threat-detection for the CONTRADICT leg, honestly flagged as computational- not
psychological-precedent) licenses re-routing the SAME two relations through a graded situation-model +
concept-relation mechanism instead of hand pools, aimed specifically at the module's own disclosed
scaling gap (5 disclosed WordNet-MWE dictionary misses: bailed out / chickened out / shied away / washed
her hands of / turned the other cheek).

**Pause state:** check `data/orchestrator_paused.flag` before shipping; this hand-off is filed regardless
of pause state per research-role convention — it is not queue authorization by itself.

Per [[feedback-no-experiment-design-in-prompts]]: this file states WHAT to test and WHY (falsifiable
bands, context pointers) — exp_dev owns exact implementation (which similarity threshold, exact axis
construction for the CONTRADICT leg, exact cell structure, seeds).

## Anchor candidates (rank-ordered)

### 1. `exp_situation_model_relation_ablation_v1` (primary, do this first — cheapest, reuses an existing self-contained eval harness verbatim)

**Anchor pointer:** research note section "Cheap decisive test (can-fail, reuses the EXISTING harness, no
new data)" + section 5 "Mapping to the owned substrate."

**Substrate-product reading:** if this HARD-PASSes, it replaces `goal_outcome_relation.py`'s hand
pool-membership booleans (INSTANTIATES side) and exact WordNet-MWE dictionary lookup (CONTRADICTS side)
with graded situation-model+concept-relation queries — directly extends the trace `goal_achievement.py`
can show from "which lexical channel fired" to "which specific concept-relation (means-end / preclusion)
was inferred, and against what concept-space evidence," a strictly richer inspectable trace, no new
opaque component. It also directly targets the ONLY disclosed generalization gap in the current
mechanism (the 5 WordNet-MWE dictionary misses).

**Tier hint:** load-bearing if HARD-PASS — decides whether the goal_outcome_relation module's next
iteration should be situation-model-grounded or whether the current hand-pool/dictionary mechanism stays
the operating point (with kaikki.org Wiktextract flagged, per that module's own docstring, as the
alternative scale-up path if this test fails). A HARD-FAIL here does NOT refute the psych literature in
the research note (the automaticity/causal-network findings are independent of this one implementation);
it means the CURRENT concept-space grounding (quality_relation.py's 23-word hand axis lexicon,
lexical_similarity.py's coverage) is not yet rich enough to beat hand-pool lists on THIS item set.

**Why now:** cheapest possible test — reuses `hdlab.goal_outcome_relation.self_test()`'s EXISTING 14
TRAIN_EXAMPLES + 11 HELDOUT_EXAMPLES (disjoint tags already asserted), `memorization_baseline_predict`,
and the scramble-label control, changing ONLY the feature/relation computation. No new data, no new
external dependency, no gradient training — reuses `hdlab.situation_model_accumulate.AccumulateRegister`
(bind/bundle/unbind/cleanup_argmax), `hdlab.lexical_similarity.concept_similarity`, and
`hdlab.quality_relation`'s opposition-channel composition shape, all already owned and wired.

**Design (from the research note, exp_dev owns implementation details):**
1. Extend `AccumulateRegister`'s `role_vocab` with a `GOAL_ROLE` (same pattern `CausalLinkRegister`
   already used to add `CAUSE_ROLE`/`EFFECT_ROLE` to the base class) — bind the goal's extracted
   predicate concept-vector into it; bind each candidate outcome event's concept-vector into an
   `OUTCOME_ROLE` filler on the same entity's register (Kintsch C-I / Zwaan multi-event-indexing shape,
   already the module's own stated justification).
2. Build `ACHIEVE_query(goal_filler, outcome_filler)`: decode both via unbind+cleanup, score via
   `lexical_similarity.concept_similarity` — a graded generalization of `goal_atoms`/`outcome_atoms`'s
   current hand pool-membership booleans (INFO_EXCHANGE_POOL / ERRAND_POOL / SKILL_TRAIN_POOL /
   COGNITION_GOAL_POOL etc.).
3. Build `CONTRADICT_query(goal_filler, outcome_filler)`: reuse `quality_relation.py`'s opposition
   composition SHAPE (WordNet-antonym-style precision guard -> signed-FPE-axis graded threshold ->
   concept_similarity fallback), extended from adjective-quality axes to an event/state-incompatibility
   axis exp_dev constructs — this is the one piece with NO direct precedent in `quality_relation.py`
   today (its 23-word axis lexicon is density/sheen/energy/tone; exp_dev decides how to seed an
   incompatibility axis for events/states, e.g. engage<->disengage, approach<->withdraw — small,
   hand-seeded, same discipline as the existing axis lexicon, disclosed as a seed not a general solution
   per that module's own docstring convention).
4. Swap these two graded queries in for `pair_feats`'s boolean atoms in `goal_outcome_relation.py`'s
   `induce`/`predict`/`self_test` pipeline — keep TRAIN_EXAMPLES, HELDOUT_EXAMPLES,
   `memorization_baseline_predict`, and the scramble control (label-shuffle on TRAIN, re-eval on
   HELDOUT) structurally unchanged, so the comparison is a clean ablation (same items, same controls,
   only the relation-computation swapped).
5. Report: (a) held-out accuracy of the grounded-relation route vs. the CURRENT hand-pool/dictionary
   route's `held_acc` (both on the same 11-item heldout set), (b) scramble-control accuracy for the
   grounded route (must collapse the same way the current route's does), (c) recovery count (0-5) on
   the 5 disclosed WordNet-MWE dictionary-gap sentences (`bailed out` / `chickened out` / `shied away` /
   `washed her hands of` / `turned the other cheek` — from `REPRESENTATIVE_DISENGAGEMENT_PHRASES`'s own
   disclosed misses) via the graded CONTRADICT query specifically.

**Pre-registered bands (from the research note, verbatim):**
- **HARD-PASS**: held-out accuracy on the existing 11-item heldout set >= current `held_acc` **AND**
  scramble control collapses to at/below the existing scramble baseline **AND** recovers >= 1/5 of the
  disclosed WordNet-MWE dictionary gaps via graded relation.
- **MIDDLE_BAND**: matches current `held_acc` within noise, scramble control collapses, but recovers 0/5
  dictionary gaps — real signal, not yet demonstrating the scaling advantage; iterate the concept-
  grounding quality (richer axis lexicon / richer concept space) before committing further.
- **HARD-FAIL**: held-out accuracy drops below `memorization_baseline_predict`'s accuracy, OR drops below
  current `held_acc` by more than trivial noise, OR the scramble control does NOT collapse (relation is
  reading general outcome-similarity/valence, ignoring which specific goal is paired — the same
  wrong-goal-leakage failure class this arc has caught 4+ times already), OR 0/5 dictionary-gap recovery
  combined with any accuracy regression.

## Context pointers (files, not summaries)

- `notes/research_psych_bridging_inference_situation_models_2026-08-09.md` — full synthesis, all 4
  lit-scan lane summaries, per-mechanism ESTABLISHED/CONTESTED/SPECULATIVE tags, section 5's mapping
  table, and the honest asymmetry flag (ACHIEVE leg strongly psych-grounded; CONTRADICT leg only
  computationally-precedented, calibrated lower).
- `hdlab/goal_outcome_relation.py` — the module to extend; `goal_atoms`/`outcome_atoms`/`pair_feats`
  (hand-pool booleans to replace on the ACHIEVE side), `mwe_disengage_scan` (dictionary lookup to
  replace/supplement on the CONTRADICT side), `self_test()` (the exact harness to reuse — TRAIN_EXAMPLES,
  HELDOUT_EXAMPLES, `memorization_baseline_predict`, scramble control all defined there already).
- `hdlab/situation_model_accumulate.py` — `AccumulateRegister` (base bind/bundle/unbind/cleanup_argmax
  register, role_vocab extension point), `CausalLinkRegister` (the exact precedent pattern for adding a
  new typed role to the register — mirror this for `GOAL_ROLE`/`OUTCOME_ROLE`).
- `hdlab/lexical_similarity.py` — `concept_similarity` (McRae-style shared-feature bundle cosine, the
  ACHIEVE-leg relevance signal), `in_lexicon`, `SIMILARITY_LINK_THRESHOLD`.
- `hdlab/quality_relation.py` — the opposition-channel composition to generalize for the CONTRADICT leg
  (Channel A WordNet-antonym precision guard, Channel B signed-FPE-axis, Channel C concept_similarity
  fallback); read its module docstring's PRE-REGISTERED CONSTANTS section (RATE_CENTER, OPP_THRESH,
  SAME_THRESH) before constructing a new axis — same calibration discipline applies.
- `hdlab/goal_achievement.py` — `utility_channel_trace_relation_grounded` / `_attribute_outcome_state_relation_grounded`
  (the existing caller that already consumes `goal_outcome_relation.relation_votes`; if this test
  HARD-PASSes, this is the wiring point for the grounded replacement, not a new caller).
- `notes/research_glassbox_utility_inverse_planning_leg_2026-08-09.md` — the sibling drill that supplied
  the WHAT-to-score attribute-predicate representation this drill's HOW-to-compute-the-relation mechanism
  complements.
- `notes/research_brain_fidelity_goal_outcome_architecture_2026-08-09.md` — independent corroboration of
  the top-down/active-goal framing this drill's automaticity finding (section 1) reinforces.

## Contract section

- exp_dev owns: exact axis-construction method for the CONTRADICT-leg incompatibility axis (which seed
  words, how many, which threshold), exact `GOAL_ROLE`/`OUTCOME_ROLE` vector-generation details, exact
  cell/file naming, exact seed handling.
- Research (this hand-off + parent note) fixes: the falsifiable HARD-PASS/MIDDLE_BAND/HARD-FAIL bands,
  the mandatory scramble-control reuse (not optional — it's what makes this a real test of goal-
  conditioning rather than a vacuous "any similarity score helps" result), the mandatory dictionary-gap
  recovery count as the specific test of generalization-past-the-disclosed-ceiling, and the glass-box/
  no-LLM-at-inference invariant — every organ named above is already owned; nothing in this test may
  introduce a trained/opaque external component.
- Honest asymmetry (carry into the pre-reg): the ACHIEVE-leg mapping is well-grounded psychologically: the
  CONTRADICT-leg mapping is only computationally-precedented (GraphPlan mutex / causal-link threat
  detection), not psychologically validated — if the two legs diverge in outcome (e.g. ACHIEVE HARD-PASSes
  but CONTRADICT does not), report them separately rather than folding into one combined verdict.

## Autonomy declaration

exp_dev decides the exact axis-construction method for the CONTRADICT-leg incompatibility axis, exact
cell/file naming, exact seed count, and whether to combine the `GOAL_ROLE`/`OUTCOME_ROLE` register
extension with the relation-query cell or split them. The falsifiable bands, the mandatory scramble
control, and the mandatory dictionary-gap recovery count are NOT exp_dev's to loosen or drop without
flagging the change explicitly in the pre-reg.
