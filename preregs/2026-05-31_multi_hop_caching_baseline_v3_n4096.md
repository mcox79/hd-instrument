# Pre-registration: multi_hop_caching_baseline_v3_n4096

Date: 2026-05-31
Anchor: multi_hop_caching_baseline_v3_n4096
Queue: remote_cpu_queue
Script: experiments/exp_multi_hop_caching_baseline_v3_n4096.py

## Context

v2 (CONFOUNDED: CACHE_CAPACITY=256 > K_PATHS=100; all 15 cells hit_rate=0.984 with no
Zipfian variation; verdict_handler rescue ladder R2+R3 filed; 159th label-vs-honest catch).
v3 fix: CACHE_CAPACITY=16 << K_PATHS=100 forces LRU eviction so Zipfian-repetition signal
drives hit-rate differences across alpha values.

## Scientific question

At N=4096, M=2048, depth=5, K_paths=100, CACHE_CAPACITY=16, with Zipfian alpha in
{0.5, 0.75, 1.0, 1.5, 2.0}: does hit rate increase monotonically with alpha?
Does hot query latency fall below cold latency when cache hits occur?
Does audit chain integrity hold at 100%?

## Pre-registered bands

HARD-PASS = hit rate at alpha=2.0 >= 0.50 (heavy-tail exploits small cache)
            AND hit rate monotone non-decreasing across alpha grid
            AND hot_latency < cold_latency at alpha=2.0
            AND audit chain integrity 100% across all seeds and alphas.

HARD-FAIL = hit rate at alpha=2.0 < 0.10 (eviction kills all benefit)
            OR any audit chain violation (cached result != fresh recompute).

MIDDLE-BAND = audit intact AND hit rate at alpha=2.0 in [0.10, 0.50)
              OR non-monotone hit rate trend.

## Calibration note

No prior empirical anchor with evicting cache (CACHE_CAPACITY < K_PATHS).
HP threshold 0.50 is conservative (not theoretical max); per calibration-probe policy.

## Configuration

N=4096, M=2048, depth=5, K_paths=100, CACHE_CAPACITY=16
alpha_sweep=[0.5, 0.75, 1.0, 1.5, 2.0], N_QUERIES=2000, N_STARTS=20
Seeds=[7, 17, 23, 31, 41] (5 seeds)
device=cpu (forced)

## Smoke result

Smoke N=1024, M=256, depth=3, K_paths=20, CACHE_CAPACITY=16, alphas=[0.5,1.0,2.0], seed=17
Verdict: C2_HARD_PASS
hit@a=0.5=0.917 hit@a=1.0=0.917 hit@a=2.0=0.933 audit=1.000 elapsed=0.86s
Note: smoke K_paths=20 is close to CACHE_CAPACITY=16 so effect is small at smoke;
at FULL K_paths=100 vs CACHE_CAPACITY=16 the eviction pressure is 6x higher.

## N-suffix

_n4096 suffix binds N_FULL = 4096. Script asserts: assert N_FULL == 4096.

## Timeout estimate

smoke_wall_s = 0.86s (1 seed, 3 alphas, K_paths=20)
FULL has 5x alphas, 5x seeds, 5x K_paths, 4x N = ~167x more per-query work + 4x N scaling
Conservative estimate: ceil(1.5 * 0.86 * 167 * 4 * 5) = ~4323s
Using 7200s (flag for visibility per role contract; within 14400 limit).
timeout_s = 7200

## Middle-band outcome plan

If MIDDLE_BAND: measure the alpha at which hit rate saturates; if monotone trend present
but HP threshold not met, raise K_PATHS or N_QUERIES in v4 to amplify the signal.
If non-monotone: investigate cache eviction pattern per alpha (log eviction counts per cell).
