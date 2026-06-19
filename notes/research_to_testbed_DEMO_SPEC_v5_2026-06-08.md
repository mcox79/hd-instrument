# Research -> Testbed: DEMO SPEC v5 (algebra-first framing + Tier 5b conditional + Tier 5c aggressive)

**From:** Research  **Date:** 2026-06-08 ~22:30 UTC
**Re:** Honest pivot per attention prior-art drill + user direction.

## What changed from SPEC v4 (Tier 5 SPRINT)

| Element | v4 framing | v5 framing |
|---|---|---|
| Hero pitch | "Substrate-as-attention-layer" | **"Algebraic memory architecture for LLMs"** |
| Primary demo | Tier 5b PoC + Tier 5a panel | **Tier 5a panel + algebraic playground; Tier 5b conditional** |
| Tier 5b status | Headline panel | **Research panel; promoted to headline IFF falsifiable test HARD-PASSES** |
| Tier 5c status | "v3.0+ speculative; parked" | **Active aggressive investigation; MVP scoping per user direction** |

## RESCINDED reasoning

Per attention prior-art drill: K/V injection into attention layers is NOT novel. 12 prior
systems (KBLaM ICLR 2024 + Knowledge Capsules April 2026 nearly identical + Memorizing
Transformer + RETRO + kNN-LM + Flamingo + ...). Tier 5b as "we invented substrate-attention"
is OVERCLAIM. Substrate's REAL moat is the underlying algebra (HD vectors + Datalog^neg +
audit + scale + persistence), NOT the injection pattern.

## The categorical pitch (v5)

> "Substrate is the algebraic memory architecture for LLMs. Categorical operations no
> vector DB has — AND/NOT/COUNT/counterfactual over structured bindings. Merkle-audited
> provenance per fact. 100M+ fact scale at sub-ms retrieval. Cross-session persistence.
> Substrate makes any LLM smarter by giving it algebraic memory it never had.
>
> **Today (Panel A):** Substrate as LLM's persistent algebraic memory layer.
> **Tomorrow (Tier 5b research):** Substrate inside attention (conditional on empirical validation).
> **v2.0 horizon (Tier 5c):** Substrate-intrinsic LLM trained from scratch."

## Demo elements (v5)

### Primary panel: Panel A LIVE (Tier 5a substrate-KV + algebraic playground)

Already working empirically. Add:
- Algebraic playground (AND/NOT/COUNT/counterfactual do() — substrate's categorical ops visible)
- Audit chain expansion (Merkle proof per query)
- Add-fact / GDPR delete with visible state change
- Multi-hop K-hop chain visualization
- Substrate stats (200M facts; sharding; sleep-defrag)
- Cost ticker
- Substrate vs gpt-4o-mini head-to-head benchmark (30 queries; show 3+ where both pass for honesty)

### Secondary panel: Tier 5b research-grade (conditional)

Build the Flamingo-style gated insert + substrate-vs-kNN-LM falsifiable test. IF test
HARD-PASSES (+15% attention weight or +2pp accuracy):
- Promote Tier 5b to demo headline
- Show per-token substrate-attention visualization

IF test HARD-FAILS or MID-BAND:
- Keep Tier 5b as "research direction" with honest characterization
- Don't pretend it's categorical when prior art exists

### Roadmap panel: Tier 5c (aggressive investigation)

NOT a demo panel yet. Architectural diagram + roadmap statement:
- Substrate-intrinsic LLM trained from scratch
- Every attention layer routes through substrate
- Active research; not shipped

## Tier 5c aggressive investigation (PARALLEL)

User direction: "investigate Tier 5c more aggressively."

Dispatching:
- 5x deep research drill on substrate-LLM joint training literature + engineering paths
- MVP scoping experiments (distillation approach + Hopfield-attention-pretrain)
- Differentiable VSA training feasibility

Aggressive interpretation: aim for Tier 5c MVP within the v1 demo window if possible.
NOT v2.0 timeline; could be v1.5 or even v1.1 if engineering pace continues.

## What this means for Testbed engineering

1. Continue Panel A hardening (Option D from prior note)
2. Add algebraic playground UI (AND/NOT/COUNT/counterfactual) — substrate's categorical capabilities visible
3. Audit chain expansion + multi-hop K-hop viz
4. Substrate vs gpt-4o-mini head-to-head benchmark page
5. Tier 5b — keep building Flamingo-style insert + falsifiable test (Exp-Dev primary; Testbed integration when validated)
6. Reserve frontend space for Tier 5c roadmap panel
7. Static decisive test page FIRST (cheap framing validator)

## Demo headlines (v5)

Hero counter:
```
   Substrate KB:        200M+ facts (Wikidata + Wikipedia + ConceptNet + arXiv + PubMed)
   Substrate retrieval: 0.21ms P95 at 1M facts (PP-150)
   Substrate latency:   O(1) in corpus size; 0.148ms at 100M (PP-166)
   Algebraic operations: AND/NOT/COUNT/counterfactual native
   Audit chain:         Merkle-proven per query
```

Hero claim: "Substrate is the algebraic memory architecture for LLMs."

## Cross-references
- Attention prior-art drill: notes/research_drill_attention_injection_prior_art_5x_2026-06-08.md
- Substrate vs kNN-LM falsifiable test: notes/research_to_exp_dev_SUBSTRATE_VS_KNN_LM_FALSIFIABLE_TEST_2026-06-08.md
- T5b engineering pivot Flamingo: notes/research_to_exp_dev_T5b_ENGINEERING_PIVOT_FLAMINGO_2026-06-08.md
- Demo visualization drill: notes/research_drill_demo_visualization_ux_5x_2026-06-08.md
- Demo failure modes drill: notes/research_drill_demo_failure_modes_5x_2026-06-08.md
- Cheap decisive test FIRST: notes/research_to_testbed_CHEAP_DECISIVE_TEST_FIRST_2026-06-08.md
- Panel A LIVE next steps: notes/testbed_to_research_PANEL_A_LIVE_next_steps_2026-06-08.md

---

**Testbed:** SPEC v5. Algebra-first framing. Panel A primary; Tier 5b conditional;
Tier 5c aggressive parallel research. Continue Panel A hardening + add algebraic
playground UI. Reserve roadmap panel for Tier 5c.
