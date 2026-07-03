"""Rectangular free convolution (Benaych-Georges) at M/N=8 — anchor B.

Motivation
----------
v176 / cap_map probes have repeatedly shown that the substrate's 4-coset
Kerdock codebook produces an anomalous spectrum at HIGH M/N ratios (M/N=8 was
flagged as an MP-divergent operating point in prior cycles). Standard
Marchenko-Pastur (MP) describes the eigenvalue distribution of (1/N) A^T A
for square or thin A; when M >> N (the "rectangular" regime), MP needs
extension. Benaych-Georges (Adv. Math. 2010, "Rectangular free convolution
with ratio lambda") gives the rectangular free convolution operation
mu ⊞_lambda nu that exactly describes the eigenvalue limit of sums of
free rectangular random matrices at rectangular ratio lambda = M/N (or its
reciprocal).

Scientific question
-------------------
At M/N = 8 (the substrate operating point flagged by prior cycles), does
the empirical spectrum of (1/N) A^T A for substrate Kerdock match the
predicted rectangular MP density mu_MP(c=8), or is there a substrate-
specific departure beyond what rectangular free probability predicts?

The relevant family of measures:
  - iid Gaussian at c=M/N=8: empirical (1/N) A^T A eigenvalues form a sum of
    8 free copies of MP(c=1) in the *rectangular* sense, with limit density
    mu_MP(c=8).
  - Substrate (Kerdock) at c=M/N=8: if substrate is free-probabilistically
    indistinguishable from iid Gaussian at this aspect ratio, its empirical
    spectrum matches mu_MP(c=8). If the substrate carries higher rectangular
    free cumulants, its spectrum departs from mu_MP(c=8) and the KS distance
    grows beyond a control band.

Vertices: RECT_FREE_CONV_MP_MATCH / RECT_FREE_CONV_DIVERGE / INCONCLUSIVE.

Design
------
- N in {256, 512, 1024} -- 3 aspect ratio anchors (CPU-cheap for c=8 means
  M in {2048, 4096, 8192}, all svd-feasible).
- 5 codebooks (iid_gauss, srht, hadamard, rm_1_m, kerdock).
- 5 seeds.
- Per cell: compute eigenvalues of (1/N) A^T A; compute KS distance to
  rectangular MP density at c=M/N=8 (analytical CDF via numerical integration
  of MP density at c=8); compute spectral moments m_1..m_4 and free cumulants
  kappa_1..kappa_4 (where rect-MP free cumulants are all equal to c=8 by
  Voiculescu/Benaych-Georges).

HARD PASS  (substrate matches rect-MP at c=8 within tolerance):
  iid_gauss KS < 0.05 (control band) AND substrate-Kerdock KS < 0.10 AND
  all kappa_n deviations < 15% on Kerdock.

HARD FAIL  (substrate has a substrate-specific rect-free anomaly at c=8):
  iid_gauss KS < 0.05 (control band still passes) AND Kerdock KS > 0.20 OR
  any Kerdock kappa_n deviation > 50%.

MIDDLE BAND: between the bands.

Pre-reg: preregs/2026-05-24_wave14_rect_free_conv_mn8_v1.md
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
# Reuse codebook builders + mp_ks_stat from kappa_profile_cross_codebook
_kp_path = REPO / "experiments" / "exp_wave14_kappa_profile_cross_codebook_v1.py"
_spec = importlib.util.spec_from_file_location("kp_v1", _kp_path)
_kp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_kp)
build_iid_gauss = _kp.build_iid_gauss
build_srht = _kp.build_srht
build_hadamard = _kp.build_hadamard
build_rm_1_m = _kp.build_rm_1_m
build_kerdock = _kp.build_kerdock

# Reuse free-cumulant inversion from free_cumulants_kerdock_v1
_fc_path = REPO / "experiments" / "exp_wave14_free_cumulants_kerdock_v1.py"
_spec2 = importlib.util.spec_from_file_location("fc_v1", _fc_path)
_fc = importlib.util.module_from_spec(_spec2)
_spec2.loader.exec_module(_fc)
moments_to_free_cumulants = _fc.moments_to_free_cumulants
mp_reference_moments = _fc.mp_reference_moments  # gives MP(c) moments
spectral_moments = _fc.spectral_moments


CODEBOOKS = [
    ("iid_gauss", build_iid_gauss),
    ("srht", build_srht),
    ("hadamard", build_hadamard),
    ("rm_1_m", build_rm_1_m),
    ("kerdock", build_kerdock),
]


# ---------------------------------------------------------------------------
# Rectangular MP density and CDF at general c = M/N
# ---------------------------------------------------------------------------

def mp_density(x: np.ndarray, c: float) -> np.ndarray:
    """Marchenko-Pastur density for general c = M/N (rectangular regime).

    Support [(1-sqrt(c))^2, (1+sqrt(c))^2] when c <= 1; for c > 1 the
    density is supported on [(sqrt(c)-1)^2, (sqrt(c)+1)^2] for the
    eigenvalues of (1/N) A^T A where A is M x N with iid entries of
    variance 1/N. Density:
      p(x) = sqrt(max(0, (lam_plus - x)(x - lam_minus))) / (2 pi x)   for c <= 1
    For c >= 1 (rectangular thick A), the limit of eigenvalues of
    (1/N) A^T A has support inside [(1-sqrt(c))^2, (1+sqrt(c))^2] (the
    formula is symmetric in this orientation since we keep c=M/N >= 1).

    Reference: Bai-Silverstein 2010, Theorem 3.6 (general c form).
    """
    lam_minus = (1.0 - math.sqrt(c)) ** 2
    lam_plus = (1.0 + math.sqrt(c)) ** 2
    p = np.zeros_like(x, dtype=np.float64)
    inside = (x >= lam_minus) & (x <= lam_plus) & (x > 0)
    p[inside] = np.sqrt(
        np.maximum(0.0, (lam_plus - x[inside]) * (x[inside] - lam_minus))
    ) / (2.0 * math.pi * x[inside])
    return p


def mp_cdf(x_grid: np.ndarray, c: float, n_quad: int = 4096) -> np.ndarray:
    """Numerical CDF of MP density at general c by trapezoid integration
    on a fine grid covering [lam_minus, x_grid.max()].

    Returns array of same length as x_grid with F(x_grid[i]) = P(X <= x_grid[i]).
    """
    lam_minus = (1.0 - math.sqrt(c)) ** 2
    lam_plus = (1.0 + math.sqrt(c)) ** 2
    grid_lo = max(0.0, lam_minus - 1e-9)
    grid_hi = lam_plus + 1e-9
    fine = np.linspace(grid_lo, grid_hi, n_quad)
    p_fine = mp_density(fine, c)
    # cumulative trapezoid
    dx = np.diff(fine)
    midp = 0.5 * (p_fine[:-1] + p_fine[1:])
    cum = np.concatenate([[0.0], np.cumsum(midp * dx)])
    # interpolate at x_grid
    cdf_vals = np.interp(x_grid, fine, cum)
    # clamp
    return np.clip(cdf_vals, 0.0, cum[-1])


def ks_distance_to_mp(eig: np.ndarray, c: float) -> float:
    """One-sample KS distance between empirical eigenvalue CDF and MP(c)."""
    eig_sorted = np.sort(eig.astype(np.float64))
    n = len(eig_sorted)
    if n == 0:
        return float("nan")
    emp_cdf = np.arange(1, n + 1) / n
    # Evaluate analytical MP CDF at eig_sorted points
    mp_at_eigs = mp_cdf(eig_sorted, c)
    # Normalize MP CDF by its total mass (should be ~1 numerically)
    total_mass = mp_cdf(np.array([(1.0 + math.sqrt(c)) ** 2 + 1.0]), c)[0]
    if total_mass > 1e-9:
        mp_at_eigs = mp_at_eigs / total_mass
    return float(np.max(np.abs(emp_cdf - mp_at_eigs)))


# ---------------------------------------------------------------------------
# Per-cell metrics
# ---------------------------------------------------------------------------

def compute_cell(
    N: int, M: int, seed: int, codebook_name: str, build_fn
) -> dict:
    """Build A, compute eigenvalues of (1/N) A^T A, KS to rect-MP(c),
    spectral moments, free cumulants, deviations."""
    A = build_fn(N, M, seed)  # builder returns A normalized to spectral O(1)
    # build_fn normalizes by /sqrt(N), so A is the rescaled matrix; its
    # singular values squared give eigenvalues of (1/N) original^T original.
    # Equivalently eigenvalues of A^T A directly.
    _, s, _ = np.linalg.svd(A, full_matrices=False)
    eig = (s ** 2).astype(np.float64)
    c = M / N
    ks = ks_distance_to_mp(eig, c)
    moms = spectral_moments(eig, 4)
    kappas = moments_to_free_cumulants(moms)
    # MP reference free cumulants: all equal to c at general aspect ratio.
    # (Benaych-Georges 2010 extends the c=1 statement to rectangular case.)
    # Compute deviations |kappa_n / c - 1| for n=2,3,4.
    devs = []
    for n_idx in range(1, len(kappas)):
        dev = abs(kappas[n_idx] / max(c, 1e-12) - 1.0)
        devs.append(dev)
    return {
        "N": int(N),
        "M": int(M),
        "c": float(c),
        "seed": int(seed),
        "codebook": codebook_name,
        "ks_distance": float(ks),
        "moments": [float(x) for x in moms],
        "free_cumulants": [float(x) for x in kappas],
        "kappa_devs_from_c": [float(d) for d in devs],
        "max_kappa_dev": float(max(devs)) if devs else 0.0,
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

KS_CONTROL_BAND = 0.05    # iid_gauss must be below this (control sanity)
KS_SUBSTRATE_PASS = 0.10  # Kerdock must be below this for HARD PASS
KS_SUBSTRATE_FAIL = 0.20  # Kerdock above this for HARD FAIL
KAPPA_PASS = 0.15
KAPPA_FAIL = 0.50


def compute_verdict(summary: dict) -> tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("RECT_FREE_CONV_INCONCLUSIVE", "No cells.")

    # Aggregate by codebook
    by_cb: dict[str, list[dict]] = {}
    for c in cells:
        by_cb.setdefault(c["codebook"], []).append(c)

    iid_ks = [c["ks_distance"] for c in by_cb.get("iid_gauss", [])]
    iid_ks_mean = float(np.mean(iid_ks)) if iid_ks else float("nan")

    kerdock_ks = [c["ks_distance"] for c in by_cb.get("kerdock", [])]
    kerdock_ks_mean = float(np.mean(kerdock_ks)) if kerdock_ks else float("nan")

    kerdock_kappa = [c["max_kappa_dev"] for c in by_cb.get("kerdock", [])]
    kerdock_kappa_max = float(np.max(kerdock_kappa)) if kerdock_kappa else 0.0

    # Control sanity: iid_gauss should match MP(c) tightly
    control_ok = iid_ks_mean < KS_CONTROL_BAND

    if not control_ok:
        return (
            "RECT_FREE_CONV_INCONCLUSIVE",
            f"Control (iid_gauss) KS={iid_ks_mean:.4f} exceeds control band "
            f"{KS_CONTROL_BAND}; finite-N MP convergence too noisy. "
            f"Kerdock KS={kerdock_ks_mean:.4f} cannot be interpreted against "
            f"this control.",
        )

    if kerdock_ks_mean > KS_SUBSTRATE_FAIL or kerdock_kappa_max > KAPPA_FAIL:
        return (
            "RECT_FREE_CONV_DIVERGE",
            f"Kerdock spectrum DIVERGES from rectangular MP(c) prediction. "
            f"Kerdock KS={kerdock_ks_mean:.4f} (threshold {KS_SUBSTRATE_FAIL}), "
            f"max kappa-dev={kerdock_kappa_max:.4f} (threshold {KAPPA_FAIL}). "
            f"iid-gauss control KS={iid_ks_mean:.4f} (OK). Substrate carries "
            f"higher rectangular free cumulants beyond what Benaych-Georges' "
            f"rect-free convolution predicts at c=M/N.",
        )

    if kerdock_ks_mean < KS_SUBSTRATE_PASS and kerdock_kappa_max < KAPPA_PASS:
        return (
            "RECT_FREE_CONV_MP_MATCH",
            f"Kerdock spectrum MATCHES rectangular MP(c) prediction. "
            f"Kerdock KS={kerdock_ks_mean:.4f} < {KS_SUBSTRATE_PASS}; "
            f"max kappa-dev={kerdock_kappa_max:.4f} < {KAPPA_PASS}; "
            f"iid-gauss control KS={iid_ks_mean:.4f}. Substrate is free-"
            f"probabilistically indistinguishable from iid Gaussian at the "
            f"rectangular regime; no substrate-specific rect-free anomaly.",
        )

    return (
        "RECT_FREE_CONV_INCONCLUSIVE",
        f"Kerdock KS={kerdock_ks_mean:.4f} in middle band "
        f"[{KS_SUBSTRATE_PASS}, {KS_SUBSTRATE_FAIL}], or kappa-dev "
        f"={kerdock_kappa_max:.4f} in [{KAPPA_PASS}, {KAPPA_FAIL}]. "
        f"iid-gauss control KS={iid_ks_mean:.4f}.",
    )


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------

def self_test() -> None:
    # 1. mp_density: nonzero inside support, zero outside
    c = 8.0
    lam_p = (1.0 + math.sqrt(c)) ** 2
    lam_m = (1.0 - math.sqrt(c)) ** 2
    pts = np.array([0.0, lam_m - 0.1, (lam_m + lam_p) / 2, lam_p + 0.1])
    d = mp_density(pts, c)
    assert d[0] == 0.0 and d[1] == 0.0 and d[3] == 0.0
    assert d[2] > 0.0
    print(f"  cell 1: mp_density inside={d[2]:.4f}, outside-zero OK", flush=True)

    # 2. mp_cdf monotone and ~1 at upper end
    grid = np.linspace(0.0, lam_p + 1.0, 200)
    cdf = mp_cdf(grid, c)
    assert np.all(np.diff(cdf) >= -1e-9), "CDF not monotone"
    assert cdf[-1] > 0.95 and cdf[-1] < 1.05, f"CDF upper={cdf[-1]:.4f} not near 1"
    print(f"  cell 2: mp_cdf monotone, total mass={cdf[-1]:.4f}", flush=True)

    # 3. KS distance: iid Gaussian at moderate N gets small KS to MP(c)
    rng_seed = 42
    A = build_iid_gauss(256, 2048, rng_seed)  # c = 8
    _, s, _ = np.linalg.svd(A, full_matrices=False)
    eig = (s ** 2).astype(np.float64)
    ks = ks_distance_to_mp(eig, 8.0)
    assert ks < 0.15, f"iid_gauss at N=256, c=8 should have small KS; got {ks:.4f}"
    print(f"  cell 3: iid_gauss N=256 c=8 KS={ks:.4f} (<0.15)", flush=True)

    # 4. Free cumulants of MP(c): all kappa_n = c
    mp_moms = mp_reference_moments(8.0, 4)
    mp_kappa = moments_to_free_cumulants(mp_moms)
    for k_n, n in zip(mp_kappa, range(1, 5)):
        assert abs(k_n - 8.0) < 1e-6, f"kappa_{n}(MP(8))={k_n} expected 8"
    print(f"  cell 4: MP(c=8) free cumulants ~ c=8 OK", flush=True)

    # 5. Verdict bands
    fake_pass = {"cells": [
        {"codebook": "iid_gauss", "ks_distance": 0.02, "max_kappa_dev": 0.05},
        {"codebook": "kerdock", "ks_distance": 0.06, "max_kappa_dev": 0.10},
    ]}
    v, _ = compute_verdict(fake_pass)
    assert v == "RECT_FREE_CONV_MP_MATCH", f"PASS -> {v}"

    fake_fail = {"cells": [
        {"codebook": "iid_gauss", "ks_distance": 0.02, "max_kappa_dev": 0.05},
        {"codebook": "kerdock", "ks_distance": 0.30, "max_kappa_dev": 0.10},
    ]}
    v, _ = compute_verdict(fake_fail)
    assert v == "RECT_FREE_CONV_DIVERGE", f"FAIL -> {v}"

    fake_mid = {"cells": [
        {"codebook": "iid_gauss", "ks_distance": 0.02, "max_kappa_dev": 0.05},
        {"codebook": "kerdock", "ks_distance": 0.15, "max_kappa_dev": 0.30},
    ]}
    v, _ = compute_verdict(fake_mid)
    assert v == "RECT_FREE_CONV_INCONCLUSIVE", f"MID -> {v}"

    fake_control_bad = {"cells": [
        {"codebook": "iid_gauss", "ks_distance": 0.10, "max_kappa_dev": 0.05},
        {"codebook": "kerdock", "ks_distance": 0.06, "max_kappa_dev": 0.10},
    ]}
    v, _ = compute_verdict(fake_control_bad)
    assert v == "RECT_FREE_CONV_INCONCLUSIVE", f"CTRL_BAD -> {v}"

    print(f"self-tests passed (5 cells)", flush=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    if smoke:
        config = {
            "mode": "smoke",
            "N_list": [64],
            "ratio": 8,  # M = ratio * N
            "n_seeds": 1,
            "codebooks": ["iid_gauss", "kerdock"],
        }
    else:
        config = {
            "mode": "full",
            "N_list": [256, 512, 1024],
            "ratio": 8,
            "n_seeds": 5,
            "codebooks": ["iid_gauss", "srht", "hadamard", "rm_1_m", "kerdock"],
        }

    cells = []
    cb_map = dict(CODEBOOKS)
    for N in config["N_list"]:
        M = config["ratio"] * N
        for cb_name in config["codebooks"]:
            build_fn = cb_map[cb_name]
            for seed in range(config["n_seeds"]):
                try:
                    cell = compute_cell(N, M, seed, cb_name, build_fn)
                    cells.append(cell)
                    print(
                        f"[N={N} M={M} cb={cb_name} seed={seed}] "
                        f"ks={cell['ks_distance']:.4f} "
                        f"max_kappa_dev={cell['max_kappa_dev']:.4f}",
                        flush=True,
                    )
                except Exception as e:
                    print(f"  ERROR N={N} cb={cb_name} seed={seed}: {e}", flush=True)

    summary = {"cells": cells, "config": config}
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
    out_dir = get_output_dir("wave14_rect_free_conv_mn8_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_rect_free_conv_mn8_v1")
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
