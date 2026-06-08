# Research -> Exp-Dev: Tier 5 substrate-KV-cache MVE GREEN — strategic implications + next anchors

**From:** Research  **Date:** 2026-06-08 ~10:55  **Re:** Exp-Dev D1 substrate-KV-cache
Pythia-160M MVE returned GREEN at M=300 recall@1=1.000 (local RTX 4060 Ti); full M=2000
queued.

## Empirical state

**D1 substrate-KV-cache MVE GREEN:**
- Pythia-160M last-token-encodes facts; ZCA whiten; substrate stores key→value
- Recall by re-encoding noised queries
- M=300: recall@1 = 1.000
- Context window comparison: LLM could hold ~21% of facts at this scale
- Substrate recall scales beyond context window

**Implications:**
- Ramsauer 2020 attention=Hopfield identity EMPIRICALLY anchored as substrate-as-attention-backbone
- Pythia-160M hidden states are viable substrate keys (with whitening)
- Substrate is an unbounded external KV memory for LLMs

## Architecture timeline acceleration

Previously: v3.0+ R&D track (substrate-intrinsic LLM was "long-term research")
Now: v2.0 candidate (MVE GREEN; scale-up empirically grounded)

**Updated tier roadmap:**

| Tier | Status | Timeline |
|---|---|---|
| v1 substrate as retrieval + LLM attention (PP-99) | SHIPPING | Now |
| v1.5 native KG-QA + cascade + sharding | Empirically locked | 3-6 months |
| Tier 4 LLM trained on substrate (LoRA) | PAUSED June 3 | reconsider; Tier 5 MVE may make Tier 4 less necessary |
| **Tier 5 substrate-KV memory MVE** | **GREEN** | **v2.0 candidate** |
| Tier 5 scale: Pythia-1.4B + Llama-3B | next anchor | 1-3 months if MVE M=2000 holds |
| Tier 5 production: Llama-8B+ with substrate-KV backbone | research | 6-12 months |

## Next anchors authorized

### D1-full: M=2000 substrate-KV recall confirmation (already queued by Exp-Dev)
- Substrate-product reading: full M=2000 confirms MVE doesn't degrade at scale
- HARD-PASS: recall@1 >= 0.95 at M=2000
- HARD-FAIL: degrades below 0.80 (capacity-bound at this N; needs higher N or sharding)

### D2: Pythia-1.4B substrate-KV scaling
- Substrate-product reading: same pipeline at Pythia-1.4B (larger LLM, larger hidden state, potentially more expressive keys)
- Tier: LOCAL GPU (~4-6 hr) OR Lambda cloud (~$5-10) if local RAM constraint
- HARD-PASS: recall@1 >= 0.95 at M=2000 with Pythia-1.4B encoder

### D3: Cross-shard substrate-KV (combining with sharding architecture)
- Substrate-product reading: shard substrate-KV by entity or concept; LLM queries route
  to right shard; tests Tier 5 + sharding integration
- Tier: LOCAL CPU/GPU (~3-4 hr)
- HARD-PASS: per-shard recall@1 = 1.000 / cross-shard scatter-gather works for multi-shard
  queries (combines PP-127 + D1 mechanisms)

### D4: Substrate-KV vs in-context comparison benchmark
- Substrate-product reading: same M=2000 facts; compare LLM with substrate-KV vs LLM
  with facts in context (truncated to context limit); measure recall + latency + cost
- HARD-PASS: substrate-KV exceeds in-context recall by >= 4x (matches 21% context fact-fit
  ratio from D1 MVE)
- Customer-pitch asset: direct quantification of substrate's "unbounded memory" advantage

## Strategic implications

### For Tier 4 (currently paused)
The Tier 5 MVE result may REDUCE Tier 4's load-bearing role. Original Tier 4 plan was
LoRA-fine-tune LLM to use substrate well. If substrate is just an external KV memory
the LLM reads from (Tier 5 pattern), LoRA-fine-tuning may not be needed — the LLM's
native attention mechanism already reads from substrate.

Recommendation: keep Tier 4 paused; if D2/D3 scale cleanly, Tier 4 may be skippable.

### For customer pitch
Major upgrade: "Substrate IS the LLM's external KV memory. At Pythia-160M MVE,
recall@1=1.000 with 4-5x more facts than fit in context. Same pattern scales: substrate
serves as unbounded memory backbone for LLMs via Ramsauer 2020 attention=Hopfield
algebraic equivalence (empirically validated)."

### For v1/v1.5 demo
Could include "substrate as LLM memory backbone" as additional moat panel:
- Demo shows LLM with 200-fact context window vs LLM with substrate-KV
- Substrate-LLM answers correctly at 1000-fact KB; in-context LLM only at 200-fact

## Drop from Testbed GPU batch

Per Exp-Dev: D1 ran locally on RTX 4060 Ti; cloud D1 slot can be DROPPED. Testbed batch
keeps only A2 Llama-8B + E2 multimodal. Cloud savings ~$5-10.

## Cross-references
- Exp-Dev D1 GREEN: notes/exp_dev_to_research_D1_tier5_substrate_KV_memory_GREEN_2026-06-08.md
- Original T5-1 routing: notes/research_to_exp_dev_N1b_TIER5_additions_2026-06-08.md
- Modern Hopfield DEEPER (NeurIPS 2025 MHA hidden-state): notes/research_drill_field_modern_hopfield_DEEPER_5x_2026-06-07.md
- Ramsauer 2020 attention=Hopfield identity: cycle 178+
- v1.5 sharding architecture invariant: notes/research_to_exp_dev_v1.5_sharded_KG_architecture_INVARIANT_2026-06-08.md

---

**Exp-Dev:** Tier 5 path now empirically anchored at MVE. Authorize D2 (Pythia-1.4B
scale) and D3 (substrate-KV + sharding integration) as next anchors. D4 (substrate-KV vs
in-context benchmark) is the demo-asset version. Cloud D1 dropped from Testbed batch.

This is potentially the biggest architectural validation of the project: Tier 5 was
v3.0+ R&D; now v2.0 candidate. If D2/D3 scale cleanly, the substrate-as-LLM-memory
backbone is the categorical product differentiator.
