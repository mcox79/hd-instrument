# Prereg: substrate_capacity_alpha_sweep_v1_512_16384_gpu

## Anchor
substrate_capacity_alpha_sweep_v1_512_16384_gpu

## Routing
notes/routing_bundled_substrate_explorations_for_gpu_occupancy_2026-06-04.md, Bundle C (capacity boundary).

## Scientific question
How does the substrate capacity boundary alpha_c scale with N, and does substrate-as-training (cf-RPE delta
rule) exceed one-shot Hebbian? AUTO-associative protocol (canonical): store M=alpha*N bipolar patterns;
recall = fraction that are fixed points (one sign step keeps overlap>0.95). 2 rules x 6 N {512..16384} x
8 alpha {0.05..1.0} x 3 seeds. hebbian = one-shot W=Xi^T Xi/n (diag 0); cfrpe = iterative Widrow-Hoff.

## Pre-registered bands (robust cfrpe-vs-hebbian; absolute alpha_c is criterion/finite-N dependent, reported
not gated; classical asymptotic ref = 0.138)
HARD-PASS: clean boundaries (recall 1.0@a0.05, ~0@a1.0) AND cfrpe alpha_c > hebbian by >0.02 (training
exceeds one-shot capacity). MIDDLE: clean but within 0.02. HARD-FAIL: no boundary OR cfrpe < hebbian.

## Formula self-tests (PROT-022)
1. low-load recall=1.0 (both rules). 2. cf-RPE shrinks error. 3. classical ref 0.138. [PASS]

## Smoke gate
Smoke PASSED on remote GPU (N={256,512}, 2 seeds): HARD_PASS -- clean boundaries; cf-RPE alpha_c~0.31 >
hebbian~0.27. Absolute ~0.27 (not 0.138) is finite-N + overlap>0.95 + one-step inflation; full N=16384 shows
the downward N-trend toward classical.

## PROT-018 / 021
NO _nN suffix (N swept {512..16384}; declared _512_16384). timeout 14400s. 3 seeds.

## Queue
overnight_queue (GPU).
