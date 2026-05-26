# Pre-reg: Wave 14 Bet Y Phase 2 — Kerdock 4-coset + β-sweep (β ∈ {2, 8, 32})

**Filed:** 2026-05-22
**Bet:** Bet Y (modern dense AM / Demircigil 2017 / Ramsauer 2020) — Phase 2 gate
**Predecessor:** `strategy_request_to_exp_dev_BetY_V2D_phase2_gate_2026-05-22.md` (Strategy 11:30 EDT)
**Predecessor:** `wave14_betY_phase1_beta_calibration_smoke` (cycle 100, c=32768 measured)

## Question

At N=4096, does modern dense AM (energy-descent cleanup) with Kerdock 4-coset keys at the **calibrated β=8** beat the argmax baseline by ≥1.5× capacity, as cap_map v100 β-calibration predicts?

Phase 0/v1 ran random bipolar keys at β=8 with ratio=1.00 (PARTIAL). Strategy hypothesizes the substrate at *structured* (Kerdock) keys + calibrated β enters the exp-capacity regime.

## Hypothesis

H_phase2: ratio = modern_capacity / argmax_capacity ≥ 1.5 at β=8 (calibrated optimal). Kerdock 4-coset gives sub-Gaussian off-diagonal cross-talk and pushes the cleanup into the regime where energy descent provides exponential capacity over argmax-only matching.

H_null: ratio < 1.0 at all tested β — modern dense AM cannot beat argmax with Kerdock keys at N=4096.

## Pre-declared verdicts

- `BET_Y_PHASE2_PASS` — best_ratio ≥ 1.5 (exp-capacity regime activated). Clears Phase 3 (N=65536 β=0.5).
- `BET_Y_PHASE2_PARTIAL` — 1.0 ≤ best_ratio < 1.5 (some gain; intermediate regime; β-blend follow-up).
- `BET_Y_PHASE2_KILLED` — best_ratio < 1.0 (modern dense AM never beats argmax with Kerdock keys at N=4096).
- `BET_Y_PHASE2_INCONCLUSIVE` — missing metric.

## Method

- **N**: 1024 (smoke), 4096 (full).
- **Key family**: Kerdock 4-coset codebook (4N codewords). Drawn from `make_kerdock_4coset_codebook` (validated in Bet C / Bet 2 / Bet A).
- **Values**: random bipolar.
- **W**: standard Hebbian outer-product `W = values.T @ keys / N`.
- **Argmax baseline**: `pred = (keys @ W.T @ values.T).argmax(dim=1)`.
- **Modern dense AM**: state init = `keys[i] @ W.T`; iterate `state = softmax(β · values @ state) @ values` for 5 iterations; final argmax over values.
- **PASS criterion per (M, β)**: accuracy ≥ 0.95 across ≥ ⌈2/3⌉ of seeds.
- **β-sweep**: {2.0, 8.0, 32.0} — bracket the calibrated optimum (β=8) with one octave below and two above.
- **M-sweep**: {1024, 4096, 8192, 16384, 32768} = M/N ∈ {0.25, 1, 2, 4, 8}.
- **Seeds**: 1 (smoke), 3 (full).

## Acceptance thresholds

- 1.5× ratio matches Strategy's PASS criterion (Demircigil-regime activation).
- 1.0× lower bound is the KILL gate (substrate at calibrated β no better than naive cleanup).

## Config

- N=4096 full, β ∈ {2, 8, 32}, M_grid = {1024, ..., 32768}, seeds = [17, 23+7, 31+7] (via base offsets).
- Expected runtime: smoke ~10s; full ~10-30 min (per Strategy estimate).

## Pre-declared interpretation

- **PASS at β=8**: substrate-product roadmap accelerates. Phase 3 cleared (N=65536, β=0.5).
- **PASS at β≠8 (calibration miss)**: c-law calibration is wrong for Kerdock keys. Update cap_map.
- **PARTIAL**: substrate is in intermediate regime. Next: β-blend or β-sweep refinement.
- **KILLED**: substrate cleanup is fundamentally argmax-class. Modern dense AM not a substrate-product enhancer at current arch.

## Not in scope

- N=65536 (gated on Phase 2 PASS).
- Phase 2.5 capability re-test at β=8 (multi-hop, Bet S K-ceiling, Bet A continual-edit, Bet C M/N=8) — gated on PASS.
- Comparison vs random bipolar — that ran in Phase 0/v1.
