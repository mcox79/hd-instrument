# Pre-registration: kf2_isolation_proof_v2_n4096_audit

**Date:** 2026-05-29
**Anchor:** kf2_isolation_proof_v2_n4096_audit
**Queue:** overnight_queue
**Script:** experiments/exp_kf2_isolation_proof_v2_n4096_audit.py
**Parent:** kf2_isolation_proof_v1 (N=4096 HARD_PASS); kf2_isolation_proof_v2_n8192 (Kerdock-risk)

## Hypothesis

KF-2 edit isolation holds at N=4096 without BE-1 precision entanglement. The v2_n8192
run may have encountered Kerdock-even-log2 silent fallback (N=8192 log2=13 ODD).
This audit re-confirms isolation at Kerdock-safe N=4096 (log2=12 EVEN), fp32 only.

## Protocol

5 seeds x 5 M_fracs ([0.25, 0.5, 1.0, 2.0, 4.0] x N) x N=4096 x fp32 only.
No bit-precision sweep; BE-1 precision entanglement explicitly excluded.

## Pre-registered bands

HARD_PASS: max_iso < 0.05 across ALL M_fracs AND all 5 seeds.
  PLUS: max_iso <= 0.02020 (matches or improves on v1; N-corroboration).

HARD_FAIL: max_iso >= 0.10 at any under-cap M_frac (structural contamination).

MIDDLE_BAND: max_iso in [0.05, 0.10).

## Formula self-tests

1. N=4096 (PROT-018 binding). N=4096 log2=12 EVEN -> Kerdock SAFE.
2. theory_bound = 1/sqrt(4096) = 0.015625. Looser than N=8192 (0.01105).
3. isolation_ratio = max(|delta_acc[j]|) over j != edited. Range [0, 1].
4. within_theory_frac = fraction of cells where iso <= theory_bound.
5. HP_ISOLATION_MATCH = 0.02020 (v1 result; achievable corroboration band).

## Timeout estimate

v1 elapsed ~19.6s at N=4096 (same protocol). Safety 100x: ~2000s.
Floor _n4096 = 14400s.
timeout_s = 14400

## N-suffix binding (PROT-018)

_n4096 suffix -> N_FULL = 4096 in script. VERIFIED.

## Kerdock audit

N=4096 log2=12 EVEN. SAFE. No silent fallback risk.
