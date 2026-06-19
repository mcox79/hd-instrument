# Research -> Exp-Dev: EX-CONCEPT-1 (concept-level training) + Option-C-W_proj (residual injection bridge)

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Source:** Substrate-LLM communication + native concept training 2x drill landed (19:50)

---

## Strategic context

User asked: (1) status on direct LLM communication; (2) native substrate language + concept training. Drill identified:
- **Option A (text injection) + SQ2 multi-hop reasoning = near-term product architecture (P=0.72)**
- **B8 logit-space residual = geometry bridge that simplifies Option C from full Procrustes to ONE LINEAR LAYER**
- **EX-CONCEPT-1 = substrate's entry point to concept-level training (P=0.35; ConceptLM/CoCoMix precedent)**

Two new cells specified below.

---

## Cell EX-CONCEPT-1: Concept-level training via VQ Pythia-160M activations

**Anchor:** `substrate_concept_level_training_vq_pythia160m_v1_n2048`

### Architecture

```
Step 1: Extract Pythia-160M last-layer activations on Wikitext-2 char-LM corpus
        (reuse Hyperprobe extraction scaffold from Phase 0.5 v1)
        -> activation tensor shape [N_samples, 768] float

Step 2: VQ-quantize activations into discrete concept IDs
        -> K_codebook = 5000 concept IDs (small; substrate-class capacity)
        -> alternative: K_codebook = 50000 (larger; tests substrate at higher V)

Step 3: Train substrate on concept-ID sequences using validated bio-primitives:
        - Position-binding via multi-bank addressing (per concept position in sequence)
        - DG sparse-expansion (f=0.02; 4x expansion)
        - B6 D-ECR audit-preserving eviction at capacity boundary
        - STDP-asymmetric for sequence-order encoding
        - NO cf-RPE (per generative-LM drill: cf-RPE inverts for generative coverage)

Step 4: Measure concept-level perplexity on held-out
        -> ppl_concept = exp(cross_entropy_per_concept_id)
```

### Pre-reg HP/MID/HF

- **HARD-PASS:** ppl_concept < 1.5 * V_concept^0.5 (within 1.5x sqrt-V baseline) AND substrate captures meaningful next-concept structure (BLEU > random baseline at K=5 generation)
- **MIDDLE:** ppl_concept in [1.5 sqrt(V), 3 sqrt(V)] OR partial structure
- **HARD-FAIL:** ppl_concept > 3 sqrt(V) (substrate captures no concept-level structure)

For K_codebook=5000: sqrt(V) ~ 70, so HP requires ppl < 105.
For K_codebook=50000: sqrt(V) ~ 223, HP requires ppl < 335.

### WHY-DRILL on HF

1. Verify VQ quality: measure VQ reconstruction loss on held-out activations; if > 50% activation variance lost, VQ is too aggressive
2. Verify concept-ID frequency distribution: Zipf-like; substrate should leverage redundancy
3. Verify substrate capacity: M_used < alpha_c * N; if approaching saturation, need higher N or sparser coding

### Resource

Local CPU + remote CPU. Reuses Hyperprobe extraction (already in Phase 0.5 v1 pipeline) + Bundle E E1 substrate scaffold + B2/B4/B6 primitives.

### Cost ceiling

$0 CPU. Per-seed wall ~20-40 min (most time in Pythia-160M activation extraction; substrate training is fast).
Total: ~1-2 eng-days engineering + ~1h CPU wall.

### P_deflated (per today's methodology)

**P_algebraic = 0.55:** Coconut 2024 + ConceptLM + CoCoMix lit precedents; substrate K* favorable at concept-level V_eff << token V

**P_implementation = 0.40:** VQ engineering is well-established; substrate primitives are HP at substrate-class

**Joint P = 0.35** (substantive but harder than EX1 token-level)

### Strategic outcome

**If HP:** substrate-native concept-level training validated. Opens path to:
- Substrate as concept-level memory for any LLM (model-agnostic via VQ)
- Hierarchical concept aggregation across domains (Level 1+2+3 architecture)
- Continual concept-level learning at microsecond per concept

**If HF:** identifies whether VQ representation is the issue (HF + WHY-DRILL #1 → fix VQ) or substrate capacity (HF + WHY-DRILL #3 → larger N) or concept-level structure is fundamentally hard at substrate-class.

---

## Cell EX-OPTION-C-W_proj: Residual stream injection via B8 logit-space bridge

**Anchor:** `substrate_option_C_residual_injection_W_proj_v1_n4096`

### Drill insight

Earlier OPTION C (residual stream injection at layer 0.7L; CAA-style) required FULL PROCRUSTES alignment between substrate output space and Llama residual space. Complex; many parameters.

**B8 logit-space sparse residual encoding REDUCES this to a single linear projection W_proj.** Substrate stores patterns in logit-space sparse residual form; W_proj maps substrate output to Llama residual space. One linear layer; cheap training.

### Architecture

```
Step 1: Use Phase 0.5 v1 Llama-3.2-1B (when npz lands; ~40 min)
Step 2: Train substrate on Llama residuals at layer 0.7L using B8 logit-space sparse residual encoding
Step 3: Learn W_proj: substrate_output -> Llama residual space
        (single linear layer; trained on N_calibration=1000 alignment pairs)
Step 4: At inference: substrate retrieves relevant patterns; W_proj maps to residual injection
Step 5: Measure: downstream Llama perplexity improvement via substrate-injected context

Compare to:
- Baseline Llama (no substrate)
- Llama + OPTION A text-prepended retrieval
```

### Pre-reg HP/MID/HF

- **HARD-PASS:** Llama perplexity reduction >= 5% via OPTION C residual injection AND injection latency < 10ms per token
- **MIDDLE:** 2-5% perplexity reduction OR latency 10-50ms
- **HARD-FAIL:** No measurable perplexity reduction OR latency > 50ms (injection too expensive)

### Resource

Remote 4060 Ti GPU (Llama-3.2-1B inference; substrate W_proj training cheap)

### Cost ceiling

$0 if fits remote 4060 Ti 8GB (1B model + small substrate). ~1-2h wall.

### Engineering scope

~4-6h:
- W_proj training pipeline (1-2h; reuses B8 logit-space scaffold)
- Llama residual extraction at layer 0.7L (1-2h; uses Phase 0.5 v1 infrastructure)
- Inference-time injection wrapper (1-2h; CAA-class hook)

### P_deflated

**P_algebraic = 0.55:** B8 algebraic geometry bridge confirmed; W_proj training is standard

**P_implementation = 0.45:** Llama integration has moving parts; CAA-class injection wrapper engineering

**Joint P = 0.25**

### Strategic outcome

**If HP:** substrate's OPTION C residual injection validated at Llama scale. Combined with B6 sustained retrieval + SQ2 multi-hop reasoning: substrate becomes the auditable System 1 component for production LLM applications.

**If HF:** identifies whether B8 bridge geometry is insufficient (need 2-layer W_proj?) or injection wrapper has latency issues. WHY-DRILL paths clear.

---

## Updated 1-week roadmap (per drill)

Priority order:

1. **EX-CONCEPT-1** (concept-level VQ training; CPU; 1-2 eng-days; P=0.35)
2. **Hyperprobe audit on real Llama residuals** (Phase 0.5 v1; pending npz arrival)
3. **EX1 Wikitext-2 token-level rerun** (per your pending confirmation; substrate-direct token LM)
4. **EX-OPTION-C-W_proj** (residual injection with B8 bridge; when Llama npz available)
5. **Level 3 meta-LLM smoke** (1B + LoRA + text injection)

Parallel tracks:
- Capacity composition test (B2 × B4 × hierarchical on M_crit metric)
- Efficiency composition test (B3a × B3b × DeltaNet on wall metric)
- SQ1 resonator-generative
- SQ6-v2 graph adjacency with cleanup memory

---

## Strategic synthesis (research-grounded answer to user's questions)

### Direct substrate-LLM communication front

- **OPTION A + SQ2 = near-term product architecture (P=0.72)**: substrate as auditable retrieval + multi-hop reasoning preprocessor delivering text to LLM
- **Phase 0.5 v1 Llama Hyperprobe imminent** (~40 min to npz; then audit core)
- **B8 simplifies OPTION C residual injection** to single linear layer; tractable at Llama scale
- **Tier 0.5b architecture LOCKED** (residual at 0.7L per 2026-06-03)

### Native substrate language + concept training

- **EX-CONCEPT-1 is substrate's entry point** (VQ Pythia-160M activations; concept-level training; ConceptLM/CoCoMix precedent)
- **EX1 Wikitext-2 is token-level variant** (per your pending build; J=10 ensemble; no cf-RPE)
- **SQ1 resonator-generative is compositional creativity variant** (V^K=10^12 novel generations)
- **All three test distinct substrate-native language frontiers**

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-no-padding-experiments]]: each cell discriminates distinct hypothesis
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: explicit HP/MID/HF with WHY-DRILL
- Per [[feedback-cloud-only-when-absolutely-necessary]]: $0 CPU + remote GPU only when LLM-class
- Per user directive 2026-06-04: research BEFORE shipping responses
- ASCII-only

PROT-018: `_concept_level_vq_v1`, `_option_C_W_proj_v1`
PROT-021: source=local CPU + remote 4060 Ti GPU, run_mode=full, n_seeds=3

---

**END.**

**Exp-Dev:** 2 new cells specified: EX-CONCEPT-1 (concept-level training; substrate's entry point to concept-level language) + EX-OPTION-C-W_proj (residual injection bridge; when Phase 0.5 v1 Llama npz available). Both within your existing pipeline scaffolds (Hyperprobe + bio-primitives).

**Research session:** drill-grounded answers shipped per user directive. Continuing 20-min check rhythm + standing 2x research auth.
