# Prereg: wave14_spectral_support_kerdock_v1

**Date:** 2026-05-23
**Author:** exp_dev (post-v165 CPU drill batch)
**Substrate-product axis:** substrate-physics geometric fingerprint (independent of moment-based v164a/v165 family)

## Hypothesis

The empirical spectrum of (1/N) A^T A for Kerdock 4-coset codewords has its support either CONFINED within the MP bulk edges (1±√c)² or has EIGENVALUE OUTLIERS beyond them. This is a geometric / support-level fingerprint complementary to the moment-based (v164a kappa_n, v165 S-transform) fingerprints already on the cap map.

## Predictions

H1: Substrate Kerdock spectrum is bulk-bounded (smoke result at N=1024 alpha=1 shows lam_max ≈ 2.99 vs MP edge 4.00) — would mean the substrate-novel signature is shape-of-bulk only, not outliers.

H2: Substrate Kerdock spectrum has outliers (>5% relative excursion beyond MP edge) — would mean an additional substrate-novel geometric axis.

## Vertex

- KERDOCK_SPECTRUM_BULK_BOUNDED : max relative excursion < 0.05 across all cells
- KERDOCK_SPECTRUM_HAS_OUTLIERS : ≥half of cells have lam_max > (1+√c)² · 1.05 or lam_min < (1-√c)² - 0.05·edge_width
- KERDOCK_SPECTRUM_INCONCLUSIVE : mixed

## Hard-fail thresholds

- BULK_BOUNDED claim requires max_excursion < 0.05 *all* cells (alpha ∈ {0.5, 1.0, 2.0}, 5 seeds each).
- HAS_OUTLIERS claim requires ≥2/3 alpha cells to show outlier excursion.

## Config

- N = 1024
- alphas = [0.5, 1.0, 2.0]
- n_seeds = 5
- numpy.linalg.svd (CPU); peak memory ~50 MB
- Expected wallclock: <60 seconds

## Cap_map row impact

- BULK_BOUNDED: confirms moment-only fingerprint family; no new row added; refines v164a/v165 framing.
- HAS_OUTLIERS: new substrate-physics row "Kerdock spectral-support excursion" added at 🟡 (single N).
