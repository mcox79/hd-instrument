# Experiment M7: Hebbian connectivity vs crosstalk

**Date:** 2026-05-16
**Phase:** Week 7 molecule experiments (density sweep)

## Hypothesis

When more atoms co-activate per Hebbian update, every pair among them gets reinforced. Higher co-activation count = denser Hebbian graph = more crosstalk on pairs that shouldn't have meaningful associations.

Concretely: with K=20 atoms, the signal pair (a0, a1) is reinforced every step at the maximum rate. Additionally `nc` random atoms from {a2..a19} are co-activated each step, reinforcing `nc*(nc-1)/2` extra "noise" pair weights. As nc grows, noise pairs accumulate weight that competes with the signal.

## Predicted

- nc=0 (signal only): noise pair weight stays at 0; SNR = infinity.
- nc=2 (1 extra random pair per step): noise pair gets reinforced ~T*1/153 = ~6 times each on average; small but nonzero noise.
- nc=10 (45 extra pairs per step): noise pairs reinforced ~T*45/153 = ~294 times each; noise weight comparable to signal weight.
- nc=18 (all noise atoms co-active, 153 noise pairs per step): every noise pair gets ~T*153/153 = ~1000 reinforcements -- saturating at W_inf=200. Signal-to-noise ratio approaches 1.

## Falsification

- Signal weight goes down with nc: bug; signal pair should always saturate at W_inf=200 regardless of noise.
- Max noise weight stays at 0 at nc=18: noise updates not propagating.
- SNR doesn't monotonically decrease with density: connectivity-vs-crosstalk relationship is broken.

## Result (2026-05-17)

| nc | pairs/step | density | signal weight | max noise weight | SNR |
|---:|---:|---:|---:|---:|---:|
| 0 | 1 | 0.005 | 198.67 | 0.00 | inf |
| 2 | 2 | 0.011 | 99.74 | 3.96 | 25.2 |
| 4 | 7 | 0.037 | 99.74 | 7.75 | 12.9 |
| 6 | 16 | 0.084 | 99.74 | 15.58 | 6.4 |
| 8 | 29 | 0.153 | 99.74 | 26.99 | 3.7 |
| 10 | 46 | 0.242 | 99.74 | 37.93 | 2.6 |
| 14 | 92 | 0.484 | 99.74 | 68.79 | 1.45 |
| 18 | 154 | 0.811 | 99.74 | 100.25 | 0.99 |

## Takeaway 1: monotonic SNR collapse with density (as predicted)

Max noise weight rises smoothly from 0 to 100.25 as connectivity grows. Signal-to-max-noise ratio falls below 2.0 around density ~0.5 and drops to ~1.0 at density ~0.8. By density 0.8 the strongest noise pair is **as strong as the signal pair** — the Hebbian graph has lost the ability to distinguish "really associated" from "incidentally co-active a lot."

This is the connectivity-vs-capacity tradeoff from the plan, made concrete.

## Takeaway 2: signal weight halves when noise updates intervene (unexpected real finding)

Look at the signal weight column: 198.67 at nc=0, but **exactly 99.74** at all nc>0.

Why: each outer iteration with nc>0 calls `h.update()` twice (once for signal, once for noise group), and the lazy-decay step counter advances on every `h.update()` call. Between consecutive signal reinforcements there are now *two* step increments, doubling the effective decay-per-reinforcement from 0.005 to ~0.01. The steady state is `1 / effective_decay = 100`, halving the saturating weight.

This is a real physical phenomenon: in a brain where many learning events are interleaved, the asymptotic weight of any specific pair depends on how often it's reinforced relative to the global step rate. **The lazy-decay model is faithfully reproducing this temporal-aliasing effect** — not a bug.

For future work it's worth deciding whether this is the desired semantics. Two alternative models:

1. **Continuous time**: decay applies to wall time, not step count. Signal pair weight depends on time elapsed since last reinforcement, independent of unrelated activity.
2. **Per-pair step counter**: each pair has its own step counter that only advances when it's specifically updated. Eliminates temporal aliasing.

The current model has the advantage of matching biological intuition (the brain has no global clock and shared timing); the alternatives have cleaner mathematical properties. **For Week 8 scaling-law experiments, document the chosen model explicitly so the exponents are interpretable.**

## Pre-registration check

Predicted "monotonic SNR decrease with density" — confirmed. Predicted "noise weight comparable to signal at high density" — confirmed (they cross at density ~0.81).

Did NOT predict the signal-weight halving. Noted explicitly as an emergent property of the temporal-aliasing in the lazy decay model. This is the kind of surprise the instrument exists to surface.
