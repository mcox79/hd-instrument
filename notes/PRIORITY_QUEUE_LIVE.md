# PRIORITY_QUEUE_LIVE -- Research-owned single-source-of-truth experiment queue

**Owner:** Research session
**Consumer:** Exp-Dev (pulls from top when runner slot opens)
**Inform:** Testbed + Orchestrator + User
**Last updated:** 2026-06-06 ~08:05
**Version:** 1 (initial)

---

## How this works

- Research keeps this list rank-ordered + current
- Exp-Dev pulls from the TOP whenever a runner slot opens
- Pull = build (if needed) + queue + run + report verdict
- After verdict reported: Research crosses the cell off + adds new cells per latest strategic state
- Empty list = idle is correct (no padding)
- Re-runs are explicit additions by Research (varied-seed only, when CI/variance gates a decision)

---

## TIER-1 ACTIVE (do these next; rank order)

### Slot 1: `capacity_sweep_n32768_asymptotic_alpha_v1`
- **Wall:** ~5 min CPU
- **Source:** today's 2x alpha drill (cycle 116 LVH catch rescue)
- **Gates:** Phase 3 N=65536 capacity commitment
- **HP threshold:** alpha in [0.036, 0.044] at N=32768
- **Why first:** cheapest decisive test before committing to Phase 3 production blueprint

### Slot 2: `n3_cubic_tensor_capacity_n4096_v1` (BUILD; multi-day)
- **Wall:** ~1-2 days engineering (sparse cubic tensor impl) + smoke
- **Source:** today's 2x alpha drill -- Tier-1 BLOCKER
- **Gates:** Phase 3 Wikipedia-class capacity claim (~10^9 facts)
- **HP threshold:** C_3 prefactor > 0; M_max scales as N^2
- **Why second:** the entire Phase 3 "facts explosion" depends on this; without it, Wikipedia-class is algebra-only
- **Status:** needs engineering build before smoke

### Slot 3: `sparse_vs_dense_write_regime_alpha_n4096_n16384_v1`
- **Wall:** ~15 min CPU
- **Source:** today's 2x alpha drill -- Tier-2 rescue path
- **Gates:** whether sparse write rule recovers alpha > 0.040 at large N
- **HP threshold:** sparse alpha >= 0.055 at large N
- **Why third:** rescue path if Cell 1 cubic-tensor is harder than expected

### Slot 4: `substrate_matthiessen_dominant_scatterer_v1`
- **Wall:** ~90 sec CPU
- **Source:** yesterday's bio/materials drill
- **Gates:** which substrate optimization mechanism matters most
- **HP threshold:** single mechanism > 60% of total noise
- **Why fourth:** super cheap diagnostic; directly informs Phase 4a infrastructure focus

### Slot 5: `substrate_native_reasoning_k_hop_v1`
- **Wall:** ~30 min CPU
- **Source:** 20-ambitious-ideas drill Deep Dive A
- **Gates:** 100x-20,000x speedup claim for structured retrieval; Idea 1 from TOP 5
- **HP threshold:** K=3 accuracy >= 0.70 at N=4096, V_c=1024
- **Why fifth:** validates a major categorical capability (LLM-free reasoning)

### Slot 6: `substrate_sparse_outer_product_write_v2` (T1-6-V2 with proper metric)
- **Wall:** ~20 min CPU
- **Source:** Exp-Dev's metric-fix re-route
- **Gates:** cross-cutting sparse-write rescue (NeurIPS 2023 linear-noise regime)
- **HP threshold:** 10x M_max at f=0.10 vs dense
- **Metric:** auto-associative + flip-corrupted cue + unique patterns + 0.95 accuracy

### Slot 7: `substrate_sparse_plus_kgram_xor_compound_v2` (T1-7-V2)
- **Wall:** ~25 min CPU
- **Source:** Exp-Dev's metric-fix re-route
- **Gates:** 30x multiplicative compound of sparse + kgram XOR
- **HP threshold:** M_max_ratio >= 30 at N=4096
- **Metric:** same as Slot 6

### Slot 8: `substrate_embedding_norm_gate_discriminability_v1` (T1-4)
- **Wall:** ~30 min CPU
- **Source:** sparse activation extraction drill
- **Gates:** 20-47x extraction speedup claim
- **HP threshold:** g=0.30 gate preserves >97% VQ coverage at 10K tokens
- **Data:** uses existing Llama-1B npz residuals

### Slot 9: `substrate_hadamard_expansion_n256_v2` (T1-5; full run)
- **Wall:** ~10 min CPU
- **Source:** sparse-write drill (preliminary 3.0x; full run pending)
- **Gates:** Hadamard expansion ceiling explanation
- **HP threshold:** 4-5x at N=256 (recovers from 2.8x at N=128)

---

## TIER-1 VARIED-SEED RE-RUNS (only after seed-randomization flag added)

### Slot V1: `substrate_capacity_scaling_sweep_xl_v1` at seeds=10
- **Why:** effective_n=2-3 currently; need real CI for alpha=0.040 before Phase 3 commit
- **Action:** Exp-Dev adds seed-randomization flag THEN re-runs

### Slot V2: `exp_hp12_v2_crypto_2048_gmpy2_latency_v1` at seeds=10
- **Why:** n=2 independent measurements currently; spec-sheet CI for HP-12 V2
- **Action:** same as V1

---

## TIER-2 BACKLOG (15 cells; ~10h CPU; pull when Tier-1 drains)

Per yesterday's OVERNIGHT_QUEUE note + bio/materials drill + disparate fields drill:

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
- T2-14 VQ coverage at sparse extraction (~60 min)
- T2-15 7B vs 70B substrate retrieval head-to-head (~30 min; depends on T1-1)

---

## TIER-3 (gated on infrastructure or larger investment; queue when unblocked)

- T1-1 7B vs 70B extraction quality (needs cloud auth)
- T1-3 STREAM-V1 vLLM Hook smoke (needs vLLM install)
- HotpotQA at Llama-1B (needs Llama-1B weights)
- HNSW empirical (gates HP-12 V2; needs FAISS env fix)
- IVF + RaBitQ smoke (needs FAISS env)
- Hierarchical VQ k-sweep (needs FAISS env)
- SPARSE-CASCADE-SMOKE FD ratio (~$2 + 4h GPU)

---

## TIER-4 PHASE 4 FEATURES (multi-day eng work; not queue-drainable cells)

- Working memory loop (Idea 2; 8-12 days)
- Continual learning via KV (Idea 17; partially anchored overnight)
- Hallucination detection (Idea 3; partially anchored overnight)
- CoT cache with cert (Idea 8; 5-8 days)
- K-hop native reasoning full scale (after Slot 5 smoke)
- HP-12 V2 build (100K facts; gates on FAISS env)
- HP-12 V3 build (1M facts with Gemma-2-2B)

---

## DO NOT QUEUE (re-runs of completed cells with deterministic results)

- KF-1 hallucination detection (AUC=0.999 with MiniLM) -- STABLE
- Real-encoder capability transfer (1.000) -- STABLE
- Continual KV injection (99.8%) -- STABLE
- HP-12 V1 anchors -- STABLE
- 23 flagship anchors with deterministic results -- STABLE

Re-runs at fixed seeds produce ZERO new information. Adding to skiplist.

---

## CHANGELOG

- 2026-06-06 08:05 -- v1 created. 9 Tier-1 cells, 2 varied-seed re-runs, 15 Tier-2, 7 Tier-3, 7 Tier-4 phase features.

---

**END.**

This file IS the queue priority. Exp-Dev pulls Slot 1 first; reports verdict; Research crosses off + updates; Exp-Dev pulls Slot 2; etc. Brief idle gaps when Tier-1 + Tier-2 drain are correct -- do not pad with re-runs.
