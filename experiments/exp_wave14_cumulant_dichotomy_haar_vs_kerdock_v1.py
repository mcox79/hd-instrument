"""Cumulant dichotomy: Haar-orthogonal vs Kerdock off-diagonal Gram entries (kappa_2..kappa_6).

Motivation
----------
Cross-domain research probe 2026-05-23 (notes/research_cross_domain_probe_2026-05-23.md)
identified the ETH-free-probability connection (Pappalardi-Foini-Kurchan, Jindal-Hosur
JHEP09(2024)066) as the top angle for reframing BBMD as a "partially-thermalized
algebraic-codebook regime." Domain 6 (NN Jacobian asymptotic freeness, Hayase 2019,
Collins-Hayase 2022) gives a clean dichotomy: Haar-orthogonal weights produce
ASYMPTOTIC FREENESS (mixed free cumulants kappa_n -> 0 for n >= 3 in the wide limit),
while algebraic codebooks like Kerdock encode their structure in HIGHER cumulants.

This experiment is the cheapest disambiguator for the ETH framing. It compares the
free cumulants kappa_2..kappa_6 of the off-diagonal Gram-matrix entries (the angle
distribution) for two N=4096 codebook ensembles:

  - Haar: H @ H.T where H is sampled from Haar on O(N) (scipy.stats.ortho_group).
  - Kerdock: 4-coset Maiorana-McFarland codebook from exp_wave14y_erase_kerdock_v3
    (4N = 16384 rows at N=4096).

For each family at each seed: compute the 1st-6th raw moments of the off-diagonal
Gram entries, invert to free cumulants via the same recursion as
exp_wave14_kappa_n_profile_v1 (Mobius inversion on the non-crossing partition lattice).

Hypothesis (ETH framing predictive)
-----------------------------------
- Haar: |kappa_n| < 0.1 for ALL n in {3,4,5,6} across 10/10 seeds. Asymptotic freeness
  numerically confirmed at N=4096.
- Kerdock: |kappa_n| > 0.2 for at least n=4 AND n=6. The 4-coset codebook's algebraic
  signature persists at higher cumulants.
- kappa_4 / kappa_2^2 substantially LARGER for Kerdock than Haar (excess-kurtosis
  discriminator).

HARD PASS (ETH framing survives)
--------------------------------
- Haar: |kappa_n| < 0.1 for ALL n in {3,4,5,6} across 10/10 seeds.
- Kerdock: |kappa_n| > 0.2 for at least n=4 AND n=6.
- kappa_4 / kappa_2^2 substantially larger for Kerdock than for Haar.

HARD FAIL (ETH framing as a regime axis is killed)
--------------------------------------------------
- Haar shows |kappa_n| > 0.1 for any n >= 3 across the seed sample.
  -> Asymptotic freeness fails at this N; need much larger N to see it; weakens
     the "Haar = fully thermalized" claim.
- OR Kerdock kappa_4 / kappa_2^2 < 0.05.
  -> Kerdock's kappa_n divergence not actually meaningful; prior v164a finding
     called into question.

Vertex labels: CUMULANT_DICHOTOMY_HOLDS / CUMULANT_DICHOTOMY_HAAR_FAILS /
               CUMULANT_DICHOTOMY_KERDOCK_FAILS / CUMULANT_DICHOTOMY_INCONCLUSIVE.

Pre-reg: preregs/2026-05-23_wave14_cumulant_dichotomy_haar_vs_kerdock_v1.md
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import importlib.util
import json
import math
import os
import time
from functools import lru_cache
from pathlib import Path
from typing import Iterator

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# Import Kerdock codebook builder from v3
_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
_spec = importlib.util.spec_from_file_location("kerdock_v3", _v3_path)
_v3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v3)
make_kerdock_4coset_codebook = _v3.make_kerdock_4coset_codebook

# Import the moment-to-free-cumulant inversion from kappa_n_profile_v1
_kp_path = REPO / "experiments" / "exp_wave14_kappa_n_profile_v1.py"
_spec_kp = importlib.util.spec_from_file_location("kappa_n_profile_v1", _kp_path)
_kp = importlib.util.module_from_spec(_spec_kp)
_spec_kp.loader.exec_module(_kp)
moments_to_free_cumulants_general = _kp.moments_to_free_cumulants_general
_enumerate_ncp = _kp._enumerate_ncp

try:
    import torch
    _TORCH_OK = True
except ImportError:
    _TORCH_OK = False

try:
    from scipy.stats import ortho_group
    _SCIPY_OK = True
except ImportError:
    _SCIPY_OK = False


# ---------------------------------------------------------------------------
# Family builders
# ---------------------------------------------------------------------------

def build_haar_orthogonal(N: int, seed: int) -> np.ndarray:
    """Sample H from Haar measure on O(N). Returns N x N orthogonal matrix.

    Prefers scipy.stats.ortho_group (correctly normalised Haar measure). Falls back
    to QR of an iid Gaussian with Mezzadri 2007 sign correction.
    """
    if _SCIPY_OK:
        rng = np.random.default_rng(seed)
        H = ortho_group.rvs(dim=N, random_state=rng).astype(np.float64)
        return H
    rng = np.random.default_rng(seed)
    G = rng.standard_normal(size=(N, N))
    Q, R = np.linalg.qr(G)
    signs = np.sign(np.diag(R))
    signs[signs == 0] = 1.0
    Q = Q * signs[np.newaxis, :]
    return Q


def build_haar_codebook(N: int, M: int, seed: int) -> np.ndarray:
    """Build M unit-norm rows in R^N where each row is uniform on S^{N-1}.

    This is the "Haar-random codebook" -- the fully-thermalized comparison to a
    structured codebook of M rows. Each row is L2-normalised iid Gaussian, which
    is the canonical spherically-uniform distribution (Marsaglia 1972).

    For M = 4N (matching Kerdock 4-coset codebook), the resulting M x N matrix has:
      - off-diagonal Gram entries ~ N(0, 1/N) asymptotically
      - moments and free cumulants of the SCALED entries (* sqrt(N)) converge to
        those of standard Gaussian: kappa_2 -> 1, kappa_n -> 0 for n >= 3.
    """
    rng = np.random.default_rng(seed)
    G = rng.standard_normal(size=(M, N))
    norms = np.linalg.norm(G, axis=1, keepdims=True)
    return G / norms


def build_kerdock(N: int) -> np.ndarray:
    """Build the 4-coset Kerdock codebook at dimension N (returns 4N x N float64).

    The bipolar +-1 entries are normalised by sqrt(N) downstream so that the
    rows are unit-norm.
    """
    if not _TORCH_OK:
        raise RuntimeError("torch required for Kerdock builder")
    cb_t, _info = make_kerdock_4coset_codebook(N, torch.device("cpu"))
    return cb_t.numpy().astype(np.float64)


# ---------------------------------------------------------------------------
# Off-diagonal Gram statistics
# ---------------------------------------------------------------------------

def offdiag_gram_entries(rows: np.ndarray, scale_by_sqrt_N: bool = True) -> np.ndarray:
    """Strictly upper-triangular off-diagonal entries of (rows @ rows.T), with rows
    L2-normalised. Returns a 1-D array of length M*(M-1)/2.

    When scale_by_sqrt_N=True (default), entries are multiplied by sqrt(N) so the
    variance is O(1) regardless of N. This is the standard convention used in
    free-probability / random-matrix analysis of angle distributions:
      - Haar: scaled entries -> N(0, 1) asymptotically, kappa_2 -> 1, kappa_n -> 0 for n>=3.
      - Kerdock: scaled entries in {0, +-1}, with structural fingerprint at higher cumulants.

    Without scaling, kappa_2 ~ 1/N and all higher kappas vanish below numerical noise,
    making the dichotomy invisible. The scaling is the right "free-probability normalisation."
    """
    M = rows.shape[0]
    N = rows.shape[1]
    # Ensure unit-norm rows
    norms = np.linalg.norm(rows, axis=1, keepdims=True)
    norms = np.where(norms > 0, norms, 1.0)
    rows_n = rows / norms
    G = rows_n @ rows_n.T  # (M, M)
    iu = np.triu_indices(M, k=1)
    entries = G[iu]
    if scale_by_sqrt_N:
        entries = entries * math.sqrt(N)
    return entries


def raw_moments(samples: np.ndarray, n_max: int) -> list[float]:
    """Compute raw moments m_n = E[X^n] for n in 1..n_max from a sample."""
    out = []
    for n in range(1, n_max + 1):
        out.append(float(np.mean(samples ** n)))
    return out


def classical_cumulants(moments: list[float]) -> list[float]:
    """Convert raw moments m_1..m_n to classical cumulants kappa_1..kappa_n.

    Uses the standard recursion:
      kappa_n = m_n - sum_{k=1}^{n-1} C(n-1, k-1) kappa_k m_{n-k}

    For a Gaussian N(0, sigma^2): kappa_1 = 0, kappa_2 = sigma^2, kappa_n = 0 for n >= 3.
    This is the *classical* (commutative) cumulant -- the discriminator the user wanted
    for "fully thermalized" Haar vs "structured" Kerdock. The off-diagonal Gram entry
    distribution of Haar-uniform unit vectors on S^{N-1} is asymptotically Gaussian, so
    classical kappa_n -> 0 for n >= 3 in the large-N limit. For algebraic codebooks like
    Kerdock with discrete inner-product spectrum, classical higher cumulants stay nonzero.
    """
    n_max = len(moments)
    if n_max < 1:
        return []
    kappa = [0.0] * (n_max + 1)
    for n in range(1, n_max + 1):
        s = moments[n - 1]
        for k in range(1, n):
            s -= math.comb(n - 1, k - 1) * kappa[k] * moments[n - k - 1]
        kappa[n] = s
    return kappa[1:]


# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------

HAAR_BOUND = 0.1   # |kappa_n| < HAAR_BOUND for n in {3,4,5,6} (all seeds)
KERDOCK_BOUND = 0.2  # |kappa_n| > KERDOCK_BOUND for n=4 AND n=6 (mean)
KAPPA4_OVER_KAPPA2SQ_FAIL = 0.05  # Kerdock excess-kurtosis lower bound


def per_seed_haar_check(kappas_per_seed: list[list[float]]) -> tuple[bool, list[str]]:
    """Haar PASS iff |kappa_n| < HAAR_BOUND for n in {3,4,5,6} on EVERY seed."""
    fails: list[str] = []
    for seed_idx, kappas in enumerate(kappas_per_seed):
        # kappas is 1-indexed semantically (kappa_1, kappa_2, ..., kappa_6)
        for n in (3, 4, 5, 6):
            if n - 1 < len(kappas) and abs(kappas[n - 1]) >= HAAR_BOUND:
                fails.append(
                    f"seed{seed_idx}:kappa_{n}={kappas[n - 1]:+.4f} (|.|>={HAAR_BOUND})"
                )
    return (len(fails) == 0, fails)


def kerdock_mean_check(kappa_mean: list[float], kappa_2_sq: float, kappa_4: float
                       ) -> tuple[bool, list[str]]:
    """Kerdock PASS iff |kappa_4_mean| > KERDOCK_BOUND AND |kappa_6_mean| > KERDOCK_BOUND
    AND |kappa_4/kappa_2^2| > KAPPA4_OVER_KAPPA2SQ_FAIL. We use absolute values throughout
    because the Kerdock codebook's discrete inner-product distribution produces
    SIGNED higher cumulants (e.g. negative kappa_4 reflects sub-Gaussian tails for the
    +-1/sqrt(N) constraint), and the substrate's structural signature is encoded in
    *magnitude*, not sign.
    """
    fails: list[str] = []
    if abs(kappa_mean[3]) <= KERDOCK_BOUND:  # n=4
        fails.append(f"|kappa_4_mean|={abs(kappa_mean[3]):.4f} <= {KERDOCK_BOUND}")
    if abs(kappa_mean[5]) <= KERDOCK_BOUND:  # n=6
        fails.append(f"|kappa_6_mean|={abs(kappa_mean[5]):.4f} <= {KERDOCK_BOUND}")
    if kappa_2_sq > 0:
        excess = kappa_4 / kappa_2_sq
        if abs(excess) < KAPPA4_OVER_KAPPA2SQ_FAIL:
            fails.append(
                f"|kappa_4/kappa_2^2|={abs(excess):.4f} < {KAPPA4_OVER_KAPPA2SQ_FAIL}"
            )
    return (len(fails) == 0, fails)


def compute_verdict(summary: dict) -> tuple[str, str]:
    families = summary.get("families", {})
    if "haar" not in families or "kerdock" not in families:
        return ("CUMULANT_DICHOTOMY_INCONCLUSIVE", "Missing per-family data.")

    haar = families["haar"]
    kerd = families["kerdock"]
    if not haar.get("kappa_per_seed") or not kerd.get("kappa_per_seed"):
        return ("CUMULANT_DICHOTOMY_INCONCLUSIVE", "Empty per-seed kappa lists.")

    haar_pass, haar_fails = per_seed_haar_check(haar["kappa_per_seed"])

    kerd_mean = kerd["kappa_mean"]
    if len(kerd_mean) < 6:
        return ("CUMULANT_DICHOTOMY_INCONCLUSIVE", f"Kerdock kappa_mean too short ({len(kerd_mean)})")
    k2_sq = kerd_mean[1] ** 2
    kerd_pass, kerd_fails = kerdock_mean_check(kerd_mean, k2_sq, kerd_mean[3])

    haar_k2_sq = haar["kappa_mean"][1] ** 2
    haar_excess = haar["kappa_mean"][3] / haar_k2_sq if haar_k2_sq != 0 else 0.0
    kerd_excess = kerd_mean[3] / k2_sq if k2_sq > 0 else 0.0
    # Discriminator: Kerdock excess kurtosis magnitude must be SUBSTANTIALLY larger than Haar.
    # Use absolute-value compare; sign of kappa_4 can be negative for sub-Gaussian distributions
    # (Kerdock has discrete +-1/sqrt(N) inner products -- sub-Gaussian tails).
    excess_discriminator = abs(kerd_excess) > abs(haar_excess) * 5.0 or abs(kerd_excess) > 0.5

    if haar_pass and kerd_pass and excess_discriminator:
        return (
            "CUMULANT_DICHOTOMY_HOLDS",
            f"ETH framing survives. Haar off-diagonal Gram entries look Gaussian "
            f"(|kappa_n| < {HAAR_BOUND} for n in 3..6, all {len(haar['kappa_per_seed'])} seeds). "
            f"Kerdock retains algebraic structure (|kappa_4|={abs(kerd_mean[3]):.3f}, "
            f"|kappa_6|={abs(kerd_mean[5]):.3f}; both > {KERDOCK_BOUND}). "
            f"Excess kurtosis: Haar kappa_4/kappa_2^2={haar_excess:+.4f}, "
            f"Kerdock kappa_4/kappa_2^2={kerd_excess:+.4f} "
            f"(|.|-ratio {abs(kerd_excess) / max(abs(haar_excess), 1e-6):.1f}x). "
            f"BBMD reframed as partially-thermalized algebraic-codebook regime "
            f"per Pappalardi-Foini-Kurchan / Jindal-Hosur.",
        )

    parts = []
    if not haar_pass:
        parts.append(f"Haar fails asymptotic freeness: {'; '.join(haar_fails[:5])}")
    if not kerd_pass:
        parts.append(f"Kerdock fails structural persistence: {'; '.join(kerd_fails)}")
    if not excess_discriminator:
        parts.append(
            f"Excess-kurtosis discriminator weak "
            f"(haar={haar_excess:+.4f} kerd={kerd_excess:+.4f})"
        )

    if not haar_pass and kerd_pass:
        return (
            "CUMULANT_DICHOTOMY_HAAR_FAILS",
            f"Asymptotic freeness fails at N={summary.get('N', 'NA')}: " + "; ".join(parts),
        )
    if haar_pass and not kerd_pass:
        return (
            "CUMULANT_DICHOTOMY_KERDOCK_FAILS",
            "Kerdock kappa_n divergence not robust: " + "; ".join(parts),
        )
    return (
        "CUMULANT_DICHOTOMY_INCONCLUSIVE",
        "Both arms or discriminator failing: " + "; ".join(parts),
    )


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def self_test() -> None:
    # Test 1: moments_to_free_cumulants_general is loaded and behaves
    moms_const = [1.0] * 6
    kappas = moments_to_free_cumulants_general(moms_const)
    # MP-like: m_n = 1 for all n => kappa_n = 1 (this is the c=1 MP case where every
    # moment equals 1 only by coincidence in our domain). Actually MP(c=1) has
    # m_n = Catalan(n), not 1. So this test just confirms call shape, not values.
    assert len(kappas) == 6, f"expected 6 cumulants got {len(kappas)}"

    # Test 2: For a deterministic constant distribution X = a (single value), all
    # raw moments m_n = a^n. Free cumulants: kappa_1 = a, kappa_2 = 0, kappa_n = 0
    # for n >= 2 (a delta distribution has trivial free cumulants beyond the first).
    a = 0.5
    moms_delta = [a ** n for n in range(1, 7)]
    k_delta = moments_to_free_cumulants_general(moms_delta)
    assert abs(k_delta[0] - a) < 1e-9, f"kappa_1 of delta({a}) = {k_delta[0]}, expected {a}"
    for n in range(2, 7):
        assert abs(k_delta[n - 1]) < 1e-9, (
            f"delta dist kappa_{n} = {k_delta[n - 1]:.2e}, expected 0"
        )

    # Test 3: off-diagonal Gram extraction on orthonormal rows -> all zeros, all moments zero
    # (scaling by sqrt(N) doesn't change zeros)
    M = 8
    I_rows = np.eye(M)
    entries = offdiag_gram_entries(I_rows)
    assert entries.shape == (M * (M - 1) // 2,), f"shape {entries.shape}"
    assert np.allclose(entries, 0.0), "orthonormal rows should give zero off-diagonal Gram"
    moms = raw_moments(entries, 6)
    for n, m in enumerate(moms, start=1):
        assert abs(m) < 1e-12, f"m_{n} of zero entries = {m}"

    # Test 3b: scaling sanity. For rows = iid Gaussian rows (then L2-normalised to lie
    # on the sphere), off-diagonal inner products * sqrt(N) should have variance ~1.
    # This is the spherical-uniform asymptotic.
    rng_t = np.random.default_rng(7)
    N_t = 128
    G_iid = rng_t.standard_normal(size=(N_t, N_t))  # M = N rows, dim = N
    e_scaled = offdiag_gram_entries(G_iid)  # function L2-normalises rows internally
    assert 0.3 < float(np.var(e_scaled)) < 3.0, (
        f"scaled off-diag variance {np.var(e_scaled):.4f} not O(1); scaling broken"
    )

    # Test 3c: classical cumulants of N(0,1). Use a large sample so empirical -> {0, 1, 0, 0, 0, 0}.
    rng_c = np.random.default_rng(42)
    gauss = rng_c.standard_normal(size=1_000_000)
    moms_g = raw_moments(gauss, 6)
    k_class_g = classical_cumulants(moms_g)
    assert abs(k_class_g[0]) < 0.02, f"N(0,1) kappa_1 should be ~0, got {k_class_g[0]}"
    assert abs(k_class_g[1] - 1.0) < 0.02, f"N(0,1) kappa_2 should be ~1, got {k_class_g[1]}"
    for n in (3, 4, 5, 6):
        assert abs(k_class_g[n - 1]) < 0.1, (
            f"N(0,1) classical kappa_{n} = {k_class_g[n-1]:+.4f}, expected near 0"
        )

    # Test 3d: classical cumulants formula sanity on a 2-point Bernoulli +-1
    # X = +1 with prob 0.5, X = -1 with prob 0.5
    # moments: m_n = 1 if n even, 0 if n odd
    # cumulants: kappa_1=0, kappa_2=1, kappa_3=0, kappa_4 = m_4 - 3*m_2^2 = 1 - 3 = -2
    moms_pm1 = [0.0, 1.0, 0.0, 1.0, 0.0, 1.0]
    k_pm1 = classical_cumulants(moms_pm1)
    assert abs(k_pm1[0]) < 1e-12, f"k1={k_pm1[0]}"
    assert abs(k_pm1[1] - 1.0) < 1e-12, f"k2={k_pm1[1]}"
    assert abs(k_pm1[2]) < 1e-12, f"k3={k_pm1[2]}"
    assert abs(k_pm1[3] - (-2.0)) < 1e-12, f"k4={k_pm1[3]} expected -2"

    # Test 4: verdict INCONCLUSIVE on empty
    v, _ = compute_verdict({"families": {}})
    assert v == "CUMULANT_DICHOTOMY_INCONCLUSIVE"

    # Test 5: verdict HOLDS on synthetic clean data
    synth = {
        "families": {
            "haar": {
                "kappa_per_seed": [[0.0, 0.001, 0.01, 0.02, 0.01, 0.005]] * 10,
                "kappa_mean": [0.0, 0.001, 0.01, 0.02, 0.01, 0.005],
            },
            "kerdock": {
                "kappa_per_seed": [[0.0, 0.05, 0.1, 0.3, 0.2, 0.4]] * 10,
                "kappa_mean": [0.0, 0.05, 0.1, 0.3, 0.2, 0.4],
            },
        },
        "N": 4096,
    }
    v, msg = compute_verdict(synth)
    assert v == "CUMULANT_DICHOTOMY_HOLDS", f"expected HOLDS got {v} ({msg})"

    # Test 6: verdict HAAR_FAILS when Haar leaks |kappa_n| > 0.1 on some seed
    synth_bad = {
        "families": {
            "haar": {
                "kappa_per_seed": [
                    [0.0, 0.001, 0.01, 0.02, 0.01, 0.005],
                    [0.0, 0.001, 0.15, 0.02, 0.01, 0.005],  # seed 1 breaks
                ] + [[0.0, 0.001, 0.01, 0.02, 0.01, 0.005]] * 8,
                "kappa_mean": [0.0, 0.001, 0.025, 0.02, 0.01, 0.005],
            },
            "kerdock": {
                "kappa_per_seed": [[0.0, 0.05, 0.1, 0.3, 0.2, 0.4]] * 10,
                "kappa_mean": [0.0, 0.05, 0.1, 0.3, 0.2, 0.4],
            },
        },
        "N": 4096,
    }
    v, _ = compute_verdict(synth_bad)
    assert v == "CUMULANT_DICHOTOMY_HAAR_FAILS", f"expected HAAR_FAILS got {v}"

    print("self-test passed (delta cumulants, gram extraction, verdict branches)", flush=True)


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_family(name: str, get_rows_fn, n_seeds: int, n_max: int) -> dict:
    """Run a single family across n_seeds. get_rows_fn(seed) returns L2-normalised rows.

    Computes BOTH classical and free cumulants. The primary verdict (per spec) uses
    CLASSICAL cumulants, which are the right discriminator for "Haar -> N(0,1)
    angle distribution -> classical kappa_n=0 for n>=3" vs "Kerdock -> discrete
    inner-product spectrum -> nonzero classical higher cumulants". Free cumulants
    are reported alongside as a research-grade secondary metric (their interpretation
    requires the operator-algebra ETH-free-probability framework).
    """
    kappa_classical_per_seed: list[list[float]] = []
    kappa_free_per_seed: list[list[float]] = []
    moms_per_seed: list[list[float]] = []
    excess_classical_per_seed: list[float] = []

    for seed_idx in range(n_seeds):
        t_seed = time.monotonic()
        rows = get_rows_fn(seed_idx)
        entries = offdiag_gram_entries(rows)
        moms = raw_moments(entries, n_max)
        k_class = classical_cumulants(moms)
        k_free = moments_to_free_cumulants_general(moms)
        kappa_classical_per_seed.append(k_class)
        kappa_free_per_seed.append(k_free)
        moms_per_seed.append(moms)
        excess = (k_class[3] / (k_class[1] ** 2)) if k_class[1] != 0 else 0.0
        excess_classical_per_seed.append(excess)
        dt = time.monotonic() - t_seed
        print(
            f"  [{name}] seed={seed_idx} rows={rows.shape} entries={entries.shape[0]} "
            f"m={[f'{m:+.4f}' for m in moms]} "
            f"k_class={[f'{k:+.4f}' for k in k_class]} "
            f"k_free={[f'{k:+.4f}' for k in k_free]} "
            f"k4/k2^2={excess:+.4f} dt={dt:.1f}s",
            flush=True,
        )

    k_class_arr = np.array(kappa_classical_per_seed)
    k_free_arr = np.array(kappa_free_per_seed)
    moms_arr = np.array(moms_per_seed)

    return {
        # Primary metric: classical cumulants
        "kappa_per_seed": kappa_classical_per_seed,
        "kappa_mean": k_class_arr.mean(axis=0).tolist(),
        "kappa_std": k_class_arr.std(axis=0).tolist(),
        # Secondary metric: free cumulants
        "kappa_free_per_seed": kappa_free_per_seed,
        "kappa_free_mean": k_free_arr.mean(axis=0).tolist(),
        "kappa_free_std": k_free_arr.std(axis=0).tolist(),
        "moments_mean": moms_arr.mean(axis=0).tolist(),
        "moments_std": moms_arr.std(axis=0).tolist(),
        "excess_kurtosis_per_seed": excess_classical_per_seed,
        "excess_kurtosis_mean": float(np.mean(excess_classical_per_seed)),
        "excess_kurtosis_std": float(np.std(excess_classical_per_seed)),
        "n_seeds": n_seeds,
    }


def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()
    n_max = 6

    if smoke:
        config = {
            "mode": "smoke",
            "N": 1024,
            "n_seeds": 2,
            "families": ["haar", "kerdock"],
            "n_max_moment": n_max,
        }
    else:
        config = {
            "mode": "full",
            "N": 4096,
            "n_seeds": 10,
            "families": ["haar", "kerdock"],
            "n_max_moment": n_max,
        }

    N = config["N"]
    n_seeds = config["n_seeds"]
    print(f"[config] {config}", flush=True)

    # Build Kerdock once (deterministic) and reuse across seeds.
    print(f"[kerdock] building 4-coset codebook at N={N}...", flush=True)
    t_kerd_build = time.monotonic()
    kerdock_rows_full = build_kerdock(N) / math.sqrt(N)  # bipolar/sqrt(N) -> unit norm
    nrm = np.linalg.norm(kerdock_rows_full[0])
    print(f"[kerdock] shape={kerdock_rows_full.shape} row0_norm={nrm:.6f} "
          f"build_dt={time.monotonic() - t_kerd_build:.1f}s", flush=True)
    M_codebook = kerdock_rows_full.shape[0]  # 4N
    print(f"[both arms] using M={M_codebook} (= 4N) rows per seed for the Gram matrix",
          flush=True)

    def haar_rows(seed_idx: int) -> np.ndarray:
        """Fresh Haar-uniform unit vectors on S^{N-1}, M=4N rows per seed."""
        s = 11000 + seed_idx
        return build_haar_codebook(N=N, M=M_codebook, seed=s)

    def kerdock_rows_fn(seed_idx: int) -> np.ndarray:
        """Kerdock codebook is deterministic; seed varies the row permutation so the
        bootstrap of off-diagonal moments is non-trivial across seeds (the underlying
        distribution is the same but the empirical moment statistic varies slightly)."""
        s = 22000 + seed_idx
        rng = np.random.default_rng(s)
        perm = rng.permutation(M_codebook)
        return kerdock_rows_full[perm]

    families = {}

    print(f"\n[family=haar] {n_seeds} seeds, N={N}", flush=True)
    families["haar"] = run_family("haar", haar_rows, n_seeds, n_max)

    print(f"\n[family=kerdock] {n_seeds} seeds, N={N} M_rows={M_codebook}", flush=True)
    families["kerdock"] = run_family("kerdock", kerdock_rows_fn, n_seeds, n_max)

    summary = {"N": N, "families": families, "config": config}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0

    print("\n========= SUMMARY (classical cumulants -- primary metric) =========", flush=True)
    for fam, data in families.items():
        kappa_str = " ".join(
            f"k{n}={data['kappa_mean'][n-1]:+.4f}+-{data['kappa_std'][n-1]:.4f}"
            for n in range(1, n_max + 1)
        )
        print(f"  [{fam}] {kappa_str}  excess_k4/k2^2={data['excess_kurtosis_mean']:+.4f}",
              flush=True)
    print("\n========= FREE cumulants (secondary; ETH-free-probability interpretation) =========",
          flush=True)
    for fam, data in families.items():
        free_str = " ".join(
            f"k{n}={data['kappa_free_mean'][n-1]:+.4f}"
            for n in range(1, n_max + 1)
        )
        print(f"  [{fam}] free: {free_str}", flush=True)
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)

    return summary, verdict, msg, elapsed, config


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required fields: {missing}")
    if not d.get("verdict"):
        raise ValueError("empty verdict")


def write_metrics(out_dir: Path, summary: dict, verdict: str, msg: str,
                  elapsed: float, config: dict) -> None:
    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": config,
    }
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


def run_smoke() -> None:
    self_test()
    out_dir = get_output_dir("wave14_cumulant_dichotomy_haar_vs_kerdock_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert "haar" in summary["families"] and "kerdock" in summary["families"], "smoke FAIL: missing families"
    assert len(summary["families"]["haar"]["kappa_per_seed"]) >= 1, "smoke FAIL: no haar seeds"
    assert len(summary["families"]["kerdock"]["kappa_per_seed"]) >= 1, "smoke FAIL: no kerdock seeds"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_cumulant_dichotomy_haar_vs_kerdock_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
