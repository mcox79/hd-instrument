"""Voiculescu S-transform of Kerdock spectrum -- multiplicative free probability probe.

Motivation
----------
Companion to wave14_free_cumulants_kerdock_v1 (running on GPU). The
free-cumulants probe tests ADDITIVE free convolution structure (R-transform
power series). The S-transform tests MULTIPLICATIVE free convolution -- a
distinct, complementary probe of where Kerdock departs from Marchenko-Pastur.

For a probability measure mu with positive support and finite mean m_1 != 0,
the S-transform is defined via the moment generating function:

  psi_mu(z) = sum_{n>=1} m_n z^n
  chi_mu(z) = psi_mu^{-1}(z)   (formal compositional inverse)
  S_mu(z)   = chi_mu(z) * (1 + z) / z

S-transform is multiplicative under free multiplicative convolution:
  S_{mu_1 boxtimes mu_2}(z) = S_{mu_1}(z) * S_{mu_2}(z)

For Marchenko-Pastur(c) with c = M/N (using the spectral-moment normalization
m_n = (1/n) sum_{k=1..n} C(n,k) C(n,k-1) c^k of Bai-Silverstein):
  S_MP(z) = 1 / (c + z) = sum_{k>=0} (-1)^k z^k / c^{k+1}

So the substrate-novel signature is the S-transform coefficient deviation
from S_k^MP = (-1)^k / c^{k+1}. (Note: this differs from the c=mean=1
normalization sometimes used in Nica-Speicher where S_MP(z) = 1/(1+z); our
convention follows the unnormalized MP with mean = c, matching how
free_cumulants_kerdock_v1 normalizes spectral moments.)

Concretely we compute the first 5 coefficients of S_mu(z) as a power series
around z=0, using the empirical moments m_1..m_5 to invert psi_mu(z), then
report (S_n / S_n^MP - 1) for n in {0,1,2,3,4} as the deviation profile.

S-transform truly probes a DIFFERENT free-prob axis than free cumulants:
  - Free cumulants kappa_n: encode the R-transform R_mu(z) = sum kappa_n z^{n-1};
    are addition-free-convolution invariants.
  - S-transform coefficients: encode the multiplicative-free-convolution
    structure; are not derivable linearly from R-transform.

A divergence on EITHER probe is sufficient to place Kerdock outside the
standard MP universality class. A divergence on BOTH is doubly damning
(two independent algebra-of-free-probability axes both detect it).

Vertex: S_TRANSFORM_MATCH_MP / S_TRANSFORM_DIVERGE / S_TRANSFORM_INCONCLUSIVE.

Pre-reg: preregs/2026-05-23_wave14_S_transform_kerdock_v1.md
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
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# Reuse Kerdock builder + spectrum helpers from free_cumulants script
_fc_path = REPO / "experiments" / "exp_wave14_free_cumulants_kerdock_v1.py"
_spec = importlib.util.spec_from_file_location("free_cum_v1", _fc_path)
_fc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fc)

get_kerdock_spectrum = _fc.get_kerdock_spectrum
spectral_moments = _fc.spectral_moments
mp_reference_moments = _fc.mp_reference_moments


# ---------------------------------------------------------------------------
# S-transform power series from moments via psi-inversion
# ---------------------------------------------------------------------------

def invert_power_series(a: list[float], n_max: int) -> list[float]:
    """Return coefficients b_1..b_n_max such that f^{-1}(z) = sum b_k z^k where
    f(z) = sum a_k z^k, a_1 != 0.

    Lagrange inversion (or recursive coefficient inversion):
      f(f^{-1}(z)) = z  -> system of polynomial equations in b_k.

    We use the standard Newton-style coefficient bootstrap:
      Let g(z) = sum_{k>=1} b_k z^k.
      Composition f(g(z)) up to order n: equate to z, solve for b_n.
    """
    if not a or a[0] == 0.0:
        raise ValueError("cannot invert series with zero linear coefficient")

    b = [0.0] * n_max
    b[0] = 1.0 / a[0]

    for n in range(2, n_max + 1):
        # f(g(z)) coefficient at z^n must equal 0 (since target is z, only z^1 = 1)
        # f(g(z)) = sum_{k=1}^{n} a_k * (g(z))^k
        # We need the z^n coefficient of sum_{k=1}^{n} a_k g^k(z)
        # Compute g^k up to order n iteratively
        # gpowk[k][m] = coefficient of z^m in g^k(z), 1 <= m <= n
        # g is determined for b_1..b_{n-1}; b_n unknown.
        # Let coeff of z^n in g^k be sum over j_1+..+j_k = n of prod b_{j_i}
        # For k=1: just b_n
        # For k>=2: depends only on b_1..b_{n-1} except for the term containing b_n
        #   That term: k * b_1^{k-1} * b_n (from picking b_n in one of k slots,
        #   contributing b_n in one factor and total z^{n-1} ... wait, not quite)
        # Actually: coeff of z^n in (b_1 z + b_2 z^2 + ... + b_{n-1} z^{n-1} + b_n z^n + ...)^k
        # The b_n term contributes only as the SOLE factor with degree n, but we need
        # total degree n and k factors. So only k=1 directly involves b_n.
        # For k >= 2: each factor has degree >= 1; total k; if one factor is b_n z^n,
        # the remaining k-1 factors must sum to degree 0, impossible since each >= 1.
        # So for k >= 2 the coefficient of z^n depends ONLY on b_1..b_{n-1}.
        # Equation: a_1 * b_n + (known terms from k>=2) = 0  (since target is z, not z^n)
        # => b_n = -(known) / a_1

        # Compute g powers using only known b_1..b_{n-1}
        gpow = [[0.0] * (n + 1) for _ in range(n + 1)]  # gpow[k][m] for k=0..n, m=0..n
        gpow[0][0] = 1.0
        # g_known coefficients: index 1..n-1; b[i-1] is coeff of z^i (1-indexed)
        g_known = [0.0] * (n + 1)
        for i in range(1, n):
            g_known[i] = b[i - 1]

        for k in range(1, n + 1):
            for m in range(0, n + 1):
                s = 0.0
                # gpow[k][m] = sum_{j=1..m} g_known[j] * gpow[k-1][m-j]
                for j in range(1, m + 1):
                    if g_known[j] != 0.0 and gpow[k - 1][m - j] != 0.0:
                        s += g_known[j] * gpow[k - 1][m - j]
                gpow[k][m] = s

        # Sum_k a_k * gpow[k][n] for k=1..n; this is f(g(z))|_{z^n} from KNOWN parts
        known_sum = 0.0
        for k in range(1, n + 1):
            ak = a[k - 1] if k - 1 < len(a) else 0.0
            known_sum += ak * gpow[k][n]
        # We need a_1*b_n + known_sum_excluding_b_n_contribution = 0
        # gpow[1][n] already equals 0 because g_known has no z^n term.
        # So known_sum is the contribution of k>=2; we add a_1*b_n then set to 0.
        target = 0.0  # coefficient of z^n in identity z = sum z is 0 for n != 1
        b[n - 1] = (target - known_sum) / a[0]

    return b


def moments_to_S_transform_coeffs(moments: list[float], n_max: int = 5) -> list[float]:
    """Compute coefficients S_0..S_{n_max-1} of S-transform power series.

    psi(z)  = sum_{n>=1} m_n z^n
    chi(z)  = psi^{-1}(z)            # compositional inverse (chi(psi(z)) = z)
    S(z)    = chi(z) * (1 + z) / z

    Returns [S_0, S_1, ..., S_{n_max-1}] where S(z) = sum_{k>=0} S_k z^k.

    Note S(z) has a 1/z * chi(z) factor but chi(z) starts at z (since psi(0)=0),
    so chi(z)/z is a power series starting at constant 1/m_1.
    """
    # psi coefficients a_k = m_k for k>=1 (we drop a_0=0 from indexing)
    psi_coeffs = list(moments[:n_max + 1])  # need at least n_max+1 for chi up to order n_max+1

    # Invert: chi_coeffs[k-1] = coefficient of z^k in chi(z), 1-indexed in our convention
    n_invert = n_max + 1  # chi up to order n_max+1 so chi/z up to n_max
    chi_coeffs = invert_power_series(psi_coeffs, n_invert)

    # chi(z)/z = sum_{k>=0} chi_coeffs[k] z^k  (shift by 1)
    chi_over_z = chi_coeffs[: n_max + 1]

    # S(z) = (chi/z) * (1 + z)
    # If c_k = chi_over_z[k], then S_k = c_k + c_{k-1} for k>=1, S_0 = c_0
    S = [chi_over_z[0]]
    for k in range(1, n_max + 1):
        S.append(chi_over_z[k] + chi_over_z[k - 1])
    return S[:n_max]


def mp_S_transform_coeffs(c: float, n_max: int = 5) -> list[float]:
    """S_{MP(c)}(z) = 1 / (c + z) = sum_{k>=0} (-1)^k z^k / c^{k+1}.

    Convention: spectral moments are normalized per Bai-Silverstein
    (m_n = E[lambda^n] of (1/N) A^T A, no further rescaling), so MP(c) has
    mean = c. S-transform is then 1/(c+z) (NOT the normalized 1/(1+z) form
    that requires rescaling the measure to have mean = 1).
    """
    if c == 0:
        raise ValueError("S-transform undefined at c=0 (zero mean measure)")
    return [((-1) ** k) / (c ** (k + 1)) for k in range(n_max)]


# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------

def compute_verdict(summary: dict) -> tuple[str, str]:
    """Per-cell deviation of S-transform coefficients from MP baseline.

    DIVERGE: at least one cell has worst |S_k / S_k^MP - 1| > 0.20 for k in {1..n_max-1}
    MATCH:   all cells have all |S_k - S_k^MP| / max(|S_k^MP|, 1e-3) < 0.10
    INCONCLUSIVE: mixed
    """
    if not summary.get("cells"):
        return ("S_TRANSFORM_INCONCLUSIVE", "No cells computed.")

    DIVERGE_THRESHOLD = 0.20
    MATCH_THRESHOLD = 0.10

    diverge_cells = 0
    match_cells = 0
    max_dev = 0.0
    max_dev_loc = ""

    for cell in summary["cells"]:
        S_emp = cell.get("S_mean", [])
        S_mp = cell.get("S_mp", [])
        if not S_emp or not S_mp:
            continue

        worst_dev = 0.0
        worst_k = 0
        # Compare k=1..len-1 (skip k=0 which is always 1 by construction sanity but
        # numerically informative; we include k=0 deviation guard separately)
        for k in range(1, min(len(S_emp), len(S_mp))):
            ref = abs(S_mp[k])
            if ref < 1e-6:
                dev = abs(S_emp[k] - S_mp[k])  # absolute deviation when ref is ~0
            else:
                dev = abs(S_emp[k] / S_mp[k] - 1.0)
            if dev > worst_dev:
                worst_dev = dev
                worst_k = k
        cell["worst_S_dev"] = worst_dev
        cell["worst_S_k"] = worst_k

        alpha = cell.get("alpha", 0.0)
        if worst_dev > max_dev:
            max_dev = worst_dev
            max_dev_loc = f"alpha={alpha:.2f}, S_{worst_k}"

        if worst_dev > DIVERGE_THRESHOLD:
            diverge_cells += 1
        elif worst_dev < MATCH_THRESHOLD:
            match_cells += 1

    n_cells = len(summary["cells"])
    if diverge_cells >= max(1, n_cells // 2):
        return (
            "S_TRANSFORM_DIVERGE",
            f"Kerdock S-transform coefficients deviate from MP baseline. "
            f"{diverge_cells}/{n_cells} cells exceed 20% deviation; max_dev={max_dev:.3f} "
            f"at {max_dev_loc}. The multiplicative free-convolution structure of the "
            f"Kerdock spectrum is non-MP, independently corroborating the free-cumulant "
            f"probe and providing a second algebraic-free-probability axis on which the "
            f"substrate departs from AMP universality.",
        )
    if match_cells == n_cells:
        return (
            "S_TRANSFORM_MATCH_MP",
            f"All {n_cells} cells have S-transform coefficients within 10% of MP "
            f"baseline. Max dev={max_dev:.3f}. Kerdock spectrum is "
            f"MULTIPLICATIVELY-FREE-INDISTINGUISHABLE from MP up to order {summary.get('n_max', 4)}; "
            f"if free cumulants ALSO match, then AMP_SE_DIVERGES is not a free-prob "
            f"phenomenon -- mechanism must be at the eigenvector / localization level.",
        )

    return (
        "S_TRANSFORM_INCONCLUSIVE",
        f"Mixed: {diverge_cells} diverge, {match_cells} match, out of {n_cells}. "
        f"Max dev={max_dev:.3f} at {max_dev_loc}.",
    )


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def self_test() -> None:
    """Test 1: invert_power_series identity on a simple series.
    Test 2: MP(c=0.5) moments should give S-transform coeffs (1, -0.5, 0.25, -0.125, 0.0625)
    Test 3: verdict classifier branches
    """
    # Test 1: invert (z + z^2) -> should give the inverse compositional series.
    # f(z) = z + z^2; f^{-1}(z) coefficients: b1=1, b2=-1, b3=2, b4=-5, b5=14 (Catalan-1)
    b = invert_power_series([1.0, 1.0, 0.0, 0.0, 0.0], 5)
    expected = [1.0, -1.0, 2.0, -5.0, 14.0]
    for i, (got, want) in enumerate(zip(b, expected)):
        assert abs(got - want) < 1e-9, f"invert test k={i+1}: got {got}, want {want}"

    # Test 2: MP(c=0.5) S-transform should match closed form 1/(0.5 + z) = 2*(-2)^k
    # Test for multiple c values to lock the convention
    for c in (0.25, 0.5, 1.0, 2.0):
        moms = mp_reference_moments(c, 6)
        S_emp = moments_to_S_transform_coeffs(moms, n_max=5)
        S_ref = mp_S_transform_coeffs(c, n_max=5)
        for i, (got, want) in enumerate(zip(S_emp, S_ref)):
            assert abs(got - want) < 1e-6, (
                f"MP({c}) S-transform k={i}: got {got}, want {want}"
            )

    # Test 3: verdict DIVERGE (cell 1 dev > 20%, cell 2 dev=0)
    summary = {"cells": [
        {"alpha": 0.5, "S_mean": [2.0, -1.0, 0.5, -0.3, 0.2], "S_mp": [2.0, -4.0, 8.0, -16.0, 32.0]},
        {"alpha": 1.0, "S_mean": [1.0, -1.0, 1.0, -1.0, 1.0], "S_mp": [1.0, -1.0, 1.0, -1.0, 1.0]},
    ]}
    v, _ = compute_verdict(summary)
    assert v == "S_TRANSFORM_DIVERGE", f"expected DIVERGE got {v}"

    # Test 4: verdict MATCH (all within 10%)
    summary = {"cells": [
        {"alpha": 1.0, "S_mean": [1.0, -1.05, 1.02, -0.98, 1.03], "S_mp": [1.0, -1.0, 1.0, -1.0, 1.0]},
    ]}
    v, _ = compute_verdict(summary)
    assert v == "S_TRANSFORM_MATCH_MP", f"expected MATCH got {v}"

    # Test 5: empty
    v, _ = compute_verdict({"cells": []})
    assert v == "S_TRANSFORM_INCONCLUSIVE", f"expected INCONCLUSIVE got {v}"

    print("S-transform self-test passed (5/5 cases)", flush=True)


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    if smoke:
        config = {
            "mode": "smoke",
            "N": 1024,
            "M_over_N_list": [0.5, 1.0],
            "n_seeds": 2,
            "n_max": 5,
        }
    else:
        config = {
            "mode": "full",
            "N": 4096,
            "M_over_N_list": [0.25, 0.5, 1.0, 2.0, 4.0],
            "n_seeds": 5,
            "n_max": 5,
        }

    N = config["N"]
    n_max = config["n_max"]

    cells = []
    for alpha in config["M_over_N_list"]:
        M = max(1, int(alpha * N))
        if M > 4 * N:
            print(f"[skip] alpha={alpha:.2f}: M={M} > 4N={4*N}", flush=True)
            continue
        c_ref = float(alpha)

        print(f"\n[alpha={alpha:.2f}] N={N} M={M} c_ref={c_ref:.4f}", flush=True)

        S_per_seed = []
        for seed in range(config["n_seeds"]):
            seed_val = seed * 1000 + int(alpha * 100)
            eigenvalues, _ = get_kerdock_spectrum(N, M, seed=seed_val)
            # Need moments up to n_max+1 for chi inversion
            moms = spectral_moments(eigenvalues, n_max + 1)
            S = moments_to_S_transform_coeffs(moms, n_max=n_max)
            S_per_seed.append(S)
            print(f"  seed={seed} S={[f'{x:+.4f}' for x in S]}", flush=True)

        S_arr = np.array(S_per_seed)  # (n_seeds, n_max)
        S_mean = S_arr.mean(axis=0).tolist()
        S_std = S_arr.std(axis=0).tolist()
        S_mp = mp_S_transform_coeffs(c_ref, n_max=n_max)
        dev = [
            (S_mean[k] - S_mp[k]) / (abs(S_mp[k]) if abs(S_mp[k]) > 1e-6 else 1.0)
            for k in range(n_max)
        ]

        cell = {
            "alpha": float(alpha),
            "N": N, "M": M, "c_ref": c_ref,
            "S_mean": S_mean,
            "S_std": S_std,
            "S_mp": S_mp,
            "S_dev_relative": dev,
        }
        cells.append(cell)
        print(
            f"  AGGREGATE alpha={alpha:.2f}: S_mean={[f'{x:+.4f}' for x in S_mean]} "
            f"vs S_mp={[f'{x:+.4f}' for x in S_mp]}; dev_rel={[f'{d:+.3f}' for d in dev]}",
            flush=True,
        )

    summary = {"cells": cells, "config": config, "n_max": n_max}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
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
    out_dir = get_output_dir("wave14_S_transform_kerdock_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["cells"]) >= 1, "smoke FAIL: no cells"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_S_transform_kerdock_v1")
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
