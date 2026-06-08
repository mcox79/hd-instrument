# exp_dev hand-off -- research: attention injection prior art

Filed-by: research sub-agent
Date: 2026-06-08
Trigger: User request -- "do we fully understand the attention layer injection? Has anyone done this before?"
Research note: d:/AI/hd-instrument/notes/research_drill_attention_injection_prior_art_5x_2026-06-08.md

Pause state: do NOT dispatch cloud experiments. CPU-local smoke gate only.

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev designs the experiment. This file provides context pointers and anchor candidates only.

---

## Anchor Candidates (rank-ordered)

### Rank 1 -- Frozen injection entropy smoke gate
Anchor pointer: attention-injection-entropy-smoke
Substrate-product reading: Determines whether frozen Pythia heads can differentiate substrate HD vectors at all. This is the gate for every subsequent experiment. If attention entropy is near-maximum, an adapter is required before any meaningful result is possible.
Tier hint: Tier 1 (gate)
Why now: The research drill found this is the HIGHEST-RISK technical issue. KBLaM and Flamingo both use adapters or training. Knowledge Capsules claims frozen works. Empirical measurement needed in our specific case before any larger PoC investment.
Expected wall time: <10 min CPU. Single forward pass, measure softmax entropy over substrate K/V prefix.

### Rank 2 -- Flamingo-style cross-attention insert on frozen Pythia
Anchor pointer: attention-cross-attn-insert-frozen
Substrate-product reading: Tests the most validated frozen-LLM injection architecture (Flamingo, 2022). Inserts a gated cross-attention layer between Pythia transformer blocks, attends to substrate K/V, tanh gate init=0. If this produces differentiated attention on factual queries, the injection path is viable.
Tier hint: Tier 2 (architecture validation)
Why now: Research shows this is the recommended first architecture (Option C in research note). Cleaner than W_k/W_v replacement. Knowledge Capsules confirms prefix injection works frozen.
Expected wall time: 30-60 min CPU, Pythia-160M or 410M.

### Rank 3 -- Multi-head bundle splitting characterization
Anchor pointer: attention-multihead-bundle-split
Substrate-product reading: Tests the algebraic prediction that splitting an N=1024 HD bundle across H=16 heads causes different heads to decode different role-filler pairs. Novel prediction; if confirmed, strengthens the "genuine VSA unbinding" claim vs prior text-encoder K/V systems.
Tier hint: Tier 2 (novelty confirmation)
Why now: Cheap CPU experiment. Algebraic prediction is specific and falsifiable. Positive result would be a concrete differentiator.
Expected wall time: 15-30 min CPU.

---

## Context Pointers

- Research note (full catalog + analysis): d:/AI/hd-instrument/notes/research_drill_attention_injection_prior_art_5x_2026-06-08.md
- Prior HD vector dimensionality work: see substrate_capability_map.md rows for N=1024 whitening + pseudoinverse
- Pythia sanity check discipline: C:\Users\marsh\.claude\projects\d--AI\memory\feedback_pythia_sanity_check_before_cloud.md
- Frozen LLM injection precedents: KBLaM (arXiv 2410.10450), Knowledge Capsules (arXiv 2604.20487), Flamingo (arXiv 2204.14198)

---

## Contract Section

exp_dev owns: experiment design, pre-reg bands, dispatch mechanics, verdict filing.
Research delivered: prior art catalog, architectural options, risk assessment, ranked anchors.
Research does NOT own: choosing which anchor to dispatch, setting HP/HF bands, running any GPU.

---

## Autonomy Declaration

exp_dev has full autonomy to modify anchor design, rename, re-rank, or decline any candidate listed here. The research note is informational context; it is not a dispatch order.
