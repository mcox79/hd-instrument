# Testbed encoder-provenance fleet audit + Path C substrate-native cleanup proposals (2026-06-26)

Author: testbed (integrator + fleet-health auditor).
Scope: full chain-grade cert portfolio (cert_ledger.jsonl meta partition, 478 chain-grade rows / 464 unique experiments).
Discipline: Fix #28 default UNDER-claim on provenance; "AMBIGUOUS" promoted to LLM_AT_INFERENCE only after surgical eyeball.
Corpus completeness: local cert_ledger 542KB / remote (marsh@home) 543KB (within seconds of sync; local is canonical).

## TL;DR

Encoder-provenance split (chain-grade portfolio, N=464 unique experiments):

| Bucket | Count | % |
|---|---|---|
| SUBSTRATE_NATIVE | 375 | 80.8% |
| LLM_AT_INFERENCE | 43 | 9.3% |
| NO_CELL_CANT_VERIFY | 34 | 7.3% |
| UNKNOWN_NO_ENCODER_SIGNAL | 6 | 1.3% |
| SUBSTRATE_NATIVE_INFERENCE_LLM_INGEST_ONLY | 2 | 0.4% |
| MIXED_LLM_AND_SUBSTRATE_AT_INFERENCE | 2 | 0.4% |
| WORD2VEC_DIAGNOSTIC_PROBE | 2 | 0.4% |

Headline: ~81% of chain-grade portfolio is already Path C-compliant. ~9% (43 cells) use LLM features at inference and need encoder-dependence triage. ~9% (NO_CELL / UNKNOWN) need bookkeeping cleanup before classification.

Top-3 cleanup actions: (a) tag each chain-grade atom in Store with `encoder_provenance` field; (b) extend cap_map with a new "Encoder provenance" column and bulk-fill from the FINAL map; (c) author 4-5 substrate-native re-validation cells for the encoder-dependent claims that ARE load-bearing for the substrate-product narrative.

New META rule candidate: `META_substrate_product_inference_uses_substrate_native_encoder_only_LLM_encoders_diagnostic_only_path_C_load_bearing`.

Top risk surface: Stage 3 audit-device pipeline (production application) cites the `t5c_*` and `kv_learned_projection_v1` chain-grade lineage — these are LLM_AT_INFERENCE and may need a Path C migration plan OR an explicit "deployment context: LLM-key inference" caveat before external citation.

---

## Section 1 -- Encoder-provenance inventory (chain-grade portfolio)

### Classifier methodology

1. Pulled all `cert_status: chain_grade` rows from `data/substrate_index/meta/cert_ledger.jsonl`: 478 rows / 465 unique atom_ids / 464 unique experiment names (one atom missing the `EXP_` prefix).
2. Mapped experiment name -> cell .py file via `experiments/exp_<name>.py` lookup: 430/464 matched directly.
3. Pattern-classified each cell source by encoder family:
   - LLM families: pythia / minilm-or-sentence-transformers / bge / llama / t5-or-flamingo / distilbert / e5
   - Word2vec / gensim / glove / KeyedVectors
   - Substrate-native: rand bipolar, sparse_bipolar, FPE/phasor, k-WTA, random codebook, np.random.RandomState
4. Surgical deep-classification for LLM-touching cells: distinguished between "LLM at inference" (cell loads + runs LLM encoder, or loads precomputed LLM-residuals .npz at runtime) vs "LLM probe only" (LLM used for ingest-time semantics only, substrate-native synthetic keys drive inference).

Persisted to `data/_testbed_encoder_provenance_FINAL.jsonl` (one row per chain-grade experiment with encoder_class + cell_file + atom_id).

### Bucket definitions and full lists

#### SUBSTRATE_NATIVE (375 -- ~81%)

Cells use random bipolar / sparse_bipolar / FPE phasor / random codebook / k-WTA / char-trigram at inference. No LLM or word2vec in inference path. Path C-compliant.

Spot-checked sample (representative):
- `a8_continual_writes_no_catastrophic_forgetting_v1` -- random ±1 patterns + noise flip
- `csp_hebbian_coexist_v1` -- Ising encoding, random patterns
- `intent_atis_multiseed_cpu_v1` -- "intent prototype = normalized bundle of training sentences' word phasors (seeded codebook)"
- `pos_tagger_multiseed_cpu_v1` -- "tag codebook init, OOV morphology, context binding"
- `temporal_contextual_multiseed_cpu_v1` -- FPE phasor (`np.exp(1j*ang)`)
- `substrate_abduction_f1_weakest_signature_kernel_kgram_xor_groundtruth_cpu_v1` -- bipolar codebook, k-gram XOR
- `modern_hopfield_n_sweep_v1` -- bipolar P patterns
- `combo3_unified_api_v1_n16384_l4_alpha_grid_v1` -- substrate VSA primitives
- (367 others in the same family; see `data/_testbed_encoder_provenance_FINAL.jsonl`)

#### LLM_AT_INFERENCE (43 -- ~9%)

Cells where the inference path uses LLM-derived features (either live-encoded via transformers AutoModel, or loaded from a precomputed `residuals.npz` extracted by an upstream LLM cell). The chain-grade claim depends on those features.

LLM family breakdown:
- MiniLM (sentence-transformers all-MiniLM-L6-v2): 16 cells
- Pythia-160m / pythia-2.8b: 11 cells
- Pythia + T5/Flamingo combo: 5 cells
- Llama-3.2-1B + multi-family arms: 3 cells
- Other multi-family combos: 8 cells

Complete LLM_AT_INFERENCE list (sorted):

1. `a1_substrate_intent_classifier_v1` (MiniLM)
2. `f6_bge_large_pinv_mmax_reaudit_v1` (BGE-large + MiniLM)
3. `f8_pinv_padfix_alpha_compound_v1` (MiniLM)
4. `fp16_vs_fp32_parity_v1` (MiniLM)
5. `hoc1_word_bigram_v1` (MiniLM)
6. `kf1_paraphrase_robustness_marianmt_v1` (MiniLM)
7. `kv_learned_projection_v1` (Pythia-2.8B; the canonical M=10k held-out KV-learned-projection chain-grade)
8. `padding_side_audit_capacity_v1` (Pythia-160m)
9. `pb_crt_real_encoder_atoms_v1` (MiniLM)
10. `pb_e5_vs_bge_pinv_headtohead_v1` (e5 + BGE + llama)
11. `pb_kf1_multilang_chain_robustness_v1` (MiniLM)
12. `pb_mmr_real_encoder_clustered_v1` (MiniLM)
13. `pb_multilang_paraphrase_chain_kf1_v1` (MiniLM)
14. `pb_pinv_llama_l15_keys_v1` (Llama-3.2-1B layer-15)
15. `pb_production_recipe_integration_v1` (MiniLM)
16. `pseudoinverse_real_encoder_keys_v1` (MiniLM)
17. `substrate_audit_core_C2_C3_whitened_llama1b_v1_n4096` (Llama-3.2-1B residuals .npz)
18. `substrate_audit_core_C2_C3_whitened_pythia160m_v2_n4096` (Pythia-160m residuals .npz)
19. `substrate_cognitive_core_analogical_v1` (Pythia-160m ICL comparator)
20. `substrate_cognitive_core_architectural_advantage_v1` (Pythia-160m)
21. `substrate_cognitive_core_counterfactual_v1` (Pythia-160m)
22. `substrate_cognitive_core_introspection_toolkit_v1` (Pythia-160m residuals.npz per-token)
23. `substrate_continual_learning_30day_realistic_stream_v1` (Pythia-160m)
24. `substrate_dim_expansion_subsumes_whitening_n_enc_10000_v1` (MiniLM, expand+whiten)
25. `substrate_encoder_capacity_at_scale_battery_gpu_v1` (MiniLM + BGE + Llama)
26. `substrate_etf_minilm_dim_expansion_v1` (MiniLM)
27. `substrate_hallucination_detection_minilm_v1` (MiniLM medical KB)
28. `substrate_hallucination_robustness_hard_negatives_v1` (MiniLM)
29. `substrate_last_token_vs_whitening_mean_pool_v1` (Llama)
30. `substrate_long_conversation_10k_exchanges_v1` (Pythia-160m comparator)
31. `substrate_long_conversation_scale_1000_exchanges_v1` (Pythia-160m comparator)
32. `substrate_minilm_encoder_fidelity_v1` (MiniLM vs Pythia head-to-head)
33. `substrate_multidoc_synthesis_1000plus_docs_v1` (Pythia)
34. `substrate_pca_prewhitening_codebook_v1` (MiniLM)
35. `substrate_real_encoder_capabilities_v1` (MiniLM + Pythia)
36. `t5c_c1_3seed_validate_gpu_v1` (Pythia-160m + T5/Flamingo trainable gate)
37. `t5c_c1_5seed_validate_gpu_v1` (same)
38. `t5c_d1_3seed_validate_gpu_v1` (same)
39. `t5c_hybrid_3seed_kb10k_v1` (Pythia + BGE + Llama + T5)
40. `t5c_multi1_everylayer_3seed_v1` (Pythia + T5)
41. `t5c_multi2_6layer_3seed_v1` (Pythia + T5)
42. `t5c_pp225_3seed_v1` (Pythia + BGE-large; "PP225 = encoder->logit direct projection")
43. `t5c_pp225_pythia14b_fp32proj_3seed_v1` (same, pythia-1.4b scale)

#### MIXED_LLM_AND_SUBSTRATE_AT_INFERENCE (2)

Cells run BOTH LLM-encoded keys AND substrate-native synthetic keys in different arms within the same cell. Per-arm verdict matters (Fix #28).

- `n8_conceptnet_ingest_eval_v1` -- ConceptNet ingestion. MiniLM-L6 encodes entities at ingest BUT inference is done over substrate-bipolar `E`/`R` codebooks AND over LLM-encoded variant arms in the same cell.
- `h_hotpotqa_ingest_v1` -- HotpotQA Wikipedia. Same pattern; bipolar `E`/`R` codebooks alongside MiniLM-encoded variants.

These are honest -- the chain-grade claim is "substrate ingestion + multi-hop traversal works at this scale on real-data KG entities", and the substrate-native arm is what gets the chain-grade tier. The LLM variant is comparator. Re-label these as Path-C-compliant with "LLM optional comparator arm" footnote.

#### SUBSTRATE_NATIVE_INFERENCE_LLM_INGEST_ONLY (2)

Cells where LLM identifiers appear in source (for comparator framing or ingest-time semantic mapping) but inference path is pure substrate-native synthetic.

- `p1_action_at_any_position_phase_diagram_v1` -- documents "Existing chain-grade evidence covers encoder-swap (audit_core_C2_C3_whitened_pythia/llama1b)" but actually runs `synthetic_bipolar_keys_with_VQ_codebook` end-to-end. Path C-compliant.
- `p1_v2_action_at_any_position_LLM_class_v1` -- same family; LLM-class is the diagram axis but inference uses bipolar codebook.

Re-label these as SUBSTRATE_NATIVE.

#### WORD2VEC_DIAGNOSTIC_PROBE (2)

- `substrate_position_binding_combined_arch_trigram_v1_n4096` -- word2vec used at probe; trigram-encoder runs inference. Likely SUBSTRATE_NATIVE; needs surgical inspection.
- `substrate_compose_freq_routing_v5_DEFINITIVE` -- `WORD2VEC_MODEL = "word2vec-google-news-300"` + `SPARSE_BIPOLAR_F = 0.05` (encoder = word2vec on sparse-bipolar projection). LLM-encoder-like at inference; treat as LLM_AT_INFERENCE-equivalent for Path C.

#### NO_CELL_CANT_VERIFY (34)

Atom_ids whose `EXP_<name>` does not match a present .py file. Mostly `*_full_v3` or `*_lambda_batch_results_*` named cells. Likely either:
- archived/renamed cells with a re-run lineage (need provenance crawl)
- bundle-level atoms whose underlying source got compacted

Sample: `c_infty_seb_detection_full_v3`, `capacity_cliff_graceful_full_v3`, `multiagent_coord_full_v3`, `crt_module_scaling_battery_fixed_v1`, `hebb_vs_pseudoinverse_long_v1`, `r_alpha_throughput_full_v3`, `lambda_batch_results_combo3_unified_api_n32768_v1_bd9c5a0f_data_exp_combo3_unified_api_n32768_v1`, `lambda_batch_results_deletion_cert_zratio_n32768_v1_bd9c5a0f_data_exp_deletion_cert_zratio_n32768_v1`, `substrate_hierarchical_5corpus_meta_v2_n2048_gpu`, `substrate_name_augmented_encoding_recovery_canonical_rerun_v593`.

Action: route to skunkworks cert-archeology to map each to a parent cell source; provisional bucket = "presumed SUBSTRATE_NATIVE pending verification" since most legacy substrate cells are bipolar.

#### UNKNOWN_NO_ENCODER_SIGNAL (6)

Cells where my classifier found neither LLM/word2vec nor substrate-encoder patterns. Likely encoder-independent (meta rules / wave sweeps that don't define an encoder explicitly).

- `tier4_multiseed_sweep_cpu_v1`
- `wave1_multiseed_sweep_cpu_v1`
- `wave1_tier1_sweep_cpu_v1`
- `wave2_rescue_multiseed_sweep_cpu_v1`
- `sql_hd_aggregation_bound_gpu_v1`
- `substrate_pp8_learned_discriminability_probe_v1`

Action: surgical eyeball next testbed cycle (sub-hour); presumed SUBSTRATE_NATIVE.

---

## Section 2 -- Decision matrix for LLM_AT_INFERENCE cells

For each LLM_AT_INFERENCE chain-grade claim, the question is: does the chain-grade rating REQUIRE the LLM encoder to hold, or would the same mechanism hold on substrate-native keys?

Six sub-categories emerge from inspection:

### 2A. Encoder-IS-the-mechanism (CANNOT re-validate on substrate-native, by construction)

The cell's claim IS about LLM-encoder feature behaviour. Re-validation would be a different claim.

| Anchor | Reason |
|---|---|
| `substrate_minilm_encoder_fidelity_v1` | "Does MiniLM give substrate-grade recall vs Pythia" -- claim is fidelity-of-LLM-encoders |
| `substrate_real_encoder_capabilities_v1` | Same family |
| `substrate_encoder_capacity_at_scale_battery_gpu_v1` | Capacity sweep across LLM encoders |
| `pb_e5_vs_bge_pinv_headtohead_v1` | LLM-encoder comparison |
| `padding_side_audit_capacity_v1` | Pythia padding-side audit -- about Pythia internals |
| `kf1_paraphrase_robustness_marianmt_v1` | MarianMT paraphrase robustness with MiniLM keys |
| `substrate_hallucination_detection_minilm_v1` | "Substrate as grounding gate for LLM output" -- LLM is the deployment context |
| `substrate_hallucination_robustness_hard_negatives_v1` | Same family |

Action: keep chain-grade. Re-label cert-class to "DEPLOYMENT_CONTEXT_LLM_KEYS" or similar sub-tier; no Path C re-validation needed because the claim is about LLM-encoder integration scope.

### 2B. Encoder-DEPENDENT mechanism (may NOT hold on substrate-native; substrate-native re-validation valuable)

The cell's mechanism (pseudoinverse / whitening / ETF / KV-learned-projection / PCA-prewhitening) is general but was VALIDATED only against LLM-anisotropic keys. The mechanism likely works on substrate-native too -- but the chain-grade claim as written is conditioned on LLM-key anisotropy.

| Anchor | Mechanism | Substrate-native re-validation worth? |
|---|---|---|
| `pseudoinverse_real_encoder_keys_v1` | Pinv lift over Hebb on whitened MiniLM keys | YES -- pinv on substrate-bipolar should ALSO show lift; quick cell |
| `pb_production_recipe_integration_v1` | Full whiten+pinv recipe lift | YES -- substrate-native version |
| `f8_pinv_padfix_alpha_compound_v1` | Pinv padding-fix alpha-compounding | YES -- substrate-native check |
| `f6_bge_large_pinv_mmax_reaudit_v1` | Pinv mmax on BGE-large keys | LOWER PRIORITY -- subsumed by pseudoinverse_real_encoder substrate-native check |
| `substrate_dim_expansion_subsumes_whitening_n_enc_10000_v1` | Expand+whiten composition lift | YES -- substrate-native bipolar should show same/different behaviour |
| `substrate_etf_minilm_dim_expansion_v1` | ETF headroom via dim-expansion on MiniLM | YES -- substrate-native bipolar dim-expansion check |
| `substrate_pca_prewhitening_codebook_v1` | PCA prewhitening on MiniLM codebook | YES |
| `substrate_last_token_vs_whitening_mean_pool_v1` | Last-token vs mean-pool on Llama keys | LOWER PRIORITY -- substrate-native has no analog |
| `fp16_vs_fp32_parity_v1` | FP16/32 numerics parity on MiniLM keys | LOWER PRIORITY -- substrate-native already FP32; tangential |
| `kv_learned_projection_v1` | Contrastive KV projection on Pythia-2.8B M=10k held-out | YES, HIGH-PRIORITY -- this is a load-bearing flagship claim; substrate-native synthetic-bipolar version proves the projection-training mechanism without LLM dependence |
| `hoc1_word_bigram_v1` | Word-bigram on MiniLM keys | YES -- substrate-native word-phasor bigram check |
| `pb_kf1_multilang_chain_robustness_v1` | Multi-lang chain robustness with MiniLM | LOWER PRIORITY -- substrate-native has no language axis |
| `pb_pinv_llama_l15_keys_v1` | Pinv on Llama-L15 keys | LOWER PRIORITY -- subsumed by substrate-native pinv check |
| `pb_crt_real_encoder_atoms_v1` | CRT (combo-residual-trial) atoms with real keys | YES -- substrate-native CRT check |
| `pb_mmr_real_encoder_clustered_v1` | MMR with clustered real keys | YES -- substrate-native MMR check |

Recommend: 4 priority substrate-native re-validation cells (NOT 15), bundled:
- **CELL_RV1**: substrate-native pinv-lift over Hebb (replaces `pseudoinverse_real_encoder_keys_v1` claim path)
- **CELL_RV2**: substrate-native dim-expansion-subsumes-whitening (substitutes `substrate_dim_expansion_subsumes_whitening_n_enc_10000_v1`)
- **CELL_RV3**: substrate-native KV-learned-projection M=10k held-out (substitutes `kv_learned_projection_v1`)
- **CELL_RV4**: substrate-native ETF dim-expansion + PCA prewhitening (subsumes `substrate_etf_minilm_dim_expansion_v1` + `substrate_pca_prewhitening_codebook_v1`)

### 2C. Audit-core C2/C3 (load-bearing for substrate-product narrative)

| Anchor | Status |
|---|---|
| `substrate_audit_core_C2_C3_whitened_pythia160m_v2_n4096` | LLM-residuals .npz input; deletion-cert + drift mechanisms |
| `substrate_audit_core_C2_C3_whitened_llama1b_v1_n4096` | Llama-1B variant |

The deletion-cert + drift mechanisms are encoder-independent (they are storage-algebra properties). The cells happen to demonstrate on LLM residuals because that's the production-storage context. Decision: re-label cert-class to "DEPLOYMENT_CONTEXT_LLM_RESIDUALS" + add a substrate-native synthetic-bipolar variant as a SHIM cell (encoder-independent re-validation; quick CPU; cycles the claim onto Path C-pure ground). Provisional bundle: `substrate_audit_core_C2_C3_synthetic_bipolar_v1_n4096`.

### 2D. Cognitive-core comparator narratives (Pythia head-to-head)

| Anchor | Decision |
|---|---|
| `substrate_cognitive_core_analogical_v1` | Pythia ICL is comparator; substrate arm is bipolar codebook. Re-label MIXED_LLM_AND_SUBSTRATE -- substrate arm Path C-compliant; Pythia arm is comparator. |
| `substrate_cognitive_core_architectural_advantage_v1` | Same |
| `substrate_cognitive_core_counterfactual_v1` | Same |
| `substrate_cognitive_core_introspection_toolkit_v1` | LOADS pythia residuals .npz at runtime -- different shape; substrate stores LLM residuals (audit-core lineage). Same decision as 2C. |
| `substrate_continual_learning_30day_realistic_stream_v1` | Pythia comparator + substrate substrate-bipolar |
| `substrate_long_conversation_10k_exchanges_v1` | Pythia comparator + substrate |
| `substrate_long_conversation_scale_1000_exchanges_v1` | Same |
| `substrate_multidoc_synthesis_1000plus_docs_v1` | Pythia comparator + substrate |

Recommend: re-classify these as MIXED_LLM_AND_SUBSTRATE (not LLM_AT_INFERENCE) -- the substrate arm IS Path C-compliant; the LLM arm is comparator. This is honest: the chain-grade tier rests on the substrate-arm result, not on LLM-encoder behaviour. Audit the per-arm metrics.json (Fix #28) to confirm before re-classification.

### 2E. T5C phase-CD architecture (largest LLM_AT_INFERENCE cluster: 7 cells)

| Anchor | Position in arc |
|---|---|
| `t5c_c1_3seed_validate_gpu_v1` | Phase C Flamingo gate on frozen Pythia-160M |
| `t5c_c1_5seed_validate_gpu_v1` | Same, 5-seed |
| `t5c_d1_3seed_validate_gpu_v1` | Phase D follow-on |
| `t5c_hybrid_3seed_kb10k_v1` | Hybrid Pythia+BGE+Llama+T5; KB=10k |
| `t5c_multi1_everylayer_3seed_v1` | Multi-layer Pythia |
| `t5c_multi2_6layer_3seed_v1` | Same, 6 layers |
| `t5c_pp225_3seed_v1` | PP225 = encoder->logit projection (Pythia+BGE-large) |
| `t5c_pp225_pythia14b_fp32proj_3seed_v1` | Same, 1.4B scale |

These cells form a coherent arc: substrate-augmented LLM. The mechanism IS the substrate-LLM interface; LLM is in the inference path by design. This is NOT substrate-product inference; it's substrate-AS-augmentation. Decision: re-label as a separate cert-tier "LLM_AUGMENTATION" -- explicitly NOT Path C-substrate-product-inference. Keep chain-grade. Make the distinction visible in cap_map.

### 2F. Production-side cells (pb_*, a1_*, kv_*)

`pb_*` cells (production-recipe lineage), `a1_substrate_intent_classifier_v1` (production intent classifier), and `kv_learned_projection_v1` are the cells closest to a real production application. These are also the cells whose chain-grade claim sits at the deployment boundary.

Decision: re-label cert-class as "DEPLOYMENT_CONTEXT_LLM_KEYS" and surface explicitly that the chain-grade tier is conditional on LLM-encoder integration. For each, document the substrate-native equivalent and authorize re-validation if the deployment use-case shifts to Path C.

---

## Section 3 -- Recommended cleanup actions (priority order)

### Action 1 (HIGH): Tag every chain-grade atom with `encoder_provenance` Store metadata

Per-atom field addition, NOT a new partition. Schema:

```
encoder_provenance: {
  family: SUBSTRATE_NATIVE | LLM_AT_INFERENCE | MIXED_LLM_AND_SUBSTRATE | LLM_INGEST_ONLY | WORD2VEC_DIAGNOSTIC | DEPLOYMENT_CONTEXT_LLM_KEYS | DEPLOYMENT_CONTEXT_LLM_RESIDUALS | LLM_AUGMENTATION | UNKNOWN,
  llm_families: list[str],   // pythia / minilm_or_st / bge / llama / t5_or_flamingo / e5_or_other
  path_c_compliant: bool,
  deep_class: str,           // result of deep classifier (LLM_AT_INFERENCE / SUBSTRATE_AT_INFERENCE_LLM_PROBE_ONLY / ...)
  audit_ts: ISO8601,
  audit_source: "testbed_encoder_provenance_audit_2026-06-26"
}
```

Route: skunkworks (cert-owner) writes via `add_atom` patch path; use `data/_testbed_encoder_provenance_FINAL.jsonl` as the input mapping. Single-writer serial per Store concurrency rule. Bulk-add wrapped in load+save+os.replace pattern.

### Action 2 (HIGH): Extend cap_map with encoder-provenance column

`notes/substrate_capability_map.md` does NOT currently surface encoder provenance per row. Add a column "Encoder provenance" to each table (Memory primitives / Concept-level / Continual / Robustness / Composed reasoning / etc). Bulk-fill from FINAL map. New column emoji legend:
- SN (SUBSTRATE_NATIVE) -- Path C-compliant
- LLM-INF (LLM_AT_INFERENCE) -- encoder-dependent
- LLM-AUG (LLM_AUGMENTATION) -- substrate-as-augmentation arc, not substrate-product inference
- MIX (MIXED_LLM_AND_SUBSTRATE) -- per-arm split; substrate arm is Path C-compliant
- LLM-INGEST (LLM_INGEST_ONLY) -- substrate-native inference; LLM at ingest only
- DEPL-LLM (DEPLOYMENT_CONTEXT_LLM_KEYS) -- claim conditional on LLM-encoder integration

Route: strategy_scribe owns cap_map mutations; this is an annotation pass (NOT P-band change) so can run while paused per directive on annotation bumps.

### Action 3 (MEDIUM): Author 4 substrate-native re-validation cells

Per Section 2B, ship:
- `CELL_RV1`: substrate-native pinv-vs-Hebb lift (subsumes `pseudoinverse_real_encoder_keys_v1` substrate-arm claim)
- `CELL_RV2`: substrate-native dim-expansion-subsumes-whitening
- `CELL_RV3`: substrate-native KV-learned-projection M=10k held-out (substrate-native version of the flagship `kv_learned_projection_v1` chain-grade)
- `CELL_RV4`: substrate-native ETF dim-expansion + PCA prewhitening composition

Route: exp_dev to design + dispatch; substrate-mine FIRST (per directive) -- check if existing chain-grade cells already cover these on substrate-native before authoring new ones (e.g. `combo3_unified_api_v1_n16384_l4_alpha_grid_v1` may cover RV1 already).

### Action 4 (MEDIUM): Audit-core C2/C3 substrate-native SHIM cell

Author `substrate_audit_core_C2_C3_synthetic_bipolar_v1_n4096`. Encoder-independent mechanism (deletion-cert + drift) gets a Path C-pure chain-grade row. ~CPU 30-min cell. Pre-reg: pass-band matches the LLM-residual chain-grade bands.

Route: exp_dev.

### Action 5 (LOW): Deprecate the 6 HARD_FAIL Gap-2 anisotropy mechanisms from active mechanism candidate lists

USER's task brief calls out: "Deprecate the 6 HARD_FAIL geometry-side anisotropy mechanisms from active mechanism candidate lists (whitening, MIMO, DG, polarimetric, expansion v4, ScaNN VQ -- all on pythia; per Gap 2 closure)".

Note: these are HARD_FAIL atoms, not chain-grade, so they are NOT in this audit's portfolio. The deprecation action is a candidate-list cleanup, separate from the chain-grade encoder-provenance tagging. Strategy_scribe owns the candidate-list mutation (likely in `notes/substrate_capability_map.md` Section 2 CANNOT or in a separate active-candidate file).

### Action 6 (LOW): Archive stale smoke-only experiment cells whose mechanisms are refuted/superseded

Sweep `experiments/exp_*.py` for cells with:
- HARD_FAIL atom + no resurrection cell in 60+ days
- Smoke-only verdict + no real-data variant in 60+ days
- Superseded mechanism (e.g. Gap-2 anisotropy refutations)

Move to `experiments/_archive/`. Route: testbed (this is an infra-refinement task within my pre-authorized scope). Will surface to USER first if scope exceeds ~50 cells.

### Action 7 (LOW): Update substrate-product positioning doc

Explicit statement in `notes/substrate_capability_map.md` PRIMARY PRODUCT NARRATIVE section:

> "Production substrate-product inference uses substrate-native encoder ONLY (random bipolar / FPE phasor / random codebook / k-WTA). LLM encoders (Pythia / MiniLM / BGE / Llama) are setup-time diagnostic probes for measuring substrate behaviour on real-data-shaped keys, OR setup-time ingest-only embeddings; they are NEVER in the production substrate-product inference path. The 43 chain-grade atoms tagged LLM_AT_INFERENCE are diagnostic-grade evidence for substrate behaviour under real-data-key geometry; they are NOT substrate-product-inference claims. Cells tagged LLM_AUGMENTATION (the t5c_* arc) are explicitly substrate-AS-augmentation-of-LLM, a separate product narrative tier from substrate-product."

Route: strategy_scribe.

---

## Section 4 -- New META rule candidate

Propose for atomization (route to skunkworks after USER ratification):

**Atom name**: `META_substrate_product_inference_uses_substrate_native_encoder_only_LLM_encoders_diagnostic_only_path_C_load_bearing`

**Description**: Path C decision (USER 2026-06-23 + 2026-06-26 formalization): production substrate-product inference uses substrate-native encoder only (random bipolar / FPE phasor / random codebook / k-WTA / char-trigram). LLM encoders (Pythia / MiniLM / BGE / Llama / E5 / sentence-transformers) are diagnostic probes at setup time OR ingest-time semantic mappers; they are never in the substrate-product inference path. Principle O (basis vs use-case): basis vectors are content-free; labels appear at readout, not in basis. Brain-existence-proof: billion years of evolution produced organism-internal encoders without borrowing other species' representations; substrate-HD shouldn't borrow LLM representations for production inference either. 80.8% of chain-grade portfolio (375/464) is already Path C-compliant; 9.3% (43 LLM_AT_INFERENCE) carries a "DEPLOYMENT_CONTEXT_LLM_KEYS" or "LLM_AUGMENTATION" sub-tier. Load-bearing for: substrate-product positioning, encoder-mining decisions, future-experiment encoder-choice defaults, cap_map row classification.

**Tier**: META.

**Audit source**: `notes/testbed_encoder_provenance_audit_path_C_cleanup_2026-06-26.md` (this note).

**Supersedes**: nothing; complements Principle O and the 2026-06-23 Path C decision atoms.

**Verification check (anti-saturation)**: META rule holds iff future encoder-related cells default to substrate-native at inference path; LLM-encoder cells default to "DEPLOYMENT_CONTEXT" or "LLM_AUGMENTATION" cert-class. Skunkworks cert-tiering routes through this META at classification time.

---

## Section 5 -- Risk surface

### Risk R1 (HIGH): Stage 3 audit-device pipeline

The `audit-core C2/C3` cells + the `t5c_pp225_*` cells are cited downstream by the Stage 3 audit-device pipeline (substrate-stores-LLM-residuals + deletion-cert + drift). These are LLM_AT_INFERENCE per this audit.

Sub-questions:
- Does the Stage 3 production-application code actually depend on Pythia/Llama residuals being in the substrate at inference?
- Or is the deletion-cert + drift mechanism encoder-independent (storage-algebra-only)?

If the former: need an explicit "deployment context: LLM-residual storage" caveat OR a Path C migration plan (substrate-native residuals from a substrate-encoder).

If the latter: the SHIM cell (Action 4) is sufficient and the production code is already encoder-agnostic at the algebra layer.

Recommend: testbed audits the Stage 3 production-application code next cycle (sub-hour scan) to determine which sub-case holds.

### Risk R2 (MEDIUM): External demos / Storefront stories citing "chain-grade @ M=10M on real-data"

Some demo materials reference "chain-grade hierarchical 2-level partition routing @ M=10M on Pythia keys" or similar. If those keys are Pythia-derived (LLM_AT_INFERENCE), the framing needs updating: either (a) re-frame as "diagnostic-grade @ M=10M on LLM-encoder keys" + the substrate-native version at smaller M, OR (b) commission a substrate-native re-validation at M=10M (substantial compute).

Recommend: testbed crawls `notes/storefront_*` and external-demo files next cycle to catalog claims that need framing-updates. Route to strategy_scribe to author updates.

### Risk R3 (MEDIUM): Test harnesses that depend on pythia keys

Test harnesses in `tools/` or `hdlab/` that auto-generate cells using Pythia keys as defaults are silent vectors for Path C drift. New cells authored via those harnesses default to LLM_AT_INFERENCE without authors realising.

Recommend: testbed scans `tools/spawn_templates/`, `tools/cell_template.py`, etc. next cycle for default-encoder choices. Route fixes through pre-authorized infra refinements (within scope).

### Risk R4 (LOW): NO_CELL_CANT_VERIFY portfolio (34 atoms)

34 chain-grade atoms with no matching .py file means there's a non-trivial chunk of the portfolio whose encoder provenance I cannot verify. Lifecycle question: were these cells renamed/archived? Do they have a re-run lineage I can pick up? Bookkeeping debt.

Recommend: route to skunkworks cert-archeology to map each NO_CELL atom back to its parent .py file (likely via git log on `data/exp_<name>/` directories OR atomization metadata). Sub-hour task.

### Risk R5 (LOW): Default-substrate-native fail-band confounds with LLM-anisotropy results

If the substrate-native re-validation cells (Action 3) FAIL but the LLM-encoder versions PASSED, it means the mechanism is ENCODER-dependent (relies on LLM-anisotropy or LLM-feature-geometry). That's INFORMATIVE -- not a defeat of Path C -- but it does narrow the substrate-product positioning. Pre-register honest bands. Make sure verdict messaging distinguishes "mechanism narrowed to LLM-anisotropy regime" from "mechanism fails".

---

## Disciplines applied

- Fix #28 (default UNDER-claim on provenance): I started with broad LLM patterns and narrowed via 3 passes of surgical inspection. The "MIXED" bucket is the under-claimed default; only after surgical eyeball did I promote AMBIGUOUS to LLM_AT_INFERENCE.
- Substrate-mine before extrapolating: substrate-native re-validation cells (Action 3) are scoped to mine the existing chain-grade portfolio FIRST before authoring new cells. E.g. `combo3_unified_api_v1_n16384_l4_alpha_grid_v1` may already cover RV1.
- Corpus-completeness: verified local (542KB) vs remote (543KB) cert_ledger.jsonl size within seconds of sync; local is canonical.
- ASCII-only output.
- Did NOT execute any persistence (Action 1-7 are proposals; route through Director after USER review).
- Verify-the-referent: each LLM_AT_INFERENCE claim cross-checked against the actual cell source (`experiments/exp_<name>.py`), not against the atom metadata alone.

## Artifacts produced

- `notes/testbed_encoder_provenance_audit_path_C_cleanup_2026-06-26.md` (this note)
- `data/_testbed_encoder_provenance_FINAL.jsonl` (per-experiment final provenance map; 464 rows; canonical for downstream actions)
- `data/_testbed_encoder_provenance_chain_grade.jsonl` (v1 classifier output; historical)
- `data/_testbed_encoder_provenance_chain_grade_v2.jsonl` (v2 refined LLM-family breakdown)
- `data/_testbed_encoder_provenance_chain_grade_v3.jsonl` (v3 broader substrate-native patterns)
- `data/_testbed_encoder_provenance_deep_v1.jsonl` (deep classifier v1 -- LLM-at-inference detection)
- `data/_testbed_encoder_provenance_deep_v2.jsonl` (deep classifier v2 -- broader inference patterns)

## Open questions for USER / Director

1. Should re-validation cells (Action 3) be substrate-mine-FIRST (testbed inspects existing chain-grade for coverage) BEFORE exp_dev dispatch, or should exp_dev own that decision tree?
2. Is "DEPLOYMENT_CONTEXT_LLM_KEYS" the right sub-tier label, or does USER prefer a different naming (e.g. "PROBE_LLM_KEYS", "DIAGNOSTIC_LLM_KEYS")?
3. For the t5c_* LLM_AUGMENTATION cluster: keep as separate cert-tier or fully exclude from Path C cap_map narrative?
4. Should the NO_CELL_CANT_VERIFY portfolio (34 atoms) be back-filled by skunkworks cert-archeology, or should they age-out and be removed from the chain-grade tally if archeology cannot recover the source?
