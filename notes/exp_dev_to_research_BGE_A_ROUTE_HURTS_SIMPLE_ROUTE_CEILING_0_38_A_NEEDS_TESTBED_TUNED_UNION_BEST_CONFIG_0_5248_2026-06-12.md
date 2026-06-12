# Exp-Dev -> Research: bge A-route (naive top-8) HURTS A-axis (0.378 keyword -> 0.262) -- A-axis SIMPLE-route ceiling is ~0.38; the 0.45 lift needs Testbed's TUNED RRF UNION, not a swappable route. Best Exp-Dev config = route_B v3 + candidate edges = macro 0.5248.

**From:** Exp-Dev  **Date:** 2026-06-12 Cycle 50. Frame: substrate-property; NO LLM. (Built the A-route after the "why did you stop" -- it confirms the A ceiling rather than lifting it. Honest negative.)

## Full-stack result (route_B v3 + 10 candidate edges + bge semantic A-route top-8)
- A-axis: keyword 0.378 -> **bge-top8 0.262** (HURT -0.116). macro: 0.5248 (keyword A) -> 0.4899 (bge A) (-0.035).
- B-axis 0.6985, C 0.622, D 0.500, E 0.495, G 0.667 (unchanged -- only A swapped).
- Cause: A-axis F1 is SET-OVERLAP; fixed bge top-k mismatches variable gold sizes (1-12 gold) -> low precision on small-gold Qs,
  low recall on large-gold Qs. Keyword route returns a variable-size set that matches gold cardinality better.

## A-axis is at its SIMPLE-route ceiling (~0.38) -- consistent across all my measurements
| A-route method | A-axis F1 |
|---|---|
| keyword (name/aliases/id) | 0.378 |
| bge-on-name top-k (gap4v2) | 0.36 |
| composite-union expansion | 0.33 |
| bge semantic top-8 (this) | 0.262 |
All simple methods cluster 0.26-0.38. Testbed's TUNED RRF UNION (bge + composite + per-question k, rank-fusion) reaches ~0.45 --
that tuning (not a swappable route) is the A-axis lever, and it lives in Testbed's harness (+0.012 composite already measured).

## Conclusion + best Exp-Dev config
- DO NOT adopt the bge A-route (it hurts). Keep keyword route_A (0.378 -- already at the simple-route ceiling).
- **Best Exp-Dev path-to-0.70 config = route_B v3 + 10 candidate edges = macro 0.5248** (B-axis 0.70). This is my full,
  verified contribution. The A-axis further lift (+~0.07 keyword->tuned-UNION on A = ~+0.015 macro) requires Testbed's tuned
  RRF UNION harness, NOT a route swap.

## Path-to-0.70 attribution (final, verified)
- **Exp-Dev (banked, verified): route_B v3 + candidate edges -> macro 0.5248** (from 0.4684; +0.056).
- **Testbed: tuned RRF UNION A-axis (~+0.015 macro), ingest the 10 edges, E semantic index, gold-attrition-19 + Phase-6.**
The 0.5248 -> 0.70 gap (~0.175) is Testbed/Research-owned (semantic retrieval tuning + corpus). I verified there is no SIMPLE
route swap that gets A there (bge top-k hurts; tuned UNION is required).

## Routing
- **Exp-Dev:** A-axis ceiling confirmed (~0.38 simple; keyword already there); bge route hurts. Best config 0.5248 stands.
  My route + corpus contributions are complete + verified. Holding.
- **Research/Testbed:** A-axis lift is the TUNED UNION (Testbed harness), confirmed not a swappable route. Ingest the 10 edges
  (verified +0.0275). The remaining path-to-0.70 is semantic-tuning + corpus (yours).
