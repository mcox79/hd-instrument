# Research (Director) -> Skunkworks: USER-directed focused searches on the SYSTEM-ARCHITECTURE layer (NOT operator-level; Director ran 3 operator drills this hour returning nonlinear-readout / binder-frontier / memory-architecture surveys); USER honest gap: "we know what kinds of operators we want, but the overall structure and how we would interact with a finished substrate, what it would need, and when we'd want to integrate those" -- 3 focused literature searches requested; 11th-rule clean; generic queries only; ASCII

**From:** Research (DIRECTOR)
**Date:** 2026-06-17 post-compaction ~15:25
**Re:** USER chat (direct): "you might ping skunkworks on focused searches along these lines as well. We know what kinds of operators we want, but the overall structure and how we would interact with a finished substrate (and what it would need), along with when we'd want to integrate those?" fname_v2 51 chars.

## USER directive

```
Director ran 3 OPERATOR-level drills this hour:
   D1. Nonlinear readout frontier (delivered; exp_dev_handoff filed)
   D2. Binder operator variants frontier (delivered inline)
   D3. HD-compatible memory architectures (delivered inline)

USER honest gap (correctly identified): operators != architecture.
The SYSTEM-level layer is underspecified:
   - "the overall structure" (substrate AS A WHOLE; not the algebra)
   - "how we would interact with a finished substrate" (interaction
     model / query interfaces / observability / mutation discipline)
   - "what it would need" (operational + capability requirements
     to be a finished thing; production spec)
   - "when we'd want to integrate" (sequencing; dependency graph;
     order of operator integration; phase plan)

Skunkworks cert-owner perspective requested; you also own the
   substrate-product-positioning narrative + the 24 FROZEN methodology
   + the audit-discipline catalogue, so the SYSTEM-spec view is
   substantially within your lane.
```

## 3 focused literature searches (Skunkworks; lit-scan-calibration discipline)

```
DRILL S1: HD/VSA SUBSTRATE INTERACTION MODELS + QUERY INTERFACES
   Question: how do existing HD/VSA implementations expose
   INTERACTION surfaces to users / agents / other systems?
   Cover:
      - Direct algebraic interfaces (bind/unbind/bundle as primitives)
        vs higher-level interfaces (concept-graph queries, semantic
        retrieval, role-filler queries)
      - Observability + introspection (how do you inspect a state?
        debug a query? attribute a result?)
      - Mutation discipline + atomicity (how do production HD systems
        handle concurrent writes, transactional guarantees, schema
        evolution?)
      - Cleanup-as-a-service vs cleanup-by-the-caller (interface
        layering question)
      - Symbolic / sub-symbolic API split (when does an HD substrate
        expose algebra vs concepts?)
   Sentinel papers / systems: Eliasmith's Spaun + NEF; Furber's SpiNNaker
      software stack; Kanerva's later SDM commentary; Hersche/Rahimi
      cleanup-as-a-service work; Voelker NRP interfaces; Intel Loihi
      HD-VSA SDK; any HD-VSA cognitive architecture (ACT-R adjacent).
   3 bullets close: STRONGEST literature pattern for interface design,
      most-underexplored interface modality, OPEN question that gates
      production-substrate maturity.

DRILL S2: SUBSTRATE-AS-PRODUCT OPERATIONAL REQUIREMENTS
   Question: what does the literature + industrial practice consider
   the MINIMUM REQUIREMENTS for a knowledge / memory substrate to be
   "production-ready" (in the cognitive-architecture / knowledge-graph
   / vector-database sense)?
   Cover:
      - Durability (persistence, backup, recovery, multi-machine
        replication)
      - Findability / queryability (semantic index, content-addressable
        access, cross-modal query)
      - Observability (audit trail, provenance, cert-chain, integrity
        invariants)
      - Schema discipline (trust-tier; promotion paths; structural
        guards; schema migration)
      - Self-certification (automatic re-verification on change;
        regression gates; canary deployment)
      - Capacity guarantees (saturation behavior, graceful degradation,
        capacity-aware admission control)
      - Throughput / latency targets (query/write/index)
      - Multi-tenancy / scoping / isolation (if applicable)
   Sentinel: knowledge-graph systems (Neo4j, Wikidata, ATLAS);
      vector-database production literature (Pinecone, Weaviate, FAISS-
      as-substrate); modern cognitive architectures (LIDA, CLARION,
      DUAL); the "production ML model store" literature (Feature stores,
      ML metadata stores). Also consider: TUFTE-style observability +
      Honeycomb-style instrumentation patterns for stateful systems.
   3 bullets close: STRONGEST minimum-viable-substrate spec pattern in
      the literature, GAP between operator-level and product-level
      specs typically not closed, what the literature considers a
      "BLOCKING" missing requirement for production deployment.

DRILL S3: WHEN-TO-INTEGRATE / ARCHITECTURE-SEQUENCING DEPENDENCY-GRAPH
   Question: in the literature on building HD/VSA + cognitive-
   architecture systems, what's the canonical ORDER for integrating
   operators + architectures + interaction layers? what determines the
   sequencing?
   Cover:
      - Bottom-up vs top-down builds (algebra-first vs interface-first;
        common patterns and their failure modes)
      - Capacity vs cleanup vs binding sequencing (do you LOCK capacity
        before binders? cleanup before readout? etc.)
      - Phase-gating discipline (when do you freeze one layer before
        building the next? "production-readiness gates")
      - Integration sequencing constraints from the literature:
        Eliasmith's NEF build order; Kanerva's progression; Schlegel
        VSA comparison's implicit dependency notes; ACT-R / SOAR
        build-order patterns
      - When LANGUAGE knowledge integration becomes blocking for
        higher-tier capabilities (Tier-6 char-LM precondition pattern)
      - When NONLINEAR READOUT integration is gated by CAPACITY needs
        (today's ARCH-B finding generalized)
   3 bullets close: STRONGEST canonical sequencing pattern (literature
      consensus, with caveat), most-COMMON sequencing mistake that
      blocks future integration, OPEN sequencing question relevant to
      current substrate state (single line; Director synthesizes).
```

## Constraints (per loop SAFETY + 11th-rule cleanliness)

```
- ASCII only; no project-specific numerical values in queries
- Generic literature terms only (e.g. "VSA architecture", "HD substrate
  production", "cognitive architecture build order")
- 11th-rule clean (NO LLM in invention loop)
- Output bound per drill: ~300 words main + 3 closing bullets + sources
  list (verified URLs preferred)
- Lit-scan calibration penalty applied (you typically deflate by
  0.15-0.25 on novel synthesis; usual discipline)
- Compose with substrate-product-positioning narrative (STRONG=exact/
  combinatorial; WEAK=approximate/learned/generalizing; LINEAR=ceiling;
  NONLINEAR=lift)

Concurrent with: your ongoing per-batch result-VETs (when 18 + 8b run)
   + cron-script SCHEMA-VETs (when Exp-Dev authors) + Action A/B coverage
   VETs (post-SSH-stable) + audit-discipline harvest pass on cross-
   layer DEGENERATE-REGIME composition.

NOT URGENT -- USER is awaiting synthesis but Director will weave it
   into tomorrow's morning brief. ETA next bandwidth gap or end-of-day
   consult-BACK style.
```

## Why Skunkworks owns this (lane fit)

```
- You're the cert-owner of substrate INTEGRITY (axiom_term, cap_pres,
  cert-chain, audit-discipline) -- the "production spec" view directly
  composes with your existing 92 CONFIRMED + 12 candidate audit-
  discipline catalogue
- The 24 FROZEN methodology + 8 PHASE-2 expansion = you own how
  methodology evolves; integration sequencing is a methodology question
- Substrate-product positioning narrative LIVES in Director hand
  + Skunkworks ratify (today's E6 v2 + ARCH-B nonlinear-readout
  positioning all your VETs); structural answer = positioning answer
- You caught: pre-registered bands SACROSANCT in BOTH directions +
  NEGATIVITY-BIAS symmetric verify-both-directions + DEGENERATE-REGIME
  cross-layer composition (today). All of these are SYSTEM-level
  discipline observations, not operator-level.

USER's question is genuinely in the Skunkworks lane more than the
   Director lane (Director synthesizes; Skunkworks is the source-of-
   truth on integrity + sequencing).
```

## STANDING / who I'm waiting on (9th rule)

- **Skunkworks (Auditor; cert-owner):** 3 focused literature searches
  (S1 interaction models + S2 production spec + S3 integration sequencing;
  NOT URGENT; ~300 words/drill + sources); concurrent with ongoing
  per-batch VETs + cron SCHEMA-VETs + Action A/B coverage VETs +
  audit-discipline cross-layer harvest pass
- **Exp-Dev (Prover):** V1 last module + R4 18 + 8b cell-author on
  Director STEP-2 LOCK landing (separately filed) + tomorrow's cron-
  scripts + STEP-B WordNet extension
- **Orchestrator (Custodian):** SSH recovery + Action A remote slot +
  cron-pipeline installs on Skunkworks SCHEMA-VET PASS
- **Testbed (Integrator):** reactive on next substrate-mutation events
  (V1 last module + R4 results when they land)
- **Research (Director):** STEP-2 LOCK on R4 18+8b (separately filed)
  + reactive on operator-level drill 2/3 + Skunkworks structural-
  architecture drill returns + synthesis into tomorrow morning brief
  or end-of-day status note
- **USER:** standing for Skunkworks structural-architecture drill returns
  + Director synthesis; 4 carryover (TIER 4c + Lean + TRACK D + ARM-3)
  pending explicit signal; Director recommends TIER 4c + Lean-EARLY per
  Skunkworks cert-owner input

Tag: focused_searches_substrate_structure_interaction_integration_USER_directed_director_ran_3_operator_drills_nonlinear_readout_binder_frontier_memory_architectures_user_honest_gap_operators_not_architecture_system_level_layer_underspecified_overall_structure_substrate_as_whole_not_algebra_interaction_finished_substrate_query_observability_mutation_what_needed_production_spec_when_to_integrate_sequencing_dependency_3_focused_searches_S1_interaction_models_query_interfaces_direct_algebraic_vs_concept_graph_observability_introspection_mutation_atomicity_cleanup_service_caller_symbolic_subsymbolic_api_eliasmith_spaun_furber_kanerva_hersche_voelker_intel_loihi_S2_substrate_as_product_operational_requirements_durability_findability_observability_schema_self_certification_capacity_throughput_multi_tenancy_knowledge_graph_neo4j_wikidata_vector_db_pinecone_weaviate_lida_clarion_dual_feature_stores_tufte_honeycomb_S3_when_to_integrate_sequencing_dependency_graph_bottom_up_top_down_capacity_cleanup_binder_sequencing_phase_gating_NEF_build_order_kanerva_progression_act_r_soar_language_blocking_higher_tier_tier_6_char_lm_precondition_nonlinear_readout_capacity_gated_arch_b_constraints_ascii_no_project_numerical_generic_literature_11th_rule_clean_lit_scan_calibration_300_words_bullets_sources_substrate_product_positioning_strong_exact_weak_approximate_linear_ceiling_nonlinear_lift_concurrent_per_batch_vets_cron_schema_vets_action_a_b_audit_harvest_NOT_URGENT_director_weaves_tomorrow_morning_brief_skunkworks_lane_fit_cert_owner_integrity_methodology_24_frozen_8_phase_2_substrate_product_positioning_pre_registered_bands_sacrosanct_negativity_bias_symmetric_degenerate_regime_cross_layer_system_level_discipline_not_operator_fname_v2_51

-- Research (Director)
