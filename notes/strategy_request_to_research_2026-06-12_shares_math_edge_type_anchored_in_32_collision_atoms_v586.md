# strategy_request: Research SHARES_MATH edge-type design drill anchored in 32-atom collision list (PP-408 follow-on; refines v585 SHARES_MATH design routing)

**From:** verdict_handler (cap_map v586 cycle 248)
**To:** Research session (pick on own cadence per 4-session architecture)
**Date:** 2026-06-12
**Anchor:** PP-408 substrate_codebook_near_duplicate_diagnostic_cpu_v1 HARD_PASS

## Context

USER SHARES_MATH architectural insight (memory note 2026-06-12) hypothesized that "capabilities at T2/T3 may share IDENTICAL underlying math; encoder couldn't distinguish them because their math IS the same." v585 strategic-design cycle filed a Research SHARES_MATH design drill (independent of UNION-B/C ship).

PP-408 v586 EMPIRICALLY INSTANTIATES SHARES_MATH at concrete atom-pair granularity: 49 pairs at cos>=0.99 (essentially exact) are concrete shares-math instances. The encoder couldn't distinguish them because (a) the math IS identical at `algebra_category` level AND (b) the `signature` + `complexity` fields are 0-populated.

This routing REFINES the v585 SHARES_MATH design drill with a concrete empirical anchor: the design must produce schema that DISTINGUISHES the 32 specific collision atoms enumerated in PP-408 metrics.

## The 32-atom collision list (empirical SHARES_MATH instances)

Key shares-math classes (from PP-408 `top_colliding_pairs`):

1. **Same algebra_category, distinct concepts:**
   - math::T1/probability_space <-> math::T1/measure_space (both measure-theoretic, distinct abstractions)
   - math::T1/matrix <-> math::T1/matrix_norms (object vs operator on object)

2. **Cross-tier SHARES_MATH:**
   - math::T1/cauchy_sequence <-> math::T3/euclidean_distance (metric-induced sequence convergence shares math with metric distance; T1-T3 spans tiers)

3. **Same role-class, different role-position:**
   - concept::MWP/ROLE_ARG0_agent <-> ROLE_ARG1_theme <-> ROLE_ARG2_recipient (all 3 mutually cos=1.0; semantic-role atoms differ only in role-position-index)

These three classes likely require DIFFERENT distinguishing field schemas:
- Class 1 (same-tier same-category): structural-sub-type signature (e.g., "object" vs "operator-norm").
- Class 2 (cross-tier shares-math): tier-level signature OR explicit SHARES_MATH edge that LINKS the atoms without encoder-confusion (different from disambiguating them).
- Class 3 (role-position differentiation): role-position scalar embedded as bound filler.

## Research drill request

### Drill 1: SHARES_MATH edge-type formal design

Design the SHARES_MATH edge-type for the substrate's typed-edge schema:
- Source/target atom typing (which atom-pairs CAN have SHARES_MATH edges?).
- Edge weight/direction semantics (symmetric? weighted by math-similarity?).
- Encoder integration: does SHARES_MATH LIVE OUTSIDE the algebra-HRR vector (graph-level edge for downstream operations) or INSIDE (bound into the vector to preserve algebraic operations)?
- Backward-compatibility with existing typed edges (DEPENDS_ON, SERVES_CAPABILITY, etc.).

### Drill 2: signature/complexity schema co-design

Co-design the per-atom signature/complexity schema such that:
- The 32 collision atoms become distinguishable post-population (validation set).
- Genuinely-shared-math atoms remain LINKED via SHARES_MATH edges (preserves USER's architectural insight at edge level not encoder level).
- Schema generalizes beyond the 32 specific atoms (apply to full 280-atom corpus; predict where additional collisions exist).

### Drill 3: relationship between SHARES_MATH edges and free-probability spike eigenvalues

Free-probability drill (in flight) predicts BBP-supercritical structured-Wishart regime where shared-class atoms produce spike eigenvalues in the Gram matrix. PP-408 supplies 49 cos>0.99 pairs as the spike-eigenvalue signature. Drill question: is SHARES_MATH edge-presence EQUIVALENT to spike-eigenvalue cluster membership? If yes, SHARES_MATH edges can be auto-derived from Gram spectral analysis.

## Pre-reg HP gate

- Drill 1 + Drill 2 produce a CONCRETE schema (atoms, edges, encoder integration) that PASSes a smoke test: schema applied to the 32 enumerated collision atoms produces post-population cleanup F1 prediction matching PP-408 dedup-upper-bound (1.0000 +/- 0.05) on the colliding subset.
- Drill 3 produces a theoretical link OR explicit refutation between SHARES_MATH edges and free-prob spike eigenvalues.

## Cross-references

- cap_map v586 PP-408 entry (this verdict).
- USER SHARES_MATH memory note 2026-06-12.
- v585 strategic-design routing (this routing refines with empirical anchor).
- v584 CSLS HARD_FAIL (encoding-not-rerank framing).
- v582 PP-406/PP-407 (clustered-codebook positioning).
- Free-probability drill (in flight; theoretical pairing).

Status: routing written to disk; NOT auto-dispatched; Research picks on own cadence.
