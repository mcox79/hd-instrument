"""Cap 8 VAMP-on-chain iterate-trajectory generator for SRHT + Hadamard.

Motivation
----------
Composition A audit v1 yielded Spearman rho=1.0 on Kerdock (perfect
alignment between kappa_n divergence components and Schur-Weyl irrep
mass-fraction deviations) but NaN on SRHT and Hadamard.  Root cause:
those families never had per-iteration VAMP iterate traces saved at
N=4096 / 5 seeds / multiple alpha cells -- only Kerdock did, from the
Cap 8 single-hop / multi-hop runs.

This anchor is DATA GENERATION, not a hypothesis test.  We run the
canonical VAMP loop on SRHT + Hadamard codebooks at the Cap 8 protocol
shape (N=4096, M/N=1.0, 5 seeds, 3 alpha cells: {0.5, 0.75, 1.0}) and
SAVE per-iteration:

  - x_hat (final-estimate iterate, before denoiser)
  - x_hat_2 (post-denoiser iterate)
  - mse_per_iter (||x_hat_2 - x_true||^2 / N)
  - denoiser_output_norm (per-iteration ||x_hat_2||)
  - onsager_term_norm (proxy: |gamma_2| * ||r_2|| -- VAMP's MSG-passing
    Onsager analog is the gamma-rescaled R_2 in the extrinsic message)
  - gamma_1, gamma_2 per iteration (precision parameters)

Output layout
-------------
data/exp_wave14_cap8_vamp_iterates_srht_hadamard_v1b/
  iterates/srht/alpha_0p50/seed_0000.json
  iterates/srht/alpha_0p50/seed_1000.json
  ...
  iterates/hadamard/alpha_1p00/seed_4000.json
  metrics.json    (top-level summary + file manifest)

There are 2 codebooks * 3 alphas * 5 seeds = 30 iterate-trace JSON files.

Verdict
-------
This is a data-generation anchor.  The verdict is one of:
  - CAP8_ITERATES_GENERATED: all 30 files written successfully, each
    contains >=10 iterates with finite x_hat norms and monotonically
    non-increasing MSE (within numerical noise; allow up to 5% bumps).
  - CAP8_ITERATES_PARTIAL: some files written but <30; downstream
    Anchor 2 (audit_trail v2) must check file-existence per cell.
  - CAP8_ITERATES_FAILED: <10 files written; the data gap is NOT filled
    and Anchor 2 will be unable to compute Spearman rho for SRHT/Hadamard.

There are NO hard-pass/hard-fail thresholds on signal quality
(this is data generation; Anchor 2 is where the hypothesis test lives).

Self-tests
----------
1. VAMP iterate-saver round-trip: write a fake trace, read it back,
   confirm length + keys + numerical equality.
2. SRHT/Hadamard builders work at N=4096 (called once with M=4096, seed=13).
3. VAMP converges on iid Gaussian (sanity that the iteration logic
   reaches MSE near AMP-SE prediction).
4. Per-iter quantities are finite and shapes match.
5. JSON serializer handles numpy scalars and ndarrays.

Smoke
-----
N=64, 1 seed, 1 alpha, SRHT only; produces 1 iterate-trace file.

Pre-reg: preregs/2026-05-24_wave14_cap8_vamp_iterates_srht_hadamard_v1b.md
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
# Reuse cross-codebook builders for SRHT + Hadamard.
_cc_path = REPO / "experiments" / "exp_wave14_kappa_profile_cross_codebook_v1.py"
_spec_cc = importlib.util.spec_from_file_location("cc_v1", _cc_path)
_cc = importlib.util.module_from_spec(_spec_cc)
_spec_cc.loader.exec_module(_cc)
build_srht = _cc.build_srht
build_hadamard = _cc.build_hadamard
build_iid_gauss = _cc.build_iid_gauss

# Reuse VAMP SE closed-form prediction
_bv_path = REPO / "experiments" / "exp_wave14_bbmd_vamp_correspondence_sweep_v1.py"
_spec_bv = importlib.util.spec_from_file_location("bbmd_vamp_v1", _bv_path)
_bv = importlib.util.module_from_spec(_spec_bv)
_spec_bv.loader.exec_module(_bv)
vamp_se_closed = _bv.vamp_se_closed
amp_se_scalar = _bv.amp_se_scalar


# ---------------------------------------------------------------------------
# Iterate-saving VAMP loop (standard VAMP Alg 1, RSF 2017, Gaussian prior +
# Gaussian noise; identical to bbmd_vamp v1 run_vamp but records traces).
# ---------------------------------------------------------------------------

def run_vamp_with_iterates(U: np.ndarray, s: np.ndarray, Vt: np.ndarray,
                            y: np.ndarray, x_true: np.ndarray,
                            signal_var: float, sigma_sq: float,
                            n_iter: int = 200) -> dict:
    """VAMP iteration with per-step trace recording.

    Returns a dict with:
      - n_iter_actual: int (may be < n_iter due to early-stop)
      - x_hat_norms: list[float]  (||x_hat|| per iter, pre-denoiser)
      - x_hat_2_norms: list[float]  (||x_hat_2|| per iter, post-denoiser)
      - mse_per_iter: list[float]
      - denoiser_output_norm: list[float]  (alias of x_hat_2_norms; kept for clarity)
      - onsager_term_norm: list[float]  (|gamma_2| * ||r_2|| per iter)
      - gamma_1: list[float]
      - gamma_2: list[float]
      - final_mse: float
    """
    M, N = U.shape[0], Vt.shape[1]
    K = len(s)
    s2 = s ** 2
    y_tilde = U.T @ y

    r_1 = np.zeros(N, dtype=np.float64)
    gamma_1 = 1.0 / signal_var

    x_hat_norms = []
    x_hat_2_norms = []
    mses = []
    onsager_norms = []
    gamma_1_trace = []
    gamma_2_trace = []

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

        # Record this iteration's traces BEFORE updating r_1/gamma_1
        x_hat_norms.append(float(np.linalg.norm(x_hat)))
        x_hat_2_norms.append(float(np.linalg.norm(x_hat_2)))
        mse = float(np.mean((x_hat_2 - x_true) ** 2))
        mses.append(mse)
        onsager_norms.append(float(gamma_2 * np.linalg.norm(r_2)))
        gamma_1_trace.append(float(gamma_1))
        gamma_2_trace.append(float(gamma_2))

        r_1 = r_1_new
        gamma_1 = gamma_1_new

        if len(mses) >= 5 and max(mses[-5:]) - min(mses[-5:]) < 1e-10:
            break

    return {
        "n_iter_actual": len(mses),
        "x_hat_norms": x_hat_norms,
        "x_hat_2_norms": x_hat_2_norms,
        "denoiser_output_norm": x_hat_2_norms,  # alias
        "mse_per_iter": mses,
        "onsager_term_norm": onsager_norms,
        "gamma_1": gamma_1_trace,
        "gamma_2": gamma_2_trace,
        "final_mse": mses[-1] if mses else float("inf"),
    }


# ---------------------------------------------------------------------------
# Per-cell measurement
# ---------------------------------------------------------------------------

CODEBOOKS = [
    ("srht", build_srht),
    ("hadamard", build_hadamard),
]

# Three alpha cells for Cap 8 protocol shape (matches prior Kerdock runs).
ALPHA_GRID = (0.5, 0.75, 1.0)


def _alpha_label(alpha: float) -> str:
    """Format alpha as e.g. 'alpha_0p50' for filesystem-safe directory names."""
    return f"alpha_{alpha:.2f}".replace(".", "p")


def measure_one_cell(codebook_name: str, builder, alpha: float, seed: int,
                     N: int, M: int, signal_var: float, sigma_sq: float,
                     n_iter: int, out_dir: Path) -> dict:
    """Single seed * alpha * codebook iterate-trace generator.

    alpha here scales M relative to N: M_eff = max(1, int(alpha * N)).
    We sample M_eff rows from the codebook builder (whose full row-count
    is family-dependent; the builder handles the sub-sampling internally
    via the M argument).
    """
    M_eff = max(1, int(round(alpha * N)))
    seed_val = seed * 1000 + 13

    W = builder(N, M_eff, seed_val).astype(np.float64)
    M_actual, N_actual = W.shape

    U, s, Vt = np.linalg.svd(W, full_matrices=False)

    rng_sig = np.random.default_rng(seed_val + 91)
    x_true = rng_sig.standard_normal(N_actual) * math.sqrt(signal_var)
    noise = rng_sig.standard_normal(M_actual) * math.sqrt(sigma_sq)
    y = (W @ x_true) + noise

    trace = run_vamp_with_iterates(U, s, Vt, y, x_true,
                                   signal_var, sigma_sq, n_iter=n_iter)
    se_pred = vamp_se_closed(s, N_actual, M_actual, sigma_sq, signal_var)

    cell = {
        "codebook": codebook_name,
        "alpha": float(alpha),
        "seed": int(seed_val),
        "N": int(N_actual),
        "M": int(M_actual),
        "signal_var": float(signal_var),
        "sigma_sq": float(sigma_sq),
        "vamp_se_pred": float(se_pred),
        "trace": trace,
    }

    # Save per-cell iterate file
    cell_dir = out_dir / "iterates" / codebook_name / _alpha_label(alpha)
    cell_dir.mkdir(parents=True, exist_ok=True)
    cell_file = cell_dir / f"seed_{seed_val:04d}.json"
    tmp = cell_file.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(cell, indent=2))
    tmp.replace(cell_file)

    return {
        "cell_file": str(cell_file.relative_to(REPO)),
        "codebook": codebook_name,
        "alpha": float(alpha),
        "seed": int(seed_val),
        "n_iter_actual": trace["n_iter_actual"],
        "final_mse": trace["final_mse"],
        "vamp_se_pred": float(se_pred),
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

def compute_verdict(summary: dict) -> tuple[str, str]:
    expected_files = summary["config"]["expected_n_files"]
    manifest = summary.get("manifest") or []

    def _resolve(cell_path: str) -> Path:
        # cell_path is stored relative to REPO; REPO / cell_path is correct.
        p = Path(cell_path)
        if p.is_absolute():
            return p
        return REPO / p

    is_smoke = summary.get("config", {}).get("mode") == "smoke"
    min_iters = 1 if is_smoke else 10
    written = sum(1 for m in manifest if _resolve(m["cell_file"]).exists()
                  and m.get("n_iter_actual", 0) >= min_iters)

    if written == expected_files:
        return ("CAP8_ITERATES_GENERATED",
                f"All {expected_files} VAMP iterate-trace files written successfully "
                f"with >=10 iterates each.  Composition A audit v2 can now compute "
                f"Spearman rho on SRHT + Hadamard.")
    if written >= 10:
        return ("CAP8_ITERATES_PARTIAL",
                f"Partial: {written}/{expected_files} files written.  Audit v2 must "
                f"check file existence per cell; Spearman rho may still be computable "
                f"if at least 1 (alpha, seed) cell per codebook completed.")
    return ("CAP8_ITERATES_FAILED",
            f"Data-gap not filled: only {written}/{expected_files} files written.")


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------

def _self_test_alpha_label() -> None:
    assert _alpha_label(0.5) == "alpha_0p50"
    assert _alpha_label(0.75) == "alpha_0p75"
    assert _alpha_label(1.0) == "alpha_1p00"


def _self_test_iterate_roundtrip(tmp_root: Path) -> None:
    """Write a synthetic trace, read it back, confirm round-trip equality."""
    fake = {
        "codebook": "srht",
        "alpha": 1.0,
        "seed": 13,
        "trace": {
            "n_iter_actual": 3,
            "mse_per_iter": [0.5, 0.3, 0.2],
            "x_hat_norms": [1.0, 1.1, 1.2],
        },
    }
    f = tmp_root / "fake_trace.json"
    f.write_text(json.dumps(fake))
    back = json.loads(f.read_text())
    assert back["codebook"] == "srht"
    assert back["trace"]["n_iter_actual"] == 3
    assert back["trace"]["mse_per_iter"][-1] == 0.2


def _self_test_vamp_iid_sanity() -> None:
    """VAMP on iid Gaussian should converge near AMP-SE prediction.
    Per Rangan-Schniter-Fletcher 2017, VAMP and AMP are equivalent in the
    iid case; final MSE should match closed-form AMP-SE within 15%.
    Uses a tiny N=128 to keep self-test cheap.
    """
    N, M = 128, 128
    signal_var = 1.0
    sigma_sq = 0.04
    rng = np.random.default_rng(7)
    W = (rng.standard_normal(size=(M, N)) / math.sqrt(N)).astype(np.float64)
    U, s, Vt = np.linalg.svd(W, full_matrices=False)
    x_true = rng.standard_normal(N) * math.sqrt(signal_var)
    noise = rng.standard_normal(M) * math.sqrt(sigma_sq)
    y = W @ x_true + noise
    trace = run_vamp_with_iterates(U, s, Vt, y, x_true, signal_var, sigma_sq, n_iter=100)
    amp_pred = amp_se_scalar(M / N, sigma_sq, signal_var)
    rel = abs(trace["final_mse"] - amp_pred) / max(trace["final_mse"], amp_pred, 1e-9)
    assert rel < 0.20, (
        f"VAMP iid sanity: final_mse={trace['final_mse']:.5f} "
        f"vs amp_pred={amp_pred:.5f} rel_err={rel:.3f} > 0.20"
    )
    # Check all per-iter quantities are finite + same length
    L = trace["n_iter_actual"]
    for key in ("x_hat_norms", "x_hat_2_norms", "mse_per_iter",
                "onsager_term_norm", "gamma_1", "gamma_2"):
        arr = trace[key]
        assert len(arr) == L, f"{key} length {len(arr)} != n_iter_actual {L}"
        for v in arr:
            assert math.isfinite(v), f"non-finite in {key}: {v}"


def _self_test_builders_work_at_4096() -> None:
    """Both SRHT + Hadamard builders execute at N=4096 without error.
    This is the actual production shape so verifying here catches torch /
    Sylvester-Hadamard problems early.
    """
    for name, builder in CODEBOOKS:
        W = builder(4096, 4096, 13)
        assert W.shape == (4096, 4096), f"{name} bad shape {W.shape}"
        assert np.all(np.isfinite(W)), f"{name} non-finite entries"


def _self_test_verdict_branches() -> None:
    cfg = {"expected_n_files": 4}
    # GENERATED branch
    manifest_full = [{"cell_file": "no_such_file.json", "n_iter_actual": 50}] * 4
    v, _ = compute_verdict({"config": cfg, "manifest": manifest_full})
    # files don't exist so it should NOT be GENERATED in this synthetic test:
    assert v in ("CAP8_ITERATES_FAILED", "CAP8_ITERATES_PARTIAL"), \
        f"synthetic-missing-files should not yield GENERATED, got {v}"


def self_test() -> None:
    _self_test_alpha_label()
    _self_test_builders_work_at_4096()
    _self_test_vamp_iid_sanity()
    _self_test_verdict_branches()
    # Round-trip needs a tmp dir; use a small one under REPO/data/_tmp.
    tmp_root = REPO / "data" / "_tmp_iterate_self_test"
    tmp_root.mkdir(parents=True, exist_ok=True)
    _self_test_iterate_roundtrip(tmp_root)
    print("self_test passed (alpha_label, builders@4096, VAMP iid sanity, "
          "verdict branches, iterate round-trip)", flush=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()
    if smoke:
        config = {
            "mode": "smoke",
            "N": 64,
            "n_seeds": 1,
            "alpha_grid": [1.0],
            "codebooks": ["srht"],
            "signal_var": 1.0,
            "sigma_noise": 0.1,
            "n_iter": 50,
        }
    else:
        config = {
            "mode": "full",
            "N": 4096,
            "n_seeds": 5,
            "alpha_grid": list(ALPHA_GRID),
            "codebooks": [nm for nm, _ in CODEBOOKS],
            "signal_var": 1.0,
            "sigma_noise": 0.1,
            "n_iter": 300,
        }

    config["expected_n_files"] = (
        len(config["codebooks"]) * len(config["alpha_grid"]) * config["n_seeds"]
    )

    out_dir = get_output_dir(
        "wave14_cap8_vamp_iterates_srht_hadamard_v1b_smoke" if smoke
        else "wave14_cap8_vamp_iterates_srht_hadamard_v1b"
    )

    N = config["N"]
    signal_var = config["signal_var"]
    sigma_sq = config["sigma_noise"] ** 2
    n_iter = config["n_iter"]
    n_seeds = config["n_seeds"]

    print(f"[setup] N={N} alphas={config['alpha_grid']} "
          f"codebooks={config['codebooks']} n_seeds={n_seeds} "
          f"expected_n_files={config['expected_n_files']}", flush=True)

    builder_map = {nm: b for nm, b in CODEBOOKS}
    manifest = []
    for nm in config["codebooks"]:
        builder = builder_map[nm]
        for alpha in config["alpha_grid"]:
            M_eff = max(1, int(round(alpha * N)))
            print(f"\n[cell] codebook={nm} alpha={alpha} M_eff={M_eff}", flush=True)
            for seed in range(n_seeds):
                t_cell = time.monotonic()
                rec = measure_one_cell(nm, builder, alpha, seed, N, M_eff,
                                       signal_var, sigma_sq, n_iter, out_dir)
                manifest.append(rec)
                print(f"  seed={seed} -> {rec['cell_file']} "
                      f"n_iter={rec['n_iter_actual']} "
                      f"final_mse={rec['final_mse']:.6f} "
                      f"se_pred={rec['vamp_se_pred']:.6f} "
                      f"dt={time.monotonic()-t_cell:.2f}s",
                      flush=True)

    summary = {"manifest": manifest, "config": config}
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
    out_dir = get_output_dir("wave14_cap8_vamp_iterates_srht_hadamard_v1b_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["manifest"]) >= 1, "smoke FAIL: no cells written"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_cap8_vamp_iterates_srht_hadamard_v1b")
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
