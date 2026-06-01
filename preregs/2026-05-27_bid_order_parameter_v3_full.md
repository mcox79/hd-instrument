# Pre-registration: bid_order_parameter_v3_full

**Date**: 2026-05-27
**Anchor**: bid_order_parameter_v3_full
**Script**: experiments/exp_bid_order_parameter_v3_full.py
**Queue**: remote_cpu_queue
**Parent**: bid_order_parameter_v2 (BID_MIDDLE_BAND_MIXED; is_smoke=True, 1 seed)

## Hypothesis

Substrate BID is OUTSIDE all 3 known Hopfield class bands in >= 4/5 seeds at N=1024.
v2 smoke showed BID=3.61 at N=256 (OUTSIDE_ALL_BANDS). Full run confirms at N=1024 multi-seed.

## Reference bands (3 Hopfield classes per arxiv 2601.17427)

At N=1024:
- Retrieval class: BID in [1.0, 2.5]
- Spin-glass class: BID in [256, 512]
- Paramagnetic class: BID in [1019, 1024]

Note: v2 smoke BID=3.61 at N=256 is OUTSIDE all three bands above (3.61 > 2.5 and < 64).

## Pre-registered bands

- HP1 (novel class): BID outside ALL 3 bands in >= 4/5 seeds at N=1024
- HP3 (stable): BID outside all 3 bands at ALL N in sweep (N=[1024,2048,4096,8192])
- HF2 (band-crossing): BID drifts INTO a band at large N
- MB1: mixed

## Timeout estimate

v1/v1_nsweep N=[1024,2048,4096] 5 seeds: elapsed 3.12s.
v3 adds N=8192: ~ceil(1.5 * 3.12 * 1.5 * 1) = 7s. timeout_s = 300s.
