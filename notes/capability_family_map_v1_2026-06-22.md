# Capability family map v1 — DIRECTOR-SIDE METADATA CLUSTERING (2026-06-22)

> ⚠️  **THIS IS NOT SUBSTRATE SELF-IMPROVEMENT.** USER 2026-06-22 corrected the misframing.
> This is Director-side lexical pattern-matching on atom_id strings using a keyword lexicon I (Director) defined.
> The substrate's own primitives (KGStore, SequenceMatrix, SubstrateGenerator, multi_hop, etc.) are NOT used.
> Output below is Director scaffolding for cert-trail navigation, NOT substrate-derived knowledge.
>
> For actual substrate self-mapping, see `exp_substrate_self_map_v2_*` (cell-author pending) which encodes
> atoms via substrate primitives + uses substrate's own multi_hop traversal on cert_ledger relations.

**DO NOT use v1 findings to drive substrate-development decisions until v2 lands** (USER directive).

**Source:** `data/substrate_index/meta/cert_ledger.jsonl` — chain-grade atoms only (latest-per-atom; supersedes-folded)
**Total chain-grade atoms analyzed:** 447
**Lexical categories identified:** 12
**Cross-category atoms (multi-lexical-match):** 18

## Capability families (sorted by size)

| Family | Atoms | Verdict mix | Tier mix | Top exemplars |
|---|---:|---|---|---|
| **composition** | 267 | PASS=266, HARD=1 | T3=267 | EXP_substrate_compositional_generalization_K10_to_K20_v1_n40; EXP_substrate_novel_assembly_2_tier2_novel_composition_equiv; EXP_q_a3_l10000_cross_layer_composition_v1_n16384 |
| **uncategorized** | 110 | PASS=107, HARD=3 | T3=110 | EXP_active_inference_dpefe_h2_cpu_v1; EXP_crt_module_scaling_battery_v1; EXP_csp_hebbian_coexist_v1 |
| **capacity** | 31 | PASS=29, HARD=2 | T3=31 | EXP_substrate_capacity_composition_b2xb4_v1_n2048; EXP_substrate_decomposition_resonator_alpha05_cpu_v1; EXP_tier4_multiseed_sweep_cpu_v1 |
| **topology** | 22 | PASS=22 | T3=22 | EXP_pp48_nkt_cross_n_depth13_v1_n8192; EXP_pp48_nkt_cross_n_depth17_v1_n8192; EXP_pp48_nkt_cross_n_depth19_v1_n16384 |
| **whitening** | 5 | PASS=5 | T3=5 | EXP_substrate_audit_core_C2_C3_whitened_pythia160m_v2_n4096; EXP_substrate_audit_core_C2_C3_whitened_llama1b_v1_n4096; EXP_substrate_dim_expansion_subsumes_whitening_n_enc_10000_v |
| **kg_ingest** | 5 | HARD=3, PASS=2 | T3=5 | EXP_ccc1_extra_fb15k237_kg_multihop_v1; EXP_substrate_multimodal_binding_text_kg_v1; EXP_u1_fb15k237_ingest_eval_v1 |
| **encoding** | 2 | PASS=1, HARD=1 | T3=2 | EXP_substrate_real_encoder_capabilities_v1; EXP_pythia_kv_desat_v2 |
| **continual** | 1 | HARD=1 | T3=1 | EXP_a8_continual_writes_no_catastrophic_forgetting_v1 |
| **noise_robust** | 1 | PASS=1 | T3=1 | EXP_ner_transition_charngram_noise_crosscut_cpu_v1 |
| **projection** | 1 | HARD=1 | T3=1 | EXP_kv_learned_projection_v1 |
| **refuse_gate** | 1 | HARD=1 | T3=1 | EXP_refuse_gate_5_graph_health_cpu_v1 |
| **sequence_binding** | 1 | HARD=1 | T3=1 | EXP_c3_compressed_sequence_replay_v1 |

## High-cohesion families (≥ 5 chain-grade atoms = substantive capability core)

### composition (267 chain-grade atoms)

- Verdict mix: {'PASS': 266, 'HARD': 1}
- Tier distribution: {'T3': 267}
- Exemplars:
  - `EXP_substrate_compositional_generalization_K10_to_K20_v1_n40`
  - `EXP_substrate_novel_assembly_2_tier2_novel_composition_equiv`
  - `EXP_q_a3_l10000_cross_layer_composition_v1_n16384`
  - `EXP_q_a3_l1000_cross_layer_composition_v1_n16384`
  - `EXP_q_a3_l1000_cross_layer_composition_v1_n8192`

### uncategorized (110 chain-grade atoms)

- Verdict mix: {'PASS': 107, 'HARD': 3}
- Tier distribution: {'T3': 110}
- Exemplars:
  - `EXP_active_inference_dpefe_h2_cpu_v1`
  - `EXP_crt_module_scaling_battery_v1`
  - `EXP_csp_hebbian_coexist_v1`
  - `EXP_deletion_cert_refusal_joint_v1`
  - `EXP_hnsw_ef_search_calibration_v1`

### capacity (31 chain-grade atoms)

- Verdict mix: {'PASS': 29, 'HARD': 2}
- Tier distribution: {'T3': 31}
- Exemplars:
  - `EXP_substrate_capacity_composition_b2xb4_v1_n2048`
  - `EXP_substrate_decomposition_resonator_alpha05_cpu_v1`
  - `EXP_tier4_multiseed_sweep_cpu_v1`
  - `EXP_wave1_multiseed_sweep_cpu_v1`
  - `EXP_wave1_tier1_sweep_cpu_v1`

### topology (22 chain-grade atoms)

- Verdict mix: {'PASS': 22}
- Tier distribution: {'T3': 22}
- Exemplars:
  - `EXP_pp48_nkt_cross_n_depth13_v1_n8192`
  - `EXP_pp48_nkt_cross_n_depth17_v1_n8192`
  - `EXP_pp48_nkt_cross_n_depth19_v1_n16384`
  - `EXP_pp48_nkt_cross_n_depth19_v1_n8192`
  - `EXP_pp48_nkt_depth_11_v1_n4096`

### whitening (5 chain-grade atoms)

- Verdict mix: {'PASS': 5}
- Tier distribution: {'T3': 5}
- Exemplars:
  - `EXP_substrate_audit_core_C2_C3_whitened_pythia160m_v2_n4096`
  - `EXP_substrate_audit_core_C2_C3_whitened_llama1b_v1_n4096`
  - `EXP_substrate_dim_expansion_subsumes_whitening_n_enc_10000_v`
  - `EXP_substrate_last_token_vs_whitening_mean_pool_v1`
  - `EXP_substrate_pca_prewhitening_codebook_v1`

### kg_ingest (5 chain-grade atoms)

- Verdict mix: {'HARD': 3, 'PASS': 2}
- Tier distribution: {'T3': 5}
- Exemplars:
  - `EXP_ccc1_extra_fb15k237_kg_multihop_v1`
  - `EXP_substrate_multimodal_binding_text_kg_v1`
  - `EXP_u1_fb15k237_ingest_eval_v1`
  - `EXP_n8_conceptnet_ingest_eval_v1`
  - `EXP_h_hotpotqa_ingest_v1`

## Cross-family atoms (candidate "core underlying mathematics" arrows)

Atoms that lexically match MULTIPLE category keywords — these are the natural candidates for *natural transformations between subcategories* (USER's framing). Each such atom links two (or more) capability families and is a candidate isomorphism arrow.

| atom | categories spanned |
|---|---|
| `EXP_substrate_audit_core_C2_C3_whitened_pythia160m_v2_n4096` | whitening × encoding |
| `EXP_substrate_audit_core_C2_C3_whitened_llama1b_v1_n4096` | whitening × encoding |
| `EXP_substrate_capacity_composition_b2xb4_v1_n2048` | capacity × composition |
| `EXP_substrate_decomposition_resonator_alpha05_cpu_v1` | capacity × composition |
| `EXP_wave1_multiseed_sweep_cpu_v1` | capacity × wave_audit |
| `EXP_wave1_tier1_sweep_cpu_v1` | capacity × multi_hop × wave_audit |
| `EXP_wave2_rescue_multiseed_sweep_cpu_v1` | capacity × wave_audit |
| `EXP_f8_pinv_padfix_alpha_compound_v1` | capacity × composition |
| `EXP_modern_hopfield_n_sweep_v1` | capacity × hopfield |
| `EXP_pp50_kappa3_delta_alpha_n16384_v2_n16384` | capacity × topology |
| `EXP_pp50_kappa3_delta_alpha_n32768_v3_n32768` | capacity × topology |
| `EXP_pp50_kappa3_delta_alpha_n8192_v1_n8192` | capacity × topology |
| `EXP_pp50_kappa3_ultra_fine_sigma_g_v4_n16384` | capacity × topology |
| `EXP_substrate_capacity_composition_full_b2xb4xhier_v1_n2048_` | capacity × composition |
| `EXP_substrate_capacity_stress_composition_v1_n16384` | capacity × composition |
| `EXP_kmax_ness_envelope_corrected_v1` | capacity × phase_diagram |
| `EXP_g1b_capacity_sweep_v1` | capacity × generation |
| `EXP_ccc1_extra_fb15k237_kg_multihop_v1` | kg_ingest × multi_hop |

## Interpretation (USER strategic vision)

The capability families above represent the substrate's *empirically validated mathematical structure*. Where families compose with each other (cross-family atoms; multi-category exemplars), those crossing points are candidates for the *core underlying mathematics* substrate has independently arrived at across cells.

**Next steps (Phase 1 → Phase 2 → Phase 3 per USER strategic vision):**
- v2: spectral analysis of the atom-relation graph + per-family eigenvalue signatures (identify which families have similar mathematical character)
- v2: cross-family natural-transformation discovery (category-theory framing per brain-drill #7 candidate)
- Phase 2 (long horizon): substrate samples NEW atom-candidates from learned distribution + auto-checks against cap_pres → autoatom proposals
- Phase 3 (AGI-adjacent): substrate's glass-box LM reasons about its own capability gaps + proposes new mathematics

— Research (Director); v1 substrate self-mapping; cert-trail durable artifact; no addressee.