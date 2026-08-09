# Direction-B build plan — grounded world/idiom/script knowledge for outcome-evidence reading

**Author:** Director (main thread, opus), 2026-08-09. **Status:** DRAFT for USER review — drafting is
autonomous; EXECUTING the multi-month build needs USER go. **Trigger:** the all-night brain-fidelity arc
localized the comprehension wall precisely (see notes/director_brain_fidelity_SYNTHESIS_and_direction_verdict_2026-08-09.md
+ the backup TOP): the architecture is validated, and the ONE failing leg is OUTCOME-EVIDENCE WORLD/IDIOM/
SCRIPT GROUNDING — reading whether a short/idiomatic outcome ("put the kabash on that idea", "she told her
no", "Uh. No.") satisfies a goal-attribute requires knowledge WordNet-lexical grounding does not have.

## Why this is the right lever (not more architecture, not pipeline polish)

Everything cheap has been ruled out this arc: valence bag-of-words, token/lexical cues, WordNet-supersense
grounding, the goal-cued valence channel (Stage-1 HARD_FAIL), the grounded utility-satisfaction channel
(Stage-2 HARD_FAIL — but activation fired 0.273 + pairscramble collapsed clean + no regression, so the
ARCHITECTURE is validated; only outcome-evidence grounding failed, recovery 0/8 on the idiomatic hardest
cohort). The goal-owner pipeline (Component-3/5) is mature. The remaining reducible headroom (~0.69 -> the
~0.77-0.87 human ceiling) is gated on grounding. This is Direction B, USER-authorized in principle 07-14.

## What is already PROVEN (the foundation this builds on — do not rebuild)

- **Mechanism proven at toy scale:** script_bridge (all 5 gates) + learned_script_bridge (all 6 gates) —
  grounded concept/script knowledge as FHRR hypervectors bridges world-knowledge outcomes to goal-relevant
  end-states AND generalizes to unseen phrasings via feature overlap AND is LEARNED from exposure by the
  owned MDL learner (no hand-authoring), expandable to new domains with no forgetting.
- **Architecture validated:** the utility_channel (6 grounded attribute-predicates, FHRR bundle(bind),
  per-attribute unbind+cleanup_with_margin) — activation fires, goal-conditioning clean (pairscramble
  collapses), no regression. It just needs a grounded READOUT that can read real idioms.
- **Owned organs to reuse:** hdlab.learner (registry.learn + estimation/ruleind/proginduction + MDL),
  hdlab.lexical_similarity (concept_vector/CONCEPT_FEATURES), hdlab.binding/bundling/glass_box_loop
  (cleanup_with_margin), hdlab.goal_typing, hdlab.frame_induction (the learner-expand template),
  consequence_learning_loop (read->propose->consolidate).

## The gap = SCALING grounding coverage from toy to real, as a LEARNED capability

Toy = 3 scripts / 24 items, hand-authored features. Real = the open-ended idiom/colloquialism/world-
knowledge of naturalistic outcome prose. The USER's directive: not hand-built — EXPAND THE LEARNING
SYSTEM so it acquires grounded concept/idiom/script knowledge from concept dictionaries + reading, the
same way word-learning already works. "We need a seed, but the capability for B must be built by the
system itself as it is exposed to new concepts."

## Grounding SOURCES (SUPPLY DATA, full+vetted, 07-14 pivot — allowed; NOT LLM-at-inference)

- **ConceptNet** (idioms/colloquialisms + world relations; already on disk, data/datasets/conceptnet5_en_100k.jsonl).
- **Wiktionary / idiom dictionaries** (idiom -> literal-meaning gloss: "put the kabash on" -> stop/prevent).
- **ATOMIC** (if-then social/world knowledge, glass-box static graph — event -> effect/reaction).
- **FrameNet + VerbNet** (event frames + roles; nltk, owned).
- **SimpleWiki / WordNet glosses** (concept definitions for grounding features).
All grounded into HVs via the PROVEN concept_vector feature-bundle mechanism (data supply, not a new organ).

## Staged milestones — each an independent CAN-FAIL gate (stop/redirect if a stage fails)

- **M1 (cheapest decisive — do FIRST): idiom-grounding recovers the DesireDB abstain cohort?** SUPPLY +
  ground a modern idiom/colloquialism lexicon (ConceptNet + Wiktionary idioms) as HVs; feed the
  utility_channel the grounded idiom meaning. GATE: recover >=40% of the Stage-2 abstain-to-majority cohort
  (the 0/8 it failed) + pairscramble collapse. HARD-FAIL <15% -> even supplied idiom-grounding doesn't
  read these outcomes (deeper wall — reconsider whole approach). This tests Direction B's core hypothesis
  on REAL data cheaply before any scaling. [~days, reuses everything owned.]
- **M2: LEARN the idiom/concept -> attribute-effect mapping from exposure** (owned learner, per the
  learned_script_bridge template) instead of hand-authoring — held-out UNSEEN idioms generalize via
  grounded-feature overlap. GATE: held-out-idiom recovery matches M1's supplied number + scramble collapse
  + no catastrophic forgetting on prior idioms. [the "part of the learning system" requirement.]
- **M3: SCALE the concept/script/idiom inventory** from the external sources (full+vetted), with the
  coverage-vs-noise VET the arc already learned (WordNet-supersense was noise-inflated; VET every source
  for polarity-informativeness, not just coverage). GATE: coverage + accuracy on the FULL DesireDB residual
  AND cross-corpus (Chaturvedi, the strongest generalization test) — target the ~0.85 human ceiling, report
  vs it. [the multi-month leg.]
- **M4: WIRE into goal_typing.congruence_decision as the OOV fallback** + the utility_channel as the graded
  readout; full verification witness; register WIRED. GATE: full-bench no-regression + the auditable
  per-attribute trace (the product differentiator) intact.

## Honest cost + risks

- **Cost:** M1 ~days; M2 ~1-2 weeks; M3 the multi-month leg (the field's 45-yr problem — but the mechanism
  is proven, so this is scaling/coverage engineering + learning, not open research).
- **Risks (arc-learned):** (1) coverage-vs-noise (VET each source for polarity-informativeness);
  (2) circular grounding (never ground-by-X + grade-by-X); (3) the OUTCOME-EXTRACTION leg (getting the
  right outcome span to ground — separate from grounding itself, flagged repeatedly); (4) idiom coverage is
  long-tailed (M1 may recover the frequent idioms but not the rare ones — measure the head/tail split).
- **Kill criterion:** if M1 HARD-FAILs (supplied idiom-grounding recovers <15% of the abstain cohort),
  Direction B's grounding hypothesis is falsified on real data and we bank the validated architecture +
  auditability edge instead.

## Recommendation

Approve M1 (the cheapest decisive test of Direction B on real data — days, owned organs). Its result gates
the multi-month M3 commitment. This is "the brain can do it, so can we" made concrete + can-fail: the
brain reads "put the kabash on" via grounded semantic memory; M1 tests whether supplying that grounding
lets our validated architecture read it too, before committing to scale.
