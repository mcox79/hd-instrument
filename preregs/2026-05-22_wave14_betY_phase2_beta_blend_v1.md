# Pre-reg: Wave 14 Bet Y Phase 2 β-blend fine grid v1

**Filed:** 2026-05-22
**Bet:** Bet Y modern dense AM (Demircigil/Ramsauer) — Outcome 2 follow-up
**Predecessor:** `wave14_betY_phase2_kerdock_betacalibrated_v2` (PARTIAL ratio=1.00 at all of β ∈ {2, 8, 32})

## Question

Across a fine β grid spanning 3 octaves below cycle 100's calibrated β=8 and 3 above, does modern dense AM EVER beat argmax baseline on Kerdock 4-coset keys at N=4096?

Phase 2 v2 found ratio=1.00 at all three coarse betas. Strategy's Outcome 2 ask: characterize the trade-off via β-blend.

## Hypothesis

H_peak: ratio peaks somewhere in {0.5, 1, 2, 4, 8, 16, 32, 64} at ≥1.5×.

H_classical: ratio stays ≤1.05 at all βs — substrate with Kerdock 4-coset is genuinely classical-Hopfield-class and modern dense AM cleanup provides no capacity gain.

## Pre-declared verdicts

- `BETA_BLEND_PEAK_FOUND` — any β gives ratio ≥ 1.5 (exp-capacity activates somewhere).
- `BETA_BLEND_NEAR_GAIN` — 1.05 ≤ peak < 1.5 (small but real gain).
- `BETA_BLEND_CLASSICAL` — peak < 1.05 (substrate locked classical).
- `BETA_BLEND_INCONCLUSIVE` — metric collection error.

## Method

- Reuses Phase 2 v1 infrastructure (`p2.kerdock_keys`, `p2.capacity_argmax`, `p2.capacity_modern_dense`, `p2.find_max_passing_M`).
- β grid: {0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0}.
- M grid: {1024, 4096, 8192, 16384} = M/N ∈ {0.25, 1, 2, 4} (capped at 4N for Kerdock 4-coset codebook size).
- N=4096 full.
- 3 seeds full.
- 5 cleanup iterations per query.

## Acceptance thresholds

- 1.5× PEAK matches Strategy's original Phase 2 PASS criterion.
- 1.05× NEAR_GAIN is a real-signal floor (above seed noise but below decisive PASS).

## Config

- N=1024 smoke (β ∈ {4, 8} only), 4096 full (full 8-β grid).
- M_grid = [1024, 4096, 8192, 16384] full.
- seeds=3 full.

## Pre-declared interpretation

- **PEAK_FOUND**: c-law calibration was wrong about where exp-capacity activates. Update cap_map; refine c-law for Kerdock keys.
- **NEAR_GAIN**: substrate is intermediate. β-blend strategy may yield real but small gains; cost-benefit analysis warranted.
- **CLASSICAL**: substrate with Kerdock 4-coset is fundamentally classical-Hopfield. Modern dense AM is NOT a substrate-product enhancer here. Pivot Bet Y line — investigate why Kerdock structure prevents exp-capacity (orthogonality too high? Codebook geometry?).

## Not in scope

- N=65536 scale-up (Phase 3 — gated on PEAK_FOUND).
- Random bipolar comparison (Phase 0 already ran that).
- Other codebook families (Kerdock 32-coset, Hadamard, random).
