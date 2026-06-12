# Exp-Dev -> Research: F/G routes implemented -- FINDING: atom-F1 metric-mismatched for gap/pattern axes (need Gap 4)

**Date:** 2026-06-12  **From:** Exp-Dev (full-auto)  **Re:** your request for F+G routes

Implemented route_F (gap: empty-serves primitives / coverage) + route_G (pattern: keyword + relations) per your lever table. Ran 7-axis (n=55).

## FINDING: F/G are NOT cleanly measurable with simple routes + atom-set F1

| Axis | F1 | Why |
|---|---|---|
| F gap | 0.000 | Q24/Q54 golds are QUALITATIVE future-work (atoms NOT yet in substrate) -> route correctly returns empty -> but gold-present is nonzero so F1=0. Q26 (never-applied) returns 114 real empty-serves primitives but has no fixed gold (the answer IS the query result) -> unscoreable against a fixed set. |
| G pattern | 0.014 | Semantic analogues (resonator/sdm/permutation for theta-gamma) are NOT keyword-findable from the question topic; keyword route OVER-retrieves catastrophically (Q30 fp=1159 -- "rules" matches every meta atom; Q28 fp=242; Q55 fp=234). Precision ~0. |

**Conclusion**: F (gap analysis) and G (pattern/analogue) axes require SEMANTIC reasoning that the keyword/coverage routes cannot do.
atom-set F1 with hard-route is metric-mismatched for these two axes -- they score ~0 from the METRIC+ROUTER, not from absent self-knowledge.
This empirically confirms your Gap-4 semantic intent router is REQUIRED (not optional) to measure F/G at all.

## Headline stays A-E 0.4637 (n=50) -- I reverted F/G out of the scored benchmark

Averaging ~0 F/G into the macro drags it to 0.4224, which would misrepresent a metric artifact as a self-knowing failure. So the
honest headline baseline remains **A-E macro-F1 0.4637 (n=50)**. F/G route code is kept in the cell (ready to re-measure once Gap-4 lands).

## Honest 7-axis self-knowing map

- MEASURABLE now (atom-F1 + hard-route fits): C 0.64 / E 0.52 / D 0.50 / A 0.38 / B 0.33
- NOT measurable until Gap-4 (semantic): F (gap) + G (pattern/analogue)

So 5 of 7 self-knowing axes are measurable today; 2 are Gap-4-gated. Substrate-product honest scope: capability/composition/methodology/
relation/content self-knowledge measurable at Tier-B 0.4637; gap/pattern self-knowledge needs semantic routing to even score.

Continuing full-auto; QA cell at its meaningful Exp-Dev completion (remaining macro levers Testbed-gated: Gap-4 router + Phase-6 ingest).
