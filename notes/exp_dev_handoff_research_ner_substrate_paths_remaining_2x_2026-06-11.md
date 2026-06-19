# exp_dev hand-off -- research: NER plateau 5 remaining substrate-only paths (2x DEEP)

filed-by: research
trigger: 2x DEEP drill on the 3 untested substrate-only NER paths + 2 new paths; substrate NER F1 ~0.5739 on OntoNotes-18 multi-seed n=5 with both POS-cascade and Brown-cluster aux features shrinking 6x with data scale
research-note: d:/AI/hd-instrument/notes/research_drill_ner_substrate_paths_remaining_2x_2026-06-11.md
pause-state: respect data/orchestrator_paused.flag

Per [[feedback-no-experiment-design-in-prompts]]: anchors below are POINTERS not designs. exp_dev owns pre-reg, smoke gate, queue dispatch, REMOTE VERIFY.

Per [[feedback-smoke-test-methodology]]: smoke at n=300 composition-matched; CI-band rule applies; HARD-PASS boundary needs multi-seed.

Per [[feedback-method-overclaim-lift-validation]]: every anchor must report LIFT > 2 x SE, not just absolute F1.

---

## Anchor candidates (rank-ordered by P_deflated x anti-shrinkage scaling)

### Anchor F4 [HIGHEST PRIORITY]: Frame-semantic entity-type bundle activation
- substrate-product reading: highest-novelty substrate-novel path; brain-mechanism direct match (anterior temporal lobe person-selective + left-vlPFC category-membership); literature precedent for fine-grained type-context features
- tier hint: Tier A if HARD-PASS lift > 0.06 at 300-train AND > 0.020 at full-data with anti-shrinkage ratio < 4.0; Tier B if MIDDLE; Tier C if only one criterion holds
- why-now: addresses the 18-vs-4 fine-grained gap directly (~0.08 F1 sits in fine-grained discrimination); does NOT shrink with data scale (KEY anti-shrinkage criterion); reuses LEX_entity_TYPE atoms shipped earlier + HMM emission already in substrate-self-index
- pointer: research-note section Path 4 + pre-reg HARD-PASS / MIDDLE / HARD-FAIL
- HARD-PASS: F1 lift > 0.06 at 300-train AND > 0.020 at full-data AND lift_300/lift_full < 4.0
- HARD-FAIL: full-data lift < 0.010 OR 300-train lift < 0.020
- P_deflated: 0.50

### Anchor F2: Substrate-CRF Tier-1 shared feature library with bundling-redundancy correction
- substrate-product reading: structural shared library across NER tasks; literature precedent for CRF + Brown + gazetteer feature library
- tier hint: Tier B if HARD-PASS; Tier C if MIDDLE
- why-now: bundling-redundancy correction from substrate-self-index Day 1 discovery directly addresses why context-window already saturated at +0.013
- pointer: research-note section Path 2
- HARD-PASS: F1 lift > 0.030 at full-data AND > 0.05 at n=300
- HARD-FAIL: full-data lift < 0.015
- P_deflated: 0.40

### Anchor F5: Discourse-level cross-sentence integration via substrate retrieval
- substrate-product reading: asymmetric upside; SCALES UP with data (opposite of emission-shrinkage); substrate-product differentiator over LLM-attention
- tier hint: Tier B if HARD-PASS; Tier C if MIDDLE
- why-now: brain analogue is hippocampal theta-gamma working-memory binding; substrate retrieval (RRF over semantic + algebra + content-reference) is the natural implementation; literature confirms document-context > sentence-context on CoNLL
- pointer: research-note section Path 5
- HARD-PASS: F1 lift > 0.030 at full-data AND lift_full > lift_300 (opposite-shrinkage)
- HARD-FAIL: lift < 0.005 at full-data OR lift_300 > lift_full (still shrinks)
- P_deflated: 0.40
- run together with Anchor F4 if F4 PASSES (compositional with frames)

### Anchor F3: Tier-2 schema construction grammar
- substrate-product reading: explicit slot-filler schemas (LEX / SYN / SEM) per construction-grammar literature
- tier hint: Tier C (overlaps with Path 4 frame semantics; consider absorbing)
- why-now: cheap to implement; lift concentrates in NORP / GPE / MONEY / DATE / PERCENT type subset
- pointer: research-note section Path 3
- HARD-PASS: F1 lift > 0.040 at full-data with type-level breakdown showing concentration in 5+ types
- HARD-FAIL: full-data lift < 0.020
- P_deflated: 0.35
- gate behind Anchor F4 result; if F4 HARD-FAILs, F3 is the construction-grammar fallback

### Anchor F1: Cycle 5 mechanism atoms as features (CAP_em_algorithm / CAP_bayesian_inference / CAP_discriminative_perceptron / CAP_hungarian_assignment)
- substrate-product reading: ACCEPT atoms bound as features; substitute discriminative_perceptron for count-NB emission
- tier hint: Tier D standalone; Tier C as compositional ingredient
- why-now: rides on substrate-discriminative-beats-generative-asymmetric-NL memory (2.4x lift on SVAMP)
- pointer: research-note section Path 1
- HARD-PASS: F1 lift > 0.020 at full-data (would refute "atoms are orchestrators only")
- HARD-FAIL: lift < 0.005
- P_deflated: 0.25
- DEFER standalone; promote to compositional ingredient for Anchors F2 / F4

---

## Context pointers (file paths, not summaries)

- d:/AI/hd-instrument/notes/research_drill_ner_substrate_paths_remaining_2x_2026-06-11.md (this drill, authoritative)
- d:/AI/hd-instrument/notes/research_drill_ner_3datapoint_plateau_substrate_paths_2x_2026-06-11.md (sibling 2x drill on the plateau itself; cycle 235-236 LVH-287/288/289)
- d:/AI/hd-instrument/notes/research_drill_ner_substrate_paths_2x_2026-06-11.md (first NER 2x drill; baseline path inventory)
- d:/AI/hd-instrument/notes/substrate_classical_NLP_methods_outperform_phasor_2026-06-11.md (HMM emission + transition + Viterbi pattern; basis for Anchor F2)
- d:/AI/hd-instrument/notes/substrate_only_NL_pos_tagger_validated_2026-06-11.md (POS 0.9064; substrate-classical primitive validated)
- d:/AI/hd-instrument/notes/substrate_discriminative_beats_generative_asymmetric_NL_2026-06-11.md (2.4x discriminative perceptron lift; basis for Anchor F1)
- d:/AI/hd-instrument/notes/substrate_two_axes_semantic_vs_content_referenced_2026-06-11.md (semantic + content-reference + algebra; basis for Anchor F5 retrieval)
- d:/AI/hd-instrument/notes/substrate_self_index_foundational_tool.md (host platform; bundling-redundancy correction Day 1 finding)
- d:/AI/hd-instrument/notes/drill_pattern_temporal_contextual_not_structural_2026-06-11.md (drill pattern: temporal+contextual wins; informs P_deflated for F4/F5 over F2/F3)
- d:/AI/hd-instrument/notes/feedback_dont_parrot_drill_defeatism_2026-06-11.md (rule applied: 5 paths inventoried before any ceiling acceptance)
- d:/AI/hd-instrument/notes/feedback_literature_is_not_oracle_2026-06-11.md (rule applied: anti-shrinkage criterion is a substrate-empirical test not literature-derived)

---

## Contract

exp_dev owns:
- Smoke gate per envelope-fail-bands (n=300 composition-matched)
- Pre-reg per substrate-product reading + HARD-PASS / MIDDLE / HARD-FAIL thresholds (above)
- queue_add.sh dispatch (CPU lane preferred; all 5 anchors are CPU-fit)
- Post-ship REMOTE VERIFY (file presence + queue index)
- Self-test per formula-selftests
- LIFT > 2 x SE validation per method-overclaim-lift-validation memory
- Anti-shrinkage ratio reporting (lift_300 / lift_full) for Anchors F4 and F5
- Reach back to research if Anchor F4 surfaces a substrate-novel angle or contradicts pre-reg

Research owns:
- Falsifiable-prediction pre-reg (done; research-note section)
- Cross-thread synthesis with memory (done)
- P_deflated estimates with calibration penalty (done; lit-scan penalty applied; novel-synthesis capped at 0.50)
- Next-drill candidate: if F4 + F5 both HARD-FAIL, substrate-Brown-cluster equivalent via Layer-3 archaeology (already saturated at +0.011; would need fresh substrate-novel angle)

---

## Autonomy declaration

Anchor F4 is the cheap decisive test. exp_dev autonomously decides:
- Whether to dispatch F4 alone first, OR F4 + F5 as a stack (F4 result decisive within the stack via ablation)
- Smoke-test composition (composition-matched per smoke-test-methodology)
- Multi-seed at HARD-PASS boundary (recommended given 3-datapoint plateau pattern from sibling drill)
- Queue lane assignment (CPU preferred; home GPU not needed for any of F1-F5 in pure-substrate setup)
- Whether to absorb Anchor F3 into Anchor F4 implementation (research suggests yes; final call is exp_dev's)

If pause flag is set, file this hand-off but do NOT dispatch. Resume on /orchestrator-resume-experiments.
