# Stage 3 definition + chain-grade verification matrix + operating envelope per capability

**Date:** 2026-06-25
**Driver:** USER asked (a) "what is stage 3?", (b) "show that all required aspects are chain grade", (c) "where everything operates best within the phase diagram"

## What is Stage 3?

**Stage definitions** (from substrate-product taxonomy):
- **Stage 1 (base):** the primitive operations — sparse codebook, cleanup, HRR binding, continual learning, working memory. The substrate's hardware-equivalent layer.
- **Stage 2 (architecture):** the architectural patterns that compose primitives into deeper structures — FREQ_ROUTED_DEEPER, MULTIPLICATIVE_LEVER (and possibly SEGREGATED_DUAL_W pending Cell 2 v6). The substrate's instruction-set-equivalent layer.
- **Stage 3 (applications):** the user-facing capabilities built on Stage 1 + Stage 2 — intent classification, templated response, audit gate (subject + relation check), graph-health refuse, CSP uncertainty quantification, KG retrieval at scale, deletion/hallucination detection. The substrate's app-equivalent layer.
- **Stage 4 (LM-equivalence):** statistical language modeling at Shannon BPC. **Deferred per USER directive.** Not pursued.

**Stage 3 in plain English:** the things a user actually does with the substrate — ask a question, get an answer-with-confidence OR a refuse-with-reason, and trust the substrate's calibration to tell them whether to trust the answer.

## Chain-grade verification matrix (all required aspects)

For each capability: anchor name, verdict, cert ledger status, operating envelope (where it works best).

### Tier 1 — Base primitives (Stage 1)

| Capability | Anchor | Verdict | Cert | Operating envelope |
|---|---|---|---|---|
| Sparse-bipolar codebook (f≈0.02) | (foundational; embedded everywhere) | CHAIN_GRADE | YES (META) | f∈[0.02, 0.05] optimal; sparse_onset_alpha_c(f) measured for f∈[0.02, 0.03, 0.04, 0.05, 0.10] |
| Cleanup sigma0 ≥ 0.95 | (foundational; META rule) | CHAIN_GRADE | YES | N≥4096 for V≤1000; N=8192 for V≤4000 |
| HRR binding (2-hop) | (foundational) | CHAIN_GRADE | YES | depth ≤ 2 chain-grade; depth ≥ 3 REFUTED (Barrier 1) |
| Continual learning | a8_continual_writes_no_catastrophic_forgetting_v1 | CHAIN_GRADE | YES | forget=0.006 over 200 cycles; saturates near V·K/N atoms |
| Working memory | working_memory_hrr_slots_PRODUCTION_v1 | CHAIN_GRADE | YES | K≤32 perfect at sigma=1.0; K≤64 at sigma=0.5; K=128 at sigma=0; N_DIM=4096 |

### Tier 2 — Architecture (Stage 2)

| Capability | Anchor | Verdict | Cert | Operating envelope |
|---|---|---|---|---|
| FREQ_ROUTED_DEEPER | substrate_compose_freq_routing_v5_DEFINITIVE | CHAIN_GRADE_DEFINITIVE | YES (today) | N∈[4096, 8192] verified; n_steps=3000 plateau; +0.148 BPC over baseline |
| MULTIPLICATIVE_COMPOSITION_LEVER | multiplicative_composition_lever_v1_cpu_v1 | CHAIN_GRADE | YES | fabrication loads [1.0, 1.5] (high); never worse than always-chain |
| SEGREGATED_DUAL_W | substrate_compose_segregated_dual_W_context_gated_v1 | IN-FLIGHT (GPU) | PENDING | TBD (Cell 2 v6 landing) |

### Tier 3 — Applications (Stage 3)

| Capability | Anchor | Verdict | Cert | Operating envelope |
|---|---|---|---|---|
| Intent classifier | a1_substrate_intent_classifier_v1 | CHAIN_GRADE | YES | acc=0.754 at 50 intents N=8192; latency p95=0.54ms; n_llm=0 |
| Templated response | a2_substrate_templated_response_v1 | CHAIN_GRADE | YES | template count ≤ 100 verified |
| Audit refuse (subject+relation) | substrate_refuse_gate_near_domain_v2 | HARD_PASS_BOTH_WORK (today) | PENDING atomize | NEAR_DOMAIN_MIXED refuse=1.000; V_C_IN=600 N=8192 |
| Graph-health refuse | refuse_gate_5_graph_health_cpu_v1 | CHAIN_GRADE | YES | health-boundary at substrate state; reads state-not-load |
| CSP uncertainty quantification | csp_first_ship_v1 | CHAIN_GRADE | YES | 8.42× speedup; recall preserved 1.000→1.000 |
| Dense projected KV retrieval | dense_projected_KV_envelope_v1 | MM CHAIN_GRADE | YES | d=768, sigma=0.1, M≥10000 recall≥0.80, M-independent O(d²) |
| Sparse projected KV variant B | flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1 | CHAIN_GRADE | YES | f=0.02 sparse; shrinkage-ZCA whiten-before-topk |
| Per-cluster stratified extraction | substrate_per_cluster_stratified_extraction_with_random_control_v1 | CHAIN_GRADE | MISSING atom | sp=1000 stratified beats random by ≥0.40 |
| NESS graph traversal | kmax_ness_envelope_gpu_v1 | CHAIN_GRADE | MISSING atom | alpha∈[0.3, 0.7] safe; ext_hopfrac=1.0 across alpha |
| KV learned projection (encoder) | kv_learned_projection_v1 | CHAIN_GRADE | YES | recall≥0.70 held-out; beats analytic ceiling by >0.30 |
| Capacity sweet spot adaptive | capacity_sweet_spot_v1_cpu_v1 | CHAIN_GRADE | MISSING atom | beats fixed-f by ≥10% on high-load tasks |

### Tier 4 — Architectural principles (META)

| Principle | Atom | Verdict | Cert |
|---|---|---|---|
| Principle O (labels at use-case OK, basis HURT) | substrate_basis_layer_label_contamination_proof_v4 | CHAIN_GRADE_DEFINITIVE | YES (today) |
| Mu-Viswanath anisotropy bound | (embedded in Principle O cert) | CHAIN_GRADE | YES |
| Provenance rail config match | META rule | META_RULE | YES |
| Prospective bands fresh seeds | META rule | META_RULE | YES (today) |
| Cross-N replication as DEFINITIVE upgrade | META rule | META_RULE | YES (today) |
| Rail-discipline 3-rule (M2+M5+M6) | META rules | META_RULE | YES (M6 today) |
| Sigma0 cleanup integrity gate | META rule | META_RULE | YES |
| Per-arm metrics (Fix #28) | META rule | META_RULE | YES |

### Tier 5 — Honest negatives (also chain-grade evidence)

| Failure | Anchor | Verdict | Implication |
|---|---|---|---|
| Multi-hop consolidation | substrate_multihop_consolidation_v3 | HARD_FAIL (today) | Crosstalk-driven; semantic consolidation needs separate W |
| Pointer-chain hybrid | substrate_multihop_pointer_chain_hybrid_v2 | HARD_FAIL (today) | Compounding cleanup error |
| WM-scaffolded multi-hop | substrate_multihop_wm_scaffolded_v1 | HARD_FAIL (today) | WM holds intermediates but doesn't upgrade them |
| Lock-in frequency stacking (shared W) | substrate_compose_lock_in_frequency_stacking_v1 | MIDDLE_BAND (today) | FDM intermod on shared W |
| Foldiak anti-Hebbian (v1, v2 surgical) | substrate_unsupervised_anisotropic_encoder_biology_native_v1, v2 | HARD_FAIL | Axis-flip bug; v3 redesign deferred |

## Operating envelope phase diagram (where each works best)

```
                           CAPACITY (V or M)
                            |
                            |
        V≤1000  V=10000   V=100000  V=1M  V=10M
        ┌──────┬─────────┬────────┬──────┬──────┐
N=8192  │  ✓✓  │   ✓     │   ?    │  ?   │  ?   │  ← chain-grade cleanup; KV verified to 10k
        │      │         │        │      │      │
N=16384 │  ✓✓  │   ✓✓    │   ?    │  ?   │  ?   │  ← scaling unverified beyond M=10k
        │      │         │        │      │      │
N=32768 │  ?   │   ?     │   ?    │  ?   │  ?   │
        └──────┴─────────┴────────┴──────┴──────┘
            DEPTH = 1   DEPTH = 2   DEPTH ≥ 3
                ✓✓        ✓           ✗ (Barrier 1)
                                       
        SPARSITY: f∈[0.02, 0.05] optimal
        WM: K≤32 chain-grade; K=64 partial
        STAGE 2: FREQ_ROUTED_DEEPER + MULTIPLICATIVE_LEVER confirmed at N=4096 + N=8192
```

## What's missing for "all required aspects chain grade"

Today's pending:
- Cell 2 v2 refuse-gate (HARD_PASS_BOTH_WORK; needs atomize) ← Skunkworks
- WM-scaffolded multi-hop (HARD_FAIL today; needs atomize as honest_negative) ← Skunkworks
- Consolidation v3 (HARD_FAIL today; needs atomize) ← Skunkworks
- 4 older HARD_PASS missing from cert (NESS, capacity_sweet_spot, per_cluster_stratified, sparse_onset) ← Skunkworks back-fill
- Cell 2 v6 SEGREGATED + Cell H' v2b NO_FOLDIAK ← landing soon

In-flight verification:
- Cell 2 v6 SEGREGATED (Stage 2 mechanism #3 candidate)
- Cell H' v2b NO_FOLDIAK (biology-native encoder closure)

Once those land + cert back-fill completes, the substrate basis is FULLY chain-grade-attested across all required aspects.

## Operating-envelope gaps (what we don't know phase-diagram-wise)

1. **KV retrieval beyond M=10k** — chain-grade at 10k; unknown at 100k/1M. **Next-step 3 KG scale-up sweep addresses this.**
2. **Stage 2 at N > 8192** — FREQ_ROUTED_DEEPER cross-N at N=4096 + N=8192; unknown at N=16384+
3. **Continual learning beyond 200 cycles** — chain-grade at 200; unknown at 1000+
4. **Intent classification beyond 50 intents** — chain-grade at 50; unknown at 100+
5. **Integrated Stage 3 pipeline** — individual primitives verified; never tested composed end-to-end. **Next-step 2 integrated demo addresses this.**

— Research (Director)
