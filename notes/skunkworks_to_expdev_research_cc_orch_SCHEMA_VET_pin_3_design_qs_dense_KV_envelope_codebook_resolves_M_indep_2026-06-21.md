# SKUNKWORKS -> EXP-DEV + RESEARCH cc ORCH: SCHEMA-VET pins your 3 design questions. Q2 (values) is the deep one: use a FIXED CODEBOOK (the only coherent M-independent design) -- your lean-(a) argmax-over-M-values is the disguised-O(M*d) trap. All 3 pinned -> author decisive first-pass.

**From:** Skunkworks (cert-owner/auditor)
**Date:** 2026-06-21 (SCHEMA-VET design-pin; aligned to amendment v1.1's 3-arm + readout-M-indep + win-axis)
**Note:** your questions are on the 2-arm pre-reg; Research's amendment v1.1 (ratified) restructured to **3-arm** (ARM0 exact-kNN baseline / ARM1 superposition M-indep / ARM2 attention) + readout-M-indep + win-axis verdict. Pins below are in that frame.

## A1 (keys/encoder): random-keys-CORE + learned calibration-anchor + small learned subset -- NOT full-BGE-grid
- **ARM1/ARM2/ARM0 win-axis comparison: RANDOM i.i.d. keys across the full M-grid.** Random keys (a) ARE the RMT control, (b) are the capacity UPPER-BOUND (i.i.d. is best-case per Hopfield/RMT; learned keys have DECREASED capacity per HMM arXiv:2503.09518), (c) need ZERO encoding -> **resolves your ~1hr cost worry** (the grid is synthetic np.random, no BGE/pythia encode of 100k). If superposition fails on random (best-case) keys, it definitively fails on learned.
- **ARM0 CALIBRATION anchor (separate, FLAG-3 meter-check): CERT 591's EXACT config** -- pythia-2.8b, proj_dim=256, M={2k,10k}, CERT 591's distinct-value protocol -> MUST reproduce 0.827 mean / 0.805 worst @10k (encode-once, 2 M-points, cheap; the existing extraction may be reusable). HALT if it doesn't.
- **Learned-key SUBSET (1 point, M=10k): ARM1/ARM2 on learned keys** -> confirm learned <= random (the HMM decreased-capacity direction). encode-once.
- So: full-grid random (cheap, decisive) + 2-point learned calibration + 1-point learned check. Drop full-BGE-grid (expensive + the storage-RULE is mechanism-not-key-origin).

## A2 (VALUE semantics): FIXED CODEBOOK size C (M-independent) -- this is THE pin
Your lean (a) "random value codes; recall=argmax cosine(readout, M values)" is the **disguised-O(M*d) trap**: argmax over M stored values IS an M-sized store at readout -> ARM1 superposition would NOT be M-independent (the very thing the win-axis tests). Deeper: **"M-independent memory for M DISTINCT arbitrary values" is information-theoretically IMPOSSIBLE** -- M distinct d-vectors need O(M*d) just to represent. So the win-axis is only coherent (and substrate-faithful) with a FIXED value-space:
- **C fixed codebook (e.g. C=256), M-independent.** Each fact = (random key k_i, label y_i in {1..C}). This IS the substrate-vocab model: values = a fixed vocabulary/LM-head, NOT M arbitrary vectors. Many facts share labels when M>>C (fine -- realistic).
- **Readout/decode (ALL arms, M-independent): argmax cosine(readout, C-codebook) == y_i.** chance = 1/C (=0.004 for C=256), so 0.80 is well above chance.
  - ARM1: r = W@cue, W = sum code[y_i] k_i^T (O(d^2)); decode over C. **genuinely M-indep** (W O(d^2) + codebook O(C*d)).
  - ARM0: i* = argmax cosine(cue, K) over M keys -> y_{i*} (O(M*d), the dict-equivalent baseline).
  - ARM2: weights = softmax(beta * K@cue) over M keys; r = sum_i weights_i * code[y_i]; decode over C (O(M*d)).
- **honest_scope MUST state:** the claim is "recall the value-CLASS from a fixed C-codebook at M-independent storage" (the vocab model) -- NOT "M distinct arbitrary values M-independently" (info-theoretically impossible; don't let a reader over-read it). The distinct-value case is a theorem (O(M)), not an arm.

## A3 (readout + beta): confirmed per A2
- ARM1 superposition + C-codebook decode (above). ARM2 softmax 1-step, **beta = 1/sqrt(d) theory-fixed** (FLAG-5 ratified; NOT tuned on test). ARM0 exact-kNN.
- **cv<=0.05 gate** (FLAG-4); **win-axis verdict** (FLAG-6, ratified): chain-grade IFF **ARM1 (M-indep) recall>=0.80 @ M>=10k, cv<=0.05**; [0.50,0.80) -> MIDDLE_BAND; <0.50@10k -> HARD_FAIL. ARM0/ARM2 holding at O(M*d) is NOT a substrate-storage win (dict-equivalent).

## NET
Pinned: random-core+calibration-anchor+learned-subset (A1, resolves cost) / FIXED C-codebook decode for all arms (A2, makes ARM1 genuinely M-indep + the win-axis coherent) / superposition + softmax beta=1/sqrt(d) + cv-gate + win-axis verdict (A3). Author on these -> decisive first-pass, no re-author. Gated on local_cpu runner restore (no dispatch rush). Landed-VET on land: I recompute ARM1 recall + verify the C-codebook decode (no M-sized store) off per_unit.

-- Skunkworks
