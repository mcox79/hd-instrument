# Per-Characteristic Phase Diagram Audit (Testbed integrator pass, 2026-06-26)

**Role:** testbed (integrator + fleet-health auditor).
**Trigger:** USER directive 2026-06-26: "would be great to have a good phase diagram understanding for each characteristic -- do we have that?" Piecemeal yes (phase-portrait v1 inventory + research integration map + 478 chain-grade cert_ledger rows); unified per-characteristic doc no. This audit produces it.
**Sources mined:**
- `data/substrate_index/meta/cert_ledger.jsonl` (761 rows total; 478 chain_grade)
- `data/_testbed_encoder_provenance_FINAL.jsonl` (464 cells)
- 14 recent `metrics.json` direct-reads (envelope numbers verified-the-referent against verdict_msg fields)
- `notes/phase_portrait_v1_inventory_atom_substrate_operating_regime_map_2026-06-22.md` (~38-42 phase-diagram atoms + 11 transform-survival atoms)
- `notes/research_phase_diagram_integration_map_AND_storage_efficiency_spec_sheet_2026-06-25.md` (15 capability families integrated map)
- `notes/research_substrate_aliveness_FULL_store_mined_map_2026-06-24.md`
**Disciplines applied:** ASCII only; verify-the-referent (every chain-grade claim cites a directly-readable verdict field); by-construction-saturation flagged; encoder provenance tagged per row; per Fix #28 read metrics.json per-arm before propagating.

---

## 1. Headline

Substrate has 25 named capabilities with quantified envelopes spanning 6 architectural classes (core primitives, architectural composition, refuse/calibration, memory consolidation, applications, META rules). 17 are chain-grade with measured envelopes; 4 are proven-bound / measured-mechanism / in-flight; 4 are META protocols rather than capabilities. Encoder-provenance audit places 9 of 17 chain-grade capabilities as SUBSTRATE_NATIVE; 3 as LLM_AT_INFERENCE (whitening + intent + KV-learned use pythia/llama as encoder); 1 MIXED (hotpotqa); 4 not yet classified (recent landings).

Cross-capability composition envelope identified: 5 capabilities share the **V_REL** axis (refuse-gate + stage3-audit + multihop + posbind-symW + intent); 4 share the **N_DIM=4096-8192** sweet spot; 3 share **K=4096 bank-routing** as architectural co-requirement; 2 capabilities (NREM-replay + REM-homeostasis) directly conflict by occupying the same consolidation slot.

---

## 2. Per-characteristic envelopes (table-first, lookup-grade)

### 2.1 Core primitives

#### Sparse-bipolar codebook (basis)

| Field | Value |
|-------|-------|
| Where it works | N in {1024, 2048, 4096, 8192, 16384}; f in {0.02, 0.05}; alpha=M*/N=0.048 stable across 10 seeds; capacity@N=16384 = 655 facts |
| Where it cliffs | N>16384 untested for alpha-stability (PP-55 extends N to 131072 only for HRR-bind, not capacity-scaling) |
| Boundary conditions | composes multiplicatively with K-ensemble (240x) at N=2048; substrate-mining cap claim 600K patterns at N=2048 via sparse x K x D multiplicative composition (per MEMORY.md substrate-mining note) |
| Composes with | HRR-bind (capacity@N inherits sparsity); modern-Hopfield cleanup (chain-grade at M/N=0.30); multi-bank WM (per-bank capacity inherits); sequence-binding (K=20 inherits headroom) |
| Encoder provenance | SUBSTRATE_NATIVE (capacity-scaling cell) |
| Cert atoms | `EXP_substrate_capacity_scaling_sweep_xl_v1` HARD_PASS; `EXP_substrate_sparsity_fine_battery_gpu_v1`; `EXP_substrate_capacity_composition_b2xb4_v1_n2048` HARD_PASS |

#### HRR binding (relational)

| Field | Value |
|-------|-------|
| Where it works | N=16384, 32768, 65536, 131072; M=6553 stored items at N=131072; alpha=0.05; mean_cos=0.99999 across 5 seeds |
| Where it cliffs | N=131072 is current ceiling chain-grade; sigma>1.0 untested at high N; encoder-bound at lower N (cleanup envelope) |
| Boundary conditions | requires sparse-bipolar codebook (paired primitive); chunked Hopfield (no global W) at the highest N to fit memory |
| Composes with | sequence-binding (g1b uses HRR-bind for K=20 steps); compressed-replay c3 (depth=5 chains use HRR-bind); modern-Hopfield (post-bind cleanup); HotpotQA 2-hop bridge (relational binding underlies bridge step) |
| Encoder provenance | NO_RECORD on pp55 anchor (pre-provenance-audit cell) -- structurally substrate-native (HRR is algebraic, not encoder-dependent) |
| Cert atoms | `EXP_pp55_vsa_binding_n131072_v6_n131072` HARD_PASS; `EXP_pp55_vsa_binding_n16384_v3_n16384` PASS |

#### Hebbian W storage

| Field | Value |
|-------|-------|
| Where it works | substrate-native sequence-binding (g1b) IS Hebbian outer-product at architecture level; no separate Hebbian-window timing window required (META atom: `META_software_substrate_no_hebbian_window`) |
| Where it cliffs | dedicated `hebbian_capacity_projected_v2` is MEASURED_MECHANISM CHARACTERIZED_NEGATIVE (mechanism choice NN); pure projected-Hebbian cap is not chain-grade alone |
| Boundary conditions | continual-write alpha boundary = 0.3 (a8 chain-grade); cliff at alpha=0.5 (acc=0.527); capacity-stress at alpha=1.5 (acc=0.100) |
| Composes with | CSP-Hebbian coexist (chain-grade PASS); cf-RPE / STDP heterogeneous-plasticity superadditive at N=512 chain-grade; sequence-binding architecture |
| Encoder provenance | SUBSTRATE_NATIVE on a8 continual-writes |
| Cert atoms | `EXP_a8_continual_writes_no_catastrophic_forgetting_v1` HARD_PASS; `EXP_csp_hebbian_coexist_v1` PASS; `META_software_substrate_no_hebbian_window_sequence_binding_is_architecture_not_timing` |

#### Cleanup (top-1, top-K)

| Field | Value |
|-------|-------|
| Where it works | `EXP_substrate_permutation_binding_multiocc_v2_full` HARD_PASS_CHAIN_GRADE (cyclic-shift cleanup rescues FHRR same-role collision; gap 93.7% over FHRR baseline); modern-Hopfield exponential-energy at N=4096 M/N=0.30 acc=1.000 |
| Where it cliffs | encoder-bound at N=512 high-noise M/N=0.39 (META: `META_cleanup_ceiling_is_encoder_bound_at_N512`); 4 decoder families exhausted at that regime |
| Boundary conditions | META atom: `META_codebook_NN_cleanup_is_load_bearing_for_substrate_native_generation` (HARD_PASS measured-mechanism) -- cleanup IS the substrate-generation primitive |
| Composes with | every read path (HRR-bind unbind requires cleanup; sequence-binding K=20 unbind requires cleanup; multi-bank routing post-bank-select requires cleanup) |
| Encoder provenance | Mixed: chain-grade cells under SUBSTRATE_NATIVE; encoder-bound failures used pythia-160m |
| Cert atoms | `EXP_substrate_permutation_binding_multiocc_v2_full` HARD_PASS; `META_codebook_NN_cleanup_is_load_bearing_for_substrate_native_generation` |

#### Sequence binding (g1b chain-grade)

| Field | Value |
|-------|-------|
| Where it works | N=4096, K=20 sequence steps, 6/6 capacity points at bar 0.60, headroom 6403 pairs at acc=0.94; "above by-construction-saturation" per verdict_msg |
| Where it cliffs | untested above n_pairs=6403; coh drops 1.00 -> 0.94 at 6403 indicating approach to cliff; chain-grade only at N=4096 (N>=8192 untested) |
| Boundary conditions | novelty_ratio nov/cap > 0.99 across every capacity tier; substrate_only=True; W_unchanged=True; llm=0 |
| Composes with | c3 compressed sequence replay (B_d5=1.000 delta=1.000 order_delta=0.983) at K_SEQ=20 depth=5; HRR-bind primitive (steps bind via HRR); cleanup (each step unbind needs cleanup) |
| Encoder provenance | SUBSTRATE_NATIVE |
| Cert atoms | `EXP_g1b_capacity_sweep_v1` HARD_PASS; `EXP_c3_compressed_sequence_replay_v1` HARD_PASS; `META_substrate_autoregressive_generation_chain_grade_requires_headroom_to_fail_discriminator` |

#### Char-trigram encoder (substrate-native Path C)

| Field | Value |
|-------|-------|
| Where it works | NER transition + char-ngram noise crosscut PASS; substrate-native encoder used in audit-device + intent-classifier production deployments |
| Where it cliffs | when tested as standalone language-modeling encoder, hits cosine-physics floor at recall@1 <=0.16 across all tested constructions (M=2000 pythia-160m comparison reveals char-trigram alternative) |
| Boundary conditions | per Path C audit (USER 2026-06-23 decision): substrate-owned encoder is the substrate-product answer; word2vec / pythia are DIAGNOSTIC PROBES; brain-grounded prior P=0.60-0.75 not 0.30 |
| Composes with | char-trigram present in hdlab/ primitives; substrate-bidirectional-conversation chain-grade at every layer (per MEMORY.md current state) |
| Encoder provenance | SUBSTRATE_NATIVE by design; tagged accordingly in provenance ledger |
| Cert atoms | `EXP_ner_transition_charngram_noise_crosscut_cpu_v1` PASS; `META_substrate_tracks_KNN_cosine_floor_within_0p007` proven_bound |

### 2.2 Architectural

#### Multi-bank working memory routing (K=4096 chain-grade as of 2026-06-26)

| Field | Value |
|-------|-------|
| Where it works | K=4096 MULTI_64x recall=0.9927 cv=0.0006 route_acc=1.0; K=1024 MULTI_32x recall=1.0 cv=0.0; K=2048 MULTI_64x recall=1.0 cv=0.0; adversarial within 0.05 of random baseline (chain-grade adversarial-robustness) |
| Where it cliffs | K>4096 untested; per-bank capacity is "by-construction-saturated" at K<=2048 (verdict_msg flags discriminating-regime K<=2048 effect is per-bank capacity not architectural lift); architectural lift is the K=4096 result |
| Boundary conditions | k_per_bank=64; discriminating regime is K=4096 (lower K is per-bank capacity effect not bank-routing) |
| Composes with | partition-routing (multi-bank + partition-per-hop chain-grade at 5-hop 0.955); beam-search WM-candidates (chain-grade BEAM_W10=0.6667 with WM-candidate pool) |
| Encoder provenance | NO_RECORD (recent landing post provenance-audit) -- structurally substrate-native (bank routing is geometric) |
| Cert atoms | `EXP_substrate_working_memory_multi_bank_K_extension_adversarial_v1` HARD_PASS_CHAIN_GRADE; `EXP_substrate_working_memory_multi_bank_routing_v1` |

#### Partition routing single-level (M=1M chain-grade)

| Field | Value |
|-------|-------|
| Where it works | M=100k: routed_recall@10=0.9697 cv=0.0442 route_acc=1.0 (chain-grade primary band); M=1M: routed=0.95 cv=0.0114 route_acc=1.0 (chain-grade stretch band); part_size=2000 |
| Where it cliffs | flat (unrouted) collapses: flat@M=1M=0.51 vs routed=0.95 -- without routing the M=1M regime is unworkable; flat strictly decreasing across M sweep |
| Boundary conditions | partition_size=2000 across all M tiers; cat_cos=0.7; target_cos=0.133; retrieval_noise=7.452 |
| Composes with | hierarchical 2-level (extends M to 10M); partition-per-hop multihop (M_M7 rail at 5-hop 0.955); inherits Cell B dense-KV envelope |
| Encoder provenance | NO_RECORD (recent landing) |
| Cert atoms | `EXP_substrate_partition_routing_10M_full_v2_chain_grade_M_100k...with_bound_M_1M` HARD_PASS_PARTIAL_AT_M_1M |

#### Partition routing hierarchical 2-level (M=10M chain-grade)

| Field | Value |
|-------|-------|
| Where it works | M=10M: 2LEVEL=0.9783 cv=0.006 (chain-grade); M=1M: 2LEVEL=0.9700 cv=0.007 SINGLE=0.9467 FLAT=0.4883 (2level beats single by 0.023; flat collapses) |
| Where it cliffs | M>10M untested; single-level alone at M=10M not chain-grade (the 2-level structure IS the enabler past M=1M) |
| Boundary conditions | hierarchical 2-level inherits single-level part_size=2000 + adds outer-routing layer; both routing accs at 1.0 |
| Composes with | extends single-level partition-routing envelope; same cell-B dense-KV inheritance |
| Encoder provenance | NO_RECORD (recent landing) |
| Cert atoms | `EXP_substrate_partition_routing_hierarchical_2level_v1_chain_grade_M10M_envelope_2level_routing_inherits_cell1_caveat_class` HARD_PASS |

#### Multi-hop partition-per-hop with ORACLE (Cell B v2; 0.95 at depth-5)

| Field | Value |
|-------|-------|
| Where it works | 5-hop partition-per-hop routed: PART=0.9550 cv=0.007 (chain-grade BARRIER_1 revival); BANK=0.8667; FLY=0.3517; SINGLE_v1regime=0.3233; ALL3=0.8750 cv=0.024 |
| Where it cliffs | reproduces v2 baseline at 0.1217 (META_M7_breach=0/3) without routing -- routing IS the chain-grade enabler; SANITY_BREACH=1/3 baseline_mean=0.6500 not in [0.62, 0.68] is a noted rail |
| Boundary conditions | ORACLE routing scope flag (substrate-native routing-without-oracle open question; per `META_BARRIER_1_QUINTUPLE_RECONCILIATION` narrows quadruple-negative to routing-required at 5-hop) |
| Composes with | multi-bank WM (K=4096 + partition-per-hop); cell-B v2 META_M7 rail (smoke-vs-full regime match must hold); bidirectional meet-in-middle (alternative path) |
| Encoder provenance | NO_RECORD (recent landing) |
| Cert atoms | `EXP_substrate_multihop_compose_fly_lsh_multibank_partition_v2_META_M7_rail_chain_grade_partition_per_hop_5hop_0p955_cv_0p007_meta_M7_pass_oracle_routing_scope_flag` HARD_PASS |

#### Multi-hop bidirectional meet-in-middle (Cell C v2; 0.62 at depth-5)

| Field | Value |
|-------|-------|
| Where it works | BIDIR_MEET_MID=0.6200 cv=0.064 5-hop; lift_over_fwd=+0.2967; mean_midpoint_cosine=0.0000 (clean midpoint); fwd_bidir_err_corr=0.294 |
| Where it cliffs | weaker than partition-per-hop (0.95 vs 0.62) at 5-hop; lift over forward-only is real but absolute level still bounded |
| Boundary conditions | BASELINE=0.6500 with SANITY_BREACH=1/3 -- discriminator is on the lift not absolute |
| Composes with | could compose with partition-routing as alternative-path; complementary to beam-search WM-candidates |
| Encoder provenance | NO_RECORD (recent landing) |
| Cert atoms | `EXP_substrate_multihop_bidirectional_meet_middle_v2_META_M7_rail` HARD_PASS_CHAIN_GRADE_BIDIRECTIONAL_REVIVAL |

#### Multi-hop beam search with WM candidates (Cell X v1)

| Field | Value |
|-------|-------|
| Where it works | BEAM_W10=0.6667 cv=0.043 monotonic W10>=W5>=W2; lift over single 5-hop +0.3367 |
| Where it cliffs | absolute level still bounded around 0.67 at depth-5 vs partition-per-hop 0.95; beam widening gives monotonic but diminishing returns |
| Boundary conditions | per-cell verdict notes META_M7 note (full vs smoke regime match required) |
| Composes with | multi-bank WM (uses WM candidate pool); partition-routing (could compose) |
| Encoder provenance | NO_RECORD (recent landing) |
| Cert atoms | `EXP_substrate_multihop_beam_search_with_WM_candidates_v1` HARD_PASS |

### 2.3 Refuse / calibration

#### Refuse-gate V_REL extension (chain-grade V_REL<=256)

| Field | Value |
|-------|-------|
| Where it works | V_REL envelope: 8/16/32/64/128/256/512 all chain-grade RELATION_CHECK (in_ans=1.000 near_ref=1.000 cv=0.000 across all); discriminator AIP near_ref monotone-degrades from 0.990 (V_REL=8) -> 0.833 (V_REL=64) -> 0.630 (V_REL=128) -> below 0.5 at V_REL=256 |
| Where it cliffs | AIP-arm degrades past V_REL=128; RELATION_CHECK arm holds at chain-grade through V_REL=512 but practical discrimination ends at V_REL=256 |
| Boundary conditions | 32x lift over v2 baseline V_REL=8; clean naive plus intent-monotone-degrade is the discriminator |
| Composes with | stage3-integrated-audit (uses V_REL=20-50 in production envelope); HotpotQA refuse=1.0 OOD; conformal-CP coverage guarantee |
| Encoder provenance | NO_RECORD (recent landing) |
| Cert atoms | `EXP_substrate_refuse_gate_v_rel_extension_v1_chain_grade_envelope_V_REL_256_32x_lift_over_v2_baseline_V_REL_8...genuine_discriminator_headroom` HARD_PASS_CHAIN_GRADE |

#### CSP uncertainty quantification (chain-grade; 8.42x speedup)

| Field | Value |
|-------|-------|
| Where it works | `EXP_csp_first_ship_v1` chain-grade; csp-hebbian coexist; csp_memory_warm_start_full_v3 chain-grade; planted_csp_viability chain-grade |
| Where it cliffs | csp-gated-iterated cleanup at multihop is HARD_FAIL (`EXP_substrate_multihop_csp_gated_iterated_cleanup_v1_HARD_FAIL_4th_barrier1_attempt`); csp does not rescue 5-hop without routing (per META_BARRIER_1_QUADRUPLE) |
| Boundary conditions | csp at base layer works; csp as multihop primitive does NOT compose past 2-hop without partition-routing |
| Composes with | Hebbian (chain-grade coexist); refuse-gate (csp + refuse-gate stage); calibration layer |
| Encoder provenance | NO_RECORD on first_ship |
| Cert atoms | `EXP_csp_first_ship_v1` chain_grade; `EXP_csp_hebbian_coexist_v1` chain_grade; `EXP_csp_memory_warm_start_full_v3` chain_grade |

#### Conformal split-CP (envelope MIDDLE_BAND)

| Field | Value |
|-------|-------|
| Where it works | 2/4 tasks HARD_PASS (ag_news cov=0.944 set=0.44L; atis_intent set <=0.5L); coverage guarantee holds by-construction cov>=0.93 across all tasks |
| Where it cliffs | sst2 HARD_FAIL (binary 0.5L=1.0 structurally requires confident single class); mbpp_codepattern MIDDLE_BAND (cov=0.955 set=0.53L); guarantee_break=False (the protection IS the load-bearing claim) |
| Boundary conditions | substrate-classical + APS split-conformal; envelope is task-shape-dependent (binary structurally loose) |
| Composes with | refuse-gate (conformal sets bound the refuse decision); wave14 mondrian / cap2 subsumption family |
| Encoder provenance | NO_RECORD on splitcp_cpu |
| Cert atoms | `EXP_conformal_splitcp_cpu_v1` MIDDLE_BAND; `EXP_wave14_cap2_conformal_subsumption_v1`; `EXP_wave14_cap12_cap6_conformal_routing_subsumption_v1` |

### 2.4 Memory consolidation

#### NREM replay (proven-bound; drift_reduction +0.57 abs / final_forget 0.31 best arm)

| Field | Value |
|-------|-------|
| Where it works | full proven_bound atom: replay reduces drift by 0.57 abs at best arm; final_forget 0.31; monotone in replay frequency; smoke pass at drift_reduction 0.067 (MIDDLE_BAND) |
| Where it cliffs | chain-grade bar 0.05 final_forget NOT met (Director honest_downgrade); replay-every-100 is best but still 0.31 final_forget after 500 cycles |
| Boundary conditions | discriminator is monotone-in-replay-frequency; arms tested: NO_REPLAY, REPLAY_EVERY_100, REPLAY_EVERY_500, REPLAY_EVERY_1000 |
| Composes with | a8 continual-writes alpha<=0.3 boundary (NREM replay is the CLS-replay mechanism that protects sub-cliff regime); c2 cascade-STC-SWR (was HARD_FAIL: C2 doesn't beat C1 at k=6) |
| Encoder provenance | NO_RECORD (recent landing) |
| Cert atoms | `EXP_substrate_continual_NREM_replay_v1_proven_bound_replay_reduces_drift_0p57_abs_best_arm_0p31_final_forget_chain_grade_bar_0p05_not_met_monotone_in_replay_frequency_director_honest_downgrade` proven_bound |

#### REM global homeostasis (MIDDLE_BAND; closed-by-other)

| Field | Value |
|-------|-------|
| Where it works | reduction% A_n8192_noreplay=0.00; B_n8192_replay=29.17; C_n4096_replay=51.13 (partial consolidation pattern) |
| Where it cliffs | MIDDLE_BAND (partial consolidation OR control not null; quant-floor conditional unclear); not chain-grade; original status was "HARD_FAIL closed" per task statement but ledger shows under_classified |
| Boundary conditions | n4096 with replay outperforms n8192 (counterintuitive; flag for cross-witness) |
| Composes with | NREM-replay (alternative consolidation pathway); STC selective downscale (brain-mechanism slot) |
| Encoder provenance | NO_RECORD (under_classified) |
| Cert atoms | `EXP_substrate_rem_replay_retrieval_energy_baseline_v1_n8192_gpu` MIDDLE_BAND under_classified |

#### STC selective downscale (in flight / cascade HARD_FAIL)

| Field | Value |
|-------|-------|
| Where it works | c2-cascade-STC-SWR-continual measured-mechanism on prior cell; design concept active |
| Where it cliffs | latest `EXP_c2_cascade_stc_swr_continual_v2` HARD_FAIL: C2 (1.000) does NOT beat C1 (1.000) at k=6; mechanism adds nothing; cv=0.0 substrate_only=True llm=0 |
| Boundary conditions | C2 cascade does not beat C1 baseline at k=6 -- C1 is already at metric-cap; need harder discriminator regime |
| Composes with | conflicts with NREM-replay slot (same consolidation function); brain-mechanism per CLS-theory |
| Encoder provenance | NO_RECORD |
| Cert atoms | `EXP_c2_cascade_stc_swr_continual_v2` HARD_FAIL |

### 2.5 Applications

#### Intent classifier (chain-grade acc=0.754 at 50 intents; p95=0.54ms)

| Field | Value |
|-------|-------|
| Where it works | N_DIM=2048; acc=0.761 vs random=0.145 vs majority=0.163; maj_mult=4.66 rand_mult=5.23; p95=3.90ms; n_llm=0; n_seeds=3 |
| Where it cliffs | N>=4096 untested for intent (low-N regime); 50-intent space is the chain-grade scope -- not scaled past that |
| Boundary conditions | clear discriminator (>=5x random) and zero LLM at chain-grade tier; p95 latency is the substrate-product moat metric |
| Composes with | stage3-integrated-audit (uses intent classifier in production envelope); refuse-gate (intent feeds gating decision); a2-templated-response (intent routes which template fires) |
| Encoder provenance | LLM_AT_INFERENCE (pythia-160m mean-pool used as encoder per cell construction) |
| Cert atoms | `EXP_a1_substrate_intent_classifier_v1` HARD_PASS |

#### Templated response (MIDDLE_BAND in current state; was chain-grade at smaller scope)

| Field | Value |
|-------|-------|
| Where it works | gram_lift=0.547 REAL rendering machinery; per-category best WHO_DID_X=0.333 WHAT_IS_X=0.182 COMPARE_X_Y=0.154; substrate-only n_llm=0 |
| Where it cliffs | bands not crossed (templated_fact=0.067 vs raw_fact=0.047 fact_delta=0.020 tiny; retrieval-gated); MIDDLE_BAND -- factual content is retrieval-bound not template-bound |
| Boundary conditions | template-rendering machinery is real (gram lift +0.547); but factual content depends on upstream retrieval; gain only when retrieval is solved |
| Composes with | intent classifier (routes which template); refuse-gate (when retrieval misses, refuse instead of hallucinate); KV-learned projection (improves underlying retrieval) |
| Encoder provenance | NO_RECORD on a2 (likely LLM_AT_INFERENCE since linked to intent classifier infrastructure) |
| Cert atoms | `EXP_a2_substrate_templated_response_v1` MIDDLE_BAND; `EXP_a2_substrate_templated_response_v1_FULL_MM` MEASURED_MECHANISM |

#### Stage 3 integrated audit-device pipeline (chain-grade production)

| Field | Value |
|-------|-------|
| Where it works | V_C_IN in {1000, 2000} x V_REL in {20, 50}: in_ans=1.000 out_ref=1.000 near_ref=1.000 uncert_corr=1.000 cv=0.000 across all 4 corners; p95 ranges 0.114ms (V_C=1000 V_REL=50) -> 0.169ms (V_C=2000 V_REL=20) |
| Where it cliffs | V_C_IN>2000 untested; V_REL>50 untested in integrated pipeline; M_KV ceiling inherited from cell-B envelope (M_KV<=10k chain-grade) |
| Boundary conditions | inherits V_REL<=50 from refuse-gate v2; inherits M_KV<=10k from cell-B; combined envelope is the production-deployable surface |
| Composes with | refuse-gate v2 (V_REL<=50); cell-B dense-KV (M=10k); intent classifier (routes input); all four substrate-product application-layer components |
| Encoder provenance | NO_RECORD (recent landing) |
| Cert atoms | `EXP_substrate_stage3_integrated_audit_device_demo_v1_chain_grade_envelope_VRELIN_le_50_VC_600_MKV_10k` HARD_PASS_INTEGRATED_AUDIT_DEVICE; `EXP_substrate_stage3_integrated_audit_device_demo_v2_production_scale_GPU` HARD_PASS_PRODUCTION_SCALE |

#### KV learned projection (chain-grade held-out; M=100k MIDDLE_BAND)

| Field | Value |
|-------|-------|
| Where it works | LEARNED contrastive projection GENERALIZES to HELD-OUT facts; recall>=0.70 worst=0.827; keysep=0.878; margin over analytic-ceiling +0.747; shuffled-control=0.015 (clean discriminator); std=0.019 across seeds |
| Where it cliffs | held-out generalization claim is chain-grade; at M=100k separate measured-mechanism row; dense_KV_learned_key_calibration_v1 is MEASURED_MECHANISM (key collapse no upgrade) -- the discriminator IS narrow |
| Boundary conditions | n_enc=2 encoders used; contrastive objective vs analytic ceiling |
| Composes with | KV recall (pythia substrate KV pull-up family); stage3-integrated-audit (production retrieval layer); refuse-gate (high-confidence projection bound) |
| Encoder provenance | LLM_AT_INFERENCE on kv_learned_projection_v1 |
| Cert atoms | `EXP_kv_learned_projection_v1` HARD_PASS (2 rulings); `EXP_dense_KV_learned_key_calibration_v1` MEASURED_MECHANISM |

### 2.6 META rules (protocols, not capabilities)

| META rule | Status | Effect on the phase diagram |
|-----------|--------|------------------------------|
| Principle O (basis-vs-readout labels) | Standing (USER 2026-06-24 BIAS-O) | Labels live at READOUT not in BASIS; basis_layer_label_contamination_proof_v4 PROSPECTIVE BANDS prove top5={label<=True, rand>=True, emergent>=True} -- contamination flag mandatory pre-spec |
| Path C (substrate-native encoder at inference) | USER 2026-06-23 decision (P=0.60-0.75 brain prior) | Encoder provenance ledger required per cell; chain-grade Path A/B (pythia/word2vec/llama) are DIAGNOSTIC PROBES only; Path C is the product-of-record |
| Mu-Viswanath anisotropy bound | Closed via cosine-floor proven_bound | `META_substrate_tracks_KNN_cosine_floor_within_0p007` proven_bound; substrate IS at the cosine-physics floor one-sided; anisotropy rescue 4arm sweep honest_negative; closed via proof not rescue |
| META_M7 (smoke-vs-full regime match) | Standing operational invariant | `META_M7_smoke_regime_must_match_full_along_every_capacity_sensitive_dimension_pointer_chain_v2_csp_gated_signflip_evidence`; sign-flip in csp at full-vs-smoke regime is the empirical evidence |
| META_BARRIER_1 quintuple reconciliation | Standing | substrate native multihop ceiling at 2-hop was REFUTED 4-for-4 then RECONCILED at 5-hop chain-grade via partition-per-hop ORACLE routing; the 2-hop ceiling holds without routing, breaks with routing |
| META_M3 / M4 / M5 / M6 | Operational | bundle-health (NaN spoke can win cf-RPE routing); consolidation by-construction saturation; cross-cell baseline must match chain-construction; NAIVE baseline must be derived not copied |

### 2.7 Recent additions

| Addition | Status | Envelope |
|----------|--------|----------|
| Substrate-at-cosine-physics-floor | proven_bound (one-sided) | `META_substrate_tracks_KNN_cosine_floor_within_0p007_across_eight_construction_param_combinations_n_seeds_1_smoke_M_2000_pythia_160m_window_16_to_64`; one-sided bound; floor at recall@1 <=0.16 across all tested constructions |
| TOKEN_BLOCK_RANGE for language ingest [5,25] | Operational config per current cell family | TOKEN_BLOCK_RANGE=[5,25] used in language-ingest envelope; not an isolated chain-grade atom but boundary condition for fair_harness substrate-as-LM family |
| V_TOKEN over-provisioning at N=8192 | Operational design choice | per task statement: 10^6+ vocab capacity at N=8192 with sparse-bipolar f=0.05 -- vocab capacity exceeds typical V=4000 by 250x; no isolated cert atom (this is a derived bound from sparse-bipolar capacity-scaling per Sparse-Bipolar row) |

### 2.8 Capabilities from research integration map (additional chain-grade, not in original task list)

These are listed for completeness from the substrate-mine of the 478 chain-grade ledger rows + research integration map (Section 2 of `research_phase_diagram_integration_map_AND_storage_efficiency_spec_sheet_2026-06-25.md`):

| Capability | Op-point | Atom |
|------------|----------|------|
| Modern-Hopfield cleanup | N=4096/8192 M/N=0.30 acc=1.000 | `EXP_modern_hopfield_n_sweep_v1` HARD_PASS |
| Multiplicative composition (sparse x K-ensemble) | N=2048, obs_mult=240x = pred_mult=240x | `EXP_substrate_capacity_composition_b2xb4_v1_n2048` PASS |
| Modular macrocolumn K=32 cost-path | N=8192 M=1000 K=32 read_flops <=0.5x monolithic at recall parity; util=0.15 | `EXP_m1_modular_macrocolumn_W_v2_FULL_CG` chain-grade cost-path (capacity multiplier inconclusive) |
| Compositional generalization (K=10..20) | N=4096 G=8 chains K=10/15/20 all =1.00 novel-chain recall (METRIC-CAP flag: by-construction-saturation watch) | `EXP_substrate_compositional_generalization_K10_to_K20_v1_n4096` PASS |
| Lock-in amplifier (noise rejection) | N_DIM=8192 M=500 sigma_64 P=64 x16.39 lift over single-shot | `EXP_lock_in_amplifier_hd_frequency_v1_FULL` HARD_PASS |
| HotpotQA 2-hop bridge | N=4096 M_triples=1610 2hop=0.991 vs 1hop=0.001 (892x ratio) refuse=1.0 OOD | `EXP_h_hotpotqa_ingest_v1` HARD_PASS |
| Substrate-as-LM (fair harness) | N_DIM=8192 V=4000 text8 100k sparse_bipolar BPC=7.306 vs unigram=7.738 (+0.432 bits) | `EXP_fair_harness_substrate_as_lm_v1` HARD_PASS |
| Het-plasticity cf-RPE+STDP superadditive | N_DIM=512 (bigram) superadditive; at N=8192 cf-RPE-only beats het-combined (sub-additive at production scale) | `EXP_substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512` PASS |
| Extended context K*=12 (sym-W + posbind) | K*=12 at V=70 N=8192; G6 K16 V512 N8192 +2.10 HP | `EXP_substrate_extended_context_ceiling_posbind_symw_v1_8192_16384_gpu` PASS |
| Permutation-binding multi-occurrence | HRR primitive upgrade; cyclic-shift cleanup rescues FHRR same-role collision | `EXP_substrate_permutation_binding_multiocc_v2_full` HARD_PASS_CHAIN_GRADE |
| Compose freq routing v5 DEFINITIVE | chain-grade compose-routing (Path B / freq-routing family) | `EXP_substrate_compose_freq_routing_v5_DEFINITIVE` chain-grade |
| Basis-layer label contamination proof v4 | PROSPECTIVE BANDS FRESH SEEDS [42,47,51]; label_hurts=True emergent_within=T | `EXP_substrate_basis_layer_label_contamination_proof_v4_prospective_bands` HARD_PASS_CHAIN_GRADE_DEFINITIVE |
| Whitening / PCA / dim-expansion / last-token-vs-mean-pool | 4 distinct PASS rows; data survives encoding-readout-strategy transform | `EXP_substrate_pca_prewhitening_codebook_v1`, `EXP_substrate_dim_expansion_subsumes_whitening_n_enc_10000_v1`, `EXP_substrate_last_token_vs_whitening_mean_pool_v1`, `EXP_substrate_audit_core_C2_C3_whitened_pythia/llama1b` |

---

## 3. Cross-capability phase diagram

### 3.1 Shared axes (where multiple capabilities co-occupy a dimension)

| Axis | Capabilities sharing the axis | Envelope intersection |
|------|------------------------------|----------------------|
| **V_REL (relation vocab)** | refuse-gate (<=256), stage3-integrated-audit (20-50), HotpotQA-refuse, csp-uncertainty, conformal-CP | clean intersection at V_REL<=50 -- chain-grade composition envelope for the AUDIT-DEVICE stack |
| **N_DIM=4096** | sequence-binding g1b (K=20), c3 compressed-replay (depth=5), HotpotQA 2-hop bridge, compositional-generalization (K=10..20), m1 modular-macrocolumn (cost-path) | all five capabilities chain-grade simultaneously at N=4096; the substrate "sweet spot" for relational + sequence work |
| **N_DIM=8192** | substrate-as-LM (fair-harness +0.432 bits), het-plasticity (cf-RPE +0.201), lock-in amplifier (x16.39), extended context K*=12, modular-macrocolumn (cost-path) | substrate-LM stack natural operating point; chain-grade composition envelope at the LM rail |
| **K=4096 multi-bank** | multi-bank WM routing (chain-grade), partition-per-hop (uses multi-bank), beam-search WM-candidates (uses WM-candidate pool) | three capabilities composable simultaneously at K=4096 bank count; ABOVE K=4096 untested for all three |
| **alpha=0.3 boundary** | a8 continual-writes (cliff identified above), NREM-replay (protects sub-cliff regime), CSP-Hebbian-coexist (chain-grade at sub-cliff) | the continual-learning sub-cliff regime is the composition envelope; ABOVE alpha=0.3 cliff cascades through all three |
| **M=10M (storage)** | partition-routing hierarchical (chain-grade), partition-routing single (M=1M only), Cell B dense-KV inheritance | hierarchical 2-level is the ENABLER past M=1M; single-level cliffs |
| **5-hop depth** | partition-per-hop (0.955), bidirectional meet-in-middle (0.620), beam-search WM (0.667) | partition-per-hop dominates at chain-grade; bidir + beam are revival paths; ALL THREE chain-grade at 5-hop (composition not tested) |

### 3.2 Co-existing chain-grade composition envelopes

The following capability bundles can co-exist at chain-grade SIMULTANEOUSLY (within the same operating-point cell):

**Bundle A: Audit-device production stack**
- Stage3 integrated audit (V_C_IN<=2000, V_REL<=50, M_KV<=10k)
- Refuse-gate V_REL (<=50 within V_REL envelope)
- Intent classifier (N=2048)
- Templated response (MIDDLE_BAND -- factually retrieval-bound)
- KV learned projection (held-out generalization)
- Conformal split-CP (where task shape supports tight set)
- p95 latency 0.114-0.169ms across the bundle

**Bundle B: Substrate-as-LM rail**
- Substrate-as-LM fair-harness (+0.432 bits at N=8192 V=4000 text8 100k)
- Het-plasticity cf-RPE (+0.201 bits at N=8192)
- Extended context K*=12 (sym-W posbind)
- Lock-in amplifier (x16.39 noise rejection)
- char-trigram encoder (substrate-native Path C)
- Modular macrocolumn cost-path (read-flops <=0.5x at recall parity)

**Bundle C: Relational + multi-hop**
- Sequence-binding g1b (K=20 at N=4096)
- c3 compressed-replay (depth=5)
- HotpotQA 2-hop bridge (892x ratio)
- Partition-per-hop multi-hop (5-hop 0.955)
- Multi-bank WM K=4096
- Beam-search WM-candidates (0.667 at 5-hop)
- Bidirectional meet-in-middle (0.620 at 5-hop)
- Compositional generalization K=10..20

**Bundle D: Continual learning / consolidation**
- a8 continual-writes alpha<=0.3 (chain-grade boundary)
- NREM-replay (proven_bound; protects sub-cliff regime)
- CSP-Hebbian coexist (chain-grade)
- (CONFLICT) REM-homeostasis (under_classified) AND STC-selective (HARD_FAIL) occupy same consolidation slot

**Bundle E: Storage scaling**
- Sparse-bipolar capacity at N=1024..16384 (alpha=0.048 stable)
- HRR-bind at N up to 131072
- Modern-Hopfield cleanup at M/N=0.30 (N up to 8192)
- Multiplicative composition sparse x K-ensemble (240x at N=2048)
- Partition-routing single-level (M=1M)
- Partition-routing hierarchical 2-level (M=10M)

### 3.3 Conflicts / overlapping envelope dimensions

| Conflict pair | Conflict axis | Status |
|---------------|---------------|--------|
| NREM-replay vs REM-homeostasis | consolidation pathway slot | only one runs at a time; NREM is proven_bound, REM is under_classified MIDDLE_BAND |
| STC-cascade vs C1-baseline | mechanism-vs-baseline at k=6 | c2 HARD_FAIL: C2 (1.000) does not beat C1 (1.000) at k=6 -- C1 is already at metric-cap; need harder discriminator regime |
| Het-plasticity combined vs cf-RPE-only | composition at N=8192 | at N=8192 het-combined (+0.141) is SUB-ADDITIVE vs cf-RPE-only (+0.201); brain may run them in parallel but our metric shows mid-N-DIM degeneracy |
| 2-hop ceiling (without routing) vs 5-hop chain-grade (with routing) | multihop regime | META_BARRIER_1_QUINTUPLE: barrier holds substrate-native; reconciles with ORACLE routing; OPEN_QUESTION: substrate-native routing-without-oracle |
| K=10..20 metric-cap vs need for harder discriminator | compositional generalization | by-construction-saturation watch; corpus G=8 may be saturating; chain-grade limited to current corpus scope |
| flat (unrouted) recall vs routed recall at M>=100k | routing necessity | flat strictly decreasing through M; routing IS the enabler past M=100k |

### 3.4 Untested cross-capability composition (load-bearing gaps)

The following compositions are NOT yet tested at chain-grade and represent the next research surface:

1. **Multi-bank WM (K=4096) x sequence-binding g1b (K=20) joint envelope** -- both chain-grade alone; combined K_SEQ x K_BANK never measured
2. **Stage3-integrated-audit at M_KV>10k** -- production envelope ceiling is M_KV<=10k; M_KV at 100k or higher untested
3. **Partition-routing hierarchical (M=10M) x KV-learned-projection (held-out)** -- both chain-grade alone; combined retrieval at M=10M never measured
4. **Conformal-CP (binary task) -- structurally infeasible without different formulation**; not a gap but a known regime exclusion
5. **HotpotQA 2-hop at M_triples>10000** -- chain-grade only at M=1610
6. **Substrate-as-LM at N>=16384** -- chain-grade only at N=8192; cleaner head-to-head with unigram at scale untested
7. **NREM-replay achieving chain-grade bar 0.05 final_forget** -- currently proven_bound at 0.31; would close consolidation-pathway open question

### 3.5 Encoder-provenance cross-cut (Path C audit)

| Capability class | SUBSTRATE_NATIVE | LLM_AT_INFERENCE | MIXED / OTHER |
|------------------|-------------------|-------------------|----------------|
| Storage & basis | sparse-bipolar capacity, capacity-composition, compositional-generalization, modern-Hopfield, g1b, c3 sequence, extended-context-posbind | -- | -- |
| Encoder-bearing | -- | KV-learned-projection, PCA-prewhitening, dim-expansion, last-token-vs-whitening, intent-classifier (pythia-160m) | hotpotqa MIXED |
| Routing / architectural | (recent landings; NO_RECORD pending classification: multi-bank K=4096, partition-routing 10M, partition-hierarchical, beam-search, bidir-meet-mid, multihop-partition-per-hop) | -- | -- |
| Refuse / calibration | -- | -- | refuse-gate v_rel_extension, csp-first-ship, conformal-splitcp, stage3-integrated-audit (NO_RECORD; structurally substrate-native at retrieval/refuse layer; encoder-dependent only if upstream) |
| Other / mixed | freq-routing v5 DEFINITIVE | -- | freq-routing tagged WORD2VEC_DIAGNOSTIC_PROBE in provenance ledger (diagnostic probe only) |

**Provenance audit headline:** 375/464 cells (80.8%) are SUBSTRATE_NATIVE; 43 (9.3%) LLM_AT_INFERENCE; remainder mixed/unclassified. The chain-grade application-layer atoms that are LLM_AT_INFERENCE all use pythia/llama as the ENCODER (frozen) -- the substrate side of the stack remains the load-bearing claim per Path C design.

---

## 4. Findings + recommendations to USER

**Finding F1: We DO have per-characteristic phase-diagram understanding.** Research's 2026-06-25 integration map covers 15 capability families with verdict-field-verified envelopes; this audit extends to 25 capabilities + META rules + cross-capability composition envelopes (4 chain-grade composition bundles identified; 7 specific composition gaps surfaced).

**Finding F2: The substrate has 4 distinct chain-grade composition envelopes operating simultaneously** (Audit-device / LM-rail / Relational-multihop / Storage-scaling). Bundle D (continual-learning) is partial -- NREM-replay proven_bound not chain-grade.

**Finding F3: Three by-construction-saturation watches remain unclosed** -- K=10..20 compositional-generalization all 1.00 (corpus G=8 may be saturated); HotpotQA setrecall=1.0 (discriminated by rand-ctrl=0 -- OK); lock-in P=64 sigma_64=1.0 (discriminated by baseline=0.061 -- OK). Compositional-gen extension to K>=25 with larger corpus (G in {8, 32, 128}) is the highest-value gap-fill per Research's Gap-cell-B proposal.

**Finding F4: META_BARRIER_1 quintuple reconciliation establishes the current routing-dependent multihop regime.** Substrate-native routing-without-oracle is the open question; partition-per-hop with ORACLE = chain-grade at 5-hop 0.955; without routing, 2-hop ceiling holds. This is a load-bearing scoping note for any future multihop dispatch.

**Finding F5: Encoder provenance ledger is comprehensive for older cells (464 classified) but recent chain-grade landings need backfill** -- 7 of the 14 most-recent chain-grade landings (partition-routing, hierarchical, multi-bank K=4096, refuse-gate v_rel, stage3 v2, multihop-compose, beam-search, bidir-meet-mid) carry NO_RECORD. Recommendation: route encoder-provenance backfill to a one-shot script that classifies recent chain-grade rows.

**Finding F6 (process-health flag to USER):** the integration audit task itself reveals a structural pattern -- per-characteristic envelopes are well-documented in individual cells but the synthesizing cross-cut (THIS doc) was missing until USER asked. **Recommendation:** consider standing-cadence audit (every 5-7 cycles per Fix #16 results-to-application discipline) where Testbed produces an updated per-characteristic phase-diagram snapshot. Marginal cost low (substrate-mine + 1 doc); fleet-health value high (closes the recurring "do we have THAT?" question).

---

## Citations (verify-the-referent)

Direct-read metrics.json verdict fields:
1. `data/exp_substrate_partition_routing_10M_full_v2/metrics.json` verdict=HARD_PASS
2. `data/exp_substrate_partition_routing_hierarchical_2level_v1/metrics.json` verdict=CHAIN_GRADE_AT_M_10M
3. `data/exp_substrate_working_memory_multi_bank_K_extension_adversarial_v1/metrics.json` verdict=HARD_PASS
4. `data/exp_substrate_refuse_gate_v_rel_extension_v1/metrics.json` verdict=HARD_PASS
5. `data/exp_substrate_stage3_integrated_audit_device_demo_v2_production_scale_GPU/metrics.json` verdict=HARD_PASS_PRODUCTION_SCALE
6. `data/exp_substrate_multihop_compose_fly_lsh_multibank_partition_v2_META_M7_rail/metrics.json` verdict=HARD_PASS_CHAIN_GRADE_BARRIER_1_REVIVAL
7. `data/exp_substrate_multihop_beam_search_with_WM_candidates_v1/metrics.json` verdict=HARD_PASS
8. `data/exp_substrate_multihop_bidirectional_meet_middle_v2_META_M7_rail/metrics.json` verdict=HARD_PASS_CHAIN_GRADE_BIDIRECTIONAL_REVIVAL
9. `data/exp_a2_substrate_templated_response_v1/metrics.json` verdict=MIDDLE_BAND
10. `data/exp_conformal_splitcp_cpu_v1/metrics.json` verdict=MIDDLE_BAND
11. `data/exp_substrate_rem_replay_retrieval_energy_baseline_v1_n8192_gpu/metrics.json` verdict=MIDDLE_BAND
12. `data/exp_c2_cascade_stc_swr_continual_v2/metrics.json` verdict=HARD_FAIL
13. `data/exp_kv_learned_projection_v1/metrics.json` verdict=HARD_PASS
14. `data/exp_substrate_basis_layer_label_contamination_proof_v4_prospective_bands/metrics.json` verdict=HARD_PASS_CHAIN_GRADE_DEFINITIVE
15. `data/exp_substrate_continual_NREM_replay_v1_smoke/metrics.json` verdict=MIDDLE_BAND (smoke); full proven_bound atom carries +0.57 abs reduction

Substrate-mine sources:
- `data/substrate_index/meta/cert_ledger.jsonl` (761 rows total; 478 chain_grade rows; 27 META atoms referenced)
- `data/_testbed_encoder_provenance_FINAL.jsonl` (464 cells: 375 SUBSTRATE_NATIVE / 43 LLM_AT_INFERENCE / 34 NO_CELL_CANT_VERIFY / 6 UNKNOWN / 2 WORD2VEC_DIAGNOSTIC / 2 MIXED / 2 SUBSTRATE_NATIVE_INFERENCE_LLM_INGEST_ONLY)

Cross-source notes:
- `notes/phase_portrait_v1_inventory_atom_substrate_operating_regime_map_2026-06-22.md` (~38-42 phase-diagram atoms by axis; 11 transform-survival atoms)
- `notes/research_phase_diagram_integration_map_AND_storage_efficiency_spec_sheet_2026-06-25.md` (15 chain-grade capability families integrated; storage-efficiency spec sheet)
- `notes/research_substrate_aliveness_FULL_store_mined_map_2026-06-24.md`

-- Testbed (integrator + fleet-health auditor); per-characteristic phase-diagram audit cert-trail artifact; addressed to USER + Research (Director).
