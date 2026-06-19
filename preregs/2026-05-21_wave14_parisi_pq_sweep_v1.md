# Pre-registration: wave14_parisi_pq_sweep_v1

Date: 2026-05-21
Status: Pre-registered, gated
Priority: Bet E comparative test (substrate-fingerprint claim)
Author: experiment_dev session, pipeline tick 64

## Why

Bet E claim: Parisi P(q) overlap distribution discriminates between substrate
codebook configurations (random ±1 vs Hadamard vs Kerdock) — if true, P(q) is a
substrate-fingerprint primitive needing no query access.

v1 scope: comparative test on 3 codebooks × 3 M_stored values (0.5N, N, 2N)
WITH 2 of the 6 diagnostic battery tests (Binder cumulant + ultrametricity).
The full 6-test battery + finite-size scaling is deferred to v2 — v1 is the
comparative-discrimination test.

If v1 shows >=2σ separation in P(q) shape across configs at same M_stored, Bet E
gets traction. If no separation, Bet E weakens (need methodology v2 to confirm).

## Mechanism

For each (codebook_type, M_stored, seed):
  pool = generate_pool(codebook_type, M_stored, seed)
  q_dist = pairwise_overlap_distribution(pool)
  binder = 1 - <q^4> / (3 <q^2>^2)   # Binder cumulant
  um_frac = ultrametricity_fraction(pool, n_triples=10000)
  histogram_peaks = detect_peaks(q_dist)

Compare across cells using mean ± std of binder, um_frac, peak_count.

## Verdict labels

- PARISI_DISCRIMINATES_CODEBOOK (>=2σ separation across configs)
- PARISI_DISCRIMINATES_M_STORED (no codebook effect but M_stored differs)
- PARISI_NO_DISCRIMINATION (Bet E weakens; P(q) generic)
- PARISI_INCONCLUSIVE

## Runtime: ~20 min full (9 cells × 3 seeds × ~30s each)
