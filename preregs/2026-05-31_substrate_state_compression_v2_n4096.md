# Pre-registration: substrate_state_compression_v2_n4096

**Date:** 2026-05-31
**Anchor:** substrate_state_compression_v2_n4096
**Queue:** remote_cpu_queue
**Script:** experiments/exp_substrate_state_compression_v2_n4096.py

## Context

Re-ship of v1 (failed 2026-05-31 due to CUDA contention). Commit 3ebb009 patched
the device line in v1; v2 is the clean re-ship with hardcoded CPU device.
Science deliverable unchanged: PP-2 evidence for C3 compression capability.

## Hypothesis

At least one of the 9 compression configs (SVD rank {N/8, N/4, N/2}, sparse
threshold {0.01, 0.05, 0.1}, quantization {4,8,16}-bit) will achieve >=4x
compression AND >=95% retrieval accuracy AND preserve all 3 killer features
(KF-1 deletion certificate, KF-2 norm drift, KF-3 edit consistency).

## Pre-registered bands

- **HARD-PASS (HP):** at least 1 config achieves compression_ratio >= 4.0 AND
  retrieval_acc >= 0.95 AND kfs_all_pass == True (across all 5 seeds).
- **HARD-FAIL (HF):** all 9 configs lose at least one killer feature across ALL seeds
  (any_kfs = False for every config).
- **MIDDLE-BAND (MB):** otherwise (some configs pass KFs but none hit HP threshold,
  or some seeds pass but not all).

**Middle-band outcome plan:** if MB, report which KF breaks first and at what
compression ratio, and file a cap_map annotation noting partial compression
viability with specific KF-safe regime.

## Config

- N = 4096 (PROT-018 binding)
- M_PROD = 2048
- N_PROBE_FULL = 100
- SEEDS_FULL = [7, 17, 23, 31, 41]
- Compression approaches: SVD (3 ranks), sparse (3 thresholds), quantization (3 bit depths)

## Timeout estimate

- smoke_wall_s = 5.26s (inner, seed=17, N=1024, M=256)
- FULL_N=4096, smoke_N=1024 (4x), FULL_seeds=5, smoke_seeds=1
- scaling_exp = 1.5 (moderate SVD ops)
- Formula: ceil(1.5 * 5.26 * 4^1.5 * 5) = ceil(315.6) = 900s
- PROT-019 floor: 14400s. Computed estimate 900s is below floor.
- **timeout_s = 14400** (PROT-019 floor applied; computed 900s << floor due to fast seed profile)
- Note: substrate_operation_cost (similar shape) completed in 310s, so 14400s is very conservative.

## N-suffix

_n4096 suffix; production N = 4096. PROT-018 compliant.
