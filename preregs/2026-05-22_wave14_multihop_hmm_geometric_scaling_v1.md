# Pre-reg: Wave 14 Multi-hop HMM Geometric Scaling v1

**Filed:** 2026-05-22
**Source:** `research_multihop_mechanism_3rd_attempt_2026-05-22.md` (Research 20:23 EDT) — Test 2 (chain-length scaling).

## Question

Does substrate's argmax-cleanup chain accuracy at N=65536, K=100 follow geometric decay acc(L) ≈ p_hop^L with p_hop ≈ 0.97 across L ∈ {5, 10, 20, 50, 100}?

Per Research's HMM/cascade-error theory: each hop is independent Bernoulli with success p_hop; n-hop chain success = p_hop^n. At p_hop=0.97, p^50 ≈ 0.218 matches cycle 121 empirical 0.217.

## Hypothesis

H_confirmed: log-linear fit r² ≥ 0.85 AND fitted p ∈ [0.94, 0.99] across L. HMM cascade-error theory validated.

H_falsified: r² < 0.60 — non-geometric scaling; cascade-error theory wrong.

## Pre-declared verdicts

- `GEOMETRIC_CONFIRMED` — r² ≥ 0.85 AND p ∈ [0.94, 0.99].
- `GEOMETRIC_PARTIAL` — r² ∈ [0.60, 0.85] OR p ∈ [0.85, 0.999].
- `GEOMETRIC_FALSIFIED` — r² < 0.60.
- `GEOMETRIC_INCONCLUSIVE` — metric collection error.

## Method

For each L ∈ {5, 10, 20, 50, 100}:
- Build factbase with depth L chain + (K-L) distractors.
- Run argmax cleanup chain query.
- 30 trials × 2 seeds.

Fit log(acc) = log(p) · L via linear regression. Report fitted p, R².

## Acceptance thresholds

- 0.85 r² = "clean geometric fit".
- [0.94, 0.99] p band = matches Research's predicted 0.97 ± tolerance.

## Config

- N=8192 smoke, 65536 full.
- num_entities=200, num_relations=20, num_facts=100.
- L_grid full: [5, 10, 20, 50, 100].
- n_trials=30, 2 seeds.

## Pre-declared interpretation

- **CONFIRMED**: HMM cascade-error theory validated quantitatively. Closes 3rd-attempt mechanism investigation with quantitative match across depth axis.
- **PARTIAL**: scaling is approximately geometric; refine theory.
- **FALSIFIED**: substrate's chain decay is non-geometric — Research's framework wrong on temporal axis too.

## Not in scope

- Test 1 three-way comparison (separate experiment).
- Test 3 per-hop p_fail measurement (separate experiment).
- K-grid sweep (single K=100).
