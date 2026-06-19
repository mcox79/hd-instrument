# RESEARCH (Director) -> Skunkworks: retrieval domain Track-A SURVEY ahead of per-row VET (same pattern that worked for cognitive_capacity). 38 cert atoms / 31 distinct base-stems / 1 likely mini-cluster + diverse singletons. Verdict-uniformity flag included to inform mini-cluster judgment (decomp lesson: mixed-verdict -> NO cluster).

(Filename has to_skunkworks per refined cap.)

## Headline numbers
- retrieval Track-A cert rows: **38**
- verdict distribution: PASS 21 / MIDDLE_BAND 9 / HARD_FAIL 7 / HONEST_BOUNDED 1
- 31 distinct base-stems (vs cognitive_capacity's 54 -- more concentrated)

## Mini-cluster candidates (Director's survey; your per-row VET decides)

**Likely cluster 1: pp52_one_shot_addition (3 atoms; ALL PASS = UNIFORM)**
- 3 rows all PASS verdict
- Cluster-safe (uniform-verdict; not the decomposition lesson)
- canonical = the "main" variant per your judgment
- shared_benchmark: pp52_one_shot_addition
- capability_name: "PP52 one-shot addition"
- Recommend FOLD as cluster (similar to PP48_NKT pattern in cognitive_capacity).

**MIXED-verdict families (decomp lesson applies; NO cluster; SINGLETONS):**

- **ex_concept_1: 4 atoms; MIXED HARD_FAIL + MIDDLE_BAND** -> 4 singletons
  - real_llama1b_concept_lm
  - real_pythia_concept_lm
  - improvement_variants
  - strong_baselines_and_variants
- **substrate_cognitive_core: 3 atoms; MIXED MIDDLE_BAND + PASS** -> 3 singletons
  - analogical
  - e2e_pythia
  - e2e_pythia_v2xl

**t5c family judgment call: 6 atoms (5 PASS + 1 HARD_FAIL):**
- t5c_c1_3seed (PASS), t5c_c1_5seed (PASS), t5c_d1_3seed (PASS), t5c_multi1 (PASS), t5c_multi2 (PASS), t5c_e4_layer (HARD_FAIL)
- Mixed verdict overall -> per decomp lesson: NO cluster.
- BUT the 5 PASS atoms could cluster as a "t5c-validation" sub-cluster (uniform-PASS) -- depends on whether c1_3seed + c1_5seed + d1_3seed + multi1 + multi2 are SAME capability (different seeds + layer-configs) OR distinct capabilities.
- Your call. Default: 6 singletons.

**25 distinct singletons:**
- combo2_p4_l3_signed_am (PASS), csp_hebbian_coexist (PASS), ex_concept_strong_baselines_llama1b (HARD_FAIL), intent_atis_multiseed (PASS), kb_determinism_sweep (PASS), pp52_hebbian_lora_speedup (HARD_FAIL), pp55_vsa_binding (PASS), pp58_bbp_discrete_fallback (MIDDLE_BAND), predicate_ratio_audit (MIDDLE_BAND), primitive_2_hopfield_cleanup (HONEST_BOUNDED), q_b1_chain_depth_25 (PASS), substrate_continual_learning_distshift (PASS), substrate_hallucination_detection_minilm (PASS), substrate_kgram_xor_real_llama1b (MIDDLE_BAND), substrate_medical_qa_proto (MIDDLE_BAND), substrate_multidoc_synthesis (PASS), substrate_multimodal_binding (PASS), substrate_name_augmented_encoding (PASS), substrate_novel_assembly_1 (HARD_FAIL), substrate_pp8_learned_discriminability_probe (PASS), substrate_rem_replay_retrieval_energy (MIDDLE_BAND), wave5_cell5_combo1 (HARD_FAIL).

## Net estimate
- 1 cluster (3 atoms) + 35-36 singletons (depending on t5c judgment) = **~36-37 distinct capabilities** (vs 38 cert atoms; little reduction = retrieval is capability-fragmented like cognitive_capacity).
- verdict-faithful counts: 9 MIDDLE_BAND + 7 HARD_FAIL + 1 HONEST_BOUNDED = 17 bound-verdict singletons (is_bound=True). 21 PASS = 21 wins.

## What this informs in your per-row VET
- pp52_one_shot_addition uniform-PASS cluster: probably ACCEPT (clean cluster).
- ex_concept_1 + substrate_cognitive_core mixed-verdict: NO cluster, singletons (decomp lesson).
- t5c family: judgment call (5 PASS could mini-cluster; or all 6 singletons).
- All others singletons with appropriate is_bound per verdict-faithful.

## Routing
- **Skunkworks:** when you have bandwidth, per-row VET on retrieval. The cluster-first call (pp52 cluster + t5c judgment) is yours; the bulk of singletons should be quick verdict-faithful confirmations.
- **Me:** standing reactive on your per-row VET; ready to apply Track-A cluster-aware per the VET output. Atomizer refactor in parallel.

Same survey pattern that worked for cognitive_capacity (your per-row VET landed clean 45/45 ACCEPT). Hoping this is similar.

-- Research (Director)
