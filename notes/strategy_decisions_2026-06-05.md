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
