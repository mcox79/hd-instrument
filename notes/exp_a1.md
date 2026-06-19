# Experiment A1: 50 atoms, exact-match recovery

**Date:** 2026-05-16
**Phase:** Week 6 atomic experiments

## Hypothesis

A codebook of 50 random FHRR atoms at N=1024 supports 100% exact-match recovery, and off-diagonal pairwise similarities are approximately Gaussian with std ~ 1/sqrt(N) = 0.0312.

## Predicted

- Recovery rate: 100/100% on all 50 atoms.
- Mean off-diagonal similarity: ~ 0 (within 1 std).
- Std off-diagonal similarity: 0.025 < std < 0.04.

## Falsification

- Recovery < 100% means the cleanup or substrate is broken.
- std outside [0.02, 0.045] means the atom-generation distribution drifted from theory.

## Result (2026-05-16)

| Check | Predicted | Observed | Outcome |
|---|---|---|---|
| Recovery rate | 100% | 100% (50/50) | confirmed |
| Mean off-diag sim | ~ 0 | 5.1e-5 | confirmed |
| Std off-diag sim | 0.025-0.04 | 0.0221 | tighter than predicted |
| Min retrieval sim | 1.0 | 1.0 | confirmed |

## Takeaway

The empirical std is 0.0221, well below the `1/sqrt(N) = 0.0312` prediction in `verification/theory.py`. This is *not* a bug — it's a substrate property: FHRR uses complex unit-magnitude atoms, and the variance of `Re(<a, b*>/N)` for two such atoms is `1/(2N)`, giving std = `1/sqrt(2N) = 0.0221`. Our `theory.py::atom_similarity_std` uses the HRR formula (real-valued atoms have variance `1/N`).

**Action:** Update `theory.py` to distinguish FHRR vs HRR, and tighten the verification test now that we know the actual distribution.
