# PRIORITY_QUEUE_LIVE -- Research-owned single-source-of-truth experiment queue

**Owner:** Research session
**Consumer:** Exp-Dev (pulls from top when runner slot opens)
**Inform:** Testbed + Orchestrator + User
**Last updated:** 2026-06-06 ~08:30 (v3 -- pared down per user audit)
**Version:** 3

---

## How this works

- Research keeps this list rank-ordered + current
- Exp-Dev pulls from the TOP whenever a runner slot opens
- Pull = build (if needed) + queue + run + report verdict
- After verdict reported: Research crosses off + adds new cells per latest strategic state
- Empty list = idle is correct (no padding)
- Re-runs are explicit additions by Research (varied-seed only, when CI/variance gates a decision)

---

## TIER-1 ACTIVE (5 cells; rank order; aligned with current strategy)

### Slot 1: `capacity_sweep_n32768_asymptotic_alpha_v1`
- **Wall:** ~5 min CPU
- **Source:** today's 2x alpha drill (cycle 116 LVH catch rescue)
- **Gates:** Phase 3 N=65536 capacity commitment
- **HP threshold:** alpha in [0.036, 0.044] at N=32768
- **Why:** cheapest decisive test before committing to Phase 3 production blueprint

### Slot 2: `n3_cubic_tensor_capacity_n4096_v1` (BUILD; multi-day)
- **Wall:** ~1-2 days engineering (sparse cubic tensor impl) + smoke
- **Source:** today's 2x alpha drill -- Tier-1 BLOCKER
- **Gates:** Phase 3 Wikipedia-class capacity claim (~10^9 facts)
- **HP threshold:** C_3 prefactor > 0; M_max scales as N^2
- **Why:** the entire Phase 3 "facts explosion" depends on this; without it, Wikipedia-class is algebra-only
- **Status:** needs engineering build; starts in parallel with other Tier-1 cells

### Slot 3: `substrate_matthiessen_dominant_scatterer_v1`
- **Wall:** ~90 sec CPU
- **Source:** yesterday's bio/materials drill
- **Gates:** which substrate optimization mechanism matters most
- **HP threshold:** single mechanism > 60% of total noise
- **Why:** super cheap diagnostic; directly informs Phase 4a infrastructure focus

### Slot 4: `sparse_vs_dense_write_regime_alpha_n4096_n16384_v1`
- **Wall:** ~15 min CPU
- **Source:** today's 2x alpha drill -- rescue path
- **Gates:** whether sparse write rule recovers alpha > 0.040 at large N
- **HP threshold:** sparse alpha >= 0.055 at large N

### Slot 5: `substrate_sparse_outer_product_write_v2` + `substrate_sparse_plus_kgram_xor_compound_v2`
- **Wall:** ~45 min CPU total
- **Source:** Exp-Dev's metric-fix re-route from yesterday
- **Gates:** cross-cutting sparse-write rescue (10x base + 30x compound)
- **HP threshold:** 10x M_max at f=0.10 (V2); 30x compound (V3)
- **Metric:** auto-associative + flip-corrupted cue + unique patterns + 0.95 accuracy

---

## TIER-1 VARIED-SEED RE-RUNS (only after seed-randomization flag added)

### Slot V1: `substrate_capacity_scaling_sweep_xl_v1` at seeds=10
- **Why:** effective_n=2-3 currently; need real CI for alpha=0.040 before Phase 3 commitment
- **Action:** Exp-Dev adds seed-randomization flag THEN re-runs

### Slot V2: `exp_hp12_v2_crypto_2048_gmpy2_latency_v1` at seeds=10
- **Why:** n=2 independent measurements currently; spec-sheet CI for HP-12 V2

---

## TIER-2 (good cells but not blocking; queue when Tier-1 drains)

Reorganized from Tier-1 per audit:
- `substrate_native_reasoning_k_hop_v1` (30 min CPU; validates Idea 1 from 20-ideas TOP 5)
- `substrate_embedding_norm_gate_discriminability_v1` (30 min CPU; Phase 3 prep for sparse extraction speedup)
- `substrate_hadamard_expansion_n256_v2` full run (10 min; already 3.0x preliminary)

Yesterday's bio/materials + disparate fields cells (lower priority given overnight HPs already validated several substrate axes):
- T2-1 ETF Hadamard codebook init (~20 min)
- T2-2 Allosteric G-register write gate (~30 min)
- T2-3 Hadamard rotation cert channel (~30 min)
- T2-4 Corneal dense-pack cert codebook (~30 min)
- T2-5 Wright-Fisher write lifespan (~45 min)
- T2-6 Physarum-weighted retrieval (~60 min)
- T2-7 Immune cloud encoding (~90 min)
- T2-8 Landauer write-gate (~30 min)
- T2-9 k=4 XOR at N=16384 (~30 min)
- T2-10 K=8-10 hierarchical Rule 8 (~20 min)
- T2-11 Bipolar sign-compression storage (~30 min)
- T2-12 STREAM-V2 multi-layer hooks (~60 min)
- T2-13 STREAM-V3 confidence-gated (~45 min)

Pull from this list ONLY when Tier-1 is empty.

---

## TIER-CLOUD (truly active; 2 cells; user authorization required per cell)

### CLOUD-1: 7B vs 70B extraction quality binding test
- **Anchor:** `substrate_extraction_quality_7B_vs_70B_v1`
- **Cost:** ~$0.50-1.00 cloud H100 (prefill-only)
- **Wall:** ~15-20 min
- **Gates:** ALL extraction infrastructure decisions (cheap CPU fleet vs M4 fleet vs continued cloud H100)
- **HARD-PASS:** 7B substrate retrieval >= 80% of 70B baseline

### CLOUD-2: PHASE4A-2 distilled 22-26M student training
- **Anchor:** `substrate_distilled_22m_student_training_v1`
- **Cost:** ~$15 cloud H100
- **Wall:** ~2-4 hours
- **Gates:** V_c=1M production scale + 20-40x extraction speedup forever after
- **Status:** awaits Exp-Dev handoff training script

---

## CLOUD-ROADMAP (future cells; not active queue; need additional gating)

Listed for visibility; do NOT dispatch without explicit user re-authorization + gating dependencies met:

- **Cascade distillation FD smoke** ($2; only matters if CLOUD-1 says we need bigger LLM)
- **Llama-8B Tier-4 replication** -- user DEPRIORITIZED 2026-06-05; do not run
- **Wikipedia layer-10 cache** ($30-400) -- need to know which model to extract from first
- **HP-12 V2 build at 100K** -- gated on FAISS env fix + cubic-tensor empirical
- **Gemma-2-2B extraction** -- Phase 3 production launch concern (weeks out)
- **HP-12 V3 build at 1M** -- gated on Gemma extraction + cubic-tensor
- **M4 Max volunteer fleet POC** -- requires coordination infrastructure that doesn't exist
- **Full Wikipedia 7B chunked extraction** ($31) -- gated on CLOUD-1 + chunking infra

---

## TIER-3 (gated on environment fixes; Testbed lane)

- T1-3 STREAM-V1 vLLM Hook smoke (needs vLLM install)
- HNSW empirical (gates HP-12 V2; needs FAISS env fix)
- IVF + RaBitQ smoke (needs FAISS env)
- Hierarchical VQ k-sweep (needs FAISS env)
- HotpotQA at Llama-1B (needs Llama-1B weights local download)

---

## TIER-4 (Phase 4 features; multi-day eng work; not queue-drainable cells)

- Working memory loop (Idea 2; partially anchored overnight via real-encoder transfer + continual KV)
- Continual learning via KV (Idea 17; partially anchored overnight via continual KV HP)
- Hallucination detection (Idea 3; partially anchored overnight via KF-1 HP at MiniLM)
- CoT cache with cert (Idea 8)
- K-hop native reasoning full scale (after Slot 5 smoke if HP)

---

## DO NOT QUEUE (re-runs of completed cells with deterministic results)

- KF-1 hallucination detection (AUC=0.999 with MiniLM) -- STABLE
- Real-encoder capability transfer (1.000) -- STABLE
- Continual KV injection (99.8%) -- STABLE
- HP-12 V1 anchors -- STABLE
- 23 flagship anchors with deterministic results -- STABLE

Re-runs at fixed seeds produce ZERO new information.

---

## CHANGELOG

- 2026-06-06 08:05 -- v1 created. 9 Tier-1 cells, 2 varied-seed re-runs, 15 Tier-2, 7 Tier-3, 7 Tier-4 phase features.
- 2026-06-06 08:15 -- v2: added TIER-CLOUD section with 10 ranked cloud experiments.
- 2026-06-06 08:30 -- v3 PARED DOWN per user audit: Tier-1 cut from 9 -> 5 (most strategically aligned); Tier-2 absorbs the rest (good but not blocking). TIER-CLOUD cut from 10 -> 2 (CLOUD-1 + CLOUD-2 only); rest moved to CLOUD-ROADMAP (future / gated; not active). Removed Llama-8B Tier-4 (user deprioritized).

---

**END.**

This file IS the queue priority. Exp-Dev pulls Slot 1 first; reports verdict; Research crosses off + updates; Exp-Dev pulls Slot 2; etc. Brief idle gaps when Tier-1 + Tier-2 drain are correct -- do not pad with re-runs.
