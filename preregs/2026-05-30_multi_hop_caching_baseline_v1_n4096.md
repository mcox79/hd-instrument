# C2 Multi-Hop Caching Baseline v1 at N=4096

## Anchor
multi_hop_caching_baseline_v1_n4096

## Queue
remote_cpu_queue

## Script
experiments/exp_multi_hop_caching_baseline_v1_n4096.py

## Scientific question
Implement simple LRU cache for Path D multi-hop results. Measure cache hit
rate + latency reduction at various Zipfian skew levels. Does cache preserve
audit chain integrity (cached results == fresh)?

## Pre-registered bands
- HARD_PASS: hit rate >= 0.30 at alpha=1.0 AND hot query latency <10ms AND
  audit chain integrity = 100% (all cache hits match fresh recompute).
- HARD_FAIL: hit rate < 0.10 OR audit chain corrupts.
- MIDDLE_BAND: otherwise.

## Config
- N = 4096 (PROT-018 _n4096)
- M = 2048, depth = 5, K_paths = 100, N_STARTS = 16
- N_QUERIES = 1000
- Zipfian alpha sweep: [0.5, 1.0, 1.5]
- Cache capacity: 256
- Seeds: [7, 17, 23, 31, 41]

## Self-test
- Verdict gates HP/HF/MB exercised
- Live CPU smoke at N=1024 alpha=1.0 with reduced n_q

## Timeout estimate
- smoke wall ~3s
- 5 seeds * 3 alpha values * 1000 queries; ~3 * (3 sec/query batch + per-query work)
- scaling_exp = 1.0; estimate = ceil(1.5 * 3 * 1 * 5 * 3 * 1000 / 30) ~ 2250s
- timeout_s = 14400 (user spec).

## Importance
HIGH - baseline for production cache layer with audit chain extension.
