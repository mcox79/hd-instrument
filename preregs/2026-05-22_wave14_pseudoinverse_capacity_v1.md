# Pre-reg: Wave 14 Pseudoinverse vs Hebbian Capacity v1

**Filed:** 2026-05-22
**Source:** `research_RS_phase_capacity_mechanisms_2026-05-22.md` (Research 15:25 EDT) — F2 learning-rule family, P=0.65.

## Question

At α ∈ {0.138, 0.50, 0.95} on N=1024 Hopfield substrate with random ±1 patterns, does the Personnaz-Guyon-Dreyfus 1985 / Kanter-Sompolinsky 1987 pseudoinverse rule W = Ξ^T (Ξ Ξ^T)^(-1) Ξ achieve higher attractor accuracy than Hebbian W = (1/N) Ξ^T Ξ?

Research's claim: pseudoinverse provably gives EXACT fixed points for all P < N linearly independent patterns (α → 1.0) WITHOUT requiring RSB. Tradeoff: basins shrink as α → 1.

## Hypothesis

H_pass: at α ≥ 0.50, pseudo_acc / hebbian_acc ≥ 2.0 (substrate's learning rule unlocks supra-AGS storage).

H_kill: ratio < 1.2 at all α — pseudoinverse doesn't beat Hebbian on substrate's bipolar patterns.

## Pre-declared verdicts

- `PINV_PASS` — best ratio ≥ 2.0 (supra-AGS storage via learning rule).
- `PINV_PARTIAL` — 1.2 ≤ ratio < 2.0.
- `PINV_KILLED` — ratio < 1.2.
- `PINV_INCONCLUSIVE` — metric collection error.

## Method

- Random ±1 patterns Ξ of size M × N, where M = ⌈α · N⌉.
- Hebbian: W_h = (Ξ^T Ξ) / N; zero diagonal.
- Pseudoinverse: W_p = Ξ^T (Ξ Ξ^T)^(-1) Ξ via `torch.linalg.pinv`; zero diagonal.
- Attractor accuracy: per pattern, run synchronous updates s_{t+1} = sign(W s_t) for n_iter steps; check if final state matches stored pattern (overlap > 0.95).
- Aggregate across seeds; ratio = pseudo_acc / hebbian_acc.

## Acceptance thresholds

- 2.0 PASS = "substantive supra-AGS gain" (matches Research's α→1.0 claim).
- 1.2 PARTIAL = "real but small gain".

## Config

- N=256 smoke, 1024 full.
- α_grid full: [0.138 (AGS), 0.50, 0.95]; smoke: [0.50, 0.95].
- n_iter=5 sync updates full.
- 3 seeds full.

## Pre-declared interpretation

- **PASS at α=0.95**: substrate's pseudoinverse rule unlocks α→1.0 capacity per F2 theory. Substantial substrate-product implication: replace Hebbian with pseudoinverse for supra-AGS use cases. Tradeoff in basin width must be characterized separately.
- **PARTIAL**: modest gain; investigate whether basin-shrinkage cost outweighs benefit.
- **KILLED**: F2 learning-rule mechanism doesn't help on substrate. Stick with Hebbian.

## Cost

`torch.linalg.pinv` on M×M with M up to ~970 at α=0.95, N=1024: ~1s on GPU. Total full run: <5 minutes.

## Not in scope

- Basin-width measurement (separate experiment — Research notes "basins shrink as α → 1").
- Online learning version (pseudoinverse is offline; online would be three-threshold perceptron).
- Kerdock or structured patterns (random ±1 baseline).
- N > 1024 (cost scales with M³ = α³N³ for pinv).
