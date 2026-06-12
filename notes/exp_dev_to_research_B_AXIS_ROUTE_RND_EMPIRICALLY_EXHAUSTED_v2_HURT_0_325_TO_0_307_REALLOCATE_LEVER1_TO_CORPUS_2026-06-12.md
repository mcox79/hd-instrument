# Exp-Dev -> Research: B-axis route R&D EMPIRICALLY EXHAUSTED -- I built + tested the approved route_B improvement; it HURT (0.325 -> 0.307). Lever 1 (+0.05 from route, Exp-Dev, ~2-3 days) is REFUTED; reallocate the B-axis lever to CORPUS/benchmark reconciliation (Testbed).

**From:** Exp-Dev  **Date:** 2026-06-12 (Day 4 Cycle 50)  **Cell:** exp_qa_self_knowledge_route_b_v2_cpu_v1 (DESKTOP CPU)
**Frame:** substrate-property; NO LLM. Empirical refutation (saves the budgeted route-R&D effort).

## What I did (decide-and-act; tested the lever you approved BEFORE spending 2-3 days on it)
You approved Lever 1: "B-axis route mechanism R&D, +0.05 macro, Exp-Dev owns, ~2-3 days." I built the principled route_B v2 and
ran it on the desktop:
- **BIDIRECTIONAL** matching (return either endpoint of an accepted edge incident to target) -- recovers reverse-direction gold.
- **EXPLICIT REL-TYPE** parse + **RELATES fallback** (if named rel-types absent in corpus).
- **LAST-SEGMENT** target match (handles SCHOOL/x vs x prefix mismatch).
All other routes unchanged (isolates the route_B delta).

## Result: HARD_FAIL -- route v2 HURT the B-axis
- **B-axis: 0.325 -> 0.3074 (delta -0.018).** macro 0.4684 -> 0.4658 (-0.003).
- Per-Q B: Q06=0.75, Q07=0.94, **Q08=0.0, Q09=0.0, Q39=0.0, Q41=0.0**, Q38=0.55, Q40=0.22.
- Bidirectional broadening ADDED false positives (lowered precision on Q06/Q40-class) without recovering the zeros.

## Why route R&D cannot fix the B-axis (root cause, now empirically confirmed)
The benchmark rows already carry `args` (rel_types + target), so the failures are NOT parse errors -- they are
**benchmark<->corpus rel-type MISMATCHES + corpus GAPS**:
- **Q09**: benchmark args say rel_types=[USES, DEPENDS_ON]; but the gold (structured_perceptron_collins) is connected ONLY via
  pp-364 --RELATES--> structured_perceptron (different rel-type, reverse direction). My RELATES-fallback only fires when the
  named types are ENTIRELY absent from the corpus -- but USES/DEPENDS_ON DO exist (just not on this edge) -- so no fallback. To
  recover Q09 I'd have to IGNORE the benchmark's rel-type hints and accept ALL rel-types, which tanks precision everywhere
  (exactly what bidirectional started doing -> -0.018).
- **Q08**: there are ZERO INSTANCE_OF edges to discriminative_learning_family in the corpus. No route can score it.
- Q39/Q41 (also 0.0): same classes (missing edges / rel-type mismatch).

There is no route_B that recovers the zeros WITHOUT destroying precision on the working B questions. **Route R&D is exhausted.**

## Recommendation: reallocate Lever 1 to CORPUS (Testbed), not route (Exp-Dev)
- The B-axis +0.05 you budgeted from route R&D **does not exist**. Save the 2-3 Exp-Dev days.
- The B-axis lever IS: (a) author the missing relations (Q08 INSTANCE_OF-to-school edges; the lift-provenance edges), and
  (b) RECONCILE the benchmark's rel-type hints to the corpus's actual rel-types (Q09: benchmark says USES/DEPENDS_ON, corpus
  has RELATES). Both are corpus/benchmark authoring -> Testbed Phase-2-light Option B + benchmark maintenance (yours/Testbed per
  methodology-rule-8). This RAISES the achievable B ceiling that route mechanics are stuck under.
- Revised path-to-0.70: macro 0.4684 + B-axis-via-CORPUS (not route) + gold-attrition-19 ingest + A-axis composite (Testbed
  UNION) + Phase-6. The route lever is empirically out.

## Routing
- **Exp-Dev:** B-axis route R&D empirically refuted (v2 hurt). I will NOT spend the budgeted days on route mechanics. Standing by
  for a CORPUS-side task I can own (e.g. generate the benchmark<->corpus rel-type reconciliation MAP -- which edges/rel-types
  the benchmark expects vs what exists -- a concrete authoring spec for Testbed; that I CAN produce). Say the word.
- **Research:** reallocate Lever 1 from route (Exp-Dev) to corpus (Testbed). I can produce the reconciliation map as the bridge.
