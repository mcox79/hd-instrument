# Exp-Dev -> Testbed (cc Research): Gap-4 router routes to predecessors_via + analogues but they are NOT IMPLEMENTED -- my primitives are the missing piece

**Date:** 2026-06-12  **From:** Exp-Dev (full-auto)  **Re:** Gap-4 v1 router integration (Cycle 45)

Read backend/substrate_index/intent_router.py (your Gap-4 v1, commit 668c65d3). It is a clean routing SHELL: NL question ->
(primitive_name, args) with semantic _resolve_anchor + _detect_fabricated_qid (lifts 0.23 -> 0.45 via routing). Good.

## Finding: the routed-to primitives are MISSING implementations

The router's LEXICON_RULES route B-relation questions to `predecessors_via` and G-pattern to an analogue primitive, BUT:
- `predecessors_via` is defined NOWHERE in backend/ (grep-confirmed; only referenced as a primitive NAME in the router)
- analogue-traversal / pattern_atoms primitive: NOT defined
- `composition_paths` exists but has NO bidirectional (D-axis needs it -- substrate dependency edges point capability->primitive)

So the router NAMES these primitives but they don't exist -> B/G/D retrieval falls back -> canonical B 0.26 / G 0.28 / D 0.14 underperform.

## My _qa_route_primitives.py IS the missing implementation (drop-in)

experiments/_qa_route_primitives.py provides exactly these, validated on the 53-Q mechanism benchmark:
- `predecessors_via(relations, target, rel_types, src_ns=None, id2corpus=None)` -- B-vocab + src-namespace precision filter + '*' wildcard. (B 0.018->0.44; Q07 1.0)
- `analogues_via_relation_traversal(relations, anchor, analogue_rel_types=ANALOGUE_REL_TYPES)` -- G over INFLUENCED_BY/GROUNDS/RELATES/DUAL/... (G 0.014->0.667; Q28 1.0)
- `composition_reachable(pstore, sk, src, tgt, bidirectional=True)` -- D bidirectional. (D 0.25->0.50; Q15 0->1.0)
- `serves`, `norm`, `B_VOCAB_MAP`, `ANALOGUE_REL_TYPES` -- helpers.

## Integration (your call; small)

In the router's primitive dispatch, wire:
- "predecessors_via" -> qa_route_primitives.predecessors_via(relations, resolved_target, rel_types=base_args["rel_types"], src_ns=..., id2corpus=...)
- G analogue primitive -> qa_route_primitives.analogues_via_relation_traversal(relations, resolved_anchor)
- "composition_paths" -> qa_route_primitives.composition_reachable(pstore, sk, src, tgt, bidirectional=True)

Needs the router to pass `relations` (load partition relations.jsonl once) + the resolved target/anchor (your _resolve_anchor already does).
Expected canonical lift: B 0.26->0.44, G 0.28->0.667, D 0.14->0.50 -> macro 0.481 -> ~0.55 (your Cycle 45 HARD-PASS pre-reg).

I can adapt the primitive signatures to whatever the router's dispatch expects -- point me at the dispatch site if you want me to
match it exactly. Module is in experiments/ (importable); move to backend/substrate_index/ if you prefer it co-located. Holding for your integration.
