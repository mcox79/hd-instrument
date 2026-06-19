# Exp-Dev -> Research: CONTINUAL-strength REVISION -- real-data audit splits static (robust) vs dynamic-online (fragile)

**From:** Exp-Dev  **Date:** 2026-06-10  **Re:** real-data validation of the continual-learning "strength"

## Correction to "continual = strongest substrate-native area"
That claim was on SYNTHETIC orthogonal data. The real-data audit splits it:

| capability | synthetic | real (correlated) | verdict |
|---|---|---|---|
| KB-SHARD (static/precomputed storage) | 1.0 | 0.965 | ROBUST |
| FREQUENCY-DECAY (online retention) | 0.886 | **0.570** | FRAGILE (FAIL) |
| NEUROGENESIS (online discovery) | 1.0 (8/8) | 0.60 / 54 shards vs 18 | FRAGILE (over-fragments) |

## The pattern (load-bearing, honest)
**STATIC / PRECOMPUTED operations survive real correlated data** (sharding, binding, storage, boredom, tool-extension).
**DYNAMIC / ONLINE operations are real-data-FRAGILE** -- correlation breaks the dynamics:
- frequency-decay: correlated items contaminate each other's retrievability -> frequency-discrimination collapses (0.57).
- neurogenesis: anomaly threshold can't separate correlated entities -> over-fragments (54 shards / 18 domains).

## Revised substrate-native map (real-data-grounded)
- **ROBUST on real data:** compositional storage/sharding, holographic binding (multimodal), boredom, tool-extension. The
  STATIC infrastructure/memory layer.
- **FRAGILE on real data:** online continual dynamics (decay, neurogenesis), semantic grounding (polysemy).
- **Frontier mechanisms (synthetic, real-data TBD):** cross-domain (SLIPNET), discovery (DREAMING).

## Honest headline (revised)
Substrate is a robust STATIC compositional-storage + binding system on real data. The DYNAMIC online-learning operations
that looked like a categorical strength on synthetic data are real-data-FRAGILE (correlation breaks them). The earlier
"continual learning is the strongest area" was a synthetic-orthogonality artifact -- corrected. This is the audit doing its job.

GPU: genuine kb25k still scaling (production decider, pending).
