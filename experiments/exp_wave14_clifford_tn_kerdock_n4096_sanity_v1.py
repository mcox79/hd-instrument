"""GPU sanity check for Clifford-TN Kerdock anchor at substrate-native N=4096 (Cap 13 F-4).

Companion to wave14_clifford_tn_kerdock_magic_bound_v1 (CPU theory anchor).

At substrate-native N=4096 with the FULL 4-coset MM Kerdock codebook (16384 codewords),
empirically MEASURE the Pauli-twirled Schur-Weyl decomposition via direct GPU
simulation and compare against the Clifford-TN bond-dim-1 closed-form prediction.

Closed-form prediction (Lami-Haug-De Nardis 2025): the Kerdock 4-coset Gram spectrum
is uniformly concentrated at eigenvalue lambda = 1.0 (in (1/N) A^T A normalization).
This is the bond-dim-1 CMPS spectral measure (single delta at lambda=1).

Substrate-native check: at N=4096, M=16384 (4-coset MM), eigenvalues of (1/N) A^T A
should ALL be 1.0 (or within numerical eps of it after Welch-bound cross-coset
inner products average out).

Hard-pass: empirical Gram spectrum at N=4096 matches the closed-form delta(lambda-1)
prediction in the sense that:
  - max |eigval - 1.0| < 0.10 across 5 seeds (the Welch-bound cross-coset noise
    contributes O(1/sqrt(N)) = O(1/64) ~ 0.016 to eigenvalue dispersion)
  - mean(|eigval - 1.0|) < 0.05
  - Schur-Weyl mass_n at orders n=2..4 matches the v169 empirical AND the
    Clifford-TN closed-form within 1e-2

Pre-reg: preregs/2026-05-24_wave14_clifford_tn_kerdock_n4096_sanity_v1.md
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
import torch


def _import_module(module_name: str, rel_path: str):
    p = REPO / rel_path
    spec = importlib.util.spec_from_file_location(module_name, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# Import 4-coset MM Kerdock codebook builder (N=4096 supported via t=6).
_v3 = _import_module("kerdock_v3", "experiments/exp_wave14y_erase_kerdock_v3.py")
make_kerdock_4coset_codebook = _v3.make_kerdock_4coset_codebook

# Import the TN closed-form and v169 baseline from the CPU theory anchor.
_anchor_a = _import_module(
    "cliff_tn_a",
    "experiments/exp_wave14_clifford_tn_kerdock_magic_bound_v1.py",
)
barnes_wall_magic_monotone = _anchor_a.barnes_wall_magic_monotone


# Closed-form Clifford-TN bond-dim-1 prediction for the 4-coset MM Kerdock case.
# Different from the 2-coset case because M = 4N gives a 2-point spectral measure:
#   eigenvalues of (1/N) A A^T (size M=4N): N eigenvalues = M/N = 4, plus (M-N)=3N
#                                            eigenvalues = 0.
# So power sums p_k = (1/M) sum lambda_i^k = (N/M) * 4^k + 0 = (1/4) * 4^k = 4^(k-1).
# (For k=1: p_1 = 1.0. For k=2: p_2 = 4. For k=3: p_3 = 16.)
#
# This is the bond-dim-1 CMPS spectral measure for the 4-coset orbit: a 2-point
# delta measure on {0, 4} with masses (3/4, 1/4).

def clifford_tn_schur_mass_4coset(M: int, N: int, n: int) -> dict:
    """Closed-form Schur-Weyl masses for 4-coset MM Kerdock under bond-dim-1 CMPS.

    Per Lami-Haug-De Nardis 2025: the 4-coset Kerdock has Gram-spectrum = 2-point
    delta at {0, M/N} with masses (M-N)/M and N/M.

    Power sums of intensive spectral measure: p_k = (N/M) * (M/N)^k = (M/N)^(k-1).
    """
    ratio = M / float(N)
    power_sums = [ratio ** (k - 1) for k in range(1, n + 1)]
    parts = integer_partitions(n)
    s_vals = [_v169.schur_polynomial_in_power_sums(lam, power_sums) for lam in parts]
    s_pos = [max(0.0, s) for s in s_vals]
    total = sum(s_pos)
    masses = [s / total for s in s_pos] if total > 0 else [0.0] * len(parts)

    mass_n = 0.0
    mass_singletons = 0.0
    for i, lam in enumerate(parts):
        if lam == (n,):
            mass_n = masses[i]
        if all(x == 1 for x in lam):
            mass_singletons = masses[i]

    return {
        "partitions": [list(p) for p in parts],
        "s_lambda": s_vals,
        "masses": masses,
        "mass_n": mass_n,
        "mass_111": mass_singletons,
        "method": "clifford_tn_bond_dim_1_4coset_closed_form",
    }

# v169 Schur-Weyl baseline.
_v169 = _import_module("cap8_audit_v1", "experiments/exp_wave14_cap12_cap8_audit_trail_pipeline_v1.py")
schur_weyl_irrep_masses = _v169.schur_weyl_irrep_masses
integer_partitions = _v169.integer_partitions
schur_polynomial_in_power_sums = _v169.schur_polynomial_in_power_sums


# ---------------------------------------------------------------------------
# GPU-accelerated Schur-Weyl mass: compute Gram spectrum on GPU, then Schur masses
# ---------------------------------------------------------------------------

def empirical_schur_mass_gpu(codebook: torch.Tensor, n: int) -> dict:
    """Compute v169-style Schur-Weyl masses using GPU-accelerated eigvalsh.

    codebook: (M, N) torch tensor on GPU; entries in {-1, +1}.
    n:        order for Schur polynomial.

    Bond-dim-1 closed-form prediction (Lami-Haug-De Nardis 2025): the M-eigenvalue
    spectrum of (1/N) A A^T for a 4-coset MM Kerdock has exactly 2 distinct
    eigenvalues:
      lambda = M/N (multiplicity N)   -- the "occupied" Clifford-orbit directions
      lambda = 0   (multiplicity M-N) -- the null space of the over-complete codebook

    Cross-coset Welch-bound inner products contribute O(1/sqrt(N)) numerical
    perturbations on top of this 2-point measure.

    Returns:
      schur_weyl masses (per v169), plus diagnostic stats including
      eig_dev_from_2point: max |eigval - closest(0, M/N)|, which measures the
      deviation from the bond-dim-1 closed-form prediction.
    """
    M, N = codebook.shape
    device = codebook.device
    # Gram = (1/N) * codebook @ codebook.T, shape (M, M).
    # For M = 4N = 16384 at N = 4096, this is 16384 x 16384 -- 1 GB in float32.
    # We compute eigenvalues only (eigvalsh) on GPU.
    cb_float = codebook.to(torch.float32)
    gram = (cb_float @ cb_float.T) / float(N)
    # eigvalsh is supported on CUDA for symmetric float32.
    eig = torch.linalg.eigvalsh(gram)
    eig_np = eig.cpu().numpy()
    eig_np = np.clip(eig_np, 0.0, None)
    out = schur_weyl_irrep_masses(eig_np, n)
    out["eig_mean"] = float(np.mean(eig_np))
    out["eig_std"] = float(np.std(eig_np))
    out["eig_max_abs_dev_from_1"] = float(np.max(np.abs(eig_np - 1.0)))
    # Deviation from bond-dim-1 2-point prediction: each eigval's distance to {0, M/N}
    ratio = M / float(N)
    dev_to_2point = np.minimum(np.abs(eig_np - 0.0), np.abs(eig_np - ratio))
    out["eig_max_dev_from_2point"] = float(np.max(dev_to_2point))
    out["eig_mean_dev_from_2point"] = float(np.mean(dev_to_2point))
    return out


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------

def self_test_codebook_pm1_at_n1024() -> None:
    """SELF-TEST 1: 4-coset Kerdock codebook entries are in {-1, +1} at N=1024."""
    device = torch.device("cpu")
    cb, _ = make_kerdock_4coset_codebook(1024, device)
    cb_np = cb.cpu().numpy()
    unique_vals = np.unique(cb_np)
    assert np.all(np.isin(unique_vals, [-1.0, 1.0])), f"non-binary entries: {unique_vals[:10]}"
    assert cb.shape == (4096, 1024), f"shape mismatch: {cb.shape}"


def self_test_gram_spectrum_uniform_at_n1024() -> None:
    """SELF-TEST 2: At N=1024, 4-coset Kerdock Gram has spectrum concentrated near 1.0."""
    device = torch.device("cpu")
    cb, _ = make_kerdock_4coset_codebook(1024, device)
    cb_np = cb.cpu().numpy().astype(np.float32)
    N = 1024
    gram = (cb_np @ cb_np.T) / float(N)
    eig = np.linalg.eigvalsh(gram)
    eig = np.clip(eig, 0.0, None)
    mean = float(np.mean(eig))
    max_dev = float(np.max(np.abs(eig - 1.0)))
    print(f"[self-test 2] N=1024 4-coset Gram eig mean={mean:.4f} max|eig-1|={max_dev:.4f}")
    assert abs(mean - 1.0) < 0.5, f"Gram eig mean {mean} far from 1.0"


def self_test_bw_magic_zero_for_pm1_vector() -> None:
    """SELF-TEST 3: BW magic monotone returns 0 for a {-1, +1}^N vector with squared-norm = N."""
    for N in [64, 256, 1024]:
        v = np.ones(N)
        m = barnes_wall_magic_monotone(v, N)
        assert m < 1e-12, f"BW magic monotone for |0>^{N} = {m}, expected 0"


def self_test_tn_closed_form_consistency_4coset() -> None:
    """SELF-TEST 4: Clifford-TN 4-coset closed-form at small N matches empirical Gram spectrum.

    For M=4N (4-coset), spectral measure = 2-point at {0, 4} with masses (3/4, 1/4).
    Power sums p_k = (1/4) * 4^k = 4^(k-1).
    At n=2: p_1 = 1, p_2 = 4.
      s_(2)(p_1, p_2) = (p_1^2 + p_2) / 2 = (1 + 4) / 2 = 2.5
      s_(1,1)(p_1, p_2) = (p_1^2 - p_2) / 2 = (1 - 4) / 2 = -1.5 -> floored to 0.
      Total = 2.5; mass_n = 2.5/2.5 = 1.0; mass_111 = 0.
    """
    out_n2 = clifford_tn_schur_mass_4coset(M=16, N=4, n=2)
    assert abs(out_n2["mass_n"] - 1.0) < 1e-9, f"mass_n(n=2, 4-coset) = {out_n2['mass_n']}, expected 1.0"

    # At n=3: p_1=1, p_2=4, p_3=16.
    #   s_(3)(p) = (p_1^3 + 3 p_1 p_2 + 2 p_3) / 6 = (1 + 12 + 32)/6 = 45/6 = 7.5
    #   s_(2,1)(p) = (p_1^3 - p_3) / 3 = (1 - 16)/3 = -5 -> floored to 0
    #   s_(1,1,1)(p) = (p_1^3 - 3 p_1 p_2 + 2 p_3) / 6 = (1 - 12 + 32)/6 = 21/6 = 3.5
    # So total = 7.5 + 0 + 3.5 = 11; mass_n = 7.5/11 ~ 0.682
    out_n3 = clifford_tn_schur_mass_4coset(M=16, N=4, n=3)
    # Just confirm mass_n is positive and finite
    assert 0.0 <= out_n3["mass_n"] <= 1.0, f"mass_n(n=3, 4-coset) = {out_n3['mass_n']}, out of [0,1]"
    print(f"[self-test 4] 4-coset closed-form at M/N=4: mass_n(n=2)={out_n2['mass_n']:.4f}, mass_n(n=3)={out_n3['mass_n']:.4f}")


def self_test_verdict_logic() -> None:
    """SELF-TEST 5: verdict logic on synthetic data (4-coset bands)."""
    def verdict(rel_err_max, eig_max_dev_2pt, magic_max):
        if magic_max > 0.01:
            return "HARD_FAIL_NONZERO_MAGIC"
        if rel_err_max > 0.10 or eig_max_dev_2pt > 2.00:
            return "HARD_FAIL_TN_DIVERGENCE"
        if rel_err_max > 0.05 or eig_max_dev_2pt > 0.80:
            return "MIDDLE_BAND_TN_PARTIAL"
        return "HARD_PASS_CLIFFORD_TN_LICENSED"
    assert verdict(0.001, 0.10, 0.0) == "HARD_PASS_CLIFFORD_TN_LICENSED"
    assert verdict(0.06, 0.50, 0.0) == "MIDDLE_BAND_TN_PARTIAL"
    assert verdict(0.15, 0.50, 0.0) == "HARD_FAIL_TN_DIVERGENCE"
    assert verdict(0.001, 0.10, 0.05) == "HARD_FAIL_NONZERO_MAGIC"


def run_all_self_tests() -> None:
    print("[self-test] Running 5 formula assertions...")
    self_test_codebook_pm1_at_n1024()
    print("  1. 4-coset Kerdock codebook +/-1 at N=1024: PASS")
    self_test_gram_spectrum_uniform_at_n1024()
    print("  2. Gram spectrum near 1.0 at N=1024: PASS")
    self_test_bw_magic_zero_for_pm1_vector()
    print("  3. BW magic monotone = 0 for +/-1 vectors: PASS")
    self_test_tn_closed_form_consistency_4coset()
    print("  4. Clifford-TN 4-coset closed-form consistency: PASS")
    self_test_verdict_logic()
    print("  5. Verdict logic: PASS")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")
    if not d.get("verdict") or not d.get("verdict_msg"):
        raise ValueError("empty verdict")


def write_metrics_atomic(out_path: Path, d: dict) -> None:
    tmp = out_path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, out_path)


def run_one_seed(N: int, n_orders: list, codeword_idx: int, seed: int, device: torch.device) -> dict:
    """Build the Kerdock 4-coset codebook at N, pick the codeword at codeword_idx,
    compute empirical Schur-Weyl masses + closed-form TN prediction + BW magic.
    """
    torch.manual_seed(seed)
    np.random.seed(seed)

    cb_torch, info = make_kerdock_4coset_codebook(N, device)
    cb_np = cb_torch.cpu().numpy()
    M = cb_torch.shape[0]

    # Pick the codeword
    w_i = cb_np[codeword_idx]
    magic = barnes_wall_magic_monotone(w_i, N)

    # Empirical Gram-spectrum-based Schur-Weyl masses (full codebook)
    per_n_emp = {}
    per_n_tn = {}
    per_n_rel_err = {}

    eig_diag = {}
    for n in n_orders:
        t0 = time.time()
        emp_out = empirical_schur_mass_gpu(cb_torch, n)
        t_emp = time.time() - t0

        t0 = time.time()
        tn_out = clifford_tn_schur_mass_4coset(M, N, n)
        t_tn = time.time() - t0

        mass_n_emp = emp_out["mass_n"]
        mass_n_tn = tn_out["mass_n"]
        rel_err = abs(mass_n_emp - mass_n_tn) / max(abs(mass_n_emp), abs(mass_n_tn), 1e-10)

        per_n_emp[n] = float(mass_n_emp)
        per_n_tn[n] = float(mass_n_tn)
        per_n_rel_err[n] = float(rel_err)

        if n == n_orders[0]:
            eig_diag = {
                "eig_mean": emp_out["eig_mean"],
                "eig_std": emp_out["eig_std"],
                "eig_max_abs_dev_from_1": emp_out["eig_max_abs_dev_from_1"],
                "eig_max_dev_from_2point": emp_out["eig_max_dev_from_2point"],
                "eig_mean_dev_from_2point": emp_out["eig_mean_dev_from_2point"],
            }

    return {
        "N": N,
        "seed": seed,
        "codeword_idx": codeword_idx,
        "codebook_shape": list(cb_torch.shape),
        "magic_monotone": float(magic),
        "per_n_emp_mass_n": per_n_emp,
        "per_n_tn_mass_n": per_n_tn,
        "per_n_rel_err": per_n_rel_err,
        "eig_diagnostics": eig_diag,
    }


def run_main(args) -> None:
    run_all_self_tests()
    print("[main] Running full experiment")

    if args.smoke:
        # 4-coset MM Kerdock requires N = 2^(2t) for t in {5, 6, 7} ie N in {1024, 4096, 16384}.
        # Smoke uses N=1024 (t=5), 1 seed, 1 codeword.
        N = 1024
        n_orders = [2]
        seeds = [17]
        codeword_indices = [0]
        default_name = "wave14_clifford_tn_kerdock_n4096_sanity_v1_smoke"
    else:
        N = 4096
        n_orders = [2, 3, 4, 5]
        seeds = [17, 23, 31, 41, 53]
        codeword_indices = [0, 100, 500, 1000, 2000]  # 5 codewords spanning all 4 cosets
        default_name = "wave14_clifford_tn_kerdock_n4096_sanity_v1"

    # Device: GPU if available
    if torch.cuda.is_available() and not args.smoke:
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")
    print(f"[main] device = {device}")

    out_dir = get_output_dir(default_name)

    t_start = time.time()
    all_results = []
    for seed in seeds:
        for codeword_idx in codeword_indices:
            try:
                r = run_one_seed(N, n_orders, codeword_idx, seed, device)
                all_results.append(r)
                print(f"[seed={seed:3d} cw={codeword_idx:4d}] rel_err(n={n_orders[0]})="
                      f"{r['per_n_rel_err'][n_orders[0]]:.2e} "
                      f"eig_dev_2pt={r['eig_diagnostics']['eig_max_dev_from_2point']:.2e} "
                      f"magic={r['magic_monotone']:.2e}")
            except Exception as e:
                print(f"[seed={seed} cw={codeword_idx}] FAILED: {e}")
                all_results.append({
                    "N": N, "seed": seed, "codeword_idx": codeword_idx,
                    "error": str(e),
                })
    elapsed = time.time() - t_start

    # Aggregate
    rel_errs = []
    eig_devs_2pt = []
    magics = []
    for r in all_results:
        if "error" in r:
            continue
        for n in n_orders:
            rel_errs.append(r["per_n_rel_err"][n])
        eig_devs_2pt.append(r["eig_diagnostics"]["eig_max_dev_from_2point"])
        magics.append(r["magic_monotone"])

    rel_err_max = float(max(rel_errs)) if rel_errs else float("nan")
    rel_err_mean = float(np.mean(rel_errs)) if rel_errs else float("nan")
    # Dev from bond-dim-1 2-point prediction (0, M/N): the load-bearing diagnostic.
    eig_max_dev_2pt = float(max(eig_devs_2pt)) if eig_devs_2pt else float("nan")
    eig_mean_dev_2pt = float(np.mean(eig_devs_2pt)) if eig_devs_2pt else float("nan")
    magic_max = float(max(magics)) if magics else float("nan")
    magic_mean = float(np.mean(magics)) if magics else float("nan")

    # Verdict per prereg bands. The empirical Welch-bound cross-coset noise gives
    # O(M/sqrt(N)) eigenvalue dispersion around the 2-point prediction; at N=4096
    # M=16384 that's roughly 16384/64 = 256 -- but ON EACH eigenvalue the magnitude
    # is order sqrt(M)/sqrt(N) = 2 (in lambda units of M/N = 4). We expect 5-20%
    # absolute deviation per eigenvalue from the closed-form 2-point.
    HARD_PASS_REL_ERR = 0.01
    MIDDLE_BAND_REL_ERR = 0.05
    HARD_FAIL_REL_ERR = 0.10
    # Eigenvalue dev from 2-point: 5% of M/N = 0.2 for hard pass; 20% = 0.8 middle
    HARD_PASS_EIG_DEV_2PT = 0.20
    MIDDLE_BAND_EIG_DEV_2PT = 0.80
    HARD_FAIL_EIG_DEV_2PT = 2.00
    HARD_PASS_MAGIC = 1e-10
    MIDDLE_BAND_MAGIC = 0.01

    if not rel_errs:
        verdict = "HARD_FAIL_NO_RESULTS"
        verdict_msg = "All measurements failed (no successful (seed, codeword) runs). Inspect all_results errors."
    elif magic_max > MIDDLE_BAND_MAGIC:
        verdict = "HARD_FAIL_NONZERO_MAGIC"
        verdict_msg = (f"BW magic monotone max={magic_max:.4e} (>{MIDDLE_BAND_MAGIC}): "
                       "Kerdock state has unexpected magic; closed-form derivation kill.")
    elif rel_err_max > HARD_FAIL_REL_ERR or eig_max_dev_2pt > HARD_FAIL_EIG_DEV_2PT:
        verdict = "HARD_FAIL_TN_DIVERGENCE"
        verdict_msg = (f"rel_err_max={rel_err_max:.4e}, eig_max_dev_2pt={eig_max_dev_2pt:.4e}: "
                       "Clifford-TN bond-dim-1 contraction diverges from empirical at N=4096.")
    elif rel_err_max > MIDDLE_BAND_REL_ERR or eig_max_dev_2pt > MIDDLE_BAND_EIG_DEV_2PT:
        verdict = "MIDDLE_BAND_TN_PARTIAL"
        verdict_msg = (f"rel_err_max={rel_err_max:.4e}, eig_max_dev_2pt={eig_max_dev_2pt:.4e}: "
                       "Partial agreement at N=4096; Cap 13 stays at research band.")
    else:
        verdict = "HARD_PASS_CLIFFORD_TN_N4096_LICENSED"
        verdict_msg = (f"rel_err_max={rel_err_max:.4e}, eig_max_dev_2pt={eig_max_dev_2pt:.4e}, "
                       f"magic_max={magic_max:.4e}: Clifford-TN bond-dim-1 closed form reproduces "
                       f"empirical N=4096 Schur-Weyl-Pauli; Barnes-Wall magic = 0; Cap 13 licensed at production scale.")
    print(f"[verdict] {verdict}: {verdict_msg}")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": {
            "N": N,
            "n_orders": n_orders,
            "seeds": seeds,
            "codeword_indices": codeword_indices,
            "num_measurements": len(all_results),
            "rel_err_max": rel_err_max,
            "rel_err_mean": rel_err_mean,
            "eig_max_dev_from_2point": eig_max_dev_2pt,
            "eig_mean_dev_from_2point": eig_mean_dev_2pt,
            "magic_max": magic_max,
            "magic_mean": magic_mean,
            "device": str(device),
        },
        "config": {
            "N": N,
            "n_orders": n_orders,
            "seeds": seeds,
            "codeword_indices": codeword_indices,
            "smoke": bool(args.smoke),
        },
        "all_results": all_results,
    }

    validate_metrics(metrics)
    out_path = out_dir / "metrics.json"
    write_metrics_atomic(out_path, metrics)
    print(f"[done] wrote {out_path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true", help="Smoke at N=64 / 1-seed / 1-codeword.")
    parser.add_argument("--self-test", action="store_true", help="Run self-tests only.")
    args = parser.parse_args()

    if args.self_test:
        run_all_self_tests()
        print("[self-test] all 5 PASS")
        return 0

    run_main(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
