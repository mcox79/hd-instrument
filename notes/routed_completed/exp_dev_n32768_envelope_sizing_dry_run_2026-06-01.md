# N=32768 Envelope Sizing Dry-Run
# Filed: 2026-06-01
# Status: SIZING ONLY — no experiment queued

## Purpose

Estimate memory footprint, compute wall-time, and feasibility threshold for experiments
at N=32768 before committing to a full-scale anchor.

---

## 1. Memory Footprint

### W matrix (full dense Hebbian)

    dtype: float32 (4 bytes)
    W shape: N x N = 32768 x 32768
    W_bytes = 32768^2 * 4 = 4,294,967,296 bytes = 4.0 GiB

    Verdict: fits on 16 GiB GPU (e.g. A10G, A100-40). Tight on A10G with overhead.
    Recommended: A100-40 or A100-80 for any W-dense anchor at N=32768.

### Per-seed overhead (M patterns, N-dimensional)

    Typical envelope: alpha = M/N in [0.05, 0.25]
    M_min = 0.05 * 32768 = 1638
    M_max = 0.25 * 32768 = 8192

    Pattern matrix X shape: M x N (float32)
    X_bytes at M=8192: 8192 * 32768 * 4 = 1,073,741,824 bytes = 1.0 GiB

    Total peak (W + X + activations): ~5.5 GiB at alpha=0.25

### Eigenvalue computation (spectral drills)

    np.linalg.eigvalsh(W) at N=32768:
    - Internally uses LAPACK dsyevd
    - Workspace: O(N^2) = 4 GiB already for W
    - Wall-time estimate: ~120-300s on CPU (single-threaded), ~5-15s on GPU with cuBLAS

    Verdict: spectral drills at N=32768 REQUIRE GPU or very long CPU timeout (>3600s).

---

## 2. Compute Wall-Time Estimates

### Reference anchor: N=4096, smoke wall ~3s, FULL wall ~60-300s (5 seeds)

Scaling law: wall ~ N^1.5 for matrix multiply dominated kernels (W construction + retrieval)
             wall ~ N^2.0 for eigvalsh (O(N^3) LAPACK)

### N=32768 vs N=4096 ratio: 32768/4096 = 8x

Retrieve/write kernel (N^1.5 scaling):
    wall_32768 = wall_4096 * (8)^1.5 = wall_4096 * 22.6x
    At FULL 300s for N=4096: 300 * 22.6 = 6780s ~ 1.9h per run

Eigvalsh kernel (N^3 scaling, LAPACK):
    wall_32768 = wall_4096 * (8)^3 = wall_4096 * 512x
    Eigvalsh at N=4096 ~0.5s -> at N=32768 ~256s = 4.3 min per eigvalsh call
    If called per seed per M point: 5 seeds * 5 M points * 256s = 6400s per run

### PROT-019 timeout floor for _n32768: 21600s (6h) MINIMUM

Recommended timeout: 28800s (8h) for any N=32768 FULL anchor.

---

## 3. Feasibility Matrix

| Kernel class        | N=32768 GPU? | N=32768 CPU? | Notes                               |
|---------------------|-------------|-------------|-------------------------------------|
| W construction      | YES         | YES (<60s)  | Straightforward                     |
| Retrieve sweep      | YES         | MARGINAL    | 2h+ per FULL run on CPU             |
| Eigvalsh (spectral) | YES (GPU)   | NO (>3h)    | Must be GPU-only at N=32768         |
| SVD                 | YES (GPU)   | NO          | O(N^3) intractable on CPU           |
| Block-sparse W      | YES         | YES         | Sparse ops; memory sub-linear in M  |
| KS-distance         | YES         | YES         | Trivial once eigvals computed       |

---

## 4. Recommended First N=32768 Anchor Profile

Anchor name template: `<mechanism>_v1_n32768`
Queue: overnight_queue (GPU required)
Seeds: 5 (standard)
Timeout: 28800s

Pre-conditions before shipping N=32768 anchor:
1. Corresponding N=4096 anchor HARD_PASS confirmed (not just smoke)
2. GPU instance available with >=16 GiB VRAM (A100 preferred)
3. Script passes `_instrumentation_selftest()` at N_smoke=512, N_smoke*4=2048 locally

Priority candidates from current cap_map:
- SKAH-M saddle-hierarchy scaling law (path_d family) — natural N extension
- Free-probability spectral drift (B1 family) — needs GPU eigvalsh
- Multi-tenant isolation at production scale (R2.1 family) — W stays sparse

---

## 5. Open Questions for Strategy

Q1: Does W need to stay in float32, or is bfloat16 acceptable at N=32768 for retrieve ops?
    - bfloat16 W: 2 GiB instead of 4 GiB; saves ~1.5 GiB peak; fidelity impact unknown
    - Flag for R2 design-space sweep

Q2: Block-sparse W at N=32768: K_block=64 theoretical nz_frac = M*K^2/N^2
    - At M=1000 K=64: nz_frac = 1000*4096/32768^2 = 0.0038 (sublinear in M)
    - Very feasible on CPU even at N=32768 — sparse_block_edit_isolation next iteration

Q3: SVD-based DR at N=32768: O(N^3) cost means random-projection sketch is mandatory
    - dr_merkle_randproj already uses random-projection; scales fine

---

## 6. Hard Budget Constraints

RAM budget for remote host (marsh@home): 32 GiB total
    - W (float32, dense): 4 GiB
    - Reserve for OS + other processes: 4 GiB
    - Available for X + activations + temporaries: 24 GiB
    - Headroom is sufficient for alpha <= 0.25 with 5 seeds sequential

GPU budget (Lambda A100-80 when available):
    - 80 GiB VRAM: fits W + X + gradients comfortably at alpha=0.25
    - No concern

---

## Conclusion

N=32768 is FEASIBLE for GPU anchors. CPU-only is marginal for retrieve-dominated
kernels and infeasible for spectral (eigvalsh) kernels. Recommended path:

1. Wait for N=4096 FULL results from current CPU queue batch
2. Select 1-2 strongest N=4096 HARD_PASS anchors
3. Scale to N=16384 as intermediate step (already running path_d_k2)
4. File N=32768 anchor only after N=16384 HARD_PASS confirmation

Acted-on 2026-06-01: N=32768 feasibility confirmed for A100-80 GPU; recommended staged escalation N=4096->N=16384->N=32768; no immediate action; deferred per readiness criteria
