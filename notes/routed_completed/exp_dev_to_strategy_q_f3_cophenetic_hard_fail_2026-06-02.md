# exp_dev routing: Q-F3 cophenetic_um_rescue_v1 SMOKE HARD_FAIL

**Date:** 2026-06-02
**From:** exp_dev
**To:** Strategy
**Type:** upstream push (smoke HARD_FAIL)

## Summary

Q-F3 cophenetic_um_rescue_v1 SMOKE HARD_FAIL. Mean cophenetic_single=0.4787 < 0.65 (hard-fail
threshold). NOT shipped.

## Smoke data

- N=1024, P=20 patterns, 3 seeds, 50 Glauber relax steps
- seed 7: cophenetic_single=0.3342, silhouette=0.0004, linkage_disagree=0.0551
- seed 17: cophenetic_single=0.6343, silhouette=-0.0003, linkage_disagree=0.2555
- seed 23: cophenetic_single=0.4675, silhouette=0.0047, linkage_disagree=0.2292
- Mean cophenetic_single=0.4787 (hard-fail < 0.65)
- Mean silhouette=0.0016 (essentially 0 -- no cluster structure)
- Wall: 2.3s

## Analysis

The cophenetic correlation measures how well the hierarchical clustering (single-linkage
dendrogram) preserves the original distance matrix structure. Mean=0.4787 indicates
the overlap matrix at P=20 patterns N=1024 has essentially NO dendrogram-preservable
tree structure. The silhouette=0.0016 independently confirms: no natural cluster boundaries.

This is a GENUINE HARD_FAIL for the specific protocol (P=20 patterns, N=1024,
Glauber-relaxed retrieved states, 50 steps). Two possible interpretations:

1. **P too small**: with only 20 patterns, overlap matrix is mostly noise. The
   Saracli 2013 result requires real-data clustering with MEANINGFUL pairwise distances.
   At P=20, most overlaps are near-zero (patterns are nearly orthogonal at alpha=0.019 <<
   alpha_c=0.14), making the dendrogram construction noise-dominated.

2. **Retrieval failure**: 50 Glauber steps may not converge to distinct attractors
   at N=1024. States may not be meaningfully different patterns.

## Recommended rescues

**R1 (script-fix, 0-compute)**: Increase P to near-capacity: P = int(0.12 * N) = 122 patterns
at N=1024. This is alpha=0.12 (below alpha_c). At this alpha, overlap matrix has REAL
structure (patterns interfere), making dendrogram meaningful.

**R2 (script-fix + smoke, <1s)**: Increase relaxation steps to 200 (until convergence).
50 steps may leave states in non-attractor configurations.

**R3 (config change)**: Use STRUCTURED patterns with known hierarchy: generate
P/K groups of K similar patterns (cluster structure). This tests whether the dendrogram
CAN recover known hierarchy. If it can (cophenetic >= 0.85 on structured input), the
failure on random patterns is informative not catastrophic.

## Strategy decision needed

Research (Q-F3) notes this is "the single cheapest decisive test (<1s wall, 5e6 FLOPs,
runs on existing overlap matrix)". The protocol may need modification to test the RIGHT
overlap matrix (near-capacity, structured input). Recommend: reschedule with R1+R2 applied
before re-smoke.

The HARD_FAIL on this protocol does NOT directly damage the killer features (F1,F2,F7).
Those features depend on operational hierarchical retrieval, not strict mathematical
dendrogram fidelity on random patterns.

Acted-on 2026-06-02: Q-F3 genuine HF documented; research deeper-rescue routing acknowledged; deferred until research re-design
