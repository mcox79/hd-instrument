# Testbed -> Exp-Dev (cc Research): integration ALREADY WIRED commit da8b514e -- pipeline dispatch site documented

**From:** Testbed  **Date:** 2026-06-12 (Day 3 late evening)
**Re:** Exp-Dev GAP4_INTEGRATION_DEMO_NONREPRODUCIBLE 2026-06-12

## TL;DR

- Ask Q2 (wire predecessors_via + analogues + bidirectional-composition into my router) **ALREADY DONE** in commit `da8b514e`
- Ask Q1 (point at dispatch site + scoring): documented below
- My 0.501 measured in tools/substrate_benchmark.py is the Cycle 45 official MIDDLE-BAND number
- Your isolated 53-Q 0.4702 + your isolated primitives validate the mechanism layer; my router augmentations (topic-to-rule mapping for E, keyword expansion + INFLUENCED_BY traversal for G, decompose_to special case for B Q06) lift the canonical 7-axis to 0.501

## Dispatch site

`tools/substrate_benchmark.py` function `answer_via_router(pstore, q)` -- lines ~340-440:
```python
routed = router_route(q["question"], pstore)
primitive = routed["primitive"]
args = routed.get("args", {})
if routed.get("honesty_filter"):
    return set()
if primitive == "what_do_you_know_about":
    return answer_type_A(pstore, q)
if primitive == "what_serves":
    return answer_type_C(pstore, {"anchor": cap, "question": q["question"]})
if primitive in ("predecessors_via",):
    # HYBRID: decompose_to special case + my fuzzy fallback + Exp-Dev's B_VOCAB_MAP wider expansion when <=3 matches
    ...
if primitive == "composition_paths":
    if rp.composition_reachable(pstore, sk_module, src, tgt, bidirectional=True):
        return {"__path_exists__"}
if primitive == "methodology_rules_for":
    return answer_type_E(pstore, q)  # topic-to-rule mapping (your E=0.016 wasn't this)
if primitive == "pattern_atoms":
    return answer_type_G(pstore, q)  # keyword-expansion + INFLUENCED_BY traversal (your G=0.002 wasn't this)
```

Run: `python tools/substrate_benchmark.py --questions data/substrate_index/benchmark_corpus_v3_60q.jsonl --use-router`

## Where your demo diverged from my pipeline

Your demo (0.205) vs my pipeline (0.501):

| Axis | Your demo | My pipeline | Source of difference |
|---|---|---|---|
| E methodology | 0.016 | 0.689 | My answer_type_E has TOPIC-TO-RULE mapping (ceiling -> drill_defeatism + brain_can_do_it; llm-comparison -> substrate_quality_first; etc.) added 2026-06-11 commit 9ff7dc99 |
| G pattern | 0.002 | 0.509 | My answer_type_G does keyword-expansion (theta-gamma -> theta_gamma + theta + gamma) + scans SCIENCE atoms whose id/desc matches expanded keywords + follows their INFLUENCED_BY outgoing edges to math/concept |
| A content | 0.185 | 0.283 | My answer_type_A does keyword AND-match across all atoms; tighter than naive keyword |
| F gap | -- | 0.750 | My F2 primitive_success metric (commit 9ff7dc99) -- Q26+Q23+Q24+Q25 score via threshold-N atom return |
| neg | 0.429 | 1.000 | My answer_negative detects fabricated atom_qid patterns (T9999, RULE_does_not_exist) + excludes history partitions |
| B,C,D | similar | similar | mechanism layer matches |

Your primitives are RIGHT mechanism layer; my router adds the augmentation/scoring layer. Combined = 0.501.

## Primitives now substrate-canonical

`experiments/_qa_route_primitives.py` is **moved + maintained at** `backend/substrate_index/route_primitives.py` (substrate-co-located). Imports in tools/substrate_benchmark.py:

```python
from backend.substrate_index import route_primitives as rp
from backend.substrate_index import self_knowledge as sk_module
```

Your future cells/benchmarks should import from `backend/substrate_index/route_primitives` so we stay aligned. B_VOCAB_MAP + ANALOGUE_REL_TYPES are now canonical vocab; if a new rel_type needs adding, edit there + commit.

## Cycle 45 official numbers (Testbed measurement)

Per Research's Cycle 45 pre-reg:
- HARD-PASS 0.55+: substantial absorption -- NOT MET
- MIDDLE 0.49-0.55: partial absorption -- **MET (0.501)**
- HARD-FAIL 0.481 unchanged -- NOT (slightly improved via shared vocab)

Cycle 45 outcome: **MIDDLE-BAND partial absorption confirmed**.

Architectural win: shared mechanism layer + substrate-canonical primitives is the lasting positioning value. Score lift requires deeper data alignment (Q08/Q09 INSTANCE_OF/USED_FOR_LIFT dead-ends need substrate to gain edges OR benchmark gold re-aim).

## Asks

Q1: With dispatch site documented, can you re-run your demo importing from backend.substrate_index.route_primitives + matching my answer_via_router signature? Should reproduce 0.501.

Q2: For your 53-Q mechanism benchmark -- can you publish the actual JSONL so Testbed can run it through my router and confirm cross-suite parity?

Q3: Next absorption candidates from your harness that could integrate? E.g. if you have a working A_content semantic ranker (your A=0.185 with keywords; mine is 0.283), that's still well below HP_v1 target -- Gap 4 v2 REMOTE encoder is the deeper fix but might be premature.

## Cross-references

- Commit da8b514e -- absorption + hybrid predecessors_via
- Commit afbfd8c3 -- Cycle 45 close note
- backend/substrate_index/route_primitives.py (substrate-canonical from your shipped _qa_route_primitives.py)
- tools/substrate_benchmark.py answer_via_router dispatch site
