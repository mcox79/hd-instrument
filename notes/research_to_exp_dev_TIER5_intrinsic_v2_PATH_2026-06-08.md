# Research -> Exp-Dev: TIER 5 intrinsic-LLM v2.0 PATH (substrate-as-attention-layer 4-8 GPU-weeks feasible)

**From:** Research  **Date:** 2026-06-08 ~14:25  **Re:** Substrate-LLM intrinsic language
5x drill flagged: cheapest path to substrate-intrinsic LLM is 4-8 GPU-weeks (NOT v3.0
speculative). Major roadmap implication.

## Drill finding

**Headline:** "Attention is a soft approximation of VSA unbinding (arXiv 2512.14709
confirmed); the algebraic gap between current Tier 5 substrate-KV and a substrate-
intrinsic LLM is SMALLER than it appears — but the three interpretations of 'intrinsic'
have very different engineering costs."

**Three interpretations + costs:**

| Interpretation | Engineering cost | Status |
|---|---|---|
| Substrate-KV memory layer (current Tier 5) | DONE | D1/D2/D3 HP |
| Substrate-as-attention-layer in 1-2 transformer blocks | **4-8 GPU-weeks** | FEASIBLE near-term |
| Full v3.0 joint pretraining | months/years; speculative | v3.0+ |

## Strategic roadmap shift

The middle interpretation (substrate-as-attention-layer) was previously parked at "v2.0+
research" but the drill estimates 4-8 GPU-weeks engineering. This is WELL WITHIN v2.0
timeframe (3-6 months post-v1).

**Revised tier roadmap:**

| Tier | Previous timeline | NEW timeline |
|---|---|---|
| Tier 5 substrate-KV memory | DONE (cycle 185 D1/D2/D3 HP) | DONE |
| **Tier 5 substrate-as-attention-layer** | **v3.0+ R&D speculative** | **v2.0 candidate** (4-8 GPU-weeks; FEASIBLE) |
| Full substrate-intrinsic LLM joint pretrain | v3.0+ speculative | v3.0+ speculative (unchanged) |

## Anchor: substrate-as-attention-layer prototype (Pythia-160M; 1 layer replaced)

### Substrate-product reading
Take Pythia-160M (12 layers). Replace ONE attention layer (e.g., middle layer 6) with
substrate-attention computation:
- Query Q comes from previous layer
- Substrate retrieval: Q -> top-K relevant bindings from substrate KB
- Keys = bound (entity, relation) vectors; Values = bound (entity, fact) vectors
- Compute attention output as weighted sum of substrate-retrieved Values
- Pass forward as if it were standard attention

Variant A: ONE layer replaced; rest unchanged
Variant B: TWO adjacent layers replaced (middle 6-7)

### Engineering
- ~4-8 GPU-weeks per drill estimate (heavier than substrate-KV; lighter than full pretrain)
- Pythia-160M ports easily; Pythia-1.4B if larger needed
- Validation: WikiText perplexity within 10% of baseline AND substrate retrieval working
- HARD-PASS: substrate-attention-layer Pythia-160M perplexity within 15% of baseline AND
  substrate hits stored facts correctly

### Tier hint
LOCAL GPU sustained (~6 GB VRAM for Pythia-160M with substrate; could need cloud for
Pythia-1.4B variant)

## v2.0 substrate-intrinsic LLM pitch (if HP)

> "Substrate IS the LLM's attention mechanism in 1-2 transformer layers. Same
> base-model size; substrate provides external memory layer that scales to 100M+
> facts; LLM forward pass routes through substrate at every query. Categorical
> efficiency: no O(n²) attention cost over context; substrate's sharded sub-ms lookup
> replaces it for keyed memory."

## v3.0+ retains full joint pretraining

Substrate-LLM joint pretraining (full v3.0 vision) remains speculative — months/years
of training; need new architecture; large compute. Stays parked. v2.0 substrate-as-
attention-layer is the BRIDGE.

## Cross-references
- Intrinsic Language 5x drill: notes/research_drill_substrate_llm_intrinsic_language_5x_2026-06-08.md
- arXiv 2512.14709 attention=VSA binding identity (Dec 2024): cited in drill
- Ramsauer 2020 attention=Hopfield retrieval: cycle 178+
- Tier 5 D1/D2/D3 HP (substrate-KV foundation): cycle 185 + D2 Pythia-1.4B HP
- Original Tier 5 routing (D1/D2/D3): notes/research_to_exp_dev_TIER5_MVE_GREEN_strategic_implications_2026-06-08.md

---

**Exp-Dev:** flag for v2.0 roadmap (post-v1-demo): substrate-as-attention-layer in
1-2 Pythia blocks is the FEASIBLE Tier 5 intrinsic-LLM path at 4-8 GPU-weeks. Major
upgrade over what we previously parked as v3.0 R&D.

Engineering kickoff after v1 demo ships. Not v1-blocking; v2.0 priority.
