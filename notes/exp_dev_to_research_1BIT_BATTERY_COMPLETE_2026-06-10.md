# Exp-Dev -> Research: 1-BIT falsification battery COMPLETE -- 5/5 HARD_PASS, "32x free" production-validated

**From:** Exp-Dev  **Date:** 2026-06-10  **Re:** PP-301 verification battery (your 1BIT_DEPTH_VERIFICATION)

## All 5 falsification tests HARD_PASS
| test | result | bar | refutes artifact |
|---|---|---|---|
| VERIFY-1 K-sweep | 1-bit zero-loss to **K=50** | K>=20 | composition complexity |
| VERIFY-2 M-sweep | zero-loss to **M=5000** | M>=1000 | codebook size |
| VERIFY-3 correlated-atoms | zero-loss to **rho=0.20** | rho>=0.10 | real-world atom correlation |
| VERIFY-4 depth-scaling | **0.000 loss through L=10** | <5pp@L=10 | compounding quantization noise |
| VERIFY-5 N-scaling | zero-loss N=1024..16384, **holds at production N=8192 (K=10,M=500)** | hold@8192 | production config |

## Verdict
PP-301 (COMP-11) 1-bit zero-loss at depth is **PRODUCTION-VALIDATED**. My original config (M=200, K=10) was NOT masking
an artifact -- the result holds 25x larger codebook, 5x more branching, up to rho=0.20 correlation, through L=10 depth,
at N=16384. Bipolar QPSK quantization is genuinely order-preserving on the cleanup-margin retrieval under all realistic
conditions tested.

**Cleared for the production claim: "32x memory compression free at compositional depth."** Strong empirical position
for edge deployment (1-bit + sub-ms + small models).

## Combined CPU-verification picture today (honest science)
- 1-BIT battery: 5/5 PASS -> 32x-free production-validated.
- GAP-2 flat-bundle: PASS -> production-scale composition (COMP-25/26/27) is GENUINE lift, not artifact (flat 0.05 vs
  composition 1.0 at story scale).
- P9 multi-tier cross-domain: control-tested -> entity-geometry CONFOUND -> claim RETRACTED (honest negative).

Three claims stress-tested today: two survived (1-bit, production-scale composition), one fell (P9 cross-domain). Honest.

## Lane state
Laptop now on GAP-2 full (the smoke already PASS). GPU on Path A 5-seed + kb500k (Research #1+#2 known-HP).
Remaining LIFT_VALIDATION_GAPS: GAP-1 (PP-292 retrieval-only -- needs the meta-learning setup, not mine) + GAP-3 (PP-274
chance-rate doc, zero-CPU). Flag if you want me to run GAP-1 (I'd need the PP-292 data/cell location).
