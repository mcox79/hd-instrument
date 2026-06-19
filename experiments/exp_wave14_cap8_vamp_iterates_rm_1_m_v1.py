"""Cap 8 VAMP-on-chain iterate-trajectory generator for RM(1, m) (v1).

Motivation
----------
Composition A audit v4 (data/exp_wave14_cap12_cap8_audit_trail_pipeline_v4/)
reported Spearman rho=0.40 for RM(1, m).  But v4's `measure_codebook_audit_trail_v2`
only loads iterate traces for SRHT + Hadamard (the families v1c covered); RM(1, m)
silently FALLS BACK to spectrum-only mode (no iterate fingerprint concatenation).
We cannot tell from v4 alone whether RM(1, m) rho=0.40 reflects:

  (a) the FALLBACK -- spectrum-only fingerprints have fewer entries (only n_max - 1 = 4
      orders at n=2..5) and intrinsically rank worse against Schur-Weyl mass-n
      deviations; this is an artifact, not a property of RM(1, m); OR

  (b) RM(1, m) genuinely having a weak kappa_n / Schur-Weyl alignment -- the iterate
      data would not help and the family would still rank near 0.40 with real traces.

This anchor is DATA GENERATION.  It generates VAMP iterate trajectories for the
RM(1, m) codebook only at the Cap 8 protocol shape (N=4096, M/N=alpha for
alpha in {0.5, 0.75, 1.0}, 5 seeds, total 15 trace files) so that the downstream
audit-trail v5 can compute a real (non-fallback) rho on RM(1, m) and disambiguate
the v4 result.

The Anchor 2 follow-up (`wave14_cap12_cap8_audit_trail_pipeline_v5`) consumes
these traces.

Output layout
-------------
data/exp_wave14_cap8_vamp_iterates_rm_1_m_v1/
  iterates/rm_1_m/alpha_0p50/seed_0013.json
  iterates/rm_1_m/alpha_0p50/seed_1013.json
  ...
  iterates/rm_1_m/alpha_1p00/seed_4013.json
  metrics.json    (top-level summary + file manifest)

There are 1 codebook * 3 alphas * 5 seeds = 15 iterate-trace JSON files.

Verdict
-------
This is a data-generation anchor.  The verdict is one of:
  - CAP8_RM_ITERATES_GENERATED: all 15 files written successfully, each
    contains >=3 iterates with finite x_hat norms.
  - CAP8_RM_ITERATES_PARTIAL: some files written but <15; downstream v5
    must check file-existence per cell.
  - CAP8_RM_ITERATES_FAILED: <5 files written; data gap is NOT filled and
    downstream rho on RM(1, m) cannot be computed with real traces.

There are NO hard-pass/hard-fail thresholds on signal quality
(this is data generation; v5 is where the hypothesis test lives).

Self-tests
----------
1. build_rm_1_m works at N=4096 with M=4096 (full row count) and M < 4096.
2. RM(1, m) shape and entry sanity (values in {-1/sqrt(N), +1/sqrt(N)}
   after the sqrt(N) normalisation).
3. VAMP iid-Gaussian sanity (inherited from v1c).
4. iterate-trace JSON round-trip (inherited from v1c).
5. compute_verdict branches.

Smoke
-----
N=64, 1 seed, 1 alpha, RM(1, m) only; produces 1 iterate-trace file.

Pre-reg: preregs/2026-05-24_wave14_cap8_vamp_iterates_rm_1_m_v1.md
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

# Reuse cross-codebook builders for RM(1, m).
_cc_path = REPO / "experiments" / "exp_wave14_kappa_profile_cross_codebook_v1.py"
_spec_cc = importlib.util.spec_from_file_location("cc_v1", _cc_path)
_cc = importlib.util.module_from_spec(_spec_cc)
_spec_cc.loader.exec_module(_cc)
build_rm_1_m = _cc.build_rm_1_m
build_iid_gauss = _cc.build_iid_gauss

# Reuse the v1c iterate-saving VAMP loop (same algorithm; we just point it at
# RM(1, m) instead of SRHT / Hadamard).  Importing this also picks up the
# vamp_se_closed / amp_se_scalar helpers transitively.
_v1c_path = REPO / "experiments" / "exp_wave14_cap8_vamp_iterates_srht_hadamard_v1c.py"
_spec_v1c = importlib.util.spec_from_file_location("iterates_v1c", _v1c_path)
_v1c = importlib.util.module_from_spec(_spec_v1c)
_spec_v1c.loader.exec_module(_v1c)
run_vamp_with_iterates = _v1c.run_vamp_with_iterates
vamp_se_closed = _v1c.vamp_se_closed
amp_se_scalar = _v1c.amp_se_scalar
_alpha_label = _v1c._alpha_label


# ---------------------------------------------------------------------------
# Per-cell measurement (RM(1, m) only)
# ---------------------------------------------------------------------------

CODEBOOKS = [
    ("rm_1_m", build_rm_1_m),
]

# Same alpha grid as v1c so the downstream audit-trail v5 can use a single
# alpha=1.0 cell (matching v3/v4's iterate-loading convention) or any of the
# three.
ALPHA_GRID = (0.5, 0.75, 1.0)


def measure_one_cell(codebook_name: str, builder, alpha: float, seed: int,
                     N: int, M: int, signal_var: float, sigma_sq: float,
                     n_iter: int, out_dir: Path) -> dict:
    """Single seed * alpha * codebook iterate-trace generator.

    Mirrors v1c.measure_one_cell exactly -- only the builder differs.
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
        norm = cell_path.replace("\\", "/")
        p = Path(norm)
        if p.is_absolute():
            return p
        return REPO / p

    is_smoke = summary.get("config", {}).get("mode") == "smoke"
    min_iters = 1 if is_smoke else 3
    written = sum(1 for m in manifest if _resolve(m["cell_file"]).exists()
                  and m.get("n_iter_actual", 0) >= min_iters)

    if written == expected_files:
        return ("CAP8_RM_ITERATES_GENERATED",
                f"All {expected_files} RM(1,m) VAMP iterate-trace files written "
                f"successfully with >={min_iters} iterates each.  Audit-trail v5 "
                f"can now compute Spearman rho on RM(1,m) with REAL iterate data "
                f"(no spectrum-only fallback) -- v4's 0.40 disambiguation unblocked.")
    if written >= 5:
        return ("CAP8_RM_ITERATES_PARTIAL",
                f"Partial: {written}/{expected_files} files written.  v5 must "
                f"check file existence per cell; Spearman rho on RM(1,m) may "
                f"still be computable if >=1 (alpha, seed) cell completed.")
    return ("CAP8_RM_ITERATES_FAILED",
            f"Data-gap not filled: only {written}/{expected_files} files "
            f"written.  Audit-trail v5 will fall back to spectrum-only for "
            f"RM(1,m); v4's 0.40 cannot be disambiguated from this anchor.")


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------

def _self_test_alpha_label() -> None:
    assert _alpha_label(0.5) == "alpha_0p50"
    assert _alpha_label(0.75) == "alpha_0p75"
    assert _alpha_label(1.0) == "alpha_1p00"


def _self_test_iterate_roundtrip(tmp_root: Path) -> None:
    fake = {
        "codebook": "rm_1_m",
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
    assert back["codebook"] == "rm_1_m"
    assert back["trace"]["n_iter_actual"] == 3
    assert back["trace"]["mse_per_iter"][-1] == 0.2


def _self_test_rm_1_m_builder_at_4096() -> None:
    """RM(1, m) builder executes at N=4096 with M up to 4096; entries are
    bipolar normalised to magnitude 1/sqrt(N).
    """
    N = 4096
    inv_sqrt_N = 1.0 / math.sqrt(N)
    for M in (2048, 4096):
        W = build_rm_1_m(N, M, 13)
        assert W.shape == (M, N), f"RM(1,m) bad shape {W.shape} for M={M}"
        assert np.all(np.isfinite(W)), f"RM(1,m) non-finite entries at M={M}"
        mags = np.abs(W)
        assert np.allclose(mags, inv_sqrt_N, atol=1e-5), (
            f"RM(1,m) entries should have magnitude 1/sqrt(N)={inv_sqrt_N:.6f} "
            f"(bipolar normalised); got min={mags.min()}, max={mags.max()}"
        )


def _self_test_rm_1_m_row_uniqueness() -> None:
    """Subsampling at M=8 yields 8 distinct rows (RM(1,m) has 2N codewords
    so M <= 2N is feasible)."""
    N = 64
    W = build_rm_1_m(N, 8, 17)
    # Convert to comparable tuples
    rows = {tuple(np.sign(r).astype(int)) for r in W}
    assert len(rows) == 8, f"RM(1,m) subsample should give 8 unique sign-rows; got {len(rows)}"


def _self_test_vamp_iid_sanity() -> None:
    """Inherited check from v1c -- VAMP converges near AMP-SE on iid Gauss."""
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
    L = trace["n_iter_actual"]
    for key in ("x_hat_norms", "x_hat_2_norms", "mse_per_iter",
                "onsager_term_norm", "gamma_1", "gamma_2"):
        arr = trace[key]
        assert len(arr) == L, f"{key} length {len(arr)} != n_iter_actual {L}"
        for v in arr:
            assert math.isfinite(v), f"non-finite in {key}: {v}"


def _self_test_verdict_branches() -> None:
    cfg = {"expected_n_files": 4}
    manifest_full = [{"cell_file": "no_such_file.json", "n_iter_actual": 50}] * 4
    v, _ = compute_verdict({"config": cfg, "manifest": manifest_full})
    # Files don't exist -> not GENERATED.
    assert v in ("CAP8_RM_ITERATES_FAILED", "CAP8_RM_ITERATES_PARTIAL"), \
        f"synthetic-missing-files should not yield GENERATED, got {v}"


def self_test() -> None:
    _self_test_alpha_label()
    _self_test_rm_1_m_builder_at_4096()
    _self_test_rm_1_m_row_uniqueness()
    _self_test_vamp_iid_sanity()
    _self_test_verdict_branches()
    tmp_root = REPO / "data" / "_tmp_iterate_rm_self_test"
    tmp_root.mkdir(parents=True, exist_ok=True)
    _self_test_iterate_roundtrip(tmp_root)
    print("self_test passed (alpha_label, RM(1,m) builder@4096, row uniqueness, "
          "VAMP iid sanity, verdict branches, iterate round-trip)", flush=True)


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
            "codebooks": ["rm_1_m"],
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
        "wave14_cap8_vamp_iterates_rm_1_m_v1_smoke" if smoke
        else "wave14_cap8_vamp_iterates_rm_1_m_v1"
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
    env_name = os.environ.get("HDLAB_EXP_NAME", name)
    out = REPO / "data" / f"exp_{env_name}"
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
    out_dir = get_output_dir("wave14_cap8_vamp_iterates_rm_1_m_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["manifest"]) >= 1, "smoke FAIL: no cells written"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_cap8_vamp_iterates_rm_1_m_v1")
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
