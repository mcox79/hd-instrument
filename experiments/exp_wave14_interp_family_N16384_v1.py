"""Cross-family AMP-error predictor N-scaling stress: Cap 12 ✅ E2 STRESS.

Motivation
----------
Cap 12 was just promoted to ✅ at cap_map v175 with three pre-registered
anchors. The composite "AMP-vs-VAMP inference routing infrastructure"
includes a META-DIAGNOSTIC predictor: Spearman rho(AMP-rel-err, sum|delta
kappa_n|) >= 0.70 was demonstrated at N=1024 across the (iid-Gauss -> SRHT)
and (iid-Gauss -> Hadamard) and (iid-Gauss -> RM) interpolation families.

The ✅ promotion exposes Cap 12 to envelope-expansion stress per
[[feedback-envelope-expansion-fail-bands]]: is the AMP-error predictor a
N=1024 artifact, or does it survive N-scaling to N=16384 (the customer-
facing regime where SVD is non-trivial and finite-N corrections dominate)?

E2 STRESS asks: across {Kerdock, SRHT, Hadamard}, does the predictor remain
strong at N=4096 and N=16384? If the Spearman rho drops on ANY family at
N=16384, the predictor was an N-artifact.

Honest framing
--------------
If E2 PASSes, Cap 12 ✅ survives a substantive N-scaling envelope expansion;
the kappa_n divergence sum is a TRUE meta-tool for customer codebooks at
scales they actually use. If E2 FAILs on one family, Cap 12 ✅ stays with an
N-bound annotation ("predictor holds up to N=4096 on this family"). If
borderline, ✅ stays with N-scaling annotation.

Design
------
- For each family in {Kerdock, SRHT, Hadamard}:
    For each N in {1024, 4096, 16384}:
      - Build W_alpha at alpha in {0, 0.25, 0.5, 0.75, 1.0}, 5 seeds each
        (matches the v174 baseline design at N=1024).
      - For each (alpha, seed): SVD; compute kappa profile k_2..k_6;
        sum|delta kappa_n|; run AMP + VAMP; AMP rel-err, VAMP rel-err.
    - Aggregate across alpha (mean of seeds): rho(AMP-rel-err, sum|delta
      kappa_n|), max VAMP rel-err.
- Output: ρ matrix [3 families × 3 N values] + max VAMP rel-err matrix.

NB: This is a GPU-routed depth probe per [[feedback-gpu-first-for-depth-
probes]] — N=16384 SVD on CPU is feasible (~2 min) but the 5-seed × 5-alpha
× 3-family × 3-N grid is 225 cells with N=16384 ones expensive. Route to
overnight_queue.

HARD PASS (Cap 12 ✅ survives E2 STRESS)
----------------------------------------
  rho >= 0.50 at N=16384 for ALL 3 families (Kerdock, SRHT, Hadamard)
  AND max VAMP rel-err < 0.20 across N=16384 cells.

HARD FAIL (Cap 12 ✅ reverts to 🟢 with N-bound annotation)
-----------------------------------------------------------
  rho < 0.30 on ANY of {Kerdock, SRHT, Hadamard} at N=16384.

MIDDLE BAND (Cap 12 ✅ stays with N-scaling annotation)
-------------------------------------------------------
  rho in [0.30, 0.50) at N=16384 on one family (partial); ✅ stays with
  N-scaling annotation.

Vertex: INTERP_FAMILY_N16384_PASS / KILLED / INCONCLUSIVE

Pre-reg: preregs/2026-05-24_wave14_interp_family_N16384_v1.md
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

# Reuse cross-codebook v1 builders (sylvester, etc.).
_cc_path = REPO / "experiments" / "exp_wave14_kappa_profile_cross_codebook_v1.py"
_spec_cc = importlib.util.spec_from_file_location("kappa_cc_v1", _cc_path)
_cc = importlib.util.module_from_spec(_spec_cc)
_spec_cc.loader.exec_module(_cc)

# Reuse BBMD-VAMP correspondence v1 helpers (AMP-SE, VAMP-SE, AMP loop, VAMP loop).
_bv_path = REPO / "experiments" / "exp_wave14_bbmd_vamp_correspondence_sweep_v1.py"
_spec_bv = importlib.util.spec_from_file_location("bbmd_vamp_v1", _bv_path)
_bv = importlib.util.module_from_spec(_spec_bv)
_spec_bv.loader.exec_module(_bv)
amp_se_scalar = _bv.amp_se_scalar
vamp_se_closed = _bv.vamp_se_closed
run_amp = _bv.run_amp
run_vamp = _bv.run_vamp

# Reuse Kerdock 4-coset codebook builder (with PRIMITIVE_POLY t in {5,6,7}).
_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
_spec_v3 = importlib.util.spec_from_file_location("v3_kerdock", _v3_path)
_v3 = importlib.util.module_from_spec(_spec_v3)
_spec_v3.loader.exec_module(_v3)
make_kerdock_4coset_codebook = _v3.make_kerdock_4coset_codebook

# Reuse kappa-profile inversion.
_v1_path = REPO / "experiments" / "exp_wave14_kappa_n_profile_v1.py"
_spec_v1 = importlib.util.spec_from_file_location("kappa_v1", _v1_path)
_v1 = importlib.util.module_from_spec(_spec_v1)
_spec_v1.loader.exec_module(_v1)
moments_to_free_cumulants_general = _v1.moments_to_free_cumulants_general


FAMILIES = ("kerdock", "srht", "hadamard")
N_GRID = (1024, 4096, 16384)
ALPHA_INTERP_LIST = (0.0, 0.25, 0.5, 0.75, 1.0)
N_MAX_MOMENT = 6


# ---------------------------------------------------------------------------
# Un-normalized builders (same scale as +/-1 entries, normalize by sqrt(N) at end)
# ---------------------------------------------------------------------------

def build_srht_unnormalized(N: int, M: int, seed: int) -> np.ndarray:
    import torch
    n_log2 = int(round(math.log2(N)))
    assert 2 ** n_log2 == N, f"N={N} must be power of 2"
    sylvester_hadamard = _cc.sylvester_hadamard
    H = sylvester_hadamard(n_log2, torch.device("cpu")).numpy().astype(np.float32)
    rng = np.random.default_rng(seed)
    D_diag = rng.choice([-1.0, 1.0], size=N).astype(np.float32)
    DH = H * D_diag[np.newaxis, :]
    row_idx = rng.choice(N, size=M, replace=False)
    return DH[row_idx].astype(np.float32)


def build_hadamard_unnormalized(N: int, M: int, seed: int) -> np.ndarray:
    import torch
    n_log2 = int(round(math.log2(N)))
    assert 2 ** n_log2 == N, f"N={N} must be power of 2"
    sylvester_hadamard = _cc.sylvester_hadamard
    H = sylvester_hadamard(n_log2, torch.device("cpu")).numpy().astype(np.float32)
    rng = np.random.default_rng(seed)
    row_idx = rng.choice(N, size=M, replace=False)
    return H[row_idx].astype(np.float32)


def build_kerdock_unnormalized(N: int, M: int, seed: int) -> np.ndarray:
    """Row-subsample of substrate Kerdock 4-coset codebook (4N codewords in
    {+1,-1}). Same un-normalized scale as Hadamard / SRHT for the alpha
    interpolation. PRIMITIVE_POLY supports t in {5 (N=1024), 6 (N=4096),
    7 (N=16384)}.
    """
    import torch
    cb, _info = make_kerdock_4coset_codebook(N, torch.device("cpu"))
    # cb is in {+1, -1} (bipolar codewords, un-normalized). Subsample M rows.
    rng = np.random.default_rng(seed)
    idx = rng.choice(cb.shape[0], size=M, replace=False)
    A = cb[idx].float().numpy().astype(np.float32)
    return A


FAMILY_BUILDERS = {
    "kerdock": build_kerdock_unnormalized,
    "srht":    build_srht_unnormalized,
    "hadamard": build_hadamard_unnormalized,
}


def build_W_alpha(family: str, alpha: float, N: int, M: int, seed: int,
                  struct_cache: dict) -> np.ndarray:
    cache_key = (family, N, M, seed)
    if cache_key not in struct_cache:
        builder = FAMILY_BUILDERS[family]
        struct_cache[cache_key] = builder(N, M, seed)
    W_struct = struct_cache[cache_key]
    rng_g = np.random.default_rng(seed + 1_000_000)
    G = rng_g.standard_normal(size=W_struct.shape).astype(np.float32)
    W = (1.0 - alpha) * G + alpha * W_struct
    return (W / math.sqrt(N)).astype(np.float32)


def bbmd_distance(kappas: list[float], c_ref: float, n_min: int = 2,
                  n_max: int = N_MAX_MOMENT) -> float:
    if not kappas or len(kappas) < n_max:
        return float("nan")
    return float(sum(abs(kappas[n - 1] - c_ref) for n in range(n_min, n_max + 1)))


# ---------------------------------------------------------------------------
# Per-cell aggregation: one rho per (family, N) over alpha grid
# ---------------------------------------------------------------------------

def compute_rho_per_family_N(cells: list[dict]) -> dict:
    """Bucket cells by (family, N); compute rho(amp_rel_err, bbmd_dist) and
    max VAMP rel-err over alpha grid for each bucket.
    """
    buckets: dict = {}
    for c in cells:
        key = (c["family"], c["N"])
        buckets.setdefault(key, []).append(c)
    by_fn = {}
    for (fam, N), bucket in buckets.items():
        dists = [b["bbmd_distance_mean"] for b in bucket
                 if math.isfinite(b.get("bbmd_distance_mean", float("nan")))]
        amp_errs = [b["amp_rel_err_mean"] for b in bucket
                    if math.isfinite(b.get("amp_rel_err_mean", float("nan")))]
        vamp_errs = [b["vamp_rel_err_mean"] for b in bucket
                     if math.isfinite(b.get("vamp_rel_err_mean", float("nan")))]
        if len(dists) < 3 or len(amp_errs) < 3 or len(vamp_errs) < 3:
            by_fn[f"{fam}@N={N}"] = {
                "rho": float("nan"), "max_vamp_rel_err": float("nan"),
                "n_alpha_cells": len(dists),
                "reason": "too few valid alpha cells",
            }
            continue
        rho_r = spearmanr(amp_errs, dists)
        rho = float(rho_r.statistic) if hasattr(rho_r, "statistic") else float(rho_r[0])
        max_v = float(max(vamp_errs))
        by_fn[f"{fam}@N={N}"] = {
            "rho": rho, "max_vamp_rel_err": max_v,
            "n_alpha_cells": len(dists),
        }
    return by_fn


def compute_verdict(summary: dict) -> tuple[str, str]:
    """E2 STRESS bands:
       HARD PASS: rho >= 0.50 at N=16384 for ALL 3 families AND max VAMP
                  rel-err < 0.20 at N=16384 across families.
       HARD FAIL: rho < 0.30 at N=16384 on ANY of the 3 families.
       MIDDLE BAND: rho in [0.30, 0.50) at N=16384 on one family.
    """
    rho_map = summary.get("rho_per_family_N") or {}
    summary["rho_per_family_N_serialized"] = dict(rho_map)

    if not rho_map:
        return ("INTERP_FAMILY_N16384_INCONCLUSIVE",
                "rho_per_family_N empty; no cells aggregated.")

    n16k_keys = [k for k in rho_map.keys() if k.endswith("@N=16384")]
    if len(n16k_keys) < 3:
        return ("INTERP_FAMILY_N16384_INCONCLUSIVE",
                f"Only {len(n16k_keys)} families at N=16384; need 3. "
                f"Available: {list(rho_map.keys())}")

    n16k_rho = {k: rho_map[k]["rho"] for k in n16k_keys}
    n16k_vamp = {k: rho_map[k].get("max_vamp_rel_err", float("nan")) for k in n16k_keys}
    summary["rho_at_N16384"] = n16k_rho
    summary["max_vamp_at_N16384"] = n16k_vamp

    # Drop NaN entries (treated as inconclusive)
    rho_vals = [v for v in n16k_rho.values() if math.isfinite(v)]
    vamp_vals = [v for v in n16k_vamp.values() if math.isfinite(v)]

    if len(rho_vals) < 3:
        return ("INTERP_FAMILY_N16384_INCONCLUSIVE",
                f"NaN rho at N=16384 for some family. rho_per_family_N16384 = "
                f"{n16k_rho}; need all 3 finite to call verdict.")

    min_rho = min(rho_vals)
    max_vamp = max(vamp_vals) if vamp_vals else float("nan")

    # HARD FAIL: ANY family at N=16384 has rho < 0.30
    if min_rho < 0.30:
        bad = [k for k, r in n16k_rho.items() if r < 0.30]
        return ("INTERP_FAMILY_N16384_KILLED",
                f"AMP-error predictor breaks at N=16384 on {bad}: "
                f"rho={n16k_rho}. The kappa_n divergence sum was an "
                f"N=1024 artifact; Cap 12 ✅ reverts to 🟢 with "
                f"N-bound annotation (predictor holds up to ~N=4096).")

    # HARD PASS: ALL families at N=16384 have rho >= 0.50 AND max VAMP < 0.20
    if min_rho >= 0.50 and max_vamp < 0.20:
        return ("INTERP_FAMILY_N16384_PASS",
                f"AMP-error predictor survives N-scaling: rho={n16k_rho} "
                f">= 0.50 at N=16384 on ALL 3 families; max VAMP rel-err = "
                f"{max_vamp:.4f} < 0.20. Cap 12 ✅ survives E2 STRESS; "
                f"kappa_n divergence is a TRUE customer-scale meta-tool.")

    # MIDDLE BAND: one family in [0.30, 0.50)
    return ("INTERP_FAMILY_N16384_INCONCLUSIVE",
            f"Partial N-scaling robustness: rho={n16k_rho}; max VAMP "
            f"rel-err = {max_vamp:.4f}. One or more families in [0.30, 0.50) "
            f"or VAMP rel-err in [0.10, 0.20). Cap 12 ✅ stays with "
            f"N-scaling annotation.")


# ---------------------------------------------------------------------------
# Self-tests (per [[feedback-strategy-spec-formula-selftests]])
# ---------------------------------------------------------------------------

def self_test() -> None:
    # Self-test 1: bbmd_distance on MP-reference -> 0
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
    assert abs(rho_val - 1.0) < 1e-9, f"spearman on monotone should be 1.0 got {rho_val}"

    # Self-test 4: compute_rho_per_family_N buckets correctly
    fake_cells = [
        {"family": "kerdock", "N": 1024, "bbmd_distance_mean": 0.05, "amp_rel_err_mean": 0.02, "vamp_rel_err_mean": 0.02},
        {"family": "kerdock", "N": 1024, "bbmd_distance_mean": 0.20, "amp_rel_err_mean": 0.10, "vamp_rel_err_mean": 0.04},
        {"family": "kerdock", "N": 1024, "bbmd_distance_mean": 0.60, "amp_rel_err_mean": 0.25, "vamp_rel_err_mean": 0.06},
        {"family": "kerdock", "N": 16384, "bbmd_distance_mean": 0.05, "amp_rel_err_mean": 0.02, "vamp_rel_err_mean": 0.02},
        {"family": "kerdock", "N": 16384, "bbmd_distance_mean": 0.20, "amp_rel_err_mean": 0.10, "vamp_rel_err_mean": 0.04},
        {"family": "kerdock", "N": 16384, "bbmd_distance_mean": 0.60, "amp_rel_err_mean": 0.25, "vamp_rel_err_mean": 0.06},
    ]
    rho_map = compute_rho_per_family_N(fake_cells)
    assert "kerdock@N=1024" in rho_map
    assert "kerdock@N=16384" in rho_map
    assert abs(rho_map["kerdock@N=1024"]["rho"] - 1.0) < 1e-9
    assert abs(rho_map["kerdock@N=16384"]["rho"] - 1.0) < 1e-9
    assert rho_map["kerdock@N=1024"]["n_alpha_cells"] == 3

    # Self-test 5: PASS verdict (all 3 families at N=16384, rho >= 0.50, VAMP < 0.20)
    rho_pass = {
        "kerdock@N=1024":  {"rho": 0.90, "max_vamp_rel_err": 0.05, "n_alpha_cells": 5},
        "kerdock@N=4096":  {"rho": 0.80, "max_vamp_rel_err": 0.06, "n_alpha_cells": 5},
        "kerdock@N=16384": {"rho": 0.75, "max_vamp_rel_err": 0.08, "n_alpha_cells": 5},
        "srht@N=1024":     {"rho": 0.70, "max_vamp_rel_err": 0.05, "n_alpha_cells": 5},
        "srht@N=4096":     {"rho": 0.65, "max_vamp_rel_err": 0.07, "n_alpha_cells": 5},
        "srht@N=16384":    {"rho": 0.60, "max_vamp_rel_err": 0.08, "n_alpha_cells": 5},
        "hadamard@N=1024": {"rho": 0.70, "max_vamp_rel_err": 0.05, "n_alpha_cells": 5},
        "hadamard@N=4096": {"rho": 0.65, "max_vamp_rel_err": 0.07, "n_alpha_cells": 5},
        "hadamard@N=16384":{"rho": 0.55, "max_vamp_rel_err": 0.10, "n_alpha_cells": 5},
    }
    # min rho at N=16384 = 0.55 >= 0.50; max VAMP = 0.10 < 0.20 -> PASS
    v, msg = compute_verdict({"rho_per_family_N": rho_pass})
    assert v == "INTERP_FAMILY_N16384_PASS", f"expected PASS got {v}: {msg}"

    # Self-test 6: HARD FAIL (one family rho < 0.30 at N=16384)
    rho_fail = dict(rho_pass)
    rho_fail["hadamard@N=16384"] = {"rho": 0.20, "max_vamp_rel_err": 0.05, "n_alpha_cells": 5}
    v, msg = compute_verdict({"rho_per_family_N": rho_fail})
    assert v == "INTERP_FAMILY_N16384_KILLED", f"expected KILLED got {v}: {msg}"

    # Self-test 7: MIDDLE BAND (one family rho in [0.30, 0.50) at N=16384)
    rho_mid = dict(rho_pass)
    rho_mid["hadamard@N=16384"] = {"rho": 0.40, "max_vamp_rel_err": 0.05, "n_alpha_cells": 5}
    v, msg = compute_verdict({"rho_per_family_N": rho_mid})
    assert v == "INTERP_FAMILY_N16384_INCONCLUSIVE", f"expected INCONCLUSIVE got {v}: {msg}"

    # Self-test 8: missing families at N=16384
    rho_missing = {k: v for k, v in rho_pass.items() if not k.endswith("@N=16384")}
    v, _ = compute_verdict({"rho_per_family_N": rho_missing})
    assert v == "INTERP_FAMILY_N16384_INCONCLUSIVE"

    # Self-test 9: VAMP blowup (rho good but VAMP > 0.20 -> middle band, not fail)
    rho_vamp = dict(rho_pass)
    rho_vamp["kerdock@N=16384"] = {"rho": 0.75, "max_vamp_rel_err": 0.25, "n_alpha_cells": 5}
    # rho min=0.55 still >= 0.50, but max VAMP=0.25 > 0.20 -> NOT pass; rho>=0.30 -> NOT fail -> INCONCLUSIVE
    v, _ = compute_verdict({"rho_per_family_N": rho_vamp})
    assert v == "INTERP_FAMILY_N16384_INCONCLUSIVE", f"expected INCONCLUSIVE from VAMP, got {v}"

    print("interp-family N=16384 self-test passed (9/9 cases)", flush=True)


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    if smoke:
        config = {
            "mode": "smoke",
            "N_grid": [64],
            "M_over_N": 1.0,
            "alpha_interp_list": [0.0, 0.5, 1.0],
            "sigma_noise": 0.1,
            "signal_var": 1.0,
            "n_seeds": 1,
            "n_iter": 50,
            "n_max_moment": N_MAX_MOMENT,
            "families": ["srht", "hadamard"],  # kerdock at N=64 fails (PRIMITIVE_POLY t=5 minimum -> N=1024)
        }
    else:
        config = {
            "mode": "full",
            "N_grid": list(N_GRID),
            "M_over_N": 1.0,
            "alpha_interp_list": list(ALPHA_INTERP_LIST),
            "sigma_noise": 0.1,
            "signal_var": 1.0,
            "n_seeds": 5,
            "n_iter": 300,
            "n_max_moment": N_MAX_MOMENT,
            "families": list(FAMILIES),
        }

    sigma = config["sigma_noise"]
    sigma_sq = sigma ** 2
    signal_var = config["signal_var"]
    n_max = config["n_max_moment"]
    n_seeds = config["n_seeds"]
    n_iter = config["n_iter"]
    alpha_list = config["alpha_interp_list"]

    print(f"[setup] families={config['families']} N_grid={config['N_grid']} "
          f"alpha_interp={alpha_list} seeds={n_seeds} mode={config['mode']}",
          flush=True)

    struct_cache: dict = {}
    cells = []
    for family in config["families"]:
        for N in config["N_grid"]:
            M = max(1, int(config["M_over_N"] * N))
            alpha_ratio = M / N
            amp_se_pred = amp_se_scalar(alpha_ratio, sigma_sq, signal_var)
            print(f"\n[family={family} N={N} M={M}]", flush=True)

            for alpha_int in alpha_list:
                seed_records = []
                for seed in range(n_seeds):
                    seed_val = seed * 1000 + 23
                    W = build_W_alpha(family, alpha_int, N, M, seed_val,
                                      struct_cache)
                    U, s, Vt = np.linalg.svd(W, full_matrices=False)
                    eig = (s ** 2).astype(np.float64)
                    moms = [float(np.mean(eig ** n)) for n in range(1, n_max + 1)]
                    kappas = moments_to_free_cumulants_general(moms)
                    d_bbmd = bbmd_distance(kappas, alpha_ratio, n_min=2,
                                           n_max=n_max)

                    vamp_se_pred = vamp_se_closed(s, N, M, sigma_sq, signal_var)

                    rng_sig = np.random.default_rng(seed_val + 77)
                    x_true = rng_sig.standard_normal(N).astype(np.float64) * math.sqrt(signal_var)
                    noise = rng_sig.standard_normal(M).astype(np.float64) * sigma
                    y = (W.astype(np.float64) @ x_true) + noise

                    amp_emp = run_amp(W, y, x_true, signal_var, sigma_sq, n_iter)
                    vamp_emp = run_vamp(U, s, Vt, y, x_true, signal_var, sigma_sq, n_iter)

                    amp_rel = abs(amp_emp - amp_se_pred) / max(amp_emp, amp_se_pred, 1e-12)
                    vamp_rel = abs(vamp_emp - vamp_se_pred) / max(vamp_emp, vamp_se_pred, 1e-12)

                    seed_records.append({
                        "seed": seed_val, "kappas": kappas,
                        "bbmd_distance": d_bbmd, "amp_emp": amp_emp,
                        "amp_rel_err": amp_rel, "vamp_emp": vamp_emp,
                        "vamp_rel_err": vamp_rel,
                    })
                    print(f"    family={family} N={N} alpha={alpha_int:.2f} "
                          f"seed={seed} bbmd={d_bbmd:.4f} amp_rel={amp_rel:.3f} "
                          f"vamp_rel={vamp_rel:.3f}", flush=True)

                d_mean = float(np.mean([r["bbmd_distance"] for r in seed_records]))
                amp_rel_mean = float(np.mean([r["amp_rel_err"] for r in seed_records]))
                vamp_rel_mean = float(np.mean([r["vamp_rel_err"] for r in seed_records]))
                cells.append({
                    "family": family, "N": N, "alpha_interp": float(alpha_int),
                    "bbmd_distance_mean": d_mean,
                    "amp_rel_err_mean": amp_rel_mean,
                    "vamp_rel_err_mean": vamp_rel_mean,
                    "n_seeds": n_seeds,
                })
                print(f"  AGG family={family} N={N} alpha={alpha_int:.2f}: "
                      f"bbmd={d_mean:.4f} amp_rel={amp_rel_mean:.4f} "
                      f"vamp_rel={vamp_rel_mean:.4f}", flush=True)

    rho_map = compute_rho_per_family_N(cells)
    print(f"\n[rho per (family, N)] {rho_map}", flush=True)

    summary = {"cells": cells, "config": config, "rho_per_family_N": rho_map}
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
        "verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
        "summary": summary, "config": config,
    }
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


def run_smoke() -> None:
    self_test()
    out_dir = get_output_dir("wave14_interp_family_N16384_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["cells"]) >= 1, "smoke FAIL: no cells produced"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_interp_family_N16384_v1")
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
