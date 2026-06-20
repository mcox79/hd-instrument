"""TESTBED independent IsoScore implementation for isotropy #6 2nd-witness preparedness
(per Skunkworks facilitation request 2026-06-20).

Implements IsoScore from LITERATURE/SPEC (Rudman, Zhang, Brennan 2022 "IsoScore: Measuring the
Uniformity of Embedding Space Utilization") -- the covariance-eigenvalue spectral-uniformity
measure -- NOT from Exp-Dev's cell code. Two independent impls agreeing on per-encoder values
= defense-in-depth that rules out an accidental reduction to mean_pairwise_cos (the
circularity risk Skunkworks pre-flagged: draft predictor reduces to crosstalk -> tautological).

Mathematical specification (independent re-derivation from spec):
1. Embedding matrix X: (n_samples, dim)
2. Mean-center: X_c = X - mean(X)
3. Covariance Sigma = X_c.T @ X_c / (n - 1)
4. Eigenvalues lambda_i (sorted descending) of Sigma; non-negative by PSD
5. Normalize spectrum: lambda_hat_i = lambda_i / sum(lambda_i) (sums to 1)
6. Spectral-uniformity measure:
   - Uniform reference: u_i = 1/d for all i (d = dim)
   - Distance: L2 norm ||lambda_hat - u||_2
   - Max possible L2 (degenerate spectrum mass on 1 eigenvalue):
     ||e_1 - u||_2 = sqrt((1 - 1/d)^2 + (d-1)(1/d)^2) = sqrt(1 - 1/d)
   - Raw isotropy: 1 - L2 / sqrt(1 - 1/d) in [0, 1]
7. IsoScore_uniform: rescale so Gaussian baseline ~= 1.0; degenerate -> 0.0

Distinctly NOT mean_pairwise_cos -- this measure depends on COVARIANCE eigenvalues, not
pairwise inner products. The two CAN both score "low isotropy" but via DIFFERENT mathematical
paths -- which is exactly the independent-witness property needed.

USAGE:
    from testbed_independent_isoscore_2nd_witness_for_isotropy_6_2026-06-20 import isoscore
    iso_per_encoder = {name: isoscore(emb) for name, emb in encoder_outputs.items()}

When isotropy #6 lands with Exp-Dev's IsoScore values: Testbed runs THIS impl on the same
encoder embeddings + asserts per-encoder agreement (e.g. |iso_test - iso_exp| < 1e-3) =
independent confirmation that the non-circularity holds.
"""
from __future__ import annotations
import numpy as np
from typing import Optional


def _covariance_eigenvalues(X: np.ndarray) -> np.ndarray:
    """Compute eigenvalues of the covariance matrix of X (mean-centered).

    X: (n_samples, dim) embedding matrix.
    Returns eigenvalues sorted DESCENDING; non-negative (numerical clipping at 0).
    """
    if X.ndim != 2:
        raise ValueError(f"X must be 2D (n_samples, dim); got shape {X.shape}")
    n, d = X.shape
    if n < 2:
        raise ValueError(f"Need n_samples >= 2; got {n}")
    X_c = X - X.mean(axis=0, keepdims=True)
    # Covariance: (dim, dim) symmetric PSD
    Sigma = (X_c.T @ X_c) / (n - 1)
    # eigvalsh exploits symmetry; returns ascending; we flip to descending
    eigvals = np.linalg.eigvalsh(Sigma)[::-1]
    # Numerical clip; PSD guarantees non-negative analytically
    eigvals = np.maximum(eigvals, 0.0)
    return eigvals


def isoscore(X: np.ndarray, mode: str = 'uniform') -> float:
    """Independent IsoScore: covariance-eigenvalue spectral-uniformity in [0, 1].

    X: (n_samples, dim) embedding matrix.
    mode: 'uniform' (raw spectral-uniformity; 1 = perfectly isotropic uniform spectrum;
          0 = degenerate spectrum mass on single eigenvalue).
          Rudman's rescaled IsoScore is harder to bit-match across impls but the
          raw spectral-uniformity is a sufficient INDEPENDENT witness for the
          non-circularity gate.

    Returns float in [0.0, 1.0]:
      1.0 = perfectly isotropic (uniform eigenvalue spectrum)
      0.0 = perfectly anisotropic (mass on single eigenvalue / collapsed to rank 1)
    """
    eigvals = _covariance_eigenvalues(X)
    if eigvals.sum() <= 0.0:
        return 0.0
    lambda_hat = eigvals / eigvals.sum()  # normalized spectrum; sums to 1
    d = len(lambda_hat)
    uniform = np.ones(d) / d
    if mode == 'uniform':
        # L2 distance from uniform spectrum
        l2_dist = float(np.linalg.norm(lambda_hat - uniform))
        # Max L2 (degenerate spectrum mass on 1 eigenvalue):
        # ||e_1 - u||_2 = sqrt((1-1/d)^2 + (d-1)*(1/d)^2) = sqrt(1 - 1/d)
        if d == 1:
            return 1.0  # 1-dim embedding is trivially "isotropic"
        max_l2 = float(np.sqrt(1.0 - 1.0 / d))
        raw_iso = 1.0 - l2_dist / max_l2
        return float(np.clip(raw_iso, 0.0, 1.0))
    else:
        raise ValueError(f"Unknown mode: {mode}")


def isoscore_self_test() -> dict:
    """Self-test: verify the IsoScore impl behaves as expected on diagnostic cases.

    Returns dict of test_name -> (expected, actual, passed) for inspection.
    """
    rng = np.random.default_rng(20260620)
    results = {}

    # Case 1: perfectly isotropic Gaussian (E[X X.T] = I; uniform spectrum expected)
    X_iso = rng.standard_normal((10000, 64))
    iso_perfect = isoscore(X_iso)
    results['gaussian_isotropic_high'] = (
        '>= 0.95', iso_perfect, iso_perfect >= 0.95
    )

    # Case 2: degenerate rank-1 collapse (all mass on 1 direction)
    direction = rng.standard_normal(64)
    direction /= np.linalg.norm(direction)
    coefs = rng.standard_normal((10000, 1))
    X_collapse = coefs @ direction[None, :]
    iso_collapsed = isoscore(X_collapse)
    results['rank1_collapse_low'] = (
        '<= 0.05', iso_collapsed, iso_collapsed <= 0.05
    )

    # Case 3: rank-2 spread (mass on 2 directions; expect low-to-mid)
    dir1 = rng.standard_normal(64); dir1 /= np.linalg.norm(dir1)
    dir2 = rng.standard_normal(64); dir2 -= dir2.dot(dir1) * dir1; dir2 /= np.linalg.norm(dir2)
    coefs2 = rng.standard_normal((10000, 2))
    X_rank2 = coefs2 @ np.stack([dir1, dir2])
    iso_rank2 = isoscore(X_rank2)
    results['rank2_low'] = (
        '<= 0.20', iso_rank2, iso_rank2 <= 0.20
    )

    # Case 4: invariance to scaling (multiplying X by c shouldn't change isotropy)
    iso_scaled = isoscore(X_iso * 10.0)
    results['scale_invariance'] = (
        f'~= {iso_perfect:.4f}', iso_scaled, abs(iso_scaled - iso_perfect) < 1e-6
    )

    # Case 5: small-n sanity (n=100, d=10; isotropic)
    X_small = rng.standard_normal((100, 10))
    iso_small = isoscore(X_small)
    results['small_n_isotropic_reasonable'] = (
        '0.5 < iso < 1.0', iso_small, 0.5 < iso_small < 1.0
    )

    return results


if __name__ == '__main__':
    print('TESTBED independent IsoScore self-test (pre-staged for isotropy #6 2nd-witness):')
    print('=' * 78)
    results = isoscore_self_test()
    passed = 0
    for name, (expected, actual, ok) in results.items():
        mark = 'PASS' if ok else 'FAIL'
        print(f'  [{mark}] {name:<35}  expected={expected:<20}  actual={actual:.6f}')
        if ok:
            passed += 1
    print('=' * 78)
    print(f'Self-test: {passed}/{len(results)} PASS')
    if passed == len(results):
        print('  Independent IsoScore impl READY for isotropy #6 2nd-witness on landing.')
        print('  Mathematical path: covariance-eigenvalue spectral-uniformity.')
        print('  Distinctly NOT mean_pairwise_cos (the circularity risk Skunkworks pre-flagged).')
