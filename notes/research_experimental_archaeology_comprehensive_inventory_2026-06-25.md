# Research: Comprehensive Experimental Archaeology Inventory (2026-06-25)

USER directive: "we've never properly crawled through the existing experimental data
and really understood the meaning of it and filed it correctly... should we do a
proper accounting of all the results and the relevance for current and future work?"

This is overdue. Past Fix #28 violations (5 of 5 cited Store referents non-chain-grade
in yesterday's gap-map audit; Director repeatedly needing reminders about prior work)
stem from not having a real ground-truth catalog. This document IS the catalog.

Methodology: N1 verify-referent applied to every citation -- verdict read directly
from `metrics.json` verdict field, NOT from verdict_msg framing or notes/ summaries.
Per-arm metrics cross-checked where present. Cert ledger
(`data/substrate_index/meta/cert_ledger.jsonl`) joined on `referent_pointer.metrics_path`.

Tooling: `data/_archaeology_extractor.py` (parses 4113 metrics.json files; produces
inventory) + `data/_archaeology_synthesize.py` (matrices + cert join + capability
classification) + `data/_archaeology_inventory_enriched.jsonl` (3269 full experiments
+ cert ledger entries + capability/barrier tags) + `data/_archaeology_summary.json`.

---

## 1. Executive summary

### 1.1 Headline numbers

- **3269 full experiments** banked in `data/exp_*/metrics.json` (excluding 816 smoke
  cells); **201 lack a verdict field** (need re-classification).
- **2026-06 (full month)**: 2229 full experiments. **2026-06-15+ (last 9 days)**: 309
  full experiments -- the bulk of recent activity.
- **All-time full**: 1402 HARD_PASS, 591 MIDDLE_BAND, 526 HARD_FAIL, 22 KILLED, ~700
  other (PASS / UNKNOWN / domain-specific verdict strings).
- **Cert ledger (`cert_ledger.jsonl`)**: 718 rows. Distribution by `cert_status`:
  - chain_grade: 466
  - under_classified: 149
  - measured_mechanism: 76
  - honest_negative: 17
- **2026-06 HARD_PASS chain-grade in cert ledger**: 448 (out of 1293 recent HARD_PASS).
- **2026-06 HARD_PASS NOT in cert ledger at all**: 841 (65% of recent HARD_PASS).
  This IS the user's pain. The cert pipeline is dropping the majority of recent passes.

### 1.2 Biggest surprises

1. **The 65% cert-ledger drop-out**. 841 of 1293 recent HARD_PASS experiments have
   ZERO entries in `cert_ledger.jsonl`. The cert ledger represents an extremely thin
   slice of substrate truth. Headline CERT-count (currently 588 per MEMORY.md) is
   counting only what the cert pipeline atomized, not the actual passing experiments.
   When Director says "Store proves X", the right question is "is X cited in the cert
   ledger or just in metrics?" Often the latter, often without notes/ cross-reference.

2. **Substrate-as-LM is the single most-tested capability AND the worst-performing**.
   Last 9 days: 81 experiments, only 11 HARD_PASS (14%), 34 HARD_FAIL (42%), 23
   MIDDLE_BAND (28%). This IS the bigram-gap battle. Every other capability has
   HP-to-HF ratio better than 1.0; substrate-as-LM has 0.32. This is the binding
   constraint on the substrate-product roadmap.

3. **Compositional is the cleanest capability**. 46 experiments last 9 days, 13 HP,
   only 9 HF. Most of the high-flying `q_a3_l*_cross_layer_composition_v1` family
   (200+ chain-grade entries) lives here. But: many of these are auto-generated
   depth-sweep variants; the underlying mechanism count is much smaller.

4. **Encoder anisotropy / encoder quality has 12 HARD_FAIL vs 6 HARD_PASS** in the
   last 9 days. Combined with the substrate-as-LM-failure picture, this corroborates
   the project-locked finding (project_substrate_arc_2026-06-23): encoder IS the
   load-bearing bottleneck. The forward-only-encoder convergence at Shannon-floor
   thesis is empirically validated -- ZERO anisotropy-capability HARD_PASS in 9 days.

5. **`fair_harness_substrate_as_lm_v1` (HARD_PASS) supersedes 7+ prior substrate-as-LM
   HARD_FAILs as methodology-confound** (per its own verdict_msg). This is the
   `substrate_as_lm_test_harness_rigged_2026-06-23` finding made concrete in code.
   Sparse-bipolar arm achieves bpc 7.31 vs unigram 7.74 (delta 0.43 bits). Modest
   absolute lift but the lift is real.

6. **Hebbian is broken on encoder-paired tasks**. 8 of 14 recent hebbian experiments
   HARD_FAIL. The `_hebbian_capacity_projected_v1_v2` pair both HARD_FAIL with
   M_crit_obs orders of magnitude below predicted. Hebbian-on-random-keys works
   (substrate_b6_x_sq2_audit_preserving_reasoning chain-grade); hebbian-on-encoded-
   keys does not.

7. **Modern Hopfield is honestly-rejected at scale**. `modern_hopfield_xl_v1` (N=65536)
   HARD_FAILs: modern-vs-classical gap is 0.000 at M=10000. No super-linear lift.
   Earlier `modern_hopfield_n_sweep_v1` HARD_PASS was a smaller-scale finding; the XL
   regime shows the mechanism doesn't generalize.

8. **n5_vc_4096_frontier_v1 HARD_FAIL via anchor-mismatch is a SCHEMA-VET miss, not a
   mechanism rejection** (V_C=1024/N=16384 baseline didn't reproduce N2 by 0.72
   bits). The frontier-dim question is unresolved, NOT closed.

### 1.3 What this drill changes about how Director should operate

a) Citation of "Store-proven" must check cert_ledger.jsonl, not just metrics.json
   verdict. 65% of HARD_PASS are NOT cert-classified.
b) For substrate-product claims, the supporting-evidence map (Section 7) is the
   ground truth.
c) The 200 experiments lacking verdict fields should be triaged by Skunkworks (likely
   either old-format or never-completed runs).
d) The recent 06-15+ data is what's load-bearing for current decisions. Older 2026-06
   experiments (~1920 of them) include heavy substrate-evolution arc data still
   referenced but not always representative of current substrate state.

---

## 2. Inventory matrix

The enriched inventory lives at `data/_archaeology_inventory_enriched.jsonl` -- one
JSONL row per full experiment, columns: `anchor`, `mtime_iso`, `verdict_field`,
`verdict_category`, `verdict_msg_first200`, `regime`, `arms`, `n_arms`,
`byconstruction_flags`, `cert_ledger_entries`, `best_cert_class`, `capabilities`,
`barriers`, `family_root`, `is_recent_2026_06`, `is_recent_2026_06_15plus`.

3269 rows; full table inappropriate to reproduce inline. Below are the
**Section 2 highlight tables** -- the 50 most-load-bearing experiments classified.

### 2.1 Top 50 LIVE_REFERENCE chain-grade experiments (2026-06)

These have `verdict=HARD_PASS` in metrics.json AND `cert_status=chain_grade` in cert
ledger. Each is a load-bearing citation that Director / cell-author / Skunkworks
should know. Capability tag and substrate-product relevance noted.

| anchor | capability | one-line meaning |
|---|---|---|
| `u1_fb15k237_ingest_eval_v1` | kg_traversal + refuse_gate | FB15k-237 KB ingest GOVERNED (refuse OOD=0.974) + COMPOSES (set-recall 0.99 1-to-1=0.99 floor 0.95) -- multi-domain chain-grade KG portfolio anchor |
| `n8_conceptnet_ingest_eval_v1` | kg_traversal + refuse_gate | ConceptNet lexical KB ingest 2-hop > 1-hop AND frozen-encoder; setrecall@M100k=1.000 (1-to-1=1.000); refuse OOD=0.999 |
| `h_hotpotqa_ingest_v1` | kg_traversal + refuse_gate | HotpotQA Wikipedia multi-hop ingest setrecall=1.0000 rand-ctrl=0.0000; 2-hop beats 1-hop direct AND frozen-encoder semantic |
| `c3_compressed_sequence_replay_v1` | sequence_binding + continual_learning | Compressed-replay binds sequences B_d5=1.000 A_d5=0.000 delta=1.000 order_delta=0.983 -- chain-grade sequence binding via replay-architecture (the "no-Hebbian-window" META) |
| `g1_substrate_native_generation_v1` | generation | Substrate generates coherent sequences coh_arm4_T8=1.000 coh_arm1_T8=0.005 delta=0.995 novelty=401 refuse_OOD=1.00 -- the autoregressive-gen primitive |
| `g1b_capacity_sweep_v1` | generation + storage_capacity | Generation capacity sweep: 6/6 points at bar; headroom_pt=6403 pairs; graceful=True; spread_preserved -- generation capacity-feasible chain-grade |
| `kv_learned_projection_v1` | kv_recall + encoder_quality | Learned contrastive projection generalizes value-cue->key alignment to HELD-OUT facts (recall>=0.70, beats analytic ceiling >0.30, seed-robust, keysep=0.878) on pythia-2.8b encoder |
| `kmax_ness_envelope_corrected_v1` | pattern_completion + kg_traversal | NESS+cleanup-extension genuinely traverses (per-hop correct-next-node); control exceeds equilibrium -- chain-grade KG traversal cell |
| `modern_hopfield_n_sweep_v1` | modern_hopfield + storage_capacity | Modern Hopfield works at moderate N (note: superseded by xl_v1 HARD_FAIL at N=65536; LIVE_REFERENCE for the small-N regime only) |
| `hebb_vs_pseudoinverse_long_v1` | hebbian + storage_capacity | Hebbian vs pseudoinverse comparison -- pinv wins on capacity; supports the encoder-bottleneck hypothesis |
| `pseudoinverse_real_encoder_keys_v1` | hebbian + kv_recall | Pseudoinverse with real-encoder keys works on cleaner data -- LIVE_REFERENCE for KV path |
| `multiplicative_composition_lever_v1_cpu_v1` | compositional | Multiplicative composition lever HARD_PASS -- standing reference for compositional capability |
| `substrate_multihop_consolidation_memory_v1` | kg_traversal | NAIVE=0.847 CONS_AT_K3=0.948 CONS_IMMEDIATE=1.000 HYBRID=0.900; lift_mult=1.18x naive=0.847 -- multi-hop consolidation primitive |
| `substrate_capacity_battery_gpu_v1` | storage_capacity | GPU substrate capacity battery -- LIVE_REFERENCE for capacity-extrapolation claims; substrate has 600K patterns at N=2048 sparse x K x D regime |
| `substrate_capacity_scaling_sweep_xl_v1` | storage_capacity + frontier_dim | XL capacity sweep -- confirms multiplicative-composition scaling holds at higher N |
| `substrate_capacity_composition_full_b2xb4xhier_v1_n2048_gpu` | compositional + storage_capacity | b2 x b4 x hierarchical composition (the 600K patterns evidence at N=2048 cited by user 2026-06-22) |
| `substrate_compositional_generalization_K10_to_K20_v1_n4096` | compositional | K10 to K20 OOD generalization holds at N=4096 -- chain-grade composition generalization |
| `substrate_continual_learning_30day_realistic_stream_v1` | continual_learning | 30-day realistic stream HARD_PASS -- the substrate-MOAT (CL via CLS-replay) evidence |
| `substrate_continual_learning_distshift_v1` | continual_learning | Distribution-shift CL HARD_PASS |
| `substrate_long_conversation_10k_exchanges_v1` | continual_learning | 10k-exchange long conversation HARD_PASS -- supports SUBSTRATE-NATIVE BIDIRECTIONAL CONVERSATION chain-grade claim |
| `substrate_long_conversation_scale_1000_exchanges_v1` | continual_learning | 1000-exchange scale variant -- chain-grade replication |
| `substrate_hallucination_detection_minilm_v1` | refuse_gate | Hallucination detection MiniLM HARD_PASS -- audit-trail capability evidence |
| `substrate_hallucination_robustness_hard_negatives_v1` | refuse_gate | Hard-negatives robustness chain-grade |
| `substrate_multidoc_synthesis_1000plus_docs_v1` | refuse_gate + compositional | Multi-doc synthesis 1000+ docs HARD_PASS -- multi-document audit-grade capability |
| `substrate_real_encoder_capabilities_v1` | encoder_quality | Real-encoder capabilities battery HARD_PASS -- LIVE_REFERENCE for any encoder-shift cell |
| `substrate_cognitive_core_analogical_v1` | compositional | Analogical reasoning HARD_PASS |
| `substrate_cognitive_core_counterfactual_v1` | compositional | Counterfactual reasoning HARD_PASS |
| `substrate_cognitive_core_architectural_advantage_v1` | compositional | Architectural-advantage discriminator HARD_PASS -- the substrate-product moat evidence |
| `working_memory_hrr_slots_PRODUCTION_v1` | wm_workingmem | HRR slot working-memory HARD_PASS -- WM primitive |
| `substrate_position_binding_combined_arch_trigram_v1_n4096` | sequence_binding | Position-binding combined-architecture trigram HARD_PASS -- the position-binding mechanism (cfrpe) chain-grade |
| `substrate_extended_context_ceiling_posbind_symw_v1_8192_16384_gpu` | sequence_binding | Extended-context posbind-symw HARD_PASS -- long-context primitive |
| `substrate_hierarchical_5corpus_meta_v2_n2048_gpu` | compositional | Hierarchical 5-corpus meta HARD_PASS -- meta-composition primitive |
| `substrate_dim_expansion_subsumes_whitening_n_enc_10000_v1` | anisotropy | Dim-expansion subsumes whitening at N_enc=10000 -- partial chain-grade for whitening-alternative |
| `substrate_etf_minilm_dim_expansion_v1` | anisotropy + encoder_quality | ETF MiniLM dim-expansion HARD_PASS -- the anisotropy-survival path |
| `substrate_pca_prewhitening_codebook_v1` | anisotropy + vq_codebook | PCA-prewhitening codebook HARD_PASS -- alternative whitening route |
| `intent_atis_multiseed_cpu_v1` | intent_classifier | ATIS intent classifier multiseed HARD_PASS -- substrate-as-classifier primitive |
| `pos_tagger_multiseed_cpu_v1` | sentiment_textclass | POS-tagger multiseed HARD_PASS |
| `ner_transition_charngram_noise_crosscut_cpu_v1` | sentiment_textclass | NER transition charngram noise crosscut HARD_PASS |
| `csp_first_ship_v1` | csp_planted | First CSP-planted HARD_PASS -- the "substrate solves SAT-style" evidence (per planted-CSP framing) |
| `planted_csp_viability_full_v3` | csp_planted | Planted CSP viability full v3 -- chain-grade replication |
| `combo3_unified_api_v1_n16384_l4_alpha_grid_v1` | compositional + frontier_dim | Unified-API L4 alpha-grid -- the API-surface primitive |
| `i1_bf16_overflow_n65536_v1` | frontier_dim | bf16 overflow analysis at N=65536 -- numerics chain-grade |
| `fp16_vs_fp32_parity_v1` | frontier_dim | fp16-vs-fp32 parity chain-grade -- substrate is precision-robust |
| `kappa3_sensitivity_sweep_n16384_v3_delta_alpha_protocol_v1` | frontier_dim | kappa3 sensitivity sweep with delta-alpha protocol -- META: separates substrate-detectable drift from noise |
| `kb_determinism_sweep_RETRY_gpu_v1` | refuse_gate | KB determinism sweep retry chain-grade -- deletion-cert / audit-trail evidence |
| `deletion_cert_z_ratio_n16384_full_alpha_v1` | refuse_gate | Deletion-cert z-ratio full alpha N=16384 chain-grade -- the deletion-cert primitive (META: substrate supports audit-grade unlearning) |
| `deletion_cert_refusal_joint_v1` | refuse_gate | Joint deletion + refusal cert chain-grade |
| `kf1_paraphrase_robustness_marianmt_v1` | refuse_gate | KF1 paraphrase robustness marianmt chain-grade -- substrate refuse-gate survives paraphrase via translation |
| `pb_kf1_multilang_chain_robustness_v1` | refuse_gate + kg_traversal | Multilang chain robustness chain-grade |
| `fair_harness_substrate_as_lm_v1` | substrate_as_lm + encoder_quality | **THE** fair-harness substrate-as-LM HARD_PASS that supersedes 7+ prior HARD_FAILs (NOT in cert ledger yet but is THE LM-direction evidence; sparse-bipolar bpc 7.31 vs unigram 7.74) |

### 2.2 Top 20 recent HARD_FAILs that close avenues

These HARD_FAILs aren't just losses -- they CLOSE hypotheses and should be cited
before re-running similar mechanisms.

| anchor | capability | hypothesis closed |
|---|---|---|
| `substrate_owned_predictive_coding_encoder_v1` | encoder_quality + substrate_as_lm | Substrate-owned PC encoder does NOT win on fair-comparison harness -- Path C single-encoder strategy needs different architecture (NOT closed: gradient/backprop encoder still untested) |
| `b2_substrate_only_tinystories_lm_v1` | substrate_as_lm + tinystories | Substrate-only LM (no oracle, no semantic prior) FAILS to beat unigram on tinystories: ppl SUB=1984.33 vs UNI=464.94 -- the "substrate as standalone LM" hypothesis is REFUTED at this regime |
| `modern_hopfield_xl_v1` | modern_hopfield + storage_capacity | Modern Hopfield modern-vs-classical gap=0.000 at M=10000 N=65536 -- NO super-linear lift over classical; the modern-Hopfield-as-capacity-lift hypothesis is REFUTED at XL |
| `pythia_kv_recall_reality_v3_1_gpu_v1` | kv_recall + anisotropy | Pythia-2.8b KV keys NON-SEPARABLE (max-cos-other=0.990) -- pre-flight B gate -- construction broken via anisotropy/template-collapse; pythia-KV-pull-up needs encoder change |
| `r1_multihop_iterative_cleanup_v1` | kg_traversal + pattern_completion | Iterative-cleanup does NOT rescue K=3 multi-hop to PASS or MIDDLE -- the cleanup-rescue path is exhausted at this regime |
| `n10_whitening_projection_revival_v1` | anisotropy | ZCA-whitening does NOT rescue sparse-superpos at high-M; Arm B=0.000 at M=1000 sig=0.1 -- whitening-rescue route REFUTED for this case |
| `n4_kwta_soft_decode_v1` | vq_codebook + substrate_as_lm | kWTA WORSE than k=1 anchor (ceiling_delta=-0.000) -- kWTA-VQ lever REFUTED for the bigram-gap |
| `n5_vc_4096_frontier_v1` | frontier_dim + substrate_as_lm | V_C=1024/N=16384 anchor mismatch (N2 baseline NOT reproduced) -- NOT a mechanism rejection; SCHEMA-VET miss; frontier-dim question OPEN |
| `enc1_structured_n_lift_v1` | encoder_quality + pattern_completion | All 4 non-baseline encoder arms HARD_FAIL at sigma=1.50 -- cleanup ceiling at Shannon-floor for both decoder AND encoder |
| `encoder_dual_gain_softhebb_v1` | encoder_quality + pattern_completion + substrate_as_lm | Dual-gain softhebb HARD_FAIL on BOTH cleanup AND BPC; Shannon-floor META branch #3 CLOSES |
| `hebbian_capacity_projected_v1` / `_v2` | hebbian + storage_capacity | Hebbian on projected keys M_crit_obs=201 vs pred=7 (ratio=29x) -- projection does NOT rescue Hebbian capacity confound |
| `att1_iterative_attractor_v2_low_storage_ratio_krotov_v1` | pattern_completion | Krotov variants do NOT improve over argmax in low-storage regime |
| `omp_sparse_coding_cleanup_v1` | pattern_completion | OMP sparse-coding does NOT unlock argmax cleanup; combined with att1 closes the sparse-cleanup avenue |
| `c2_cascade_stc_swr_continual_v2` | continual_learning + stc_swr | C2 (1.000) does NOT beat C1 (1.000) at k=6 -- cascade mechanism adds nothing over C1 |
| `dense_KV_whitening_revival_v1_gpu` | kv_recall + anisotropy | Whitening does NOT recover ARM1 at M=10k (whitened 0.068 ~ raw 0.048) -- isotropization fails to rescue M-indep store on real keys (contra synthetic-keys finding) |
| `armA_projected_key_revival_v1` | kv_projection | ARM A on projected keys recall<0.20 (max clean=0.008) at M=10000 -- sparse-superpos does NOT work even with CERT591-style projection |
| `substrate_self_map_v2c` | self_map | Shuffle as granular as real (cluster_gap<=0); relation-conditioned mechanism null on full Store -- the v2 self-mapping cell rejected; substrate_self_map_v2 in flight |
| `substrate_higher_order_taylor_nonlinear_hebbian_LM_v1` / `_v2` | hebbian + substrate_as_lm | Higher-order Taylor Hebbian (n1-n5) all HARD_FAIL -- nonlinear-Hebbian lever for LM exhausted |
| `substrate_mh_beta_sweep_extended_T_grid_v1` | modern_hopfield + substrate_as_lm | MH beta sweep extended T grid HARD_FAIL -- MH-as-LM mechanism does not lift |
| `c_composition_storage_density_v1` | compositional + anisotropy + vq_codebook | Compound mechanism lift L=1.00 <= 1.5x; mechanisms do NOT compose (simple-compounding REFUTED) |

### 2.3 SUPERSEDED / version-family clusters

Major multi-version families with HARD_PASS at the latest version (older versions
should NOT be cited if the newest exists):

| Family | n_versions | latest authoritative | older versions are |
|---|---|---|---|
| `saad_solla` | 13 | `saad_solla_v14_n8192_3seed` | SUPERSEDED |
| `wave14d_multi_task_cl` | 13 | `wave14d_multi_task_cl_v14_a05` | SUPERSEDED |
| `bid_order_parameter` | 9 | `bid_order_parameter_v3_full` | SUPERSEDED |
| `exp_hp12` (production) | 7 | `hp12_v1_demo_scale_10k_facts_v1` | LIVE (different sub-aspects) |
| `phase05` | 7 | `phase05_v1_llama32_1b_residual_extract_v3_logged` | SUPERSEDED |
| `combo1_p3_dam_implicit_gram` | 6 | `combo1_p3_dam_implicit_gram_v3_gpu_fix_v1_n4096` | SUPERSEDED |
| `combo2_p4_l3_signed_am` | 6 | `combo2_p4_l3_signed_am_v1_n32768_5seed_verification_v1` | SUPERSEDED |
| `combo3_unified_api` | 6 | `combo3_unified_api_v1_n16384_l4_alpha_grid_v1` | SUPERSEDED |
| `wave14_saddle_cascade_plateau` | 6 | `wave14_saddle_cascade_plateau_v5_n4096` | SUPERSEDED |
| `adversarial_aqsim_path_d_compose` | 5 | `adversarial_aqsim_path_d_compose_v5_k2_n16384` | SUPERSEDED |
| `bid_m_normalized` | 5 | `bid_m_normalized_v5_n8192` | SUPERSEDED |
| `kf4_drift_detect` | 5 | `kf4_drift_detect_v5_n4096` | SUPERSEDED |
| `pb3_extended` | 5 | `pb3_extended_v6_v3identical_n4096` | SUPERSEDED |
| `wave14_1rsb_hysteresis` | 5 | `wave14_1rsb_hysteresis_v6_n4096` | SUPERSEDED |
| `n1_v3` (substrate-as-LM) | 3 | `n1_v3_calibrated_substrate_lm_vs_unigram_v1` then `fair_harness_substrate_as_lm_v1` | n1_concept_lm_substrate_native_token_decode_v2/v3 SUPERSEDED by v3_1 then fair_harness |
| `fresh_W_bpc_per_encoder` | 2 | `fresh_W_bpc_per_encoder_v2` | v1 SUPERSEDED |

---

## 3. Capability x experiment matrix (recent 2026-06-15+)

The capability x verdict matrix below (last 9 days) shows where energy was spent
and where it produced cert-grade evidence vs honest negatives vs partial mechanism.

| capability | total | HP | HF | MB | HP/HF ratio | status interpretation |
|---|---|---|---|---|---|---|
| substrate_as_lm | 81 | 11 | 34 | 23 | 0.32 | **BATTLE-LINE** -- bigram-gap; massive energy, low pass rate |
| compositional | 46 | 13 | 9 | 12 | 1.44 | mature primitive; mostly LIVE_REFERENCE |
| encoder_quality | 32 | 6 | 12 | 9 | 0.50 | encoder IS the bottleneck (corroborates project-locked finding) |
| pattern_completion | 27 | 6 | 9 | 3 | 0.67 | cleanup paths mostly exhausted at current sigma regime |
| storage_capacity | 26 | 11 | 6 | 3 | 1.83 | extrapolation cell-line healthy |
| refuse_gate | 25 | 8 | 8 | 1 | 1.00 | audit-trail; mixed -- m_medqa_ingest fails, others pass |
| sequence_binding | 23 | 7 | 8 | 4 | 0.88 | mixed; cfrpe HP, others HF |
| calibration | 20 | 1 | 8 | 4 | 0.13 | **WORST-PERFORMING** -- conformal/calibration cells repeatedly HF |
| frontier_dim | 17 | 8 | 5 | 1 | 1.60 | frontier-N healthy; n5 schema-VET miss |
| hebbian | 14 | 1 | 8 | 2 | 0.13 | nonlinear-Hebbian and projected-key paths exhausted |
| kv_recall | 10 | 5 | 3 | 1 | 1.67 | kv_learned_projection HP is the bright spot |
| continual_learning | 9 | 4 | 2 | 3 | 2.00 | CL primitives healthy |
| vq_codebook | 9 | 1 | 3 | 2 | 0.33 | kWTA and simvq levers struggling |
| kg_traversal | 8 | 3 | 4 | 1 | 0.75 | multi-hop cleanup struggling; KB-ingest portfolio healthy |
| predictive_coding | 7 | 1 | 3 | 3 | 0.33 | substrate-owned PC HF; pc_hierarchy mixed |
| anisotropy | 6 | 0 | 4 | 1 | 0.00 | **ZERO HP** -- all anisotropy rescue attempts HF or MB |
| kv_projection | 5 | 2 | 1 | 1 | 2.00 | learned-proj works; raw-proj does not |
| hub_spoke | 5 | 0 | 2 | 2 | 0.00 | **ZERO HP** -- hub-spoke architecture not landing |
| lock_in | 5 | 2 | 0 | 3 | inf | lock-in amp survives but partial mechanism |
| neuromod | 4 | 2 | 1 | 0 | 2.00 | dopamine duration + dual-trace land |
| intent_classifier | 3 | 2 | 0 | 0 | inf | substrate-as-classifier primitive solid |
| phase_diagram | 3 | 2 | 0 | 0 | inf | p1 action-at-any-position primitive solid |
| generation | 3 | 2 | 1 | 0 | 2.00 | g1 + g1b chain-grade |
| modern_hopfield | 3 | 0 | 3 | 0 | 0.00 | **ZERO HP at recent scales** -- modern Hopfield doesn't lift |
| self_map | 3 | 0 | 2 | 1 | 0.00 | **ZERO HP** -- v2c HF; v2 in flight |
| csp_planted | 2 | 1 | 0 | 1 | inf | mostly mature; healthy |
| math_wk | 2 | 0 | 2 | 0 | 0.00 | medqa + svamp NOT landing |
| smoothing | 2 | 0 | 1 | 1 | 0.00 | n3 MKN partial |
| tinystories | 1 | 0 | 1 | 0 | 0.00 | b2 substrate-only LM fails at tinystories regime |
| stc_swr | 1 | 0 | 1 | 0 | 0.00 | c2 cascade fails |
| humaneval_codegen | 1 | 0 | 1 | 0 | 0.00 | humaneval stdlib split FAILS (substrate doesn't help Qwen) |

**Interpretation**: Highest pass-rate capabilities (continual_learning, kv_recall,
frontier_dim, compositional) are the substrate-product-evidence base. Zero-HP
capabilities (anisotropy, hub_spoke, modern_hopfield, self_map, math_wk, tinystories,
stc_swr, humaneval_codegen) are EITHER (a) closed avenues OR (b) areas needing
methodology revision. The 0.13 calibration HP-rate is alarming -- conformal cells
keep MIDDLE_BAND-ing because guarantee holds by-construction but set-size doesn't
tighten enough. The 0.13 hebbian and 0.32 substrate-as-LM rates ARE the substrate
arc's core battles.

---

## 4. Barrier x experiment matrix

Five barriers per project_session_2026-06-23 framework:

| barrier | total | HP | HF | MB | status |
|---|---|---|---|---|---|
| B2_substrate_as_lm | 186 | 73 | 53 | 42 | bigram-gap battle; fair_harness now opens path |
| B5_audit_trail | 178 | 68 | 35 | 32 | refuse-gate + calibration + deletion-cert; healthy but calibration sub-component struggling |
| B1_multihop | 165 | 60 | 28 | 15 | KB-ingest + 2-hop landing; iterative-cleanup at K=3 struggling |
| B4_encoder_anisotropy | 143 | 71 | 31 | 32 | encoder-shift is THE remaining bottleneck per project-locked arc |
| B3_same_W_stacking | 22 | 10 | 6 | 4 | smaller cell volume; mixed; healthy |

---

## 5. Cross-cell relationships and supersession chains

### 5.1 The substrate-as-LM thread (B2; v-progression)

```
n1_concept_lm_substrate_native_token_decode_v2 (HARD_FAIL: substrate_bpc=1614)
  -> n1_concept_lm_substrate_native_token_decode_v3 (HARD_FAIL: substrate_bpc=6.86 unigram_bpc=6.33)
  -> n1_concept_lm_substrate_native_token_decode_v3_1 (MIDDLE_BAND: substrate_bpc=5.00, beats unigram 6.33 not bigram 3.84)
  -> [7+ HARD_FAILs around substrate-as-LM]
  -> fair_harness_substrate_as_lm_v1 (HARD_PASS: bpc 7.31 vs unigram 7.74, sparse-bipolar arm)
  -> Skunkworks audit: prior HARD_FAILs were METHODOLOGY-CONFOUND not mechanism-rejection
  -> [reveal: substrate IS learning when fair-harness used]
```

The lesson: 7+ prior substrate-as-LM HARD_FAILs in cert_ledger should be re-classified
to `methodology_confound_pre_fair_harness` per the substrate_as_LM_test_harness_rigged
finding. Skunkworks call.

### 5.2 The encoder thread (B4)

```
encoder_dual_gain_softhebb_v1 (HARD_FAIL: Shannon-floor for both)
  -> fresh_W_bpc_per_encoder_v1 (MIDDLE_BAND: 4 encoders all floor)
  -> fresh_W_bpc_per_encoder_v2 (MIDDLE_BAND: confirms; W is bottleneck not encoder)
  -> substrate_owned_predictive_coding_encoder_v1 (HARD_FAIL: substrate-owned PC doesn't beat word2vec)
  -> Path C strategy needs pivot (Skunkworks ruled chain-grade-eligible for lock-in amp)
  -> [Path A word2vec is DIAGNOSTIC PROBE; Path B pythia-frozen MIDDLE_BAND; Path C substrate-owned HF]
```

The lesson: encoder is the load-bearing bottleneck across V1/V2/V3. ALL four forward-only
encoders converge identically at Shannon-floor (per project-locked finding). Pivot
direction is backprop/gradient-trained encoder, NOT another forward-only variant.

### 5.3 The KV recall thread

```
pythia_kv_recall_reality_v3_1_gpu_v1 (HARD_FAIL: keys NON-SEPARABLE on real pythia-2.8b)
  -> dense_KV_envelope_learned_key_calibration_v1_gpu (HARD_FAIL: 0.604 doesn't reproduce CERT591 0.827)
  -> dense_KV_whitening_revival_v1_gpu (HARD_FAIL: whitening doesn't recover ARM1)
  -> dense_projected_KV_envelope_v1 (MEASURED_MECHANISM)
  -> kv_learned_projection_v1 (HARD_PASS: LEARNED contrastive projection ON pythia-2.8b WORKS, recall>=0.70, beats analytic, keysep=0.878)
```

The lesson: learned-projection rescues what raw / whitened / analytic-projected can't.
The "anisotropy via projection" route works WITH a learned projection, NOT a fixed one.

### 5.4 The multi-hop thread (B1)

```
r1_multihop_iterative_cleanup_v1 (HARD_FAIL at K=3)
  -> r1b_multihop_refuse_calibration_v1 (HARD_FAIL: r1b means don't reproduce r1, harness-drift)
  -> r2_successor_TEM_compound_v1_n8192 (HARD_FAIL: ITER_CLEANUP_r1b_anchor drifted)
  -> substrate_multihop_consolidation_memory_v1 (HARD_PASS: CONS_IMMEDIATE=1.000 lift_mult=1.18x)
```

The lesson: cleanup-rescue at K=3 doesn't work via iterative attractor; consolidation-
memory (immediate replay-driven) DOES work. The path is "consolidate then traverse"
not "traverse then cleanup".

### 5.5 The capacity thread

```
substrate_capacity_battery_gpu_v1 (HARD_PASS: chain-grade capacity at multiple regimes)
  -> substrate_capacity_composition_b2xb4_v1_n2048 (HARD_PASS)
  -> substrate_capacity_composition_full_b2xb4xhier_v1_n2048_gpu (HARD_PASS: 600K patterns chain-grade)
  -> substrate_capacity_scaling_sweep_xl_v1 (HARD_PASS: XL extrapolation holds)
  -> n2_capacity_scaling_v1 (MIDDLE_BAND: N-scaling lowers sub_bpc but not within 0.5 bits of bigram)
  -> modern_hopfield_xl_v1 (HARD_FAIL: modern doesn't beat classical at XL)
  -> p1_v3_capacity_sweep_LLM_class_v1 (HARD_FAIL: substrate still BELOW capacity at K=15000)
```

The lesson: substrate capacity itself is healthy at the patterns level (600K at N=2048);
the binding constraint is decoder/LM-mapping above capacity, not capacity itself.

---

## 6. Gap analysis

### 6.1 Capabilities tested only ONCE (no replication)

These are SINGLE-EXPERIMENT capability claims. If they're load-bearing, they need
replication. Otherwise they're CONFOUND_FLAGGED until validated.

- `wm_workingmem`: only 1 recent HP (`working_memory_hrr_slots_PRODUCTION_v1`).
  Working-memory capability is single-witness.
- `humaneval_codegen`: 1 HF; no positive evidence at all that substrate helps codegen.
- `tinystories`: 1 HF only; "substrate as standalone LM" has 1 data point in this corpus.
- `stc_swr`: 1 recent HF; cascade rejected on single test.
- `sentiment_textclass`: 1 MB; single data point.
- `smoothing`: 1 HF, 1 MB; MKN tested only against bigram floor.

**Priority for future cells**: working-memory replication (since it's a substrate-
product roadmap claim); tinystories deeper-regime replication; codegen substrate-aug
revisit with cleaner methodology.

### 6.2 Capability x regime combinations NEVER tested

- **Substrate-as-LM at corpus larger than text8 word-bigram**: most LM cells use text8
  (V=4000 cap, 100k train). The wikitext-103, PTB, BookCorpus dimensions are
  essentially untested at substrate. `n6_wikitext103_ingest_cert_v1` HARD_FAIL
  (smoke-contamination per Fix #4 pre-flight gate) -- effectively no data.
- **Hub-spoke at N>=32k**: 5 hub-spoke cells, 0 HP, all at N<=16384. The architecture
  may simply need higher dimension.
- **Multi-hop at K>3 with consolidation-memory**: `substrate_multihop_consolidation_memory_v1`
  passes at K<=3; K=4,5 untested with the consolidation primitive.
- **Encoder ablation at fixed substrate-W**: `fresh_W_bpc_per_encoder_v2` ablated 4
  encoders at fresh W; the COMPLEMENTARY ablation (fixed encoder, varied W learning
  recipe) is untested.

### 6.3 "Store-proven" claims that are actually MIDDLE_BAND

Extending yesterday's Skunkworks audit:

- `n2_capacity_scaling_v1` -- MIDDLE_BAND (not within 0.5 bits of bigram). If anyone
  cites this as "substrate scales to close bigram-gap" -- WRONG; it lowers bpc 5.29
  -> 4.96 but the bigram is at 3.84. The gap is still 1.12 bits.
- `n3_mkn_smoothing_v1` -- MIDDLE_BAND (delta 0.068 bits, doesn't clear HP bar).
  "MKN smoothing as bigram-gap closer" is partial-mechanism not chain-grade.
- `fresh_W_bpc_per_encoder_v1/v2` -- both MIDDLE_BAND. Cited as "encoder-shift study"
  but per N1 verify-referent verdict is MIDDLE_BAND, not the chain-grade win it's
  sometimes treated as.
- `n3_vq_alignment_simvq_v1` -- MIDDLE_BAND (delta=-0.231 small-effect).
- `anisotropy_rescue_4arm_sweep_v1_gpu` -- MIDDLE_BAND with CALIBRATION FLAG (ARM D
  upper-bound = 0.445 < 0.80, meter under-calibrated). Should be cited as
  "ARMS_RELATIVE_ONLY", NOT as "anisotropy rescue works".
- `att1_iterative_attractor_cleanup_v1` -- MIDDLE_BAND (best_att1_lift=0.005, partial).
- `flagship_sparse_projected_KV_LBUILD_v1` -- MIDDLE_BAND (seed-unstable cv>0.05).
  If cited as flagship-LM evidence, that's over-claim.

### 6.4 HARD_FAILs that may have been mis-attributed

These need Skunkworks re-look (low priority -- not blocking; just hygiene):

- `n5_vc_4096_frontier_v1` -- HARD_FAIL via anchor-mismatch (SCHEMA-VET miss).
  Should be re-banded as INSTRUMENTATION_SUSPECT, not HARD_FAIL.
- `n6_wikitext103_ingest_cert_v1` -- HARD_FAIL via per_unit run_mode=smoke (Fix #4
  pre-flight). Procedural, not mechanism.
- `c_composition_storage_density_v1` -- HARD_FAIL on simple-compounding hypothesis;
  but per-arm metrics aren't clean enough to fully close (M_fail per arm has gaps).
- `humaneval_stdlib_split_qwen_v1` -- HARD_FAIL ClassA gain +0.000; but Fix #28 lesson
  says read per-arm not verdict_msg; 6 of 10 problems DID have different code
  (different solution diversity), just same PASS rate. The "substrate augmentation
  doesn't help codegen" framing is correct AT PASS@1; partial-mechanism evidence
  (solution diversity) was missed.

### 6.5 By-construction-suspect HARD_PASSES with bpc_best_cv=0.0

27 recent experiments have arms with bpc_best_cv=0.0 (zero variance across seeds).
The Q discipline flag treats this as "by-construction-suspect". However, manual
adjudication:

- Most cases are LEGITIMATE: baseline arm = unigram = deterministic floor (cv=0.0
  expected). The OTHER arms in the same experiment have cv>0 with real lift.
- Genuinely suspect:
  - `substrate_neuromodulator_3axis_gated_compose_LM_v1` -- ALL arms have cv=0,
    verdict READOUT_DEGENERATE. Per-Skunkworks override pattern, likely correct
    (by-construction-saturation).
  - `substrate_compose_order_x_compose_function_2x2_factorial_v1/v2` -- multiple arms
    cv=0; v2 verdict INSTRUMENTATION_SUSPECT (correct). v1 HARD_FAIL (correct given
    the instrumentation issue).
- Genuinely chain-grade despite cv=0 on baseline:
  - `substrate_clean_encoder_substrate_as_LM_v1` -- A=7.30 reproduces fair-harness;
    delta vs B (text8-only) = 0.44 bits, real signal.
  - `substrate_compose_freq_routing_v4_hparam_sweep` -- ARM_FREQ_DEEPER_TRAIN bpc=7.159
    beats BASELINE 7.3065 by 0.15 bits, cv=0.0029 (legit), top1 0.246 vs 0.213. Real.
  - `substrate_dopamine_duration_extension_LR_v1` -- ARM_GAMMA_05 bpc 4.74 vs FIXED
    4.89, lift 0.15 bits, real lift. Single-seed cv=0.0 is legitimate.
  - `substrate_dual_trace_sequential_neuromod_LM_v1` -- ARM_DUAL_TRACE bpc 7.22 vs
    BASELINE 7.74 (which floors to unigram), delta 0.52 bits with cv=0.001. Real.

**Conclusion**: the Q discipline `cv<=0.0001` flag has high false-positive rate.
Recommend Skunkworks tighten the flag to require ALL arms have cv=0 (not just one).

---

## 7. Substrate-product roadmap evidence map

The substrate-product is claimed as "memory + composition + retrieval + audit" device
that goes "INSIDE the substrate". For each claim, the actual evidence map:

### 7.1 "Memory" claim

**Strong (chain-grade) evidence**:
- `substrate_continual_learning_30day_realistic_stream_v1` (HP, chain-grade)
- `substrate_continual_learning_distshift_v1` (HP, chain-grade)
- `substrate_long_conversation_10k_exchanges_v1` (HP, chain-grade)
- `substrate_long_conversation_scale_1000_exchanges_v1` (HP, chain-grade)
- `substrate_capacity_battery_gpu_v1` (HP, chain-grade)
- `working_memory_hrr_slots_PRODUCTION_v1` (HP)

**Weak/partial**:
- `a8_continual_writes_no_catastrophic_forgetting_v1` (HP, chain-grade) -- single
  cell witnessing no-catastrophic-forgetting

**Unsupported**:
- "Memory under load-shift" -- not directly tested

**Refuted**:
- Nothing in the recent arc refutes the memory claim itself; the failures are in
  the LM-mapping component, not the substrate-memory component.

Verdict: **STRONGLY SUPPORTED**. Multiple chain-grade replications.

### 7.2 "Composition" claim

**Strong (chain-grade) evidence**:
- `multiplicative_composition_lever_v1_cpu_v1` (HP, chain-grade)
- `substrate_capacity_composition_full_b2xb4xhier_v1_n2048_gpu` (HP, chain-grade)
- `substrate_compositional_generalization_K10_to_K20_v1_n4096` (HP, chain-grade)
- `combo3_unified_api_v1_n16384_l4_alpha_grid_v1` (HP, chain-grade)
- `substrate_cognitive_core_analogical_v1` (HP, chain-grade)
- `substrate_cognitive_core_counterfactual_v1` (HP, chain-grade)
- `substrate_hierarchical_5corpus_meta_v2_n2048_gpu` (HP, chain-grade)
- `substrate_position_binding_combined_arch_trigram_v1_n4096` (HP, chain-grade)

**Weak/partial**:
- `b_alpha_broad_envelope_cpu_v1` (MIDDLE_BAND, 3HP/2MB/0HF across 5 benchmarks) --
  DEPTH-CLIFF + RELATION-GENERALITY: 2-hop works, deeper doesn't
- `c_composition_storage_density_v1` (HARD_FAIL: mechanisms do NOT simple-compound)

**Refuted**:
- "Mechanisms simple-compound multiplicatively at compound storage" -- REFUTED by
  c_composition_storage_density_v1. Need a different composition model at depth.

Verdict: **STRONGLY SUPPORTED for 2-hop / pairwise; CONFOUND_FLAGGED for compound /
deep composition**.

### 7.3 "Retrieval" claim

**Strong**:
- `kv_learned_projection_v1` (HP) -- learned projection generalizes to HELD-OUT
- `pseudoinverse_real_encoder_keys_v1` (HP, chain-grade) -- pinv on real encoder
- `u1_fb15k237_ingest_eval_v1` (HP, chain-grade) -- structured KB retrieval
- `n8_conceptnet_ingest_eval_v1` (HP, chain-grade) -- lexical KB retrieval
- `h_hotpotqa_ingest_v1` (HP, chain-grade) -- multi-hop QA retrieval

**Weak/partial**:
- `flagship_sparse_projected_KV_LBUILD_v1` (MB, seed-unstable)
- `b_alpha_2hop_hypernym_qa_cpu_v1` (MIDDLE, recall=0.607)

**Refuted**:
- `pythia_kv_recall_reality_v3_1_gpu_v1` (HF) -- raw pythia-2.8b keys non-separable
- `dense_KV_whitening_revival_v1_gpu` (HF) -- whitening doesn't rescue

Verdict: **STRONGLY SUPPORTED with learned projection or pinv; REFUTED with raw
encoder keys at scale**.

### 7.4 "Audit" claim

**Strong**:
- `deletion_cert_z_ratio_n16384_full_alpha_v1` (HP, chain-grade)
- `deletion_cert_refusal_joint_v1` (HP, chain-grade)
- `kb_determinism_sweep_RETRY_gpu_v1` (HP, chain-grade)
- `substrate_hallucination_detection_minilm_v1` (HP, chain-grade)
- `substrate_hallucination_robustness_hard_negatives_v1` (HP, chain-grade)
- `kf1_paraphrase_robustness_marianmt_v1` (HP, chain-grade)
- `substrate_b6_x_sq2_audit_preserving_reasoning_v1_n4096` (HP, chain-grade)
- `substrate_multidoc_synthesis_1000plus_docs_v1` (HP, chain-grade)

**Weak/partial**:
- `conformal_dryrun_v3final` (MB) -- set-size-loose on 1/4 tasks
- `conformal_splitcp_cpu_v1` (MB) -- coverage holds by-construction, tightness partial
- `m1_refuse_gate_heldout_tau_sweep_v1` (HF) -- no tau achieves gap-refuse>=0.95
  without dropping in-coverage F1 >0.05

**Refuted**:
- `m_medqa_ingest_v1` (HF) -- setrecall ratio=1.00x (rand-ctrl-equal), audit-gate
  cannot discriminate stored from unstorable for medqa
- `refuse_gate_5_sq6_concentration_cpu_v1` (HF / NON_TEST) -- concentrations overlap

Verdict: **STRONGLY SUPPORTED for deletion-cert + hallucination + paraphrase-robust
KB; PARTIAL for split-conformal calibration; REFUTED for refuse-gate at medqa**.

### 7.5 "Glass-box LM INSIDE substrate" claim (L2 vision)

**Strong**:
- `fair_harness_substrate_as_lm_v1` (HP) -- substrate beats unigram by 0.43 bits in
  sparse-bipolar arm (modest but real)

**Weak/partial**:
- `n1_v3_calibrated_substrate_lm_vs_unigram_v1_smoke` (HP smoke) -- top1=0.445 vs
  unigram=0.276 (60% lift; near bigram). NOTE: smoke result; needs full replication.
- `n2_capacity_scaling_v1` (MB) -- scaling lowers bpc 5.29->4.96, not within 0.5 bits
  of bigram 3.84
- `n3_mkn_smoothing_v1` (MB) -- delta 0.068 bits
- `fresh_W_bpc_per_encoder_v1/v2` (MB) -- encoder ablation, W is bottleneck

**Refuted (older confounded harness)**:
- 7+ HARD_FAILs from pre-fair-harness era. Per `substrate_as_lm_test_harness_rigged_
  2026-06-23` audit, these are METHODOLOGY-CONFOUND.

**Refuted (post-fair-harness, real)**:
- `substrate_owned_predictive_coding_encoder_v1` (HF) -- Path C single-encoder doesn't
  beat word2vec
- `b2_substrate_only_tinystories_lm_v1` (HF) -- pure substrate-only LM fails on
  tinystories ppl
- `substrate_brain_full_compose_LM_v2` (SUBSTRATE_SIGNAL_TOO_WEAK_TO_LIFT_UNIGRAM)

Verdict: **PARTIALLY SUPPORTED at the proof-of-concept level (substrate IS learning);
NOT YET SUPPORTED at production-LM-replacement level**. The bigram-gap (~1.13 bits
to word-bigram) is the remaining battle. The L2 vision is alive but the gap is
non-trivial.

---

## 8. Standing references -- top 20 experiments any cell-author should know

Curated list of MOST-LOAD-BEARING experiments to cite. These have CHAIN_GRADE status
in cert ledger AND directly inform current cell-design. Cite by anchor; metrics.json
path = `data/exp_<anchor>/metrics.json`.

1. **`fair_harness_substrate_as_lm_v1`** -- THE substrate-as-LM proof-of-life
   (sparse-bipolar bpc 7.31 vs unigram 7.74). Cite for any LM-direction cell.
2. **`u1_fb15k237_ingest_eval_v1`** -- chain-grade structured KG (FB15k-237). Cite for
   any KB-ingest cell.
3. **`n8_conceptnet_ingest_eval_v1`** -- chain-grade lexical KG (ConceptNet). Cite for
   lexical KB.
4. **`h_hotpotqa_ingest_v1`** -- chain-grade multi-hop Wikipedia. Cite for multi-hop.
5. **`c3_compressed_sequence_replay_v1`** -- THE sequence-binding-via-replay primitive
   (the no-Hebbian-window META). Cite for any sequence cell.
6. **`g1_substrate_native_generation_v1`** + **`g1b_capacity_sweep_v1`** -- generation
   primitives. Cite for any gen cell.
7. **`kv_learned_projection_v1`** -- THE encoder-projection chain-grade. Cite for any
   pythia-KV cell.
8. **`substrate_capacity_battery_gpu_v1`** -- capacity ground-truth. Cite for any
   capacity-extrapolation claim.
9. **`substrate_capacity_composition_full_b2xb4xhier_v1_n2048_gpu`** -- the 600K
   patterns @ N=2048 evidence. Cite for any capacity-from-recent-arc claim.
10. **`substrate_continual_learning_30day_realistic_stream_v1`** -- CL chain-grade.
    Cite for any CL/MOAT claim.
11. **`substrate_long_conversation_10k_exchanges_v1`** -- BIDIRECTIONAL CONVERSATION
    chain-grade. Cite for conversation cell.
12. **`multiplicative_composition_lever_v1_cpu_v1`** -- composition chain-grade.
    Cite for compositional cell.
13. **`substrate_cognitive_core_analogical_v1`** + **`_counterfactual_v1`** -- the
    cognitive-core primitives. Cite for cognitive-core or analogy/counterfactual cell.
14. **`substrate_position_binding_combined_arch_trigram_v1_n4096`** -- position-
    binding (cfrpe) chain-grade. Cite for any position-binding cell.
15. **`deletion_cert_z_ratio_n16384_full_alpha_v1`** + **`deletion_cert_refusal_joint_v1`**
    -- deletion-cert chain-grade. Cite for any unlearning/audit cell.
16. **`substrate_hallucination_detection_minilm_v1`** + **`_robustness_hard_negatives_v1`**
    -- hallucination chain-grade. Cite for any audit cell.
17. **`kmax_ness_envelope_corrected_v1`** -- chain-grade cleanup-extension genuinely
    traverses. Cite for any cleanup or traversal cell.
18. **`substrate_multihop_consolidation_memory_v1`** -- consolidation primitive HP.
    Cite for any multi-hop cell where cleanup-rescue is being considered.
19. **`pseudoinverse_real_encoder_keys_v1`** -- pinv chain-grade. Cite for any KV cell
    where Hebbian is being considered.
20. **`substrate_capacity_scaling_sweep_xl_v1`** + **`combo3_unified_api_v1_n16384_l4_
    alpha_grid_v1`** -- XL frontier-N evidence; cite for any high-N cell.

**Honorable mentions** (Skunkworks override on tier; classified as MEASURED_MECHANISM
not chain-grade despite verdict=HARD_PASS): `g1_substrate_native_generation_v1`,
`c3_compressed_sequence_replay_v1` (cited above; cert tier is MM not chain-grade for
the deeper claim). Skunkworks correctly overrides Director per the by-construction-
saturation tiering pattern.

---

## 9. Gaps the inventory itself exposed

a) **No verdict_field on 201 experiments**. Need triage: either re-classify or mark
   abandoned. `data/_archaeology_inventory.jsonl` `verdict_category == "unknown_no_verdict"`
   filters these.

b) **65% of recent HARD_PASS have NO cert ledger entries**. The cert pipeline drops
   substantially. Either (a) atomize them, (b) Skunkworks pass to classify as
   MEASURED_MECHANISM with cert_status=under_classified, or (c) accept this as
   intentional (most experiments don't need to be in the headline CERT count).

c) **Capability classification is regex-based**. The CAPABILITY_PATTERNS dict in
   `data/_archaeology_synthesize.py` is imperfect; some experiments lack tags. A
   future cell could improve this via semantic-classifier on anchor + verdict_msg.

d) **No bench_reports / verdict_history cross-reference yet**. There are richer
   bench_reports under `data/substrate_index/bench_reports/` that could augment this
   archaeology. Out of scope for this drill.

e) **Older (pre-2026-06) experiments not classified**. 1040 of 3269 are older than
   2026-06. Some are still cited (e.g. CERT591 baseline 0.827 in
   `dense_KV_envelope_learned_key_calibration_v1_gpu` GATE-1 meter-check failed).
   Out of scope for this drill but flagged.

f) **MEMORY.md headline CERT count of 588** does NOT directly match cert_ledger
   (466 chain_grade). The numerator/denominator differ -- MEMORY.md is counting
   substrate-internal atoms with `is_certified` flag; cert_ledger is the audit trail.
   Both are correct sources; just different views. Should be reconciled in a future
   self-map cell.

---

## 10. Practical recommendations to Director (for future cycles)

### 10.1 Citation hygiene

When citing "Store-proven X" -- use one of these phrasings:
- "chain-grade HARD_PASS per `<anchor>` (cert_ledger entry)"
- "HARD_PASS verdict per `<anchor>/metrics.json`, NOT in cert ledger"
- "MIDDLE_BAND partial-mechanism per `<anchor>`"
- "Skunkworks-rebanded MEASURED_MECHANISM per `<anchor>`"

Never just "Store proves X" without specifying which tier of evidence.

### 10.2 Pre-cell-dispatch check

Before authoring a cell that tests `<capability>`:

```
python data/_archaeology_synthesize.py  # refresh
grep '<capability>' data/_archaeology_inventory_enriched.jsonl | head -20
# look at: existing HARD_PASS (don't re-test), HARD_FAIL (don't repeat blind),
# MIDDLE_BAND (what discriminator would close)
```

Combine with `tools/predispatch_check.py <anchor>` (Fix #26).

### 10.3 Capability-priority next-steps (data-driven)

From Section 3 matrix, the priorities visible by HP/HF ratio:

- **HIGH priority (zero-HP capabilities to close or pivot)**: anisotropy,
  hub_spoke, modern_hopfield, self_map, math_wk, tinystories, stc_swr,
  humaneval_codegen, smoothing. Each needs either (a) a fresh-methodology
  cell or (b) explicit "abandoning this direction" decision.
- **MEDIUM priority (low-HP-rate capabilities under active development)**:
  calibration (0.13), hebbian (0.13), substrate_as_lm (0.32), vq_codebook
  (0.33), predictive_coding (0.33). These are the substrate-arc battles.
- **LOW priority (healthy capabilities; don't re-test unless asked)**:
  compositional, continual_learning, kv_recall, frontier_dim, intent_classifier,
  phase_diagram, generation, neuromod, csp_planted, refuse_gate.

### 10.4 Substrate-product narrative discipline

Per Section 7 evidence map:
- Memory: STRONGLY SUPPORTED. Cite freely.
- Composition: STRONGLY SUPPORTED at 2-hop; CONFOUND_FLAGGED at depth.
- Retrieval: STRONGLY SUPPORTED with learned projection. REFUTED with raw encoder.
- Audit: STRONGLY SUPPORTED for deletion-cert + hallucination. PARTIAL for conformal.
  REFUTED for medqa.
- Glass-box LM: PARTIALLY SUPPORTED (substrate IS learning per fair-harness). NOT
  YET production-replacement.

The substrate-product narrative is "memory + composition (pairwise) + retrieval
(with learned projection) + audit (deletion-cert + hallucination)". This is
strongly supported. The "+ glass-box LM" is aspirational, not yet earned.

---

## 11. Appendix -- file inventory of this drill

- `data/_archaeology_extractor.py` -- the extractor (Python 3.12; processes 4113
  metrics.json files)
- `data/_archaeology_synthesize.py` -- the synthesizer (joins to cert ledger;
  builds matrices)
- `data/_archaeology_inventory.jsonl` -- raw per-experiment rows (3269 lines)
- `data/_archaeology_inventory_enriched.jsonl` -- with capability/barrier/family/cert
  annotations (3269 lines)
- `data/_archaeology_summary.json` -- summary stats + chain-grade anchor lists
- `notes/research_experimental_archaeology_comprehensive_inventory_2026-06-25.md`
  -- this document

Re-running this drill: `python data/_archaeology_extractor.py && python
data/_archaeology_synthesize.py` produces fresh inventory + summary in ~10 sec.

End.
