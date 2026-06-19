# Research -> Testbed: T1+T2 BATCH 26 -- 12 MOTIVATION + TIME substrate primitives -- philosophy INFORMAL_SYSTEMS content-type per USER architecture extension -- INGEST-READY

**From:** Research (guiding session)  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight; per WHILE-USER-AWAY L4 priority queue; per USER architecture extension implications motivation + time-based ruleset)

## Intuitive framing

Substrate currently has no explicit MOTIVATION or TIME-BASED ruleset. Like a chef who has tools and materials but no understanding of "why cook" or "when to serve."

Per USER architecture extension (philosophy as 4th content-type):
- **MOTIVATION primitives** = informal-system atoms for substrate's "why does it operate?" (philosophy of action: intentionality + agency + practical reason)
- **TIME-BASED primitives** = informal-system atoms for substrate's "when + how does change happen?" (philosophy of time: A/B series + diachronic identity + causation + temporal logic)

These are INFORMAL_SYSTEMS per the 4-way content-type axis (rule-governed thought systems but NOT mathematically axiomatizable; reasoning is dialectical not deductive). Promotion via argument-coherence + dialectical-position not L6-PROOF formal proof.

## Batch 26 -- 12 motivation + time primitives

```yaml
# MOTIVATION primitives (philosophy of action / agency / intentionality)
- canonical_name: intentionality_aboutness_relation
  tier: T1
  partition: math_foundation::philosophy_of_mind
  science_algebra_category: informal_systems::philosophy_of_action::intentionality
  algebra_dict:
    definition: "mental state has intentional content; is ABOUT some object/concept; reference relation explicit (Brentano 1874)"
    properties: [aboutness_directedness, propositional_content, intensional_not_extensional]
    related: [husserl_noema, searle_intentionality, brentano_aboutness]
  is_axiom: true
  content_type: INFORMAL_SYSTEMS
  substrate_load_bearing: false   # substrate KNOWS this concept; not yet used by operators
  serves_capability: [substrate_self_knowledge_aboutness, motivation_ruleset_foundation]
  signature_hint: aboutness_relation_axiom

- canonical_name: goal_directedness_telos
  tier: T1
  partition: math_foundation::philosophy_of_mind
  science_algebra_category: informal_systems::philosophy_of_action::teleology
  algebra_dict:
    definition: "directedness-toward-end; aristotelian telos (final cause); davidson 1963 'Actions Reasons and Causes'"
    related: [aristotle_telos, davidson_actions_reasons, anscombe_intention]
  is_axiom: false
  content_type: INFORMAL_SYSTEMS
  substrate_load_bearing: false
  serves_capability: [substrate_master_plan_telos, motivation_ruleset_means_end]
  depends_on: [intentionality_aboutness_relation]
  signature_hint: telos_directedness_toward_end

- canonical_name: practical_reason_anscombe
  tier: T2
  partition: math_foundation::philosophy_of_mind
  science_algebra_category: informal_systems::philosophy_of_action::practical_reason
  algebra_dict:
    definition: "reasoning about what to DO not what is the case (Anscombe 1957); practical syllogism + means-end reasoning"
    related: [aristotle_practical_syllogism, anscombe_intention, davidson_action]
  is_axiom: false
  content_type: INFORMAL_SYSTEMS
  substrate_load_bearing: false
  serves_capability: [substrate_decision_making, master_plan_reasoning]
  depends_on: [goal_directedness_telos, intentionality_aboutness_relation]
  signature_hint: practical_reasoning_about_action

- canonical_name: agency_higher_order_desire_frankfurt
  tier: T2
  partition: math_foundation::philosophy_of_mind
  science_algebra_category: informal_systems::philosophy_of_action::agency
  algebra_dict:
    definition: "Frankfurt 1971 hierarchy of desires; first-order desire wants X; second-order desire wants to want X; agency = higher-order endorsement"
    properties: [hierarchy_of_desires, second_order_endorsement, wantonness_as_failure]
    related: [frankfurt_freedom_of_will, taylor_dignity, bratman_planning_theory]
  is_axiom: false
  content_type: INFORMAL_SYSTEMS
  substrate_load_bearing: false
  serves_capability: [substrate_recursive_self_improvement_higher_order, master_plan_endorsement]
  depends_on: [practical_reason_anscombe, intentionality_aboutness_relation]
  signature_hint: higher_order_desire_endorsement

- canonical_name: bratman_planning_theory
  tier: T2
  partition: math_foundation::philosophy_of_mind
  science_algebra_category: informal_systems::philosophy_of_action::planning
  algebra_dict:
    definition: "Bratman 1987 'Intentions Plans and Practical Reason'; planning agency = future-directed intentions + plans as structures of practical reasoning"
    properties: [partial_plans, plan_filtering, reconsideration_resistance]
    related: [bratman_intentions_plans, anscombe_intention, agency_higher_order_desire_frankfurt]
  is_axiom: false
  content_type: INFORMAL_SYSTEMS
  substrate_load_bearing: false
  serves_capability: [substrate_master_plan_structure, future_directed_intention]
  depends_on: [practical_reason_anscombe, agency_higher_order_desire_frankfurt]
  signature_hint: planning_as_practical_reasoning_structure

# TIME-BASED primitives (philosophy of time / diachronic identity / causation)
- canonical_name: a_series_indexical_temporal_NOW
  tier: T1
  partition: math_foundation::philosophy_of_time
  science_algebra_category: informal_systems::philosophy_of_time::a_series
  algebra_dict:
    definition: "McTaggart 1908 A-series; indexical temporal predicates past/present/future relative to NOW pointer"
    properties: [indexical_PAST_PRESENT_FUTURE, NOW_pointer_required, presentism_compatible]
    related: [mctaggart_unreality_of_time, prior_tense_logic, presentism]
  is_axiom: true
  content_type: INFORMAL_SYSTEMS
  substrate_load_bearing: false
  serves_capability: [substrate_NOW_pointer, agent_temporal_reasoning]
  signature_hint: indexical_temporal_NOW_axiom

- canonical_name: b_series_relational_temporal
  tier: T1
  partition: math_foundation::philosophy_of_time
  science_algebra_category: informal_systems::philosophy_of_time::b_series
  algebra_dict:
    definition: "McTaggart B-series; relational earlier-than/later-than predicates; permanent + not indexical"
    properties: [earlier_than_relation, eternalist_compatible, no_NOW_required]
    related: [mctaggart_unreality_of_time, mellor_real_time, sider_four_dimensionalism]
  is_axiom: true
  content_type: INFORMAL_SYSTEMS
  substrate_load_bearing: false
  serves_capability: [substrate_commit_history_temporal, B_series_event_ordering]
  signature_hint: relational_temporal_earlier_later

- canonical_name: diachronic_identity_persistence_parfit
  tier: T2
  partition: math_foundation::philosophy_of_time
  science_algebra_category: informal_systems::philosophy_of_time::diachronic_identity
  algebra_dict:
    definition: "Parfit 1984 personal identity across time; persistence via psychological-continuity + connectedness vs branching"
    properties: [psychological_continuity, branching_problem, identity_what_matters]
    related: [parfit_reasons_persons, lewis_temporal_parts, sider_four_dimensionalism]
  is_axiom: false
  content_type: INFORMAL_SYSTEMS
  substrate_load_bearing: false
  serves_capability: [substrate_cycle_to_cycle_identity, cross_cycle_continuity]
  depends_on: [b_series_relational_temporal, a_series_indexical_temporal_NOW]
  signature_hint: psychological_continuity_persistence

- canonical_name: causal_intervention_pearl
  tier: T2
  partition: math_foundation::philosophy_of_time
  science_algebra_category: informal_systems::philosophy_of_time::causation
  algebra_dict:
    definition: "Pearl 2009 causal hierarchy 1-2-3; level 2 intervention do(X=x) counterfactual; substrate's recursive loop Stage 4 verify-fix-spec IS intervention"
    properties: [do_operator_intervention, structural_causal_model, levels_1_2_3_hierarchy]
    related: [pearl_causality, woodward_interventionism, halpern_causes_explanations]
  is_axiom: false
  content_type: INFORMAL_SYSTEMS
  substrate_load_bearing: false
  serves_capability: [substrate_recursive_loop_Stage_4_intervention, causal_inference]
  depends_on: [causation_concept_general, conditional_probability]
  signature_hint: interventional_do_operator

- canonical_name: counterfactual_dependence_lewis
  tier: T2
  partition: math_foundation::philosophy_of_time
  science_algebra_category: informal_systems::philosophy_of_time::counterfactuals
  algebra_dict:
    definition: "Lewis 1973 'Counterfactuals'; counterfactual If A had not occurred, C would not occur; closeness of possible worlds semantics"
    properties: [possible_world_semantics, similarity_metric_over_worlds, sphere_system]
    related: [lewis_counterfactuals, stalnaker_a_theory_of_conditionals, pearl_causality]
  is_axiom: false
  content_type: INFORMAL_SYSTEMS
  substrate_load_bearing: false
  serves_capability: [substrate_recursive_loop_Stage_6_regression_check, counterfactual_reasoning]
  depends_on: [causal_intervention_pearl]
  signature_hint: possible_world_similarity_counterfactual

- canonical_name: linear_temporal_logic_LTL
  tier: T2
  partition: math_foundation::philosophy_of_time
  science_algebra_category: informal_systems::philosophy_of_time::temporal_logic
  algebra_dict:
    definition: "Pnueli 1977 Linear Temporal Logic; modal operators X (next) F (eventually) G (always) U (until); LTL formula evaluated over infinite linear sequence of states"
    properties: [linear_time_assumption, modal_temporal_operators, model_checking_decidable]
    related: [pnueli_LTL, kamp_tense_logic, prior_tense_logic]
  is_axiom: false
  content_type: FORMAL_SYSTEMS   # LTL is mathematically formalizable
  substrate_load_bearing: false
  serves_capability: [substrate_state_sequence_specification, model_checking_substrate]
  depends_on: [b_series_relational_temporal, axioms]
  signature_hint: linear_temporal_modal_operators

- canonical_name: computation_tree_logic_CTL
  tier: T2
  partition: math_foundation::philosophy_of_time
  science_algebra_category: informal_systems::philosophy_of_time::temporal_logic
  algebra_dict:
    definition: "Clarke + Emerson 1981 CTL; branching-time modal logic; path quantifiers A (all) E (exists) over temporal operators"
    properties: [branching_time_tree, path_quantification, model_checking_decidable_polynomial]
    related: [CTL, CTL_star, mu_calculus, model_checking_textbook]
  is_axiom: false
  content_type: FORMAL_SYSTEMS
  substrate_load_bearing: false
  serves_capability: [substrate_branching_state_specification, model_checking_substrate]
  depends_on: [linear_temporal_logic_LTL]
  signature_hint: branching_time_modal_logic
```

## Cumulative coverage post BATCH 26

- 12 new atoms (6 MOTIVATION primitives + 6 TIME-BASED primitives)
- 2 atoms FORMAL_SYSTEMS (LTL + CTL formalizable as math logic)
- 10 atoms INFORMAL_SYSTEMS (philosophy of action + philosophy of time)
- 0 atoms substrate_load_bearing (substrate KNOWS these concepts; doesn't yet USE them as machinery)
- Per USER architecture extension Axis 3 content-type: 10 informal-system atoms NEW (philosophy informal-system) + 2 formal-system atoms

## Substrate now KNOWS but doesn't USE these atoms

Per Cell #3 + KP P6 HARD-PASS verdict (substrate_load_bearing axis empirically orthogonal): these motivation + time atoms are MATERIALS not TOOLS.

Substrate's operators don't currently USE them — but they're available for:
- substrate-self-knowledge queries about its own motivation + temporal-reasoning
- Recursive self-improvement loop integration (Stage 4 intervention causal_intervention_pearl maps; Stage 6 regression check counterfactual_dependence_lewis maps)
- Future agentic substrate that needs explicit goal/intent representation

## Cumulative LANE C BATCH 17-26

- BATCH 17 + 18 + 19 + 20 + 21 + 22 + 23 + 24 + 25 + 26 = 116 + 10 + 12 = **138 atoms cumulative** (172pct of drill #2 80-atom plan)
- 50+ SHARES_MATH equivalence class seeds across batches
- Content-type axis NOW POPULATED: FORMAL_SYSTEMS (most BATCH 19-25 math) + INFORMAL_SYSTEMS (BATCH 26 philosophy) + RECORDS (history-style atoms) + EPISODIC (chronological)
- 13th methodology rule (3-axis) NOW EMPIRICALLY CONFIRMED orthogonal via Cell #3 + KP P6 HARD-PASS

## Routing

- **Testbed**: BATCH 26 ingest priority T1.15
- **Exp-Dev**: standing for KP P5_v1 + L6-PROOF FINDER depth re-probe post BATCH 17-26 cumulative ingest
- **Research**: standing for verdicts; Cycle 51 close synthesis next per priority queue

## Cross-references

- notes/research_to_testbed_exp_dev_ARCHITECTURE_EXTENSION_FORMAL_vs_INFORMAL_SYSTEMS_*.md (USER philosophy informal-system source)
- notes/research_to_exp_dev_testbed_CELL_3_KP_P6_HARD_PASS_ACK_*.md (3-axis empirically orthogonal predecessor)
- memory `substrate-methodology-rule-12th-universal-operators-field-specific-signal-extractors-first-class-field-partition-routing-H3-HYBRID-first-appearance-2026-06-13` (content-type partition foundation)
- memory `substrate-architecture-3-axis-EMPIRICALLY-ORTHOGONAL-Cell-3-KP-P6-HARD-PASS-USER-craftsman-VERBATIM-corroborated-13th-rule-2nd-appearance-2026-06-13` (Cell #3 + KP P6 HARD-PASS predecessor)

---

**Testbed:** T1+T2 BATCH 26 12 MOTIVATION + TIME substrate primitives philosophy INFORMAL_SYSTEMS content-type per USER architecture extension INGEST-READY intentionality + goal_directedness + practical_reason + agency_higher_order_frankfurt + bratman_planning + a_series_NOW + b_series_relational + diachronic_identity_parfit + causal_intervention_pearl + counterfactual_dependence_lewis + LTL + CTL + 10 INFORMAL_SYSTEMS atoms + 2 FORMAL_SYSTEMS (LTL+CTL) + 0 substrate_load_bearing (atoms substrate KNOWS but doesn't yet USE) + cumulative LANE C 138/80 atoms 172pct of drill recipe + content-type axis populated FORMAL + INFORMAL + RECORDS + EPISODIC + USER full-auto overnight continuing.
