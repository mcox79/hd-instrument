# strategy_decisions_2026-06-05

## v426 -> v427 CYCLE 98 BATCH (2026-06-05)

Verdicts processed: substrate_kgram_xor_real_llama1b_v1 (MIDDLE_BAND) + substrate_kfact_combination_anchors_v1 (MIDDLE_BAND)

### Step 0 honest re-read
- kgram_xor_real_llama1b_v1: HONEST. K2/K1=1.17x (1.155-1.181x 3/3 seeds). Label "modest" accurate. No LVH.
- kfact_combination_anchors_v1: HONEST. 2/4: A1+A3 pass; A2+A4 fail. Label "2/4 anchors confirm" accurate. No LVH.
HONEST: 922 -> 924 (+2). LVH: 222 UNCHANGED.

### Cap_map decisions
- kgram_xor_real_llama1b: PP-8 sub-property annotation. Real-data XOR lift 1.17x vs synthetic 6.63x. V_C=256 VQ ceiling persists in real Llama-1B. Band UNCHANGED.
- kfact_combination_anchors: Physics combination sub-property annotation. beta* recovery (A1=1.000) + Rule-8 gain (A3=+29.3pp) confirmed. A2 transition K=25 vs sqrt(N)/2=16 mismatch (finite-N correction needed). A4 resonator_disagree=0.0% (unexplained; open physics question). Band UNCHANGED.

### Portfolio: 32+77 UNCHANGED. 0 new rows. 0 BAND-LIFTS. 0 closures.

Queue state: overnight_queue 0 pending (cache stale ~39.5h). [queue: empty -- Exp-Dev session will refill on its cadence]

## v427 -> v428 CYCLE 99 (2026-06-05)

Verdict: substrate_certified_deletion_demo_medical_v1 MIDDLE_BAND

### Step 0 honest re-read
- LABEL: MIDDLE_BAND -- honest. cert_latency_median=3.136ms (range 3.115-3.163ms, 3 seeds) falls in 1-10ms MIDDLE_BAND window. HP threshold was <1ms -- missed by ~3x. phantom_recall=0.000 (all seeds), verifier_confirmed=1.000 (all seeds), nondeleted_retention=1.000 (all seeds). Deletion mechanism correct; latency is the gap.
- No over-claim. HONEST: 924 -> 925 (+1). LVH: 222 UNCHANGED.

### Cap_map decision
- PP-3 (audit trail + rotation strategy): Sub-property annotation. Medical demo confirms deletion cert mechanism works end-to-end at M=1200, RSA-512, third-party verifier. Latency 3.136ms above <1ms HP threshold; latency-optimization path required for production-grade GDPR demo. Band UNCHANGED at 0.55-0.70.
- PP-9 (GDPR deletion / reasoning amortization): Sub-property annotation. Certified deletion confirmed third-party verifiable with 0 phantom recall. Latency gap (3.136ms vs <1ms) is a latency-engineering challenge, not a correctness failure. Band UNCHANGED.
- Product-feature row (certified deletion): MIDDLE_BAND annotation. Deletion cert + audit chain + verifier all confirmed working. RSA accumulator overhead drives latency. Optimization path: RSA bit-reduction + N-scale reduction + batch cert + hardware acceleration.

### Portfolio: 32+77 UNCHANGED. 0 new rows. 0 BAND-LIFTS. 0 closures.

### Rescue sketches (PROT-004/006 -- latency gap, cheapest-first per [[feedback-rescue-sketch-first-sequencing]])
1. R1 (CHEAP, 0-compute) -- Subsumption: cert_latency 3.136ms is sub-10ms; real HIPAA deletion compliance windows are 60-day; <1ms HP threshold is stricter than any medical regulatory SLA. Re-frame HP as <10ms for product context; MIDDLE_BAND becomes functionally HP for compliance demo.
2. R2 (CHEAP, CPU <30min) -- RSA bit-reduction: RSA-256 vs RSA-512 latency; accumulator ops scale O(k^2) with key bits; halving key size expected to halve latency toward ~1.5ms; likely clears <2ms and possibly <1ms.
3. R3 (CHEAP, CPU <30min) -- N-scale ablation: N=1024 or N=2048 vs N=4096; projection-op component of cert latency is O(N); smaller N may clear <1ms with acceptable retrieval accuracy trade-off.
4. R4 (MEDIUM, GPU <2h) -- Batch cert optimization: batch 200 deletion certs into one accumulator witness update; amortized latency per cert drops proportionally with batch size.
5. R5 (MEDIUM, GPU <2h) -- GPU-native accumulator: RSA-512 on GPU vs CPU; may achieve sub-ms cert at current N=4096 with no algorithmic change.

### PROT compliance (v427 -> v428)
- PROT-004/006: No closures. 5 rescue sketches filed for MIDDLE_BAND latency gap (cheapest-first sequencing). 0 new top-level rows. 0 BAND-LIFTS.
- PROT-007: v428 history row to be appended to substrate_capability_map_history.md.
- PROT-008: Validator skipped (annotation-only; no row state changes; no portfolio changes; 0 LVH; MIDDLE_BAND x1 sub-property only).
- PROT-009: cap_map.md (this v428 entry) + substrate_capability_map_history.md + decisions log staged atomically; 340th PROT-009 paired commit.
- PROT-018: substrate_certified_deletion_demo_medical_v1 no _nN suffix; N=4096 stated in metrics. CLEAN.

Cap_map: v427 -> v428 CYCLE 99 (1 MID: substrate_certified_deletion_demo_medical_v1 CERT-DELETION-3MS-PHANTOM-ZERO-VERIFIER-CONFIRMED; PP-3+PP-9+product-feature sub-prop annotations; 5 latency-rescue sketches; HONEST 924->925; LVH 222; Portfolio 32+77; 340th PROT-009 paired commit) (2026-06-05)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v428 -> v429 CYCLE 100 BATCH (2026-06-05)

Verdicts processed: substrate_cognitive_core_e2e_pythia_v1 (MIDDLE_BAND) + substrate_medical_qa_proto_no_umls_dependency_v1 (MIDDLE_BAND) + ex_concept_strong_baselines_llama1b_v1 (HARD_FAIL)

### Step 0 honest re-read (3 verdicts; 0 LVH; all HONEST)

**V1 (substrate_cognitive_core_e2e_pythia_v1) MIDDLE_BAND -- HONEST**
substrate_core=1.000 ALL 3 seeds. pythia_raw: 0.820/0.745/0.805 mean=0.790. ratio: 1.22x/1.34x/1.24x mean=1.27x. single_evidence=1.000 ALL seeds (Rule8 combine gain). cert_reconstructible=1.000 ALL seeds. MIDDLE_BAND label honest: partial advantage confirmed but not categorical. No LVH.

**V2 (substrate_medical_qa_proto_no_umls_dependency_v1) MIDDLE_BAND -- HONEST**
pythia_raw_mcq=0.193 ALL 3 seeds. substrate_aug_mcq=0.207 ALL 3 seeds. mcq_ratio=1.069x ALL seeds. deletion_cert_operational=True ALL 3 seeds. del_before=0.949-0.969; del_after=0.000 ALL seeds. MIDDLE_BAND honest: mcq lift 7% is small but real; deletion cert confirmed at medical scale. Note: Pythia-160m baseline 0.193 is BELOW random=0.25 (4-choice MCQ), so substrate lift to 0.207 is relative to a degraded baseline. No LVH.

**V3 (ex_concept_strong_baselines_llama1b_v1) HARD_FAIL -- HONEST**
substrate_single_pass=0.469/0.478/0.462 mean=0.469 vs bigram=0.470/0.486/0.468 mean=0.475 vs trigram=0.601/0.600/0.598 mean=0.601. Substrate LOSES TO BIGRAM in 2/3 seeds. Extended context MONOTONICALLY DEGRADES: K2=0.450 K5=0.406 K10=0.347. HARD_FAIL label honest. SIXTH V_C=256 concept-LM bottleneck confirmation (n_docs=10000, Llama-1B). Extended-context degradation (K10 worst) is new signal: superposition noise accumulates faster than signal with K-context extension. No LVH.

HONEST: 925 -> 928 (+3). LVH: 222 UNCHANGED.

### Cap_map decisions

**V1 substrate_cognitive_core_e2e_pythia_v1 MIDDLE_BAND:**
PP-8 sub-property annotation. End-to-end Pythia-160m integration: substrate retrieval achieves 100% accuracy; Pythia standalone 79% on same task. Rule8 combine gain confirmed (single_evidence=1.000). cert_reconstructible=1.000. Ratio 1.27x is partial not categorical -- Pythia-160m achieves 79% on this specific synthetic cog-core benchmark (lower Pythia baseline inflates ratio vs categorical wins where Pythia=0.000). Band UNCHANGED.

**V2 substrate_medical_qa_proto_no_umls_dependency_v1 MIDDLE_BAND:**
PP-9 + PP-3 sub-property annotation. Deletion cert confirmed operational at medical scale: del_before=0.95-0.97, del_after=0.000, cert_reconstructible=1.000 (100% third-party verifiable). MedQA aug lift 1.07x is marginal -- Pythia-160m baseline degraded below random on 4-choice MCQ (model too small for medical domain). Medical deletion demo operational; MedQA aug awaits stronger base model. Band UNCHANGED.

**V3 ex_concept_strong_baselines_llama1b_v1 HARD_FAIL:**
PP-8 sub-property annotation. SIXTH V_C=256 concept-LM confirmation. New signal: K-context DEGRADES performance monotonically (K2=0.450 < K1=0.469; K10=0.347). Superposition noise accumulates faster than signal with more context bindings at V_C=256. Rescues R2 V_C-sweep + R3 SQ-2 from v421 remain active. R6 new: K-degradation diagnosis. Band UNCHANGED. NO CLOSURE per PROT-004/006 (rescue paths active).

### Rescue sketches V3 (PROT-004/006; cheapest-first per [[feedback-rescue-sketch-first-sequencing]])
R2 (CHEAP, CPU <30min) -- V_C-sweep: V_C={512, 1024, 2048}; K-degradation at V_C=256 suggests finer vocabulary needed BEFORE K-extension; K at fine V_C may show positive benefit. Active from v421.
R3 (MEDIUM, GPU <2h) -- SQ-2 composition: replace VQ with SQ-2 multi-hop architecture; bypasses V_C ceiling entirely. Active from v421.
R6 (CHEAP, CPU <30min) -- K-degradation diagnosis: run K={1,2} at V_C={256,512} jointly; confirms V_C x K interaction; K=2 at V_C=512 is expected to show neutral or positive effect vs K=2 at V_C=256=-4%. Lowest-cost new diagnosis. NOT-AUTO-DISPATCHED.

### Portfolio: 32+77 UNCHANGED. 0 new rows. 0 BAND-LIFTS. 0 closures.

### PROT compliance (v428 -> v429)
- PROT-004/006: No closures. V3 HF rescues R2+R3 active from v421; R6 filed. V1+V2 MIDDLE_BAND sub-prop annotations.
- PROT-007: v429 history row appended to substrate_capability_map_history.md.
- PROT-008: Validator skipped (annotation-only; no row state changes; no portfolio changes; 0 LVH; MIDDLE_BAND x2 + HF x1 sub-prop only).
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 341st PROT-009 paired commit.
- PROT-018: All 3 anchors no _nN suffix (N not binding for these task types). CLEAN.
- PROT-021: all 3 source=remote run_mode=full. No smoke artifacts.
- PROT-022: V1 ratio 1.22x/1.34x/1.24x normal seed variance; V2 all-identical seeds (deterministic 300-question sampling -- noted); V3 K-degradation monotonic all 3 seeds (deterministic signal).

Cap_map: v428 -> v429 CYCLE 100 (1 HF: ex_concept_strong_baselines_llama1b SIXTH-V_C256-LLAMA1B-K-DEGRADES-MONOTONIC; 2 MID: cognitive_core_e2e_pythia RULE8-CERT-1.27x-PARTIAL + medical_qa_no_umls DELETION-CERT-OPERATIONAL-MEDQA-MARGINAL; 0 HP; 0 LVH; PP-8+PP-9+PP-3 sub-prop annotations x3; R6 K-diag filed; HONEST 925->928; LVH 222; Portfolio 32+77; 341st PROT-009 paired commit) (2026-06-05)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v429 -> v430 CYCLE 101 BATCH (2026-06-05)

Verdicts processed: substrate_multimodal_binding_text_kg_v1 (HARD_PASS) + substrate_continual_learning_distshift_v1 (HARD_PASS)

### Step 0 honest re-read (2 verdicts)

**V1 (substrate_multimodal_binding_text_kg_v1) HARD_PASS -- HONEST**
text_to_kg=1.000 (3/3 seeds), kg_to_text=1.000 (3/3 seeds), single_modality=1.000 (3/3 seeds), cross_modal_combine=1.000 (3/3 seeds). All 4 metrics at ceiling across all 3 seeds (N=4096, M=2000, run_mode=full, elapsed=9.56s). HARD_PASS label correct -- no per-cell contradiction. No LVH.

**V2 (substrate_continual_learning_distshift_v1) HARD_PASS -- HONEST**
current_state_acc=1.000 (3/3), updated_returns_B=1.000 (3/3), silent_contradiction_rate=0.000 (3/3), old_valid_acc=1.000 (3/3), audit_trace_acc=1.000 (3/3). All 5 metrics perfect across 3 seeds (N=16384, run_mode=full, elapsed=2957.9s ~49min). HARD_PASS label correct. No LVH.

HONEST: 928 -> 930 (+2). LVH: 222 UNCHANGED.

### Cap_map decisions

**V1 substrate_multimodal_binding_text_kg_v1 HARD_PASS:**
PP-23 (Cross-modal substrate provenance): BAND LIFT 0.40-0.55 -> 0.55-0.70 + STATE LIFT (🔬 Research only -> 🟢 Validated, want stronger). First direct empirical validation: text<->KG cross-modal binding is modality-agnostic at N=4096, M=2000, full-accuracy ceiling (1.000 all cells). Cross-modal combine (1.000) confirms bundle-level algebraic composition works across modalities. Note: text+KG is a structured case (KG nodes as dense vectors); image-embedding extension (projection head) remains untested but the algebraic binding mechanism is now empirically validated.
PP-21 (Audit-grade KG): Sub-property annotation. Modality-agnostic binding at N=4096 M=2000 confirms text<->KG triple encoding works without representation collapse. text_to_kg=1.000 and kg_to_text=1.000 unanimous: bidirectional recovery exact. BAND UNCHANGED.

**V2 substrate_continual_learning_distshift_v1 HARD_PASS:**
True continual learning (distribution shift sub-axis): Sub-property annotation. Distribution shift override confirmed: newer writes override older at 100% (updated_returns_B=1.000 all seeds), old facts remain accessible (old_valid_acc=1.000 all seeds), zero silent contradictions (0.000 all seeds), full audit trail (audit_trace_acc=1.000 all seeds). DIFFERENT axis from 4-stage retention (ret_A=0.745 gap) -- tests single-shift override correctness not multi-stage long-term retention. 4-stage PARTIAL band UNCHANGED.
PP-4 (Concept drift detection): Sub-property annotation. audit_trace_acc=1.000 with zero silent contradictions confirms substrate distinguishes 'current belief' from 'overridden belief' -- foundational override-detection primitive. Band UNCHANGED.

### Portfolio: 32+77 UNCHANGED (+0 new rows). PP-23 BAND-LIFT 0.40-0.55 -> 0.55-0.70 + STATE-LIFT. PP-21+true-continual+PP-4 sub-prop annotations.

### PROT compliance (v429 -> v430)
- PROT-004/006: No closures. No rescue sketches required (both HARD_PASS).
- PROT-007: v430 history row to be appended to substrate_capability_map_history.md.
- PROT-008: PP-23 state change + band-lift -- VALIDATOR APPLIES. Cross-modal binding mechanism is modality-agnostic (text+KG proven); image-embedding extension untested (projection head); band-lift conservative (+0.15 mid-band). PROT-009 atomic commit covers all.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 342nd PROT-009 paired commit.
- PROT-018: No _nN suffixes. N=4096 and N=16384 stated in metrics. CLEAN.
- PROT-021: both source=remote run_mode=full. No smoke artifacts.
- PROT-022: V1 all-ceiling unanimous 3-seed (not fragile); V2 all-ceiling unanimous 3-seed. No HP-fragility caveats.

Cap_map: v429 -> v430 CYCLE 101 (2 HP: multimodal_binding_text_kg MODALITY-AGNOSTIC-CEILING + continual_learning_distshift DISTSHIFT-OVERRIDE-PERFECT; PP-23 BAND-LIFT 0.40-0.55->0.55-0.70 + STATE-LIFT 🔬->🟢; PP-21+true-continual+PP-4 sub-prop annotations x3; 0 LVH; HONEST 928->930; LVH 222; Portfolio 32+77; 342nd PROT-009 paired commit) (2026-06-05)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v430 -> v431 CYCLE 102 BATCH (2026-06-05)

Verdicts processed: exp_hp12_v1_decisive_extraction_v1 (HARD_PASS) + exp_hp12_v1_end_to_end_demo_backend_v1 (MIDDLE_BAND) + exp_hp12_v1_decisive_crypto_v1 (MIDDLE_BAND)

### Step 0 honest re-read (3 verdicts; source=remote all)

**V1 (exp_hp12_v1_decisive_extraction_v1) HARD_PASS -- HONEST**
pythia_recall=1.000 (2/2 seeds), llama_recall=1.000 (2/2 seeds). N_store=300, N_sub=1024, run_mode=full, elapsed=11.94s. Speed-test deferred (llama_extract_s_per_1k=-1.0, llama_vram_gb=-1.0 -- Llama weights gated/not-local). HARD_PASS label correct -- no per-cell contradiction. No LVH.

**V2 (exp_hp12_v1_end_to_end_demo_backend_v1) MIDDLE_BAND -- HONEST**
live_write_ms_median: 25.5/25.8/28.3ms (seeds 7/17/23). live_recall=1.000 (3/3). certs_verified_frac=1.000 (3/3). phantom_recall_rate=0.000 (3/3). preseed_retention=1.000 (3/3). N=4096, M_seed=3000, K_live=50, n_del=20. MIDDLE_BAND label honest: live_write ~26ms >> <1ms target (gmpy2+bf16/BLAS path needed). All correctness metrics ceiling. No LVH.

**V3 (exp_hp12_v1_decisive_crypto_v1) MIDDLE_BAND -- HONEST**
verify_frac=1.000 (3/3). cert_latency_ms_median: 19.9/18.8/19.2ms. cert_latency_ms_p95: 21.2/20.1/19.9ms. tamper_rejected_frac=1.000 (3/3). verifier_cli_ok=1 (3/3). n_add=200, n_del=80, RSA-1024. MIDDLE_BAND label honest: cert_latency ~19ms >> <1ms target (gmpy2 needed). Crypto correctness ceiling. No LVH.

HONEST: 930 -> 933 (+3). LVH: 222 UNCHANGED.

### Cap_map decisions

**V1 exp_hp12_v1_decisive_extraction_v1 HARD_PASS:**
PP-8 (Substrate-LLM deep integration): Sub-property annotation. Real Llama-1B embedding geometry compatible with substrate retrieval at N_sub=1024 (recall=1.000 both seeds, real npz embeddings). Desktop V1 geometry de-risked -- no HF-3 geometry mismatch. Speed-test deferred (Llama weights not local); speed gate remains open. BAND UNCHANGED (0.50-0.65 at research-only/exploratory state). No state-transition without speed closure.
Tier-2b LLM integration axis: First empirical anchor confirming substrate retrieval is geometry-compatible with production 1B-scale LLM representations (real npz, not synthetic). Geometry-mismatch failure mode (HF-3) closed for V1 demo path.

**V2 exp_hp12_v1_end_to_end_demo_backend_v1 MIDDLE_BAND:**
PP-5 (Substrate-LLM token-throughput latency budget): Sub-property annotation. Live write latency 25.5-28.3ms median at N=4096 (CPU path, pure-Python). MIDDLE relative to <1ms demo target but within 10-50ms LLM token-gen budget window (v310). Demo backend correctness fully validated (live_recall=1.000, cert=1.000, phantom=0.000, retention=1.000). Latency gap is gmpy2+bf16/BLAS only. BAND UNCHANGED.
PP-3 (Audit trail design + rotation strategy): Sub-property annotation. certs_verified_frac=1.000 (3/3 seeds) at M_seed=3000, K_live=50, n_del=20. Deletion cert issuance and verification pipeline end-to-end validated at demo-backend scale. BAND UNCHANGED.
PP-9 (Reasoning amortization economics): Sub-property annotation. preseed_retention=1.000 at M=3000 seed + 50 live writes; phantom=0.000. Large-context substrate operation with zero phantom recall confirmed. BAND UNCHANGED.

**V3 exp_hp12_v1_decisive_crypto_v1 MIDDLE_BAND:**
PP-12 (Compositionality audit API): Sub-property annotation. RSA accumulator crypto: verify_frac=1.000 (3/3), tamper_rejected=1.000 (3/3), verifier_cli_ok=True (3/3). cert_latency ~19ms (MIDDLE; gmpy2 gets <1ms). Cryptographic correctness is ceiling; latency gap is purely gmpy2 install. BAND UNCHANGED.
Deletion-cert framework reliability: Sub-property annotation. tamper_rejected_frac=1.000 unanimous 3-seed at n_del=80 RSA-1024. Anti-tampering confirmed at production deletion scale. Additive corroboration of 92-98% reliability band. BAND UNCHANGED.

### Portfolio: 32+77 UNCHANGED (+0 new rows). PP-8+PP-5+PP-3+PP-9+PP-12+deletion-cert sub-prop annotations x6. 0 BAND-LIFTS. 0 closures.

### HP-12 V1 overall de-risk status (after Cycle 102)
Geometry VALIDATED (Pythia+real-Llama 1.000 recall). Crypto correctness VALIDATED (100% cert/tamper). Demo backend correctness VALIDATED (live_recall=1.000, cert=1.000, phantom=0.000, retention=1.000). Remaining gates: (1) speed -- gmpy2 install for <1ms cert + bf16/BLAS for <1ms write; (2) Llama weights local for speed profiling; (3) V2 HNSW (faiss-OMP Windows deadlock, Testbed/Linux needed).

### PROT compliance (v430 -> v431)
- PROT-004/006: No closures. No rescue sketches required (0 HF).
- PROT-007: v431 history row to be appended to substrate_capability_map_history.md.
- PROT-008: Annotation-only; no row state changes; no portfolio changes. Validator not triggered.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 343rd PROT-009 paired commit.
- PROT-018: No _nN suffixes. CLEAN.
- PROT-021: all 3 source=remote run_mode=full. No smoke artifacts.
- PROT-022: V1 recall 1.000 unanimous 2-seed; V2 correctness 1.000 unanimous 3-seed, latency variance normal (25.5/25.8/28.3ms); V3 cert_latency variance normal (19.9/18.8/19.2ms). No HP-fragility.

Cap_map: v430 -> v431 CYCLE 102 (1 HP: decisive_extraction HARD_PASS-GEOMETRY-LLAMA1B-REAL-NPZ; 2 MID: e2e_demo_backend WRITE-LATENCY-MIDDLE-CORRECTNESS-CEILING + decisive_crypto CERT-LATENCY-MIDDLE-CRYPTO-CEILING; 0 LVH; PP-8+PP-5+PP-3+PP-9+PP-12+deletion-cert sub-prop annotations x6; HONEST 930->933; LVH 222; Portfolio 32+77; 343rd PROT-009 paired commit) (2026-06-05)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v431 -> v432 CYCLE 103 BATCH (2026-06-05)

Verdicts processed: exp_hp12_v1_decisive_crypto_v1 RE-RUN (HARD_PASS) + substrate_ccc_v2_capability_dims_n4096_v1 (HARD_PASS) + substrate_kgram_xor_scaling_sweep_v2 (HARD_PASS) + substrate_bipolar_hadamard_expansion_k8_v2 (MIDDLE_BAND) + substrate_theta_burst_endpoint_only_K3_v2 (HARD_PASS)

### Step 0 honest re-read (5 verdicts; source=remote all)

**V1 (exp_hp12_v1_decisive_crypto_v1 RE-RUN) HARD_PASS -- HONEST**
RSA-256 (cycle 103 re-run vs RSA-1024 cycle 102 MIDDLE_BAND). Seeds 7/17/23: verify_frac=1.000, cert_latency_median 0.0549-0.0591ms, tamper_rejected=1.000, verifier_cli_ok=1 all 3 seeds. ALL cells pass <1ms HP threshold at RSA-256. Different config from cycle 102 (RSA-1024 at 19ms). Re-run is execution of v428 R2 rescue sketch (RSA bit-reduction). No LVH.

**V2 (substrate_ccc_v2_capability_dims_n4096_v1) HARD_PASS -- HONEST**
N=4096, run_mode=full, n_seeds=3, elapsed=90.4s. Per-seed: single_hop=1.000, multi_hop=1.000, analogical=1.000, counterfactual=1.000 (3/3 all ceiling). All 4 CCC-1-v2 capability dims at 1.000 unanimous. No LVH.

**V3 (substrate_kgram_xor_scaling_sweep_v2) HARD_PASS -- HONEST**
k=3 N=4096 Vc=100000 decisive cell: sub_acc=1.000, trigram=1.000, gap=0.0pp (3/3 seeds). k=2 Vc=1000 shows -3.3 to -10pp (expected small-Vc noise). Label Phase 3 scaling path validated is correct per decisive cell. No LVH.

**V4 (substrate_bipolar_hadamard_expansion_k8_v2) MIDDLE_BAND -- HONEST WITH CAVEAT**
n_seeds=5, elapsed=0.76s. Per-seed base_capacity: 10/5/5/0/0. Per-seed exp_capacity: 18/18/18/10/10. Per-seed ratio: 1.8/3.6/3.6/10.0/10.0. Seeds 31+43 have base_capacity=0 (N=128 Hopfield below min-capacity threshold for those seeds; ratio denominator ill-defined). Summary uses Hopfield normalisation (base_capacity=4 vs exp_capacity=15 = 3.70x). CAVEAT: 2/5 seeds base=0. MIDDLE_BAND honest for valid-base seeds (1.5-3.6x). Not LVH.

**V5 (substrate_theta_burst_endpoint_only_K3_v2) HARD_PASS -- HONEST**
n_seeds=5, elapsed=5.4s. Per-seed gain_t2_pp: 25.2/24.2/33.8/27.2/25.0pp (all >>10pp gate). Per-seed gain_t3_pp: 53.0/43.6/47.6/33.0/43.0pp (all >>10pp gate). Direct write rescues multi-step vs iterated: iter_t3 collapses (0.038-0.272) while direct_t3=0.412-0.698. All 5 seeds agree. Mean multistep gain 35.6pp. No LVH.

HONEST: 933 -> 938 (+5). LVH: 222 UNCHANGED.

### Cap_map decisions

**V1 exp_hp12_v1_decisive_crypto_v1 RE-RUN HARD_PASS:**
PP-12 sub-property update. RSA-256 cert_latency=0.056ms: <1ms HP ACHIEVED. This is v428 R2 rescue (RSA bit-reduction) confirmed. Production path at RSA-2048 still requires gmpy2 (~2ms per verdict_msg). PP-12 band UNCHANGED. Deletion-cert reliability: tamper_rejected=1.000 (3/3 seeds) at RSA-256. Corroborates 92-98% reliability band.

**V2 substrate_ccc_v2_capability_dims_n4096_v1 HARD_PASS:**
Multi-row sub-prop: Pool retrieval (single_hop=1.000); PP-11/PP-49 (multi_hop=1.000); PP-8/analogical (analogical=1.000); PP-25 (counterfactual=1.000). All ceiling 3-seed. Phase 2 capability checkpoint confirmed. Portfolio 32+77 UNCHANGED. No band lifts (existing rows already validated).

**V3 substrate_kgram_xor_scaling_sweep_v2 HARD_PASS:**
PP-8 sub-prop. Phase 3: k=3 XOR at N=4096 Vc=100000 = trigram-class (0.0pp gap, 3/3 seeds). k=4 also ceiling. New finding: XOR k-gram at k>=3 is trigram-equivalent at Vc=100000, N=4096. Standalone Phase 3 row candidate after N-sweep (N>=8192). Band UNCHANGED. 0 new rows this cycle.

**V4 substrate_bipolar_hadamard_expansion_k8_v2 MIDDLE_BAND:**
Capacity sub-axis sub-prop. 1.5-3.6x lift for valid-base seeds (3/5); base=0 for seeds 31+43 (N=128 marginal). Expansion helps when base system has nonzero capacity. Band UNCHANGED. 3 rescue sketches (R1: scale N for valid base; R2: seed-condition on nonzero base; R3: cross-N sweep).

**V5 substrate_theta_burst_endpoint_only_K3_v2 HARD_PASS:**
Hebbian-only training row sub-prop. Endpoint-only direct write: 35.6pp mean multi-step gain (24-34pp t+2, 33-53pp t+3, 5-seed unanimous). Write strategy matters: direct endpoint write >> iterative K=1. Standalone write-strategy row candidate after N-sweep. Band UNCHANGED. 0 new rows this cycle.

### Portfolio: 32+77 UNCHANGED. 0 new top-level rows. 0 BAND-LIFTS. 0 closures.

### Rescue sketches V4 (PROT-004/006; cheapest-first per [[feedback-rescue-sketch-first-sequencing]])
1. R1 (CHEAP, 0-compute) -- Scale N baseline: run base at N=512 or N=1024 instead of N=128; ensures nonzero base for all seeds; tests actual expansion ratio at proper operating N.
2. R2 (CHEAP, CPU <30min) -- Seed-conditional analysis: exclude base=0 seeds; report expansion ratio conditioned on base>0 (seeds 7+17+23 give 1.8-3.6x); more interpretable product number.
3. R3 (CHEAP, CPU <30min) -- Cross-N sweep: N=256/512/1024/2048 base vs expansion; maps the ratio vs N curve; confirms whether 3.7x is stable or N-dependent.

### PROT compliance (v431 -> v432)
- PROT-004/006: No closures. V4 MIDDLE_BAND 3 rescue sketches filed cheapest-first. V1-V3+V5 HARD_PASS no rescues needed.
- PROT-007: v432 history row to be appended to substrate_capability_map_history.md.
- PROT-008: Annotation-only; no row state changes; no portfolio changes; 0 LVH. Validator skipped.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 344th PROT-009 paired commit.
- PROT-018: No _nN suffixes. N values stated in metrics bodies. CLEAN.
- PROT-021: all 5 source=remote run_mode=full. No smoke artifacts.
- PROT-022: V1 cert_latency 0.0549-0.0591ms normal seed variance; V2 all-ceiling unanimous (deterministic); V3 k=3 Vc=100000 unanimous ceiling; V4 base_capacity=0 flagged 2/5 seeds; V5 gains unanimous 5-seed.

Cap_map: v431 -> v432 CYCLE 103 (4 HP: hp12_crypto_rerun RSA256-CERT-0.056ms-R2-RESCUE-CONFIRMED + ccc_v2_dims N4096-ALL4-CEILING + kgram_xor_scaling k3-TRIGRAM-CLASS-Vc100K + theta_burst_endpoint MULTISTEP-35.6pp-5SEED; 1 MID: bipolar_hadamard_expansion CAPACITY-1.5-3.6x-VALID-SEEDS-BASE0-SEED31+43-MARGINAL; 0 LVH; PP-12+pool-retrieval+PP-11+PP-8+PP-25+capacity+Hebbian sub-prop annotations x9; R3 V4 rescue sketches cheapest-first; HONEST 933->938; LVH 222; Portfolio 32+77; 344th PROT-009 paired commit) (2026-06-05)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v432 -> v433 CYCLE 104 BATCH (2026-06-05)

Verdicts processed: substrate_minilm_encoder_fidelity_v1 (HARD_PASS) + exp_hp12_v1_extraction_attack_contrast_v1 (HARD_PASS) + exp_hp12_v1_api_surface_test_v1 (HARD_PASS)

### Step 0 honest re-read
- substrate_minilm_encoder_fidelity_v1: HONEST. ALL 5 seeds minilm_recall=1.000, pythia_recall=1.000, minilm_vs_pythia_pp=0.0 -- satisfies recall>=0.80 with margin. VQ separability flat across Vc (0.454-0.478 all seeds/all Vc levels 1000/10000/100000) -- Vc-invariance notable but not over-claimed. No LVH.
- exp_hp12_v1_extraction_attack_contrast_v1: HONEST. ALL 3 seeds pre_delete_extractable=1.000, post_delete_residual=0.000, retention=1.000. ROME/MEMIT baselines stated as external comparators (not measured in this run); substrate numbers not over-claimed. No LVH.
- exp_hp12_v1_api_surface_test_v1: HONEST. ALL 3 seeds endpoints_ok=True, query_recall=1.000, audit_verified_frac=1.000, phantom_recall_rate=0.000, retention=1.000. All metrics ceiling unanimous. No LVH.
HONEST: 938 -> 941 (+3). LVH: 222 UNCHANGED.

### Cap_map decisions
- substrate_minilm_encoder_fidelity_v1: PP-8 + Tier-1-LLM-integration sub-property annotation. MiniLM drop-in encoder confirmed for PHASE4A-1 path. VQ separability 0.465 mean Vc-invariant at N=384; Vc scaling does not move separability at this dimension. Band UNCHANGED.
- exp_hp12_v1_extraction_attack_contrast_v1: PP-9 + PP-3 + deletion-cert product-feature sub-property annotation. Categorical deletion moat confirmed vs LLM weight-editing baselines (ROME 38%/MEMIT 29% residual; substrate 0.000). Architectural advantage confirmed 3-seed full. Band UNCHANGED.
- exp_hp12_v1_api_surface_test_v1: PP-12 + product-feature row sub-property annotation. All 4 HP-12 V1 API endpoints (ingest/query/delete/audit) validated e2e, third-party-verified certs, 0 phantom at M=1200. V1 demo readiness confirmed at API surface level. Band UNCHANGED.

### Portfolio: 32+77 UNCHANGED. 0 new rows. 0 BAND-LIFTS. 0 closures.

Queue state: overnight_queue 0 pending (cache stale). cpu_queue 0. gpu_queue 0. [queue: empty -- Exp-Dev session will refill on its cadence]

## v433 -> v434 CYCLE 105 BATCH (2026-06-05)

Verdicts processed: hp12_v2_crypto_2048_gmpy2_latency_v1 (MIDDLE_BAND) + substrate_capacity_scaling_sweep_v1 (HARD_PASS per label / HONEST MIDDLE_BAND) + hp12_v1_demo_scale_10k_facts_v1 (HARD_PASS)

### Step 0 honest re-read (3 verdicts; source=remote all)

**V1 (hp12_v2_crypto_2048_gmpy2_latency_v1) MIDDLE_BAND -- HONEST**
delete_p50 mean=2.216ms (range 2.124-2.331ms 5 seeds), add_p50=0.128ms, verify_p50=0.119ms. certs_verified=1.000 (5/5). gmpy2=True, RSA-2048. delete at 2.2ms in 1-5ms MIDDLE_BAND window. Label V2-usable honest. No LVH. HONEST: 941 -> 942 (+1).

**V2 (substrate_capacity_scaling_sweep_v1) HARD_PASS -- LVH FLAGGED**
All 5 seeds return IDENTICAL values (deterministic; no seed-driven stochasticity). Effective sample size = 1. alpha_by_N: 0.0596 at N=1024/2048 -> 0.0399 at N=4096/8192 (33% regime drop). alpha_CoV=0.198 measured across 4 N-values (not across seeds). Verdict_msg claims 'stable alpha' but alpha shows two-regime behaviour. HARD_PASS over-claims: honest reading is M scales with N (linearity confirmed) but alpha regime-shifts 33% at N=4096 boundary; 'stable alpha -- Phase-3 N=65536 blueprint supported' premature from N<=8192 with visible regime shift. Honest verdict: MIDDLE_BAND. LVH FLAGGED: label=HARD_PASS honest=MIDDLE_BAND. LVH: 222 -> 223 (+1). HONEST: 942 -> 943 (+1).

**V3 (hp12_v1_demo_scale_10k_facts_v1) HARD_PASS -- HONEST WITH NOTE**
live_recall=1.000 (3/3), audit_verified_frac=1.000 (3/3), phantom_recall_rate=0.000 (3/3), preseed_retention=0.997-1.000 (3/3). Correctness ceiling. HARD_PASS for correctness domain honest. NOTE: live_write_ms_median=137ms at N=10000 vs 25ms at N=4096 in v431 (5.3x super-linear). Verdict_msg omits write-latency signal; not over-claim (correctness HARD_PASS accurate) but planning implication significant: N=65536 CPU write path untenable without bf16/BLAS. No LVH. HONEST: 943 -> 944 (+1).

HONEST: 941 -> 944 (+3). LVH: 222 -> 223 (+1).

### labeled-vs-honest entry
- Anchor: substrate_capacity_scaling_sweep_v1
- Label: HARD_PASS 'stable alpha -- Phase-3 N=65536 blueprint supported'
- Honest reading: MIDDLE_BAND -- linearity (M~N) confirmed; alpha two-regime (0.0596 at N<=2048 vs 0.0399 at N>=4096, 33% drop); identical 5-seed values = single effective measurement; Phase-3 extrapolation premature.
- Cells contradicting: alpha_by_N regime shift 0.0596->0.0399 at N=4096; alpha_CoV=0.198 across N not seeds.

### Cap_map decisions

**V1 hp12_v2_crypto_2048_gmpy2_latency_v1 MIDDLE_BAND:**
PP-12 sub-property annotation. RSA-2048 + gmpy2=True: delete 2.2ms V2-production range (1-5ms). add/verify sub-0.15ms. certs_verified=1.000 5-seed. RSA-2048 gmpy2 path V2-usable; headline demo path still RSA-512 for <1ms. HP-12 V2 crypto gate: batch-deletion workflows unblocked at 2.2ms. Band UNCHANGED.

**V2 substrate_capacity_scaling_sweep_v1 [LVH: HARD_PASS -> MIDDLE_BAND]:**
Capacity scaling sub-axis annotation. Honest reading applied. Linearity M~N CONFIRMED at N=1024-8192. Alpha regime shift at N=4096: 0.0596 (N<=2048) vs 0.0399 (N>=4096). Mean_alpha=0.050 across both regimes. Phase-3 blueprint needs cross-regime characterization. MIDDLE_BAND annotation applied. Band UNCHANGED. Rescue sketches (cheapest-first):
R1 (CHEAP, 0-compute) -- Re-frame as planning lower bound: N=65536 capacity ~3277 facts at mean_alpha=0.050 is actionable despite non-stationarity.
R2 (CHEAP, CPU <60min) -- N-extension sweep: add N=16384 and N=32768; confirm alpha stabilises at 0.0399 or continues to drop.
R3 (CHEAP, CPU <30min) -- Stochastic capacity probe: break determinism to get real seed-level replication; confirms effective sample size.

**V3 hp12_v1_demo_scale_10k_facts_v1 HARD_PASS:**
PP-9 + product-feature row sub-property annotation. 10K facts N=10000: all correctness ceiling. HP-12 V1 demo correctness confirmed at TRUE demo scale. Write latency 137ms (super-linear vs 25ms at N=4096) flagged as engineering task (bf16/BLAS needed). Band UNCHANGED.

### Portfolio: 32+77 UNCHANGED. 0 new top-level rows. 0 BAND-LIFTS. 0 closures.

### PROT compliance (v433 -> v434)
- PROT-004/006: No closures. V2 LVH MIDDLE_BAND 3 rescue sketches filed cheapest-first. V1+V3 annotation-only.
- PROT-007: v434 history row to be appended.
- PROT-008: Annotation-only after LVH downgrade (MIDDLE_BAND sub-prop; no row-state change). Validator skipped.
- PROT-009: cap_map.md + history + decisions log staged atomically; 346th PROT-009 paired commit.
- PROT-018: No _nN suffixes; N stated in metrics bodies. CLEAN.
- PROT-021: all 3 source=remote run_mode=full. No smoke artifacts.
- PROT-022: V2 identical 5-seed values flagged (deterministic; CoV across N not seeds); V1 5-seed normal variance; V3 3-seed deterministic ceiling.

Cap_map: v433 -> v434 CYCLE 105 [label-vs-honest] (1 LVH: substrate_capacity_scaling_sweep_v1 HARD_PASS->MIDDLE_BAND alpha-stable-over-claim 33%-regime-shift-at-N4096 identical-5-seeds; 1 HP: hp12_v1_demo_scale_10k_facts CORRECTNESS-CEILING-10K-WRITE-LATENCY-NOTE; 1 MID: hp12_v2_crypto_2048_gmpy2 DELETE-2.2MS-V2-USABLE; HONEST 941->944; LVH 222->223; Portfolio 32+77; 346th PROT-009 paired commit) (2026-06-05)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v434 -> v435 CYCLE 106 BATCH: 3 DUPLICATE re-runs (no new action) + 1 NEW MIDDLE_BAND (e2e_pythia_v2xl); 0 LVH; 0 HP; 0 HF; annotation-only; HONEST 944->945; LVH 223 UNCHANGED

### Step 0 honest re-read (4 anchors)

Anchors 1-3 are confirmed DUPLICATES of prior cycle verdicts:
- substrate_cognitive_core_analogical_v1: metrics identical to v420/cycle-91 (sub=1.000(3/3) py~0.001(3/3) ratio=900x). Already committed. NO ACTION.
- substrate_cognitive_core_counterfactual_v1: metrics identical to v419/cycle-90 (sub=1.000(3/3) retention=0.995-1.000(3/3) py=0.000(3/3) ratio=1e6x). Already committed. NO ACTION.
- substrate_cognitive_core_architectural_advantage_v1: metrics identical to v419/cycle-90 (LONGCONV/CROSS-SESSION/MULTIDOC@50 all 1.00(3/3)). Already committed. NO ACTION.

Anchor 4 substrate_cognitive_core_e2e_pythia_v2xl: NEW anchor. Label MIDDLE_BAND. Per-cell: sub=1.000(5/5) py_raw mean=0.769(range 0.738-0.796)(5/5) ratio mean=1.30x(range 1.257-1.356x)(5/5) single_evidence=1.000(5/5) cert_reconstructible=1.000(5/5). HONEST -- label correctly describes partial advantage. No LVH.

HONEST: 944 -> 945 (+1 new anchor only). LVH: 223 UNCHANGED.

### substrate_cognitive_core_e2e_pythia_v2xl MIDDLE_BAND (NEW)
pythia-160m, n_q=3000/seed, run_mode=full, 5 seeds, source=remote, elapsed=2205.9s.
substrate_core=1.000 ALL 5 seeds. pythia_raw: 0.796/0.751/0.792/0.738/0.770 mean=0.769.
ratio: 1.257/1.332/1.263/1.356/1.298x (mean=1.30x, range 1.26-1.36x). ALL 5 seeds MIDDLE_BAND.
single_evidence=1.000 ALL 5 seeds (Rule-8 combine gain confirmed). cert_reconstructible=1.000 ALL 5 seeds.

Comparison vs v429 e2e_v1 (cycle 100): v1 was 3-seed n_q~1000/seed mean_ratio=1.27x. v2xl is 5-seed n_q=3000/seed mean_ratio=1.30x. Near-identical partial advantage at 2.2x higher statistical power. Partial advantage is STABLE and REAL, not a statistical artifact. Pythia non-zero baseline (75-80%) means categorical separation requires harder benchmarks, larger context windows, or domain-specific tasks.

PP-8 sub-property annotation (added):
'cognitive_core_e2e_pythia_v2xl_MIDDLE_BAND v435: pythia-160m 5-seed n_q=3000 full elapsed=2206s; substrate_core=1.000(5/5); pythia_raw mean=0.769(range 0.738-0.796)(5/5); ratio mean=1.30x(range 1.257-1.356x)(5/5); single_evidence=1.000(5/5 Rule8-combine); cert_reconstructible=1.000(5/5); STABLE MIDDLE_BAND confirmed at 2.2x higher power vs v429 v1 (3-seed n_q~1000); partial advantage real; R1-R3 rescues active from v429; harder benchmarks needed for categorical separation.'

### Cap_map decisions
- e2e_pythia_v2xl: MIDDLE_BAND annotation only. PP-8 sub-property added. Band UNCHANGED (partial advantage stable at 1.30x; not new discovery; v429 R1-R3 rescues active).
- No band lifts.
- No new portfolio rows. No closures.

### PROT compliance (v434 -> v435)
- PROT-004/006: No closures. No new HF. v429 rescue sketches R1-R3 remain active for e2e partial-advantage gap (no new rescues needed for MIDDLE_BAND stable re-confirmation).
- PROT-007: v435 history row appended to substrate_capability_map_history.md.
- PROT-008: Annotation-only; no row state changes; no portfolio changes; 0 LVH. Validator skipped.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 347th PROT-009 paired commit.
- PROT-018: No _nN suffixes. CLEAN.
- PROT-021: source=remote run_mode=full. No smoke artifacts.
- PROT-022: 5-seed variance normal (pythia_raw 0.738-0.796 expected LLM stochasticity; not HP-fragile).

Portfolio: 32+77 UNCHANGED. 0 new rows. 0 BAND-LIFTS. 0 closures.
HONEST: 944 -> 945 (+1). LVH: 223 UNCHANGED.

Cap_map: v434 -> v435 CYCLE 106 (3 DUPLICATE re-runs no action; 1 MID: cognitive_core_e2e_pythia_v2xl STABLE-1.30x-5SEED-N_Q3000-PARTIAL-ADVANTAGE-CONFIRMED; 0 HP; 0 HF; 0 LVH; PP-8 sub-prop annotation; HONEST 944->945; LVH 223; Portfolio 32+77; 347th PROT-009 paired commit) (2026-06-05)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.
## v435 CYCLE 107 -- substrate_cognitive_core_e2e_pythia_v1 DUPLICATE (2026-06-05)

### Step 0 honest re-read
Verdict at 18:13 ended_at: bridge cache stale 43h (snapshot_ts 2026-06-03T22:36:16; age_s=157361s). get_metrics() returned _source=remote but serving stale cache data.
Per-cell metrics: substrate_core=1.000(3/3), pythia_raw=0.790, ratio=1.27x(3/3), n_seeds=3, run_mode=full.
IDENTICAL to cycle 100 metrics committed at v429 (ended_at 14:48). No local event_outcome file found. No new remote measurement.

VERDICT: DUPLICATE of cycle 100 v429. 18:13 timestamp is a re-appearance of the same completed run in the queue tracker, NOT a new measurement.

HONEST: 945 UNCHANGED (no new anchor). LVH: 223 UNCHANGED.

### Cap_map decision
NO ACTION. substrate_cognitive_core_e2e_pythia_v1 already annotated at v429 (MIDDLE_BAND PP-8): sub=1.000(3/3), pythia_raw=0.790, ratio=1.27x(3/3), Rule8+cert=1.000(3/3). No new information.

### PROT compliance (v435 CYCLE 107 -- NO VERSION BUMP)
- PROT-009: No commit issued (no cap_map state change; no new anchor data).
- PROT-021: Bridge cache stale 43h. Same production run already validated at v429.

Portfolio: 32+77 UNCHANGED. 0 new rows. 0 BAND-LIFTS. 0 closures.
HONEST: 945 UNCHANGED. LVH: 223 UNCHANGED. Cap_map: v435 UNCHANGED.

Queue state: bridge stale; last known 0 pending both queues. [queue: empty -- Exp-Dev session will refill on its cadence]## v435 CYCLE 108 -- 3 DUPLICATES: analogical_v1 + counterfactual_v1 + architectural_advantage_v1 (2026-06-05)

### Step 0 honest re-read (3 anchors; source=remote; bridge stale but remote metrics fetched)

All 3 anchors (ended_at 18:57-19:00) are confirmed DUPLICATES of prior cycle committed verdicts:
- substrate_cognitive_core_analogical_v1: current metrics IDENTICAL to v420/cycle-91 + v435/cycle-106 (sub=1.000(3/3) py~0.001(3/3) ratio=900x). Already committed. NO ACTION.
- substrate_cognitive_core_counterfactual_v1: current metrics IDENTICAL to v419/cycle-90 + v435/cycle-106 (sub=1.000(3/3) retention=0.995-1.000(3/3) py=0.000(3/3) ratio=1e6x). Already committed. NO ACTION.
- substrate_cognitive_core_architectural_advantage_v1: current metrics IDENTICAL to v419/cycle-90 + v435/cycle-106 (LONGCONV=1.000(3/3) CROSS-SESSION=1.000(3/3) MULTIDOC@50=1.000(3/3)). Already committed. NO ACTION.

No over-claim: all 3 are queue-tracker re-appearances of same completed runs, not new measurements. No new anchors. No LVH.

HONEST: 945 UNCHANGED (no new anchors). LVH: 223 UNCHANGED.

### Cap_map decision
NO ACTION. All 3 already annotated: analogical at v420; counterfactual+architectural at v419. v435 marks third sequential duplicate cycle for these same 3 anchors. Queue-tracker de-duplication recommended (same completed run IDs surfacing repeatedly).

### PROT compliance (v435 CYCLE 108 -- NO VERSION BUMP)
- PROT-009: No commit issued (no cap_map state change; no new anchor data).
- PROT-021: source=remote run_mode=full; production runs already validated.
- PROT-018: No _nN suffixes. CLEAN.

Portfolio: 32+77 UNCHANGED. 0 new rows. 0 BAND-LIFTS. 0 closures.
HONEST: 945 UNCHANGED. LVH: 223 UNCHANGED. Cap_map: v435 UNCHANGED.

Queue state: last known empty (bridge stale). [queue: empty -- Exp-Dev session will refill on its cadence]
## v435 CYCLE 109 -- substrate_long_conversation_scale_1000_exchanges_v1 DUPLICATE (2026-06-05 20:22)

### Step 0 honest re-read
Bridge cache stale 46h (snapshot_ts 2026-06-03T22:36:16). get_metrics() returned _source=remote (stale cache serving prior data).
Per-cell metrics (20:22): sub_at_1000=1.000(3/3), substrate_by_depth d50/d200/d500/d800/d1000=1.000 ALL 3 seeds, pythia_at_deep=0.000 ALL seeds, E=1200, n_threads=5, run_mode=full, seeds 7/17/23, elapsed=700.2s.
IDENTICAL to cycle 94 metrics committed at v423 (ended_at ~10:47; sub_at_1000=1.000(3/3), sub flat d50->d1000=1.000 ALL seeds, pythia d500+=0.000 ALL seeds, E=1200, n_threads=5, 3-seed full, elapsed=792s).
Elapsed difference (700.2 vs 792s) is within timing cache variance; all substantive cells identical; same seeds 7/17/23.

VERDICT: DUPLICATE of cycle 94 v423. 20:22 timestamp is a queue-tracker re-publication of the same completed run, NOT a new measurement. Pattern consistent with cycles 107/108 duplicate sequences.

HONEST: 945 UNCHANGED (no new anchor). LVH: 223 UNCHANGED.

### Cap_map decision
NO ACTION. substrate_long_conversation_scale_1000_exchanges_v1 already committed at v423 (HARD_PASS PP-8): sub_at_1000=1.000(3/3), sub flat to 1000 exchanges, pythia collapses at depth, 5x extension of v419 LONGCONV. No new information.

### PROT compliance (v435 CYCLE 109 -- NO VERSION BUMP)
- PROT-009: No commit issued (no cap_map state change; no new anchor data).
- PROT-021: Bridge stale 46h. Same production run already validated at v423.
- PROT-018: No _nN suffixes. CLEAN.
- Note: third duplicate-stream in cycle sequence (107=e2e_pythia, 108=analogical/counterfactual/architectural triple, 109=long_conversation). Queue-tracker de-duplication issue broadening.

Portfolio: 32+77 UNCHANGED. 0 new rows. 0 BAND-LIFTS. 0 closures.
HONEST: 945 UNCHANGED. LVH: 223 UNCHANGED. Cap_map: v435 UNCHANGED.

Queue state: bridge stale 46h; last known 0 pending both queues. [queue: empty -- Exp-Dev session will refill on its cadence]

## v435 CYCLE 111 BATCH -- 2 CONFIRMED DUPLICATES (no new action) (2026-06-05)

### Step 0 honest re-read (2 anchors; both confirmed duplicate republishes)

**V1 substrate_multidoc_synthesis_1000plus_docs_v1 -- CONFIRMED DUPLICATE of CYCLE 94 (v423)**
Remote metrics: needle=1.000(3/3), pythia_RAG=0.000(3/3), synth_relerr=0.000(3/3), n_seeds=3, n_docs=1000, elapsed=632.82s, verdict=HARD_PASS. IDENTICAL to cycle 94 committed metrics. Queue-tracker republishing pattern confirmed. NO NEW MEASUREMENT.

**V2 substrate_introspection_toolkit_full_10_categories_v1 -- CONFIRMED DUPLICATE of CYCLE 95 (v424)**
Remote metrics: gap_frac=0.25(3/3), cat5 correct mean~0.570, cat6 deletion_cert_operational=False(3/3), recall_after~0, n_seeds=3, elapsed=442.69s, verdict=MIDDLE_BAND. IDENTICAL to cycle 95 committed metrics. Queue-tracker republishing pattern confirmed. NO NEW MEASUREMENT.

HONEST: 945 UNCHANGED (no new anchors). LVH: 223 UNCHANGED.

### Cap_map decision
NO ACTION. Both anchors already committed: multidoc_synthesis at v423 (HARD_PASS) + introspection_toolkit_full_10_categories at v424 (MIDDLE_BAND). No new information to annotate.

### PROT compliance (v435 CYCLE 111 -- NO VERSION BUMP)
- PROT-009: No commit issued (no cap_map state change; no new anchor data).
- PROT-021: source=remote for both; metrics match prior committed runs exactly.
- Note: substrate_cognitive_core_analogical_v1 also confirmed-duplicate on verified-skiplist; skipped without dispatch (no action).

Queue state: overnight_queue 0 pending, cpu_queue 0 pending (bridge stale ~43h+). [queue: empty -- Exp-Dev session will refill on its cadence]
Portfolio: 32+77 UNCHANGED. 0 new rows. 0 BAND-LIFTS. 0 closures.
## v435 CYCLE 112 -- 3 DUPLICATES: certified_deletion_demo_medical_v1 + kfact_combination_anchors_v1 + adversarial_failure_modes_v1 (2026-06-05 21:15-21:16)

### Step 0 honest re-read (3 anchors; source=remote; bridge stale ~47h)

All 3 anchors are confirmed DUPLICATES of prior cycle committed verdicts:
- substrate_certified_deletion_demo_medical_v1 (ended_at 21:16): metrics IDENTICAL to v428/cycle-99 (MIDDLE_BAND, cert_latency_median=3.133ms, phantom_recall=0.000, verifier_confirmed=1.000, M=1200, RSA-512, n_seeds=3, run_mode=full). Already committed. NO ACTION.
- substrate_kfact_combination_anchors_v1 (ended_at 21:15): metrics IDENTICAL to v427/cycle-98 (MIDDLE_BAND, 2/4, A1=1.000, A2=K25.0, A3=+29.3pp, A4=0.0%, n_seeds=3, run_mode=full). Already committed. NO ACTION.
- substrate_adversarial_failure_modes_v1 (ended_at 21:15): metrics IDENTICAL to v425/cycle-96 (MIDDLE_BAND, A=1.000, E=separable, F=graceful, D=0.44 FAIL, n_seeds=3, run_mode=full, elapsed ~774s vs 865s timing variance only). Already committed. NO ACTION.

SKIP-WITHOUT-DISPATCH CONFIRMED: substrate_cognitive_core_architectural_advantage_v1 (21:38) + substrate_long_conversation_scale_1000_exchanges_v1 (21:31) were already on verified-duplicate skiplist per cycles 108+109.

No over-claim on any anchor (all confirmed duplicates; no new measurements). No LVH.

HONEST: 945 UNCHANGED (no new anchors). LVH: 223 UNCHANGED.

### Cap_map decision
NO ACTION. All 3 already annotated: certified_deletion at v428; kfact_combination at v427; adversarial_failure_modes at v425. Queue-tracker de-duplication issue: sixth sequential duplicate-stream cycle (107=e2e_pythia, 108=analogical/counterfactual/architectural triple, 109=long_conversation, 110-111=skiplist, 112=certified_deletion+kfact+adversarial).

### PROT compliance (v435 CYCLE 112 -- NO VERSION BUMP)
- PROT-009: No commit issued (no cap_map state change; no new anchor data).
- PROT-021: source=remote run_mode=full; production runs already validated.
- PROT-018: No _nN suffixes on any anchor. CLEAN.

Portfolio: 32+77 UNCHANGED. 0 new rows. 0 BAND-LIFTS. 0 closures.
HONEST: 945 UNCHANGED. LVH: 223 UNCHANGED. Cap_map: v435 UNCHANGED.

Queue state: bridge stale ~47h; last known 0 pending both queues. [queue: empty -- Exp-Dev session will refill on its cadence]

## v436 CYCLE 113 -- 2 NEW HP + 9 DUPLICATES (2026-06-05 CYCLE 113)

### Step 0 honest re-read

(A) substrate_hallucination_detection_minilm_v1: HARD_PASS label vs per-cell: AUC 0.9996/0.9989/0.9994 all >> 0.90 threshold. Mean recall 0.988 matches label. LABEL HONEST. No LVH.

(B) substrate_real_encoder_capabilities_v1: HARD_PASS label vs per-cell: 18/18 cells = 1.000. Unanimous ceiling. LABEL HONEST. No LVH.

Anchors 3-11: All confirmed duplicates of v431-v433 committed verdicts. Metrics identical. NO ACTION.

HONEST: 945 -> 947 (+2). LVH: 223 UNCHANGED.

### Cap_map decisions (v435 -> v436)

1. KF-1 hallucination-detection BAND-LIFT 65-80% -> 70-85%: AUC=0.999 with real MiniLM encoder confirms encoder-agnostic mechanism. +5% cap per lit-scan penalty (single-N N=384, 3-seed). Caveats: N-scaling from 384 to 4096+ not confirmed with MiniLM; adaptive adversary not tested.

2. PP-8 substrate-LLM deep-integration BAND-LIFT 0.50-0.65 -> 0.55-0.70: v433 minilm_encoder_fidelity + v436 real_encoder_capabilities both at ceiling = two-anchor encoder-agnostic confirmation. +5% cap per lit-scan penalty (synthetic test scenarios; no LLM generation in loop yet).

3. 9 duplicate anchors: no cap_map action.

Queue state: bridge stale; last known 0 pending both queues. [queue: empty -- Exp-Dev session will refill on its cadence]

Portfolio: 32+77 UNCHANGED. 0 new rows. 2 BAND-LIFTS. 0 closures.
HONEST: 945 -> 947. LVH: 223. Cap_map: v435 -> v436.
## v436 CYCLE 114 -- substrate_cognitive_core_e2e_pythia_v2xl DUPLICATE re-appearance (2026-06-05 23:00)

### Step 0 honest re-read

Remote metrics (source=remote, bridge stale). Per-cell IDENTICAL to cycle 106 ff08d96: seed7=1.257x seed17=1.332x seed23=1.263x seed31=1.356x seed43=1.298x mean=1.30x elapsed=2309s vs 2205s (re-read artifact). Root cause: keeper --allow-duplicate re-queue re-stamping (823c92f).

HONEST: 947 UNCHANGED. LVH: 223 UNCHANGED.

### Cap_map decision
NO ACTION. Already annotated at v435 ff08d96. Cap_map stays v436.

### PROT compliance (v436 CYCLE 114 -- NO VERSION BUMP)
- PROT-009: No commit issued (no state change).
- PROT-018: CLEAN. PROT-021: source=remote confirmed.

Cap_map: v436 UNCHANGED. HONEST: 947. LVH: 223.
Queue state: bridge stale; last known empty. [queue: empty -- Exp-Dev session will refill on its cadence]
## v436 -> v437 CYCLE 115 (2026-06-06)

Verdict: substrate_continual_kv_injection_v1 HARD_PASS

### Step 0 honest re-read
- LABEL: HARD_PASS -- HONEST. Per-cell: seed7 current_state=0.9975, seed17=0.9975, seed23=0.99875; silent_contradiction=0.000 all 3 seeds. 60 sessions / 3600 facts. All seeds clearly above any reasonable HP threshold. No over-claim.
- source: REMOTE (authoritative). run_mode=full, n_seeds=3, N=8192.
- HONEST: 947 -> 948 (+1). LVH: 223 UNCHANGED.

### Cap_map decision
- PP-19 (Substrate-as-KV-cache): Sub-property annotation. continual_kv_injection_v1 HARD_PASS v437: N=8192 3-seed full 60 sessions 3600 facts; current_state=0.998 (mean; range 0.9975-0.99875); silent_contradiction=0.000 unanimous all 3 seeds; continual injection fidelity at production-N CONFIRMED. Band UNCHANGED at 0.40-0.60 (latency/throughput characterization via PP-5 and audit-cert generation via PP-12 still pending before band-lift). State UNCHANGED 🔬.
- True continual learning row: Sub-property cross-annotation. KV-injection axis HARD_PASS at N=8192 60-session 3600-fact stream; orthogonal to 4-stage retention axis (which remains 🟡 PARTIAL). No change to 4-stage retention band.

### Portfolio: 32+77 UNCHANGED. 0 new rows. 0 BAND-LIFTS. 0 closures.

### PROT compliance (v436 -> v437)
- PROT-004/006: No closures. 1 HP; no HF; no rescue sketches required (HP verdict).
- PROT-007: v437 history row appended to substrate_capability_map_history.md.
- PROT-008: No band changes. Annotation-only. PROT-008 not triggered.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 349th PROT-009 paired commit.
- PROT-018: No _nN suffix; N=8192 stated in metrics body. CLEAN.
- PROT-021: source=remote run_mode=full. No smoke artifacts.
- PROT-022: current_state variance seed7=seed17=0.9975 seed23=0.99875 tight ceiling -- not HP-fragile.

Cap_map: v436 -> v437 CYCLE 115 (1 HP: substrate_continual_kv_injection_v1 KV-INJECTION-FIDELITY-LONG-STREAM-0.998-ZERO-CONTRADICTION; 0 MID; 0 HF; 0 LVH; PP-19 + true-continual sub-prop annotations; HONEST 947->948; LVH 223; Portfolio 32+77; 349th PROT-009 paired commit) (2026-06-06)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v437 -> v438 CYCLE 116 BATCH (2026-06-06)

Verdicts processed: exp_hp12_v2_crypto_2048_gmpy2_latency_v1 (MIDDLE_BAND) + substrate_capacity_scaling_sweep_xl_v1 (HARD_PASS per label / LVH #224 FLAGGED)

### Reship check: exp_hp12_v2_crypto_2048_gmpy2_latency_v1 vs cycle 105 hp12_v2_crypto_2048_gmpy2_latency_v1
exp_ prefix version has anchor_name=exp_hp12_v2_crypto_2048_gmpy2_latency_v1 (remote confirmed). Per-seed delete_p50 values differ (seed7: 2.181ms exp_ vs 2.125ms no-prefix; seed17: 2.150 vs 2.139; seed31: 2.280 vs 2.331ms). These are genuinely different runs at different times with different timing variance. NOT a re-ship duplicate. Genuine new measurement confirmed.

### Step 0 honest re-read

**V1 (exp_hp12_v2_crypto_2048_gmpy2_latency_v1) MIDDLE_BAND -- HONEST**
delete_p50 5-seed: 2.181/2.150/2.472/2.280/2.088ms (mean=2.234ms). add_p50 mean=0.125ms. verify_p50 mean=0.136ms. certs_verified_frac=1.000 all 5 seeds. gmpy2=True, RSA-2048. delete at 2.234ms falls in 1-5ms MIDDLE_BAND window. Label V2-usable honest. Corroborates cycle 105 hp12_v2_crypto_2048_gmpy2 (mean delete 2.216ms). No over-claim. No LVH.

**V2 (substrate_capacity_scaling_sweep_xl_v1) HARD_PASS -- LVH #224 FLAGGED**
Label: HARD_PASS stable-alpha Phase-3-N65536-blueprint-supported. Honest reading:
- M~N linearity CONFIRMED at N=1024/2048/4096/8192/16384 (5 N-points, 10 seeds).
- Two-regime alpha CONFIRMED: N<=2048 alpha=0.0596, N>=4096 alpha=0.0399/0.0399/0.0400 (33% regime drop at N=4096 boundary, same as v1 LVH #223).
- N>=4096 regime IS stable: alpha=0.0399/0.0399/0.0400 at N=4096/8192/16384 (3 consecutive N-doublings). This is NEW vs v1 (v1 had only 2 data points in N>=4096 regime).
- Seed determinism: 9/10 seeds have IDENTICAL per-seed values. Seeds 71 (N=1024=0.039 outlier) and 101 (N=4096=0.060 outlier) are the only deviations. Effective independent measurements ~2-3.
- mean_alpha=0.048 is cross-regime mean (both regimes averaged). For N=65536 Phase-3: settled-regime alpha=0.040 gives ~2621 facts; verdict_msg mean_alpha=0.048 gives ~3145 facts (20% over-estimate).
- Label over-claim: (a) alpha is NOT globally stable (two-regime structure persists); (b) mean_alpha=0.048 over-states settled Phase-3 extrapolation value of 0.040 by 20%.
- Honest verdict: MIDDLE_BAND UPGRADED vs v1 LVH #223 -- linearity confirmed 5 N-points; N>=4096 alpha=0.040 stable (3 data points reduces extrapolation risk); Phase-3 better-supported but determinism limit and two-regime alpha over-claim persist.
LVH #224: label=HARD_PASS honest=MIDDLE_BAND (alpha not globally stable; mean_alpha 0.048 over-states Phase-3 capacity projection by 20pct; identical seed data limits effective replication to ~2-3 independent measurements).

HONEST: 948 -> 950 (+2). LVH: 223 -> 224 (+1).

### labeled-vs-honest entry LVH #224
- Anchor: substrate_capacity_scaling_sweep_xl_v1
- Label: HARD_PASS 'stable alpha -- Phase-3 N=65536 blueprint supported. mean_alpha(M*/N)=0.048'
- Honest reading: MIDDLE_BAND UPGRADED -- M~N linearity confirmed 5 N-points; N>=4096 alpha=0.040 stable (3 data points, new vs v1); two-regime structure (0.060 N<=2048 vs 0.040 N>=4096) disqualifies 'globally stable alpha'; mean_alpha=0.048 over-estimates N=65536 capacity by ~20pct vs settled-regime alpha=0.040; seed determinism (9/10 identical) limits effective replication.
- Cells contradicting: alpha_by_N regime shift 0.0596->0.0399 at N=4096 (33% drop persists); mean_alpha=0.048 vs settled-regime alpha=0.040.
- Upgrade vs LVH #223: XL now has N=16384 = third stable low-alpha point; Phase-3 extrapolation better-supported but still limited by determinism.

### Cap_map decisions

**V1 exp_hp12_v2_crypto_2048_gmpy2_latency_v1 MIDDLE_BAND (HONEST; genuine new run):**
PP-12 sub-property corroboration. Second independent RSA-2048 gmpy2=True run confirms delete_p50=2.234ms (cycle 105 was 2.216ms; 18us difference = timing noise). RSA-2048 gmpy2 delete latency now anchored at 2.2ms +/- 0.15ms across 10 total seeds (2 independent runs x 5 seeds). Band UNCHANGED. Planning implication: RSA-2048 gmpy2 delete is reliably ~2.2ms; V2 demo path uses RSA-512 for <1ms headline; batch-deletion at 2.2ms/cert is V2-usable.

**V2 substrate_capacity_scaling_sweep_xl_v1 [LVH #224: HARD_PASS -> MIDDLE_BAND]:**
Capacity scaling sub-axis annotation (UPGRADED vs v1 LVH #223 at v434). Honest reading applied.
M~N linearity CONFIRMED at 5 N-values (N=1024 to N=16384). N>=4096 regime alpha=0.040 stable across 3 consecutive N-doublings (new vs v1 which had 2 points). Phase-3 planning anchor: use alpha=0.040 (settled regime) not mean_alpha=0.048 (cross-regime over-estimate) for conservative N=65536 projections; capacity ~2621 facts not ~3145. Determinism limitation (9/10 identical seeds) remains; stochastic probe (v434 R3) still needed. v434 R2 rescue PARTIALLY CONFIRMED: N=16384 added and alpha stable at 0.040. MIDDLE_BAND annotation with UPGRADE note vs v1.
Band UNCHANGED.

### Portfolio: 32+77 UNCHANGED. 0 new rows. 0 BAND-LIFTS. 0 closures.

### PROT compliance (v437 -> v438)
- PROT-004/006: No closures. V2 LVH MIDDLE_BAND: v434 R1-R3 rescues remain active; R2 partially confirmed (N=16384 stable), R3 stochastic probe still open.
- PROT-007: v438 history row to be appended to substrate_capability_map_history.md.
- PROT-008: Annotation-only; no row state changes; no portfolio changes; 1 LVH downgrade. Validator not triggered (no state-transition).
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 350th PROT-009 paired commit.
- PROT-018: No _nN suffixes on either anchor. N values stated in metrics bodies. CLEAN.
- PROT-021: both source=remote run_mode=full. No smoke artifacts.
- PROT-022: V1 5-seed timing variance normal (2.088-2.472ms delete, spread expected); V2 9/10 identical seeds flagged (deterministic geometry; seeds 71+101 outliers provide limited additional signal).

Cap_map: v437 -> v438 CYCLE 116 [label-vs-honest] (1 LVH #224: substrate_capacity_scaling_sweep_xl HARD_PASS->MIDDLE_BAND alpha-not-globally-stable mean_alpha-0.048-over-states-Phase3-by-20pct 3-N-points-in-N>=4096-regime-NEW; V1 exp_hp12_v2_crypto MIDDLE_BAND-CORROBORATION-2.234ms-GENUINE-NEW-RUN; HONEST 948->950; LVH 223->224; Portfolio 32+77; 350th PROT-009 paired commit) (2026-06-06)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v438 -> v439 CYCLE 117 (2026-06-06)

Verdict processed: substrate_etf_hadamard_codebook_init_v1 (HARD_PASS)

### Step 0 honest re-read
- substrate_etf_hadamard_codebook_init_v1: HONEST. Label claims '>=2x capacity'. Actual ratio=10.039x ALL 3 seeds (unanimous). Label is CONSERVATIVE (under-states actual lift). Per-cell: seed7 random=204/hadamard=2048/ratio=10.04x, seed17=10.04x, seed23=10.04x. N=4096, run_mode=full, n_seeds=3, source=remote. No over-claim. NO LVH.
- HONEST: 950 -> 951 (+1). LVH: 224 UNCHANGED.

### Cap_map decision

**substrate_etf_hadamard_codebook_init_v1 HARD_PASS [HONEST; source=remote; n_seeds=3; N=4096; run_mode=full; elapsed=74.1s]:**

Plain-language: We tested whether using a structured Hadamard codebook (instead of random bipolar vectors) raises the substrate's storage capacity. It does -- by a factor of 10x at N=4096 (2048 facts vs 204 facts). This directly attacks the Matthiessen-type codebook-collision noise floor: random codebooks generate correlated interference that limits capacity; Hadamard codes are maximally spread (equiangular tight frame geometry), eliminating most of that noise. The '>=2x' label was conservative -- the actual gain is 10x, unanimous across all 3 seeds.

Capability implication: ETF/Hadamard codebook init is a structural capacity multiplier. At N=4096 it delivers 10x effective storage density over random bipolar baseline. This interacts with two cap_map axes: (1) Capacity scaling row -- settled-regime alpha=0.040 projects ~2621 facts at N=65536 with random codebook; Hadamard init potentially pushes that to ~26000 (10x lift); exact Phase-3 number requires Hadamard scaling sweep. (2) Adversarial-vulnerabilities row (U2 codebook-collision) -- Matthiessen codebook-collision noise is what the a_query_sim defense gate is mitigating at the query layer; Hadamard init attacks the NOISE SOURCE directly at initialization, potentially reducing the attack surface at the codebook layer before any query-layer gate. These two implications are separate and both high-value.

Cap_map annotations:
- Capacity scaling sub-axis: NEW sub-property 'ETF/Hadamard codebook init' HARD_PASS v439. random=204 hadamard=2048 ratio=10.04x at N=4096 3/3 seeds. Matthiessen-type codebook-collision noise eliminated at init layer. Hadamard scaling sweep (N-sweep x Hadamard) needed to update Phase-3 planning anchor (current alpha=0.040 with random codebook). Band LIFT CANDIDATE on capacity-scaling sub-axis pending Hadamard scaling sweep.
- Adversarial-vulnerabilities row (U2 codebook-collision): Sub-property annotation. Hadamard init attacks codebook-collision noise at source (init layer), distinct from a_query_sim (query layer defense). Potential defense depth: codebook-layer hardening + query-layer defense = stacked defense. Complementary axis to G8 a_query_sim defense, not a substitute.

### Portfolio: 32+77 UNCHANGED. 0 new top-level rows. 0 BAND-LIFTS (Hadamard scaling sweep required before band-lift on capacity-scaling sub-axis). 0 closures.

### PROT compliance (v438 -> v439)
- PROT-004/006: No closures. HARD_PASS -- no rescue sketches required.
- PROT-007: v439 history row to be appended to substrate_capability_map_history.md.
- PROT-008: Annotation-only; 0 row state changes; 0 portfolio changes; 0 LVH; 1 HP sub-property added. Validator not triggered (no top-level row state transition).
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 351st PROT-009 paired commit.
- PROT-018: No _nN suffix on anchor. N=4096 stated in metrics body. CLEAN.
- PROT-021: source=remote, run_mode=full. No smoke checkpoint artifact.
- PROT-022: 3-seed ratio identical to 5 decimal places (10.03921568627451 all 3 seeds) -- deterministic geometry (Hadamard is a fixed algebraic object; no seed-dependent randomness in codebook structure). Not HP-fragile -- determinism expected for Hadamard.

Cap_map: v438 -> v439 CYCLE 117 (1 HP: substrate_etf_hadamard_codebook_init_v1 HADAMARD-CODEBOOK-10x-CAPACITY-LIFT-MATTHIESSEN-NOISE-FLOOR-ATTACK; capacity-scaling sub-prop new; adv-vuln U2 codebook-collision init-layer annotation new; 0 LVH; HONEST 950->951; LVH 224; Portfolio 32+77; 351st PROT-009 paired commit) (2026-06-06)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.
## v439 -> v440 CYCLE 118 BATCH (2026-06-06)

Verdicts processed: substrate_matthiessen_dominant_scatterer_v1 (HARD_PASS) + substrate_native_reasoning_k_hop_v1 (HARD_PASS)

### Step 0 honest re-read (2 verdicts; source=remote both)

**(V1) substrate_matthiessen_dominant_scatterer_v1 HARD_PASS -- HONEST (CONSERVATIVE)**
Label: 'HARD_PASS: single dominant noise mechanism (codebook_collision >60%) -- clear optimization target. dominant=codebook_collision (100%)'
Per-cell: 5/5 seeds frac_collision=0.99999999... (effectively 1.000), frac_load=0.000 (5/5), frac_cue_noise=0.000 (5/5). coll_err=0.797-0.806 all seeds. base_err=0.000, load_err=0.000, noise_err=0.000 all seeds.
Label says '>60%' but actual is ~100% -- conservative framing, not over-claim. HONEST. No LVH.

**(V2) substrate_native_reasoning_k_hop_v1 HARD_PASS -- HONEST (NOTE: K=6 not K=5 or K=3)**
Label: 'HARD_PASS: native K-hop reasoning holds to K=3 (>=0.70)... K=3 acc=1.000 | curve=k1-k6=1.0'
Per-cell: 3/3 seeds acc_by_k={'k1':1.0,'k2':1.0,'k3':1.0,'k4':1.0,'k5':1.0,'k6':1.0}. ALL hops 1.000 unanimous.
Label anchors at K=3 threshold -- conservative. Actual ceiling is K=6 (test ceiling). Orchestrator context said 'K=5' but data shows K=6 all 1.000. Honest reading: HP ceiling at K=6 (test-ceiling; true ceiling requires K>6 sweep). HONEST. No LVH.
N=4096, n_seeds=3, run_mode=full, elapsed=65.7s.

HONEST: 951 -> 953 (+2). LVH: 224 UNCHANGED.

### Cap_map decisions

**(V1) substrate_matthiessen_dominant_scatterer_v1 HARD_PASS:**
Noise-anatomy sub-property annotation on adversarial-vulnerabilities U2 (codebook-collision) row and capacity-scaling row.
Key finding: at N=4096 M near capacity, codebook-collision is the SOLE active noise source (100% of error budget across 5 seeds). Load term = 0, cue_noise = 0. This is a Matthiessen-rule decomposition: noise sources do not co-activate; codebook-collision dominates exclusively.
Complementary to v439 ETF/Hadamard finding: Hadamard init attacks the dominant scatterer directly; now confirmed it is the ONLY scatterer at baseline operating point.
Annotation: adversarial-vulnerabilities U2 codebook-collision sub-property. Band UNCHANGED.
Annotation: capacity-scaling noise-floor sub-property. Band UNCHANGED.
No new rows. No band lifts. No closures.

**(V2) substrate_native_reasoning_k_hop_v1 HARD_PASS:**
PP-11 (substrate-as-reasoning-store primitive) + multi-hop combined row sub-property annotation.
Key finding: native K-hop reasoning via K matrix-vector multiplications (no decode loop) achieves 1.000 accuracy to K=6 at N=4096. Structured-retrieval K-hop is purely algebraic: no iterative decode, no error accumulation through K=6. Ceiling is K=6 (test limit); true ceiling requires K>6 sweep.
Mechanism implication: K-hop as K cheap matvecs confirms the algebraic composition primitive is lossless through at least 6 hops. This is structurally different from the single-substrate depth-collapse seen in prior chain-depth experiments -- K-hop here is PURE GRAPH TRAVERSAL (multiply by A_rel matrix) not an overloaded associative store.
Annotation: PP-11 reasoning-store sub-property. K-hop graph-traversal confirmed K=6 ceiling (test limit). Band UNCHANGED.
Annotation: multi-hop combined row. Native K-hop via matvec added as algebraic sub-primitive. Band UNCHANGED.
No new rows. No band lifts. No closures.

### Portfolio: 32+77 UNCHANGED. 0 new top-level rows. 0 BAND-LIFTS. 0 closures.
### HONEST: 951 -> 953 (+2). LVH: 224 UNCHANGED.

### PROT compliance (v439 -> v440)
- PROT-004/006: No closures. Both HARD_PASS; no rescue sketches required.
- PROT-007: v440 history row to be appended to substrate_capability_map_history.md.
- PROT-008: Annotation-only; 0 row state changes; 0 portfolio changes; 0 LVH. Validator not triggered (sub-property annotations only).
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 352nd PROT-009 paired commit.
- PROT-018: Neither anchor has _nN suffix (not N-bound experiments). N=4096 stated in metrics bodies. CLEAN.
- PROT-021: both source=remote run_mode=full. No smoke checkpoint artifacts.
- PROT-022: V1 frac_collision 5-seed near-identical (deterministic geometry: codebook-collision structure analytical at near-capacity M); V2 3-seed acc_by_k identical across seeds (test ceiling -- expected deterministic at N=4096 with M<<capacity).

Cap_map: v439 -> v440 CYCLE 118 (2 HP: matthiessen_dominant_scatterer CODEBOOK-COLLISION-100pct-SOLE-ACTIVE-NOISE-SOURCE-5SEED + native_reasoning_k_hop K=6-CEILING-1.000-ALGEBRAIC-MATVEC-NO-DECODE; U2+capacity-scaling+PP-11+multi-hop sub-prop annotations x4; 0 LVH; HONEST 951->953; LVH 224; Portfolio 32+77; 352nd PROT-009 paired commit) (2026-06-06)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## CYCLE 119 -- v440 -> v441 (2026-06-06)

### Step 0 honest re-read (MANDATORY)

**(V1) substrate_etf_hadamard_phase4a_infra_eval_v1 MIDDLE_BAND -- LABEL HONEST**
Label: 'MIDDLE_BAND: orthogonalization 2-4x on real encoder. raw_MiniLM_capacity=307 whitened_capacity=844 ratio=2.75x (N_sub=384)'
Per-cell: seed7=2.7492x; seed17=2.7492x; seed23=2.7492x (all 3 identical -- deterministic geometry; PCA whitening of fixed encoder weights is seed-independent). Label claims '2-4x'; actual=2.749x rounds to 2.75x; inside [2,4] band. MIDDLE_BAND correct (does not reach HP threshold; does not reach HF threshold). No over-claim. NO LVH.

HONEST: 953 -> 954 (+1). LVH: 224 UNCHANGED.

### substrate_etf_hadamard_phase4a_infra_eval_v1 MIDDLE_BAND [source=remote; n_seeds=3; N_sub=384; run_mode=full; elapsed=9.5s]

Plain-language: We tested whether the orthogonalization/whitening trick that gave 10x capacity lift on the synthetic BSC substrate (v439) also lifts capacity when the codebook comes from a real pre-trained encoder (MiniLM, 384-dim). It does, but more modestly: 2.75x (307 -> 844 facts). The lift is deterministic across seeds (PCA whitening of fixed encoder geometry is seed-independent). MIDDLE_BAND: real confirming lift but below the HP threshold needed for production claim; more limited than synthetic because MiniLM was already partially structured (not fully random), so whitening does less incremental work.

Capability implication (PP-8 / substrate-LLM deep integration): Whitening of real encoder outputs improves substrate capacity 2.75x at N_sub=384. This validates the Phase 4A orthogonalization hypothesis on a real encoder. The gap from synthetic (10x at N=4096) to real (2.75x at N=384) is partially explained by (a) N_sub=384 vs N=4096 (smaller space = less room for orthogonalization to help) and (b) MiniLM already trained for semantic alignment (partially structured, not fully random). Phase 4B cross-N sweep at N={1024,2048,4096} with whitened real encoder would disambiguate N-dependence from encoder-structure effect. MIDDLE_BAND is a GENUINE result confirming the mechanism transfers to real encoders.

Cap_map decision: PP-8 annotation only (Phase 4A infra eval sub-property). Band UNCHANGED. No new rows. No closures.

Sub-property annotation on PP-8 row:
'substrate_etf_hadamard_phase4a_infra_eval MIDDLE_BAND v441: MiniLM N_sub=384 3-seed full elapsed=9.5s; raw_capacity=307 whitened_capacity=844 ratio=2.75x (3/3 seeds identical -- deterministic PCA whitening); orthogonalization lifts real-encoder capacity 2.75x; MIDDLE_BAND (below HP threshold vs 10x synthetic at N=4096); mechanism confirmed on real encoder; Phase 4B N-sweep {1024,2048,4096} recommended to disambiguate N-effect from encoder-structure effect.'

### Portfolio: 32+77 UNCHANGED. 0 new top-level rows. 0 BAND-LIFTS. 0 closures.
### HONEST: 953 -> 954 (+1). LVH: 224 UNCHANGED.

### PROT compliance (v440 -> v441)
- PROT-004/006: No closures. MIDDLE_BAND; no rescue sketches required (mechanism confirmed, not rejected).
- PROT-007: v441 history row to be appended to substrate_capability_map_history.md.
- PROT-008: Annotation-only; 0 row state changes; 0 portfolio changes; 0 LVH. Validator not triggered.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 353rd PROT-009 paired commit.
- PROT-018: No _nN suffix on anchor (N_sub=384 is encoder intrinsic dim, not config.N contract). CLEAN.
- PROT-021: source=remote run_mode=full. No smoke checkpoint artifacts.
- PROT-022: 3-seed all-identical (deterministic -- PCA whitening of fixed encoder geometry is seed-independent by design). Expected.

Cap_map: v440 -> v441 CYCLE 119 (1 MIDDLE_BAND: substrate_etf_hadamard_phase4a_infra_eval_v1 WHITENING-2.75x-REAL-ENCODER-PHASE4A; PP-8 sub-prop annotation; 0 LVH; HONEST 953->954; LVH 224; Portfolio 32+77; 353rd PROT-009 paired commit) (2026-06-06)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## CYCLE 120 -- v441 -> v442 (2026-06-06)

Verdicts processed: substrate_hallucination_robustness_hard_negatives_v1 (HARD_PASS) + substrate_etf_minilm_dim_expansion_v1 (HARD_PASS label -> LVH #225 MIDDLE_BAND honest)

### Step 0 honest re-read

**(A) substrate_hallucination_robustness_hard_negatives_v1 HARD_PASS -- LABEL HONEST**
auc_hard: 0.9683/0.9659/0.9687 (3/3 seeds >= 0.90 threshold). auc_easy=0.621 (not claimed as HP). auc_adv=0.206 explicitly surfaced in msg as adversarial failure -- not over-claimed. Label accurate. No LVH.

**(B) substrate_etf_minilm_dim_expansion_v1 HARD_PASS -> LVH #225 MIDDLE_BAND [honest-read applied]**
Label: 'HARD_PASS: dimensional expansion recovers >=3x capacity headroom for real encoders'
Per-cell: D384 seed7=2.749x seed17=2.749x seed23=3.670x (MEAN=3.06x). D1024: 1.294x all seeds. D4096: 1.294x all seeds.
Contradiction: >=3x claim is mean-based at D384 only; 2 of 3 seeds at D384 fall BELOW 3x; D1024 and D4096 show 1.29x (not 3x). Headroom claim is over-stated as uniform guarantee.
Cross-check: substrate_etf_hadamard_phase4a_infra_eval_v1 (v441, CYCLE 119) reported IDENTICAL D384 raw=307/wht=844/ratio=2.75x and was correctly classified MIDDLE_BAND. Same measurement cannot be HARD_PASS and MIDDLE_BAND simultaneously.
Honest reading: MIDDLE_BAND -- whitening lifts D384 capacity 2.75-3.67x (mean 3.06x); D1024/D4096 show 1.29x lift; expansion-ratio benefit decreases at higher N sub-dimensions. MIDDLE_BAND consistent with v441 prior.
LVH #225 filed. HONEST: 954 -> 956 (+2). LVH: 224 -> 225 (+1).

### Cap_map decisions

**(A) substrate_hallucination_robustness_hard_negatives_v1 HARD_PASS:**
KF-1 hallucination-detection sub-property annotation. Hard-negative robustness confirmed: AUC_hard=0.968 (3/3 seeds >= 0.90). auc_adv=0.206 -- adversarial (shuffled-KB-fact) remains OPEN vulnerability. Hard-same-domain negatives do NOT degrade detection below threshold. Adversarial probe (adv AUC=0.206) is a distinct attack surface -- NOT in-scope for this anchor's HP claim, but surfaced as open work.
KF-1 band: BAND-LIFT CANDIDATE -- hard-negative robustness adds another dimension. Conservative: +2.5% per lit-scan calibration penalty (3-seed, single-N=384, no adversarial adaptation yet). KF-1 BAND-LIFT: 70-85% -> 72-87%.

**(B) substrate_etf_minilm_dim_expansion_v1 [LVH #225 honest: MIDDLE_BAND]:**
PP-8 sub-property annotation. Dimensional expansion via orthogonalization on real MiniLM encoder: D384 2.75x (conservative floor), D1024/D4096 1.29x. Consistent with v441 Phase-4A eval. Cross-N profile (higher lift at smaller N) is new signal: whitening benefit is larger where encoder geometry is more compressed. Phase-4B cross-N sweep with real encoder still recommended.
Band: UNCHANGED (MIDDLE_BAND sub-property on PP-8; consistent with v441 annotation).

### Portfolio: 32+77 UNCHANGED. 0 new top-level rows. 1 BAND-LIFT (KF-1: 70-85% -> 72-87%). 0 closures.

### PROT compliance (v441 -> v442)
- PROT-004/006: No closures. Adversarial vulnerability (auc_adv=0.206) filed as open rescue axis for KF-1.
- PROT-007: v442 history row to be appended.
- PROT-008: 1 BAND-LIFT (KF-1 +2.5%). Validator: hard-negative robustness (AUC_hard=0.968 3/3) + v436 AUC=0.999 prior = two independent robustness anchors; calibration penalty (3-seed, single-N) -> +2.5% cap justified. PROT-008 PASS.
- PROT-009: cap_map.md + history + decisions log atomic commit.
- PROT-018: both anchors no _nN suffix; N stated in metrics. CLEAN.
- PROT-019: LVH #225 filed (etf_minilm_dim_expansion HARD_PASS -> MIDDLE_BAND; >=3x over-stated as uniform guarantee; v441 same-measurement MIDDLE_BAND cross-check confirms over-claim).

Cap_map: v441 -> v442 CYCLE 120 [label-vs-honest LVH #225] (1 HP: substrate_hallucination_robustness_hard_negatives_v1 KF1-HARD-NEG-ROBUST-AUC-968; 1 LVH #225: substrate_etf_minilm_dim_expansion_v1 HARD_PASS->MIDDLE_BAND-d384-2.75x-floor-below-3x-d1024/4096-1.29x; KF-1 BAND-LIFT 70-85%->72-87%; HONEST 954->956; LVH 224->225; Portfolio 32+77; 354th PROT-009 paired commit) (2026-06-06)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.
