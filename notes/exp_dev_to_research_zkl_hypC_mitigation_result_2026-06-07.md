# Exp-Dev -> Research: Hyp C cosine-entropy mitigation -- MIDDLE (marginal, F1-free) but not HIPAA

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** zkl_hypC_mitigations_authorize #1

First-pass cosine-entropy whitening (whiten + project out top-r residual member-clustering directions), calibrated MarianMT
harness, smoke n=60 k=16:
  r=0(base)=0.167  r=2=0.167  r=5=0.150  r=10=0.150  r=20=0.167   (KEY-F1=1.000 throughout)

## Read: marginal F1-free reduction, doesn't reach 0.10
Projecting out the member-clustering directions reduces ZKL ~0.167->0.150 (10% relative) at ZERO KEY-job cost -- real but
small. Like the Hyp-B mitigations, it nudges leakage down but plateaus well above the 0.10 HIPAA target. MIDDLE_BAND.

## Caveat + remaining variant
My implementation is a PROXY for "cosine-entropy whitening": I project out the top-r principal directions of the whitened-
member cosine-Gram. The spec's full version is a whitening basis that directly MAXIMIZES cosine-distribution entropy (a
proper optimization, not a projection). That could do better -- but the trend across BOTH mechanisms' linear mitigations
(Hyp-B capping 0.43->0.27; Hyp-C projection 0.167->0.150) is the same: marginal F1-free reduction, no path to 0.10.

## Honest conclusion (strengthened)
The leak is robust to linear mitigations targeting EITHER mechanism. Recommend: (1) optionally run the full entropy-max
optimization as the last Hyp-C variant, but (2) the evidence increasingly supports the locked qualified posture + Path-D
(per-customer fine-tune) for absolute HIPAA. The F1-free reductions (B-capping + C-projection) compose as cheap defense-in-
depth (~0.43->~0.15 stacked, speculative) but not HIPAA-sufficient.
Queued: zkl_hypC_cosine_entropy_v1 (full n=500).
