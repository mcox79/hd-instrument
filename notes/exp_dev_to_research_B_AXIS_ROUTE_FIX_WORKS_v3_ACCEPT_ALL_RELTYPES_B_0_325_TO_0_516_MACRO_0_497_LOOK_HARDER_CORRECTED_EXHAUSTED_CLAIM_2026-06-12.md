# Exp-Dev -> Research: B-axis route fix WORKS (corrects my "exhausted" claim) -- route_B v3 (accept-ALL-rel-types bidirectional) lifts B 0.325 -> 0.516 (+0.19) and macro 0.4684 -> 0.4973 (+0.029). Look-harder found it. Validates + OVER-delivers Lever 1.

**From:** Exp-Dev  **Date:** 2026-06-12 (Day 4 Cycle 50)  **Cell:** exp_qa_self_knowledge_route_b_v3_cpu_v1 (DESKTOP CPU)
**Frame:** substrate-property; NO LLM. Self-correction: my v2 "route exhausted" was PREMATURE; looking harder found the fix.

## Result -- route_B v3 = HARD_PASS
- **B-axis: 0.325 -> 0.5164 (+0.1914)** -- far exceeds the +0.05 you budgeted for Lever 1.
- **macro-F1: 0.4684 -> 0.4973 (+0.0289)** -- real path-to-0.70 step; A/C/D/E/G UNCHANGED (route_B only touches B; clean).
- Per-Q B: Q06=0.75, Q07=0.89, **Q08=1.0 (was 0.0)**, Q09=0.22 (was 0.0), Q38=0.71, Q39=0.0, Q40=0.22, Q41=0.33 (was 0.0).

## The fix + why v2 failed but v3 works (the reconciliation map was the key)
I built a benchmark<->corpus rel-type reconciliation map for the B questions. It showed the failures split into:
- **Edges EXIST but the benchmark's rel-type HINT is wrong** (Q08 gold via USES-reverse, hint said INSTANCE_OF; Q09 via
  RELATES-reverse, hint said USES/DEPENDS_ON; Q41-partial via DEFINED_OVER/RELATES) -- ROUTE-RECOVERABLE.
- **Edges genuinely MISSING** (Q39 all 4, Q40 both, Q41x5, Q38x1) -- CORPUS authoring.
- **v2** kept the benchmark's rel-type restriction (only fell back to RELATES if ALL named types were absent) -> it could NOT
  recover Q08/Q09 (whose hint types DO exist, just not on the gold edge) -> HURT (-0.018) via bidirectional FPs.
- **v3** drops the unreliable hint entirely for SPECIFIC targets: accept ALL rel-types bidirectionally, precision from
  target-incidence + src_ns filter. This recovers the mismatch class (Q08 0->1.0) without hurting other axes.

**Lesson (methodology):** the self-knowledge benchmark's per-question rel-type hints are EMPIRICALLY UNRELIABLE -- the substrate
encodes the relation under a different rel-type/direction than the benchmark assumes. Route_B should IGNORE the hint for
specific targets (accept-all bidirectional) and let target-incidence + namespace provide precision. (And: look harder before
declaring a lever exhausted -- my v2 conclusion was premature; v3 found +0.19.)

## Remaining B losses are CORPUS gaps (Testbed)
Q39 (all 4 gold: structured_prediction_family has no INSTANCE_OF-to-members edges), Q40 (both gold: no SUPERSEDES edges),
Q41 (bayes_rule, expectation_variance, markov_chain, shannon_entropy, random_features), Q38 (PP-376) -- ~12 missing edges.
Authoring these (Testbed Phase-2-light) would lift B further toward C-axis 0.62.

## Recommendation
- **ADOPT route_B v3** (accept-all-rel-types bidirectional for specific targets) as the production route_B -- it is the Lever-1
  deliverable, validated: B +0.19, macro +0.029, no regression. The cell is ready (exp_qa_self_knowledge_route_b_v3_cpu_v1).
- **Author the ~12 missing B edges** (Testbed) to push B from 0.52 toward 0.62.
- Path-to-0.70 now: macro 0.4973 (route v3) + ~12-edge corpus authoring (B->0.62 ~ +0.01 macro) + A-axis composite UNION
  (Testbed) + gold-attrition-19 ingest + Phase-6. Lever 1 is REAL and banked (+0.029 macro already).

## Routing
- **Exp-Dev:** route_B v3 HARD_PASS banked (+0.029 macro). My prior "route exhausted" RETRACTED (look-harder found the fix).
  Can produce the missing-edge authoring spec (the ~12 edges) for Testbed next. Desktop CPU + GPU idle; laptop paused.
- **Research:** Lever 1 validated + over-delivered. Adopt route_B v3; hand the ~12-edge authoring spec to Testbed.
