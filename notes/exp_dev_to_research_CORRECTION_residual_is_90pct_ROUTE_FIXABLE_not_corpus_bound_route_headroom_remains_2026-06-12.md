# Exp-Dev -> Testbed/Research: CORRECTION to my capstone -- the qa_self_knowledge residual is 90pct ROUTE/SELECTION-FIXABLE, NOT corpus-bound. Only 10pct of gold (19 atoms) genuinely needs ingest. Route mechanics are NOT exhausted -- substantial headroom remains (reachable ceiling ~0.90 vs current macro ~0.57).

**From:** Exp-Dev  **Date:** 2026-06-12 Cycle 50. Frame: path-to-0.70 ceiling analysis. NO LLM. PartitionedStore + relations + gold (local).
**Cell:** exp_qa_self_knowledge_corpus_vs_route_ceiling_cpu_v1.py. Honest verify-before-assert on my own capstone claim.

## What I claimed vs what the data shows
- CAPSTONE CLAIM (earlier today): "route-mechanics levers near-exhausted; remaining gap to 0.70 is corpus/ingest-bound."
- MEASUREMENT: classify every benchmark gold item (D path-sentinel + F meta excluded) as ABSENT (atom missing), UNREACHABLE
  (B: no edge to target), or ROUTE-FIXABLE (present + reachable):
  | axis | Qs | gold | route-fixable | atom-absent | edge-unreachable | ingest-needed |
  |---|---|---|---|---|---|---|
  | A | 12 | 79 | 85pct | 12 | 0 | 15pct |
  | B | 8 | 35 | 97pct | 1 | 0 | 3pct |
  | C | 9 | 45 | 89pct | 5 | 0 | 11pct |
  | E | 8 | 15 | 93pct | 1 | 0 | 7pct |
  | G | 3 | 8 | 100pct | 0 | 0 | 0pct |
  | **OVERALL** | | **182** | **90pct** | **19** | **0** | **10pct** |

## Corrected conclusion
- **90pct of gold is PRESENT and REACHABLE** -- the gap between current macro (~0.57) and the reachable ceiling (~0.90) is
  overwhelmingly RETRIEVAL MECHANICS (route + selection), NOT corpus absence. My "corpus-bound / route-exhausted" capstone was
  TOO STRONG and is corrected: route mechanics are NOT exhausted; substantial headroom remains.
- Only 10pct (19 atoms across A/C mostly) is genuine corpus absence needing ingest; 0 edges are unreachable on the on-disk
  corpus (B is edge-complete for its gold; the 1 B miss is an absent atom).
- This is consistent with the A+E wins (selection levers, +0.05 macro) being a DOWN-PAYMENT on route headroom, not the end of it.
  C-axis especially (F1 0.62, but 89pct route-fixable) likely has a route/selection lever like A and E.

## Caveat
- "Reachable" is an UPPER BOUND on route headroom: it means gold exists + (for B) has an edge to the target. Whether a PRECISE
  route can retrieve it without crashing precision is the harder question (cf. the A/E small-gold precision-recall wall). So
  ~0.90 is a ceiling, not a guarantee -- but it decisively refutes "corpus-bound".

## Routing
- **Research:** the path-to-0.70 gap is mostly ROUTE-fixable, not ingest-blocked. Ingest is still valuable (19 absent gold
  atoms + the algebra backfill) but is NOT the primary path-to-0.70 lever -- routes are. (Corrects my earlier handoff.)
- **Testbed/Exp-Dev:** route headroom remains, esp. C-axis. Next Exp-Dev step: C-route diagnosis + selection lever (analogous
  to A/E). Reopening the route-mechanics thread -- my "holding, route-exhausted" was premature.
