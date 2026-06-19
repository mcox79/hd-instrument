# Prereg — wave14_rect_free_conv_mn8_v1

## Hypothesis

At M/N = 8 (the substrate rectangular operating point), the substrate's
4-coset Kerdock codebook produces an eigenvalue distribution for (1/N) A^T A
that **matches** the rectangular Marchenko-Pastur (rect-MP) density predicted
by Benaych-Georges rectangular free convolution at aspect ratio c = M/N = 8.

If iid-Gauss control matches rect-MP(c=8) but Kerdock does not, the
substrate carries higher rectangular free cumulants beyond what rect-free
probability predicts — this is the formal mechanism for any
substrate-specific anomaly in the M/N=8 regime.

## Pre-registered bands

- **HARD PASS** (`RECT_FREE_CONV_MP_MATCH`):
  - iid-Gauss control KS to rect-MP(c=8) < 0.05 (sanity).
  - Kerdock KS to rect-MP(c=8) < 0.10.
  - Max Kerdock |kappa_n / c - 1| < 0.15 for n in {2,3,4}.

- **HARD FAIL** (`RECT_FREE_CONV_DIVERGE`):
  - iid-Gauss control KS < 0.05 (control still OK).
  - AND (Kerdock KS > 0.20 OR max Kerdock kappa-dev > 0.50).

- **MIDDLE BAND** (`RECT_FREE_CONV_INCONCLUSIVE`):
  - Anything between the bands, OR iid-Gauss control KS > 0.05
    (in which case the substrate test cannot be cleanly interpreted).

## Design

- N in {256, 512, 1024}, M = 8 * N (so c = 8 throughout).
- 5 codebooks: iid_gauss (control), srht, hadamard, rm_1_m, kerdock (substrate).
- 5 seeds per (N, codebook) cell.
- Per cell: SVD of A; eigenvalues of A^T A; KS distance to rect-MP(c=8);
  spectral moments m_1..m_4; free cumulants kappa_1..kappa_4; deviation
  |kappa_n / c - 1|.

Total cells = 3 N * 5 codebooks * 5 seeds = 75 SVDs. At N=1024, M=8192 the
SVD on (M, N) is feasible CPU (~5-10 sec per cell). ETA 30-45 min total.

## Citations

- Benaych-Georges, Adv. Math. 224 (2010): "Rectangular random matrices,
  related convolution"; introduces rect-free convolution mu ⊞_lambda nu at
  aspect ratio lambda.
- Marchenko & Pastur 1967.
- Bai-Silverstein 2010, Theorem 3.6 (general c MP density).
- Nica-Speicher 2006 (moment-free-cumulant inversion).

## Routing

- Queue: `remote_cpu_queue`.
- Timeout: 3600 s.
- Pure-CPU: SVD on (M, N) with M up to 8192, no CUDA needed.
