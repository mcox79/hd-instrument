# Pre-registration: wave14r_multihop_FHRR_v1

Date: 2026-05-21
Status: Pre-registered, gated
Priority: Strategy push (R8 A1 — multi-hop mechanism correction)
Author: experiment_dev session, pipeline tick 59

## Why

R8 identifies BSC's Walsh-XOR closure as the mechanism behind the multi-hop
depth cliff at d=25 (per wave14yp v17/v23). FHRR's continuous group has no
finite closure subgroup over generic codebooks, so chained binds avoid
collision-induced cross-talk.

A1 (pure FHRR) is R8's top-ranked rescue: BSC entities → FHRR phasors,
binding = element-wise complex multiply, bundle = complex sum, cleanup =
argmax over complex inner product magnitude (resonator-equivalent for
small codebook).

Comparison baseline (per R8 success criteria): wave14z_multihop_hadamard_entities
at NUM_FACTS=100 — FHRR must beat BSC across the curve.

## Verdict labels

- MULTIHOP_FHRR_50HOP_VALIDATED (acc_50 >= 0.80 AND monotone-decreasing)
- MULTIHOP_FHRR_PARTIAL_AT_<D> (0.40 <= acc_50 < 0.80)
- MULTIHOP_FHRR_KILLED (acc_50 < 0.40 across 3 seeds — R8 rescue fails)
- MULTIHOP_FHRR_INCONCLUSIVE

## Pre-armed rescue sketches (per PROT-004 + feedback-rehabilitation-after-rejection)

If MULTIHOP_FHRR_KILLED:
1. C1 hybrid (BSC store + FHRR chain) — boundary conversion may help
2. B1 modern Hopfield exponential cleanup — stronger per-hop denoise
3. Smaller NUM_FACTS — capacity/depth tradeoff may shift envelope
4. Increased N — Goldstone-mode literature predicts noise ~ sqrt(K)/N
5. Different relation codebook (orthogonal phasors per Sussillo+Abbott)

## Runtime: ~15 min (full multi-seed at depth=50, NUM_FACTS=100)
