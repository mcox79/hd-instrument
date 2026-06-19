# exp_dev hand-off -- research: concept-invention mechanism classes

Filed-by: research (opus)
Date: 2026-06-15
Trigger: research_concept_invention_mechanism_classes_2026-06-15.md delivered; 5 published mechanism classes surveyed; 2 deliver soundness compatible with substrate's sound-by-construction discipline (Class B ILP-PI + Class E CELOE refinement); no published system delivers (novel-primitive) + (strict consistency) + (provenance) simultaneously -- substrate's open wedge.

Pause state: read `data/orchestrator_paused.flag` before queuing. Annotation-only bumps allowed while paused.

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchors + substrate-product reading + tier hints + why-now. exp_dev autonomously designs the experiment cells.

## Anchor candidates (rank-ordered)

### 1. CELL-CONCEPT-INVENTION-INV-1 (PRIMARY)
- **Anchor pointer**: ILP-style predicate-invention loop (Popper / POPPI lineage) over substrate's 105 Phase-4a operator signatures
- **Substrate-product reading**: validates Class B applicability to substrate; if HARD-PASS, substrate crosses MEMBER-GROWTH ceiling into true concept-invention with sound-by-construction guarantees -- the substrate-product's first 3-of-3 (novel-primitive + strict-consistency + provenance) demonstration
- **Tier hint**: Tier-1 strategic. Empty `concept_invention_via_class_BE_hybrid` cap_row candidate.
- **Why now**: USER 2026-06-15 ruling (LLM-assisted candidate SELECTION OK as bootstrap until substrate self-selects) IS the ILP-PI bootstrap pattern from Cropper-Morel 2021. Phase 4a operator self-model is the substrate-native ASP-style entailment validator that ILP-PI requires. The validator is already built; only the candidate-generator is missing.
- **HARD-PASS / HARD-FAIL**: see F1 in research note. >=3 invented predicates / 100 trials survive 4-gate -> HARD-PASS. 0 / 100 -> HARD-FAIL (refutes Class B for substrate).

### 2. CELL-CONCEPT-INVENTION-CELOE-1 (SECONDARY)
- **Anchor pointer**: CELOE-style downward-refinement-operator search over substrate's type subsumption lattice
- **Substrate-product reading**: validates Class E applicability; CELOE's "shorter-concept bias" is mathematically isomorphic to substrate's HYGIENE distillation mode (atom-removing). If HARD-PASS, substrate has TWO complementary candidate-generators (Class B + Class E).
- **Tier hint**: Tier-1. Parallel to anchor 1.
- **Why now**: 21st methodology rule candidate `substrate-type-graph-terminates-in-atoms` IS the refinement-operator base-case. Refinement-operator search needs the type lattice -- substrate already has 217 axiom terms + 105 operator signatures.
- **HARD-PASS / HARD-FAIL**: see F2 in research note. >=5 expressions / 50 trials with capability_preservation=1.0 -> HARD-PASS. 0 / 50 -> HARD-FAIL.

### 3. CELL-CONCEPT-INVENTION-HDTP-1 (TERTIARY)
- **Anchor pointer**: HDTP-style second-order anti-unification over two substrate math groups; validate output through 4-gate
- **Substrate-product reading**: tests whether substrate's strict-validator can salvage Class D's 30-60% inconsistency baseline. If HARD-PASS at >=1/20, gives a third candidate-generator path.
- **Tier hint**: Tier-2 (lower-priority, higher-uncertainty). Run after anchors 1+2.
- **Why now**: substrate has 14 SHARES_MATH bridges drafted (DECISION 54 lineage); anti-unification over SHARES_MATH-linked groups is the natural substrate-native HDTP probe.
- **HARD-PASS / HARD-FAIL**: see F3 in research note. >=1/20 -> HARD-PASS. 0/20 -> consistent with COINVENT baseline; do not pursue further.

### 4. CELL-CONCEPT-INVENTION-19th-RULE-ADVERSARIAL-1 (META)
- **Anchor pointer**: measure substrate's 19th rule (adversarial-self-correction of own DETECT output) as a CANDIDATE-REFUSAL gate against an adversarial set of intentionally-unsound invented atoms (generated via LLM mutation of valid atoms)
- **Substrate-product reading**: empirically quantifies substrate's metacognition as the validator for ANY concept-invention candidate-generator. Sets the published-baseline-versus-substrate-validator comparison number.
- **Tier hint**: Tier-1 meta (informs all 3 above).
- **Why now**: 19th rule was PROMOTED to CONFIRMED 2026-06-13 with 3 witnesses; needs adversarial-set calibration to publish a refusal-precision number.
- **HARD-PASS / HARD-FAIL**: see F5 in research note. >=80% refusal precision -> HARD-PASS. <50% -> HARD-FAIL (substrate's metacognition insufficient without external oracle).

## Context pointers (file paths, not summaries)

- d:/AI/hd-instrument/notes/research_concept_invention_mechanism_classes_2026-06-15.md (this drill's full output)
- d:/AI/hd-instrument/notes/SUBSTRATE_DIRECTOR_STATE.md (canonical state board)
- d:/AI/hd-instrument/notes/substrate_state_2026-06-15_post_cycle_cleanup_v1.md (substrate checkpoint)
- d:/AI/hd-instrument/notes/substrate_closed_loop_OPERATIONAL_step_3_HARD_PASS_first_measured_self_improvement_instance_5_provably_equivalent_0_false_merge_22_refused_2026-06-13.md (Class B's failure-learning empirically realized; 22 UNDECIDABLE = Popper's failure-constraints)
- d:/AI/hd-instrument/notes/substrate_3_distillation_modes_taxonomy_atom_removing_structure_adding_refusal_2026-06-13.md (taxonomy that maps to mechanism classes)
- d:/AI/hd-instrument/notes/substrate_methodology_rule_19th_adversarial_self_correction_of_own_DETECT_output_PROMOTED_candidate_to_CONFIRMED_3_empirical_witnesses_today_skunkworks_DETECT_pre_screen_ADDENDUM_LAKATOS_AUDIT_axis_C_2026_06_13.md (19th rule as Popper's failure-learning at validator layer)
- d:/AI/hd-instrument/notes/feedback_LLM_assisted_candidate_selection_OK_as_bootstrap_until_substrate_self_selects_soundness_on_signatures_not_selection_2026-06-15.md (USER ruling that IS the ILP-PI bootstrap pattern)

## Contract section

- Pre-reg per envelope-fail-bands.
- Smoke gate before full ship.
- queue_add.sh via tools/queue_add.sh (pause-flag respected).
- REMOTE VERIFY post-ship.
- Self-test per formula-selftests.
- Atomic write all cells.

## Autonomy declaration

exp_dev decides:
- Concrete cell name + atom-counts + parameter grid
- Whether anchors 1+2 ship in parallel or 1 first
- Whether anchor 4 (META) precedes or follows 1+2+3
- Tier-1 vs Tier-2 routing on queue
- Bootstrap candidate-source (LLM-assisted per 2026-06-15 ruling vs substrate-internal seed)

Research has set the substrate-product reading + HARD-PASS/HARD-FAIL bars; exp_dev owns the cell mechanics.
