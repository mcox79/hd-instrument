# Pre-registration: substrate_state_compression_v4_n16384

**Date:** 2026-05-31
**Anchor:** substrate_state_compression_v4_n16384
**Queue:** remote_cpu_queue
**Script:** experiments/exp_substrate_state_compression_v4_n16384.py
**Cap-map row:** PP-2 (state compression / quantization)

## Hypothesis

c_quant/bits8 quantization that HARD_PASSed at N=4096 (v2) and N=8192 (v3 in flight)
also preserves 4x compression + retrieval >= 95% + KF-1/KF-2/KF-3 at N=16384.

## Pre-registered Bands

**HARD-PASS:** c_quant/bits8 achieves >=4x compression AND retrieval_acc >= 0.95 AND
all KFs pass (KF-1 + KF-2 + KF-3) in 2/3+ seeds at N=16384.

**HARD-FAIL:** c_quant/bits8 KF preservation breaks (any KF fails in majority of seeds)
AND compression < 4x at N=16384. Foothold is N-bounded -- does not scale.

**MIDDLE-BAND:** c_quant/bits8 holds compression >= 4x but retrieval degrades <95%,
OR KFs partially preserved. Suggests scaling boundary or regime shift.

## Middle-band outcome plan

If MIDDLE_BAND: file exp_dev_to_strategy note identifying the scaling boundary.
Strategy decides: (a) accept N=4096 + N=8192 as the valid product range, (b) commission
retrieval-preservation rescue at N=16384.

## Config

- N = 16384 (PROT-018 binding)
- bits tested: {4, 8, 16}
- M_PROD = 8192 (N/2, matches v2/v3 ratio)
- N_PROBE = 100
- Seeds: [7, 17, 23] (3-seed, matches v3 scope at N=16384 CPU cost)
- device: CPU (remote_cpu_queue)

## Timeout estimate

- smoke_wall_s = 0.07s (N=1024, 1 seed, 3 configs)
- FULL_N / smoke_N = 16384 / 1024 = 16
- FULL_seeds / smoke_seeds = 3 / 1 = 3
- scaling_exp = 1.5 (vector ops with intermediate allocations)
- formula: ceil(1.5 * 0.07 * 16^1.5 * 3) = ceil(20.2) = 21s
- rounded to 300s floor (conservative 5-min minimum)
- **timeout_s = 300**

## Smoke result

N=1024, 1 seed: C3V4_MIDDLE_BAND (expected at 1 seed -- HP requires 2/3+ seeds)
All 3 configs measured, no errors. bits8: comp=4.0x retr=1.000 kfs=OK.
No suspicious results. Proceeding to FULL.

## N-suffix binding (PROT-018)

Anchor name _n16384 binds N_FULL = 16384. Verified: `N = 16384` in script.

## Strategic context

Third data point for PP-2 cross-N validation. If PASS, PP-2 is empirically anchored
at N={4096, 8192, 16384} -- the substrate's full N range. Production-deployment
confidence for quantization layer.
