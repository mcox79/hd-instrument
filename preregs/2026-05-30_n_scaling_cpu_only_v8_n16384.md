# Pre-registration: n_scaling_cpu_only_v8_n16384

**Date:** 2026-05-30
**Anchor:** n_scaling_cpu_only_v8_n16384
**Test:** T3 (Test 22-alt of user-routed batch)
**Queue:** remote_cpu_queue (CPU-only by design)
**Script:** experiments/exp_n_scaling_cpu_only_v8_n16384.py

## Hypothesis

The N=16384 Modern Hopfield activation bend (max_M_at_95_recall > N/4) is
not observable via GPU codebook construction within the 8 GB GPU budget —
v4 / v5 / v6 / v7 all OOM'd. CPU-only patient construction with explicit
chunkwise memory management can succeed where GPU could not, because
system RAM (>=16 GiB on the remote runner) is large enough to hold
codebook + W simultaneously.

If max_M_at_95_recall > N/4 = 4096, we have empirical confirmation of the
Modern Hopfield activation bend at N=16384 (currently unobserved).

## Config

- N = 16384 (PROT-018 _n16384 binding).
- BSC bipolar codebook (+/-1 sign matrix) at C = N = 16384.
  Constructed chunkwise on CPU, 256 rows per chunk.
- W is float32 (N, N) on CPU = 1.07 GiB.
- M sweep = [N/8, N/4, N/2, N] = [2048, 4096, 8192, 16384] (4 points).
- 3 seeds = [7, 17, 23].
- 12 cells total (4 M-points * 3 seeds).
- RSS logged at every chunk allocation; MEM_HARD_CEILING_GB = 12 GiB.
- Storage batch size W_BATCH = 64 (small batches to limit per-store peak).

## Pre-registered bands

**HARD_PASS:**
- Construction succeeds for ALL 4 M-points across all 3 seeds (12/12).
- max_M_at_95_recall (mean recall across seeds per M >= 0.95) > N/4 = 4096.
  (Bend confirmed.)

**HARD_FAIL:**
- All 12 cells OOM (no construction succeeds), OR
- Linear pattern: max_M_at_95 within +/-20% of N/4 = 4096
  (max_M in [3277, 4915]; storage capacity is linear, no Modern
  Hopfield bend).

**MIDDLE_BAND:** construction succeeds at smaller M (N/8, N/4) but OOMs
or fails at the N=16384 cell.

## Self-tests

- N_FULL == 16384 (PROT-018).
- make_bsc_codebook_cpu_chunked emits codebook of shape (C, N) with values
  exactly +1 / -1 (verified via float32 = 2 * randint(0,2) - 1).
- RSS guard triggers MemoryError if rss > MEM_HARD_CEILING_GB.
- compute_verdict returns T3_HARD_PASS / T3_HARD_FAIL / T3_MIDDLE_BAND /
  T3_INCONCLUSIVE only.
- Smoke at N=128, M=16: recall = 1.000 (sub-capacity perfect storage as
  expected); verdict computes without TypeError.

## Memory / OOM check

- Codebook: C*N*4 bytes = 16384*16384*4 = 1.07 GiB.
- W: N*N*4 = 1.07 GiB.
- Per-store batch keys+vals: 64 * 16384 * 4 = 4 MiB per batch.
- Peak (codebook + W + addmm temporary): ~3-4 GiB.
- Hard ceiling guard at 12 GiB triggers early exit with diagnostic info.
- The remote_cpu runner has >=16 GiB RAM; well within budget.

## Multi-scale smoke

- Smoke 1 (N=1024, M_sweep=[128, 256, 512, 1024]): all 4 cells succeed,
  recall=1.0; verdict T3_HARD_PASS (sub-capacity); wall=0.4s.
- Smoke 2 (N=4096, M_sweep=[512, 1024, 2048, 4096]): all 4 cells succeed,
  recall=1.0; verdict T3_HARD_PASS (still sub-capacity at M=N=4096 with
  BSC); wall=2.3s.
- Multi-scale smoke confirms CPU pipeline scales correctly through N=4096
  without OOM or integer-overflow. N=16384 is the production target.

## Walk-back gate

Smoke shows recall=1.0 at all (N, M) tested (BSC at C=N stores at near-perfect
fidelity up to M~=N in practice for ideal random codes). The genuine question
at N=16384 is whether max_M_at_95 exceeds N/4=4096 (the Modern Hopfield
prediction), so the test is well-posed at FULL even if smoke is uniformly
1.0.

## Timeout estimate

- smoke_wall_s = 2.3s at N=4096, 4 cells (1 seed) = 0.58s/cell.
- FULL: N=16384 (4x). Time scales O(M*N^2/W_BATCH) per cell. M ratio = ~4x
  (full M_sweep mean vs smoke). Per-cell scale factor: 4 * 16 = 64x.
- 12 cells * 0.58s * 64 = 446s. Apply 2x safety -> 892s.
- But: CPU at N=16384 the W matrix-multiplication inside addmm scales
  cubically when keys gather + addmm dominate. Conservative per-cell
  estimate at N=16384 is 30-300s/cell.
- Conservative budget: 12 cells * 300s * 1.5 = 5400s; round up + apply
  user spec: timeout_s = 86400 (24h budget per user task spec; CPU at
  N=16384 is slow).

**timeout_s = 86400** (user task spec).

## Notes

- This is the first N=16384 anchor that adopts pure-CPU construction
  after GPU paths failed in v4 / v5 / v6 / v7. If construction succeeds
  but recall is uniformly 1.0 at all M including M=N=16384, BSC at N=16384
  is in the sub-capacity regime even at M=N — that itself is a Tier-1
  scaling finding for the substrate.
