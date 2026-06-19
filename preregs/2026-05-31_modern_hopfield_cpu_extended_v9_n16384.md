# Pre-registration: modern_hopfield_cpu_extended_v9_n16384

Date: 2026-05-31
Origin: v290 cap_map follow-on to C1.
Trigger: C1 measured max_M=4N at N=16384 CPU with 100% recall in 3/3 seeds,
but the sweep STOPPED at 4N. C9 extends to identify the actual ceiling.

## Hypothesis

At N=16384, CPU, BSC bipolar, outer-product Hopfield W, the ceiling on M for
which 95% recall holds extends past 16N=262144 (i.e., capacity is at least
64x linear in N).

## Setup

- N = 16384 (PROT-018: `_n16384`).
- Codebook: CPU patient construction in 256-row chunks (BSC bipolar).
- W = (vals.T @ keys) / N (rank-M outer-product Hopfield).
- M sweep: [4N, 8N, 16N] = [65536, 131072, 262144].
- Seeds: [7, 17, 23].
- Probes: N_PROBE=100 per M.
- Recall threshold: 0.95.

## Memory budget

- Codebook at C=16N=262144, N=16384 float32: 262144 * 16384 * 4 = 16.4 GiB
  (the dominant memory item).
- W matrix at N=16384: 16384 * 16384 * 4 = 1.0 GiB.
- sims tensor (codebook @ q.T) at C=262144, n=100: 262144 * 100 * 4 = 100 MiB.
- Peak: ~17.5 GiB. Remote desktop has ~64 GiB system RAM; fits with headroom.
- If 8N construction OOMs, that is HARD_FAIL (informative: ceiling is at
  8N or lower due to memory budget, not algorithmic capacity).

## Pre-registered bands

- **HARD-PASS (HP)**: max_M_per_seed includes 16N=262144 in 2/3+ seeds
  (ceiling past 16N confirmed; at least 64x linear capacity).
- **HARD-FAIL (HF)**: construction OOMs at 8N=131072 or before in 2/3+
  seeds (system RAM limit hit; still informative).
- **MIDDLE-BAND (MB)**: max_M between 4N and 16N (ceiling identified
  within sweep at 4N < M < 16N).

## Smoke notes

- Smoke at N=1024, M_sweep=[2N=2048, 4N=4096]. Memory at smoke scale is
  trivial (~16 MiB codebook, 4 MiB W). Smoke verifies the construction
  loop and verdict gates fire correctly.

## Timeout estimate

- Smoke wall ~ 1-3 s at N=1024 / 2-cell M sweep / 1 seed.
- Full: N=16x, FULL_seeds=3, scaling_exp=2.0 (matrix-multiply dominant).
- formula: ceil(1.5 * 3 * 16^2 * 3) = ceil(3456) ~ 3500 s on GPU.
- CPU is slower (no GPU); estimated 10x slowdown for the W matmul +
  sims; codebook construction is also slow at C=262144 (262144/256 = 1024
  chunks, each requires 16384 random Bernoulli draws).
- Conservative total estimate per seed: 3-8 hours; total 9-24 hours.
- Queue TIMEOUT: **86400s (24h)** to allow full 3-seed sweep at worst-case
  CPU speed. Per role contract flag: >7200s is a long-run flag.

> NOTE: Long-run flag (>>7200s). Justification: codebook at C=16N=262144 is
> the dominant cost; cannot be reduced without changing the scientific
> question (ceiling identification at 16N).

## Queue + routing

- Queue: `remote_cpu_queue`.
- Script: `experiments/exp_modern_hopfield_cpu_extended_v9_n16384.py`.
- Anchor: `modern_hopfield_cpu_extended_v9_n16384`.
- Timeout: 86400 s.
