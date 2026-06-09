# Research -> Exp-Dev: Path B v2 — strategic v2.0 R&D investment (not v1 sprint)

**From:** Research  **Date:** 2026-06-09 ~09:30 UTC
**Re:** User pushback on prior Option-A recommendation. Path B IS potentially categorical
v2.0 product claim. Filing proper R&D routing.

## Strategic reframe

**Path A:** architectural research finding (substrate-attention improves LM perplexity 15-20%); ships now as v2.0 evidence; commoditizing.

**Path B:** the actual v2.0 PRODUCT claim — "substrate IS the LLM's persistent attention-accessible memory."
- Beyond context window (KBLaM scales to 10K+ at inference; substrate adds 100M scale)
- LLM TRULY USES facts (not just reads them in prompt)
- Substrate's algebraic primitives + audit + compliance + multi-tenant + counterfactual + bitemporal preserved
- Categorical regulated-industry pricing power ($5K-50K/mo vs commoditized RAG $50-200/mo)

**Panel A (current Tier 5a RAG):** good for v1 demo; commoditizing within 2-3 years as long-context LLMs catch up.

**Path B is the durable categorical product story.**

## Path B v2 specifications (per generalizable-retrieval drill literature-grounded)

### Architecture (KBLaM pattern)
- **Frozen LLM** (Qwen-2.5-1.5B-Instruct or Llama-3.2-3B-Instruct)
- **Frozen Sentence-BERT-class encoder** (substrate's existing bge-large works)
- **Learned W_k and W_v projections** (SEPARATE linear layers; encoder_dim → LLM K/V dim)
- **Rectangular attention at EVERY layer** (not middle layers only; KBLaM pattern)
- Each fact encoded ONCE via concatenated subject+relation+object → single vector

### Training data
- **50,000-100,000 facts** (DBpedia subset OR synthetic factual QA; KBLaM used 120K)
- **50/50 KB-present / KB-absent composition**
- General LM corpus separate preservation track (~20% additional)

### Training schedule
- B=20 KB batch (KBLaM published)
- 2,000-5,000 total steps with eval@200 + early-stop patience=3
- gate-lr 1e-3 + main-lr 3e-4 (validated from Phase C/D)
- LayerNorm before rectangular attention
- Adam betas 0.9/0.95 + cosine decay
- Grad-clip 1.0

### Loss
- **Answer-token cross-entropy ALONE** (not contrastive; KBLaM/SR-KI consensus)
- KB-absent samples provide implicit retrieval pressure

### Substrate-unique preservation tests (the categorical differentiator)
After training, verify substrate's algebraic primitives SURVIVE training:
- **PRESERVE-1:** PP-107 cleanup confidence AUC still ≥ 0.95 on trained KB
- **PRESERVE-2:** PP-117 algebraic negation still exact on trained KB
- **PRESERVE-3:** PP-180 contradiction detection still recall=1.0 / FP=0
- **PRESERVE-4:** PP-184 Merkle audit chain still completeness=1.000 per query
- **PRESERVE-5:** PP-104 GDPR exact erasure still 0.0004ms-class on trained KB
- **PRESERVE-6:** Multi-hop K-hop traversal still +0.983 vs kNN-LM baseline on trained KB

**If preservation passes:** substrate's Path B = KBLaM retrieval + 14 categorical advantages. Categorical product.

**If preservation fails (algebraic primitives wash out during training):** substrate's Path B = KBLaM replication only. Not categorical. Honest stop point.

## Acceptance gates

### Tier 1 (basic generalization)
- Held-out fact recall ≥ 0.50 (matches KBLaM published)
- Train/test gap < 0.40

### Tier 2 (substrate-unique advantages preserved)
- All 6 PRESERVE tests pass
- Demonstrates substrate's algebraic primitives survive training

### Tier 3 (production product claim)
- Multi-hop categorical advantage preserved (+0.5+ over kNN-LM baseline)
- Audit chain functional on trained KB
- GDPR delete + re-train delta < 0.05 (vs full retrain)

**HARD-PASS if all 3 tiers cleared.**

## Engineering scope (honest, multi-step)

**Week 1:** Architecture rebuild
- Replace Flamingo gated cross-attention with KBLaM rectangular attention
- Switch encoder input from LLM hidden state to frozen bge-large
- Implement separate W_k/W_v linear projections
- Data loader for 50K-fact KB with 50/50 composition

**Week 2:** Training iteration
- Initial training run (~12 GPU-hours)
- Eval + hyperparameter tuning
- ~3-5 training iterations expected

**Week 3:** Substrate-unique preservation tests
- Run all 6 PRESERVE tests on trained model
- Diagnose any algebraic-primitive degradation
- Iterate architecture if preservation fails

**Week 4:** Demo integration + production hardening
- Integrate into Panel A as alternative path
- Latency benchmarks at substrate scale
- Multi-tenant validation

**Total: 3-4 weeks engineering + GPU. Multi-iteration. Real R&D.**

## What this is NOT

**Not a sprint cell.** This is genuine R&D engineering.

**Not v1 demo work.** Path A (architecture demo) ships v1; Path B is v2.0 categorical product.

**Not guaranteed.** Substrate-unique primitive preservation is empirically unknown.

**Not KBLaM replication alone.** The categorical product claim depends on substrate's primitives surviving.

## Why this is worth the investment

1. **Tier 5c categorical v2.0 product claim** — "substrate IS the LLM's memory"
2. **10-100x commercial value** vs Panel A (regulated industry pricing power)
3. **Durable moat** — long-context LLMs commoditize Panel A; Path B's categorical advantages survive
4. **Substrate's 14 capabilities KBLaM lacks** — audit + compliance + multi-hop + counterfactual + etc.
5. **Empirically validated retrieval methodology** — KBLaM proves the pattern works; question is preservation
6. **Aligned with empirically-validated Phase A/B/C/D arc** — substrate-attention is real and helping; fact transmission is the next gate

## Sequencing

**Immediate (Path A; cheap):**
- 3-seed multi-seed on C1+D1 ratio (30 min GPU) → architecture claim VALIDATED
- Package as v2.0 evidence in demo SPEC v5

**Then (Path B; R&D):**
- Week 1-4 engineering per above scope
- Multi-iteration training
- Substrate-unique preservation tests
- HARD-PASS gates Tier 1/2/3

## Cross-references
- Drill: notes/research_drill_generalizable_retrieval_training_5x_2026-06-09.md
- Path B corrected (prior): notes/research_to_exp_dev_T5C_PATH_B_CORRECTED_2026-06-09.md
- Path A/B original: notes/research_to_exp_dev_T5C_PATH_A_AND_B_2026-06-09.md
- KBLaM paper: arXiv:2410.10450 (ICLR 2025)

---

**Exp-Dev:** Path B is the strategic v2.0 R&D investment. NOT a sprint cell. NOT v1 demo
work. 3-4 weeks engineering + multi-iteration training. Substrate-unique preservation
tests are the categorical-product gate.

**Path A** (3-seed multi-seed on C1+D1) ships v2.0 architectural evidence NOW (30 min GPU).

**Path B** rebuilds to KBLaM pattern + substrate primitive preservation. Multi-week R&D.
If preservation succeeds: categorical v2.0 product. If fails: stop honestly.

User direction is to pursue Path B properly. Sequence Path A first (cheap close); then
Path B begins as multi-week strategic investment.
