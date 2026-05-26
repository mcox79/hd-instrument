"""Cross-interpolation-family AMP-error predictor: iid-Gauss -> Hadamard.

Cap 12 Gate B (second of two anchor families per cap_map v174 promotion gate).

Motivation
----------
Cap 12 (AMP-vs-VAMP inference routing infrastructure) was promoted to GREEN at
v174 with the SRHT interpolation family hitting the at-threshold Spearman rho
of 0.700 (INTERP_FAMILY_SRHT_PASS). Promotion from GREEN to GREEN-CHECK requires
TWO pre-registered ✅ gates:

  Gate A: tau-robustness sweep (separate script).
  Gate B (this experiment): a second-family validation of the AMP-error
      predictor (sum |delta kappa_n|) on iid-Gauss -> Hadamard interpolation.

The question Gate B asks: does the v170 + SRHT free-cumulant divergence
predictor generalize across a THIRD interpolation family (Hadamard), or
was it Kerdock + SRHT specific?

Hadamard differs from SRHT because the latter post-multiplies by a random
diagonal sign matrix D and a column-subsample S -- the Dudeja-Lu-Kini
construction. Plain Hadamard is row-subsample of Sylvester without D or S,
so its singular spectrum is more deterministic (every left singular vector
is a Hadamard column).

Honest framing
--------------
Three-family validation hardens the meta-tool capability. A PASS upgrades
the predictor from "two families confirmed" to "three families confirmed";
a FAIL means the SRHT-family PASS was the boundary, and Hadamard is the
first family where the explainer breaks.

Design
------
W_alpha = (1-alpha) * G + alpha * W_struct (un-normalized scales matched,
normalized by sqrt(N) at the end), where W_struct is row-subsampled
Sylvester Hadamard at (N, M, seed). Same alpha grid as the SRHT family
{0, 0.25, 0.5, 0.75, 1.0}, 5 seeds, N=1024, M/N=1.0.

For each alpha and seed:
  1. Build W_alpha; SVD; kappa profile k_2..k_6.
  2. BBMD-distance d_alpha = sum_{n=2..6} | kappa_n - alpha_ratio |.
  3. AMP-SE prediction; empirical AMP; AMP rel-err.
  4. VAMP-SE closed-form using empirical singular spectrum; empirical VAMP;
     VAMP rel-err.

Aggregate: across 5 alpha cells (mean across seeds), Spearman rho between
AMP-rel-err and BBMD-distance; max VAMP-rel-err.

HARD PASS (Cap 12 Gate B satisfied)
-----------------------------------
  Spearman rho(amp_rel_err, bbmd_dist) >= 0.70 across 5 alpha cells
  AND max VAMP-rel-err < 0.10.

HARD FAIL (Cap 12 Gate B fails)
-------------------------------
  Spearman rho < 0.50
  OR max VAMP-rel-err > 0.20.

MIDDLE BAND
-----------
  rho in [0.50, 0.70) or VAMP rel-err in [0.10, 0.20) -- marginal.

Vertex: INTERP_FAMILY_HADAMARD_PASS / KILLED / INCONCLUSIVE

Pre-reg: preregs/2026-05-24_wave14_interp_family_hadamard_v1.md
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

# Reuse cross-codebook v1 builders.
_cc_path = REPO / "experiments" / "exp_wave14_kappa_profile_cross_codebook_v1.py"
_spec_cc = importlib.util.spec_from_file_location("kappa_cc_v1", _cc_path)
_cc = importlib.util.module_from_spec(_spec_cc)
_spec_cc.loader.exec_module(_cc)

# Reuse BBMD-VAMP correspondence v1 helpers.
_bv_path = REPO / "experiments" / "exp_wave14_bbmd_vamp_correspondence_sweep_v1.py"
_spec_bv = importlib.util.spec_from_file_location("bbmd_vamp_v1", _bv_path)
_bv = importlib.util.module_from_spec(_spec_bv)
_spec_bv.loader.exec_module(_bv)
amp_se_scalar = _bv.amp_se_scalar
vamp_se_closed = _bv.vamp_se_closed
run_amp = _bv.run_amp
run_vamp = _bv.run_vamp

# Reuse kappa-profile inversion.
_v1_path = REPO / "experiments" / "exp_wave14_kappa_n_profile_v1.py"
_spec_v1 = importlib.util.spec_from_file_location("kappa_v1", _v1_path)
_v1 = importlib.util.module_from_spec(_spec_v1)
_spec_v1.loader.exec_module(_v1)
moments_to_free_cumulants_general = _v1.moments_to_free_cumulants_general


FAMILY = "hadamard"


def build_hadamard_unnormalized(N: int, M: int, seed: int) -> np.ndarray:
    """Plain Hadamard row-subsample (no D, no S, no 1/sqrt(N) post-normalize).

    Entries are in {+1, -1}; shape (M, N).
    """
    import torch
    n_log2 = int(round(math.log2(N)))
    assert 2 ** n_log2 == N, f"N={N} must be power of 2"
    sylvester_hadamard = _cc.sylvester_hadamard
    H = sylvester_hadamard(n_log2, torch.device("cpu")).numpy().astype(np.float32)
    rng = np.random.default_rng(seed)
    row_idx = rng.choice(N, size=M, replace=False)
    return H[row_idx].astype(np.float32)  # (M, N) in {+/-1}


def build_W_alpha_hadamard(alpha: float, N: int, M: int, seed: int,
                            struct_cache: dict) -> np.ndarray:
    """W_alpha = ((1-alpha) * G + alpha * W_hadamard) / sqrt(N).

    G entries iid N(0,1) (un-normalized; same scale as +/-1 Hadamard entries).
    Caches the Hadamard block per (N, M, seed). Gaussian seed offset by 1_000_000
    matches the SRHT-family convention.
    """
    cache_key = (N, M, seed)
    if cache_key not in struct_cache:
        struct_cache[cache_key] = build_hadamard_unnormalized(N, M, seed)
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
        return ("INTERP_FAMILY_HADAMARD_INCONCLUSIVE",
                f"Only {len(cells)} cells; need >=3 for trend test.")

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
        return ("INTERP_FAMILY_HADAMARD_INCONCLUSIVE",
                f"Only {len(dists)} valid cells with finite metrics.")

    rho_result = spearmanr(amp_errs, dists)
    rho = float(rho_result.statistic) if hasattr(rho_result, "statistic") else float(rho_result[0])
    if not math.isfinite(rho):
        return ("INTERP_FAMILY_HADAMARD_INCONCLUSIVE",
                f"Spearman rho not finite.")

    max_vamp = max(vamp_errs)
    summary["spearman_rho"] = rho
    summary["max_vamp_rel_err"] = max_vamp
    summary["bbmd_distances"] = dists
    summary["amp_rel_errs"] = amp_errs
    summary["vamp_rel_errs"] = vamp_errs

    if rho >= 0.70 and max_vamp < 0.10:
        return ("INTERP_FAMILY_HADAMARD_PASS",
                f"AMP-error predictor generalizes to iid-Gauss -> Hadamard: "
                f"Spearman rho(amp_rel_err, sum|delta_kappa_n|) = {rho:.3f} >= 0.70 "
                f"across {len(dists)} alpha cells; max VAMP-rel-err = {max_vamp:.4f} "
                f"< 0.10. Cap 12 Gate B satisfied on Hadamard family; the kappa_n "
                f"divergence is a THREE-family predictor (Kerdock + SRHT + Hadamard).")

    if rho < 0.50 or max_vamp > 0.20:
        return ("INTERP_FAMILY_HADAMARD_KILLED",
                f"Predictor does NOT generalize to iid-Gauss -> Hadamard: "
                f"rho = {rho:.3f} (HARD FAIL if < 0.50); max VAMP-rel-err = "
                f"{max_vamp:.4f} (HARD FAIL if > 0.20). Hadamard is the first "
                f"family where the kappa_n explainer breaks; Cap 12 Gate B fails.")

    return ("INTERP_FAMILY_HADAMARD_INCONCLUSIVE",
            f"Marginal: rho = {rho:.3f} (PASS>=0.70, FAIL<0.50), "
            f"max VAMP-rel-err = {max_vamp:.4f} (PASS<0.10, FAIL>0.20). "
            f"Cap 12 Gate B middle band on Hadamard family.")


def self_test() -> None:
    # Self-test 1: bbmd_distance on MP-reference
    c = 0.5
    d = bbmd_distance([c] * 6, c, 2, 6)
    assert abs(d) < 1e-12, f"bbmd on MP should be 0, got {d}"

    # Self-test 2: bbmd on deviating cumulants
    devs = [c, c + 0.1, c + 0.2, c + 0.3, c + 0.4, c + 0.5]
    d = bbmd_distance(devs, c, 2, 6)
    assert abs(d - 1.5) < 1e-9, f"bbmd want 1.5 got {d}"

    # Self-test 3: spearmanr on monotone -> 1.0
    rho_r = spearmanr([0.01, 0.02, 0.10, 0.20, 0.30], [0.0, 0.5, 1.0, 1.5, 2.0])
    rho_val = float(rho_r.statistic) if hasattr(rho_r, "statistic") else float(rho_r[0])
    assert abs(rho_val - 1.0) < 1e-9

    # Self-test 4: PASS
    cells_pass = [
        {"alpha_interp": 0.0,  "bbmd_distance_mean": 0.05, "amp_rel_err_mean": 0.02, "vamp_rel_err_mean": 0.02},
        {"alpha_interp": 0.25, "bbmd_distance_mean": 0.10, "amp_rel_err_mean": 0.05, "vamp_rel_err_mean": 0.03},
        {"alpha_interp": 0.50, "bbmd_distance_mean": 0.20, "amp_rel_err_mean": 0.10, "vamp_rel_err_mean": 0.04},
        {"alpha_interp": 0.75, "bbmd_distance_mean": 0.40, "amp_rel_err_mean": 0.15, "vamp_rel_err_mean": 0.05},
        {"alpha_interp": 1.0,  "bbmd_distance_mean": 0.60, "amp_rel_err_mean": 0.25, "vamp_rel_err_mean": 0.06},
    ]
    v, msg = compute_verdict({"cells": cells_pass})
    assert v == "INTERP_FAMILY_HADAMARD_PASS", f"expected PASS got {v}: {msg}"

    # Self-test 5: KILLED via low rho
    cells_killed = [
        {"alpha_interp": 0.0,  "bbmd_distance_mean": 0.05, "amp_rel_err_mean": 0.20, "vamp_rel_err_mean": 0.02},
        {"alpha_interp": 0.25, "bbmd_distance_mean": 0.10, "amp_rel_err_mean": 0.05, "vamp_rel_err_mean": 0.03},
        {"alpha_interp": 0.50, "bbmd_distance_mean": 0.20, "amp_rel_err_mean": 0.10, "vamp_rel_err_mean": 0.04},
        {"alpha_interp": 0.75, "bbmd_distance_mean": 0.40, "amp_rel_err_mean": 0.05, "vamp_rel_err_mean": 0.05},
        {"alpha_interp": 1.0,  "bbmd_distance_mean": 0.60, "amp_rel_err_mean": 0.08, "vamp_rel_err_mean": 0.06},
    ]
    v, _ = compute_verdict({"cells": cells_killed})
    assert v == "INTERP_FAMILY_HADAMARD_KILLED"

    # Self-test 6: KILLED via VAMP blowup
    cells_killed_v = [
        {"alpha_interp": 0.0,  "bbmd_distance_mean": 0.05, "amp_rel_err_mean": 0.02, "vamp_rel_err_mean": 0.02},
        {"alpha_interp": 0.50, "bbmd_distance_mean": 0.20, "amp_rel_err_mean": 0.10, "vamp_rel_err_mean": 0.04},
        {"alpha_interp": 1.0,  "bbmd_distance_mean": 0.60, "amp_rel_err_mean": 0.25, "vamp_rel_err_mean": 0.30},
    ]
    v, _ = compute_verdict({"cells": cells_killed_v})
    assert v == "INTERP_FAMILY_HADAMARD_KILLED"

    # Self-test 7: MIDDLE BAND (monotone rho but vamp in (0.10, 0.20))
    cells_inc = [
        {"alpha_interp": 0.0,  "bbmd_distance_mean": 0.05, "amp_rel_err_mean": 0.02, "vamp_rel_err_mean": 0.05},
        {"alpha_interp": 0.50, "bbmd_distance_mean": 0.20, "amp_rel_err_mean": 0.10, "vamp_rel_err_mean": 0.08},
        {"alpha_interp": 1.0,  "bbmd_distance_mean": 0.60, "amp_rel_err_mean": 0.25, "vamp_rel_err_mean": 0.15},
    ]
    v, _ = compute_verdict({"cells": cells_inc})
    assert v == "INTERP_FAMILY_HADAMARD_INCONCLUSIVE"

    # Self-test 8: too-few cells
    v, _ = compute_verdict({"cells": cells_inc[:1]})
    assert v == "INTERP_FAMILY_HADAMARD_INCONCLUSIVE"

    print("interp-family Hadamard self-test passed (8/8 cases)", flush=True)


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

    print(f"[setup] family={FAMILY} N={N} M={M} M/N={alpha_ratio:.3f} sigma={sigma} "
          f"alpha_interp={config['alpha_interp_list']} seeds={config['n_seeds']}",
          flush=True)

    amp_se_pred = amp_se_scalar(alpha_ratio, sigma_sq, signal_var)
    struct_cache: dict = {}

    cells = []
    for alpha_int in config["alpha_interp_list"]:
        seed_records = []
        for seed in range(config["n_seeds"]):
            seed_val = seed * 1000 + 23
            W = build_W_alpha_hadamard(alpha_int, N, M, seed_val, struct_cache)

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
            print(f"  alpha_int={alpha_int:.2f} seed={seed} bbmd={d_bbmd:.4f} "
                  f"AMP_emp={amp_emp:.5f} (rel={amp_rel:.3f}) "
                  f"VAMP_emp={vamp_emp:.5f} (rel={vamp_rel:.3f})", flush=True)

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
        print(f"  AGG alpha_int={alpha_int:.2f}: bbmd={d_mean:.4f} "
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
    out_dir = get_output_dir("wave14_interp_family_hadamard_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["cells"]) >= 1, "smoke FAIL: no cells"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_interp_family_hadamard_v1")
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
