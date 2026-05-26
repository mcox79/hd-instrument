# Prereg — wave14_mingo_speicher_1st_order_mn8_v1

## Hypothesis

The Mingo-Speicher 2nd-order probe at M/N=8 just returned INCONCLUSIVE
(2026-05-24). Before scaling K up to resolve 2nd-order fluctuations, verify
that the 1st-order spectral moments m_1, m_2, m_3, m_4 of (1/N) A^T A match
the rectangular Marchenko-Pastur prediction at c=8 across codebooks
{iid_gauss, srht, kerdock}.

If 1st-order moments already diverge between iid_gauss (AMP-equivalent) and
kerdock (VAMP-equivalent), no amount of 2nd-order resolution will help —
the divergence is detectable at moment level.

## Pre-registered bands

- **HARD PASS** (`MS_1ST_ORDER_MATCH`):
  - iid_gauss control max_rel_dev < 0.05 across m_1..m_4.
  - Kerdock max_rel_dev < 0.05 across m_1..m_4.
  - AMP and VAMP are 1st-order equivalent at this aspect ratio.

- **HARD FAIL** (`MS_1ST_ORDER_DIVERGE`):
  - iid_gauss control max_rel_dev < 0.10 (control still OK).
  - Kerdock max_rel_dev > 0.20 (clear divergence).

- **MIDDLE BAND** (`MS_1ST_ORDER_INCONCLUSIVE`):
  - Anything between, or control fails too.

## Design

- N = 512, M = 8 * N = 4096 (c = 8).
- 3 codebooks: iid_gauss (AMP-equiv), srht (VAMP-equiv variant), kerdock (substrate).
- 20 seeds per codebook (gives 1/sqrt(20) ≈ 22% noise on 1st moment; mean
  across seeds drives this down to ~5%).
- Per cell: SVD; eigenvalues; m_p = mean(eig^p) for p in 1..4.
- Compare empirical means to rect-MP closed-form moments at c=8
  (Narayanan formula m_p = sum_{k=0..p-1} (1/(k+1)) C(p,k) C(p-1,k) c^{k+1}):
    m_1 = 8.0
    m_2 = 72.0
    m_3 = 712.0
    m_4 = 7560.0

ETA: ~30-45 min CPU. 60 SVDs of (4096, 512).

## Citations

- Mingo & Speicher, J. Funct. Anal. 235 (2006).
- Capitaine, Donati-Martin (2007): rectangular Wishart limits.
- Bai-Silverstein 2010, Theorem 3.6.
- Parent: `wave14_mingo_speicher_2nd_order_mn8_v1` (INCONCLUSIVE 2026-05-24).

## Routing

- Queue: `remote_cpu_queue`.
- Timeout: 3600 s.
- Pure-CPU numpy (no CUDA).
