# exp_dev upstream push: PP-50 N=65536+ kappa3 delta-alpha requires CLOUD

**Date:** 2026-06-03
**Priority:** HIGH
**Owner:** strategy

## Situation

PP-50 kappa3 delta-alpha N=65536 v1 FAILED with OOM on display GPU (RTX 4060 Ti, 8.6 GB total).
Measured actual failure: W matrix allocation ~17 GB required vs ~8 GB available.
Revised memory estimate for N=65536: Xi=860 MB + 4*V(2000 probes)=524 MB = 1.38 GB at N_PROBES=2000,
BUT in practice the runner allocates additional W-build workspace that pushes above 8 GB.

## N=32768 resolution

PP-50 N=32768 v3 (anchor: pp50_kappa3_delta_alpha_n32768_v3_n32768) is now queued. Peak VRAM
estimate 1.26 GB -- safe. This closes the N=32768 delta-alpha v3 protocol gap. If it HARD_PASS,
the N^(2/3) scaling law is confirmed at 3 N-values (16384, 32768, and post-cloud 65536).

## Cloud requirement for N=65536+

Any N >= 65536 kappa3 delta-alpha run requires a dedicated headless GPU with >= 24 GB VRAM.
Recommendations:
- Lambda A10 (24 GB VRAM): fits N=65536 and potentially N=131072
- Lambda A100 (40/80 GB): headroom for N=131072+ and larger N_PROBES sweeps
- Do NOT use display-adapter GPU for N >= 65536: Windows desktop display consumes ~4.5 GB VRAM
  leaving only ~4 GB for compute, which is insufficient for even N_PROBES=2000 at N=65536

## Authorization needed

Strategy: please authorize a cloud Lambda dispatch for pp50_kappa3_delta_alpha_n65536_v3 once:
1. pp50_kappa3_delta_alpha_n32768_v3_n32768 returns HARD_PASS (confirming N^(2/3) scaling continues)
2. User confirms cloud spend for ~$5-15 Lambda A10 run (~1-3h wall)

## Memory scaling (informational)

N=16384: peak ~0.3 GB (safe)
N=32768: peak ~1.26 GB (safe)
N=65536: peak ~5-17 GB depending on workspace alloc (requires cloud headless)
N=131072: peak ~20-70 GB (requires A100)
