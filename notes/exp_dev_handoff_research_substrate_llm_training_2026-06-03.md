# exp_dev hand-off -- research: bipolar Hebbian substrate as full LLM training mechanism

**Filed-by:** research sub-agent  
**Date:** 2026-06-03  
**Trigger:** d:/AI/hd-instrument/notes/research_drill_substrate_as_full_llm_training_deep_dive_2026-06-03.md  
**Pause state:** check data/orchestrator_paused.flag before queueing  

Per [[feedback-no-experiment-design-in-prompts]]: this file hands ANCHOR CANDIDATES + WHY-NOW + CONTEXT POINTERS to exp_dev. exp_dev designs the sweep grids, threshold formulas, and queue entries autonomously.

---

## Anchor candidates (rank-ordered)

**Rank 1 — DeltaNet algebraic isomorphism probe (CPU-class, theory + micro empirical)**  
- Anchor pointer: verify whether DeltaNet delta-rule update (arXiv:2406.06484) is algebraically isomorphic to bipolar substrate rank-1 deletion + Hebbian rewrite
- Substrate-product reading: if isomorphic, DeltaNet's empirical 1.3B LLM results (outperforms Mamba on perplexity) directly validate substrate-native LLM training — no new experiments needed, just the algebraic verification + a micro smoke
- Tier hint: Tier-2 verification (algebraic + micro smoke); cheap CPU
- Why-now: DeltaNet paper is published, code is public; algebraic isomorphism check is <1 day theory work; would collapse the Tier-6 uncertainty from 0.18 to either ~0.05 (not isomorphic) or ~0.55 (isomorphic + DeltaNet results apply)

**Rank 2 — Character-level Hebbian attention probe (GPU smoke, single pass)**  
- Anchor pointer: 4-layer character-level LM on Wikitext-2 (2M chars), replace attention inner products with outer-product Hebbian writes (DeltaNet-style delta-rule, no softmax), keep gradient-trained linear output head
- Substrate-product reading: tests whether Hebbian writes to attention layers produce usable language representations; BPC <= 1.62 is HARD-PASS
- Tier hint: GPU smoke (single A100, ~2-4h); direct empirical test of smallest-viable-probe from research drill
- Why-now: no published result exists for this exact config; DeltaNet infrastructure can be adapted; closes the "does it work at language modeling?" uncertainty

**Rank 3 — Intra-layer competition as softmax normalization (theory only)**  
- Anchor pointer: mathematical analysis of whether substrate energy-basin winner-takes-all competition implements Z = sum(exp(q^T k_i)) normalization up to monotone transformation
- Substrate-product reading: if yes, the hard expressivity boundary (softmax normalization gap) is solvable without gradient; closes the expressivity analysis from sub-question (2)
- Tier hint: CPU theory (no GPU needed); output is closed-form analysis or counterexample
- Why-now: expressivity gap is now precisely characterized (see research note Section 2); the algebraic question is tractable

---

## Context pointers

- Research note (full synthesis): d:/AI/hd-instrument/notes/research_drill_substrate_as_full_llm_training_deep_dive_2026-06-03.md
- DeltaNet paper: arXiv:2406.06484 (NeurIPS 2024)
- FWP/linear transformer equivalence: arXiv:2508.08435v2
- Associative memory expressivity: arXiv:2505.19488
- Hebbian-FW transformer precedent: arXiv:2510.21908
- Dense AM capacity (alpha_c=1.59): arXiv:2511.02584
- cap_map rows affected: hierarchical-retrieval (🟢), auditable-memory (core), compositional-algebra

---

## Contract

exp_dev receives this file, reads the context pointers, designs the experiment anchors (sweep grids, threshold formulas, N choices, queue entry names) autonomously. No experiment design is provided here per [[feedback-no-experiment-design-in-prompts]].

## Autonomy declaration

exp_dev decides: anchor naming, N and L_stages values, whether Rank 1 algebraic check is sufficient to supersede Rank 2 GPU probe, queue routing (CPU vs GPU), and pre-reg threshold formulas. Orchestrator approves before queue_add.
