"""Spectral universality (Dudeja-Sen-Lu 2023) at Kerdock M/N up to 8.

Tests whether substrate's Kerdock measurement matrix lies inside the
Dudeja-Sen-Lu spectral-universality class (arXiv:2208.02753, IEEE TIT 2023),
which accommodates structured DETERMINISTIC sensing matrices beyond RUI.

Mechanism:
  For each M/N in {0.5, 1, 2, 4, 8}:
    1. Build Kerdock 4-coset measurement matrix W_k (M x N).
    2. Build 3 spectrum/structure surrogates:
       (a) iid_gaussian: A_g with iid N(0, 1/N) entries; same M, N.
       (b) random_sign_hadamard: random +-1 sign-flip + Hadamard rows,
           same M, N.
       (c) haar_kerdock_spectrum: U * diag(sigma_k) * V^T with sigma_k =
           Kerdock's empirical singular spectrum (so spectrum is exactly
           matched), U, V drawn from Haar(M), Haar(N).
    3. Run AMP (matched Gaussian denoiser) on all 4 matrices for n_seeds.
    4. Record AMP-MSE for each (M/N, family).
    5. Compute pairwise % deviation Kerdock vs each surrogate.

Decision rule (Dudeja-Sen-Lu lens):
  HARD PASS  -- Cap 8 envelope extends to M/N=8 via Dudeja-Sen-Lu:
     Kerdock AMP-MSE matches AT LEAST ONE of the 3 surrogates within +-25%
     across ALL 5 M/N cells.  Means Kerdock is "in-class" with that
     surrogate's universality regime.

  HARD FAIL  -- test inconclusive:
     The 3 surrogates disagree with each other by >25% on at least one M/N.
     No clean baseline -> can't classify Kerdock.

  MIDDLE BAND -- Cap 12 novel non-universality finding:
     Surrogates agree (test informative), but Kerdock disagrees with ALL 3
     of them by >25% on at least one M/N.  Substrate is genuinely outside
     Dudeja-Sen-Lu's surrogate class.

Verdict labels:
   KERDOCK_UNIVERSALITY_IN_CLASS
   KERDOCK_UNIVERSALITY_NOVEL_OUT_OF_CLASS
   KERDOCK_UNIVERSALITY_TEST_INCONCLUSIVE

Pre-reg: preregs/2026-05-24_wave14_spectral_universality_kerdock_v1.md
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
# Import Kerdock codebook builder from v3
_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
_spec = importlib.util.spec_from_file_location("kerdock_v3", _v3_path)
_v3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v3)
make_kerdock_4coset_codebook = _v3.make_kerdock_4coset_codebook

try:
    import torch
    _TORCH_OK = True
except ImportError:
    _TORCH_OK = False


# ---------------------------------------------------------------------------
# Matrix family builders (each returns A normalized so A^T A / N has unit-ish
# bulk eigenvalue scale, matching AMP-SE conventions used in v1 of the
# Kerdock anchor)
# ---------------------------------------------------------------------------

def _build_kerdock(N: int, M: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Kerdock 4-coset codebook, subsample M rows. Returns (A_norm, sigma).

    A_norm = A / sqrt(N) with A entries in {-1, +1}, so each row has unit L2
    norm in expectation and (A_norm)^T (A_norm) has same scale as
    (1/N) A^T A. sigma = singular values of A_norm.
    """
    if not _TORCH_OK:
        raise RuntimeError("torch required for Kerdock codebook builder")

    device = torch.device("cpu")
    cb, _info = make_kerdock_4coset_codebook(N, device)  # (4N, N) bipolar
    K = cb.shape[0]
    if M > K:
        # repeat-without-replacement: cycle through codewords
        rng = np.random.default_rng(seed)
        idx_pool = np.tile(np.arange(K), int(np.ceil(M / K)))
        idx = rng.permutation(idx_pool)[:M]
    else:
        rng = np.random.default_rng(seed)
        idx = rng.choice(K, size=M, replace=False)
    A_t = cb[idx].float()
    A = A_t.numpy()
    A_norm = A / math.sqrt(N)
    s = np.linalg.svd(A_norm, compute_uv=False)
    return A_norm, s


def _build_iid_gaussian(N: int, M: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """A_norm with iid N(0, 1/N) entries; same M, N."""
    rng = np.random.default_rng(seed)
    A_norm = rng.standard_normal(size=(M, N)) / math.sqrt(N)
    s = np.linalg.svd(A_norm, compute_uv=False)
    return A_norm, s


def _build_random_sign_hadamard(N: int, M: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Random-sign Hadamard: D2 * H_N * D1 then subsample/replicate rows.

    H_N: Walsh-Hadamard matrix (Sylvester construction, N must be power of 2).
    D1: diagonal random +-1 (N x N).
    D2: diagonal random +-1 (M x M) (acts on rows after subsampling).
    Then subsample (if M<=N) or cyclic-repeat-with-fresh-signs (if M>N).

    The rows are all unit Walsh-Hadamard rows times random signs; entries
    are in {-1/sqrt(N), +1/sqrt(N)} so A_norm rows have unit L2 norm.
    """
    if N & (N - 1) != 0:
        raise ValueError(f"N must be power of 2 for Hadamard surrogate; got {N}")
    rng = np.random.default_rng(seed)
    # Build Walsh-Hadamard via Sylvester construction
    H = np.array([[1.0]])
    while H.shape[0] < N:
        H = np.block([[H, H], [H, -H]])
    H = H / math.sqrt(N)  # normalize so rows are unit L2
    # Right-side column signs D1: same as flipping columns of H
    d1 = rng.choice([-1.0, 1.0], size=N)
    H_signed = H * d1[None, :]  # (N, N), each col scaled by +-1
    # Row selection: subsample with replacement to allow M > N (random rows)
    # If M <= N, subsample without replacement
    if M <= N:
        idx = rng.choice(N, size=M, replace=False)
    else:
        idx = rng.choice(N, size=M, replace=True)
    A = H_signed[idx, :]  # (M, N)
    # Left-side row signs D2 to further randomize when M > N (rows repeat)
    d2 = rng.choice([-1.0, 1.0], size=M)
    A_norm = A * d2[:, None]
    s = np.linalg.svd(A_norm, compute_uv=False)
    return A_norm, s


def _build_haar_with_spectrum(N: int, M: int, sigma_target: np.ndarray,
                              seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Build U * diag(sigma_target) * V^T with U, V Haar.

    Constructs A_norm whose singular values exactly equal sigma_target (truncated
    or padded to min(M, N) entries) and whose singular vectors are uniform on
    the orthogonal groups O(M), O(N) respectively.
    """
    rng = np.random.default_rng(seed)
    k = min(M, N)
    # Truncate/pad sigma_target to length k
    if len(sigma_target) >= k:
        sigma = np.sort(sigma_target)[::-1][:k].copy()
    else:
        sigma = np.zeros(k)
        sigma[: len(sigma_target)] = np.sort(sigma_target)[::-1]

    # Haar U (M x k) via QR of Gaussian
    def haar_truncated(d: int, k_: int) -> np.ndarray:
        G = rng.standard_normal(size=(d, k_))
        Q, R = np.linalg.qr(G)
        # Make sign-canonical so U is exactly Haar
        signs = np.sign(np.diag(R))
        signs[signs == 0] = 1.0
        return Q * signs[None, :]

    U = haar_truncated(M, k)
    V = haar_truncated(N, k)
    # A_norm = U * diag(sigma) * V^T, shape (M, N)
    A_norm = (U * sigma[None, :]) @ V.T
    s = np.linalg.svd(A_norm, compute_uv=False)
    return A_norm, s


# ---------------------------------------------------------------------------
# Empirical AMP (matched Gaussian denoiser; mirrors v1 anchor)
# ---------------------------------------------------------------------------

def run_empirical_amp(A: np.ndarray, x_true: np.ndarray, sigma_noise: float,
                      n_iter: int = 200) -> dict:
    """AMP on measurement matrix A; matched Gaussian denoiser."""
    M, N = A.shape
    alpha = M / N
    signal_var = float(np.var(x_true))
    if signal_var < 1e-12:
        signal_var = 1.0

    rng_obs = np.random.default_rng(0xC0FFEE ^ M ^ N)
    y = A @ x_true + sigma_noise * rng_obs.standard_normal(M)

    x_hat = np.zeros(N)
    z = y.copy()
    mse_history = []

    for it in range(n_iter):
        r = A.T @ z + x_hat
        tau_sq_eff = float(np.mean(z ** 2)) / alpha
        tau_sq_eff = max(tau_sq_eff, 1e-10)
        gain = signal_var / (signal_var + tau_sq_eff)
        x_hat_new = gain * r
        b = gain
        z = y - A @ x_hat_new + b * z * (1.0 / alpha)
        x_hat = x_hat_new
        mse = float(np.mean((x_hat - x_true) ** 2))
        mse_history.append(mse)
        if it >= 5:
            recent = mse_history[-5:]
            if max(recent) - min(recent) < 1e-10:
                break

    mse_final = mse_history[-1] if mse_history else float("inf")
    return {
        "mse_history": mse_history,
        "mse_final": float(mse_final),
        "n_iters": len(mse_history),
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

VERDICT_IN_CLASS = "KERDOCK_UNIVERSALITY_IN_CLASS"
VERDICT_NOVEL = "KERDOCK_UNIVERSALITY_NOVEL_OUT_OF_CLASS"
VERDICT_INCONCLUSIVE = "KERDOCK_UNIVERSALITY_TEST_INCONCLUSIVE"

SURROGATE_NAMES = ("iid_gaussian", "random_sign_hadamard", "haar_kerdock_spectrum")
TAU = 0.25  # +-25% threshold


def _pair_rel_diff(a: float, b: float) -> float:
    denom = max(abs(a), abs(b), 1e-12)
    return abs(a - b) / denom


def compute_verdict(cells: list[dict], tau: float = TAU) -> tuple[str, str]:
    """Apply Dudeja-Sen-Lu decision rule.

    cells: list of per-(M/N) dicts each with key 'mse_mean' mapping
           family name -> mean AMP-MSE across seeds. Must include 'kerdock';
           surrogate set is whatever family keys (other than kerdock) appear.
    """
    if not cells:
        return (VERDICT_INCONCLUSIVE, "no cells produced")

    # Determine surrogate set from the first cell's keys.
    present_surrogates = tuple(
        k for k in cells[0]["mse_mean"].keys() if k != "kerdock"
    )
    if not present_surrogates:
        return (VERDICT_INCONCLUSIVE, "no surrogates present in cells")

    # Step 1: check surrogate agreement on every cell.
    bad_surrogate_alphas = []
    for cell in cells:
        mse = cell["mse_mean"]
        # All pairwise diffs among surrogates
        pair_diffs = []
        for i, a in enumerate(present_surrogates):
            for b in present_surrogates[i + 1:]:
                pair_diffs.append(_pair_rel_diff(mse[a], mse[b]))
        cell["surrogate_max_pair_diff"] = max(pair_diffs) if pair_diffs else 0.0
        if cell["surrogate_max_pair_diff"] > tau:
            bad_surrogate_alphas.append((cell["alpha"], cell["surrogate_max_pair_diff"]))

    if bad_surrogate_alphas:
        return (
            VERDICT_INCONCLUSIVE,
            f"surrogates disagree among themselves by >{int(tau*100)}% at "
            f"M/N in {bad_surrogate_alphas}; no clean baseline. "
            f"Dudeja-Sen-Lu test is uninformative on these cells.",
        )

    # Step 2: surrogates agree everywhere. Now check Kerdock vs each surrogate
    # per cell. For HARD PASS we need at least one surrogate that matches
    # Kerdock within +-tau across ALL cells.
    n_cells = len(cells)
    matches_per_surrogate = {s: 0 for s in present_surrogates}
    worst_cell_diff = {s: 0.0 for s in present_surrogates}
    for cell in cells:
        mse = cell["mse_mean"]
        cell["kerdock_vs_surrogate_diff"] = {}
        for s in present_surrogates:
            d = _pair_rel_diff(mse["kerdock"], mse[s])
            cell["kerdock_vs_surrogate_diff"][s] = d
            if d <= tau:
                matches_per_surrogate[s] += 1
            if d > worst_cell_diff[s]:
                worst_cell_diff[s] = d

    in_class_surrogates = [s for s, c in matches_per_surrogate.items() if c == n_cells]
    if in_class_surrogates:
        return (
            VERDICT_IN_CLASS,
            f"Kerdock AMP-MSE matches surrogate(s) {in_class_surrogates} within "
            f"+-{int(tau*100)}% across all {n_cells} M/N cells. Cap 8 envelope "
            f"extends to M/N=8 via Dudeja-Sen-Lu spectral universality.",
        )

    # Otherwise: is Kerdock OUT of class (disagrees with ALL 3 surrogates by
    # >tau on at least one cell)?
    out_of_class_cells = []
    for cell in cells:
        diffs = cell["kerdock_vs_surrogate_diff"]
        if all(d > tau for d in diffs.values()):
            out_of_class_cells.append((cell["alpha"], diffs))

    if out_of_class_cells:
        return (
            VERDICT_NOVEL,
            f"Kerdock disagrees with ALL 3 surrogates by >{int(tau*100)}% at "
            f"M/N in {[c[0] for c in out_of_class_cells]}. Substrate is "
            f"genuinely outside Dudeja-Sen-Lu's surrogate class. "
            f"Cap 12 promotes to novel non-universality annotation.",
        )

    # Mixed: Kerdock partially matches some surrogates but not all-cell match
    # for any single surrogate -> inconclusive (between bands)
    best_s = min(worst_cell_diff, key=worst_cell_diff.get)
    return (
        VERDICT_INCONCLUSIVE,
        f"Kerdock partially matches surrogates but no single surrogate is "
        f"within +-{int(tau*100)}% across all {n_cells} cells. Closest: "
        f"{best_s} (worst diff {worst_cell_diff[best_s]:.3f}). Mixed band; "
        f"neither HARD PASS nor HARD FAIL.",
    )


def self_test_verdict() -> None:
    """Hand-crafted cases for compute_verdict."""
    SUR = SURROGATE_NAMES
    # Case 1: HARD PASS via iid_gaussian
    cells_pass = [
        {"alpha": a, "mse_mean": {"kerdock": 0.10, SUR[0]: 0.11, SUR[1]: 0.13, SUR[2]: 0.12}}
        for a in [0.5, 1.0, 2.0, 4.0, 8.0]
    ]
    v, _ = compute_verdict(cells_pass)
    assert v == VERDICT_IN_CLASS, f"case1 fail: {v}"

    # Case 2: HARD FAIL via surrogate-disagreement at one cell
    cells_fail = [
        {"alpha": a, "mse_mean": {"kerdock": 0.10, SUR[0]: 0.10, SUR[1]: 0.11, SUR[2]: 0.10}}
        for a in [0.5, 1.0, 2.0, 4.0]
    ]
    cells_fail.append({"alpha": 8.0, "mse_mean": {"kerdock": 0.10, SUR[0]: 0.10, SUR[1]: 0.50, SUR[2]: 0.11}})
    v, _ = compute_verdict(cells_fail)
    assert v == VERDICT_INCONCLUSIVE, f"case2 fail: {v}"

    # Case 3: MIDDLE BAND (novel out-of-class) — Kerdock far from ALL surrogates at M/N=8
    cells_novel = [
        {"alpha": a, "mse_mean": {"kerdock": 0.10, SUR[0]: 0.10, SUR[1]: 0.11, SUR[2]: 0.10}}
        for a in [0.5, 1.0, 2.0, 4.0]
    ]
    cells_novel.append({"alpha": 8.0, "mse_mean": {"kerdock": 0.40, SUR[0]: 0.10, SUR[1]: 0.11, SUR[2]: 0.10}})
    v, _ = compute_verdict(cells_novel)
    assert v == VERDICT_NOVEL, f"case3 fail: {v}"

    # Case 4: Mixed (partial match) — should be INCONCLUSIVE
    cells_mixed = [
        {"alpha": 0.5, "mse_mean": {"kerdock": 0.10, SUR[0]: 0.10, SUR[1]: 0.10, SUR[2]: 0.10}},
        {"alpha": 8.0, "mse_mean": {"kerdock": 0.20, SUR[0]: 0.10, SUR[1]: 0.18, SUR[2]: 0.11}},
    ]
    v, _ = compute_verdict(cells_mixed)
    assert v == VERDICT_INCONCLUSIVE, f"case4 fail: {v}"

    # Case 5: Empty
    v, _ = compute_verdict([])
    assert v == VERDICT_INCONCLUSIVE, f"case5 fail: {v}"

    print("verdict self-test passed (5/5 cases)", flush=True)


def self_test_surrogate_spectrum(N: int = 64) -> None:
    """Sanity-check each surrogate produces correct singular spectrum.

    Verifies:
      - iid Gaussian: spectrum approx Marchenko-Pastur edge for given M/N
      - random-sign Hadamard with M<=N: all singular values == 1 (orthonormal rows)
      - Haar with target spectrum: returned sigma matches target within 1e-6
    """
    M = N  # square case
    _, sig_g = _build_iid_gaussian(N, M, seed=0)
    # MP bulk edge for square Gaussian/sqrt(N): support in [0, 2], roughly
    assert sig_g.min() >= 0.0 and sig_g.max() <= 4.0, \
        f"iid Gaussian spectrum out of range: min={sig_g.min()}, max={sig_g.max()}"

    _, sig_h = _build_random_sign_hadamard(N, M, seed=0)
    # When M==N (no row subsampling), DH is orthogonal -> all sigma == 1
    assert np.allclose(sig_h, 1.0, atol=1e-10), \
        f"random-sign Hadamard square: expected sigma==1, got [{sig_h.min()}, {sig_h.max()}]"

    # Haar with given spectrum
    target = np.linspace(0.5, 2.0, M)
    _, sig_h2 = _build_haar_with_spectrum(N, M, sigma_target=target, seed=0)
    sig_h2_sorted = np.sort(sig_h2)[::-1]
    target_sorted = np.sort(target)[::-1]
    assert np.allclose(sig_h2_sorted, target_sorted, atol=1e-6), \
        f"Haar surrogate spectrum mismatch: max diff = {np.max(np.abs(sig_h2_sorted - target_sorted))}"

    # Sub-square random-sign Hadamard (M < N): rows are still orthonormal so
    # all M singular values should be 1.
    M_sub = N // 2
    _, sig_h3 = _build_random_sign_hadamard(N, M_sub, seed=0)
    assert np.allclose(sig_h3, 1.0, atol=1e-10), \
        f"random-sign Hadamard M<N: expected sigma==1, got [{sig_h3.min()}, {sig_h3.max()}]"

    print("surrogate-spectrum self-test passed (4/4 cases)", flush=True)


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    if smoke:
        config = {
            "mode": "smoke",
            "N": 1024,  # smallest Kerdock-supporting power-of-2 (even log2 N)
            "M_over_N_list": [0.5, 1.0],
            "signal_var": 1.0,
            "sigma_noise": 0.1,
            "n_seeds": 1,
            "amp_n_iter": 50,
            # smoke uses only iid_gaussian to keep it fast; full run uses all 3
            "surrogates": ("iid_gaussian",),
        }
    else:
        config = {
            "mode": "full",
            "N": 4096,
            "M_over_N_list": [0.5, 1.0, 2.0, 4.0, 8.0],
            "signal_var": 1.0,
            "sigma_noise": 0.1,
            "n_seeds": 5,
            "amp_n_iter": 200,
            "surrogates": SURROGATE_NAMES,
        }

    N = config["N"]
    sigma_noise = config["sigma_noise"]
    signal_var = config["signal_var"]
    surrogates = config["surrogates"]
    rng_signal = np.random.default_rng(42)

    cells = []
    for alpha in config["M_over_N_list"]:
        M = max(1, int(alpha * N))
        print(f"\n[alpha={alpha:.2f}] N={N} M={M}", flush=True)

        mse_by_family = {"kerdock": [], **{s: [] for s in surrogates}}
        sigma_summary = {"kerdock": []}  # store mean/max sigma for sanity
        for s in surrogates:
            sigma_summary[s] = []

        for seed in range(config["n_seeds"]):
            seed_base = seed * 1000 + int(alpha * 100)
            x_true = rng_signal.standard_normal(N) * math.sqrt(signal_var)

            # Kerdock
            A_k, s_k = _build_kerdock(N, M, seed=seed_base)
            emp_k = run_empirical_amp(A_k, x_true, sigma_noise,
                                      n_iter=config["amp_n_iter"])
            mse_by_family["kerdock"].append(emp_k["mse_final"])
            sigma_summary["kerdock"].append((float(s_k.mean()),
                                              float(s_k.max()),
                                              float(s_k.min())))

            # Surrogates
            for s in surrogates:
                if s == "iid_gaussian":
                    A_s, sig_s = _build_iid_gaussian(N, M, seed=seed_base + 1)
                elif s == "random_sign_hadamard":
                    A_s, sig_s = _build_random_sign_hadamard(N, M, seed=seed_base + 2)
                elif s == "haar_kerdock_spectrum":
                    A_s, sig_s = _build_haar_with_spectrum(N, M, sigma_target=s_k,
                                                            seed=seed_base + 3)
                else:
                    raise ValueError(f"unknown surrogate: {s}")
                emp_s = run_empirical_amp(A_s, x_true, sigma_noise,
                                          n_iter=config["amp_n_iter"])
                mse_by_family[s].append(emp_s["mse_final"])
                sigma_summary[s].append((float(sig_s.mean()),
                                          float(sig_s.max()),
                                          float(sig_s.min())))

            kvals = " ".join(
                f"{k}={mse_by_family[k][-1]:.5f}"
                for k in ["kerdock"] + list(surrogates)
            )
            print(f"  seed={seed} {kvals}", flush=True)

        cell = {
            "alpha": alpha,
            "N": N,
            "M": M,
            "mse_mean": {fam: float(np.mean(v)) for fam, v in mse_by_family.items()},
            "mse_std": {fam: float(np.std(v)) for fam, v in mse_by_family.items()},
            "sigma_summary": {fam: v for fam, v in sigma_summary.items()},
        }
        cells.append(cell)
        print(
            f"  AGGREGATE alpha={alpha:.2f}: "
            + " ".join(f"{k}={cell['mse_mean'][k]:.5f}"
                       for k in ["kerdock"] + list(surrogates)),
            flush=True,
        )

    summary = {"cells": cells, "config": config}
    verdict, msg = compute_verdict(cells)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


# ---------------------------------------------------------------------------
# Output / metrics
# ---------------------------------------------------------------------------

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
    self_test_verdict()
    self_test_surrogate_spectrum(N=64)
    out_dir = get_output_dir("wave14_spectral_universality_kerdock_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["cells"]) >= 1, "smoke FAIL: no cells produced"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test_verdict()
    self_test_surrogate_spectrum(N=64)
    out_dir = get_output_dir("wave14_spectral_universality_kerdock_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict()
        self_test_surrogate_spectrum(N=64)
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
