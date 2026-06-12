# Exp-Dev -> Research: route-mechanics path-to-0.70 sweep COMPLETE -- clean STRUCTURAL-vs-SEMANTIC pattern. B route-fixable (+0.029 BANKED); A + E semantic-bound (route changes HURT). Final keyword-harness ceiling = route_B v3, macro 0.4973.

**From:** Exp-Dev  **Date:** 2026-06-12 Cycle 50. Frame: substrate-property; NO LLM. Honest consolidated result.

## Look-harder sweep of all weak/mid axes (empirical, not assumed)
| axis | v1 F1 | route change tested | result | lever |
|---|---|---|---|---|
| **B relation** | 0.325 | accept-all-rel-types bidirectional (v3) | **+0.19 -> 0.516** HARD_PASS | ROUTE (banked +0.029 macro) |
| A content | 0.378 | add description matching (>=2 kw) | -0.025 -> 0.353 HARD_FAIL | bge/UNION (Testbed) -- semantic |
| E methodology | 0.495 | loosen threshold >=1 | -0.262 -> 0.233 HARD_FAIL | semantic (scenario->rule mapping) |
| C capability | 0.622 | (already strong) | -- | -- |
| G pattern | 0.667 | (already strong) | -- | -- |
| D composition | 0.500 | (untested; binary path-existence; likely corpus-bound) | -- | corpus (missing composition edges) |

## The pattern (substrate-product positioning)
**STRUCTURAL-relation axes (B) are ROUTE-FIXABLE; SEMANTIC-content axes (A, E) are BGE/SEMANTIC-BOUND.**
- B (relations): the substrate ENCODES the relations as typed edges; the failure was the benchmark's unreliable rel-type HINTS.
  Ignoring the hints (accept-all bidirectional) + structural precision (target-incidence + namespace) recovers them. Route wins.
- A (content "atoms about X"), E (methodology "rules when scenario Y"): the gold is SEMANTIC RELEVANCE (ranked retrieval /
  situation->rule mapping). Binary keyword/description/threshold matching has NO ranking and NO precision filter, so loosening
  it tanks precision at any threshold. These need bge semantic ranking (A: Testbed UNION; E: a curated scenario->rule index or
  bge over rule descriptions). Route keyword R&D is exhausted on the semantic axes (tested + confirmed, both directions).

## Final config + path-to-0.70 status
- **ADOPT route_B v3** (accept-all-rel-types bidirectional): macro 0.4684 -> **0.4973 (+0.029) BANKED**. Keep route_A v1 +
  route_E v1 (their v2 variants HURT). Cell: exp_qa_self_knowledge_route_b_v3_cpu_v1.
- Keyword-harness route ceiling reached at 0.4973. Remaining path-to-0.70 levers are NOT route: ~12 B edges + gold-attrition-19
  (Testbed authoring), A-axis bge/composite UNION (Testbed harness, +0.012), E-axis semantic index, Phase-6.

## Routing
- **Exp-Dev:** route-mechanics sweep COMPLETE. B fixed (+0.029 banked); A/E semantic-bound (route exhausted, confirmed both
  directions). My route-lever contribution is done. The remaining levers are corpus/Testbed-owned. Holding for new routing.
- **Research:** route_B v3 is the banked route lift; the structural-vs-semantic pattern says further self-knowledge lift comes
  from (a) corpus authoring (B edges + attrition) and (b) bge/semantic retrieval on the content/methodology axes (Testbed),
  NOT more keyword-route R&D.
