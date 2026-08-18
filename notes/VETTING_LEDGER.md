THE VETTING LEDGER -- every claim that has been checked, its verdict, and its DISPOSITION.

WHY THIS EXISTS (owner, 2026-08-18): "make sure these are making it into a clear final wired and/or
well tracked state. Everything should be categorized so we don't lose it again."

The "again" is earned. This project lost track of its own results three separate ways in one day:
  - `tools/substrate_query.sh`, the MANDATORY prior-work check, RETURNS ZERO BYTES AND EXITS 0, so
    every "no prior work found" report from every agent and from the Director was vacuous;
  - the figure "3,544 grounded concepts / 9.87x the hand lexicon" was REFUTED ON OUR OWN DISK by a
    successor cell and was still being quoted in `SUBSTRATE_CHARTER_read_first.md`, the document
    every session is told to read first;
  - `exp_unified_self_learning_loop_v3` was refuted by its OWN v4 five hours later and was still
    sitting on the vetting queue as a HARD_PASS weeks afterwards.
A verdict that lives only in a session transcript is a verdict the project will re-derive or,
worse, keep citing. This file is the durable home.

DISPOSITIONS -- every vetted cell gets exactly one, and nothing is allowed to sit in limbo:
  WIRE            UPHELD. Survives its own controls. Promote and register it.
  WIRE_NARROWED   QUALIFIED. Real but narrower than claimed. Citable ONLY with the narrowing
                  attached, which is recorded in `narrowing` and must travel with the number.
  RERUN_NAMED     SUSPENDED. Cannot be judged as it stands; the specific rerun is named in `rerun`.
  SHELVED_REFUTED REFUTED. Do NOT cite. If a figure from it is quoted anywhere, retire it there too.

THE RECORD SO FAR: 30 cells vetted across five passes -- 13 REFUTED, 5 SUSPENDED, 11 QUALIFIED,
**1 UPHELD**.

TWO PREDICTORS, IN ORDER OF STRENGTH. Both were learned from this ledger's own contents:
  1. **DID THE TEST ITEMS EXIST BEFORE THE MECHANISM DID?** This is the strong one. Every survivor
     was scored on items built independently of the rule; every refutation in pass 5 had detectors
     authored against the very items they were scored on. Free to check, and it beats every
     statistical signal we tried.
  2. Does the file carry a CI and a null? Necessary and WEAK -- `tools/verdict_evidence_gate.py`
     measures it (only 13 of 2,678 HARD_PASS carry both), but a cell can carry both and still be
     refuted, and one in this ledger is.

**30 cells vetted.** RERUN_NAMED 4 | SHELVED_REFUTED 13 | WIRE 1 | WIRE_NARROWED 12

## WIRE -- UPHELD, survives its own controls  (1)

Promote and register. The claim stands as made.

### `exp_agreement_depth_productivity_generalization_v1`  <sub>pass 5</sub>
Supervised only on depth<=1; 0.7324 [0.7154,0.7494] on 2,597 held-out depth>1 items vs majority floor 0.5741 (upper 0.5931); margin +0.1223 from the CI LOWER bound; holds OOD at depth 4+; scramble changes 86.5% of decisions.
- **NARROWING (must travel with the number):** TIES the hand-written recursive rule (0.7312), does not beat it. Parity, not supremacy.

## WIRE_NARROWED -- QUALIFIED, real but narrower than claimed  (12)

**Citable ONLY with the narrowing attached.** The narrowing is not a footnote; it is part of the result, and every one of these was claimed without it.

### `exp_graded_divisive_comparator_v1`  <sub>pass 5</sub>
Real +0.0602 [0.0440,0.0762] over the live comparator; scramble twin 0.5065.
- **NARROWING (must travel with the number):** CI lower bound does NOT clear its own pre-registered d>=0.05, and the 'divisive normalisation' half of the title contributes +0.00175.

### `exp_read_xsent_coref_scene_protagonist_v1`  <sub>pass 5</sub>
Accuracy 0.2462 -> 0.4003; McNemar CI lower +0.1039 off its own discordant counts.
- **NARROWING (must travel with the number):** The mechanism is a 5-sentence WINDOW, not 'scenes'. The cell says so itself.

### `exp_pivot_selectional_knowledge_richness_2afc_v1`  <sub>pass 4</sub>
117 rated pairs vs 117 eval pairs is a PERFECT BIJECTION -- an LLM rated exactly the test. But the dumb twins do NOT reproduce it (0.5508 / 0.5339 / 0.4915).
- **NARROWING (must travel with the number):** A CHEATING ORACLE reaches 0.78-0.85; the substrate did none of it. What it proves is that the knowledge is real AND ABSENT FROM OUR CORPUS -- which is the useful half.

### `exp_learned_argstruct_parser_lccp_independent_gold_v1`  <sub>pass 4</sub>
Arm B (NO LCCP) already clears every gate; adding LCCP moves F1 0.3934->0.4048, two items.
- **NARROWING (must travel with the number):** The wrong component is credited, and 'generalizes' is a ONE-SIDED gate that fired because the held-out subset was EASIER (precision 0.632 vs 0.449). Absolute P=0.50, R=0.34.

### `exp_reading_grounding_loop_cycle1_v1`  <sub>pass 3</sub>
Context-scramble control BINDS (removed 132 of 185).
- **NARROWING (must travel with the number):** Same 67% self-anchoring applies; its curriculum-order arm is a NULL shipped inside a pass (0.3297 -> 0.3047).

### `exp_c5_primacy_trap_endtoend_goal_coherence_candidate_gen_v1`  <sub>pass 3</sub>
Genuinely LEAK-CLEAN -- it fixed a predecessor's gold leak and proves it with seven self-tests.
- **NARROWING (must travel with the number):** Its four floors are ALL POSITIONAL and read 0.0000 by construction; a lexical-overlap floor scores 0.80/0.675 and its CI OVERLAPS the system's.

### `exp_context_vector_signal_v1`  <sub>pass 2</sub>
THE DENIAL QUESTION IS CLOSED CLEAN: heartbeats from unit 0 prove a cache miss, so the run was a genuine fresh computation and CLAUDE.md's requested clean-slate re-run is NOT needed.
- **NARROWING (must travel with the number):** CITE `argmax_in_own_window_rate` 0.2871 vs an exactly bag-matched scramble 0.0050 -- NOT the ceiling-saturated 0.7830/0.9984 pair. And its HARD_PASS is POST-HOC: the pre-registered ceiling guard fired and was amended away after the run; prereg-literal tier is MIDDLE_BAND.

### `exp_lexicon_coverage_audit_barrier2_v1`  <sub>pass 2</sub>
The COVERAGE half is UPHELD EXACTLY -- independently re-implemented, every figure reproduces to 4 dp (union 0.9893/0.9648).
- **NARROWING (must travel with the number):** The second half is a SINGLE-RATER, UNBLINDED LLM self-audit of the prediction being tested; under the stricter rubric the cell itself names, it falls to 0.7417, BELOW its own 0.80 floor.

### `exp_information_foraging_reading_v1`  <sub>pass 2</sub>
FORAGE genuinely beats RANDOM (185 vs 38 of 3000, z=10.1).
- **NARROWING (must travel with the number):** A FLOOR-BEATER, NOT A SHELF-BEATER: FROZEN, the fixed schedule foraging exists to REPLACE, scores HIGHER (0.0743 vs 0.0617). Any claim it improved reading must say this.

### `exp_read_grow_construction_induction_dop_fragments_v1`  <sub>pass 1</sub>
The strongest of the first six: real external corpus (UD English-EWT, 846 sentences), deprel-multiset-preserving scramble binding HARD across 3 seeds (2/124 vs 44/124 etc), CI-separated 0.355 [0.271,0.439], split_overlap=0.
- **NARROWING (must travel with the number):** Parses are GOLD-SUPPLIED (upos+deprel read directly) and the metric is COVERAGE, not correctness (tunable 0.508/0.355/0.25 by min_count). Its own label -- FEASIBILITY PROBE -- is the honest one.

### `exp_read_grow_openvocab_fastmap_v1`  <sub>pass 1</sub>
Real mechanism; its NO_CONFIRM control binds (removed 2 false facts).
- **NARROWING (must travel with the number):** TOY SCOPE: 26 hand-authored sentences, 3 nonce words, 5 query cues; ABSTAIN_BASELINE=0.0 BY CONSTRUCTION; 5 seeds vary only the codebook, so n=1 dataset; no CI, no floor, no scramble.

### `exp_read_grow_oov_verb_extension_v1`  <sub>pass 1</sub>
Real residue: the morphology inverter.
- **NARROWING (must travel with the number):** `OOV_VERB_BASE_LEX` HARDCODES munch->eats etc, and THE SAME TABLE GENERATES THE SENTENCE AND SCORES IT; coverage_current_pooled=0.0 by construction, so '+88.2pp' is a gain over a definitional zero. Its OOS control removed 0 items.

## RERUN_NAMED -- SUSPENDED, cannot be judged as it stands  (4)

Not refuted. The named rerun would settle it.

### `exp_multi_turn_loop_realtext_nphead_gate_v1`  <sub>pass 5</sub>
'True zero confident-wrong' is 0 wrong of 18 KEPT (rule-of-three upper 0.167) against a declared band of 0.01; its new variable fired on 2 items that are the same passage, same answer, same gold.
- **RERUN:** RERUN: enough kept items to resolve 0.01, and independent events rather than one passage.

### `exp_outcome_valence_goal_congruence_v1`  <sub>pass 4</sub>
The dumbest rule (goal verb lemma == outcome verb lemma) scores 7/8 = EXACTLY the pre-registered floor; mechanism beats it by one item; CIs overlap; P(8/8|p=0.875)=0.34.
- **RERUN:** RERUN: >=20 D-type items where lemma-identity and goal-congruence DISSOCIATE, on verbs outside the hand-authored register, banked by someone who did not write it.

### `exp_read_grow_foundation_realprose_glassbox_ie_v1`  <sub>pass 1</sub>
Its only floor is a HARDCODED literal 1.0 imported from a different cell on a different corpus; no floor was run on its own 34 sentences.
- **RERUN:** DO NOT CITE v1. CITE `exp_read_grow_foundation_realprose_glassbox_ie_v2` INSTEAD: 46 sentences, 0.891 vs a REAL STANDALONE baseline 0.565, stub removed.

### `exp_online_knowledge_condenser_selectional_v1`  <sub>pass 1</sub>
Best-designed of the first six -- real held-out split, explicit leakage guard, 4,151 mining sentences -- but n=48; FULL 0.750 [0.6275,0.8725] vs a 0.650 shuffle floor; z=1.07, p=0.285.
- **RERUN:** RERUN at n~350, which is what separating 0.75 from 0.65 at 80% power requires.

## SHELVED_REFUTED -- DO NOT CITE  (13)

If a figure from one of these is quoted anywhere, retire it there too -- that is how the 3,544-concept number survived in the charter for weeks after being refuted.

### `exp_social_relational_grounding_axis_v1`  <sub>pass 5</sub>
`valence` takes exactly THREE distinct values across all 12 items, and acc_real equals the WordNet dictionary_lookup accuracy EXACTLY (10/12).
- **NARROWING (must travel with the number):** A 3-entry lookup table wearing a substrate; it cannot change any prediction.

### `exp_desiderative_negation_channel_v1`  <sub>pass 5</sub>
8 of 8 recoveries lie INSIDE the 10-item set the taxonomy was designed from; 0 of 27 outside it; channel bit-identical ON vs OFF on both benches (0.6992/0.6992, 0.6623/0.6623).
- **NARROWING (must travel with the number):** Pattern (f): the test items did not exist before the mechanism.

### `exp_causal_link_comprehension_pilot_v1`  <sub>pass 4</sub>
Sibling of fuller_v3: the answer is written in and read back.

### `exp_causal_link_comprehension_fuller_v3_cleaned`  <sub>pass 4</sub>
Re-ran with gold links replaced by RANDOM PAIRS -> organ_integration 0.9722, BIT-IDENTICAL to the headline. Measures FHRR write/read fidelity at bundle-load 2. Baseline was swept until it failed ('...while driving mr_integration to 0.0000').

### `exp_causal_link_comprehension_fuller_v2`  <sub>pass 4</sub>
Same code as fuller_v3; dies with it.

### `exp_unified_self_learning_loop_v3`  <sub>pass 4</sub>
Its OWN scramble control scored HIGHER (0.0288 vs 0.0243); separation gates are literally 0.0; two arms share a store digest; and its v4 five hours later records teaches_new=False.

### `exp_gap_driven_reader_controlled_v1`  <sub>pass 3</sub>
A 12-line `Counter` with no substrate reproduces the headline 8/8 exactly; the margin is authored into the templates.

### `exp_reading_grounding_loop_cycle2_v1`  <sub>pass 3</sub>
Already refuted ON DISK by cycle3 (3544 -> 634). 2,328 of 3,544 GROUNDED_MEANING facts are SELF-ANCHORED. NOTE: this cell CARRIES a CI and a null and is still refuted -- proof that the evidence gate is necessary, not sufficient.
- **NARROWING (must travel with the number):** RETIRE the figure '3,544 concepts / 9.87x the hand lexicon' wherever it appears.

### `exp_verb_class_openvocab_similarity_v1`  <sub>pass 3</sub>
All 26 words -- 10 seeds AND 16 'held-out' -- share ONE hand-written tag vector, so held-out similarity is exactly 1.0000. 64 decisions, 4 distinct vectors. Its cited baseline of 0.30 reads 0.6000 on disk and postdates the run.

### `exp_c5_multigoal_content_coherence_tiebreak_v1`  <sub>pass 3</sub>
Gold is defined by the rule the mechanism applies; bag-of-words overlap scores 12/12 under all three tie conventions. Margin over the strongest floor: 0.0000.

### `exp_pivot_scaled_seed_knowledge_table_v1`  <sub>pass 2</sub>
A corpus-attestation floor computable from the cell's OWN cache scores 1.0000 (108/108) vs the LLM table's 0.6898. And scaling changed NOTHING: scaled and tiny digests identical, arms_differ_verified=False.

### `exp_read_grow_adaptor_pyp_kn_breadth_v1`  <sub>pass 2</sub>
Treatment coverage is a STRICT SUPERSET of baseline by construction, so the gate cannot fail; '3/3 seeds' is one measurement printed three times; a Zipf null reproduces the preemption correlation; on the only genuine generalization test it is WORSE than its own scramble.

### `exp_base_reader_grounded_relations_coref_v1`  <sub>pass 1</sub>
Headline p=0.000 is RESAMPLE DEGENERACY -- (2/7)^7 over SEVEN paired differences. Exact McNemar gives p=0.0625, failing its own alpha. The cell RAN a real floor scoring 5/7 and did not use it.
- **NARROWING (must travel with the number):** SURVIVING SECONDARY: relation_lift over all 25 items, full vs floor exact p=0.0215.

