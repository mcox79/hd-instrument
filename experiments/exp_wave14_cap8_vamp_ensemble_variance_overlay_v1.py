"""Cap 8 VAMP ensemble-variance overlay (Bet Z.5 S2 closure anchor).

Question
--------
Does VAMP-on-chain's K-trace empirical variance (across noise-seed
perturbations) Spearman-rank-correlate with per-coordinate reconstruction
error, at a level comparable to the absorbing-discrete-diffusion ensemble
estimator (Diao 2025, arXiv:2507.07586, reports Spearman rho = 0.996 vs
reconstruction error on WikiText-2)?

If YES (Spearman rho >= 0.50 in >= 3/5 codewords): Bet Z.5's distinguishing
per-coordinate-variance axis is recoverable from existing Cap 8 + cheap
ensemble overlay. Bet Z.5 closes by absorption into a Cap 8 envelope-extension
annotation; no fresh impl needed.

If NO (Spearman rho < 0.30 in >= 3/5 codewords): VAMP-ensemble variance is
not informative about per-coordinate reconstruction error. Bet Z.5's
distinguishing capability is genuinely additional; file S3 toy-scale fresh
impl as a NEW 🔬 row.

If MIDDLE (1-2 codewords pass, others don't): annotate Cap 8 with
'ensemble-variance overlay is partially informative'; Bet Z.5 stays 🔬
with reduced priority.

Protocol
--------
- Kerdock 4-coset codebook substrate, N=4096, alpha=0.5 (M=2048; in-capacity
  regime per cycle-127 Cap 8 validation envelope).
- 5 test codewords x_true, sampled from a Gaussian signal prior with
  signal_var=1.0 (matches existing Cap 8 protocol shape).
- For each codeword: run K=64 VAMP-on-chain traces, perturbing the noise
  realization seed across the K runs (channel matrix W and signal x_true are
  FIXED per codeword; only the channel noise z ~ N(0, sigma_sq * I) varies).
- After each VAMP run converges, record the final post-denoiser estimate
  x_hat_2 in R^N.
- Across the K=64 traces, compute per-coordinate empirical sample variance
  var_i = (1/K-1) * sum_k (x_hat_2[k, i] - mean(x_hat_2[:, i]))^2 for i in 1..N.
- Compute per-coordinate reconstruction error err_i = (mean(x_hat_2[:, i]) - x_true[i])^2.
- Spearman rank correlation rho = spearmanr(var_i, err_i) across N=4096 coords.
- Repeat for 5 codewords (each with its own x_true sampled from prior;
  shared channel W fixed across codewords for clean comparison).

Hard pass / hard fail / middle band
-----------------------------------
HARD PASS (Bet Z.5 closes as Cap 8 envelope-extension):
  Spearman rho >= 0.50 in >= 3/5 codewords.
HARD FAIL (Bet Z.5 stays as new fresh-impl row):
  Spearman rho < 0.30 in >= 3/5 codewords.
MIDDLE BAND:
  Anything else (1-2 codewords pass, others don't).

Self-tests
----------
1. VAMP IID Gaussian sanity (reused from Cap 8 v1c).
2. Ensemble variance analytical test: K=200 unit-Gaussian samples should
   have sample variance close to 1.0 (tolerance |est - 1.0| < 0.20).
3. Spearman rho monotonicity test: var = err + tiny noise -> rho approx 1.0.
4. Spearman rho null test: var independent of err -> rho approx 0.0 within
   sqrt(1/N) bound.
5. Verdict-branch test: synthetic per-codeword rho arrays -> expected verdict.

Smoke
-----
N=64, K=4, 1 codeword, Kerdock builder; verify per-coord variance is
computable end-to-end and matches the analytical test.

Pre-reg: preregs/2026-05-24_wave14_cap8_vamp_ensemble_variance_overlay_v1.md
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
from scipy.stats import spearmanr

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# Reuse Kerdock builder (already wired through kappa_profile_cross_codebook_v1).
_cc_path = REPO / "experiments" / "exp_wave14_kappa_profile_cross_codebook_v1.py"
_spec_cc = importlib.util.spec_from_file_location("cc_v1", _cc_path)
_cc = importlib.util.module_from_spec(_spec_cc)
_spec_cc.loader.exec_module(_cc)
build_kerdock = _cc.build_kerdock

# Reuse VAMP SE closed-form for sanity check.
_bv_path = REPO / "experiments" / "exp_wave14_bbmd_vamp_correspondence_sweep_v1.py"
_spec_bv = importlib.util.spec_from_file_location("bbmd_vamp_v1", _bv_path)
_bv = importlib.util.module_from_spec(_spec_bv)
_spec_bv.loader.exec_module(_bv)
vamp_se_closed = _bv.vamp_se_closed
amp_se_scalar = _bv.amp_se_scalar


# ---------------------------------------------------------------------------
# Standard VAMP loop (single trace; returns final post-denoiser estimate).
# Mirrors run_vamp_with_iterates from v1c but minimal: we only need x_hat_2.
# ---------------------------------------------------------------------------

def run_vamp_single(U: np.ndarray, s: np.ndarray, Vt: np.ndarray,
                    y: np.ndarray, signal_var: float, sigma_sq: float,
                    n_iter: int = 200) -> np.ndarray:
    """Run a single VAMP trace; return final x_hat_2 in R^N."""
    N = Vt.shape[1]
    K = len(s)
    s2 = s ** 2
    y_tilde = U.T @ y

    r_1 = np.zeros(N, dtype=np.float64)
    gamma_1 = 1.0 / signal_var

    mses_window: list[float] = []
    x_hat_2 = np.zeros(N, dtype=np.float64)

    for _ in range(n_iter):
        prec = s2 / sigma_sq + gamma_1
        var_per = 1.0 / prec
        Vtr1 = Vt @ r_1
        mean_per = var_per * (s * y_tilde / sigma_sq + gamma_1 * Vtr1)

        x_hat_signal = Vt.T @ mean_per
        null_r1 = r_1 - Vt.T @ (Vt @ r_1)
        x_hat = x_hat_signal + null_r1

        avg_post_var = (K / N) * float(np.mean(var_per)) + ((N - K) / N) * (1.0 / gamma_1)
        inv_var = 1.0 / max(avg_post_var, 1e-15)
        gamma_2 = max(inv_var - gamma_1, 1e-12)
        r_2 = (inv_var * x_hat - gamma_1 * r_1) / gamma_2

        post_var_den = 1.0 / (gamma_2 + 1.0 / signal_var)
        x_hat_2 = post_var_den * gamma_2 * r_2

        inv_var_den = 1.0 / post_var_den
        gamma_1_new = max(inv_var_den - gamma_2, 1e-12)
        r_1_new = (inv_var_den * x_hat_2 - gamma_2 * r_2) / gamma_1_new

        mses_window.append(float(np.linalg.norm(x_hat_2 - r_2) ** 2 / max(N, 1)))
        if len(mses_window) > 5:
            mses_window.pop(0)

        r_1 = r_1_new
        gamma_1 = gamma_1_new

        if len(mses_window) == 5 and (max(mses_window) - min(mses_window) < 1e-10):
            break

    return x_hat_2


# ---------------------------------------------------------------------------
# Ensemble overlay
# ---------------------------------------------------------------------------

def per_coordinate_variance(traces: np.ndarray) -> np.ndarray:
    """traces: (K, N) array of K independent VAMP final estimates.
    Returns per-coordinate sample variance (length N), unbiased estimator."""
    if traces.shape[0] < 2:
        raise ValueError("need K >= 2 for sample variance")
    return traces.var(axis=0, ddof=1)


def per_coordinate_reconstruction_error(traces: np.ndarray, x_true: np.ndarray) -> np.ndarray:
    """err_i = (mean(traces[:, i]) - x_true[i])^2."""
    means = traces.mean(axis=0)
    return (means - x_true) ** 2


def overlay_for_codeword(W: np.ndarray, U: np.ndarray, s: np.ndarray, Vt: np.ndarray,
                         x_true: np.ndarray, signal_var: float, sigma_sq: float,
                         K: int, base_seed: int, n_iter: int) -> dict:
    """Run K seed-perturbed VAMP traces for a fixed (W, x_true).

    Each trace draws an independent noise realization z ~ N(0, sigma_sq * I);
    the channel matrix W and signal x_true are fixed.
    """
    N = W.shape[1]
    M = W.shape[0]
    traces = np.zeros((K, N), dtype=np.float64)
    for k in range(K):
        rng_noise = np.random.default_rng(base_seed * 100003 + k * 1009)
        noise = rng_noise.standard_normal(M) * math.sqrt(sigma_sq)
        y = (W @ x_true) + noise
        x_hat_2 = run_vamp_single(U, s, Vt, y, signal_var, sigma_sq, n_iter=n_iter)
        traces[k, :] = x_hat_2

    var_per = per_coordinate_variance(traces)
    err_per = per_coordinate_reconstruction_error(traces, x_true)
    rho, pval = spearmanr(var_per, err_per)
    return {
        "spearman_rho": float(rho),
        "spearman_p": float(pval),
        "mean_var": float(var_per.mean()),
        "mean_err": float(err_per.mean()),
        "K": int(K),
        "N": int(N),
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

PASS_RHO = 0.50
FAIL_RHO = 0.30
PASS_COUNT = 3   # >= 3/5 codewords cross the line


def compute_verdict(summary: dict) -> tuple[str, str]:
    per_cw = summary.get("per_codeword") or []
    if len(per_cw) < 1:
        return ("ENSEMBLE_OVERLAY_INCONCLUSIVE", "no per-codeword results")
    n_total = len(per_cw)
    rhos = [r["spearman_rho"] for r in per_cw]
    finite = [r for r in rhos if math.isfinite(r)]
    if len(finite) < n_total:
        return ("ENSEMBLE_OVERLAY_INCONCLUSIVE",
                f"non-finite rho in {n_total - len(finite)}/{n_total} codewords")
    n_pass = sum(1 for r in rhos if r >= PASS_RHO)
    n_fail = sum(1 for r in rhos if r < FAIL_RHO)
    if n_pass >= PASS_COUNT:
        return (
            "ENSEMBLE_OVERLAY_PASS",
            f"Spearman rho >= {PASS_RHO} in {n_pass}/{n_total} codewords "
            f"(rhos={[round(r, 3) for r in rhos]}). Bet Z.5 closes by absorption: "
            f"Cap 8 + K-trace ensemble overlay captures the per-coordinate-variance axis "
            f"claimed novel by absorbing-discrete-diffusion (Diao 2025). Annotate Cap 8 "
            f"envelope-extension; no fresh Bet Z.5 impl required."
        )
    if n_fail >= PASS_COUNT:
        return (
            "ENSEMBLE_OVERLAY_FAIL",
            f"Spearman rho < {FAIL_RHO} in {n_fail}/{n_total} codewords "
            f"(rhos={[round(r, 3) for r in rhos]}). VAMP-ensemble variance is NOT "
            f"informative about per-coordinate reconstruction error. Bet Z.5's "
            f"per-coordinate-variance certificate is genuinely additional capability; "
            f"file S3 toy-scale fresh impl as a NEW 🔬 row."
        )
    return (
        "ENSEMBLE_OVERLAY_MIDDLE",
        f"Mixed: {n_pass}/{n_total} pass (rho>={PASS_RHO}); {n_fail}/{n_total} fail "
        f"(rho<{FAIL_RHO}); {n_total - n_pass - n_fail} between. rhos="
        f"{[round(r, 3) for r in rhos]}. Annotate Cap 8 as 'ensemble-variance overlay "
        f"is partially informative'; Bet Z.5 stays 🔬 with reduced priority."
    )


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------

def _self_test_ensemble_variance_analytical() -> None:
    """K=200 unit-Gaussian samples -> sample variance approx 1.0 per coord."""
    rng = np.random.default_rng(123)
    K_test = 200
    N_test = 1024
    traces = rng.standard_normal(size=(K_test, N_test))
    var = per_coordinate_variance(traces)
    mean_var = float(var.mean())
    assert abs(mean_var - 1.0) < 0.05, (
        f"ensemble variance analytical test: mean_var={mean_var:.4f} not within 0.05 of 1.0 "
        f"(K={K_test}, expected MC error ~ sqrt(2/K)={math.sqrt(2/K_test):.3f})"
    )


def _self_test_spearman_monotone() -> None:
    """If var = err + tiny noise -> rho approx 1.0."""
    rng = np.random.default_rng(7)
    N_test = 1000
    err = rng.uniform(0, 1, size=N_test)
    var = err + 0.01 * rng.standard_normal(N_test)
    rho, _ = spearmanr(var, err)
    assert rho > 0.99, f"monotone test: rho={rho:.4f} <= 0.99"


def _self_test_spearman_null() -> None:
    """If var independent of err -> |rho| < few/sqrt(N)."""
    rng = np.random.default_rng(11)
    N_test = 1000
    var = rng.uniform(0, 1, size=N_test)
    err = rng.uniform(0, 1, size=N_test)
    rho, _ = spearmanr(var, err)
    # 5 sigma bound for spearman under null: ~ 5 / sqrt(N) = 0.158
    assert abs(rho) < 0.20, f"null test: |rho|={abs(rho):.4f} >= 0.20"


def _self_test_verdict_branches() -> None:
    # PASS branch: 3/5 codewords with rho >= 0.5
    pc = [{"spearman_rho": r} for r in [0.55, 0.62, 0.80, 0.45, 0.20]]
    v, _ = compute_verdict({"per_codeword": pc})
    assert v == "ENSEMBLE_OVERLAY_PASS", f"PASS branch: got {v}"

    # FAIL branch: 3/5 codewords with rho < 0.3
    pc = [{"spearman_rho": r} for r in [0.10, 0.15, 0.20, 0.40, 0.55]]
    v, _ = compute_verdict({"per_codeword": pc})
    assert v == "ENSEMBLE_OVERLAY_FAIL", f"FAIL branch: got {v}"

    # MIDDLE branch: 1 pass, 1 fail, 3 in-between
    pc = [{"spearman_rho": r} for r in [0.55, 0.20, 0.35, 0.40, 0.45]]
    v, _ = compute_verdict({"per_codeword": pc})
    assert v == "ENSEMBLE_OVERLAY_MIDDLE", f"MIDDLE branch: got {v}"

    # MIDDLE branch: 2 pass (under threshold of 3)
    pc = [{"spearman_rho": r} for r in [0.55, 0.62, 0.35, 0.40, 0.45]]
    v, _ = compute_verdict({"per_codeword": pc})
    assert v == "ENSEMBLE_OVERLAY_MIDDLE", f"MIDDLE (2-pass) branch: got {v}"

    # INCONCLUSIVE branch: non-finite rho
    pc = [{"spearman_rho": float("nan")}, {"spearman_rho": 0.6}]
    v, _ = compute_verdict({"per_codeword": pc})
    assert v == "ENSEMBLE_OVERLAY_INCONCLUSIVE", f"INCONCLUSIVE branch: got {v}"


def _self_test_vamp_iid_sanity() -> None:
    """VAMP on iid Gaussian: final estimate's MSE should be near AMP-SE."""
    N_test, M_test = 128, 128
    signal_var = 1.0
    sigma_sq = 0.04
    rng = np.random.default_rng(7)
    W = (rng.standard_normal(size=(M_test, N_test)) / math.sqrt(N_test)).astype(np.float64)
    U, s, Vt = np.linalg.svd(W, full_matrices=False)
    x_true = rng.standard_normal(N_test) * math.sqrt(signal_var)
    noise = rng.standard_normal(M_test) * math.sqrt(sigma_sq)
    y = W @ x_true + noise
    x_hat_2 = run_vamp_single(U, s, Vt, y, signal_var, sigma_sq, n_iter=100)
    mse = float(np.mean((x_hat_2 - x_true) ** 2))
    amp_pred = amp_se_scalar(M_test / N_test, sigma_sq, signal_var)
    rel = abs(mse - amp_pred) / max(mse, amp_pred, 1e-9)
    assert rel < 0.20, f"VAMP iid sanity: mse={mse:.5f} vs amp_pred={amp_pred:.5f} rel_err={rel:.3f}"


def self_test() -> None:
    _self_test_ensemble_variance_analytical()
    _self_test_spearman_monotone()
    _self_test_spearman_null()
    _self_test_verdict_branches()
    _self_test_vamp_iid_sanity()
    print("self_test passed (5 cases: ensemble-var analytical, monotone, null, verdict-branches, vamp-iid-sanity)", flush=True)


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()
    if smoke:
        config = {
            "mode": "smoke",
            "codebook": "kerdock",
            "N": 1024,   # Kerdock 4-coset requires N=2^k for even k; t=5 smallest
            "alpha": 0.5,
            "n_codewords": 1,
            "K": 4,
            "signal_var": 1.0,
            "sigma_noise": 0.1,
            "n_iter": 50,
            "base_seed": 13,
        }
    else:
        config = {
            "mode": "full",
            "codebook": "kerdock",
            "N": 4096,
            "alpha": 0.5,
            "n_codewords": 5,
            "K": 64,
            "signal_var": 1.0,
            "sigma_noise": 0.1,
            "n_iter": 200,
            "base_seed": 13,
        }
    N = config["N"]
    M = max(1, int(round(config["alpha"] * N)))
    config["M"] = M
    print(f"[setup] codebook={config['codebook']} N={N} M={M} alpha={config['alpha']} "
          f"K={config['K']} n_codewords={config['n_codewords']}", flush=True)

    # Build Kerdock channel matrix W (M, N).
    t_build = time.monotonic()
    W = build_kerdock(N, M, config["base_seed"]).astype(np.float64)
    print(f"  built Kerdock W shape={W.shape} dt={time.monotonic() - t_build:.2f}s", flush=True)

    # Cache SVD (re-used across all K traces + all codewords).
    t_svd = time.monotonic()
    U, s, Vt = np.linalg.svd(W, full_matrices=False)
    print(f"  SVD cached dt={time.monotonic() - t_svd:.2f}s", flush=True)

    sigma_sq = config["sigma_noise"] ** 2
    signal_var = config["signal_var"]

    per_codeword: list[dict] = []
    for cw_idx in range(config["n_codewords"]):
        t_cw = time.monotonic()
        # Sample x_true from Gaussian prior; per-codeword seed lineage.
        rng_signal = np.random.default_rng(config["base_seed"] + 7 * (cw_idx + 1))
        x_true = rng_signal.standard_normal(N) * math.sqrt(signal_var)

        result = overlay_for_codeword(
            W, U, s, Vt, x_true, signal_var, sigma_sq,
            K=config["K"],
            base_seed=config["base_seed"] + 1000 * (cw_idx + 1),
            n_iter=config["n_iter"],
        )
        result["codeword_idx"] = cw_idx
        per_codeword.append(result)
        print(f"  cw={cw_idx} K={config['K']} spearman_rho={result['spearman_rho']:.4f} "
              f"p={result['spearman_p']:.2e} mean_var={result['mean_var']:.5f} "
              f"mean_err={result['mean_err']:.5f} dt={time.monotonic() - t_cw:.2f}s",
              flush=True)

    rhos = [r["spearman_rho"] for r in per_codeword]
    summary = {
        "per_codeword": per_codeword,
        "spearman_rhos": rhos,
        "n_pass_rho_ge_0p50": sum(1 for r in rhos if r >= PASS_RHO),
        "n_fail_rho_lt_0p30": sum(1 for r in rhos if r < FAIL_RHO),
        "vamp_se_pred_mse": float(vamp_se_closed(s, N, M, sigma_sq, signal_var)),
        "config": config,
    }
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


# ---------------------------------------------------------------------------
# Metrics + I/O
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
    self_test()
    out_dir = get_output_dir("wave14_cap8_vamp_ensemble_variance_overlay_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["per_codeword"]) >= 1, "smoke FAIL: no per-codeword result"
    rho = summary["per_codeword"][0]["spearman_rho"]
    assert math.isfinite(rho) or math.isnan(rho), "smoke: rho must be a number"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_cap8_vamp_ensemble_variance_overlay_v1")
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
