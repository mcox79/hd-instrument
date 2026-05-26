# Pre-reg: Wave 14 Bet R Polynomial p-body Coupling v1

**Filed:** 2026-05-22
**Bet:** Bet R p-body coupling super-linear capacity (forward direction #4 per active_priorities)
**Source:** R27 L.1 Musa 2025 inspiration; closed-form polynomial Krotov (no N^4 dense storage)

## Question

At N=4096 with Kerdock 4-coset keys, does closed-form polynomial Krotov cleanup (E(s) = -Σ_μ (s·ξ_μ)^p) at p ∈ {2, 4, 8} give a capacity advantage over the argmax baseline?

This distinguishes from Bet Y (softmax = exp of similarities = all p-bodies weighted by Taylor): polynomial cleanup has *finite* p-body order only. Bet Y Phase 2 found ratio=1.0 across β grid; we test whether finite p can do better.

## Hypothesis

H_pass: at p=4 or p=8, ratio ≥ 1.5 (substrate-novel finding consistent with Musa 2025 χ^(3)/χ^(5) photonic Hopfield).

H_nogain: ratio stays ≤ 1.05 across all p. Substrate finite p-body provides no advantage over argmax with Kerdock 4-coset.

## Pre-declared verdicts

- `PBODY_PASS` — best ratio ≥ 1.5 (substrate-product significant).
- `PBODY_PARTIAL` — 1.05 ≤ best ratio < 1.5 (small but real).
- `PBODY_NOGAIN` — best ratio < 1.05.
- `PBODY_INCONCLUSIVE` — metric collection error.

## Method

- Reuses Phase 2 v1 infrastructure (`p2.kerdock_keys`, `p2.capacity_argmax`, `p2.find_max_passing_M`).
- Polynomial p-body cleanup: state_{t+1} = (sims_norm)^(p-1) @ values, where sims = values @ state. Renormalize state magnitude to sqrt(N) after each step to avoid drift.
- p-values: {2, 4, 8}. p=2 should match argmax (sanity). p=4 = Musa 2025 χ^(3). p=8 = beyond canonical.
- N=4096 full, M_grid = {1024, 4096, 8192, 16384}.
- 3 seeds full.
- 5 cleanup iterations per query.

## Acceptance thresholds

- 1.5× PASS matches Bet Y Phase 2 PASS criterion (consistent substrate-product standard).
- 1.05× PARTIAL same as β-blend floor.

## Config

- N=1024 smoke, 4096 full.
- p_values full: [2, 4, 8].
- M_grid full: [1024, 4096, 8192, 16384].
- seeds=3 full.

## Pre-declared interpretation

- **PASS**: substrate finite p-body coupling is the right cleanup mechanism (not softmax). Pivot Bet Y line to polynomial. Update cap_map (Bet R PROMOTED to validated).
- **PARTIAL**: closed-form polynomial gives marginal gain; full Musa 2025 explicit-coupling would require sparse N^4 storage (separate engineering bet).
- **NOGAIN**: Kerdock 4-coset codebook locks substrate into classical regime regardless of cleanup. Bet R closed PROVISIONAL.

## Not in scope

- Dense N^4 storage (infeasible per Strategy notes).
- Sparse 4-body W_ijkl construction (separate experiment, requires sampling protocol).
- Other key families (Hadamard, random) — Phase 2 v0 covered random bipolar; Kerdock is the validated substrate-product codebook.
