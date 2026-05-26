# Pre-registration: wave14zc_erase_kerdock_v7_32coset

Date: 2026-05-21
Status: Pre-registered, gated
Priority: Bet 2 envelope at 32x over-capacity (M up to 131072)
Author: experiment_dev session, pipeline tick 36

## Why
v5 (16 cosets) showed envelope extends to 16N. v7 tests 32N=131072.
Codebook = 2 GB at full mode; GPU memory risk.

## Verdict labels
- KERDOCK_V7_EXTENDS_TO_32N
- KERDOCK_V7_DECAYS_AT_<M>
- KERDOCK_V7_INCONCLUSIVE

## Risk
If full mode OOMs, fall back to M up to 16N (already validated by v5).

## Runtime: ~5-15 min (M scales linearly with cost)
