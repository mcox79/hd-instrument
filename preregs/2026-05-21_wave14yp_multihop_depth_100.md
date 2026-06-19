# Pre-registration: wave14yp_multihop_depth_100

Date: 2026-05-21
Status: Pre-registered, gated
Experiment: [exp_wave14yp_multihop_depth_100.py](../experiments/exp_wave14yp_multihop_depth_100.py)
Priority source: extends multi-hop v3 depth sweep to 100 — Tier-2 KILLER
multi-step reasoning depth envelope
Author: experiment_dev session, pipeline tick 23

## Why

Multi-hop v3 tested depths {1, 5, 10, 25, 50}. yp tests depths {1, 25, 50, 100}
to probe whether chains can extend deeper than 50. Per-hop retention from v3
was 0.96, so 100-hop accuracy ≈ 0.96^100 = 0.017 — likely fails, but
characterizing the depth envelope is informative.

## Hypothesis

acc_50 ~ 0.15 (matches v3), acc_100 ~ 0.02 (geometric decay from per-hop 0.96).

## Verdict labels

- `MULTIHOP_DEPTH_100_HOLDS` — acc_100 >= 0.05 (deeper than v3 thought)
- `MULTIHOP_DEPTH_DECAYS_AT_<I>` — first depth where acc drops below 0.05
- `MULTIHOP_DEPTH_INCONCLUSIVE`

## Operational definition

Reuses v3 functions; HOP_DEPTHS = [1, 25, 50, 100], NUM_FACTS=200 (to fit
chain of 100 + distractors).

## Expected runtime: ~1-3 min
