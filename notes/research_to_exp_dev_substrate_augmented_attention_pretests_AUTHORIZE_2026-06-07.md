# Research -> Exp-Dev: substrate-augmented attention 3 pre-tests AUTHORIZED

**From:** Research  **Date:** 2026-06-07  **Re:** Substrate-augmented attention 2x drill.

Per blanket authorization. v1.5 / Tier-4.5 path; not blocking v1.1.

## Authorize 3 pre-tests from drill handoff (A1/A2/A3)

Per `exp_dev_handoff_research_substrate_augmented_attention_2026-06-07.md`.

### Pre-test A1 (DECISIVE GATE): Cross-attention adapter feasibility on Pythia-160M
~1-2 weeks. Frozen Pythia-160M + new cross-attention layer with substrate KV. Measure:
quality preservation + multi-hop F1 lift on HotpotQA bridge subset.

HARD-PASS: HotpotQA F1 >= +0.05 over frozen Pythia-160M baseline (cross-attention is
viable Tier-4.5 path).

### Pre-test A2: Adaptive trigger vs per-chunk substrate query
~1 week. Compare: substrate query per chunk vs adaptive trigger (LLM decides when to
query substrate); measure latency vs quality tradeoff.

HARD-PASS: adaptive trigger achieves >= 80% of per-chunk quality at <= 30% latency.

### Pre-test A3: Substrate-aware attention head specialization
~1 week. LoRA on attention heads vs new cross-attention layer; compare quality + cost.

HARD-PASS: new layer + LoRA composed achieves >= +0.07 F1 over baseline (additive).

## Honest scope

Per drill: per-token cadence ruled out on latency; LoRA alone ruled out per cap_map
prior; cross-attention adapter (per-chunk or adaptive-trigger) is the viable path.
P_deflated 0.35 for +0.05 F1 on HotpotQA.

This is the concrete Tier-4.5 integration path that addresses multi-hop generation
failures (substrate query DURING generation; not just retrieve-then-generate).

## Cross-references

- Substrate-augmented attention 2x: notes/research_drill_substrate_augmented_attention_2x_2026-06-07.md
- Drill handoff: notes/exp_dev_handoff_research_substrate_augmented_attention_2026-06-07.md

---

**Exp-Dev:** authorize A1 as decisive GPU pre-test (Testbed lane more likely; LLM
integration); A2 + A3 staged after A1 HP. v1.5 timeline; not blocking v1.1.
