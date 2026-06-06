# exp_dev hand-off -- research: substrate context-window interaction deep dive

Filed-by: research sub-agent
Trigger: notes/research_drill_substrate_context_interaction_deep_dive_2026-06-03.md
Pause state: check data/orchestrator_paused.flag before dispatching

Per [[feedback-no-experiment-design-in-prompts]]: this file provides TASK + WHY + CONTRACT + AUTONOMY only. Anchor names, sweep grids, threshold formulas, HF/HP numerical bounds, and queue choice are for exp_dev to decide.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (highest priority): Sub-cell G -- token-overhead comparison
Pointer: Sub-cell G (context-cost-per-query) architectural comparison
Substrate-product reading: Measure actual token count difference between residual-injection path (zero extra tokens) vs tool-call-into-context path (K_avg * K_facts extra tokens) for 100 representative queries. The research drill derives expected savings of ~375 tokens/query at K_avg=75, K_facts=5. This anchor confirms the token-economy model and identifies the dominant cost-scaling regime for production deployment.
Tier hint: CPU smoke class. No GPU needed -- token counting is inference-side measurement.
Why-now: Sub-cell G is the most direct economic validation. The breakeven model (< 0.2 QPS) depends on this measurement. Should precede any cloud deployment decision.

### Anchor 2 (high priority): Sub-cell I -- long-context regression probe
Pointer: Sub-cell I (long-context regression) with RoPE aliasing focus
Substrate-product reading: Run LLM forward pass with and without substrate residual injection at layer ~0.7L across context lengths 512, 2048, 4096, 8192 tokens. Primary measurement: perplexity delta and attention entropy H(a_t). The research drill identifies RoPE position aliasing as the highest-probability subtle regression risk (P_deflated=0.55). Injection must be at the current generation position (last token), NOT at a static prefix.
Tier hint: GPU required (LLM forward passes). Smoke: 2-3 context lengths x 2 conditions.
Why-now: Failure mode Risk 1 (RoPE aliasing) is the single highest-risk unknown for the residual injection architecture. Must be confirmed safe before Path 1a is committed as the production integration architecture.

### Anchor 3 (medium priority): Sub-cell H -- ICL equivalence test
Pointer: Sub-cell H (in-context learning replacement)
Substrate-product reading: Store K patterns via Hebbian write at alpha < 0.05; present noisy cue; compare substrate retrieval accuracy vs K-shot in-context prompting with the same K examples. The research drill establishes RIGOROUS equivalence for linear attention and SUGGESTIVE equivalence for softmax attention at low loading. The empirical gap at alpha in [0.05, 0.15] determines the production design parameter (max alpha before ICL parity breaks down).
Tier hint: GPU. Sweep over alpha x K to identify the equivalence boundary.
Why-now: The ICL-replacement narrative ("facts in substrate = facts in context, no tokens") is the key product story. Empirical confirmation of the equivalence boundary determines the marketed operating regime.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_substrate_context_interaction_deep_dive_2026-06-03.md
- ICL/GD equivalence papers: arXiv:2102.11174 (Schlag 2021), arXiv:2212.07677 (von Oswald 2022), arXiv:2212.10559 (Dai 2023)
- Residual injection precedent: arXiv:2409.14026 (CAA / Panickssery 2024), Zou et al. 2023 Representation Engineering
- Memory Layers at Scale: arXiv:2412.09764 (Berges Meta FAIR Dec 2024)
- RoPE failure mode: arXiv:2605.15514 (2026 RoPE aliasing proof)
- Economic reference: Together AI pricing $0.18/M tokens (June 2026)
- Prior hebbian_vs_gd_flops_gap drill: notes/research_drill_hebbian_vs_gd_flops_gap_2026-06-03.md

---

## Contract

exp_dev designs and queues the cheapest decisive test per the research note's "Cheap decisive test" and sub-cell refinement sections. Pre-register HARD-PASS / HARD-FAIL bands before shipping. Priority order: G (cheapest, CPU) -> I (GPU, risk elimination) -> H (GPU, product story). Anchors G and I can potentially be batched on the same GPU instance.

## Autonomy declaration

exp_dev decides: anchor naming, exact context lengths tested, injection layer fraction (near 0.7L), injection magnitude schedule, HARD-PASS/HARD-FAIL threshold values, runner assignment, timeout formula, whether to batch G+I on one instance. Orchestrator does not specify these.
