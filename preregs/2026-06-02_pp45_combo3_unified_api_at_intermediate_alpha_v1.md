# Prereg: pp45_combo3_unified_api_at_intermediate_alpha_v1

**Date:** 2026-06-02
**Anchor:** pp45_combo3_unified_api_at_intermediate_alpha_v1
**Queue:** remote_cpu_queue

## Scientific question
PP-45 5-method unified API algebraic uniformity at intermediate alpha values (0.05, 0.10, 0.12).

## Pre-registered thresholds
Same as PP-45 founding: HP1 |delta_err| < 1e-10, HP2 k3_err < 1e-4, HP3 CNDC < 1e-10, HP4 cert < 1e-10, HP5 matvecs <= 5.
HARD-PASS: all 5 HP at all 3 alpha cells in >= 4/5 seeds.
HARD-FAIL: HP1 fails >3 primitives at any cell.
MIDDLE: 4/5 HP or 2/3 cells all-HP.

## Timeout estimate
smoke_wall_s < 1s (N=512 CPU). FULL 3 cells * 5 seeds ~ 10s total.
timeout_s = **300s** (generous).
