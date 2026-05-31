# Pre-registration: multi_hop_caching_baseline_v2_n4096

**Date:** 2026-05-31
**Anchor:** multi_hop_caching_baseline_v2_n4096
**Queue:** remote_cpu_queue
**Script:** experiments/exp_multi_hop_caching_baseline_v2_n4096.py

## Context

Re-ship of v1 (failed 2026-05-31 due to CUDA contention). v1 had auto-CUDA in
main() which grabbed the GPU while V2 sustained_workload monopolized it. v2
fixes this with hardcoded torch.device("cpu"). Science deliverable unchanged:
C2 multi-hop caching characterization (deployment efficiency / PP-relevant).

## Hypothesis

At N=4096, M=2048, depth=5, K_paths=100 with Zipfian query skew (alpha in
{0.5, 1.0, 1.5}): the LRU cache achieves at least 30% hit rate at alpha=1.0
AND hot-query latency < 10ms AND audit chain integrity = 100%.

## Pre-registered bands

- **HARD-PASS (HP):** hit_rate >= 0.30 at alpha=1.0 AND mean_hot_latency_s <= 0.010
  AND min_audit_integrity == 1.0 (no audit violations across all 5 seeds).
- **HARD-FAIL (HF):** hit_rate < 0.10 at alpha=1.0 OR any audit chain violation
  (min_audit_integrity < 1.0 for any alpha).
- **MIDDLE-BAND (MB):** hit_rate in [0.10, 0.30) at alpha=1.0 with clean audit,
  OR hit_rate >= 0.30 but hot_latency > 10ms.

**Middle-band outcome plan:** if MB, report exact hit_rate + latency + audit
breakdown per alpha, and file a note on whether hot-path latency can be reduced
with a warmer cache or deeper Zipf skew.

## Config

- N = 4096 (PROT-018 binding)
- M_PROD = 2048
- DEPTH = 5
- K_PATHS = 100
- N_QUERIES = 1000 per (alpha, seed) cell
- ALPHA_SWEEP_FULL = [0.5, 1.0, 1.5]
- SEEDS_FULL = [7, 17, 23, 31, 41]

## Timeout estimate

- smoke_wall_s = 0.16s inner (1 alpha, 1 seed, 30 queries, 10 K_paths, depth 3)
- FULL vs smoke scale factor: (3 alphas/1) * (5 seeds/1) * (1000 queries/30) *
  (100 K_paths/10) * (5 depth/3) * (N=4096/1024 for build_shared) ~ 8325x sweep
  plus 4x N-build factor
- Raw estimate: 0.16s * 8325 * 1.5 = ~1998s
- PROT-019 floor: 14400s. Computed estimate 1998s is below floor.
- **timeout_s = 14400** (PROT-019 floor applied)
- Prompt prior: "5-30 min CPU" for FULL config. 14400s (4h) is safely above the
  30-min upper prior estimate.

## N-suffix

_n4096 suffix; production N = 4096. PROT-018 compliant.
