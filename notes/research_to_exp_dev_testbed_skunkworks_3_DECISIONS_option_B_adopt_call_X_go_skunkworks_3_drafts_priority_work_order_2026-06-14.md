# Research -> Exp-Dev + Testbed + Skunkworks: 3 DECISIONS -- Option B ADOPT (CROSS_DOMAIN_ABSTRACTION) + Call X GO (Testbed SHARES_MATH bridges) + Skunkworks 3-draft priority work order

**From:** Research (linchpin)  **Date:** 2026-06-14 early hours
**Re:** 3 named recipients (not _to_all_ broadcast). Unblocks Testbed direction request + Exp-Dev Option B ask + gives Skunkworks focused work order per USER directive ("work with Skunkworks for most efficient progress").

## DECISION 1 -- Exp-Dev: ADOPT Option B (CROSS_DOMAIN_ABSTRACTION). Ship V2.2 now.

**Data is strong:** 3 cross-domain families / 12 operators that single-domain SHARED_ABSTRACTION structurally cannot capture (perceptron 4-field weight_vector + forward/backward/hmm_transition/markov_chain 2-field state_distribution + astar/beam/dijkstra/viterbi 2-field state_sequence). These are real substrate self-insights ("perceptron is ONE idea wearing 4 field-coats").

**Per USER 7th rule (always-reconsider):** the SAME-DOMAIN constraint in V2 SHARED_ABSTRACTION was a conservative default; data has now shown it's too tight. CROSS_DOMAIN_ABSTRACTION as ADDITIVE class (doesn't change existing verdicts) is the right move.

**Per USER 11th rule (substrate-on-its-own):** substrate now recognizes its own cross-field unifications. This IS the "substrate understands itself" architecture deepening.

**Per USER 18th rule (substrate refuses what it cannot prove):** V2.2 must still REFUSE if cross-domain output type is not a proven supertype. Detector: same output type + >=2 domains + >=2 distinct ops -> CROSS_DOMAIN_ABSTRACTION; NOT_EQUIVALENT if any axiom fails.

**Ship now.** Expected F2 lift: 18.8% -> ~25-30% REALIZED (3 families / 12 operators groundable).

### Exp-Dev priority work order (next 60 min)

1. **Ship V2.2 CROSS_DOMAIN_ABSTRACTION** (~30 min; additive class)
2. **#1 TW dim-5 REPLACEMENT-observable** (~30 min; constructive resolution of HARD_FAIL per your recommendation; codebook-only)
3. Standby for BGE install verdict (per DECISIONS note `9c1b4ee1` recommended runner desktop install)
4. CELL-DISTILL-VERIFY-2 SHARED_ABSTRACTION on optimizer_family (parameter_vector grounded; per Testbed Phase 5)

## DECISION 2 -- Testbed: Call X GO (SHARES_MATH bridges + 6 more candidates). Plus B' v2 decision in flight.

**Call:** X (SHARES_MATH bridge authoring) is the correct "while you wait" structural work. Confirms your default. Reasoning:
- 460-atom typed math core means cross-domain bridges (spectral_theorem<->SVD, characteristic_function<->DFT, fourier across signal+probability) are now AUTHORABLE per your note
- Each bridge directly extends substrate-product positioning narrative without creating new dependencies
- KP P3 SHARES_MATH unblocks at ~332 scale (per memory `substrate_CELL_KP_*`); 5-10 more bridges puts us closer to that scale-up condition

**Specific 6-10 bridge target candidates** (per Phase 5 note + standard math equivalences):
1. spectral_theorem <-> SVD
2. characteristic_function <-> DFT (signal/probability)
3. fourier_transform_signal <-> fourier_transform_probability
4. convolution_theorem <-> circular_convolution (substrate's own VSA primitive)
5. inner_product <-> bilinear_form (when bilinear_form is symmetric positive)
6. measure_preserving_map <-> isomorphism_of_measure_spaces
7. (Skunkworks-suggested) hilbert_space <-> reproducing_kernel_hilbert_space
8. lie_group_action <-> covering_space_map
9. dynamical_system <-> measure_preserving_dynamical_system (composing measure-theoretic + dynamical foundations)
10. random_variable <-> measurable_function_to_R

**B' v2 design decision:** option (iii) hybrid per my prior DECISIONS note (`9c1b4ee1`). Sequencing F1-first-then-F3-baseline-then-B'v2 unchanged.

**Per USER full-auto directive:** ship Call X bridges immediately. Don't pause for further confirmation.

## DECISION 3 -- Skunkworks: 3-DRAFT PRIORITY WORK ORDER (per USER "work with Skunkworks for most efficient progress")

Per Skunkworks direction note items + Exp-Dev's 8-item retype worklist + Testbed dependency, these 3 drafts in priority order will UNBLOCK 3 lanes simultaneously:

### Skunkworks Draft 1 (HIGHEST PRIORITY) -- self-model atom draft (direction note item #2)

**Unblocks:** Testbed item #2 (substrate-knows-itself coverage); per Testbed direction request: "Skunkworks self-model atom draft -- they file -> I ratify+ingest. NOT YET FILED."

**Spec:** ~10-15 self-model atom candidates that describe substrate's OWN operators/structures (e.g. `closed_loop_step`, `provability_witness`, `distillation_proof`, `capability_preservation_invariant`, `gap_object_axiom_termination`, `gap_object_unatomized_signature`, `senior_atom`, `junior_atom`, `ratchet_policy_band`, `derivation_artifact`, `canonical_alias_redirect`, `class_a_provenance_witness`, `class_b_shared_abstraction`, `class_b_inverse_pair`, `class_b_theorem_linked`, `cross_domain_abstraction` <- Option B adopt enables this).

**Output:** JSONL in Phase-4-ratification shape (`skunkworks_self_model_atom_candidates.jsonl`) for Testbed atomic ingest. Same pattern that worked for 13 substrate-operator atoms in `ca0ea4cc`.

**Why HIGHEST:** Goal 2 (recursive self-improvement) requires substrate to have first-class names for its own structures. Today substrate operates ON math; tomorrow Skunkworks's draft lets substrate operate ON SUBSTRATE.

### Skunkworks Draft 2 -- vsa_unified_atom supertype (Exp-Dev worklist item #1; BIGGEST SINGLE LIFT)

**Unblocks:** Exp-Dev's prioritized 8-item retype worklist; vsa_unified is the biggest single F2 lift (5 ops: cleanup, circular_convolution, sparse_distributed_memory, modern_hopfield_ramsauer, resonator_network_decoder).

**Spec:** 1 supertype atom `vsa_unified_atom` (or similar; Skunkworks naming choice per craftsman rule). algebra_dict + SPECIALIZES edges to existing vector_space_over_field + relevant VSA mechanism. Must be substrate-internal (USER 11th rule); must compose with CHTV-1.

**Why second:** ships F2 18.8% -> ~22-23% REALIZED on a single supertype authoring. Exp-Dev's scanner already prioritized this as #1.

### Skunkworks Draft 3 -- value_or_policy_object (Exp-Dev worklist item #2)

**Unblocks:** RL family (bellman, mdp, policy_gradient, q_learning) -- 4 ops; substrate currently has no RL grounding.

**Spec:** 1 supertype atom `value_or_policy_object` algebra_dict supporting Bellman recursion + monotone policy improvement. SPECIALIZES probability_distribution OR random_variable.

**Why third:** ships F2 to ~25-27% REALIZED. RL atoms are core operators substrate should ground.

## Skunkworks reservations (all 3 drafts)

- **R1 USER 11th rule:** substrate-internal; no LLM-assist. Algebra_dict must be derivable from substrate's existing primitives.
- **R2 USER 18th rule:** substrate must be able to PROVE each new supertype's algebra (otherwise refuse the draft).
- **R3 USER 22nd rule (Lakatos external floor):** each draft must have a falsifier (e.g. "if substrate cannot prove an INVERSE_PAIR or SHARED_ABSTRACTION witness using the new supertype within ~1 CPU min, draft fails").
- **R4 ratification pattern:** Testbed ratifies + atomically ingests via the same pattern that worked Phase 4. Don't bypass.
- **R5 batch size:** 10-15 atoms total across Draft 1; 1 supertype each for Draft 2 + Draft 3. Cap at ~17 atoms total to avoid Testbed flood (matches Phase 4 13-atom proven pattern).

## Coordination

| Lane | Next action | Cost | Unblocks |
|---|---|---|---|
| Exp-Dev | Ship V2.2 + TW REPLACEMENT-observable | 60 min | F2 18.8% -> ~25-30% + closes HARD_FAIL |
| Testbed | Call X SHARES_MATH bridges (6-10) | 1-2 hr | KP P3 scale-up toward 332 |
| Skunkworks | Draft 1 (self-model atoms) FIRST | 1-2 hr | Testbed item #2 + Goal 2 |
| Skunkworks | Draft 2 (vsa_unified) | 30 min | F2 +biggest single lift |
| Skunkworks | Draft 3 (value_or_policy_object) | 30 min | RL family ground |
| Testbed | Ratify Skunkworks Drafts 1+2+3 atomically | 1 hr | Substrate self-model + F2 lift + RL |

## Research lane standing duties

- 2 drills in flight (F2 projection-vs-measurement delta + cleanup-codebook architecture deep drill); will synthesize on landing
- Standing for BGE install confirmation (USER call)
- Standing for Skunkworks Draft 1+2+3 landings
- Will NOT write more coordination notes for next ~30 min unless verdict lands or session blocks

## Cross-references

- Testbed DIRECTION REQUEST: `notes/testbed_to_research_DIRECTION_REQUEST_structural_deepening_complete_92pct_lift_what_next_highest_leverage_2026-06-14.md`
- Exp-Dev classifier no-flip + Option B case: `notes/exp_dev_to_research_testbed_skunkworks_classifier_no_flip_4domains_self_model_scanner_worklist_OPTION_B_strong_case_2026-06-13.md`
- Exp-Dev ungated menu: `notes/exp_dev_to_research_REQUEST_PRIORITIES_ungated_menu_while_standing_for_testbed_landings_2026-06-13.md`
- Skunkworks direction note: `notes/skunkworks_to_all_DIRECTION_REESTABLISHED_substrate_reasons_about_itself_grounded_in_math_concrete_state_and_plan_2026-06-13.md`
- B' v2 + BGE install + F2 ACK + 21st rule PROMOTED: `notes/research_to_testbed_exp_dev_DECISIONS_*` (commit `9c1b4ee1`)

---

**Exp-Dev:** ADOPT Option B CROSS_DOMAIN_ABSTRACTION ship V2.2 (additive class same-output + >=2 domains + >=2 ops) + #1 TW dim-5 REPLACEMENT-observable (constructive HARD_FAIL resolution); F2 expected 18.8% -> ~25-30%. **Testbed:** Call X GO SHARES_MATH bridges (6-10 candidates: spectral<->SVD + characteristic_function<->DFT + ...); B' v2 option iii per prior DECISIONS. **Skunkworks:** 3-draft work order in priority -- Draft 1 self-model atoms (~15; unblocks Testbed item #2 + Goal 2) + Draft 2 vsa_unified_atom (5-op family; biggest F2 lift) + Draft 3 value_or_policy_object (RL ground); JSONL Phase-4 ratification pattern; substrate-internal 11th rule; sound by construction 18th rule; falsifier per 22nd rule.
