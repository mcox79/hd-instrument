# Prereg: wave14_kerdock_sff_vs_gue_v1

**Date filed**: 2026-05-23
**Owner**: exp_dev (sonnet sub-agent)
**Parent drill**: `notes/research_eth_thermalization_drill_2026-05-23.md` (Anchor #1 / P1)

## Question

Does the substrate's Kerdock-Hebbian spectrum show non-GUE structure at
the Spectral Form Factor (SFF) level, consistent with the
partial-thermalization (PFK) interpretation?

PFK 2022 / Cotler et al. 2017 / Mehta: a fully ergodic chaotic system has
SFF that follows the GUE "ramp + plateau" structure (linear ramp tau/2pi
up to the Heisenberg time, then plateau at 1). Deviations from this
shape -- in particular at the dip or plateau height -- signal structure
the GUE ensemble does not capture, consistent with partial thermalization.

## Quantity

For sub-sampled Kerdock Hebbian W_alpha = (1/N) C_sub^T C_sub at alpha=M/N=1
(matches v167 central case where kappa_n GROWS with n through n=8; the full
M=4N tight-frame case makes W = 4*I exactly with a degenerate spectrum):
- Eigenvalues lambda_i = eigvalsh(W_alpha).
- Global-unfolded spectrum: lambda_i / mean_spacing.
- SFF(tau) = | sum_i exp(-i lambda_i_unfolded tau) |^2 / N.
- Compare to a matched-pair N x N GUE matrix SFF computed identically
  on the same tau grid, 1 GUE realization per seed.
- Each seed also sub-samples a fresh M=N subset of the 4N codewords so the
  Kerdock SFF varies per seed too (not single-realization).
- tau grid: 256 points in [0.05, 10 * 2 pi] on the unfolded axis (10
  Heisenberg times).

Matched-pair design: identical processing on both spectra means any
unfolding-convention artifact cancels in the relative deviation.

## Diagnostic regions

- DIP region:     tau in [0.05 T_H, 0.5 T_H]   (T_H = 2 pi unfolded)
- PLATEAU region: tau in [3 T_H, 10 T_H]

Per-seed metric:
- dip_rel_dev      = |<SFF_kerdock> - <SFF_GUE>| / <SFF_GUE> on DIP region
- plateau_rel_dev  = same on PLATEAU region

## Config (full run)

- N = 4096 (t = 6 primitive polynomial in Kerdock 4-coset)
- n_seeds = 5 (each seed = one fresh GUE realization)
- n_tau = 256 in [0.05, 10 * 2 pi]
- queue: remote_cpu_queue (numpy eigvalsh + complex exponentials)

## Pass / fail thresholds (HARD)

**HARD PASS (PFK_SFF_NON_GUE)**:
- dip_rel_dev > 0.15 OR plateau_rel_dev > 0.15 in >= 4/5 seeds.
- Interpretation: substrate spectrum has structure GUE does not capture;
  PFK partial-thermalization framing survives this anchor.

**HARD FAIL (PFK_SFF_MATCHES_GUE)**:
- dip_rel_dev <= 0.05 AND plateau_rel_dev <= 0.05 in >= 4/5 seeds.
- Interpretation: substrate is GUE-like at the SFF level; ETH
  "structured-chaos" interpretation collapses to "non-Gaussian bulk
  shape with no chaos analog." PFK framing KILLED at the SFF level.

**INCONCLUSIVE (PFK_SFF_INCONCLUSIVE)**:
- No threshold reached.

## Honest framing

- Kerdock W is positive-semidefinite (Gram matrix of bipolar codewords).
  GUE has signed eigenvalues on [-2, 2]; Kerdock-W eigenvalues are
  non-negative. We are NOT claiming the Kerdock spectrum equals GUE
  shape; the SFF comparison happens on the UNFOLDED axis where mean
  spacing is normalized to 1 in both cases, so only correlation
  structure matters.
- This is the cheapest single-shot ETH-FP diagnostic but the LEAST
  surgical test of the PFK mapping. A SFF match would not by itself
  kill the entire framing (R_6 anchor is more direct); a SFF mismatch
  is necessary but not sufficient.
- Global-rescale unfolding is coarser than full local polynomial
  unfolding. Robust enough for "deviates from GUE by 15%" but not for
  fine-grained dip-depth analysis. Pre-registered as a limitation.

Per [[feedback-no-papers-product-only]]: substrate-product positioning,
not publication.
