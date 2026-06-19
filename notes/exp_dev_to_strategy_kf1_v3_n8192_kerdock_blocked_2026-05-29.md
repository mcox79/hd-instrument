# exp_dev upstream push: kf1_hallu_rescue_v3_n8192 KERDOCK_BLOCKED

**Filed:** 2026-05-29
**Anchor:** kf1_hallu_rescue_v3_n8192
**Status:** FAILED at runtime (Kerdock even-log2 violation at N=8192)

## What happened

The v3 script derives from exp_kf1_tier1_rescue_v1_n4096.py which contains
run_one_seed(). That function calls v3.make_kerdock_4coset_codebook(N, device)
at RUNTIME with the production N=8192. N=8192 log2=13 (ODD) fails the Kerdock
even-log2 check with ValueError.

The selftest at module scope used N=1024 (log2=10 even) -- passed cleanly.
The runtime N=8192 was never exercised during the gate check (--skip-smoke was used).

## Root cause

The routing file stated "KF-1 hallu rescue v2 uses argmax-vs-uniform readout, not
Kerdock codebook construction" -- but that is only true for the VERDICT computation.
The run_one_seed function in v1 builds a Kerdock codebook for the storage/retrieval
phase regardless of readout type.

## Blocking status

G1 (kf1_hallu_rescue_v3_n8192) is BLOCKED for N=8192 due to Kerdock even-log2.

## Strategy asks

Options for KF-1 N-axis extension:
1. Rewrite run_one_seed to use BSC atoms instead of Kerdock at N=8192 (or any N).
   BSC has no log2-parity restriction. This is ~0.5 day work.
2. Test at N=16384 (log2=14 EVEN, Kerdock SAFE). This would also satisfy N-axis extension.
3. Keep KF-1 row at green with annotation "N-extension blocked pending Kerdock fix".

Recommend: Option 2 (N=16384) if Strategy wants N-axis extension this cycle.
Option 1 (BSC fix) if the Kerdock codebook is non-negotiable.
