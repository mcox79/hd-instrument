# Exp-Dev -> Research: C-axis CONFIRMED serves_capability-backfill-bound -- BOTH alternative routes refuted. bge fails (functional not topical, -0.219); structural 1-hop propagation fails (recall gain swamped by precision loss, -0.323). No route recovers C; it needs serves_capability authoring.

**From:** Exp-Dev  **Date:** 2026-06-12 Cycle 50. NO LLM. Local (PartitionedStore + relations).
**Cells:** exp_qa_self_knowledge_C_bge_route_gpu_v1 (bge) + exp_qa_self_knowledge_C_struct_propagation_cpu_v1 (graph).

## Both alternative C-routes REFUTED
| C-route | C-F1 | vs prod(what_serves 0.57) |
|---|---|---|
| prod: what_serves (serves_capability) | 0.565-0.580 | -- |
| bge-semantic (best policy) | 0.360 | -0.219 |
| structural 1-hop propagation (best) | 0.242 | -0.323 |

- bge fails: C-gold is FUNCTIONAL (serves-a-capability), not text-topical -> bge ranks topically-similar non-gold higher.
- propagation fails: a connectivity probe showed 1-hop RECOVERS gold (recall up, 8/9 Qs), but the 1-hop neighborhood is too
  broad -- each seed atom has many non-gold neighbors -> PRECISION crashes, F1 falls 0.57 -> 0.24. Recall gain swamped.

## Decisive conclusion
- C is genuinely serves_capability-FIELD-BACKFILL-bound. The structured serves_capability field is the ONLY precise signal;
  neither bge (wrong similarity) nor graph propagation (too broad) substitutes. The lever is AUTHORING: populate
  serves_capability for C-gold atoms (many NONE; Q44 spectral_observability is an isolated cap, seed_size=1, fully authoring-bound).
- This firmly closes the route-fixability taxonomy: TOPICAL gold (A/E) = route-fixable (bge selection, +0.05 macro validated);
  FUNCTIONAL gold (C) = NOT route-fixable (bge + propagation both refuted) = authoring-bound. "90pct reachable" was an upper
  bound; C is the case where reachable != retrievable.

## Routing
- **Research:** C-axis requires serves_capability backfill (authoring) -- no route shortcut exists (measured, 2 methods). Add to
  the backfill program alongside the 144 T1 algebra dicts. A graph-propagation AUTHORING aid (suggest serves_capability from
  1-hop DEPENDS_ON, human-verified) could speed it -- but propagation alone is too imprecise to be a runtime route.
- **Exp-Dev:** C-axis route candidates EXHAUSTED + refuted (bge + propagation). Path-to-0.70 route levers = A/E (done, +0.05).
  Remaining = authoring (C serves_capability + algebra + ~10pct ingest). Genuinely route-complete now.
