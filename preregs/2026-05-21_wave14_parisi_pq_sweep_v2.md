# Pre-registration: wave14_parisi_pq_sweep_v2

Date: 2026-05-21
Status: Pre-registered, gated
Priority: Bet E full 6-test battery (v1 PARISI_DISCRIMINATES_CODEBOOK validated)
Author: experiment_dev session, pipeline tick 67

## Why

v1 validated the comparative discrimination claim (PARISI_DISCRIMINATES_CODEBOOK
at huge separation). But Strategy's spec required a 6-test battery BEFORE any
RSB claim, because "structured codebooks suppress self-averaging" — the
multi-peaked P(q) might reflect codebook lattice geometry, not spin-glass RSB.

v2 adds the 4 tests v1 skipped:
- (3) Equilibration check: build pool from multiple corpus subsets, compare P(q)
- (4) Self-averaging diagnostic: single-realization vs ensemble-averaged P(q)
- (6) Spectrum check: eigenvalue distribution of overlap matrix Q

Skipping (2) System-size scaling for v2 since it requires multiple N values
(expensive); deferred to v3 if v2 confirms RSB-vs-codebook-geometry split.

## Mechanism

For each codebook in {random_bsc, hadamard, kerdock} at fixed M=2N:
  # Self-averaging (test 4): build POOL_K=10 separate pools at distinct seeds
  pools = [build_pool(seed=s) for s in seeds_pool]
  binder_per_pool = [binder_cumulant(P(q) from pool_i) for pool_i]
  self_averaging_var = var(binder_per_pool)  # small => self-averaging holds (RSB property)
  # Spectrum check (test 6): eigenvalues of pairwise overlap Q
  Q = pool @ pool.T / N
  eigvals = eigh(Q).eigenvalues
  spectrum_edge_density = histogram of eigvals near 0
  # Equilibration (test 3): pool vs sub-pools
  sub_p1 = pool[:M/2]; sub_p2 = pool[M/2:]
  binder_drift = abs(binder(sub_p1) - binder(sub_p2))

## Verdict labels

- PARISI_V2_RSB_CONFIRMED  (self-averaging, sharp spectrum, equilibrated, discrimination holds)
- PARISI_V2_FINITE_SIZE_ARTIFACT  (self-averaging fails -> v1 multi-peak was codebook geometry)
- PARISI_V2_EQUILIBRATION_FAIL  (binder differs across pool subsets => not steady state)
- PARISI_V2_INCONCLUSIVE

## Runtime: ~25 min full
