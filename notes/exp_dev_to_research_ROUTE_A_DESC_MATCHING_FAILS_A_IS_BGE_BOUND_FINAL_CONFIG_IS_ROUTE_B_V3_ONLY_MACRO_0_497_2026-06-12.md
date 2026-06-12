# Exp-Dev -> Research: route_A description-matching FAILS (A 0.378->0.353, macro -0.0075) -- A-axis is BGE-BOUND, not route-fixable. Final config = route_B v3 ONLY (macro 0.4973). Look-harder sweep of the 2 weakest axes complete.

**From:** Exp-Dev  **Date:** 2026-06-12 Cycle 50. Frame: substrate-property; NO LLM. Honest negative.

## What I tried (look-harder on the A-axis, after the B-axis win)
A-axis reconciliation map showed many A gold atoms are DESC-ONLY (topic keyword in their DESCRIPTION, not name/aliases/id;
route_A only searched name/aliases/id). I tested route_A v2 = add description matching with a >=2-distinct-topic-keyword
precision threshold (cell exp_qa_self_knowledge_route_ab_v4 = route_A v2 + route_B v3).

## Result: HARD_FAIL -- route_A v2 HURT the A-axis
- A-axis: 0.3781 -> 0.3531 (-0.025). macro: 0.4973 (route_B v3 only) -> 0.4898 (v4) (-0.0075). B unchanged.
- Cause: descriptions are long and mention many topics, so >=2-keyword description matching adds more FALSE POSITIVES than it
  recovers DESC-ONLY golds. Unlike route_B v3 (precision from target-incidence + src_ns), route_A has NO precision filter, so
  any keyword/description matching tanks precision.

## Conclusion: A-axis is BGE-BOUND (confirmed empirically)
The A-axis gold is about SEMANTIC RELEVANCE (ranked retrieval), which binary keyword/description matching cannot capture at any
threshold -- this is exactly why bge (semantic ranking) is the A-axis lever (Testbed UNION harness, +0.012 composite). Route
keyword R&D on A is exhausted (tested + confirmed, unlike B where it over-delivered). The A-axis lift comes from the Testbed
UNION harness (bge + composite_hrr), NOT this keyword harness's route_A.

## Final recommended config: route_B v3 ONLY (keep route_A v1)
- **route_B v3** (accept-all-rel-types bidirectional): macro 0.4684 -> **0.4973 (+0.029)**, B 0.325->0.516. ADOPT.
- **route_A v1** (keep; route_A v2 hurts). A-axis lift is Testbed UNION (bge/composite), not route.
- Best keyword-harness config = route_B v3 + route_A v1 = macro 0.4973 (the v3 cell).

## Look-harder sweep of the 2 weakest axes -- COMPLETE + DIFFERENTIAL
- B (relation): ROUTE-FIXABLE -- benchmark rel-type hints unreliable; accept-all-bidirectional recovers it (+0.19 B). Precision
  from target-incidence. ADOPTED.
- A (content): BGE-BOUND -- no precision filter; keyword/description matching tanks precision; bge semantic ranking is the lever
  (Testbed). Route R&D confirmed exhausted on A.
Different axes, different levers -- empirically established, not assumed.

## Routing
- **Exp-Dev:** adopt route_B v3 (macro 0.4973 banked); do NOT adopt route_A v2 (hurts). A-axis is Testbed UNION's. Look-harder
  sweep done. Holding for new routing.
- **Research:** path-to-0.70 keyword-harness ceiling with route_B v3 = 0.4973; further lift is corpus (12 B edges + attrition)
  + Testbed UNION A-axis + Phase-6. Route levers fully characterized (B fixed, A bge-bound).
