# Prereg: wave14_realtime_inference_learning_v1

**Date**: 2026-05-24
**Source**: untested-rows triage Priority A #4 (K5 / U6 KILLER T2)
**Script**: experiments/exp_wave14_realtime_inference_learning_v1.py
**Queue**: remote_cpu_queue (CPU-bound; N=2048, single stream, 3 seeds)

## Question

Does updating the substrate W after every prediction during inference (single-query
Hebbian update) reduce held-out-stream BPC compared to a frozen-W baseline trained
on a held-out corpus?

## Falsifier statements (per [[feedback-no-smoke]])

- **HARD-PASS**: mean delta = bpc_online - bpc_frozen <= -0.10 bits/char across 3 seeds.
  -> Online updates LIFT capability; K5 substrate-compatible; pipeline-config-change
     delivers measurable uplift.

- **HARD-FAIL**: mean delta >= +0.10 bits/char across 3 seeds.
  -> Online updates DEGRADE prediction; K5 incompatible with substrate.

- **MIDDLE_BAND**: mean delta in (-0.10, +0.10).
  -> Pipeline viable; no capability uplift; substrate accepts per-query updates
     without breaking but does not benefit.

## Discipline citations

- Per [[feedback-no-experiment-design-in-prompts]]: exp_dev chose online_alpha=0.05
  (6x smaller than the offline trainer's DELTA_ALPHA=0.3; conservative), N=2048
  (CPU-tractable at T=4000), T=4000 stream length, 3 seeds. Update rule matches
  the offline trainer's delta-rule (residual = target - predicted; dW = residual.T
  @ ctxs / N; W = (1-decay)*W + alpha*dW) -- same structural form, rescaled alpha.
- Per [[feedback-no-smoke]]: HARD-PASS + HARD-FAIL + MIDDLE bands pre-specified.
- Per [[feedback-rehabilitation-after-rejection]]: K5 is an UNTESTED row at v189;
  this is the first probe.
- Per [[feedback-ascii-only-in-scripts]] (OBSOLETED): N/A.

## Smoke gate

N=512 + T=800 + 1 seed. Should complete < 30s. Smoke PASS = bpc_frozen finite
and > 0 (sanity).

## Expected runtime full

CPU at N=2048, T=4000 stream, 3 seeds: ~5-15 min. Two streams per seed (frozen + online)
each ~T/batch_size matrix-vector passes at N=2048. Setting timeout=1800 (30 min)
as conservative upper bound.

## Smoke result summary (for reference)

N=512 + T=400 + 1 seed (lr_online=0.05): bpc_frozen=3.834, bpc_online=3.762,
delta=-0.072 -> would clear HARD-PASS -0.05 at smoke scale. Full run will validate
whether the lift survives at N=2048 + 3 seeds + T=4000.

## Out-of-scope (deferred to follow-up)

- Stream length scaling (T = 8000 vs T = 64000).
- LR sweep (lr in {0.005, 0.02, 0.1}).
- OOD stream (corpus B byte-shuffled).

These follow-ups dispatched only if this v1 verdict is HARD-PASS or interesting
MIDDLE_BAND.
