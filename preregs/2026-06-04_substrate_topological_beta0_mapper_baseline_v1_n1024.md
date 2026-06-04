# Prereg: substrate_topological_beta0_mapper_baseline_v1_n1024

## Anchor
substrate_topological_beta0_mapper_baseline_v1_n1024

## Routing
notes/routing_convergent_brain_architecture_empirical_batch_2026-06-04.md (Research), Phase 1b. EXPLORATORY
(not load-bearing): baseline for topological memory-inspection capability.

## Scientific question
Can beta_0 (connected-components) connectivity curve + a Mapper graph on stored patterns detect a
kappa_2-INVARIANT drift event (random pattern swap) that the second moment misses, and produce non-trivial
Mapper structure? beta_0(tau) via union-find over cosine-sim thresholds; drift = 20% random swap; KS test
of clean-vs-drift beta_0 curves; Mapper = 1st-PCA filter + overlapping cover + single-linkage. 3 cells, 3 seeds.

## Pre-registered bands
HARD-PASS: beta_0 KS-detects drift (p<0.05) AND drift kappa_2-invariant (delta_kappa2<0.10) AND Mapper>=5 nodes.
MIDDLE: detects but delta_kappa2>=0.10 (kappa_2 also moved) OR Mapper 2-4 nodes.
HARD-FAIL: beta_0 insensitive (KS p>=0.05) OR Mapper collapses to 1 node.

## Formula self-tests (PROT-022)
1. union-find: chain->1 component, no edges->M. 2. KS(identical)=0. 3. kappa_2=Tr(W^2)/N>0. [ALL PASS]

## Smoke gate
Smoke PASSED (M=120/200, N=256, 2 seeds): self-test green; Mapper ~20-50 nodes; drift kappa_2-invariant
(delta=0.007). PREVIEW: beta_0 does NOT detect random swaps (ks_p=0.999) -> likely HARD_FAIL at full scale
too (random->random swaps are topologically invisible). Shipped as an honest exploratory baseline (not rigged).

## PROT-018 / 021
_n1024 -> N=1024. 3 seeds; partials keyed seed+run_mode+N.

## Queue
remote_cpu_queue (CPU; pure numpy). timeout 7200s.
