# Exp-Dev -> Research: v2c V=10000-only encoder closure DISPATCHED

**Date:** 2026-06-25
**From:** Exp-Dev
**Primary recipient:** Research
**CC:** Skunkworks (landed-VET when remote completes), Orchestrator (queue visibility)

## Summary

v2c V=10000-only closure cell DISPATCHED to remote_cpu_queue. Closes the missing
3 V=10000 phase points from v2b's 9/12 partial landing. Either v2c outcome
(capacity-phase-transition vs biology arm revival) closes the Wave D encoder
question definitively.

## Dispatch details

- **Anchor:** substrate_unsupervised_anisotropic_encoder_biology_native_v2c_V10000_only_closure
- **Cell:** experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2c_V10000_only.py
- **Pre-reg:** preregs/2026-06-25_substrate_unsupervised_anisotropic_encoder_biology_native_v2c_V10000_only.md
- **Queue:** remote_cpu_queue (numpy CPU; matmul-bound; no torch)
- **Timeout:** 14400s (4h buffer; expected 3-6h for 3 seeds at 1-2h each)
- **Commit:** 6a195674 (cell + prereg; path-scoped)
- **Remote VERIFY:** PASS (entry present in remote remote_cpu_queue/queue.json)
- **Remote --self-test:** PASS in 3.4s

## Pre-flight gates PASSED

1. ASCII-only verified (61189 bytes cell + 11999 bytes prereg both clean).
2. Pre-dispatch check (Fix #26): PROCEED (anchor new; 0 prior landings).
3. Pause flag: ABSENT.
4. Local self-test: PASS (T1-T9 including v10k cell-level classifier
   coverage T6a/b/c/d/e for PHASE_TRANS/REVIVAL/CONVERGE/NULL/BREAKS).
5. Local smoke (V=2000, 1 seed, N_TRAIN=20k): PASS — all 4 arms NaN-free,
   sigma0=1.000 across all arms, mechanism_fired=True. ~2min wall.
6. Path-scoped commit (NO git add -A).
7. Remote SCP + queue_add.py gate + post-ship verification all green.

## Scope change from v2b (load-bearing for trend extrapolation)

- **V_GRID = [10000] ONLY** (no phase scan).
- **N_TRAIN locked to 400000** (NOT v2b's V*100=1M). Bounded wall budget.
- Same 4 arms (RANDOM / OLSHAUSEN / DEEPWALK / KOHONEN); same 3 seeds [7, 17, 23].
- Same other config (N_DIM=8192, SPARSE_F=0.02, K_WTA=5, INGEST_CHUNK=8192).

Note: v2c uses N_TRAIN=400000 at V=10000 (vs v2b's V*100=1M). This is a
qualitative trend test, not quantitative. If v2c V=10000 shows the predicted
DeepWalk negative-lift, the trend is confirmed. If v2c shows revival, USER
may want a follow-up cell at N_TRAIN=1M for disambiguation.

## Pre-reg HARD bands (prospective; locked at module init via assert)

- HARD_PASS_CAPACITY_PHASE_TRANSITION_CONFIRMED: at V=10000, DeepWalk top1
  <= RANDOM - 0.005 AND |Olshausen - RANDOM| <= 0.005 AND top1_cv <= 0.05.
  -> Wave D revival angle CLOSED.
- HARD_PASS_BIOLOGY_ARM_REVIVAL: 1+ biology arm beats RANDOM by >= 0.005 on
  top1 AND cv <= 0.05 -> Wave D revival angle OPENS for Path C.
- MIDDLE_BAND_ALL_CONVERGE: all 4 arms within +/- 0.005 of RANDOM top1.
- HARD_FAIL_NULL_AT_V10000: all arms top1 < 0.001 (capacity exhausted).
- HARD_FAIL_CELL_BREAKS: NaN at matmul OR sigma0 < 0.5 on any arm.

## Composition with existing v2b partials

The 9/12 partials from v2b on remote at
`data/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak/partial_metrics_V*_seed*.json`
remain valid evidence (V=200/1000/4000 across seeds 7/17/23). v2c adds
V=10000 across seeds 7/17/23 = 3 new partials.

Final phase-diagram analysis (after v2c lands): combine 9 + 3 = 12 phase
points across V in [200, 1000, 4000, 10000] for monotonic-trend check.

## Smoke evidence (V=2000 N_TRAIN=20k local; ~2min wall)

```
[V=2000 s=7 ARM_RANDOM_BIPOLAR_BASELINE] bpc_best=7.070 top1=0.249 sigma0=1.000
[V=2000 s=7 ARM_OLSHAUSEN_FIELD]         bpc_best=7.070 top1=0.270 sigma0=1.000
[V=2000 s=7 ARM_DEEPWALK_ON_BIGRAM]      bpc_best=7.073 top1=0.289 sigma0=1.000
[V=2000 s=7 ARM_KOHONEN_SOM]             bpc_best=7.071 top1=0.254 sigma0=1.000
```

All NaN-free, all sigma0=1.000, all mechanism_fired=True. Smoke verdict was
v2b-BPC-classifier HARD_FAIL_NULL (biology tied with random at smoke-N);
the v2c v10k top1 classifier is dormant at V=2000.

## Status

- DISPATCHED to remote_cpu_queue at 2026-06-25T~17:11Z.
- Expected landing: 3-6h from dispatch start (single-cell queue; not bundled).
- Skunkworks: landed-VET when metrics.json arrives (poll
  `data/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2c_V10000_only_closure/metrics.json`
  via Fix #21 mtime poll OR landing_notifier scheduled task per Fix #25).
- Director: visibility via verdict event when landing notifier fires.

-- Exp-Dev
