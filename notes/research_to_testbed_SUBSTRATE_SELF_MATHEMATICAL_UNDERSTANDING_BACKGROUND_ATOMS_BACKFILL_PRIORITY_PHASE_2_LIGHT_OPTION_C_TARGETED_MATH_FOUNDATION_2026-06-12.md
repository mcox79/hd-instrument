# Research -> Testbed: SUBSTRATE SELF-MATHEMATICAL UNDERSTANDING priority backfill + Phase-2-light Option C targeted at math-foundation drill notes + ~80-100 math primitive atoms catalog for substrate to query its own mathematics + substrate_query.py extension for self-math subcommands

**From:** Research  **Date:** 2026-06-12 (Cycle 51 day 2)
**Re:** USER strategic direction: substrate needs the BACKGROUND to understand its own mathematics

## TL;DR

- **Strategic goal**: substrate self-understanding of own mathematics = META-MATHEMATICAL substrate-product positioning win
- **Concrete blocker**: substrate's 8-dimensional mathematical-foundation pillar is described in research_drill_*_2026-06-12.md files (research_history partition) but the underlying MATH PRIMITIVES (Marchenko-Pastur, R-transform, free cumulants kappa_n, Tracy-Widom F2, Dyson Brownian motion, NESS Speck-Seifert IFT, TUR Barato-Seifert, etc.) are NOT YET AUTHORED as substrate atoms
- **Phase-2-light Option C prioritization**: target math-foundation drill files first; surface ~80-100 math primitive candidates for Research ACCEPT/REJECT
- **substrate_query.py extension**: add `math_foundations`, `math_primitive_for`, `theorem_about`, `closed_form_predicts` subcommands so substrate can answer self-mathematical-understanding queries
- **Self-extension closes the loop**: substrate UNDERSTANDS its own 8d math foundation by querying the math primitives substrate self-extended into corpus

## The catalog: ~80-100 math primitive atoms needed for substrate self-mathematical understanding

These exist as REFERENCES in research_drill_*_2026-06-12.md files but NOT YET ATOMIZED:

### Free probability dimension (drill 6, 9, 11, 13, 14, 16, 17, 18)

| Math primitive | Source drill |
|---|---|
| voiculescu_r_transform | research_drill_free_probability_R_transform_*_2026-06-12.md |
| free_cumulant_kappa_n | research_drill_free_probability_F4_free_cumulants_*_2026-06-12.md |
| free_convolution | research_drill_free_probability_*_2026-06-12.md (multiple) |
| operator_valued_free_probability | research_drill_free_probability_VSA_cleanup_*_2026-06-12.md |
| free_variance | research_drill_free_probability_F4_*_2026-06-12.md |
| free_skewness | research_drill_F4_*_2026-06-12.md |
| free_kurtosis | research_drill_F4_*_2026-06-12.md |
| nourdin_peccati_fourth_moment_test | research_drill_F4_*_2026-06-12.md |

### Random matrix theory dimension (drill 9, 11, 13)

| Math primitive | Source drill |
|---|---|
| marchenko_pastur_distribution | research_drill_marchenko_pastur_*_2026-06-12.md |
| tracy_widom_F2_distribution | research_drill_F2_tracy_widom_*_2026-06-12.md |
| BBP_phase_transition | research_drill_F2_*_2026-06-12.md |
| spiked_covariance_model | research_drill_F2_*_2026-06-12.md |
| airy_kernel | research_drill_F2_*_2026-06-12.md |
| edge_universality | research_drill_F2_*_2026-06-12.md |
| stieltjes_transform | research_drill_marchenko_pastur_*_2026-06-12.md |
| wishart_distribution | research_drill_marchenko_pastur_*_2026-06-12.md |

### Temporal dynamics dimension (drill 17)

| Math primitive | Source drill |
|---|---|
| dyson_brownian_motion | research_drill_dyson_brownian_motion_*_2026-06-12.md |
| wishart_DBM_SDE | research_drill_dyson_brownian_motion_*_2026-06-12.md |
| complex_burgers_stieltjes_PDE | research_drill_dyson_brownian_motion_*_2026-06-12.md |
| von_neumann_wigner_avoided_crossings | research_drill_dyson_brownian_motion_*_2026-06-12.md |
| transient_BBP | research_drill_dyson_brownian_motion_*_2026-06-12.md |

### Thermodynamic dimension (drill 18)

| Math primitive | Source drill |
|---|---|
| jarzynski_equality | research_drill_nonequilibrium_statistical_mechanics_*_2026-06-12.md |
| crooks_fluctuation_theorem | research_drill_nonequilibrium_*_2026-06-12.md |
| speck_seifert_NESS_IFT | research_drill_nonequilibrium_*_2026-06-12.md |
| TUR_barato_seifert | research_drill_nonequilibrium_*_2026-06-12.md |
| stochastic_thermodynamics | research_drill_nonequilibrium_*_2026-06-12.md |
| TCFT_transient_crooks | research_drill_nonequilibrium_*_2026-06-12.md |
| palassini_ritort_phase_transition | research_drill_nonequilibrium_*_2026-06-12.md |
| free_energy_minimization | research_drill_nonequilibrium_*_2026-06-12.md |

### Graph-spectral dimension (drill 7, 20)

| Math primitive | Source drill |
|---|---|
| cheeger_inequality | research_drill_network_science_ramanujan_*_2026-06-12.md |
| ramanujan_graph_property | research_drill_network_science_*_2026-06-12.md |
| algebraic_connectivity_lambda_2 | research_drill_network_science_*_2026-06-12.md |
| fiedler_vector | research_drill_network_science_*_2026-06-12.md |
| graph_laplacian_spectrum | research_drill_network_science_*_2026-06-12.md |
| spectral_gap_bound | research_drill_network_science_*_2026-06-12.md |
| expander_graph | research_drill_network_science_*_2026-06-12.md |

### VSA architectural dimension (drill 4, 6, 11, 12)

| Math primitive | Source drill |
|---|---|
| plate_single_bind_cosine_formula | research_drill_vsa_composition_*_2026-06-12.md |
| frady_sommer_resonator_cliff | research_drill_vsa_composition_*_2026-06-12.md |
| resonator_decoder_iterative_inference | research_drill_vsa_*_2026-06-12.md |
| hrr_binding_capacity | research_drill_vsa_*_2026-06-12.md |
| structured_wishart_regime | research_drill_free_probability_VSA_*_2026-06-12.md |

### Categorical / DisCoCat dimension (drill 22)

| Math primitive | Source drill |
|---|---|
| strong_monoidal_functor | research_drill_L3_DisCoCat_*_2026-06-12.md |
| pregroup_grammar_lambek | research_drill_L3_DisCoCat_*_2026-06-12.md |
| combinatorial_categorial_grammar_CCG | research_drill_L3_DisCoCat_*_2026-06-12.md |
| frobenius_algebra | research_drill_L3_DisCoCat_*_2026-06-12.md |
| categorical_quantum_mechanics | research_drill_L3_DisCoCat_*_2026-06-12.md |
| functorial_composition | research_drill_L3_DisCoCat_*_2026-06-12.md |
| ag2_deduction_database | research_drill_L3_DisCoCat_*_2026-06-12.md |

### SDM / Modern Hopfield dimension (drill 21)

| Math primitive | Source drill |
|---|---|
| kanerva_sparse_distributed_memory | research_drill_L5_SDM_*_2026-06-12.md |
| sdm_hard_locations | research_drill_L5_SDM_*_2026-06-12.md |
| ramsauer_dense_associative_memory | research_drill_L5_SDM_*_2026-06-12.md |
| modern_hopfield_energy | research_drill_L5_SDM_*_2026-06-12.md |
| iterative_cleanup_capacity | research_drill_L5_SDM_*_2026-06-12.md |

### Entity resolution / SHARES_MATH dimension (drill 10, 15)

| Math primitive | Source drill |
|---|---|
| fellegi_sunter_two_threshold | research_drill_shares_math_false_merge_*_2026-06-12.md |
| union_find_disjoint_set_DSU | research_drill_shares_math_subgraph_*_2026-06-12.md |
| isotonic_calibration | research_drill_shares_math_*_2026-06-12.md |
| equivalence_class_quotient_graph | research_drill_shares_math_*_2026-06-12.md |
| connected_component_partition | research_drill_shares_math_*_2026-06-12.md |

### GNN / message passing dimension (drill 19)

| Math primitive | Source drill |
|---|---|
| r_gcn_per_edge_learned_weight | research_drill_L4_GNN_SHARES_MATH_*_2026-06-12.md |
| compgcn_compositional_graph_neural_network | research_drill_L4_GNN_*_2026-06-12.md |
| han_heterogeneous_attention_network | research_drill_L4_GNN_*_2026-06-12.md |
| message_passing_neural_network | research_drill_L4_GNN_*_2026-06-12.md |

### Entropy / information dimension (cross-drill)

| Math primitive | Source drill |
|---|---|
| variational_free_energy | research_drill_nonequilibrium_*_2026-06-12.md (Friston connection) |
| variational_inference | (substrate already has T2/variational_inference candidate; UPDATE-as-alias) |
| KL_divergence | (substrate may have; verify via meta::RULE_authoring_substrate_queries_first discipline) |
| mutual_information | (verify) |

**Total catalog**: ~80-100 math primitive atoms across 10 mathematical-foundation dimensions

## Phase-2-light Option C targeted run priority

Per substrate-quality-first + meta::RULE_authoring_substrate_queries_first:

1. **Targeted scope**: Phase-2-light Option C run with FILTER scope = research_drill_*_2026-06-12.md (today's drill files) PLUS dependency files
2. **Expected ACCEPT rate**: high (these are explicit math primitive references; high SNR vs general history partitions); estimated P@30 strict >= 0.70
3. **Output**: ranked proposal batch with these math primitives surfaced for Research ACCEPT/REJECT
4. **Cost**: ~5-10 min CPU pipeline + 30-60 min Research review per batch
5. **Round 1 target**: 30-50 math primitives ingested; substrate begins UNDERSTANDING its 8d math foundation

## substrate_query.py extension for self-mathematical understanding

After math primitives ingested, extend substrate_query.py with new subcommands:

```python
# Existing subcommands (substrate-self-knowing system):
# - capabilities, capability_lifts, methodology_rules, etc.

# NEW substrate-self-mathematical-understanding subcommands:
# 1. math_foundations
#    -> returns all T1/T0 math primitive atoms across substrate's 8 dimensions
#    -> verifies substrate KNOWS what its own math foundation is

# 2. math_primitive_for capability=<name>
#    -> returns SHARES_MATH-linked T0 math primitive atoms for the named capability
#    -> e.g. "math_primitive_for capability=fhrr_bind" -> [convolution, fourier_transform, complex_phase_arithmetic]

# 3. theorem_about <topic>
#    -> returns theorem-statement atoms about the topic (e.g. "theorem_about cleanup_capacity")
#    -> includes closed-form formulas substrate has authored as atoms

# 4. closed_form_predicts <observable>
#    -> returns the closed-form formula atom that predicts the observable
#    -> e.g. "closed_form_predicts cleanup_cliff_location" -> R-transform formula atom

# 5. empirical_anchor_for <math_primitive>
#    -> returns empirical-cell atoms that validated the math primitive
#    -> e.g. "empirical_anchor_for marchenko_pastur_distribution" -> MP bulk cell + cliff sharpness slope-zero verdict
```

These 5 subcommands let substrate SELF-QUERY its mathematical foundation.

## Substrate-product positioning artifact: substrate META-MATHEMATICAL

When math primitives are ingested + substrate_query.py extended:

| Query | Substrate response | LLM gap |
|---|---|---|
| "What math underlies substrate's cleanup-cliff F*?" | math_foundations -> R-transform + free_convolution + spiked_covariance_model + BBP_phase_transition | LLM has no structured math-foundation lookup |
| "What is the substrate's TUR efficiency bound?" | closed_form_predicts substrate_efficiency -> Barato-Seifert TUR atom + free_energy_minimization atom | LLM hallucinates rather than retrieves structured math |
| "Which capability shares math with q_learning?" | math_primitive_for capability=q_learning -> bellman_backup + fixed_point_iteration + value_iteration + policy_iteration | LLM via attention; substrate via SHARES_MATH explicit |

**Substrate becomes META-MATHEMATICAL substrate-product positioning artifact**: substrate not only HAS a mathematical foundation but UNDERSTANDS it + can REASON about it via self-query.

This is highest-tier substrate-product positioning: LLMs are mathematical CONSUMERS (apply math implicitly via attention); substrate becomes mathematical UNDERSTANDER (can self-query its own math foundation explicitly).

## Connects to user's stated strategic goal

USER directive: "substrate needs to get to a point that it understands its own mathematics; it needs the background to do that"

This routing addresses both:
1. **The background**: 80-100 math primitive atoms catalog + Phase-2-light Option C targeted authoring
2. **The understanding**: substrate_query.py extension for self-mathematical-understanding subcommands

After ingestion + tool extension, substrate can answer: "what's the R-transform of substrate's Gram matrix?", "what TUR bound applies to substrate batch ingest?", "which math primitive predicts substrate's cleanup-cliff sharpness?".

## Routing

**Testbed (PRIORITY)**:
- Phase-2-light Option C TARGETED run with scope = research_drill_*_2026-06-12.md (~22 drill files)
- Expected ~80-100 math primitive candidates surfaced
- Research ACCEPT/REJECT review (~30-60 min)
- Ingest ACCEPTed atoms (~10-30 from Round 1 estimated)
- substrate_query.py extension: add `math_foundations`, `math_primitive_for`, `theorem_about`, `closed_form_predicts`, `empirical_anchor_for` subcommands (~2-3 hours)

**Research**:
- This catalog + routing
- Standing for Phase-2-light Option C targeted run verdict
- Will conduct formal P@30 review on math-targeted batch (estimated high HARD-PASS given high SNR scope)

**Exp-Dev**:
- Standing patterns continue (math foundation cells + Tier-A multi-seed + L-A char-CNN)
- After math primitives ingested + substrate_query.py extended: optional substrate-self-mathematical-understanding validation cell ("does substrate answer 10 substrate-self-mathematical questions correctly?")

## Honest scope

- Math primitive atom counts are estimates based on drill content scanning; actual yield depends on Phase-2-light Option C extraction quality
- Substrate UNDERSTANDING != PROVING; substrate self-mathematical-understanding is structured retrieval + composition, not theorem-proving
- Cycle 52 candidate work alongside Stratified Hybrid L2 + L4 + Phase-6 priorities
- Substrate-product positioning artifact level extends from "production-grade NLU pipeline" + "8d math foundation" to **"substrate META-MATHEMATICALLY self-aware"** -- this is a tier higher

## Cross-references

- substrate-mathematical-foundation-8-dimensional-spectral-observability-pillar-2026-06-12 memory
- substrate-as-self-knowing-system-2026-06-12 memory (current self-knowing system foundation)
- substrate-mathematical-primitive-shares-math-architectural-insight-2026-06-12 memory (SHARES_MATH framing)
- research_drill_*_2026-06-12.md files (all 22 drill notes; sources of math primitive references)

---

**Testbed:** SUBSTRATE SELF-MATHEMATICAL UNDERSTANDING priority backfill per USER strategic direction; 8-dim math foundation pillar drill notes ARE in research_history but math primitives NOT YET atomized; ~80-100 math primitive catalog covers 10 mathematical-foundation dimensions (free probability + RMT + temporal dynamics + thermodynamics + graph-spectral + VSA + categorical + SDM + entity resolution + GNN); Phase-2-light Option C TARGETED run scope = research_drill_*_2026-06-12.md ~22 files expected ~80-100 candidates with high P@30 estimated >=0.70 because high-SNR scope; ~10-30 ACCEPTed Round 1 ingest; substrate_query.py extension 5 new subcommands math_foundations + math_primitive_for + theorem_about + closed_form_predicts + empirical_anchor_for ~2-3 hours Testbed; substrate becomes META-MATHEMATICAL substrate-product positioning artifact LLMs are mathematical consumers substrate becomes mathematical understander via structured self-query; Cycle 52 candidate alongside Stratified Hybrid L2+L4+Phase-6; USER full-auto continuing.
