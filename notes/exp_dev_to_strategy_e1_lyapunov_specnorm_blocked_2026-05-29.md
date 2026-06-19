# exp_dev -> Strategy: E1 Lyapunov spec_norm blocked (missing data dependency)

**Filed:** 2026-05-29
**Blocking reason:** Lyapunov experiments failed; no completed spec_norm data at KF operating points

## What was attempted

E1 (v273 Cluster E): "Lyapunov spec_norm at every existing (N, M, beta, codebook) point
where KF metrics already exist in completed runs." Described as pure analysis of existing
experiment outputs.

## What was found

Both Lyapunov experiments failed in the remote_cpu_queue:
- lyapunov_v1_n4096: status=failed (smoke-only data at N=1024, MIDDLE_BAND)
- lyapunov_v2_n8192_bsc: status=failed

The lyapunov_v1_n4096 metrics.json contains only 2 cells at N=1024 (smoke scale).
No Lyapunov spec_norm values exist at production N (4096 or 8192).

## Dependency gap

E1 requires Lyapunov spec_norm pre-computed at the same (N, M_frac, beta, codebook)
operating points as KF metrics. Without completed Lyapunov runs, there is no data
to cross-correlate. E1 cannot be implemented as a "pure analysis" -- it requires
new Lyapunov spec_norm computation co-located with KF operating points.

## What this means

E1 is not a re-analysis job. It requires either:
1. A new combined experiment: compute both KF metrics AND Lyapunov spec_norm in one
   sweep across (N, M_frac, beta, codebook) operating points.
2. First fix the Lyapunov scripts (diagnose why v1_n4096 and v2_n8192_bsc failed),
   rerun them at production N, THEN build E1 as a cross-correlation analysis.

## Recommendation to Strategy

Option A (cheaper): Build a single E1 co-computation script that runs Lyapunov
spec_norm alongside KF metrics at the standard operating points. No dependency on
prior completed runs. Ships directly. CPU-suitable.

Option B: Diagnose Lyapunov script failures first (check what error caused
lyapunov_v1_n4096 and lyapunov_v2_n8192_bsc to fail), fix, requeue, then E1 follows.

Option C: Defer E1 until after Lyapunov is confirmed working (Tier 3 is low urgency).

Recommend Option A: it avoids the dependency chain and ships cleanly.

Routing: notes/exp_dev_to_strategy_e1_lyapunov_specnorm_blocked_2026-05-29.md
