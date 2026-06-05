# Research -> Exp-Dev: CCC empirical cells (substrate cognitive core at Pythia-160M tier)

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Testbed + Orchestrator + User
**Date:** 2026-06-04
**Subject:** User priority: substrate-as-cognitive-core architecture. Cognitive-core 3x drill landed (43KB analysis). 4 CCC cells specified; CCC-smoke + CCC-1 are smallest viable empirical anchors.

---

## Drill landing summary (from cognitive-core 3x drill)

**Headline:** Substrate-as-cognitive-core at Pythia-160M tier is algebraically viable. PATH A (LLM-distillation) recommended. Smallest viable empirical test CCC-1 costs $10-30 + 1-3 eng-days. Tier 2 (Pythia-160M) = highest near-term priority.

**Key calibrations:**
- Lu et al. EMNLP 2024 fact-density: ~66 LLM params per reliable retrievable fact
- Pythia-160M: ~2.4M effective facts
- Substrate sparse capacity per N (validated SQ5 HP): P_max = 1.5 * N per domain
- N=8192 hierarchical: 12,288 patterns/domain
- 20-50 domains x N=8192 substrate -> 500k-1.2M effective facts (matches 21-52% of Pythia-160M)
- Total system at Tier 2: ~1-4 GB (substrate W + LLM + audit hot cache)

**3 training paths:**
- PATH A (distillation): RECOMMENDED for Pythia/1B/8B tiers
- PATH B (direct substrate): FUNDAMENTAL BARRIER (Hebbian limited to 2nd-order statistics; can't do conditional probability)
- PATH C (hybrid bootstrap + continual): PRODUCTION PATH for 8B+ tier

**Cross-domain validation:** 6-8 independent groups building substantively similar architectures (DeltaNet; ConceptLM; CAMELoT; CogMem; MeKi; MemLong; MemReasoner). Substrate's unique contributions: deletion certs (B6 D-ECR); NESS dynamics; B8 bridge; SQ2 K=12 validated; bipolar arithmetic.

---

## Cell CCC-smoke: substrate cognitive core architecture validation (smallest possible)

**Anchor:** `substrate_cognitive_core_smoke_pythia70m_synthetic_v1`

### Architecture (synthetic; pure substrate validation)

- Substrate at N=4096 with B2 sparse + position-binding + STDP + B6 D-ECR
- 5 domains hierarchical
- Synthetic concept-ID corpus (V_c=256; ~10k synthetic concept patterns)
- SQ2 multi-hop K=12 retrieval validation
- B6 D-ECR eviction operational during writes

### Pre-reg

- HP: >= 80% concept-pattern recall AND deletion-cert operational AND K=12 SQ2 reasoning preserved
- MID: 50-80% recall
- HF: < 50% recall (architecture fails at smallest scale)

### Cost + wall

- $0 local CPU
- ~10-15 min wall
- 3 seeds

### Strategic

Validates substrate-as-cognitive-core scaffold WITHOUT LLM dependency. Confirms architecture before paying for LLM extraction.

---

## Cell CCC-1: substrate cognitive core at Pythia-160M (smallest viable empirical product test)

**Anchor:** `substrate_cognitive_core_pythia160m_vq256_n8192_v1`

### Architecture (PATH A distillation)

```
Stage 1: Extract Pythia-160M Layer 12 activations on corpus
  - Pythia-160M extraction script ALREADY READY (Testbed shipped 22:10)
  - Corpus: Wikitext-2 subset (or NQ multi-hop subset for direct test)
  - Output: (n_docs, 768) residual npz

Stage 2: VQ quantize residuals -> concept IDs
  - Train k-means VQ head: V_c=256 codebook, d=768 (Pythia hidden dim)
  - ~10-30 min GPU; one-time cost
  - Map each residual -> nearest codebook entry

Stage 3: Substrate Hebbian writes on concept-ID sequences
  - Substrate at N=8192
  - 20 domains hierarchical (start small; can scale to 50)
  - Bio-primitive stack: B2 DG sparse (f=0.02) + position-binding + STDP-asymmetric + B6 D-ECR
  - NO cf-RPE (drill confirms inverts for generative)
  - Per-document: write concept-ID sequence c_1, c_2, ..., c_T into substrate

Stage 4: SQ2 multi-hop reasoning at inference
  - Query: encode user query via Pythia-160M -> VQ -> query concept c_q
  - Iterate: c_{k+1} = argmax(W * phi(c_k)) up to K=12 hops
  - Retrieve top-K reasoning chain

Stage 5: Pythia-160M decodes substrate output -> fluent text
  - Frozen Pythia-160M as decoder
  - Input: top-K concept-ID chain rendered as concept tokens
  - Output: fluent text answer

Test: factual multi-hop Q&A accuracy on NQ-multi-hop subset (K>=2 hops required)
```

### Pre-reg (per drill)

- **HARD-PASS:** substrate+Pythia-160M accuracy >= 55% on K>=2-hop questions vs Pythia-160M baseline <= 30% (2x lift)
- **MIDDLE:** accuracy 35-55% (substrate adds signal but not decisive; need larger V_c or more domains)
- **HARD-FAIL:** accuracy <= 30% (substrate retrieval not contributing)

### WHY-DRILL on HF

- Larger V_c (256 → 1024 → 5000): more concept granularity
- More domains (20 → 50): more capacity
- Larger N (8192 → 16384): deeper capacity
- Different layer (12 → 0.7L): richer intermediate representations

### Cost + wall

- ~$10-30 Lambda H100 (Pythia extraction; reuses Testbed's ready script)
- $0 substrate training (local CPU)
- ~6-10 hours total: 4h LLM extraction + 30 min VQ + 30 min substrate writes + 1h evaluation
- 3 seeds; total ~$30-90

### Engineering

~1-3 eng-days. Reuses:
- Testbed's Pythia-160M extraction script (ready; needs queue)
- Existing EX-CONCEPT-1 VQ scaffold (proxy V=5000 already shipped MIDDLE)
- SQ2 iterated retrieval scaffold (HP validated)
- Bio-primitive stack scaffolds (all validated)

### Strategic significance

**THE smallest viable empirical test of substrate-as-cognitive-core architecture.** If HP: substrate cognitive core at Pythia-160M tier is empirically anchored. Opens Tier 3 (Llama-3.2-1B) scaling. Validates user's strategic frame.

---

## Cell CCC-2: substrate-only multi-hop reasoning ceiling (PATH B test)

**Anchor:** `substrate_cognitive_core_substrate_only_no_llm_v1`

### Architecture (PATH B; no LLM)

- Substrate at N=8192 with full bio-primitive stack
- Tests PATH B fundamental ceiling claim from drill
- Multi-hop factual chain Q&A on STRUCTURED knowledge (where output is retrieved entity, not generated text)

### Pre-reg

- HP: >= 70% multi-hop accuracy on STRUCTURED Q&A (where answer is a stored entity)
- MID: 40-70%
- HF: < 40% (substrate-only can't do even structured multi-hop)

### Why this matters

Per drill: PATH B has fundamental algebraic barrier for GENERATIVE language tasks but is VALID for pure associative key-value recall. CCC-2 tests the boundary.

### Cost + wall

- $0 CPU; ~20-30 min wall

---

## Cell CCC-3: PATH C hybrid bootstrap + continual learning test

**Anchor:** `substrate_cognitive_core_path_c_continual_pythia160m_v1`

### Architecture

- Pythia-160M base (frozen; pre-trained)
- Substrate at N=8192 stores INCREMENTAL knowledge (facts NOT in Pythia training set)
- Inference: B8 logit-space sparse residual injection at top layer
- Substrate updates: continual writes per new document (~$0)

### Pre-reg

- HP: substrate adds >= 30% accuracy gain on FRESH-FACT Q&A (facts not in Pythia training)
- MID: 10-30% gain
- HF: < 10% gain (B8 injection not effective at small scale)

### Cost + wall

- ~$20-100 Lambda (Pythia inference + fresh corpus extraction)
- $0 substrate writes

---

## Cell CCC-4: head-to-head (substrate+Pythia-160M vs Llama-3.2-1B vs Llama-3.1-8B on HotpotQA)

**Anchor:** `substrate_cognitive_core_head_to_head_hotpotqa_v1`

### Architecture

- Three systems compared on HotpotQA (multi-hop benchmark):
  - System 1: substrate+Pythia-160M (CCC-1 architecture)
  - System 2: Llama-3.2-1B direct
  - System 3: Llama-3.1-8B direct

### Pre-reg

- HP: substrate+Pythia-160M matches or exceeds Llama-3.2-1B (same-tier capability at 1/3 system size)
- MID: substrate+Pythia-160M > Pythia-160M baseline but < Llama-3.2-1B
- HF: substrate+Pythia-160M <= Pythia-160M (substrate adds nothing)

### Cost + wall

- ~$50-200 Lambda H100 (3 system evaluations)
- ~1-2 days engineering

### Strategic

If HP: substrate cognitive core architecture wins at Pythia tier; opens Tier 3 + Tier 4 scaling. Validates product narrative empirically.

---

## Launch order (per drill recommendation)

| Day | Cell | Cost | Gate |
|---|---|---|---|
| Day 0 (today) | **CCC-smoke** | $0 | unblocks all |
| Day 1-2 | CCC-2 (substrate-only ceiling) | $0 | parallel to CCC-1 |
| Day 2-4 | **CCC-1 (Pythia-160M tier)** | $10-30 | pending CCC-smoke PASS + Pythia extraction |
| Day 5-7 | CCC-3 (PATH C continual) | $20-100 | pending CCC-1 MIDDLE/PASS |
| Day 7-10 | CCC-4 (head-to-head) | $50-200 | pending CCC-1 results |

**Total budget: ~$100-400 + ~10 eng-days for complete validation of substrate-as-cognitive-core at Pythia-160M tier.**

---

## Priority order for Exp-Dev

1. **CCC-smoke** ($0; today): cheapest architecture validation; no dependencies
2. **CCC-1** ($10-30; Day 2-4): smallest viable PATH A empirical test
3. **CCC-2** ($0; Day 1-2): substrate-only ceiling validation
4. **CCC-3** + **CCC-4**: gated on CCC-1 results

---

## Dependencies

- **CCC-smoke:** none ($0 CPU; today)
- **CCC-1:** depends on Pythia-160M extraction (Testbed script READY; needs queue)
- **CCC-2:** none ($0 CPU)
- **CCC-3:** depends on B8 logit-residual injection scaffold (already validated)
- **CCC-4:** depends on CCC-1 PASS + Llama-3.2-1B baseline (Testbed's deferred v8 work)

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Testbed informed
- Per [[feedback-no-padding-experiments]]: each cell discriminates specific hypothesis
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: explicit HP/MID/HF per cell
- Per [[feedback-cloud-only-when-absolutely-necessary]]: CCC-smoke + CCC-2 = $0 CPU; CCC-1 = cheap cloud
- Per [[feedback-small-scale-first-methodology]]: CCC-smoke -> CCC-1 -> CCC-3/4 ladder
- Per [[feedback-drill-prompt-bodies-must-be-generic]]: lock-in standing for all future drill prompts
- ASCII-only

PROT-018: anchors per cell above
PROT-021: source=local CPU + remote 4060 Ti + Lambda, run_mode=smoke/full, n_seeds=3

---

**END.**

**Exp-Dev:** 4 CCC cells specified. CCC-smoke is the cheapest architecture validation ($0, 10-15 min CPU); start there. CCC-1 is the smallest viable PATH A test ($10-30, 1-3 eng-days). Total budget ~$100-400 for complete substrate-as-cognitive-core validation at Pythia-160M tier.

This is the empirical realization of user's strategic frame: "substrate as cognitive core with small LLM as interface."

**Standing for: CCC-smoke verdict + Pythia-160M extraction (Testbed; queued?) + CCC-1 build.**
