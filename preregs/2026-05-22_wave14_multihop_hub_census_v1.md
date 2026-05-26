# Pre-reg: Wave 14 Multi-hop Hub Census v1

**Filed:** 2026-05-22
**Source:** `research_multihop_mechanism_redrill_2026-05-22.md` (Research 19:25 EDT) — section (b) NEW mechanism diagnosis.

## Question

Does codebook nearest-neighbor graph exhibit hubness signature (k-occurrence skewness ≥ 1.0) that grows with N, validating Research's new diagnosis: hubness × DPI information contraction?

Background: cycle 124 falsified Research's prior eigenvalue-near-degeneracy diagnosis. Research's redrill identifies hubness (Radovanović-Nanopoulos-Ivanović 2010) as primary candidate at P=0.45.

## Hypothesis

H_confirms: skew(N=65536) ≥ 1.0 AND monotone growth across N=4096 → 16384 → 65536.

H_absent: skew(N=65536) < 0.5 — substrate's codebook does NOT show hubness; Research's redrill diagnosis also wrong.

## Pre-declared verdicts

- `HUBNESS_CONFIRMED` — skew(N=65536) ≥ 1.0 AND monotone growth.
- `HUBNESS_PARTIAL` — skew(N=65536) in [0.5, 1.0] with monotone growth.
- `HUBNESS_ABSENT` — skew(N=65536) < 0.5 OR no growth.
- `HUBNESS_INCONCLUSIVE` — <2 N values.

## Method

For each N ∈ {4096, 16384, 65536}:
1. Generate K=100 random ±1 patterns (codebook).
2. Compute pairwise sim = codebook @ codebook^T / N; exclude self.
3. For each pattern, find its argmax (nearest neighbor).
4. k_occurrence = bincount(nearest); skewness = ⟨(k_occ - μ)³⟩ / σ³.

## Acceptance thresholds

- 1.0 skewness = standard hubness threshold (Radovanović 2010).
- 0.5 = "intermediate" boundary.

## Config

- N_grid full: [4096, 16384, 65536].
- K=100 (matches substrate multi-hop test).
- Single seed=17 (initial scan).
- Smoke: N=[1024, 2048].

## Pre-declared interpretation

- **CONFIRMED**: hubness mechanism viable. Substrate's deep-chain failure at large N is geometric (hub absorbing states), not dynamical (eigenvalue degeneracy). Routes substrate-product fixes toward codebook redesign (V3) or hub-aware readout.
- **PARTIAL**: hubness contributes but may not be dominant; investigate dual mechanisms.
- **ABSENT**: hubness also falsified. Substrate's deep-chain mechanism is genuinely unknown — substantial substrate-physics investigation needed.

## Cost

K×K matmul at K=100 + bincount: ~5 sec at N=65536 (CPU). Total <1 min.

## Not in scope

- K-NN beyond k=1 (single nearest neighbor only).
- Multi-K sweep.
- Kerdock 4-coset codebook (random ±1 baseline).
