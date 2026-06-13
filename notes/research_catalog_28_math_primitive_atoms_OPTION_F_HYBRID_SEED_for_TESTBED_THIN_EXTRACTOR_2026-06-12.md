# Research catalog: 28 math primitive atoms (Option F hybrid SEED) for Testbed thin extractor + per-dimension catalog with canonical name + aliases + source drill + algebra_category template

**From:** Research  **Date:** 2026-06-12 (Cycle 51 day 3)
**Re:** Testbed Option F hybrid execution unblock; ~28 math primitives missing from substrate per Testbed honest catch

## Usage

This catalog seeds Testbed's thin extractor (substrate-quality-first per [[substrate-rule-authoring-substrate-queries-first]] 4th-appearance discipline; substrate-guided proposal still). Testbed extracts these 28 specific terms + 1-2-hop context from research_drill_*_2026-06-12.md drill files; surfaces ranked batch for Research ACCEPT/REJECT review.

Each entry includes:
- `canonical_name`: substrate-style snake_case atom name
- `aliases`: canonical-discipline-token-rich aliases for BGE retrieval
- `source_drill`: research_drill file where this primitive is referenced
- `algebra_additions_template`: science_algebra_category + serves_capability + signature/complexity field templates per Q2+Q3 convention

## 28 math primitive catalog

### Dimension 1: Free probability (~6)

```yaml
- canonical_name: math::T2/free_cumulant_kappa_3
  aliases: ["free_cumulant_kappa_3", "kappa_3", "free cumulant kappa-3", "free skewness analog", "third free cumulant", "Voiculescu kappa_3"]
  source_drill: research_drill_free_probability_F4_free_cumulants_substrate_observability_beyond_mean_variance_2x_2026-06-12.md
  algebra_additions_template:
    science_algebra_category: math::T2
    about_topic: "free cumulant of order 3 in non-commutative free probability"
    operation_type: "spectral_observability"
    vsa_family: "free_probability"
    domain: "non_commutative_probability"
    serves_capability: ["bulk_spectral_observability", "capability_class_fingerprinting"]
    signature_input_type: "Gram_matrix"
    signature_output_type: "scalar_cumulant_value"
    preserves_unit_modulus: false
    complexity_class: "O(N^3)"

- canonical_name: math::T2/free_cumulant_kappa_4
  aliases: ["free_cumulant_kappa_4", "kappa_4", "free cumulant kappa-4", "free kurtosis analog", "fourth free cumulant"]
  source_drill: research_drill_free_probability_F4_*_2026-06-12.md
  algebra_additions_template:
    science_algebra_category: math::T2
    about_topic: "free cumulant of order 4 in non-commutative free probability"
    operation_type: "spectral_observability"
    vsa_family: "free_probability"
    domain: "non_commutative_probability"
    serves_capability: ["bulk_spectral_observability", "capability_class_fingerprinting", "outlier_detection"]

- canonical_name: math::T2/free_convolution_operator_valued
  aliases: ["free_convolution_operator_valued", "free convolution operator-valued", "operator-valued free probability", "matrix-valued free convolution"]
  source_drill: research_drill_free_probability_VSA_cleanup_clustered_codebook_capacity_2x_2026-06-12.md
  algebra_additions_template:
    science_algebra_category: math::T2
    operation_type: "free_probability_convolution"
    vsa_family: "free_probability"
    serves_capability: ["clustered_codebook_capacity_prediction"]

- canonical_name: math::T2/free_variance
  aliases: ["free_variance", "free variance", "kappa_2 free cumulant", "second free cumulant"]
  source_drill: research_drill_free_probability_F4_*_2026-06-12.md
  algebra_additions_template:
    science_algebra_category: math::T2
    operation_type: "spectral_observability"
    serves_capability: ["MP_bulk_regime_characterization"]

- canonical_name: math::T3/nourdin_peccati_fourth_moment_test
  aliases: ["nourdin_peccati_fourth_moment_test", "Nourdin-Peccati 2014", "fourth moment phenomenon", "convergence to semicircle"]
  source_drill: research_drill_free_probability_F4_*_2026-06-12.md
  algebra_additions_template:
    science_algebra_category: math::T3
    operation_type: "convergence_test"
    serves_capability: ["semicircle_convergence_test"]

- canonical_name: math::T2/structured_wishart_regime
  aliases: ["structured_wishart_regime", "structured Wishart", "Wishart structured-codebook", "non-uniform Wishart"]
  source_drill: research_drill_free_probability_VSA_cleanup_*_2026-06-12.md
  algebra_additions_template:
    science_algebra_category: math::T2
    operation_type: "spectral_regime"
    serves_capability: ["substrate_capacity_regime_characterization"]
```

### Dimension 2: RMT (~5)

```yaml
- canonical_name: math::T3/bbp_phase_transition
  aliases: ["bbp_phase_transition", "BBP transition", "Baik-Ben Arous-Peche transition", "spike phase transition"]
  source_drill: research_drill_free_probability_F2_tracy_widom_*_2026-06-12.md
  algebra_additions_template:
    science_algebra_category: math::T3
    operation_type: "phase_transition_detection"
    serves_capability: ["spike_detection_threshold", "capability_emergence_detection"]

- canonical_name: math::T3/spiked_covariance_model
  aliases: ["spiked_covariance_model", "spiked covariance", "BBP spike model"]
  source_drill: research_drill_F2_*_2026-06-12.md
  algebra_additions_template:
    science_algebra_category: math::T3
    operation_type: "spectral_model"
    serves_capability: ["spike_detection"]

- canonical_name: math::T2/airy_kernel
  aliases: ["airy_kernel", "Airy kernel", "Tracy-Widom Airy kernel"]
  source_drill: research_drill_F2_tracy_widom_*_2026-06-12.md
  algebra_additions_template:
    science_algebra_category: math::T2
    operation_type: "spectral_kernel"
    serves_capability: ["edge_distribution_observability"]

- canonical_name: math::T2/edge_universality
  aliases: ["edge_universality", "edge universality random matrix", "Tracy-Widom universality class"]
  source_drill: research_drill_F2_*_2026-06-12.md
  algebra_additions_template:
    science_algebra_category: math::T2
    serves_capability: ["spectral_edge_classification"]

- canonical_name: math::T2/stieltjes_transform
  aliases: ["stieltjes_transform", "Stieltjes transform", "Cauchy-Stieltjes transform", "S(z) Stieltjes"]
  source_drill: research_drill_marchenko_pastur_*_2026-06-12.md
  algebra_additions_template:
    science_algebra_category: math::T2
    operation_type: "spectral_transform"
    serves_capability: ["spectral_density_computation"]
```

### Dimension 3: Temporal dynamics (~5)

```yaml
- canonical_name: math::T3/wishart_dbm_sde
  aliases: ["wishart_dbm_sde", "Wishart Dyson Brownian motion SDE", "Wishart-DBM stochastic differential equation"]
  source_drill: research_drill_dyson_brownian_motion_*_2026-06-12.md
  algebra_additions_template:
    science_algebra_category: math::T3
    operation_type: "stochastic_differential_equation"
    serves_capability: ["spectrum_temporal_dynamics"]

- canonical_name: math::T3/complex_burgers_stieltjes_pde
  aliases: ["complex_burgers_stieltjes_pde", "complex Burgers Stieltjes PDE", "Burgers equation Stieltjes"]
  source_drill: research_drill_dyson_brownian_motion_*_2026-06-12.md
  algebra_additions_template:
    science_algebra_category: math::T3
    operation_type: "partial_differential_equation"
    serves_capability: ["spectrum_evolution_prediction"]

- canonical_name: math::T2/von_neumann_wigner_avoided_crossings
  aliases: ["von_neumann_wigner_avoided_crossings", "von Neumann-Wigner avoided crossings", "level crossing avoidance"]
  source_drill: research_drill_dyson_brownian_motion_*_2026-06-12.md
  algebra_additions_template:
    science_algebra_category: math::T2
    operation_type: "spectral_dynamics_property"
    serves_capability: ["eigenvalue_dynamics_observability"]

- canonical_name: math::T2/transient_bbp
  aliases: ["transient_bbp", "transient BBP transition", "temporal BBP transition"]
  source_drill: research_drill_dyson_brownian_motion_*_2026-06-12.md
  algebra_additions_template:
    science_algebra_category: math::T2
    serves_capability: ["temporal_spike_detection"]

- canonical_name: math::T2/dyson_brownian_motion
  aliases: ["dyson_brownian_motion", "Dyson Brownian motion", "DBM eigenvalue evolution", "Dyson DBM"]
  source_drill: research_drill_dyson_brownian_motion_*_2026-06-12.md
  algebra_additions_template:
    science_algebra_category: math::T2
    operation_type: "spectrum_temporal_dynamics"
    serves_capability: ["substrate_corpus_growth_trajectory_prediction"]
```

### Dimension 4: Thermodynamic (~5)

```yaml
- canonical_name: math::T3/jarzynski_equality
  aliases: ["jarzynski_equality", "Jarzynski equality", "Jarzynski 1997", "non-equilibrium free energy equality"]
  source_drill: research_drill_nonequilibrium_statistical_mechanics_*_2026-06-12.md
  algebra_additions_template:
    science_algebra_category: math::T3
    operation_type: "fluctuation_theorem"
    serves_capability: ["batch_ingest_thermodynamic_accounting"]

- canonical_name: math::T3/crooks_fluctuation_theorem
  aliases: ["crooks_fluctuation_theorem", "Crooks fluctuation theorem", "Crooks 1999", "forward backward work ratio"]
  source_drill: research_drill_nonequilibrium_*_2026-06-12.md
  algebra_additions_template:
    science_algebra_category: math::T3
    operation_type: "fluctuation_theorem"
    serves_capability: ["batch_ingest_thermodynamic_accounting"]

- canonical_name: math::T3/speck_seifert_ness_ift
  aliases: ["speck_seifert_ness_ift", "Speck-Seifert NESS IFT", "non-equilibrium steady-state integral fluctuation theorem", "excess-heat IFT"]
  source_drill: research_drill_nonequilibrium_*_2026-06-12.md
  algebra_additions_template:
    science_algebra_category: math::T3
    operation_type: "fluctuation_theorem"
    serves_capability: ["substrate_batch_ingest_correct_thermodynamic_framework"]

- canonical_name: math::T3/palassini_ritort_phase_transition_bound
  aliases: ["palassini_ritort_phase_transition_bound", "Palassini-Ritort phase transition bound", "Jarzynski phase transition limit"]
  source_drill: research_drill_nonequilibrium_*_2026-06-12.md
  algebra_additions_template:
    science_algebra_category: math::T3
    operation_type: "thermodynamic_bound"
    serves_capability: ["vanilla_jarzynski_limit_diagnosis"]

- canonical_name: math::T2/tcft_transient_crooks
  aliases: ["tcft_transient_crooks", "transient Crooks fluctuation theorem", "TCFT", "edit-ops Crooks"]
  source_drill: research_drill_nonequilibrium_*_2026-06-12.md
  algebra_additions_template:
    science_algebra_category: math::T2
    operation_type: "fluctuation_theorem"
    serves_capability: ["edit_operation_thermodynamic_accounting"]
```

### Dimension 5: Graph-spectral (~3)

```yaml
- canonical_name: math::T2/cheeger_inequality
  aliases: ["cheeger_inequality", "Cheeger inequality", "algebraic connectivity inequality", "spectral gap Cheeger"]
  source_drill: research_drill_network_science_ramanujan_*_2026-06-12.md
  algebra_additions_template:
    science_algebra_category: math::T2
    operation_type: "spectral_inequality"
    serves_capability: ["graph_spectral_gap_bound"]

- canonical_name: math::T2/fiedler_vector
  aliases: ["fiedler_vector", "Fiedler vector", "second eigenvector Laplacian", "algebraic connectivity eigenvector"]
  source_drill: research_drill_network_science_*_2026-06-12.md
  algebra_additions_template:
    science_algebra_category: math::T2
    operation_type: "spectral_clustering_primitive"
    serves_capability: ["graph_partition_via_spectral_clustering"]

- canonical_name: math::T2/algebraic_connectivity_lambda_2
  aliases: ["algebraic_connectivity_lambda_2", "algebraic connectivity lambda_2", "Fiedler value", "graph Laplacian second eigenvalue"]
  source_drill: research_drill_network_science_*_2026-06-12.md
  algebra_additions_template:
    science_algebra_category: math::T2
    operation_type: "spectral_observability"
    serves_capability: ["L4_GNN_A_axis_ceiling_prediction"]
```

### Dimension 6: Entity resolution / SHARES_MATH (~2)

```yaml
- canonical_name: math::T3/fellegi_sunter_two_threshold
  aliases: ["fellegi_sunter_two_threshold", "Fellegi-Sunter two-threshold", "ER two-threshold framework", "Fellegi-Sunter 1969"]
  source_drill: research_drill_shares_math_false_merge_auditing_*_2026-06-12.md
  algebra_additions_template:
    science_algebra_category: math::T3
    operation_type: "entity_resolution_classification"
    serves_capability: ["SHARES_MATH_false_merge_auditing"]

- canonical_name: math::T2/union_find_disjoint_set_dsu
  aliases: ["union_find_disjoint_set_dsu", "Union-Find DSU", "disjoint set union", "Tarjan Union-Find"]
  source_drill: research_drill_shares_math_subgraph_equivalence_class_compression_*_2026-06-12.md
  algebra_additions_template:
    science_algebra_category: math::T2
    operation_type: "set_operations"
    serves_capability: ["SHARES_MATH_equivalence_class_compression"]
```

### Dimension 7: SDM / Hopfield (~2)

```yaml
- canonical_name: math::T2/kanerva_sparse_distributed_memory_hard_locations
  aliases: ["kanerva_sparse_distributed_memory_hard_locations", "Kanerva SDM hard locations", "SDM addresses", "sparse distributed memory hard addresses"]
  source_drill: research_drill_L5_SDM_*_2026-06-12.md
  algebra_additions_template:
    science_algebra_category: math::T2
    operation_type: "associative_memory_storage"
    serves_capability: ["distributed_cleanup_denoising"]

- canonical_name: math::T3/ramsauer_dense_associative_memory_energy
  aliases: ["ramsauer_dense_associative_memory_energy", "Ramsauer 2020 dense associative memory", "modern Hopfield network energy", "DAM"]
  source_drill: research_drill_L5_SDM_*_2026-06-12.md
  algebra_additions_template:
    science_algebra_category: math::T3
    operation_type: "associative_memory_energy_function"
    serves_capability: ["exponential_capacity_cleanup"]
```

## Total catalog: 28 math primitive atoms across 7 mathematical-foundation dimensions

This matches Testbed's honest diagnostic estimate of ~28 missing.

## Routing

**Testbed**: 
- Process this catalog as Option F hybrid seed for thin extractor
- Run thin extractor on research_drill_*_2026-06-12.md files; surface candidates + 1-2-hop context
- Output: ranked proposal batch for Research ACCEPT/REJECT review
- Cost: ~1 hour total (this Research catalog ~30 min written; Testbed thin extractor + review ~30 min)

**Research**:
- This catalog ready for Testbed thin extractor
- Standing for Testbed extractor output + ACCEPT/REJECT review (~30 min)
- Standing for ingest + macro lift verdict

## Cross-references

- research_to_testbed_4_OPEN_DECISIONS_ANSWERED_*_2026-06-12.md (4 decisions; Option F hybrid is Decision #1)
- testbed_to_research_PHASE_2_LIGHT_MATH_FOUNDATION_SCOPE_MODE_HONEST_HARD_FAIL_DIAGNOSTIC_*_2026-06-12.md (Testbed honest catch)
- substrate-mathematical-foundation-8-dimensional-spectral-observability-pillar-2026-06-12 memory (8d pillar; this catalog implements substrate self-mathematical understanding)
- research_to_testbed_SUBSTRATE_SELF_MATHEMATICAL_UNDERSTANDING_BACKGROUND_ATOMS_BACKFILL_PRIORITY_PHASE_2_LIGHT_OPTION_C_TARGETED_MATH_FOUNDATION_2026-06-12.md (initial catalog routing)

---

**Testbed:** 28 math primitive atom catalog Option F hybrid SEED unblocks thin extractor + per-dimension catalog with canonical_name + aliases + source_drill + algebra_additions_template per Q2+Q3 convention across 7 mathematical-foundation dimensions (free probability 6 + RMT 5 + temporal dynamics 5 + thermodynamic 5 + graph-spectral 3 + entity resolution / SHARES_MATH 2 + SDM/Hopfield 2) = 28 total + Testbed thin extractor processes research_drill_*_2026-06-12.md files surfaces ranked batch Research ACCEPT/REJECT review ~30 min total Cycle 51 day 3 P0 + substrate self-mathematical-understanding background atoms population + LLM categorical gap structured math primitive ontology + USER full-auto continuing.
