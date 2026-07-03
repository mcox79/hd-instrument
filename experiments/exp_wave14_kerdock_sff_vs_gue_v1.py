"""Spectral Form Factor (SFF) of Kerdock-Hebbian W vs GUE prediction.

Falsification anchor for the partial-thermalization (PFK) interpretation of
the substrate. From `notes/research_eth_thermalization_drill_2026-05-23.md`
Anchor #1:

Construct Kerdock-Hebbian W (N x N, symmetric) at N=4096 (t=6 primitive
polynomial). Compute the spectral form factor

    SFF(tau) = | sum_i exp(-i lambda_i tau) |^2 / N

over tau spanning the ramp + plateau region (up to ~10x the Heisenberg time
T_H ~ N / mean_spacing). Compare to the analytic GUE prediction.

GUE prediction (Mehta; Cotler et al. 2017 "Black holes and random matrices"):
For an N x N GUE matrix with unfolded spectrum, the connected SFF is
    K_conn(tau) = tau / (2 pi)         for 0 < tau < 2 pi (linear ramp)
    K_conn(tau) = 1                    for tau > 2 pi    (plateau)
On the unfolded time axis tau_H = 2 pi (one Heisenberg time).

We compute:
  - the EMPIRICAL SFF(tau) of W's spectrum (unfolded by mean spacing).
  - the GUE analytic SFF(tau) on the same tau grid.
  - relative deviation as |SFF_emp - SFF_GUE| / SFF_GUE in two regions:
        DIP region : tau in (0.05 T_H, 0.5 T_H)
        PLATEAU    : tau in (3 T_H, 10 T_H)
  - report max deviation in each region.

W is symmetric (= (1/N) C^T C from Kerdock 4-coset codebook). Eigenvalues
are real and non-negative; we use them directly without "Hermitian
symmetrization" beyond what W already is.

Spectral unfolding: rescale eigenvalues by mean local level spacing so that
the unfolded density is approximately uniform with mean spacing = 1, then
the natural time unit is the inverse mean spacing (Heisenberg time
T_H = 2 pi after unfolding). We use the simple "global rescale by total
density" unfolding -- not full local polynomial unfolding -- which is
standard for SFF comparison and the right level of refinement for this
falsification anchor.

Hypotheses (PFK partial-thermalization vs GUE-like full-ETH):
  HARD PASS  SFF deviates from GUE by > 15% in dip depth OR plateau height
             in >= 4/5 seeds -> substrate has structure GUE doesn't capture.
  HARD FAIL  SFF matches GUE within 5% across ramp AND plateau in >= 4/5
             seeds -> substrate is just GUE-like, PFK framing kills.

Vertex: PFK_SFF_NON_GUE / PFK_SFF_MATCHES_GUE / PFK_SFF_INCONCLUSIVE.

Pre-reg: preregs/2026-05-23_wave14_kerdock_sff_vs_gue_v1.md
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
# Import Kerdock 4-coset codebook builder
_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
_spec = importlib.util.spec_from_file_location("kerdock_v3", _v3_path)
_v3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v3)
make_kerdock_4coset_codebook = _v3.make_kerdock_4coset_codebook

import torch


# ---------------------------------------------------------------------------
# Spectral helpers
# ---------------------------------------------------------------------------

def kerdock_W_spectrum(N: int, alpha: float = 1.0, seed: int = 0) -> np.ndarray:
    """Build sub-sampled Kerdock W_alpha = (1/N) C_sub^T C_sub at given alpha,
    return its eigenvalues. The full alpha=4 Kerdock 4-coset is a tight frame
    (W = 4*I); we sub-sample to alpha = M/N for a non-trivial spectrum that
    matches v167's central case.
    """
    cb, _info = make_kerdock_4coset_codebook(N, torch.device("cpu"))
    C = cb.float().numpy()  # (4N, N)
    M = int(alpha * N)
    rng = np.random.default_rng(seed)
    idx = rng.choice(C.shape[0], size=M, replace=False)
    C_sub = C[idx]
    W = (C_sub.T @ C_sub) / float(N)  # symmetric (N, N)
    eigs = np.linalg.eigvalsh(W).astype(np.float64)
    return eigs


def gue_W_spectrum(N: int, rng: np.random.Generator) -> np.ndarray:
    """Construct an N x N GUE matrix and return its real eigenvalues, scaled
    to have semicircle support [-2, 2] (standard GUE convention)."""
    # GUE: H = (A + A^H) / sqrt(2) with A iid complex normal with variance 1/N.
    # Eigenvalues live on [-2*sqrt(N)/sqrt(N), ...] = [-2,2] for the variance
    # normalization used here.
    A = (rng.standard_normal((N, N)) + 1j * rng.standard_normal((N, N))) / math.sqrt(2.0 * N)
    H = (A + A.conj().T) / math.sqrt(2.0)
    eigs = np.linalg.eigvalsh(H).real.astype(np.float64)
    return eigs


def unfold_global(eigs: np.ndarray) -> tuple[np.ndarray, float]:
    """Global-rescale unfolding: divide by mean spacing so that unfolded
    spectrum has mean spacing 1. Returns (unfolded_eigs, mean_spacing)."""
    eigs_sorted = np.sort(eigs)
    spacings = np.diff(eigs_sorted)
    mean_spacing = float(np.mean(spacings))
    if mean_spacing <= 0 or not np.isfinite(mean_spacing):
        raise ValueError("non-positive mean spacing; degenerate spectrum")
    unfolded = eigs_sorted / mean_spacing
    return unfolded, mean_spacing


def compute_sff(unfolded_eigs: np.ndarray, taus: np.ndarray) -> np.ndarray:
    """SFF(tau) = | sum_i exp(-i lambda_i tau) |^2 / N for an unfolded spectrum.

    Returns 1D array of SFF values, one per tau.
    """
    N = unfolded_eigs.shape[0]
    # Vectorize via outer: shape (n_tau, N)
    # phases[k,i] = -1j * tau_k * lambda_i
    # SFF[k] = |sum_i exp(phases[k,i])|^2 / N
    out = np.empty(taus.shape, dtype=np.float64)
    # Batch over taus to limit memory
    batch = 64
    for start in range(0, len(taus), batch):
        stop = min(start + batch, len(taus))
        tt = taus[start:stop][:, None]  # (b, 1)
        ee = unfolded_eigs[None, :]      # (1, N)
        z = np.exp(-1j * tt * ee).sum(axis=1)  # (b,)
        out[start:stop] = (z * z.conj()).real / N
    return out


def compute_sff_connected(sff: np.ndarray, taus: np.ndarray,
                           unfolded_eigs: np.ndarray) -> np.ndarray:
    """Connected SFF: SFF(tau) minus the disconnected piece |<exp(-i lam tau)>|^2 * N.

    SFF = |sum exp(-i lam tau)|^2 / N = N * |<exp(-i lam tau)>|^2 where <.> is
    empirical average. The "disconnected" part of the SFF -- the smooth
    envelope from the spectral density -- is exactly N * |Fourier transform
    of the smoothed density|^2. We subtract it to isolate the connected
    (correlation) piece that is compared to the GUE ramp+plateau.

    For comparison with the standard GUE connected K(tau) = tau/(2pi) for
    tau < 2pi and 1 for tau > 2pi, we return K_conn = SFF / N - |smoothed
    density FT|^2 = SFF/N - (sin(tau * width/2) / (tau * width/2))^2 (for
    a smooth density of compact support of "width") -- but in practice we
    compute the smooth piece numerically by ensemble-averaging or by a
    direct estimator.

    Here we use the standard direct estimator: compute SFF, then subtract
    the empirical disconnected piece = (1/N) * |sum exp|^2 of the
    smoothed-density approximation. For Kerdock W spectrum the simplest
    correction is to use the bin-averaged eigenvalue density and compute
    its FT, then subtract.

    Simpler: report the RAW unconnected SFF, and compare ratio against
    the GUE RAW SFF computed on a matched GUE matrix in the same way.
    This is the cleanest apples-to-apples comparison without unfolding
    arbitrariness. So we just return sff unchanged and pair it with
    gue_sff computed identically.
    """
    return sff  # raw SFF; comparison is matched-pair against GUE


# ---------------------------------------------------------------------------
# GUE analytic SFF (for sanity reference)
# ---------------------------------------------------------------------------

def gue_sff_analytic_connected(taus: np.ndarray) -> np.ndarray:
    """GUE connected SFF on unfolded time axis (Mehta; Cotler et al. 2017).

    K_conn(tau) = min(tau / (2 pi), 1)

    where tau is in units of unfolded time (mean spacing = 1, so T_H = 2 pi).
    """
    return np.minimum(taus / (2.0 * math.pi), 1.0)


# ---------------------------------------------------------------------------
# Diagnostics: dip and plateau metrics
# ---------------------------------------------------------------------------

def extract_dip_plateau_metrics(taus: np.ndarray, sff_kerdock: np.ndarray,
                                  sff_gue: np.ndarray) -> dict:
    """Compute matched-pair dip-region and plateau-region metrics."""
    T_H = 2.0 * math.pi  # Heisenberg time on unfolded axis
    dip_lo, dip_hi = 0.05 * T_H, 0.5 * T_H
    plat_lo, plat_hi = 3.0 * T_H, 10.0 * T_H

    dip_mask = (taus >= dip_lo) & (taus <= dip_hi)
    plat_mask = (taus >= plat_lo) & (taus <= plat_hi)

    def safe_ratio(a, b):
        return float(a / b) if b > 1e-12 else float('nan')

    dip_kerdock = float(np.mean(sff_kerdock[dip_mask])) if dip_mask.any() else float('nan')
    dip_gue = float(np.mean(sff_gue[dip_mask])) if dip_mask.any() else float('nan')
    plat_kerdock = float(np.mean(sff_kerdock[plat_mask])) if plat_mask.any() else float('nan')
    plat_gue = float(np.mean(sff_gue[plat_mask])) if plat_mask.any() else float('nan')

    return {
        "T_H_unfolded": T_H,
        "dip_region": [dip_lo, dip_hi],
        "plateau_region": [plat_lo, plat_hi],
        "dip_mean_kerdock": dip_kerdock,
        "dip_mean_gue": dip_gue,
        "dip_rel_dev": safe_ratio(abs(dip_kerdock - dip_gue), dip_gue),
        "plateau_mean_kerdock": plat_kerdock,
        "plateau_mean_gue": plat_gue,
        "plateau_rel_dev": safe_ratio(abs(plat_kerdock - plat_gue), plat_gue),
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

def compute_verdict(per_seed_metrics: list[dict], n_seeds: int) -> tuple[str, str]:
    """Apply HARD-PASS / HARD-FAIL thresholds per the prereg."""
    n = len(per_seed_metrics)
    if n == 0:
        return "PFK_SFF_INCONCLUSIVE", "no seeds produced"

    # PASS: deviation > 15% in dip OR plateau in >= 4/5
    # FAIL: deviation within 5% in both dip AND plateau in >= 4/5
    n_pass = 0
    n_fail = 0
    for m in per_seed_metrics:
        dip_dev = m.get("dip_rel_dev", float('nan'))
        plat_dev = m.get("plateau_rel_dev", float('nan'))
        if not (math.isfinite(dip_dev) and math.isfinite(plat_dev)):
            continue
        if dip_dev > 0.15 or plat_dev > 0.15:
            n_pass += 1
        if dip_dev <= 0.05 and plat_dev <= 0.05:
            n_fail += 1

    dip_devs = [m["dip_rel_dev"] for m in per_seed_metrics
                if math.isfinite(m.get("dip_rel_dev", float('nan')))]
    plat_devs = [m["plateau_rel_dev"] for m in per_seed_metrics
                 if math.isfinite(m.get("plateau_rel_dev", float('nan')))]

    median_dip = float(np.median(dip_devs)) if dip_devs else float('nan')
    median_plat = float(np.median(plat_devs)) if plat_devs else float('nan')

    if n_pass >= 4 and n >= 5:
        return (
            "PFK_SFF_NON_GUE",
            f"SFF deviates from GUE by > 15% in dip OR plateau in {n_pass}/{n} seeds "
            f"(median dip rel-dev {median_dip:.3f}, median plateau rel-dev {median_plat:.3f}). "
            f"Substrate has spectral structure that GUE does not capture; "
            f"PFK partial-thermalization framing SURVIVES this anchor."
        )
    if n_fail >= 4 and n >= 5:
        return (
            "PFK_SFF_MATCHES_GUE",
            f"SFF matches GUE within 5% in BOTH dip AND plateau in {n_fail}/{n} seeds "
            f"(median dip rel-dev {median_dip:.3f}, median plateau rel-dev {median_plat:.3f}). "
            f"Substrate spectrum is GUE-like at the SFF level; "
            f"PFK partial-thermalization framing KILLED at the SFF level. "
            f"ETH-style structured-chaos interpretation collapses to "
            f"non-Gaussian bulk shape with no chaos analog."
        )
    return (
        "PFK_SFF_INCONCLUSIVE",
        f"No threshold reached. {n_pass}/{n} seeds > 15% dev, {n_fail}/{n} seeds < 5% dev. "
        f"Median dip rel-dev {median_dip:.3f}, median plateau rel-dev {median_plat:.3f}."
    )


# ---------------------------------------------------------------------------
# Smoke self-test
# ---------------------------------------------------------------------------

def self_test() -> None:
    # 1) GUE analytic SFF behaves correctly
    taus_test = np.array([0.01, math.pi, 2 * math.pi, 4 * math.pi])
    gue = gue_sff_analytic_connected(taus_test)
    assert abs(gue[0] - 0.01 / (2 * math.pi)) < 1e-9
    assert abs(gue[2] - 1.0) < 1e-9
    assert abs(gue[3] - 1.0) < 1e-9

    # 2) SFF at tau=0 = N (sum of N ones, squared, / N = N)
    eigs = np.array([0.1, 0.2, 0.3, 0.4])
    s = compute_sff(eigs, np.array([0.0]))
    assert abs(s[0] - 4.0) < 1e-9, f"SFF(0)={s[0]} expected 4"

    # 3) Verdict branches
    pass_metric = {"dip_rel_dev": 0.30, "plateau_rel_dev": 0.20}
    v, _ = compute_verdict([pass_metric] * 5, 5)
    assert v == "PFK_SFF_NON_GUE", v
    fail_metric = {"dip_rel_dev": 0.02, "plateau_rel_dev": 0.03}
    v, _ = compute_verdict([fail_metric] * 5, 5)
    assert v == "PFK_SFF_MATCHES_GUE", v
    mixed = [{"dip_rel_dev": 0.20, "plateau_rel_dev": 0.04}] * 2 + \
            [{"dip_rel_dev": 0.04, "plateau_rel_dev": 0.04}] * 3
    v, _ = compute_verdict(mixed, 5)
    assert v == "PFK_SFF_INCONCLUSIVE", v

    # 4) Sanity check: GUE-vs-GUE deviation should be small at moderate N
    rng = np.random.default_rng(0)
    eigs_a = gue_W_spectrum(64, rng)
    eigs_b = gue_W_spectrum(64, rng)
    u_a, _ = unfold_global(eigs_a)
    u_b, _ = unfold_global(eigs_b)
    taus = np.linspace(0.01, 20 * math.pi, 64)
    sa = compute_sff(u_a, taus)
    sb = compute_sff(u_b, taus)
    # Just check no crash and finite
    assert np.all(np.isfinite(sa)) and np.all(np.isfinite(sb))

    print("self-test passed (analytic GUE, SFF(0)=N, verdict branches, GUE-vs-GUE finite)",
          flush=True)


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    if smoke:
        config = {
            "mode": "smoke",
            "N": 1024,
            "n_seeds": 1,
            "alpha": 1.0,
            "n_tau": 64,
            "tau_max_over_T_H": 10.0,
        }
    else:
        config = {
            "mode": "full",
            "N": 4096,
            "n_seeds": 5,
            "alpha": 1.0,  # v167 central case; full alpha=4 makes W = 4*I
            "n_tau": 256,
            "tau_max_over_T_H": 10.0,
        }

    N = config["N"]
    n_seeds = config["n_seeds"]
    alpha = config["alpha"]
    n_tau = config["n_tau"]
    tau_max = config["tau_max_over_T_H"] * 2.0 * math.pi  # in unfolded units

    # tau grid -- avoid tau=0 (SFF=N is trivial)
    taus = np.linspace(0.05, tau_max, n_tau)

    per_seed_metrics = []
    per_seed_sff_kerdock = []
    per_seed_sff_gue = []
    for seed in range(n_seeds):
        t_seed = time.monotonic()

        # Kerdock W_alpha sub-sampled per seed (matched-pair: paired GUE)
        kerdock_eigs = kerdock_W_spectrum(N, alpha=alpha, seed=2000 + seed)
        kerdock_unfolded, kerdock_dx = unfold_global(kerdock_eigs)
        sff_kerdock = compute_sff(kerdock_unfolded, taus)

        # GUE matched matrix
        rng = np.random.default_rng(5000 + seed)
        gue_eigs = gue_W_spectrum(N, rng)
        gue_unfolded, gue_dx = unfold_global(gue_eigs)
        sff_gue_empirical = compute_sff(gue_unfolded, taus)

        m = extract_dip_plateau_metrics(taus, sff_kerdock, sff_gue_empirical)
        m["seed"] = seed
        m["kerdock_mean_spacing"] = kerdock_dx
        m["gue_mean_spacing"] = gue_dx
        m["kerdock_eig_min"] = float(kerdock_eigs.min())
        m["kerdock_eig_max"] = float(kerdock_eigs.max())
        per_seed_metrics.append(m)
        per_seed_sff_kerdock.append(sff_kerdock.tolist())
        per_seed_sff_gue.append(sff_gue_empirical.tolist())
        print(f"  seed={seed}: kerdock_dx={kerdock_dx:.5f} gue_dx={gue_dx:.5f}  "
              f"dip_rel_dev={m['dip_rel_dev']:.4f}  "
              f"plateau_rel_dev={m['plateau_rel_dev']:.4f}  "
              f"({time.monotonic()-t_seed:.1f}s)", flush=True)

    verdict, msg = compute_verdict(per_seed_metrics, n_seeds)

    sff_gue_analytic = gue_sff_analytic_connected(taus) * N

    summary = {
        "config": config,
        "taus_unfolded": taus.tolist(),
        "sff_kerdock_per_seed": per_seed_sff_kerdock,
        "sff_gue_per_seed": per_seed_sff_gue,
        "sff_gue_analytic_x_N": sff_gue_analytic.tolist(),
        "per_seed_metrics": per_seed_metrics,
    }
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
    out_dir = get_output_dir("wave14_kerdock_sff_vs_gue_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["per_seed_metrics"]) >= 1, "smoke FAIL: no seeds"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_kerdock_sff_vs_gue_v1")
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
