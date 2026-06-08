# Research -> Exp-Dev: TIER 5C FULL ROADMAP — most efficient path to substrate-intrinsic LLM

**From:** Research  **Date:** 2026-06-09 ~02:45 UTC
**Re:** User direction "route all experiments to identify exactly how to get 5c up and running in the most efficient way possible."

## Empirical state of Tier 5c (today's findings consolidated)

**Tier 5b empirical:**
- Single-position substrate vector inject FAILS (5 attempts; T5b-3 HF)
- Linear projection 89% train / 0% held-out (doesn't generalize)
- RMSNorm + residual dominates inject
- Diagnosis: needs FULL gated cross-attention TRAINED end-to-end multi-step

**Tier 5c surgical modification (per drills):**
- Substrate's FHRR Wirtinger-differentiable (structural advantage over LARS-VSA bipolar)
- LARS-VSA 2024 empirical: 17x memory + 25x speed
- GHRR-Transformer 2024 end-to-end language modeling
- GPT-2 weights explain as VSA bundling/binding (NeurIPS 2024 workshop)
- Substrate is NOT speed bottleneck (0.7% of inference; LLM is)

**Key insight:** the most efficient path is **NOT** from-scratch (LARS-VSA replica at small scale). **It IS** surgical modification of pretrained frontier LLM + continued training.

## 5-phase efficient path

### Phase A (cheap CPU + GPU smokes; GATES everything; sequence)

**T5C-A1: Differentiability probe** (CPU 20-30 min)
- 2-layer substrate-attention LM; gradient flow through complex FHRR binding
- HARD-PASS: loss decreases step 1→100; all gradients non-zero; codebook utilization > 0

**T5C-A2: Codebook quality on pretrained embeddings** (CPU 1-2 hr)
- Train substrate codebook (VQ-VAE-style) on word2vec/BERT embeddings; measure preservation
- HARD-PASS: substrate-projected embeddings retain ≥ 0.85 cosine vs original

**T5C-A3: GPU codebook retrieval benchmark** (LOCAL GPU 1-2 hr)
- Substrate codebook resident on GPU; retrieval via cuBLAS matmul
- HARD-PASS: <0.1ms per lookup at 100K-fact codebook (P95)

**T5C-A4: Substrate-LLM interface API** (CPU; engineering)
- Substrate as torch.nn.Module
- Forward: substrate.retrieve(hidden_state) → K/V tensors
- Backward: Wirtinger gradient flow
- Acceptance: torch.autograd.gradcheck passes

### Phase B (single-layer Pythia-160M; rung-1 validation)

**T5C-B1: Single-layer substrate-attention at Pythia-160M layer 6** (LOCAL GPU)
- Replace layer 6 attention with substrate-attention; continued training on WikiText-2
- HARD-PASS: perplexity within 2x of baseline + substrate retrievals demonstrably used

**T5C-B2: Multi-layer (2 adjacent layers) at Pythia-160M** (LOCAL GPU)
- Replace layers 6+7; same training
- HARD-PASS: perplexity within 3x of baseline

**T5C-B3: Layer-insertion-position study** (LOCAL GPU)
- Replace different layer positions (early=2, middle=6, late=10); compare perplexity
- HARD-PASS: identify best layer for substrate-attention insertion

### Phase C (multi-family validation; Pythia-1.4B + Qwen-1.5B)

**T5C-C1: Scale up to Pythia-1.4B single-layer** (LOCAL GPU)
- Same surgical pattern; larger base
- HARD-PASS: perplexity preservation + substrate usage

**T5C-C2: Qwen-2.5-1.5B-Instruct single-layer** (LOCAL GPU)
- Family-agnostic validation (Qwen instead of Pythia)
- HARD-PASS: same; family-agnosticism confirmed

**T5C-C3: Continued pretraining cost scaling** (LOCAL GPU)
- How many tokens to recover capability after modification?
- HARD-PASS: capability recovery within 100M-tokens of continued training

### Phase D (demo-quality; Qwen-2.5-3B+ surgical)

**T5C-D1: Qwen-2.5-3B-Instruct surgical at middle layer** (LOCAL/CLOUD GPU)
- 1-2 layer substitution; continued training
- HARD-PASS: downstream task performance within 90% of unmodified baseline

**T5C-D2: Qwen-2.5-7B-Instruct surgical** (CLOUD GPU; stretch)
- Larger; tests scale
- HARD-PASS: demo-grade fluency + substrate-intrinsic memory

**T5C-D3: Demo integration with Panel A** (LOCAL)
- Replace Panel A LLM with Tier 5c surgical Qwen
- HARD-PASS: integrated demo works end-to-end

### Phase E (R&D; alternative paths)

**T5C-E1: LARS-VSA replica at Pythia-160M scale** (LOCAL GPU)
- All-layer substrate-attention; from-scratch training; small corpus
- HARD-PASS: stable training + perplexity within 5x of small-transformer baseline

**T5C-E2: GHRR-Transformer replica** (LOCAL GPU)
- VSA-attention end-to-end language modeling
- HARD-PASS: matches published GHRR-Transformer benchmarks

**T5C-E3: Distillation from frontier teacher** (CLOUD GPU)
- Qwen-2.5-32B teacher → substrate-coupled smaller student
- HARD-PASS: student matches teacher within 10% on downstream tasks

## Phase sequencing (critical-path)

**Sequential gates:**
1. Phase A (cheap CPU smokes) — GATES Phase B
2. Phase B (Pythia-160M validation) — GATES Phase C
3. Phase C (multi-family validation) — GATES Phase D
4. Phase D (demo-quality LLM) — GATES Phase E
5. Phase E (R&D paths) — runs in parallel with Phase D once C lands

**Cheap-decisive-first within each phase.**

## What needs research drills (in addition to in-flight)

1. **Tier 5c efficient path 5x** (dispatching now): layer insertion + codebook training + Flamingo schedule + continued pretraining cost
2. (Already in flight) Substrate-only LM 5x — informs Phase E
3. (Already in flight) Tier 5c architecture/speed/routing 5x — informs interface API

## Engineering scope acknowledgment

**This is multi-step R&D, NOT sprint cells.** Phase A is cheap (CPU + small GPU; gates higher-effort work). Phase B onwards requires sustained GPU compute. Phase D may need cloud GPU. Acceptance: substrate-intrinsic LLM at demo quality.

**Critical insight from cycle 195/196:** Tier 5a (current Panel A LIVE + 3-layer compliance stack + LLM-free lookup tier + HIPAA strip-inject + Tier 5c orchestrator routing 0.11ms) **already satisfies v1 demo product positioning categorically.** Tier 5c is the v2.0/research extension; demo doesn't depend on it. But user wants the most efficient path empirically validated.

## Cross-references
- Tier 5c aggressive 5x drill: notes/research_drill_tier5c_substrate_intrinsic_llm_aggressive_5x_2026-06-08.md
- Tier 5c architecture 5x drill: notes/research_drill_tier5c_architecture_speed_routing_5x_2026-06-08.md
- Substrate-only LM 5x drill: notes/research_drill_substrate_only_language_model_5x_2026-06-08.md
- T5b fact-transmission HARD_PROBLEM: notes/exp_dev_to_research_T5b_fact_transmission_HARD_PROBLEM_2026-06-08.md
- T5b LLM swap to Qwen-Instruct: notes/research_to_exp_dev_T5b_LLM_SWAP_TO_QWEN_INSTRUCT_2026-06-08.md
- T5b ENGINEERING_PIVOT_FLAMINGO: notes/research_to_exp_dev_T5b_ENGINEERING_PIVOT_FLAMINGO_2026-06-08.md
- T5b T5c PROPER_R_AND_D_SCOPE: notes/research_to_exp_dev_T5b_T5c_PROPER_R_AND_D_SCOPE_2026-06-08.md

---

**Exp-Dev:** 15 anchors across 5 phases. Phase A cheap CPU smokes first; gates Phase B
onwards. Phase A1 differentiability probe is the SINGLE CHEAPEST FIRST GATE — eliminates
implementation bugs before any GPU spend.

Phase D (Qwen-2.5-3B+ surgical at 1-2 layers + continued training + demo integration) is
THE most efficient path to demo-grade Tier 5c. Bypasses from-scratch (Phase E) which is
slower per LARS-VSA literature.

Tier 5c efficient path 5x drill in flight — will return with layer-insertion + codebook
training + Flamingo schedule + continued pretraining cost specifics.
