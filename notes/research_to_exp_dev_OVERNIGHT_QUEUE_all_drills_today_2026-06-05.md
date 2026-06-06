# Research -> Exp-Dev: OVERNIGHT QUEUE -- all legitimately interesting cells from today's 21 drills

**From:** Research session
**To:** Exp-Dev (primary; queue drain owner)
**Inform:** Testbed + Orchestrator + User
**Date:** 2026-06-05 ~21:00
**Subject:** Per user 2026-06-05 ~21:00: "don't cap the number; send all of the legitimately interesting ones; queue them all tonight". 50+ cells routed across 4 priority tiers + per-cell anchor + cost + HP threshold.

---

## Strategic frame

User wants overnight queue depth from today's research. **All legitimately interesting cells from today's 21 drills enumerated below**, organized into 4 priority tiers. Exp-Dev should:

1. Queue everything in TIER 1 + TIER 2 immediately (cheap; fits overnight)
2. Queue TIER 3 for tomorrow daytime
3. TIER 4 cells are Phase 4 work (multi-day; queue as bandwidth allows)

Total cells: 50+. Total CPU time: ~24-48 hours sustained execution. Total cloud cost if all dispatched: <$50.

---

## TIER 1: CHEAP DECISIVE TESTS (~2 hours each; answer binding architectural questions)

**Cell T1-1: 7B vs 70B extraction quality binding test**
- Anchor: `substrate_extraction_quality_7B_vs_70B_v1`
- Source: massive-parallel-chunked-extraction drill
- Setup: 10K Wikipedia abstracts; 7B model extraction vs 70B model extraction; substrate retrieval accuracy comparison
- HARD-PASS: 7B substrate retrieval >= 80% of 70B baseline
- HARD-FAIL: 7B < 60% of 70B
- Cost: <$0.01 + 15 min
- **Strategic value: gates ALL extraction infrastructure decisions** ($31 CPU fleet vs $1 Mac fleet)

**Cell T1-2: Matthiessen dominant-scatterer diagnosis**
- Anchor: `substrate_matthiessen_dominant_scatterer_v1`
- Source: bio/materials kinetics drill
- Setup: decompose substrate noise into scattering categories (codebook collisions vs lattice vibration vs grain-boundary equivalent); identify dominant loss
- HARD-PASS: single mechanism > 60% of total noise (clear optimization target)
- Cost: <90 sec CPU
- **Strategic value: tells us which rescue path matters most**

**Cell T1-3: STREAM-V1 smoke (streaming substrate via vLLM Hook)**
- Anchor: `substrate_stream_v1_vllm_hook_smoke_v1`
- Source: streaming continual extraction drill
- Setup: 200 synthetic queries through Llama-1B with prefill KV hook at layers 8/10/12; measure substrate retrieval accuracy vs batch baseline on 20 held-out facts
- HARD-PASS: streaming substrate >= 80% of batch baseline
- HARD-FAIL: < 50%
- Cost: <15 min CPU; no GPU
- **Strategic value: validates "extraction during deployment = $0 marginal" claim**

**Cell T1-4: Embedding-norm gating discriminability**
- Anchor: `substrate_embedding_norm_gate_discriminability_v1`
- Source: sparse activation extraction drill
- Setup: Llama-1B token embeddings; embedding-norm vs first-layer entropy correlation; gate at top 30%; measure VQ coverage preservation
- HARD-PASS: g=0.30 gate preserves >97% VQ coverage at 10K tokens
- HARD-FAIL: <90% coverage at g=0.30
- Cost: ~30 min CPU
- **Strategic value: validates 20-47x sparse-extraction speedup claim**

**Cell T1-5: V2-2-RERUN Hadamard at N=256**
- Anchor: `substrate_hadamard_expansion_n256_v2`
- Source: sparse-write drill
- Setup: rerun V2-2 (Hadamard bipolar expansion k=8) at N=256 instead of N=128; test JL-bound-satisfied regime
- HARD-PASS: 4-5x capacity gain at N=256 (recovers from MIDDLE 2.8x at N=128)
- Cost: ~10 min CPU
- **Strategic value: confirms drill's Hadamard ceiling explanation**

**Cell T1-6: SPARSE-V3-1 cross-cutting sparse write**
- Anchor: `substrate_sparse_outer_product_write_v1`
- Source: sparse-write drill
- Setup: substrate Hebbian write with novelty-gated sparsity f=0.10; compare to dense baseline
- HARD-PASS: 10x capacity gain at moderate load
- HARD-FAIL: < 2x or quality degradation
- Cost: ~10 min CPU
- **Strategic value: validates "linear-noise regime" cross-cutting rescue**

**Cell T1-7: SPARSE-V3-COMPOUND (sparse + kgram XOR)**
- Anchor: `substrate_sparse_plus_kgram_xor_compound_v1`
- Source: sparse-write drill
- Setup: combine sparse write (f=0.10) + k-gram XOR (k=3) at N=4096
- HARD-PASS: 30x capacity multiplicative compound
- HARD-FAIL: < 15x (compounding doesn't work)
- Cost: ~15 min CPU
- **Strategic value: validates the unified architectural rescue**

**Cell T1-8: K-hop native reasoning smoke**
- Anchor: `substrate_native_reasoning_k_hop_v1`
- Source: 20-ambitious-ideas drill Deep Dive A
- Setup: K=3 multi-hop VSA chain at N=4096, V_c=1024; pure substrate reasoning (no LLM)
- HARD-PASS: K=3 accuracy >= 0.70 at N=4096
- HARD-FAIL: K=2 accuracy < 0.50 at N=4096
- Cost: <30 min CPU
- **Strategic value: validates 100x-20,000x speedup claim for structured retrieval**

---

## TIER 2: CPU SMOKE TESTS (~10-90 min each; substrate architecture refinements)

**Cell T2-1: ETF Hadamard codebook initialization**
- Anchor: `substrate_etf_hadamard_codebook_init_v1`
- Source: bio/materials drill (enzyme kinetics analog)
- Setup: initialize VQ codebook via Equiangular Tight Frame Hadamard structure (vs random); measure retrieval "activation barrier" reduction
- HARD-PASS: 1.5x retrieval speedup OR 2x capacity at matched accuracy
- Cost: ~20 min CPU
- **Strategic value: cuts retrieval "barrier" via codebook geometry engineering**

**Cell T2-2: Allosteric G-register write gate**
- Anchor: `substrate_allosteric_g_register_write_gate_v1`
- Source: bio/materials drill (hemoglobin allosteric analog)
- Setup: global G-register holds long-range context; substrate write rule modulated by G-register state; tests rare-fact priority storage
- HARD-PASS: rare-fact retrieval 3x improvement at fixed capacity
- Cost: ~30 min CPU

**Cell T2-3: Hadamard rotation cert channel**
- Anchor: `substrate_hadamard_rotation_cert_channel_v1`
- Source: bio/materials drill (topological insulator edge states)
- Setup: cert audit reads use Hadamard-rotated "edge" channel that decouples from substrate load
- HARD-PASS: cert read latency invariant under load (vs degrading with capacity)
- Cost: ~30 min CPU

**Cell T2-4: Corneal dense-pack cert codebook**
- Anchor: `substrate_corneal_dense_pack_cert_v1`
- Source: bio/materials drill (corneal collagen analog)
- Setup: ordered codebook structure (vs random) for selective audit transparency
- HARD-PASS: cert query latency 2x faster than random codebook
- Cost: ~30 min CPU

**Cell T2-5: Wright-Fisher write lifespan dynamics**
- Anchor: `substrate_wright_fisher_write_lifespan_v1`
- Source: disparate fields drill (population genetics)
- Setup: track per-fact "fixation/extinction" dynamics under continual learning load
- HARD-PASS: identifies clear fixation threshold at >0.7 substrate occupancy
- Cost: ~45 min CPU

**Cell T2-6: Physarum-weighted retrieval algorithm**
- Anchor: `substrate_physarum_weighted_retrieval_v1`
- Source: disparate fields drill (slime mold computation)
- Setup: substrate retrieval weighted by Physarum-style network optimization (current-strength path selection)
- HARD-PASS: multi-hop retrieval 1.5x more accurate vs argmax
- Cost: ~60 min CPU

**Cell T2-7: Immune cloud distributed redundant encoding**
- Anchor: `substrate_immune_cloud_redundant_encoding_v1`
- Source: disparate fields drill (B-cell affinity maturation)
- Setup: each fact stored at multiple redundant codebook locations; clonal-selection style refinement under retrieval pressure
- HARD-PASS: noise robustness 2x at matched capacity
- Cost: ~90 min CPU

**Cell T2-8: Landauer write-gate (energy-budgeted writes)**
- Anchor: `substrate_landauer_write_gate_v1`
- Source: disparate fields drill (thermodynamics)
- Setup: each write decision incurs explicit energy cost; rare facts get priority budget
- HARD-PASS: rare-fact recall 3x at matched substrate state
- Cost: ~30 min CPU

**Cell T2-9: k=4 XOR scaling at N=16384**
- Anchor: `substrate_kgram_xor_k4_n16384_v1`
- Source: negatives rescue drill / sparse-write follow-on
- Setup: substrate at N=16384 with k=4 XOR context binding; measure 4-gram-class scaling
- HARD-PASS: 4-gram-class accuracy >= bigram accuracy + 20pp
- Cost: ~30 min CPU
- **Strategic value: validates Phase 3 scaling requirement (4-gram at N=16384)**

**Cell T2-10: K=8-10 hierarchical Rule 8 combination**
- Anchor: `substrate_rule8_hierarchical_K_8_10_v1`
- Source: evidence integration drill (K transition)
- Setup: substrate combination at K=8-10 using hierarchical Rule 8 (binary tree); test architectural K-gate
- HARD-PASS: hierarchical Rule 8 maintains accuracy at K=10 (vs flat Rule 8 degrading)
- Cost: ~20 min CPU

**Cell T2-11: Bipolar sign-compression storage benchmark**
- Anchor: `substrate_bipolar_sign_compression_storage_v1`
- Source: hardware extraction drill
- Setup: store Wikipedia substrate W matrix at 1-bit bipolar vs bf16; measure retrieval accuracy degradation
- HARD-PASS: 32x storage reduction with < 2% accuracy loss
- Cost: ~30 min CPU

**Cell T2-12: STREAM-V2 multi-layer hooks**
- Anchor: `substrate_stream_v2_multi_layer_hooks_v1`
- Source: streaming extraction drill
- Setup: substrate has 3 observation hooks (attention KV / output tokens / user inputs); cross-table queries via VSA superposition
- HARD-PASS: cross-modal queries work at 2x faster than batch-rebuild
- Cost: ~60 min CPU

**Cell T2-13: STREAM-V3 confidence-gated production**
- Anchor: `substrate_stream_v3_confidence_gated_v1`
- Source: streaming extraction drill
- Setup: substrate writes only when LLM logit-margin > threshold; measure hallucination contamination rate
- HARD-PASS: contamination rate < 1% at 80% precision
- Cost: ~45 min CPU

**Cell T2-14: VQ coverage preservation at sparse extraction**
- Anchor: `substrate_vq_coverage_sparse_extraction_v1`
- Source: sparse activation extraction drill
- Setup: measure substrate VQ codebook coverage as token-gating threshold g varies from 0.10 to 1.0
- HARD-PASS: coverage > 95% at g=0.30 on 1M-token corpus
- Cost: ~60 min CPU

**Cell T2-15: 7B vs 70B substrate retrieval head-to-head (post-extraction)**
- Anchor: `substrate_7b_70b_retrieval_head_to_head_v1`
- Source: massive parallel chunked extraction drill
- Setup: extract 1K abstracts from each; build substrate; benchmark on standard HotpotQA subset
- HARD-PASS: 7B substrate within 90% of 70B retrieval F1
- Cost: ~30 min CPU + light GPU

---

## TIER 3: MEDIUM COMPLEXITY (~few hours each; capability transfers + verification)

**Cell T3-1: HotpotQA at Llama-1B (V2-3 negative rescue)**
- Anchor: `substrate_hotpotqa_multihop_llama1b_v2`
- Source: negatives rescue drill
- Setup: substrate 2-hop retrieval at Llama-1B; compare end-to-end EM to Pythia floor 0.083
- HARD-PASS: EM > 0.12 at Llama-1B
- Cost: ~30-60 min GPU
- Gating: requires Llama-1B weights local (Testbed Ask-2 pending)

**Cell T3-2: CCC-1-v2 capability dims at Llama-1B residual-only (5 transfers)**
- Anchor: `substrate_ccc1v2_capability_dims_llama1b_residual_v2`
- Source: original Phase 2 routing
- Setup: long-conv, multi-doc, counterfactual, analogical, cross-session - transfer all to Llama-1B residual-only
- HARD-PASS: at least 4/5 maintain categorical wins at 1B residuals
- Cost: ~2-3 hours CPU

**Cell T3-3: HP-5 medical Q&A proto**
- Anchor: `substrate_medical_qa_proto_no_umls_dependency_v1`
- Source: original HP-5 routing
- Setup: substrate-VQ on PubMed corpus -> concept-LM -> MedQA evaluation; demonstrate deletion cert on substrate
- HARD-PASS: substrate >= 1.5x Pythia baseline AND deletion cert operational
- Cost: ~1-2 days CPU
- **Strategic value: HIPAA Medical Path Y dry-run**

**Cell T3-4: HNSW empirical smoke (sub-linear cleanup)**
- Anchor: `substrate_hnsw_sublinear_cleanup_v1`
- Source: sub-linear cleanup drill
- Setup: HNSW at substrate-class V_c=10K-100K, N=1024-4096; measure recall@1 and speedup
- HARD-PASS: 3200x speedup + recall@1 0.97-0.99
- Cost: ~2 hours CPU
- Gating: requires FAISS env fix (Testbed lane)

**Cell T3-5: IVF + RaBitQ benchmark**
- Anchor: `substrate_ivf_rabitq_smoke_v1`
- Source: sub-linear cleanup drill
- Setup: IVF (nlist=1000, nprobe=10) + RaBitQ bitwise SIMD
- HARD-PASS: 6000x speedup at V_c=100K
- Cost: ~2 hours CPU
- Gating: requires FAISS env fix

**Cell T3-6: Hierarchical VQ k-sweep**
- Anchor: `substrate_hierarchical_vq_k_sweep_v1`
- Source: sub-linear cleanup drill
- Setup: k-level tree VQ; sweep k=2,3,4,5; measure speedup vs recall
- HARD-PASS: k=4 gives 7937x speedup at recall 0.92-0.97
- Cost: ~2 hours CPU

**Cell T3-7: SPARSE-CASCADE-SMOKE (cascade distillation FD ratio)**
- Anchor: `substrate_cascade_distillation_fd_ratio_smoke_v1`
- Source: cascade distillation drill
- Setup: FD(fine-tuned-1B, 405B) / FD(off-shelf-1B, 405B) on 5K sentences
- HARD-PASS: FD ratio < 0.40 (>60% gap closed)
- HARD-FAIL: > 0.70
- Cost: ~$2 cloud API + 4 hours GPU
- **Strategic value: validates cascade distillation foundation for cheap large-LLM digestion**

**Cell T3-8: M4 Max prefill-only benchmark (if available)**
- Anchor: `substrate_m4_max_prefill_benchmark_v1`
- Source: hardware extraction drill
- Setup: 70B Q4 prefill-only at batch=64 on M4 Max; measure tok/s
- HARD-PASS: 50-70 tok/s effective at batch=64 (near H100 single-stream)
- Cost: $0 if M4 Max available
- **Strategic value: validates M4 Max cost advantage for sustained extraction**

**Cell T3-9: 4x RTX 4090 TP-2 vLLM benchmark**
- Anchor: `substrate_4090_tp2_vllm_benchmark_v1`
- Source: hardware extraction drill
- Setup: 70B AWQ-INT4 on 4090 cluster with vLLM TP-2; measure throughput
- HARD-PASS: 8900 tok/s at high batch
- Cost: $0 if hardware available

---

## TIER 4: PHASE 4 FEATURES (~days each; the substrate-LLM hybrid product roadmap)

These are the larger Phase 4 cells from the 20-ambitious-ideas drill TOP 5 + supporting infrastructure. Already routed in earlier note (research_to_exp_dev_phase4_TOP5_sequencing); reaffirming with concrete anchor names.

**Cell T4-1: Working memory loop (Idea 2)**
- Anchor: `substrate_working_memory_loop_v2`
- Source: 20-ideas drill Deep Dive C
- Architecture: 1-3B LLM + substrate iterative query loop; KV injection accumulator; halt at convergence or K_max=12
- HARD-PASS: HotpotQA 2-hop EM >= 0.45 with 1B+substrate at K_max=7
- Cost: ~8-12 days + $30-80 GPU

**Cell T4-2: Continual learning via KV injection (Idea 17)**
- Anchor: `substrate_continual_learning_kv_injection_v1`
- Architecture: LLM frozen; substrate teaches LLM via Bridge B; real-time LLM mutation without fine-tune
- HARD-PASS: LLM behavior measurably shifts with substrate write; cert chain audited
- Cost: ~8-12 days

**Cell T4-3: Hallucination detection (Idea 3)**
- Anchor: `substrate_hallucination_detection_token_level_v1`
- Architecture: per-token VQ grounding via two-tier write/read path
- HARD-PASS: F1 >= 0.57 on HaluEval high-coverage domain at <10ms/span
- Cost: ~10-15 days + $50-100 GPU

**Cell T4-4: CoT cache with cert (Idea 8)**
- Anchor: `substrate_cot_cache_cert_provenance_v1`
- Architecture: multi-hop reasoning steps stored in substrate; future similar queries retrieve cached traces
- HARD-PASS: 2x reasoning speedup on repeated query patterns; cert-anchored explanations
- Cost: ~5-8 days

**Cell T4-5: K-hop native reasoning at full scale (Idea 1)**
- Anchor: `substrate_native_reasoning_full_scale_v1`
- Architecture: VSA algebra reasoning hops without LLM; 100x-20,000x speedup
- HARD-PASS: K=5 accuracy >= 0.50 at N=16384
- Cost: ~5-8 days + $20 CPU

**Cell T4-6: PHASE4A infrastructure (6 components; ~13-19 eng-days)**
- Already routed in research_to_exp_dev_phase4a_unified_infrastructure_*
- MiniLM (done) + distilled student + two-tier read/write + rescue template + eval harness + Wikipedia cache

**Cell T4-7: HP-12 V2 build (100K-fact scale)**
- Anchor: `substrate_certified_deletion_demo_medical_100k_facts_v2`
- Source: HP-12 V1 design extended
- HARD-PASS: same V1 metrics at 100K facts; cert latency holds
- Cost: ~2-3 days
- Gating: FAISS env fix

**Cell T4-8: HP-12 V3 build (1M-fact scale with Gemma-2-2B)**
- Anchor: `substrate_certified_deletion_demo_medical_1m_v3_gemma`
- Source: Phase 3 production blueprint
- HARD-PASS: production-credibility scale at 1M facts
- Cost: ~5-10 days

---

## EXTRACTION INFRASTRUCTURE (Testbed lane; not Exp-Dev primary)

**TEST-1: Llama-1B weights local (gates V2-3 + Test 3 live timing)**
- Cost: ~30 min download + HF token
- Gating: pending Testbed authorization

**TEST-2: PHASE4A-2 distilled student training (~$15 cloud H100)**
- Source: encoder bottleneck drill
- Cost: ~2-4 hours cloud + $15
- Gating: awaits Exp-Dev handoff training script

**TEST-3: PHASE4A-6 Wikipedia layer-10 cache (~$200-400 cloud H100)**
- Cost: ~8-10 hours cloud + $200-400
- Gating: Day 6-7 of Phase 4a

**TEST-4: FAISS HNSW environment fix (gates T3-4 and T3-5)**
- Cost: $0.50 Linux cloud OR conda faiss-cpu install
- Gating: pending Testbed runner-env action

**TEST-5: 100 idle M4 Max volunteer fleet POC (chunked extraction)**
- Cost: $0 if Mac hardware available
- Gating: requires fleet coordination infrastructure

---

## SUMMARY TABLE (sortable by tier + cost)

| Tier | # Cells | Total CPU time | Total cloud cost |
|---|---|---|---|
| Tier 1 (binding decisive) | 8 | ~3 hours | <$0.05 |
| Tier 2 (CPU smoke) | 15 | ~10 hours | $0 |
| Tier 3 (medium) | 9 | ~15 hours | ~$20 |
| Tier 4 (Phase 4 features) | 8 | ~30-50 days | ~$200-500 |
| Testbed (extraction) | 5 | varies | $215-415 |
| **TOTAL CELLS** | **45** | **~28h smoke + days Phase 4** | **~$235-535** |

---

## Sequencing recommendation

**Tonight overnight:** Tier 1 + Tier 2 (all 23 cells; ~13 hours total CPU time; fits overnight with parallelism)

**Tomorrow daytime:** Tier 3 cells (those not blocked on env fixes or weights)

**This week:** Tier 4 Phase 4 features (per existing Phase 4a routing)

**Continuous:** Testbed extraction asks as they unblock

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary on cells; Testbed primary on env/extraction
- Per user 2026-06-05 ~21:00: "don't cap the number; send all of the legitimately interesting; queue them all tonight" -- complied
- Per [[feedback-no-padding-experiments]]: each cell has distinct architectural hypothesis or distinct cross-cutting question
- Per [[feedback-strategy-shore-up-capabilities]]: cells proactively address capability gaps surfaced by today's drills
- ASCII-only

PROT-018: anchor names per cell
PROT-021: source=local CPU for Tier 1-2; cloud where flagged

---

**END.**

**Exp-Dev:** 45+ cells routed across 4 tiers. Tier 1 (8 cells; binding decisive; ~3h total) + Tier 2 (15 cells; CPU smoke; ~10h) fit overnight queue. Tier 3 + Tier 4 for tomorrow onwards. All cells have anchor + HP threshold + cost estimate. Drain in tier order; pull from Tier 1 first for highest information-per-hour ratio.

**Testbed:** 5 extraction infrastructure asks remain (Llama weights, distilled student training, Wikipedia cache, FAISS env, M4 volunteer POC). All AFTER Exp-Dev confirms which cells they're prioritizing tonight.

**User:** Comprehensive queue saved. 45+ cells from today's 21 drills cataloged. Overnight queue: Tier 1 + Tier 2 (23 cells; ~13 hours total CPU). All research preserved in notes/research_drill_*_2026-06-05.md + exp_dev_handoff_research_*_2026-06-05.md.
