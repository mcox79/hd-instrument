# Pre-reg: sustained_workload_24h_baseline_v1_n4096

**Date:** 2026-05-30
**Anchor:** `sustained_workload_24h_baseline_v1_n4096`
**Script:** `experiments/exp_sustained_workload_24h_baseline_v1_n4096.py`
**Queue:** `overnight_queue` (GPU; per S11 confirmed 56x Path D speedup)
**Timeout:** 90000s (25h; 1h headroom over 24h target)
**Phase:** 1 of 3 (corrected plan; 24h hours-scale validation BEFORE multi-day cloud)

## Purpose

24-hour sustained workload validation. Detects state drift, memory
leaks, audit chain integrity issues, performance drift over hours-scale
BEFORE multi-day cloud dispatch. This is the FIRST sustained-workload
test of the substrate at production scale.

This anchor occupies one GPU runner slot for ~24 hours. Other anchors
queue around it. User-acknowledged trade-off.

## Design

- **N=4096, M=2048, BSC, 1 seed (long-running single trial).**
- **Operation mix:** 40% retrieve, 30% Path D multi-hop (depth=5, K=100,
  1 start per op), 20% edit, 10% delete-with-cert + replenish.
- **Target rate:** 1000 ops/hour = ~0.28 ops/sec = ~17 ops/min.
  24h total: 24,000 operations.
- **Hourly checkpoint:** 24 hourly partials with per-hour aggregations.
- **Audit chain:** verified every 1000 ops via `verify_cert_chain`.
- **KF spot-checks:** every 4 hours (6 spot-checks total) for KF-1
  spurious firing rate and KF-2 max edit isolation.

## Measurements (logged continuously, aggregated at hourly + final)

- Per-op latency (mean, p99) per hour, in milliseconds
- Hourly throughput (ops/sec actual vs target)
- Memory footprint: RSS (psutil), GPU memory (torch.cuda), Python heap
  (tracemalloc)
- Audit chain length + integrity (% valid at each 1000-op checkpoint)
- KF-2 max_iso and KF-1 spurious firing rate at every 4-hour spot-check
- State drift: substrate W L2-norm change over time, codebook usage
  histogram L1 drift vs initial

## Pre-registered bands

| Outcome | Criterion |
|---------|-----------|
| `SUSTAINED_HARD_PASS` | 24h sustained operation completes (>=95% of target ops) AND throughput within 10% of baseline (first-60s window) AND audit chain 100% integrity (no corruptions) AND RSS growth <= 2x initial AND KF-2 spot-check drift < 0.2 absolute across 6 checks AND KF-1 drift < 0.2 |
| `SUSTAINED_HARD_FAIL` | Mid-run crash (any operation raises) OR throughput drops > 50% over 24h OR audit chain corrupts (verify_cert_chain returns False at any checkpoint) OR RSS growth > 5x OR killer feature degrades (KF drift exceeds threshold during stable-state region) |
| `SUSTAINED_MIDDLE_BAND` | Otherwise -- pipeline completes but informative drift (e.g. throughput drifts 10-50%, RSS grows 2-5x, KF spots drift 0.2-0.5); investigate but cloud-dispatch still possibly viable |

## Smoke result (recorded 2026-05-30)

- N=512, M_init=256, total_ops=1000, target_seconds=60s (1-minute sim).
- Wall: 61.0s.
- Verdict: `SUSTAINED_HARD_PASS` ("PRODUCTION_READY: ops=1000
  throughput_drift=0.026 rss_growth=1.00x kf2_drift=0.0 kf1_drift=0.0
  cert_valid=True w_norm_drift=0.998").
- Baseline throughput: 16.514 ops/s; final throughput: 16.428 ops/s
  (drift 0.5%).
- Audit chain: 119 links built and validated.
- KF spots: stable across 3 checks.
- W L2-norm drift: 0.998 (essentially flat over 1000 ops).

This is a small-scale "pipeline works" smoke; the FULL run extends this
to 24h with N=4096, M=2048 stress.

## Effect-size / walk-back gate

Not applicable. The HARD_PASS is multi-criterion (throughput drift,
memory growth, audit integrity, KF stability) -- each criterion has an
explicit numerical band.

## Timeout estimate

User-specified: 90000s (25h; 1h headroom over 24h target). Honored.

This exceeds the 14400s (4h) escalation ceiling, but the experiment is
INHERENTLY long-running (the 24h duration is the test). Surfacing to
For You status_log with `importance=HIGH` per role-contract long-run
flag.

Per role-contract:
- Estimate exceeds 7200s -> flag in For You.
- Estimate exceeds 14400s -> normally BLOCK; but user explicitly
  specified the 24h duration as the test parameter, so this is
  user-approved-long-run, not a smoke-estimate overrun.

## OOM pre-check

- W at N=4096 = 4096 * 4096 * 4 bytes = 67 MB. OK on 8 GB GPU.
- Codebook at C=N=4096: 67 MB. OK.
- DenseStore replaces W via `self.W = self.W + ...` each edit/delete --
  this allocates a NEW tensor each time. Over 24,000 ops, naive PyTorch
  refcount-handling SHOULD free the old tensor immediately, but
  fragmentation may grow GPU memory. The HARD_FAIL ceiling of 5x growth
  captures this. The MIDDLE_BAND captures 2-5x informative drift.
- Tracemalloc + RSS + GPU memory tracked HOURLY to catch leaks early.

## Dependencies verified

- `experiments/_workload_harness.py` exists (DenseStore, make_cert,
  verify_cert_chain, kf2_spot_check) -- imported and self-test PASSES.
- `experiments/_seed_checkpoint.py` exists.
- No Research deliverables required -- this is a pipeline stress test.
- Cap_map row: `sustained_workload_hours_scale` is currently empty
  (this is the first measurement); successful HARD_PASS would populate
  it.

## PROT-018

Suffix `_n4096`. Validator extracts suffix-N = 4096. Script has bare
`N = 4096` and `N_FULL = 4096` assignments at module scope.

## Runner-slot impact

- Occupies overnight_queue for ~24h.
- Other anchors queue around it (FIFO; runner picks next-in-queue).
- Heartbeat watchdog `silent_idle` will NOT fire because the runner
  IS active; it will, however, see the same anchor name running for
  24h, which may trigger `for_you_stale` if no other status events
  are logged. exp_dev/orchestrator should fire periodic status_log
  entries while this is in flight.

## What happens after this anchor lands

- If `SUSTAINED_HARD_PASS`: substrate is production-ready for
  hours-scale workloads. Multi-day cloud dispatch becomes possible.
  Cap_map row `sustained_workload_24h_n4096` becomes Tier-1 evidence.
- If `SUSTAINED_HARD_FAIL`: identify failure mode (crash, leak, cert
  corruption, throughput drift) -- each is a distinct bug class.
  Multi-day cloud dispatch BLOCKED until fixed.
- If `SUSTAINED_MIDDLE_BAND`: investigate the drift pattern; may need
  M-stationarity guards or W normalization before multi-day cloud.
