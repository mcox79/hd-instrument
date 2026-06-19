# Prereg — wave14_mingo_speicher_2nd_order_mn8_v1

## Hypothesis

At M/N = 8, the substrate's 4-coset Kerdock codebook produces 2nd-order
moment fluctuations alpha_pq (Mingo-Speicher second-order freeness sense)
that **match** the iid-Gaussian rectangular reference at the same aspect
ratio. If they do not match, the substrate has a 2nd-order substrate
signature beyond what 1st-order (spectral KS) probes can detect.

## Pre-registered bands

- **HARD PASS** (`MS_2ND_ORDER_MATCH`):
  - max relative-deviation of Kerdock alpha_pq from iid-Gauss reference
    < 0.20 across (p,q) in {(2,2), (2,3), (3,3)}.

- **HARD FAIL** (`MS_2ND_ORDER_DIVERGE`):
  - max relative-deviation > 0.50 for any (p,q).

- **MIDDLE BAND** (`MS_2ND_ORDER_INCONCLUSIVE`):
  - max relative-deviation in [0.20, 0.50], OR missing data.

## Design

- N = 1024, M = 8 * N = 8192 (c = M/N = 8).
- 4 codebooks: iid_gauss (reference), srht, hadamard, kerdock.
- K = 40 independent samples per codebook (drives Cov estimate down to
  noise ~ 1/sqrt(K) ≈ 0.16).
- For each sample: SVD of A; eigenvalues lambda_i; tau_p = sum_i lambda_i^p / N_dim
  for p in {2, 3}.
- Per codebook: alpha_pq = N_dim * empirical_Cov(tau_p, tau_q) over the K samples.

Total cells = 4 codebooks * 40 samples = 160 SVDs of (8192, 1024). Each
SVD ~ 5 sec CPU; total ~ 13 min, plus build-time (Kerdock construction
amortized). ETA 30-45 min.

## Citations

- Mingo & Speicher, J. Funct. Anal. 235 (2006): "Second order freeness
  and fluctuations of random matrices".
- Capitaine, Donati-Martin (2007): rectangular Wishart second-order limits.

## Routing

- Queue: `remote_cpu_queue`.
- Timeout: 3600 s.
- Pure-CPU; no CUDA.
