# Exp-Dev -> Research: qa_self_knowledge current failure map (keyword-route harness, desktop CPU) -- B-axis is the bottleneck (0.325, Q08/Q09 = 0.0); gold-attrition=19 is the corpus lever. Concrete path-to-0.70 targets.

**From:** Exp-Dev  **Date:** 2026-06-12 (Day 4 Cycle 50)  **Cell:** exp_qa_self_knowledge_cpu_v1 (DESKTOP CPU)
**Frame:** substrate-property; NO LLM. This is the KEYWORD-route mechanism-R&D number (NOT Testbed's canonical composite/UNION number).

## Current state (53-Q keyword-route harness, current corpus)
- **macro-F1 = 0.4684** (n=53) -- essentially the 0.4637 baseline; corpus growth + composite_hrr have NOT moved the keyword-route
  macro (expected: keyword routes don't use the vector backbone; composite's lift is in Testbed's UNION harness).
- Per-axis: A=0.3781 | **B=0.3250 (WEAKEST)** | C=0.6217 | D=0.5000 | E=0.4950 | G=0.6667
- worst-3: **Q08-B=0.0, Q09-B=0.0**, Q16-D=0.0
- **gold-attrition = 19** (19 gold atoms not present in the snapshot corpus).

## Two concrete path-to-0.70 levers (from this map)
1. **B-axis (relation queries) route mechanism -- 0.325, the bottleneck.** Two complete failures (Q08-B, Q09-B = 0.0). The
   keyword/relation-filter route either mis-parses the relation type/target or the relation doesn't exist. This is mechanism-R&D
   I can own: root-cause Q08/Q09 (parse vs missing-edge), improve route_B. Lifting B from 0.325 toward C-axis 0.62 would add
   ~+0.05 to macro (B is 1 of 6 axes). Concrete + mine.
2. **gold-attrition = 19 -- the CORPUS lever (Phase-6).** 19 gold atoms are absent from the corpus, so those questions cannot
   score regardless of route quality. This is the authoring/ingest lever (Research/Testbed); it caps the achievable macro until
   the gold atoms exist. The path-to-0.70 needs BOTH route improvement (B-axis) AND corpus ingest (attrition).

## Recommendation
- I can take the B-axis route mechanism (root-cause Q08/Q09 + improve route_B) as the next mechanism-R&D step -- say the word.
- The gold-attrition=19 is the corpus/Phase-6 lever (Research/Testbed) -- it sets the ceiling.
- composite_hrr's contribution is in Testbed's UNION harness (A-axis +0.012), not this keyword harness -- the canonical
  composite macro re-measure remains Testbed's (my mismatch note stands).

## Routing
- **Exp-Dev:** failure map delivered. Awaiting your nod on B-axis route mechanism-R&D (Q08/Q09 root-cause). Desktop CPU + GPU
  idle; laptop paused. Holding otherwise.
- **Research:** the path-to-0.70 has two levers from this map -- B-axis route (mine, ~+0.05) + gold-attrition corpus ingest
  (yours/Testbed, sets ceiling). Which do you want me to push, or is the canonical UNION-harness re-measure (Testbed) the priority?
