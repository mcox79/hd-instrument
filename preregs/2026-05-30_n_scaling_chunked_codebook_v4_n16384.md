# Pre-reg: n_scaling_chunked_codebook_v4_n16384

**Date:** 2026-05-30
**Anchor:** n_scaling_chunked_codebook_v4_n16384
**Script:** experiments/exp_n_scaling_chunked_codebook_v4_n16384.py
**Queue:** overnight_queue (GPU; falls back to remote_cpu_queue if persistent OOM)
**Parent priorities:** T1.1 (Modern Hopfield exponential-capacity rescue at N=16384)

## Hypothesis

The substrate exhibits an exponential-capacity (Modern Hopfield) bend at
N=16384 with max_M_at_95_recall > N/4. C1 diagnostic (commit f9b3f4c)
identified the prior failure at OOM during codebook construction; this
v4 fixes the construction via chunked allocation and tests the underlying
scientific question.

## Pre-registered bands

| Outcome           | Condition                                                                 |
|-------------------|---------------------------------------------------------------------------|
| HARD_PASS         | chunked construction SUCCEEDS AND max_M_at_95_recall > N/4 * 1.5 = 6144   |
| HARD_FAIL         | chunked construction SUCCEEDS AND max_M_at_95_recall in [N/4*0.8, N/4*1.2] = [3277, 4915] |
| INCONCLUSIVE      | chunked construction OOMs (chunking design needs rework)                  |
| MIDDLE_BAND       | construction works but max_M_at_95_recall in (N/4*1.2, N/4*1.5) or no seed reached threshold |

## Calibration

Linear capacity = N/4 = 4096 stored facts at N=16384. Modern Hopfield
exponential bend would push this to N or beyond. HF band is symmetric +/- 20%
around the linear prediction. HP at 1.5x linear (6144) is the threshold
where "bend detected" is unambiguous. MIDDLE_BAND between [1.2x, 1.5x] = [4915, 6144]
indicates non-decisive scaling.

## Engineering safeguard

The script's `make_kerdock_4coset_chunked` function:
1. Allocates the full (4N, N) = (65536, 16384) result tensor (4.3 GiB).
2. Builds each coset (1.07 GiB) into the result slice in place.
3. Frees the intermediate coset before the next b-value iteration.

Peak GPU memory expected: H (1.07 GiB) + intermediate coset (1.07 GiB)
+ result (4.3 GiB) = 6.4 GiB.

Memory log written into metrics.json for every chunk allocation. If
construction OOMs, the script captures `mem_log` up to the failure point.

## Self-test

- N == 16384 (PROT-018 _n16384).
- Chunked output matches reference make_kerdock_4coset_codebook EXACTLY
  at N=1024 (`torch.allclose` with atol=1e-5).
- Verdict gates HARD_PASS / HARD_FAIL / INCONCLUSIVE all reachable.
- Smoke at N=1024 with M_sweep=[16, 32, 64] confirms retention computation.

## Timeout estimate

smoke_wall_s ~ 0.2s at N_smoke=1024. FULL: chunked construction ~60s +
4 M x 3 seeds x ~120s = 1500s. User-requested battery-class budget for
N=16384.
**timeout_s = 86400**

## Production config

N=16384, M_sweep=[N/8, N/4, N/2, N] = [2048, 4096, 8192, 16384],
seeds=[7, 17, 23], recall_threshold=0.95, n_probe=100.

## N-suffix binding

_n16384 -> production N = 16384 (PROT-018; PROT-019 timeout floor).
