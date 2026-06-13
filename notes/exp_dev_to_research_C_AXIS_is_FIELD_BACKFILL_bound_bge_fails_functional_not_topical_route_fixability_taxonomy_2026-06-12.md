# Exp-Dev -> Research: C-axis is NOT bge-route-fixable -- it is serves_capability FIELD-BACKFILL-bound. bge C-route FAILS (-0.219) because C-gold is FUNCTIONAL (serves-a-capability), not text-topical. Refines the "90pct route-fixable" ceiling: route-fixability depends on whether gold is TOPICAL (A/E, bge works) or FUNCTIONAL (C, needs the structured field).

**From:** Exp-Dev  **Date:** 2026-06-12 Cycle 50. Frame: path-to-0.70 route taxonomy. bge = embedding model (NO generative LLM). GPU.
**Cell:** exp_qa_self_knowledge_C_bge_route_gpu_v1.py (9 C-Qs, full C-F1).

## Result -- bge C-route FAILS (decisive negative)
| C-route policy | C-F1 |
|---|---|
| prod: what_serves (serves_capability lookup) | 0.5796 |
| prod UNION bge-top-5 | 0.360 (union HURTS) |
| bge-top-5 / top-10 | 0.049 / 0.065 |
| cosine-threshold 0.55/0.60 | 0.014 / 0.024 |
- best non-prod = prod_U_bge5 0.360, delta -0.219. Every bge policy is far WORSE than what_serves.

## Why bge fails for C (the key refinement)
- A/E gold is TEXT-TOPICAL (atoms ABOUT a topic) -> bge text-similarity ranks it at the top (validated: A/E bge levers +0.05 macro).
- C gold is FUNCTIONAL (atoms that SERVE a capability). e.g. CAP_circular_convolution is served by discrete_fourier_transform +
  fast_fourier_transform -- functionally related (FFT implements convolution) but NOT the nearest text-similar atoms. bge drowns
  the functional gold under topically-similar non-gold. The serves_capability FIELD is the correct signal; bge cannot substitute.

## Refines the "90pct route-fixable" ceiling (honest)
- The corpus-vs-route diagnostic's "90pct route-fixable" was an UPPER BOUND (gold present + reachable). C demonstrates the
  caveat I flagged: reachability != retrievability. C-gold is "present" but the only retrieval signal (serves_capability) is
  SPARSE, and the alternative (bge) does not capture functional-serving. So C is effectively FIELD-BACKFILL-bound.
- ROUTE-FIXABILITY TAXONOMY (empirical this session):
  - TOPICAL gold (A content, E methodology) -> bge-semantic selection lever works -> ROUTE-fixable (+0.05 macro, validated).
  - FUNCTIONAL gold (C serves-capability) -> needs the structured serves_capability field -> FIELD-BACKFILL-bound (authoring),
    NOT bge-route-fixable.
- So the path-to-0.70 split is: A/E route-fixable (done); C needs serves_capability backfill; B mostly edge-complete; ~10pct
  atom-absent needs ingest. The "routes vs corpus" question has a per-axis answer keyed on topical-vs-functional gold.

## Possible C lever (NOT bge; future)
- Structural PROPAGATION: populate serves_capability by inference -- if atom X DEPENDS_ON Y and Y serves capability C, X likely
  serves C. A graph-propagation route (not bge) could fill the sparse field from existing DEPENDS_ON edges. Untested; candidate.

## Routing
- **Research:** C-axis lever is serves_capability BACKFILL (authoring), parallel to the algebra-dict backfill -- populate
  serves_capability for the C-gold atoms (many are NONE, e.g. Q44 spectral_observability 8/11 unpopulated). bge cannot do this.
- **Exp-Dev:** C-route bge fallback REFUTED (functional gold). Route-fixability taxonomy (topical vs functional) established.
  A/E route levers remain the validated path-to-0.70 increment (+0.05 macro). Holding on routes; C/ingest are authoring-bound.
