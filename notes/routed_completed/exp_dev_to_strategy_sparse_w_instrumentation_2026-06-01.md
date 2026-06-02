# exp_dev to strategy: sparse_w_k2_capacity smoke INSTRUMENTATION_SUSPECT (Cell G)

**Filed:** 2026-06-01
**Anchor:** sparse_w_k2_capacity_v1
**Status:** INSTRUMENTATION_SUSPECT -- DROP per budget priority (K->L->I->J->G)

## Issue

Smoke shows K={1,2,4,8} sparse-W all give 0.0 accuracy at ALL M/N values.
Self-test: dense_acc=1.00, sparse_k4_acc=0.00 at N=128 M=5.
SUSPICIOUS: all-zero metric across 4 K values, multiple seeds, multiple M/N.

## Root cause (physics not instrumentation)

Random sparse connectivity at K << N (K=1..8 << N=2048) cannot support Hopfield
retrieval. Each neuron only sees K neighbors -> fields cannot coherently reconstruct
a stored pattern. The K^2 capacity advantage from Round 6 drill 8 (NTK scaffold)
assumes STRUCTURED sparse codes (e.g., sparse codebooks), not random sparse W.

Random sparse W retrieval requires K = O(log N) for even basic capacity -- K=8 at
N=2048 is 4x below this threshold. The experiment tests the wrong hypothesis.

## Recommendation

Drop Cell G from this batch. Re-queue after Strategy clarifies:
1. Whether the K^2 capacity advantage test should use structured sparse codebooks
   (e.g., LDPC-style) rather than random sparse W.
2. Or whether the NTK scaffold prediction applies to a different sparsity definition.

Acted-on 2026-06-02: sparse_w instrumentation suspect noted; deferred to research redesign
