# Prereg: substrate_drosophila_mb_sparse_single_modulator_v1_n4096

## Anchor
substrate_drosophila_mb_sparse_single_modulator_v1_n4096

## Routing
notes/routing_convergent_brain_architecture_empirical_batch_2026-06-04.md (Research), Phase 1a -- the
CHEAPEST DECISIVE TEST gating the Phase 2/3 convergent-architecture decision tree.

## Scientific question
Does the Drosophila MB template (sparse binary {0,1} coding f=0.05 + single cf-RPE modulator) beat the
current dense bipolar K=8 multi-channel substrate-as-training design at N=4096? 2 cells, 3 seeds, shared
char-LM scaffold + calibrated readout. Codes unit-normalized (preserves sparse support; well-scaled algebra).
Cell A: dense bipolar + cf-RPE + K=8 gate. Cell B: sparse f=0.05 + single cf-RPE (no gating).

## Pre-registered bands (NATS; gap = loss_A - loss_B)
HARD-PASS: gap_mean > 0.5 nats AND Cell B better on 3/3 seeds AND no instability (B norm osc < 3x).
MIDDLE: gap_mean in [0.1, 0.5] nats.
HARD-FAIL: gap_mean < 0.1 nats (sparse+single does not help).

## Formula self-tests (PROT-022)
1. sparse support = f*N nonzeros. 2. bipolar dense + unit-norm. 3. sparse heteroassoc recall cos>0.5.
4. cf-RPE shrinks error (1.000->0.000). 5. uniform nats = ln(V). [ALL PASS]

## Smoke gate
Smoke PASSED (N=256, 2 seeds): self-test green, both cells run, losses ~2.70 nats vs uniform 3.83.
Gap~0 at smoke is EXPECTED (N=256 -> only ~12 active sparse dims; sparse advantage needs full N=4096 ~205).

## PROT-018 / 019 / 021
_n4096 -> N=4096 (full). timeout floor 14400s. 3 seeds; partials keyed seed+run_mode+N.

## Queue
remote_cpu_queue (CPU; pure numpy).
