# Pre-registration: wave14_betY_modern_dense_AM_v1

Date: 2026-05-21 (build); 2026-05-22 prereg-hygiene rewrite per Strategy
Status: Pre-registered, gated
Priority: Bet Y V2.D **Phase 0 baseline** — confirms modern dense AM beats
          argmax at N=4096 before Phase 1 beta-calibration sweep

## Why

Per Strategy v79 + cycle 93 addendum: modern exponential-capacity dense AM
(Demircigil 2017 / Krotov-Hopfield 2020 / Ramsauer 2020) should outperform
argmax cleanup. v1 is **Phase 0 baseline only**: at fixed N=4096 with fixed
beta=8, does modern energy-descent cleanup beat argmax?

Phase 0 PASS -> green-light Phase 1 beta-calibration sweep at varying N.
Phase 0 FAIL -> mechanism doesn't compose with substrate; abort Bet Y.

## Mechanism

For each M in grid:
  Baseline argmax: keys, values random +/-1; W = (values.T @ keys)/N;
                   predict via argmax(keys @ W.T @ values.T)
  Modern energy-descent: same W; cleanup iterates
                   state_t+1 = softmax(beta * values @ state_t) @ values
                   for n_iter=5 with beta=8

Capacity = max M (in units of N) where 95% retrieval passes over seeds.

## Verdict labels

- BET_Y_PASS (modern_capacity >= 1.5x argmax_capacity)
- BET_Y_PARTIAL (1.0x < ratio < 1.5x)
- BET_Y_KILLED (modern <= 0.9x argmax baseline)
- BET_Y_INCONCLUSIVE

## Phase 0 explicit caveat

Phase 0 uses **fixed beta=8 at N=4096** — NOT the beta(N)=c/N scaling protocol
from cycle 93 addendum. Phase 1 (separate experiment) will calibrate c via N
sweep. This v1 is "does the mechanism even work at substrate-product-optimal N".

## Runtime: ~15 min
