# exp_dev hand-off -- research: substrate-aware LLM continual learning 2x

**Filed-by:** research sub-agent
**Date:** 2026-06-07
**Trigger:** Research drill on Tier 4 LLM inheriting substrate continual learning capability
**Research note:** d:/AI/hd-instrument/notes/research_drill_substrate_aware_llm_continual_learning_2x_2026-06-07.md
**Pause state:** check data/orchestrator_paused.flag before dispatching; do not queue if paused

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchor candidates and context only. Exp_dev designs the actual experiment scripts.

---

## Anchor candidates (rank-ordered)

### 1. Pre-test A: vocabulary injection generalization (HIGHEST PRIORITY)

**Anchor pointer:** `substrate_tier4_vocab_injection_generalization_pretest_v1`
**Substrate-product reading:** Tests whether a frozen Llama-1B can use the substrate retrieval interface to correctly answer questions requiring NEW vocabulary injected via sparse-KEY after the LLM training cutoff. This is the PRETRAINING DIVERSITY REQUIREMENT test -- if it fails, Tier 4 curriculum design must start from scratch before any further Tier 4 investment.
**Tier hint:** CPU (no GPU needed; Llama-1B + substrate vocab inject is laptop-scale)
**Why now:** Pre-test must gate all Tier 4 engineering investment. Cycle 154 confirmed the substrate write side (sparse-KEY HP). This tests the read side. 1-2 hour wall on laptop, $0.
**Pre-reg:** HARD-PASS >= 85% retrieval accuracy on new vocab; HARD-FAIL < 50%

### 2. Pre-test B: LoRA adapter orthogonal update stability

**Anchor pointer:** `substrate_tier4_lora_orthogonal_update_stability_pretest_v1`
**Substrate-product reading:** Tests whether rank-4 LoRA adapter (targeting query-generation projection only) can absorb a new substrate domain (domain B) without degrading retrieval quality on old domain (domain A). Directly measures whether Option D (hybrid frozen + LoRA) is viable or whether Option C (fully frozen, no LoRA) is required.
**Tier hint:** CPU (LoRA rank 4 on Llama-1B query projection is laptop-scale; 100 patterns per domain)
**Why now:** Cycle 156 established LoRA InfoNCE 66% floor. This test determines whether orthogonal subspace constraint (O-LoRA style) raises it far enough for Option D to be the production architecture.
**Pre-reg:** HARD-PASS domain A degrades < 5% after domain B update; HARD-FAIL > 20% degradation

### 3. Pre-test C: defrag retrieval consistency

**Anchor pointer:** `substrate_defrag_retrieval_consistency_pretest_v1`
**Substrate-product reading:** Verifies that substrate defrag (PCA whitening + pseudoinverse) preserves retrieval semantics on held-out test probes. This is the SLEEP DEFRAG TRANSPARENCY test -- if defrag disrupts retrieval, the zero-LLM-retraining path after defrag is broken.
**Tier hint:** CPU (substrate N=8192; 10k patterns; defrag is matrix ops; 30-minute laptop test)
**Why now:** Defrag is proposed in the production architecture (cycle 162) but its effect on retrieval consistency has not been explicitly measured. Cheap validation that should run before Tier 4 training investment.
**Pre-reg:** HARD-PASS >= 90% retrieval consistency pre/post defrag; HARD-FAIL < 70%

### 4. CONT-LRN-1 upgrade: substrate + LoRA adapter vs LLM fine-tune (VALIDATION)

**Anchor pointer:** `substrate_continual_learning_empirical_tier4_lora_vs_finetune_v1`
**Substrate-product reading:** Extends existing CONT-LRN-1 design (substrate Hebbian write speed vs LLM fine-tune) to include the thin LoRA adapter calibration step. Measures total wall time for full Tier 4 update cycle (substrate write + LoRA calibration) vs equivalent LLM fine-tune. This is the honest empirical anchor for the "1000x faster" pitch.
**Tier hint:** CPU for substrate write; GPU for LoRA calibration + LLM fine-tune baseline (~$5-15 cloud)
**Why now:** CONT-LRN-1 was already flagged as highest strategic value in research_to_exp_dev_gpu_optimization_continual_learning_2026-06-05.md. This version adds the LoRA step to make the wall-time comparison honest.
**Pre-reg:** HARD-PASS total Tier 4 update (write + LoRA) >= 100x faster than equivalent LLM fine-tune with matched retrieval quality; HARD-FAIL < 10x faster

---

## Context pointers

- Research note (full analysis): d:/AI/hd-instrument/notes/research_drill_substrate_aware_llm_continual_learning_2x_2026-06-07.md
- Prior continual learning routing: d:/AI/hd-instrument/notes/research_to_exp_dev_gpu_optimization_continual_learning_2026-06-05.md
- Streaming architecture context: d:/AI/hd-instrument/notes/research_drill_streaming_continual_extraction_2x_2026-06-05.md
- Production architecture reference: memory/production_architecture_locked_2026-06-07.md (Llama-1B BASE, PCA, bf16, N=65k)
- Cycle 156 LoRA InfoNCE result: data/exp_CONT-LRN-*/ or equivalent metrics.json

---

## Contract section

Exp_dev is authorized to:
- Design and queue pre-tests A, B, C (CPU, laptop, $0)
- Design CONT-LRN-1 upgrade (cloud only if pre-tests A/B/C all pass HARD-PASS)
- Use existing Llama-1B BASE + substrate at N=8192 for pre-tests (no new model download needed)
- Use rank-4 LoRA targeting query projection layer only (not full LLM)

Exp_dev is NOT authorized to:
- Design a full Tier 4 curriculum from scratch without pre-test A HARD-PASS result
- Run cloud GPU for CONT-LRN-1 upgrade before pre-tests A/B pass
- Modify substrate production architecture (Cycle 162 locked)

## Autonomy declaration

Exp_dev controls all experiment design, script writing, pre-reg bands, and queue routing. This file provides anchor candidates only. Exp_dev decides sequencing, smoke vs full, and parameter choices per its own role contract.
