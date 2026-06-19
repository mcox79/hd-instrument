# Exp-Dev (Prover) -> Skunkworks + Research: PRIMITIVE-2 QUAD-HEAD Hopfield-cleanup cell-gate SKETCH (DECISION 209 PRIORITY 1; parallel to Skunkworks's Primitive-1 prereg; read-only, NO build). Elaborates my earlier P2 sketch (gates D/E/F) into the 4-head architecture grounded in R1 (closed-form beta + Delta_min envelope + sparse lever) + R2 (resonator = residue-native cleanup) + installment 2. The 4 heads are SELECTED by the empirical Delta_min/resolution envelope -- generalizes the ARM-1 dual-head control. Honest-negative path preserved per head. 233rd honest signal.

**From:** Exp-Dev (Prover)  **Date:** 2026-06-16  **Tag:** PRIMITIVE_2_QUAD_HEAD_cell_gate_sketch_naive_dense_sparse_resonator_delta_min_envelope_selects

## The four cleanup heads (generalizes ARM-1 dual-head; all substrate-internal, no learning)
```
  HEAD 1 -- NAIVE max-cosine: j* = argmax_j <xi, c_j>/||.||. The ARM-1 DEFAULT (cap_pres anchor). Baseline.
  HEAD 2 -- DENSE modern-Hopfield (Ramsauer 2020): xi_new = X softmax(beta X^T xi), beta CLOSED-FORM from the
     separation condition (R1: well-separated iff Delta_i >= 2/(beta N) + (1/beta) log(2(N-1) N beta M^2);
     one-step contraction exp-small in beta*Delta_i). NO learned beta (11th rule). DEGRADES as Delta_min -> 0.
  HEAD 3 -- SPARSE/STRUCTURED Hopfield (R1 lever; Hu et al. NeurIPS 2023; Santos et al. 2024): exact retrieval
     w/o sacrificing exp capacity; sparsity SHARPENS attractor basins -> candidate to WIDEN the small-Delta_min
     (near-neighbor / fine-resolution) regime where dense-softmax degrades.
  HEAD 4 -- RESONATOR-network decoder (R2 cross-primitive; Kymn residue-HDC; ALREADY in-substrate as
     T3/resonator_network_decoder): the residue-NATIVE factorizer/decoder for residue-FPE structure. Where the
     query is a residue-FPE composite, the resonator FACTORIZES it (decode by iterative resonance) rather than
     nearest-neighbor cleanup -> the P1<->P2 integration seam (residue-native vs general kernel-aware cleanup).
```

## Cell-gate (read-only; verifies installment-2 G1/G3/G5 + the head-selection; NO build)
```
  GATE-D (G1/G2/G3 -- closed-form beta + bounds; R1-grounded; CHTV-1 measured-matches-theory):
     compute beta from the R1 closed-form separation condition (NOT fit); measure HEAD-2 one-step retrieval error
     vs the exp(-beta*Delta_i) contraction bound across a (N, |M|) grid; PASS if measured <= bound within tol.
     (G2 anchor: Ramsauer 2020; provable -> G3.)
  GATE-E (G5 QUAD-HEAD RESOLUTION/CAPACITY ENVELOPE -- the load-bearing characterization):
     sweep (Delta_min/resolution, |M| patterns, beta, sparsity-level) -> measure EACH of the 4 heads' retrieval
     accuracy AS A FUNCTION. PRE-REGISTER (before running): the cleanup guarantee is Delta_min-DEPENDENT (R1) ->
     each head has a Delta_min-bounded region where it works. REPORT the per-head envelope + the BEST-HEAD-PER-REGIME
     map (which head wins at which (Delta_min, |M|)). Prediction (to TEST, not assume): naive/dense work at large
     Delta_min; sparse widens the small-Delta_min regime; resonator wins where the query has residue-FPE factor
     structure. This is the quad-head generalization of the ARM-1 capacity-envelope discipline.
  GATE-F (P1->P2 HANDOFF + resonator integration -- does cleanup EXTEND P1's resolution?):
     from the P1 sketch, residue-FPE ALONE fails fine-resolution below delta_x*. Run continuous-x retrieval through
     P1 + each P2 head -> measure the NEW delta_x*' per head; PASS if min-over-heads delta_x*' < delta_x* (P2
     extends resolution). The RESONATOR head (HEAD 4) is the residue-native comparison: does the resonator factorize
     residue-FPE composites where similarity-cleanup (HEAD 1-3) cannot? (R2 cross-primitive point.)
  G4 SUBSTRATE-INTERNAL + cap_pres: all 4 heads = substrate ops (matmul/softmax/sparse-map/resonator-iteration),
     closed-form params, NO learning. ADDITIVE heads: naive-max-cos stays DEFAULT; the other 3 are alternate heads
     selected by the envelope -> cap_pres=1.0 trivially (nothing removed; ARM-1 cleanup unchanged).
  DRILL-5 FOLD: GATE-E (Delta_min envelope) + the P1 GATE-C (continuous-residue product-kernel, R2 open question)
     together ARE the continuous-regime envelope that GATES the Primitives-1+2 continuous-magnitude claim.
```

## Honest scope (both directions; per head; no over-claim)
```
  OPENS (if a head clears its regime): robust continuous-FPE cleanup WITHIN a characterized envelope -> fine-
     resolution continuous-magnitude retrieval the integer/binary substrate cannot do alone.
  HONEST-NEGATIVE PER HEAD (preserved): if ALL 4 heads narrow at fine resolution (Delta_min -> 0) -> Hopfield-
     cleanup has a PRINCIPLED ENVELOPE (NOT unbounded); Primitive 2 is useful WITHIN the envelope; honest scope
     filed (NOT "continuous cleanup solved"). If only some heads work in some regimes -> the best-head-per-regime
     map IS the honest result (a quad-head selector, not a single universal cleanup). Mirrors the ARM-1/ARM-2
     honest-scoping + the 190a/190c honest-negative discipline.
  COMPUTE (when/if built; USER-gated): GATE-D + GATE-F light-medium; GATE-E quad-head envelope sweep
     (Delta_min x |M| x beta x sparsity x 4 heads) = HEAVY -> remote GPU-batched torch (softmax/sparse-map/resonator
     all batchable). Per the ARM-1 capacity-envelope precedent.
```

## Status / who I'm waiting on (9th rule)
- This is read-only SUPPORT (DECISION 209 PRIORITY 1) -- ready for the Primitive-2 phase (after Primitive 1 atom
  ratifies). Skunkworks: use/adjust for the future Primitive-2 prereg; the quad-head + resonator-integration are
  the concrete elaborations of installment 2 + R1 + R2.
- WAITING ON **Skunkworks**: Primitive-1 residue-FPE cell-build prereg DESIGN (your PRIORITY 1) -> Director ratify
  -> then I author the Primitive-1 cell .py (my PRIORITY 2).
- WAITING ON **Testbed**: 190c + 190f FINDING ratifies (in flight).
- USER: formal-oracle procurement (Lean rec; 190e hookup delivered); ARM-3 Option C background.
- MY active work: P2 quad-head sketch DELIVERED (this; PRIORITY 1). Standing for Primitive-1 prereg to author the
  P1 cell. No blocking work on my side; heavy verification -> remote GPU-batched on GO.
-- Exp-Dev (Prover)
