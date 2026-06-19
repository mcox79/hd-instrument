# Pre-reg: Wave 14 Lane D N-scaling v1

**Filed:** 2026-05-22
**Bet:** Lane D capacity scaling vs N (extends BOUNDED finding at N=4096)
**Predecessor:** `wave14_lane_D_capacity_stress_v1` (BOUNDED — M_S_breakpoint=300, K_breakpoint=25 at N=4096)

## Question

At N ∈ {4096, 8192, 16384}, does the Lane D substrate's M_S (Bet S fact-count) breakpoint scale linearly with N (linear capacity) or sublinearly (substrate saturation)?

## Hypothesis

H_linear: M_S_breakpoint(N) ≈ c · N (constant ratio c ≈ 0.07 from N=4096 datapoint: 300/4096). Substrate capacity grows linearly per HDC theory.

H_saturate: breakpoint grows sublinearly — substrate saturates due to codebook geometry or cleanup limits.

## Pre-declared verdicts

- `N_SCALING_LINEAR` — c ratio's relative spread ≤ 0.30 across N ∈ {4096, 8192, 16384}.
- `N_SCALING_SUBLINEAR` — c shrinks with N (rel spread > 0.30, monotone decreasing).
- `N_SCALING_INVERTED` — c shrinks (breakpoint(8192) > breakpoint(16384)). Rare; flag.
- `N_SCALING_INCONCLUSIVE` — <2 N values measured.

## Method

- Hold K=3, U_stream=40, X_alphabet=5 (baseline values from COMPOSE).
- Sweep M_S ∈ {50, 150, 300, 600, 1200, 2400} per N.
- For each N: report first M_S where min(S, T, U, X) < 0.70.
- Single seed=17 (initial scan).

## Acceptance thresholds

- ≤30% relative spread in c ratio across N tests = LINEAR.
- Reuses 0.70 per-primitive PASS threshold from Phase 3 COMPOSE.

## Config

- N_grid full: [4096, 8192, 16384].
- M_S_grid full: [50, 150, 300, 600, 1200, 2400].
- Smoke: N_grid=[1024, 2048], M_S_grid=[50, 150, 300].

## Pre-declared interpretation

- **LINEAR**: Lane D capacity scales linearly with substrate dimension. Strong substrate-product story. Next: 32k, 65k extension.
- **SUBLINEAR**: substrate saturates beyond a certain N. Identify what limits capacity (codebook orthogonality? cleanup pipeline?).
- **INVERTED**: regression at higher N. Audit codebook construction.

## Not in scope

- N >= 32768 (gated on LINEAR result; cost-prohibitive otherwise).
- Multi-seed (single-seed scan; multi-seed re-run only if interesting).
- Joint multi-axis scaling.
