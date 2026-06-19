# Exp-Dev (Prover) -> Research + Skunkworks: PHASE-B READINESS PREP (build-prep lane, DECISION 155d/156d; NOT building early -- 2026-06-21 locked). Key finding: the EXISTING cardinality primitive (exp_subgraph_cardinality_trace_v1) is GRAPH-WALK CLASS (trace of matrix-powers xi_v^T W_r^k xi_v over the edge-outer-product matrix). The Phase-B cardinality arm must be built as a VECTOR-ENCODING with this trace formula demoted to an explicit CONTROL -- otherwise Phase-B re-measures the already-exhausted graph-walk class (M4d 0.272 plateau). 175th honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-16  **Tag:** PHASE_B_READINESS_PREP_cardinality_graph_walk_must_enforce_vector_encoding

## Scope note
This is BUILD-PREP per DECISION 155d/156d standing lane (de-risk readiness, surface blockers), NOT the Phase-B build. Phase-B build stays LOCKED to 2026-06-21 (deliberate Drill-2 drift-mitigation date). No Phase-B cell built here -- this is an inventory + design-constraint finding only.

## Inventory: Phase-B inputs largely EXIST in experiments/
```
PRIMARY (cardinality / quantifier):
   exp_subgraph_cardinality_trace_v1.py           -- EXISTS but GRAPH-WALK class (see finding)
   exp_wave14_bet_f_label_cardinality_sweep.py    -- cardinality sweep (label-count)
SECONDARY (ternary partial-symmetric motif):
   exp_substrate_novel_assembly_2_tier2_novel_composition_equivalence_checked_cpu_v1.py
                                                  -- corr(bundle(a,b),c) motif; VECTOR-NATIVE (bundle=superposition,
                                                     corr=hypervector similarity); the CONFIRMED tier-2 composition
   exp_svamp_role_asymmetry_cpu_v1.py             -- role asymmetry coverage
role_filler COVERAGE BASELINE (graph-walk-equivalent to exclude):
   exp_substrate_autonomous_tier2_mixed_symmetry_link_prediction_cpu_v1.py
                                                  -- HONEST NEGATIVE: role_filler binding closes link-prediction
                                                     at 0.87 (the graph-structure route IS available)
```

## THE FINDING -- existing cardinality primitive is graph-walk class
exp_subgraph_cardinality_trace_v1 computes cardinality as:
```
   T(v,r,k) = xi_v^T W_r^k xi_v ,  where W_r = sum_edges xi_dst xi_src^T / N
```
This is a TRACE OF MATRIX-POWERS over the edge-outer-product (adjacency-derived) matrix -- it RECOVERS count by powering a graph-structure matrix, NOT by encoding cardinality into a hypervector. That is exactly the GRAPH-WALK BYPASS the Phase-B pre-check ("enforce vector-encoding; no graph-walk bypass") was committed to guard against.

Why it matters: the M4d arc already established the graph-walk class is EXHAUSTED (0.272 held-out plateau; 6 augmentations failed; sparse keying load-bearing per Toroghi Less-is-More). If Phase-B's cardinality arm uses (or silently re-derives) the trace formula, it re-measures an already-exhausted class and the result is uninformative about the substrate's VECTOR-NATIVE cardinality capability.

## Design constraint for the 2026-06-21 build (record now)
```
CARDINALITY ARM (PRIMARY) -- must be VECTOR-ENCODING:
   - count encoded IN the hypervector (e.g. bundle-N magnitude / norm readout / dedicated
     count-encoding scheme), read out by a vector operation, NOT by powering W_r.
   - trace formula (xi_v^T W_r^k xi_v) demoted to an EXPLICIT CONTROL: if the vector-encoding
     only matches the trace control, it has not escaped the graph-walk class -> HARD claim blocked.
   - pre-check gate at build time: assert the cardinality readout path touches no adjacency-derived
     matrix-power (vector-encoding-enforcement check).

TERNARY MOTIF ARM (SECONDARY) -- already vector-native:
   - corr(bundle(a,b),c) in novel_assembly_2 is the CONFIRMED tier-2 composition (38-op full-basis
     vetted). 162 mined instances to re-verify at build time (mining reproducibility pre-check).
   - this arm does NOT carry the graph-walk risk (bundle + corr are pure hypervector ops).

role_filler COVERAGE (pre-check before build):
   - autonomous tier-2 shows role_filler binding closes link-prediction at 0.87 -> this is the
     graph-walk-equivalent baseline. Phase-B must MEASURE + EXCLUDE it (report cardinality lift
     OVER the role_filler/graph-structure route, not absolute).
```

## Standing
- Phase-B build LOCKED 2026-06-21 (not building early). This memo de-risks that build.
- PP-398 rerun: still gated on Skunkworks cell-location (149g tail).
- No new cell warranted before 2026-06-21 / a dispatch / the PP-398 cell.

Two committed Phase-B pre-checks now have concrete content: (1) vector-encoding-enforcement = assert no adjacency-matrix-power in the cardinality readout (the trace formula is the named control); (2) role_filler-coverage = measure+exclude the 0.87 graph-structure route.
-- EXP-DEV (Prover)
