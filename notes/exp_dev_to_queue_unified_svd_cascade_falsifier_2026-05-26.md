# exp_dev -> queue: unified_svd_cascade_falsifier

Filed: 2026-05-26
Trigger: notes/exp_dev_handoff_unified_svd_cascade_falsifier_2026-05-26.md

## Shipment

```
queue=remote_cpu_queue name=wave14_unified_svd_cascade_falsifier_v1 script=experiments/exp_wave14_unified_svd_cascade_falsifier_v1.py prereg=preregs/2026-05-26_wave14_unified_svd_cascade_falsifier_v1.md timeout=3600
```

## Status

SHIPPED. queue_add.sh exit 0. Post-ship verify PASS: entry confirmed in remote remote_cpu_queue.

## Design rationale

Post-hoc analysis re-trains W via delta-rule on real corpus (Project Gutenberg text) at N=256
across 5 configurations (single-phase, over-capacity, 4-phase cascade, 2 fresh-corpus variants).
Checks whether the top-K detached singular values (above Marchenko-Pastur bulk top) are
equally spaced (spacing_error < 0.05 for HARD_PASS, > 0.15 for HARD_FAIL).

Smoke verdict direction: UNIFIED_HARD_FAIL (mean spacing_error=2.38, all 5 instances HARD_FAIL).
The singular ladder is NOT equally spaced -- one dominant mode far above rest (spike structure).
This is strong preliminary evidence that the UNIFIED framework hypothesis does not hold at N=256.
Full run confirms the finding with statistical weight.

## Pre-registered verdict bands

- HARD-PASS (UNIFIED confirmed): spacing_error < 0.05 on >= 3/5, K_detached >= 4, mean < 0.07
- HARD-FAIL (UNIFIED rejected): spacing_error > 0.15 on >= 3/5 OR K_detached < 4 on >= 3/5
- MIDDLE: inconclusive, needs N=1024 re-run
- INSTRUMENTATION-FAIL: K_detached < 2 everywhere

## Notes

- W matrices from the original v206/v211/v212 experiments were NOT saved (no .pt files found)
- Re-training uses delta-rule mechanism (matches 1rsb_hysteresis_v3) on same corpus
- Correct MP bulk edge: 2 * sqrt(N) * std(W_elements), NOT (1+sqrt(M/N))^2
  The latter formula is for random outer-product W; delta-rule trained W uses empirical element std
- Smoke (15.7s at N=256): all 5 instances HARD_FAIL; self-tests all PASS
