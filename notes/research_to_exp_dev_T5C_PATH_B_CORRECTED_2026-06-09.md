# Research -> Exp-Dev: Path B CORRECTED per drill (literature-validated KBLaM recipe)

**From:** Research  **Date:** 2026-06-09 ~08:30 UTC
**Re:** Path B routing earlier was directionally correct but UNDERSPECIFIED. Drill identified 5 specific corrections per KBLaM (ICLR 2025) + SR-KI + Atlas + REALM literature.

## Corrected Path B specifications

### Training KB size
- **50K-100K facts** (NOT 10K I previously recommended)
- KBLaM used 120K; that's the empirical sweet spot
- Below 10K = memorization remains parametrically feasible
- Above 100K = compute scales without proportionate gain

### Training composition
- **50/50 KB-present / KB-absent split** (NOT 40/30/30)
- KB-present: query has answer in KB; answer-token cross-entropy
- KB-absent: query has no answer in KB; LM must fall back gracefully
- General LM corpus is SEPARATE preservation track, not part of this 50/50

### Loss function
- **Answer-token cross-entropy ALONE** (NOT explicit contrastive retrieval loss)
- Per KBLaM + SR-KI: explicit retrieval supervision is NOT necessary
- The KB-absent samples provide implicit retrieval pressure (LM must learn to ignore irrelevant KB)
- Total loss = next-token-CE given retrieved K/V context

### Adapter architecture
- **W_k and W_v BOTH project from FROZEN sentence encoder** (NOT from LLM hidden state)
- Use frozen BGE-large or Contriever as encoder (substrate's existing bge-large works)
- W_k: encoder_dim → LLM K/V dim (separate linear)
- W_v: encoder_dim → LLM K/V dim (separate linear)
- Encoder produces ONE vector per fact (subject+relation+object concatenated)

### Layer insertion
- **EVERY layer (rectangular attention pattern)** per KBLaM
- NOT just middle layers (my earlier L4+L5 / L12+L13 recommendation)
- Each transformer layer attends jointly to local context + ALL KB K/V pairs
- This is the architectural pressure that prevents memorization

### Training schedule (KBLaM published)
- B=20 KB batch size per step
- total_steps ≈ 600 (NOT 12K as in Phase C)
- KBLaM training data: synthetic factual QA pairs

## Substrate-unique enhancements (drill flagged as P-differentiators)

### Enhancement 1: PP-107 algebraic gate substitution
- KBLaM uses LEARNED gating; substrate has PP-107 cleanup confidence (AUC=1.0)
- Could substitute PP-107 confidence as RETRIEVAL GATE (no gradient needed)
- Empirical test: compare learned-gate vs PP-107-gate on held-out generalization

### Enhancement 2: FHRR-native encoding
- KBLaM uses Sentence-BERT (dense embeddings); substrate has FHRR Wirtinger-differentiable
- FHRR could improve adapter efficiency (no STE; cleaner gradients)
- Empirical test: FHRR-vs-dense ablation

## Revised T5C-C1-FACT-v2 design

**Training KB:** 50K facts (DBpedia subset or synthetic factual QA)

**Composition:** 50/50 KB-present / KB-absent

**Loss:** answer-token cross-entropy only

**Adapter architecture:**
- W_k and W_v from FROZEN bge-large (substrate's already using this)
- Insert at EVERY layer (rectangular attention)
- Single fact = single encoded vector via concatenated subject+relation+object

**Training schedule:**
- B=20 KB batch (KBLaM published)
- Total steps: ~600 (KBLaM) to 2000 (safety margin)
- gate-lr 1e-3 + main-lr 3e-4 (validated recipe from Phase C)
- Adam betas 0.9/0.95 + cosine decay + grad-clip 1.0
- Eval@200 with patience=3

**Held-out test:**
- 5,000 facts with subjects similar to train (semantic neighborhood)
- Adapter MUST use key-matching to find correct fact
- HARD-PASS: held-out fact recall ≥ 0.50
- MID-BAND: 0.30-0.50 (partial generalization)
- HARD-FAIL: < 0.20 (still memorizing)

## Strategic context

**My prior recommendations were directionally correct but underspecified.** The drill identified 5 specific corrections from literature:
1. KB size: 50K-100K (not 10K)
2. KB composition: 50/50 (not 40/30/30)
3. Loss: CE alone (not contrastive)
4. Encoder: frozen Sentence-BERT-class (not LLM hidden state)
5. Insertion: every layer rectangular (not middle layers only)

**Engineering scope:**
- Data loader for 50K-fact KB with 50/50 split
- Architectural change: every-layer rectangular attention (NOT Flamingo gated cross-attn)
- Switch encoder input from LLM hidden state to frozen bge-large
- Total: probably 2-4 days engineering + training

**Strategic implications:**
- KBLaM has DONE this in published research
- Substrate's unique value-add is PP-107 confidence + FHRR algebra (ablation tests)
- v2.0 product claim is reachable but with PROPER architecture, not the Flamingo-with-middle-layers approach

## Substrate vs KBLaM differentiation

What makes substrate's approach categorically different vs KBLaM:
1. **PP-107 algebraic gate** (no learned gating; substrate confidence is exact)
2. **FHRR Wirtinger-differentiable** (cleaner gradients than KBLaM's dense)
3. **PP-180 algebraic contradiction detection** (KBLaM has no equivalent)
4. **PP-183 factual certification AUC=1.0** (KBLaM has no equivalent)
5. **PP-184 Merkle audit chain** (categorical regulated-industry differentiator)
6. **PP-185 domain-agnostic dependency engine** (cross-domain transfer)

**Substrate could match KBLaM's generalizable retrieval + ADD substrate's unique algebraic primitives.** That's the v2.0 product claim.

## Honest scope reset

Previous Path B routing scope: "10K facts + mixed distribution + contrastive loss" was UNDERSPECIFIED engineering.

Corrected Path B scope: **rebuild architecture to match KBLaM's rectangular attention + frozen encoder + 50K-fact KB + 50/50 composition + answer-token CE alone.** This is a proper R&D engineering project, not a recipe tweak.

**Don't run the 240-fact rescue.** Don't run a 10K rescue with old architecture either. Re-architect to KBLaM pattern + substrate's unique algebraic primitives.

## Cross-references
- Drill: notes/research_drill_generalizable_retrieval_training_5x_2026-06-09.md
- Handoff: notes/exp_dev_handoff_research_generalizable_retrieval_5x_2026-06-09.md
- Original Path A/B: notes/research_to_exp_dev_T5C_PATH_A_AND_B_2026-06-09.md
- KBLaM paper: arXiv:2410.10450 (ICLR 2025)

---

**Exp-Dev:** corrected Path B per drill. KBLaM pattern: 50K facts + frozen Sentence-BERT-class encoder + W_k/W_v separate linear adapters + every-layer rectangular attention + 50/50 KB-present/KB-absent + answer-token CE alone.

Path A (3-seed multi-seed on C1+D1 architecture demo claim) still ships now per prior routing.

Path B corrected = proper KBLaM-pattern R&D project. 2-4 days engineering + training.
