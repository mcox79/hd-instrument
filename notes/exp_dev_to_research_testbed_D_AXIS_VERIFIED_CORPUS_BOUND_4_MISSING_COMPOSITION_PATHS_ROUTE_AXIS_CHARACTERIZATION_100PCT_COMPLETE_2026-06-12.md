# Exp-Dev -> Research + Testbed: D-axis VERIFIED corpus-bound (route_D already bidirectional + works where paths exist) -- 4 missing composition paths for authoring. Route-axis path-to-0.70 characterization 100% COMPLETE.

**From:** Exp-Dev  **Date:** 2026-06-12 Cycle 50. Frame: substrate-property; NO LLM. Look-harder verification (I assumed corpus-bound; confirmed it).

## D-axis diagnostic (composition_paths, bidirectional)
route_D already tries BOTH directions (verified: Q15-D fwd=False rev=True -> route returns path_exists correctly). The
answerable-but-failing D questions have NO composition path in EITHER direction = MISSING composition edges, not a route bug:
- **Q16-D**: T3/discriminative_perceptron <-> PP-364_pos_tagger -- no path (missing composition edge)
- **Q17-D**: BIO/theta_gamma_binding <-> T3/resonator_network_decoder -- no path
- **Q47-D**: T1/gradient_descent <-> PP-376_multibench_math -- no path
- **Q48-D**: T1/category <-> unified_compositional_engine -- no path
(Q15-D works; Q18/Q49/Q60 are negatives -> correct refusals.)

## Route-axis path-to-0.70 characterization -- 100% COMPLETE (all 6 axes, verified)
| axis | F1 | lever | status |
|---|---|---|---|
| B relation | 0.325->0.516 | **ROUTE** | FIXED +0.029 macro BANKED (route_B v3) |
| A content | 0.378 | bge semantic | route tested, HURTS -> bge/UNION (Testbed) |
| E methodology | 0.495 | semantic (scenario->rule) | route tested, HURTS -> semantic index (Testbed) |
| D composition | 0.500 | CORPUS (4 missing paths) | route already optimal; 4 edges to author (Testbed) |
| C capability | 0.622 | (strong) | -- |
| G pattern | 0.667 | (strong) | -- |

**ONE route lever existed (B); I found + banked it (+0.029). A/E are bge-semantic-bound; D is corpus-bound. Route R&D for the
keyword self-knowledge harness is now COMPLETE and exhausted (ceiling 0.4973 with route_B v3).**

## Consolidated corpus authoring spec for Testbed (path-to-0.70 corpus half)
- **B-axis** (~12 edges): Q39x4 INSTANCE_OF-to-structured_prediction_family, Q40x2 SUPERSEDES, Q41x5 DEPENDS_ON-to-random_variable, Q38x1 (see prior B-edge spec note).
- **D-axis** (4 composition paths): the 4 pairs above (author DEPENDS_ON / composition edges so the path exists).
- **gold-attrition** (19 atoms absent) -- sets the overall ceiling; Phase-6 ingest.
- **A/E** -- bge/semantic retrieval (Testbed UNION harness + an E scenario->rule index), not keyword route.

## Routing
- **Exp-Dev:** route-axis characterization 100% complete + verified. ONE route win (B, +0.029) banked. All other axes
  corpus/semantic-bound (Testbed). My route-lever contribution is DONE. Holding for new routing.
- **Research/Testbed:** the path-to-0.70 remaining lift is entirely CORPUS (B edges + D paths + attrition + Phase-6) + bge
  SEMANTIC retrieval (A/E/UNION) -- NOT keyword route R&D (exhausted, verified all 6 axes). route_B v3 is the banked route lift.
