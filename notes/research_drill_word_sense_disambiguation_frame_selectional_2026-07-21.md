---
name: research_drill_word_sense_disambiguation_frame_selectional_2026-07-21
description: "Brain-drill + design for the word-sense-disambiguation gate (the confirmed next meaning-module gap): frame-matching the parse to VerbNet's frame-specific senses + selectional restrictions"
metadata:
  node_type: memory
  type: reference
  originSessionId: 02e8b04e-1164-42ee-b96d-ac16726a826a
---

**Context:** the held-out full-gate eval (2026-07-21, a55db898) confirmed WORD-SENSE-DISAMBIGUATION as the meaning module's next gap: the verb-affectedness gate is lemma-level and picks the MODAL sense, so it fails on polysemy (leave=depart-vs-DEPOSIT, meet=contact-vs-encounter) -- but the CORRECT sense is present in VerbNet's per_sense data (3/3 held-out failures rescuable_by_per_sense). Directive-#4: drill the brain mechanism before building the disambiguator.

**BRAIN MECHANISM (word-sense disambiguation in context):** the brain settles on a sense by MUTUAL CONSTRAINT between a word and its syntactically-related neighbors -- "each restricts the meaning of the other through selectional preferences." Two signals: (1) SYNTACTIC FRAME / argument structure (a constraining sentence frame pre-activates the likely sense -> the reduced-N400 prediction effect; formal structure constrains especially closed-class + argument-taking words); (2) SELECTIONAL RESTRICTIONS on the argument fillers (the verb prefers certain semantic types in each slot). Initially multiple senses are active; context rapidly SETTLES to the coherent one (same settling/coherence dynamic as comprehension). Sources: Paczynski-Kuperberg (JML 2012); N400 prediction/pre-activation (Scholarpedia N400; PMC5108799); selectional-preference sense-restriction (arXiv cs/0501095).

**DESIGN (glass-box, in-wheelhouse -- build from parts we HAVE):**
- The reader's PARSE already gives the argument structure (direct object? location-PP? PP-goal?). VerbNet senses are FRAME-DEFINED. -> DISAMBIGUATOR = match the sentence's parse-frame to the VerbNet sense whose frame matches, pick THAT sense, read its affectedness. ("leave NP PP.location" -> deposit sense = affected; "leave NP" bare / motion -> depart = none.)
- REFINE with SELECTIONAL RESTRICTIONS on the argument fillers (VerbNet has per-role selrestrs: +location, +animate, +concrete). The filler's semantic type further constrains the sense. -> this NATURALLY pulls in ENTITY/NOUN SEMANTICS (the predicted gap AFTER word-sense) -- the meaning module builds up coherently: verb-affectedness -> word-sense (frame) -> entity-semantics (selectional fillers).
- Brain-faithful: frame + selectional MUTUAL constraint, settling to the coherent sense (same coherence dynamic as the reader).
- CAN-FAIL / bounds: some senses aren't frame-distinguishable (need selectional/world-knowledge); VerbNet frame granularity may be coarse; the reader's parse errors propagate. Measure on the held-out word-sense cases (leave-deposit, met, + more) -- does frame-matching pick the right sense?

Related: [[project_meaning_module_grounding_read_drives_knowledge_loop_2026-07-21]] (the read-drives-knowledge loop; word-sense = the surfaced next gap); atom 29414 (the lemma-level gate that this disambiguates); the VerbNet lexicon (data/verbnet_affectedness_lexicon_v1, has per_sense + frames). Brain-drill sibling: [[research_drill_metacognitive_calibration_escalation_trigger_2026-07-21]].
