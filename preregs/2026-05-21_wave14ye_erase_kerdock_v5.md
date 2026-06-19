# Pre-registration: wave14ye_erase_kerdock_v5

Date: 2026-05-21
Status: Pre-registered, gated
Experiment: [exp_wave14ye_erase_kerdock_v5.py](../experiments/exp_wave14ye_erase_kerdock_v5.py)
Priority source: extends [wave14ya_erase_kerdock_v4](../experiments/exp_wave14ya_erase_kerdock_v4.py)
(EXTENDS_TO_8N) — find if Kerdock has any cliff at all
Author: experiment_dev session, pipeline tick 16

## Why

v4 showed Kerdock 8-coset MM codebook protects multi-probe through
M=8N=32768 (substrate 8x over-capacity, kept_preservation holds).
v5 extends to **16 cosets** = 16N=65536 codewords. M_stored sweep
{2N, 4N, 8N, 12N, 16N} = {8192, 16384, 32768, 49152, 65536}.

This is the limit test: at 16x over-capacity, the substrate stores 65k
(v, k) pairs in an N×N matrix of rank ≤ N=4096 — a 16:1 compression
ratio. Welch-bound cross-talk holds by construction; the question is
whether kept_preservation finally breaks.

## Hypothesis

Either:
- Kerdock arm STILL passes at M=16N (envelope effectively unbounded
  by codebook density, bounded only by what we choose to test)
- OR Kerdock fails at some M in (8N, 16N] — finally finds the cliff

## Multi-probe success criteria

Same five as v1-v4. PASS verdict requires all five at every M_stored.

## Verdict labels

- `KERDOCK_V5_EXTENDS_TO_16N` — passes at all M; envelope to 16N
- `KERDOCK_V5_DECAYS_AT_<M>` — Kerdock cliff at some M ∈ (8N, 16N]
- `KERDOCK_V5_REGRESSES_BELOW_V4` — fails at M ≤ 8N (regression)
- `KERDOCK_V5_CORRELATED_PASSES` — control unexpectedly passes
- `KERDOCK_V5_INCONCLUSIVE`

## Pre-mortem

1. **GPU memory at M=16N**: codebook = 16N × N = 65536 × 4096 × 4 bytes
   = 1.0 GB. Plus probe tensors. Workstation has 8+ GB; should fit but
   borderline. Mitigation: smoke at N=1024 (16N=16384, 64MB) tests
   the construction path.
2. **Runtime**: matmul cost scales linearly with M. v4 at M=8N ran 128s.
   v5 at M=16N is 2x = ~250-400s. Within 1800s timeout.
3. **MM construction at 16 cosets**: 16 b values from GF(2^6) (period
   63 ≥ 15, fits). All 16 distinct, all 16 nonzero (except b_0=0), all
   C(16,2)=120 pairwise differences nonzero distinct GF elements
   (since they're 16 distinct powers of α; differences are nonzero).
   All differences are bent by MM property.

## Operational definition

Reuses v4 infrastructure; only changes:
- NUM_COSETS = 16
- M_STORED_FULL = [8192, 16384, 32768, 49152, 65536]

## Expected runtime

- Smoke (N=1024, M up to 16N=16384): ~10s
- Full (N=4096, M up to 65536): estimated 4-7 min

## What product decision this enables

- `EXTENDS_TO_16N` → Bet 2 envelope is unbounded for practical purposes
- `DECAYS_AT_<M>` → cap_map gets the actual ceiling number
