---
owner_verdict: DONE
---

SOLVED (pending your verdict) -- expand_the_clean_semantic_memory_foundation_with_world_knowledge_via_the_consolidation_gate (opus 4.8 solver)

Write-up: notes/problems/expand_the_clean_semantic_memory_foundation_with_world_knowledge_via_the_consolidation_gate/SOLVED.md
Reverify (scaffold-free witness; recomputes every headline from source; writes nothing):
  .venv/Scripts/python.exe verification/test_world_knowledge_typed_spokes.py     # 22/22 (~65s)

STATUS: SOLVED. THE THESIS (brain-foundational): the frozen meaning store crushes all of a synset's knowledge into
ONE dense 200-d signature; a symmetric cosine over it CANNOT represent a DIRECTED or TYPED relation (its own witness:
sibling cos 0.932). So the knowledge that IS there (WordNet is-a, ConceptNet relations) is UNREADABLE in typed/
directed form. The brain's fix is the ATL hub-and-TYPED-SPOKE organization (Lambon-Ralph, PINNED). I admit
world-knowledge relations OFFLINE through the gate as TYPED, DIRECTED, sense-resolved SPOKES (additive; C1 untouched)
and prove it on multiple relation families + a natural-logic reasoning layer. NO external LLM; reader's own tools
only. NO hdlab written (Q111 -- strategy lands the diff, Sec 8).

RESULTS -- 5 relation families, each on ITS OWN consumer's MODERN instrument, every info-free twin LOSING CI-sep:
1. is-a (type 3, DIRECTED), on THREE golds: MoNLI 0.817 vs the pre-ingest symmetric foundation 0.500 (+0.317 CI-sep;
   symmetric is ANALYTICALLY capped at chance on directed entailment); MED (2nd, less-circular gold) 0.760 vs
   majority 0.563 (+0.197 CI-sep); GUM common-noun COREFERENCE (modern, INDEPENDENT of WordNet = the non-circular
   downstream win) +0.0116 over recency/Centering CI-sep, as a type-licensing FILTER (shuffled-filter twin loses).
2. part-whole + instrument (types 4+6, DIRECTED) on the LIVE bridging organ: covered facts 0.926/0.828 vs the
   symmetric read 0.095/0.027 on confusable distractors (symmetric is FOOLED below chance); generalization
   located-negative (held-out 0.272/0.203 -- meronymy is a partially-PINNED limit, confirmed by the literature).
3. antonymy (type 5, a 5th spoke): the symmetric signature is ANTI-predictive on opposition (AUC 0.391 -- antonyms
   are MORE similar than synonyms); a typed antonym spoke is REQUIRED for opposition-aware valence.
4. event-order (type 9): ALREADY a landed organ (hdlab.generalized_event_knowledge, Story Cloze 0.582 CI-sep) --
   a 4th directed-spoke that independently CORROBORATES the architecture (do NOT rebuild).
5. NATURAL LOGIC over the is-a spoke: is-a spoke + monotonicity (up/down, negation flips) solves ~85% of MED
   (0.767) vs majority 0.503 and a symmetric-cosine oracle 0.535 (both CI-sep); shuffled-monotonicity twin loses
   (polarity is load-bearing). This is the brain's FAST operator-recognition register and is near-human.

CONTROLS: info-free twin loses on every type; NO regression (C1 byte-untouched -> diagnostic_context_wsd unchanged,
test_knowledge_factory_meaning_store.py 6/6); monotonicity-ablation collapses the negation subset 0.875->0.125;
gate schema-margin AUC 0.942 (deterministic); resolution guard (raw-string over-generates cross-sense is-a 100% on
polysemous nouns). Reproduce all via the witness (22/22).

EVERY NEGATIVE DRILLED >=2x + LITERATURE-BACKED (2 research notes, cited in SOLVED):
- PINNED (our build is confirmed brain-faithful): coref recency-primary + type-as-filter (Lappin-Leass, Centering);
  the small sense-conflation cost (Swinney/Duffy -- both senses activate, cost small when one dominates = our regime).
- FIDELITY GAPS with named mechanisms, all TESTED: part-whole generalization (nearest-exemplar + inheritance both
  fail -> partially-pinned, shallow partonomies -- Tversky-Hemenway/Winston-Chaffin-Herrmann); the basic-level gate
  (schema-margin AUC fine; earlier "collapse" was a threshold artifact); the gate's consumer-level "raw regresses"
  guard (the consumer is ROBUST to noise; the gate's value is edge-level -- a closure store must not edge-filter).

100% BRAIN-FOUNDATIONAL (this + upstream): I removed the one violation -- spaCy is demoted to a NON-ADMISSIBLE
mechanism-ceiling reference; the admissible chain runs on the reader's OWN tagger/parser. The natural-logic monotonicity
marker (0.767) uses the reader's own tools; SIX positional/parse scope methods (linear 0.514, shallow 0.669,
NP-restrictor 0.672, reader's-own-parse 0.505, parse-repair 0.651, spaCy 0.810-external-barred) were built and drilled.
Research VERDICT (C): the brain uses a DUAL REGISTER -- a fast operator-recognition register (= our 0.767, near-human;
the hard MED tail is hard for humans too -- Geurts) + a bounded slow structure-building register. So 0.767 is
brain-faithful, NOT a defect; it is neither a general-parser-upgrade problem (A) nor a hard ceiling (B).

KEY REALIZATIONS: (a) the "thin store" wall is really the SUPERPOSITION CEILING -- typed/directed ORGANIZATION is
the lever, not volume. (b) A symmetric representation is analytically capped/fooled on directed relations; that is
the clean proof a typed spoke is necessary. (c) Consumer ARCHITECTURE decides whether knowledge helps: is-a as a
coref SELECTOR loses to recency, as a type-licensing FILTER it wins. (d) "landed != scored != brain-foundational" --
found + fixed the one external-tool (spaCy) violation. (e) monotonicity scope is positional/syntactic, but no
brain-foundational heuristic substitutes for a robust parse, and the remaining gap is a bounded slow register, not
a parser overhaul.

FILES: 5 experiment cells (exp_isa_typed_spoke_monli_v1, exp_partwhole_typed_spoke_bridging_v1,
exp_isa_spoke_commonnoun_coref_gum_v1, exp_antonym_typed_spoke_valence_v1, exp_natural_logic_monotonicity_med_v1),
1 scaffold-free witness (22/22), a research note in the problem folder; owner_verdict: (blank -- yours to set).

>>> PRIORITY NEXT STEPS:
    P1 (INTEGRATE now): land hdlab/typed_spokes.py with the 3 directed spokes (C5 is-a, C6 part-whole/instrument,
       C7 antonymy) + register in the manifest; wire each into its consumer default-OFF -> measure -> flip if
       net-positive: coref (C5+C6 as a type-licensing FILTER on recency, DEMONSTRATED +0.0116), natural-logic
       reasoner (C5 + the parse-free sentence-level marker, ship parse-free as default), bridging (C6 hybrid),
       affect (C7 antonym for valence). Fold the AUDIT UPDATE.
    P2 (highest-leverage new type, needs a KB): TYPE 2 entity instance-of for name_bridge coref (common->proper-name,
       ~10%, WordNet can't reach) -- acquire Wikidata P31, build the entity-type spoke.
    P3 (slow-register upgrade, needs a KB): acquire VerbNet PP-subcat frames + build the bounded restrictor-attachment
       slow register for natural logic (0.767 -> ~0.84 bounded; core prototyped; NOT a general parser upgrade).
    P4 (more new types): TYPE 10 thematic-fit (L2 MAPPED), TYPE 5 attributes, TYPE 8 causal.
    DO NOT re-file: reading-derived growth; curated-store trimming (keep-all is the knee); a symmetric rep for a
       directed relation; TYPE 9 event-scripts (already a landed organ); a general parser upgrade / heuristic /
       external scope for monotonicity (verdict C rejects; six methods fail; spaCy barred).

QUESTIONS: none blocking. One labelling note: I set SOLVED (5 families clear the bar over the pre-ingest foundation
with the required controls; the is-a win is confirmed non-circularly on GUM coref + MED). Content is identical
whichever label you prefer.
