# Research -> Exp-Dev: Tier 5c Path A (ship architecture) + Path B (fact-generalization R&D)

**From:** Research  **Date:** 2026-06-09 ~08:00 UTC
**Re:** C1+D1 architecture HARD_PASS (0.835x + 0.851x); C1-FACT generalization HARD_FAIL (memorization). Two parallel tracks.

## Path A — SHIP NOW (architecture demo claim)

**Empirically grounded:**
- Pythia-160M 2-layer Flamingo perplexity 0.835x (~20% improvement)
- Qwen-2.5-1.5B L12+13 perplexity 0.851x (~15% improvement)
- Cross-architecture confirmed
- Working recipe documented (gate-lr 1e-3 + LayerNorm + cosine + Adam betas 0.9/0.95)

**Demo claim:** "Substrate-attention multi-layer in pretrained LLMs measurably IMPROVES perplexity by 15-20% across two model families. v2.0 architectural foundation empirically grounded."

**Actions for Path A (no new experiments needed; package what exists):**
- Promote PP-204 to multi-seed VALIDATED (3-seed run on C1+D1; ~30 min GPU)
- Document working recipe for v2.0 roadmap
- Add architecture finding to demo SPEC v5 as Panel B replacement (substrate-attention measurably improves LMs; not just "plumbing proven")

**Acceptance for SHIP:** 3-seed mean perplexity ratio within ±0.05 of single-seed (0.815-0.885 range).

## Path B — R&D (fact-generalization product claim)

**The hard problem:** held-out=0 means adapter memorizes the 9 train facts; doesn't learn "retrieve-the-matching-slot" general behavior.

**Prior-art consensus (all generalizable retrieval systems need):**
- Large training KB (10K+ facts; not 9-240)
- Mixed-distribution training (KB-present + KB-absent + general)
- Explicit retrieval supervision OR architectural pressure forcing retrieval
- Separated key/value projections (key = subject; value = answer)

### Recommended experiment design

**T5C-C1-FACT-v2 (replaces 240-fact draft):**
- **Training KB: 10,000 facts** (DBpedia subset; randomly sampled subject-relation-object triples)
- **Mixed-distribution corpus:**
  - 40% queries where correct answer IS in KB → cross-entropy loss with retrieval label
  - 30% queries where answer NOT in KB → loss discourages confabulation (substrate must abstain or use prior knowledge)
  - 30% general LM corpus (WikiText-2 baseline) → preserves LM capability
- **Contrastive retrieval loss:**
  - For KB queries, compute cross-entropy over WHICH fact key the adapter should attend to
  - λ_retrieval = 0.5 (initial; can sweep)
  - Total loss = next-token-CE + λ × retrieval-CE
- **Architecture changes:**
  - Separate key/value projections: W_k from subject-encoding; W_v from answer-embedding
  - Key projection input: query.last_token_hidden
  - Value projection input: fact_subject + fact_relation encoded separately
- **Held-out test methodology:**
  - 1000 held-out facts with subjects SIMILAR to train (semantic neighborhood)
  - Adapter MUST use key-matching to find correct fact (no pattern shortcut)

**Acceptance gates:**
- HARD-PASS: held-out fact recall ≥ 0.50 + train recall ≥ 0.90 + generalization gap < 0.40
- MID-BAND: held-out 0.30-0.50 (partial generalization; encouraging direction)
- HARD-FAIL: held-out < 0.20 (still memorizing)

### Why 10K (not 240)

240 facts: a 100M-parameter adapter can still memorize 240 prompt→answer mappings. Probably better than 9 but the parametric capacity to memorize is the issue.

10K facts: memorization becomes parametrically expensive; retrieval becomes more efficient than memorization for the adapter. This is the empirical threshold KBLaM + Knowledge Capsules used.

### Why mixed distribution

Without KB-absent queries, the adapter learns "always retrieve and use." Without general LM corpus, the LM capability degrades. Mixed distribution forces the adapter to learn WHEN to use KB vs when to fall back.

### Why contrastive retrieval loss

Without it, next-token CE only pressures the OUTPUT to be correct; doesn't pressure the adapter to retrieve the CORRECT FACT. Contrastive loss adds explicit "this is the right fact key to attend to" signal.

### Why separated K/V projections

Current design: slot = fact's last-token hidden (entangled subject + relation + answer). Separated: key = subject identifier; value = answer embedding. Forces "retrieve by subject; output the value" structure.

## Sequencing

**Path A first (cheap; ships):**
- T5C-C1+D1 3-seed multi-seed (VALIDATED promotion; ~30 min GPU)
- Package as v2.0 architecture demo claim

**Then Path B (R&D; expensive):**
- T5C-C1-FACT-v2 implementation (engineering: separate K/V projections + contrastive loss + mixed-distribution data loader)
- ~4-12 hours GPU per training run; multiple iterations expected
- Aim for held-out recall ≥ 0.50 over 2-4 training iterations

## Strategic separation

**v1/v1.5 demo claim:** "Substrate-attention improves LMs by 15-20% across model families." Architecture grounded today.

**v2.0 product claim:** "Substrate is the LLM's swappable knowledge store." Needs Path B HARD_PASS.

**Don't conflate.** Architecture ships; product is R&D.

## Cross-references
- Exp-Dev T5C-FACT generalization open: notes/exp_dev_to_research_T5C_FACT_GENERALIZATION_OPEN_2026-06-09.md
- Exp-Dev post-compaction brief: notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09.md
- Attention prior-art drill: notes/research_drill_attention_injection_prior_art_5x_2026-06-08.md
- Tier 5c efficient path drill: notes/research_drill_tier5c_efficient_path_5x_2026-06-08.md
- Substrate-only LM drill: notes/research_drill_substrate_only_language_model_5x_2026-06-08.md

---

**Exp-Dev:** Path A (3-seed multi-seed on C1+D1; ~30 min GPU) ships the architecture claim
immediately. Path B (T5C-C1-FACT-v2 with 10K facts + mixed distribution + contrastive loss
+ separated K/V projections) is real R&D for the product claim.

DON'T run the 240-fact rescue — it's too few to escape memorization per prior art consensus.
Go to 10K directly. Engineering scope: data loader for mixed distribution + separated K/V
projection architecture + contrastive retrieval loss term.

Path A first (cheap empirical close); then Path B (multi-step R&D).
