# Prereg: wave14_F6_boolean_kkl_v1

**Filed**: 2026-05-24 exp_dev
**Anchor**: F-6 Boolean KKL probe re-ship (residual from v183 5-anchor hand-off)
**Source**: `notes/exp_dev_handoff_5anchors_post_v183_2026-05-24.md` anchor 3
**Hand-off**: `notes/exp_dev_handoff_v193_queue_refill_2026-05-24.md` optional anchor 4

## Hypothesis

Kahn-Kalai-Linial total influence theorem: substrate boundary functions f(x) = sign(<x, W e_j>) may satisfy Inf_total(f) >= C * Var(f) * log(n) with low single-coordinate dominance. If so, substrate boundaries are smooth and well-distributed (NOT a sparse junta).

## Design

- N=256 substrate width
- 2 operating-density points: M_density in {0.10, 0.30}
- n_samples=2000 per coordinate
- 5 seeds: [7, 17, 23, 31, 41]
- Boolean function: f(x) = sign(<x, W[:, 0]>) (first output coordinate)
- Influence: per-coordinate flip-rate over random BSC samples

## Falsifier bands (pre-registered)

- **HARD-PASS — Boolean-analysis row 🔬 -> 🟡 smooth boundaries**: max_inf_share <= 0.30 AND KKL ratio (Inf_total / (Var * log n)) >= 1.0 at ALL operating points.
- **HARD-FAIL — substrate behaves as junta; KKL row REJECTED**: max_inf_share >= 0.60 at >=1 operating point.
- **MIDDLE**: any intermediate; report bands.

## Smoke result (N=64, density=0.10, 1 seed)

`KKL_HARD_PASS_LOW_INFLUENCE` (max_inf_share=0.052, KKL ratio=1.064). Hypothesis supported at smoke; FULL needs density 0.30 stress and 5-seed confirmation.

## Self-test

`verdict self-test passed (4/4 cases)`.

## Queue

`queue=remote_cpu_queue name=wave14_F6_boolean_kkl_v1 script=experiments/exp_wave14_F6_boolean_kkl_v1.py prereg=preregs/2026-05-24_wave14_F6_boolean_kkl_v1.md timeout=2400`
