# Pre-reg: Wave 14 Chain Smoother-Only v1

**Filed:** 2026-05-22
**Follow-up to:** HMM_3WAY_REFUTED (cycle 132) — backward smoothing identified as the sole effective mechanism.

## Question

Is backward-only (no forward iteration) sufficient to restore chain composition at N=65536? Or does the smoother need both forward + backward?

## Verdicts
- `SMOOTHER_ONLY_WORKS` — acc ≥ 0.70 (backward alone sufficient).
- `SMOOTHER_ONLY_PARTIAL` — 0.30 ≤ acc < 0.70.
- `SMOOTHER_ONLY_INSUFFICIENT` — acc < 0.30 (need both passes).

## Config
- N=65536, depth=50, K=100.
- 20 trials × 2 seeds.
