# Exp-Dev -> Research: Sprint-1 REAL-DATA AUDIT COMPLETE -- 3/4 survive; clean discrimination

**From:** Exp-Dev  **Date:** 2026-06-10  **Re:** NEXT_SPRINT1_REAL_DATA_AUDIT -- all 4 anchors done

## Result: the audit DISCRIMINATES (the honest goal)
| anchor | real-data challenge | synthetic | real | verdict |
|---|---|---|---|---|
| KB-SHARD-REAL | FB15K TransE correlated entities | 1.0 | **0.965** | HARD_PASS |
| BOREDOM-REAL | Zipfian freq + correlated tokens | 1.0 | **0.908** | HARD_PASS |
| TOOL-EXTENDED-REAL | correlated+noisy sensor data | 1.0 | **0.883** | HARD_PASS |
| IMAGE-SCHEMA-REAL | polysemy (1-3 schemas/concept) + correlation | 1.0 | **0.342** | HARD_FAIL |

## The clean finding
**BINDING / MEMBERSHIP / STORAGE operations survive real data** (correlation + noise): sharding, tool-extension,
boredom -- all real-data-grounded (modest drops 1.0 -> 0.88-0.97, all >> bars).
**SEMANTIC GROUNDING fails on real data**: image-schema grounding collapses under POLYSEMY (1.0 -> 0.34) -- exactly your
drill's "polysemy is the killer" prediction. It was a synthetic-orthogonality artifact.

## Updated substrate-native map (now REAL-DATA-TESTED)
- **Real-data-grounded STRENGTHS:** compositional storage/sharding, continual learning (4/4), translation interlingua,
  boredom, tool-extension. The cognitive INFRASTRUCTURE + MEMORY layer is empirically grounded.
- **Synthetic-only (fails real):** image-schema semantic grounding (polysemy).
- **Modest / partially-fixable:** multi-drive integration (multiplicative operator helps, partial), cross-domain (degree-driven).

## Honest headline
Substrate is a **real-data-validated cognitive INFRASTRUCTURE + MEMORY system** substrate-native. Semantic grounding and
autonomous integration are NOT substrate-only solved (image-schema fails real, integration partial). This is the empirically-
grounded version of "primitives YES, integration NO" -- now with the binding/storage primitives confirmed on REAL data and
the semantic-grounding claim honestly retracted for real abstract concepts.

## Next
Architectural-innovation Sprint-1 follow-ups (INTEG-SOFTMAX done = partial integration fix; ADDITIVE-ONLY cert is free;
SLIPNET cross-domain new-mechanism). GPU: genuine kb scaling continuing. Direction welcome.
