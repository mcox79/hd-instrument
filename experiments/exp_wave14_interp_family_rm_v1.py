"""Cross-interpolation-family AMP-error predictor: iid-Gauss -> RM(1,m).

Cap 12 Gate B THIRD-family hardening (optional anchor per the cap_map v174
promotion directive).

Motivation
----------
Anchors 1 (tau-robustness) and 2 (Hadamard family) cover the two strict
✅ gates. If both pass quickly, a third-family RM(1,m) hardening turns
"three-family confirmed" into "four-family confirmed" (Kerdock + SRHT +
Hadamard + RM), making the kappa_n divergence a more general meta-tool.

RM(1, m) is the Reed-Muller code of order 1 (length N=2^m, 2N codewords;
bipolar Hadamard rows union their negations). Structurally similar to
Hadamard but with the codeword count doubled and explicit antipodal pairs.

Honest framing
--------------
This is the weakest of the three anchors -- pass adds breadth, not depth.
A KILL on RM but PASS on Hadamard would still leave Cap 12 promotable to
✅ with Gate B at-threshold; a KILL on both Hadamard and RM would deepen
the Cap 12 family-specificity caveat.

Design
------
W_alpha = (1-alpha) * G + alpha * W_struct where W_struct is M rows
subsampled from the 2N-row RM(1,m) bipolar codebook. Alpha grid {0, 0.25,
0.5, 0.75, 1.0}, 5 seeds, N=1024, M/N=1.0.

For each alpha and seed: SVD, kappa profile, BBMD-distance, AMP/VAMP.

HARD PASS (Cap 12 third-family hardening)
-----------------------------------------
  Spearman rho >= 0.70 AND max VAMP-rel-err < 0.10.

HARD FAIL (Cap 12 third-family hardening fails)
-----------------------------------------------
  Spearman rho < 0.50 OR max VAMP-rel-err > 0.20.

MIDDLE BAND: rho in [0.50, 0.70) or VAMP rel-err in [0.10, 0.20).

Vertex: INTERP_FAMILY_RM_PASS / KILLED / INCONCLUSIVE

Pre-reg: preregs/2026-05-24_wave14_interp_family_rm_v1.md
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

_cc_path = REPO / "experiments" / "exp_wave14_kappa_profile_cross_codebook_v1.py"
_spec_cc = importlib.util.spec_from_file_location("kappa_cc_v1", _cc_path)
_cc = importlib.util.module_from_spec(_spec_cc)
_spec_cc.loader.exec_module(_cc)

_bv_path = REPO / "experiments" / "exp_wave14_bbmd_vamp_correspondence_sweep_v1.py"
_spec_bv = importlib.util.spec_from_file_location("bbmd_vamp_v1", _bv_path)
_bv = importlib.util.module_from_spec(_spec_bv)
_spec_bv.loader.exec_module(_bv)
amp_se_scalar = _bv.amp_se_scalar
vamp_se_closed = _bv.vamp_se_closed
run_amp = _bv.run_amp
run_vamp = _bv.run_vamp

_v1_path = REPO / "experiments" / "exp_wave14_kappa_n_profile_v1.py"
_spec_v1 = importlib.util.spec_from_file_location("kappa_v1", _v1_path)
_v1 = importlib.util.module_from_spec(_spec_v1)
_spec_v1.loader.exec_module(_v1)
moments_to_free_cumulants_general = _v1.moments_to_free_cumulants_general


FAMILY = "rm_1_m"


def build_rm_unnormalized(N: int, M: int, seed: int) -> np.ndarray:
    """RM(1,m) bipolar codeword set (2N codewords) without 1/sqrt(N) post-normalize.

    Entries in {+1, -1}; shape (M, N).
    """
    import torch
    n_log2 = int(round(math.log2(N)))
    assert 2 ** n_log2 == N, f"N={N} must be power of 2"
    sylvester_hadamard = _cc.sylvester_hadamard
    H = sylvester_hadamard(n_log2, torch.device("cpu")).numpy().astype(np.float32)
    codebook = np.concatenate([H, -H], axis=0)  # (2N, N)
    rng = np.random.default_rng(seed)
    row_idx = rng.choice(codebook.shape[0], size=M, replace=False)
    return codebook[row_idx].astype(np.float32)


def build_W_alpha_rm(alpha: float, N: int, M: int, seed: int,
                     struct_cache: dict) -> np.ndarray:
    cache_key = (N, M, seed)
    if cache_key not in struct_cache:
        struct_cache[cache_key] = build_rm_unnormalized(N, M, seed)
    W_struct = struct_cache[cache_key]
    rng_g = np.random.default_rng(seed + 1_000_000)
    G = rng_g.standard_normal(size=(M, N)).astype(np.float32)
    W = (1.0 - alpha) * G + alpha * W_struct
    return (W / math.sqrt(N)).astype(np.float32)


def bbmd_distance(kappas: list[float], c_ref: float, n_min: int = 2,
                  n_max: int = 6) -> float:
    if not kappas or len(kappas) < n_max:
        return float("nan")
    return float(sum(abs(kappas[n - 1] - c_ref) for n in range(n_min, n_max + 1)))


def compute_verdict(summary: dict) -> tuple[str, str]:
    cells = summary.get("cells") or []
    if len(cells) < 3:
        return ("INTERP_FAMILY_RM_INCONCLUSIVE",
                f"Only {len(cells)} cells; need >=3.")

    dists, amp_errs, vamp_errs = [], [], []
    for c in cells:
        d = c.get("bbmd_distance_mean")
        ae = c.get("amp_rel_err_mean")
        ve = c.get("vamp_rel_err_mean")
        if d is None or ae is None or ve is None:
            continue
        if not (math.isfinite(d) and math.isfinite(ae) and math.isfinite(ve)):
            continue
        dists.append(d)
        amp_errs.append(ae)
        vamp_errs.append(ve)

    if len(dists) < 3:
        return ("INTERP_FAMILY_RM_INCONCLUSIVE",
                f"Only {len(dists)} valid cells.")

    rho_result = spearmanr(amp_errs, dists)
    rho = float(rho_result.statistic) if hasattr(rho_result, "statistic") else float(rho_result[0])
    if not math.isfinite(rho):
        return ("INTERP_FAMILY_RM_INCONCLUSIVE", "rho not finite.")

    max_vamp = max(vamp_errs)
    summary["spearman_rho"] = rho
    summary["max_vamp_rel_err"] = max_vamp

    if rho >= 0.70 and max_vamp < 0.10:
        return ("INTERP_FAMILY_RM_PASS",
                f"AMP-error predictor extends to RM(1,m) family: "
                f"rho = {rho:.3f} >= 0.70; max VAMP-rel-err = {max_vamp:.4f} < 0.10. "
                f"Cap 12 third-family hardening lands positive.")

    if rho < 0.50 or max_vamp > 0.20:
        return ("INTERP_FAMILY_RM_KILLED",
                f"Predictor does NOT generalize to RM(1,m): "
                f"rho = {rho:.3f} (HARD FAIL if < 0.50); max VAMP-rel-err = "
                f"{max_vamp:.4f} (HARD FAIL if > 0.20). Cap 12 RM hardening fails.")

    return ("INTERP_FAMILY_RM_INCONCLUSIVE",
            f"Marginal: rho = {rho:.3f}, max VAMP-rel-err = {max_vamp:.4f}.")


def self_test() -> None:
    # bbmd identity
    c = 0.5
    assert abs(bbmd_distance([c] * 6, c, 2, 6)) < 1e-12
    devs = [c, c + 0.1, c + 0.2, c + 0.3, c + 0.4, c + 0.5]
    assert abs(bbmd_distance(devs, c, 2, 6) - 1.5) < 1e-9

    # spearmanr monotone
    rho_r = spearmanr([0.01, 0.02, 0.10, 0.20, 0.30], [0.0, 0.5, 1.0, 1.5, 2.0])
    rho_val = float(rho_r.statistic) if hasattr(rho_r, "statistic") else float(rho_r[0])
    assert abs(rho_val - 1.0) < 1e-9

    # PASS
    cells_pass = [
        {"alpha_interp": 0.0,  "bbmd_distance_mean": 0.05, "amp_rel_err_mean": 0.02, "vamp_rel_err_mean": 0.02},
        {"alpha_interp": 0.25, "bbmd_distance_mean": 0.10, "amp_rel_err_mean": 0.05, "vamp_rel_err_mean": 0.03},
        {"alpha_interp": 0.50, "bbmd_distance_mean": 0.20, "amp_rel_err_mean": 0.10, "vamp_rel_err_mean": 0.04},
        {"alpha_interp": 0.75, "bbmd_distance_mean": 0.40, "amp_rel_err_mean": 0.15, "vamp_rel_err_mean": 0.05},
        {"alpha_interp": 1.0,  "bbmd_distance_mean": 0.60, "amp_rel_err_mean": 0.25, "vamp_rel_err_mean": 0.06},
    ]
    v, _ = compute_verdict({"cells": cells_pass})
    assert v == "INTERP_FAMILY_RM_PASS"

    # KILLED rho
    cells_k = [
        {"alpha_interp": 0.0,  "bbmd_distance_mean": 0.05, "amp_rel_err_mean": 0.20, "vamp_rel_err_mean": 0.02},
        {"alpha_interp": 0.25, "bbmd_distance_mean": 0.10, "amp_rel_err_mean": 0.05, "vamp_rel_err_mean": 0.03},
        {"alpha_interp": 0.50, "bbmd_distance_mean": 0.20, "amp_rel_err_mean": 0.10, "vamp_rel_err_mean": 0.04},
        {"alpha_interp": 0.75, "bbmd_distance_mean": 0.40, "amp_rel_err_mean": 0.05, "vamp_rel_err_mean": 0.05},
        {"alpha_interp": 1.0,  "bbmd_distance_mean": 0.60, "amp_rel_err_mean": 0.08, "vamp_rel_err_mean": 0.06},
    ]
    v, _ = compute_verdict({"cells": cells_k})
    assert v == "INTERP_FAMILY_RM_KILLED"

    # MIDDLE
    cells_inc = [
        {"alpha_interp": 0.0,  "bbmd_distance_mean": 0.05, "amp_rel_err_mean": 0.02, "vamp_rel_err_mean": 0.05},
        {"alpha_interp": 0.50, "bbmd_distance_mean": 0.20, "amp_rel_err_mean": 0.10, "vamp_rel_err_mean": 0.08},
        {"alpha_interp": 1.0,  "bbmd_distance_mean": 0.60, "amp_rel_err_mean": 0.25, "vamp_rel_err_mean": 0.15},
    ]
    v, _ = compute_verdict({"cells": cells_inc})
    assert v == "INTERP_FAMILY_RM_INCONCLUSIVE"

    # missing
    v, _ = compute_verdict({"cells": cells_inc[:1]})
    assert v == "INTERP_FAMILY_RM_INCONCLUSIVE"

    print("interp-family RM self-test passed (6/6 cases)", flush=True)


def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    if smoke:
        config = {
            "mode": "smoke",
            "N": 64,
            "M_over_N": 1.0,
            "alpha_interp_list": [0.0, 0.5, 1.0],
            "sigma_noise": 0.1,
            "signal_var": 1.0,
            "n_seeds": 1,
            "n_iter": 50,
            "n_max_moment": 6,
            "family": FAMILY,
        }
    else:
        config = {
            "mode": "full",
            "N": 1024,
            "M_over_N": 1.0,
            "alpha_interp_list": [0.0, 0.25, 0.5, 0.75, 1.0],
            "sigma_noise": 0.1,
            "signal_var": 1.0,
            "n_seeds": 5,
            "n_iter": 300,
            "n_max_moment": 6,
            "family": FAMILY,
        }

    N = config["N"]
    M = max(1, int(config["M_over_N"] * N))
    sigma = config["sigma_noise"]
    sigma_sq = sigma ** 2
    signal_var = config["signal_var"]
    alpha_ratio = M / N
    n_max = config["n_max_moment"]

    print(f"[setup] family={FAMILY} N={N} M={M} seeds={config['n_seeds']}",
          flush=True)

    amp_se_pred = amp_se_scalar(alpha_ratio, sigma_sq, signal_var)
    struct_cache: dict = {}

    cells = []
    for alpha_int in config["alpha_interp_list"]:
        seed_records = []
        for seed in range(config["n_seeds"]):
            seed_val = seed * 1000 + 23
            W = build_W_alpha_rm(alpha_int, N, M, seed_val, struct_cache)

            U, s, Vt = np.linalg.svd(W, full_matrices=False)
            eig = (s ** 2).astype(np.float64)
            moms = [float(np.mean(eig ** n)) for n in range(1, n_max + 1)]
            kappas = moments_to_free_cumulants_general(moms)
            d_bbmd = bbmd_distance(kappas, alpha_ratio, n_min=2, n_max=n_max)

            vamp_se_pred = vamp_se_closed(s, N, M, sigma_sq, signal_var)

            rng_sig = np.random.default_rng(seed_val + 77)
            x_true = rng_sig.standard_normal(N).astype(np.float64) * math.sqrt(signal_var)
            noise = rng_sig.standard_normal(M).astype(np.float64) * sigma
            y = (W.astype(np.float64) @ x_true) + noise

            amp_emp = run_amp(W, y, x_true, signal_var, sigma_sq, config["n_iter"])
            vamp_emp = run_vamp(U, s, Vt, y, x_true, signal_var, sigma_sq, config["n_iter"])

            amp_rel = abs(amp_emp - amp_se_pred) / max(amp_emp, amp_se_pred, 1e-12)
            vamp_rel = abs(vamp_emp - vamp_se_pred) / max(vamp_emp, vamp_se_pred, 1e-12)

            seed_records.append({
                "seed": seed_val,
                "kappas": kappas,
                "bbmd_distance": d_bbmd,
                "amp_se_pred": amp_se_pred,
                "amp_emp": amp_emp,
                "amp_rel_err": amp_rel,
                "vamp_se_pred": vamp_se_pred,
                "vamp_emp": vamp_emp,
                "vamp_rel_err": vamp_rel,
            })
            print(f"  alpha={alpha_int:.2f} seed={seed} bbmd={d_bbmd:.4f} "
                  f"AMP={amp_emp:.5f} (rel={amp_rel:.3f}) "
                  f"VAMP={vamp_emp:.5f} (rel={vamp_rel:.3f})", flush=True)

        d_mean = float(np.mean([r["bbmd_distance"] for r in seed_records]))
        amp_rel_mean = float(np.mean([r["amp_rel_err"] for r in seed_records]))
        vamp_rel_mean = float(np.mean([r["vamp_rel_err"] for r in seed_records]))
        kappa_mean = np.mean([r["kappas"] for r in seed_records], axis=0).tolist()

        cells.append({
            "alpha_interp": float(alpha_int),
            "bbmd_distance_mean": d_mean,
            "amp_rel_err_mean": amp_rel_mean,
            "vamp_rel_err_mean": vamp_rel_mean,
            "kappa_mean": kappa_mean,
            "per_seed": seed_records,
        })
        print(f"  AGG alpha={alpha_int:.2f}: bbmd={d_mean:.4f} "
              f"amp_rel={amp_rel_mean:.4f} vamp_rel={vamp_rel_mean:.4f}", flush=True)

    summary = {"cells": cells, "config": config, "family": FAMILY}
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
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


def run_smoke() -> None:
    self_test()
    out_dir = get_output_dir("wave14_interp_family_rm_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["cells"]) >= 1
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_interp_family_rm_v1")
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
