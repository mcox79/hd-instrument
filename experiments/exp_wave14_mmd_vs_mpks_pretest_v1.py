"""MMD / Sliced-Wasserstein vs MP-KS: alternative pre-test scores for Cap 12.

Research's anchor proposal #3 identified MMD-with-RBF-kernel and Sliced-
Wasserstein as candidates that may strictly out-perform MP-KS for the Cap 12
pre-test. If true, this either (a) tightens the v175 Cap-12 ✅ predictor from
rho=0.700 (MP-KS) to >= 0.75 (MMD/Wasserstein), or (b) reveals that v175's
rho=0.700 was a test-power artifact (the underlying signal is stronger but
KS doesn't capture it).

Design
------
For each codebook in {iid_gauss, srht, hadamard, rm_1_m, kerdock} at N=1024,
5 seeds:
  1. Build W; SVD to get empirical eigenvalues eig.
  2. Compute MP-KS score (Cap 12 baseline).
  3. Compute MMD-RBF score (between empirical eig and MP reference eig).
  4. Compute Sliced-Wasserstein-1D score (1-Wasserstein between empirical
     and MP reference CDFs).
  5. Run AMP -> empirical AMP-rel-err.
  6. Per codebook (mean across seeds): record all 4 quantities (KS, MMD, W1,
     amp_rel_err).
  7. Across 5 codebook cells, compute Spearman rho(amp_rel_err, score) for
     each of the 3 scores.

Score definitions
-----------------
1. MP-KS (Cap 12 baseline; via mp_ks_stat): empirical CDF distance to MP CDF.

2. MMD-RBF: Maximum Mean Discrepancy with Gaussian kernel between empirical
   eigenvalue samples {lambda_i} and reference samples drawn from MP density.
     MMD^2 = (1/n^2) sum_{i,j} k(x_i, x_j)
           + (1/m^2) sum_{i,j} k(y_i, y_j)
           - (2/nm) sum_{i,j} k(x_i, y_j)
   where k(a,b) = exp(-|a-b|^2 / (2 sigma_kernel^2)). We use sigma_kernel
   chosen by the median heuristic on the pooled sample (standard practice
   in the MMD literature; Gretton et al. 2012).

3. Sliced-Wasserstein 1D (W1): for 1D distributions, exact W1 = integral of
   |F_x(t) - F_y(t)| dt = mean |x_(i) - y_(i)| after sorting (the "earth-
   mover's distance" between order statistics). With same n samples each
   side, this is the standard "1D OT" closed form.

Reference distribution
----------------------
MP density at ratio c = M/N has support [(1-sqrt(c))^2, (1+sqrt(c))^2] (for
c <= 1) with pdf rho_MP(x) = sqrt((b-x)(x-a)) / (2 pi c x). We sample N_ref
points by inverse-CDF sampling (numerical) from this density and use that
as the reference set for MMD and W1.

HARD PASS (MMD or Wasserstein strictly better than MP-KS by > 5%)
------------------------------------------------------------------
- rho_MMD >= 0.75 OR rho_Wasserstein >= 0.75
- AND routing accuracy at the new score's natural threshold (tau*-equivalent)
  >= MP-KS's 4/5 baseline (the v175 ✅ result).

HARD FAIL (MMD/Wasserstein add nothing)
---------------------------------------
- Both rho_MMD AND rho_Wasserstein <= 0.70 (no improvement over MP-KS)
- AND neither's routing accuracy at any natural tau* beats MP-KS.

MIDDLE BAND
-----------
- rho improvement < 5% over MP-KS (rho_alt in (rho_KS, rho_KS+0.05]) -- marginal.

Honest framing
--------------
This is a META-tool experiment: it interrogates Cap 12's own design. PASS
gives Strategy a license to swap the score in the next Cap 12 revision (or
add MMD as a secondary pre-test). FAIL hardens the v175 ✅ claim by showing
MP-KS is at least as good as the alternatives.

Vertex: MMD_VS_MPKS_PRETEST_PASS / KILLED / INCONCLUSIVE

Pre-reg: preregs/2026-05-24_wave14_mmd_vs_mpks_pretest_v1.md
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

# Reuse cross-codebook v1 builders + MP-KS routine
_cc_path = REPO / "experiments" / "exp_wave14_kappa_profile_cross_codebook_v1.py"
_spec_cc = importlib.util.spec_from_file_location("kappa_cc_v1", _cc_path)
_cc = importlib.util.module_from_spec(_spec_cc)
_spec_cc.loader.exec_module(_cc)
build_iid_gauss = _cc.build_iid_gauss
build_srht = _cc.build_srht
build_hadamard = _cc.build_hadamard
build_rm_1_m = _cc.build_rm_1_m
build_kerdock = _cc.build_kerdock
mp_ks_stat = _cc.mp_ks_stat

# Reuse BBMD-VAMP AMP/VAMP loops
_bv_path = REPO / "experiments" / "exp_wave14_bbmd_vamp_correspondence_sweep_v1.py"
_spec_bv = importlib.util.spec_from_file_location("bbmd_vamp_v1", _bv_path)
_bv = importlib.util.module_from_spec(_spec_bv)
_spec_bv.loader.exec_module(_bv)
amp_se_scalar = _bv.amp_se_scalar
run_amp = _bv.run_amp


CODEBOOKS = [
    ("iid_gauss", build_iid_gauss, "AMP_OK"),
    ("srht",      build_srht,      "AMP_OK"),
    ("hadamard",  build_hadamard,  "VAMP_REQUIRED"),
    ("rm_1_m",    build_rm_1_m,    "VAMP_REQUIRED"),
    ("kerdock",   build_kerdock,   "VAMP_REQUIRED"),
]


# ---------------------------------------------------------------------------
# Reference distribution: MP density inverse-CDF sampler
# ---------------------------------------------------------------------------

def sample_mp_reference(c: float, n_samples: int, seed: int = 0) -> np.ndarray:
    """Reference Marchenko-Pastur eigenvalue samples.

    Implementation: empirical eigenvalues of a large iid Gaussian matrix whose
    aspect ratio matches c = M/N. The empirical eigenvalue distribution of
    (1/N) W W^T for iid N(0,1) entries converges to the MP density at ratio
    M/N (Marchenko-Pastur theorem). At N = max(n_samples, 1024) this gives a
    clean numerical reference WITHOUT the 1/x singularity at the lower edge
    that destroys naive inverse-CDF samplers for c near 1.

    Returns n_samples eigenvalues (truncated or interpolated from M = c*N).
    """
    # Use a power-of-2 N for the synthetic iid matrix; M = c*N
    N_ref = max(int(n_samples), 1024)
    M_ref = max(int(round(c * N_ref)), 1)
    rng = np.random.default_rng(seed)
    G = rng.standard_normal(size=(M_ref, N_ref)) / math.sqrt(N_ref)
    s = np.linalg.svd(G, compute_uv=False)
    eig = np.sort((s ** 2).astype(np.float64))  # ascending; len = min(M_ref, N_ref)
    if len(eig) == n_samples:
        return eig
    # Resample to exactly n_samples points by linear interpolation in quantile space
    q_src = np.linspace(0, 1, len(eig))
    q_tgt = np.linspace(0, 1, n_samples)
    return np.interp(q_tgt, q_src, eig)


# ---------------------------------------------------------------------------
# Scores
# ---------------------------------------------------------------------------

def mmd_rbf(x: np.ndarray, y: np.ndarray, sigma_kernel: float = None) -> float:
    """MMD^2 between samples x and y under an RBF (Gaussian) kernel.

    Sigma chosen by median heuristic on pooled (x cup y) pairwise distances
    if not provided. Returns sqrt(max(MMD^2, 0)) for stability.
    """
    x = np.asarray(x, dtype=np.float64).flatten()
    y = np.asarray(y, dtype=np.float64).flatten()
    n, m = len(x), len(y)
    if sigma_kernel is None:
        pooled = np.concatenate([x, y])
        # Subsample for median heuristic to avoid O(L^2) where L = n+m can be 2048
        L = len(pooled)
        if L > 512:
            idx = np.random.default_rng(0).choice(L, size=512, replace=False)
            sub = pooled[idx]
        else:
            sub = pooled
        # pairwise distance matrix on subsample
        diffs = sub[:, None] - sub[None, :]
        d2 = diffs ** 2
        # median of upper triangle (excluding zeros on diag)
        tri = d2[np.triu_indices_from(d2, k=1)]
        med = np.median(tri[tri > 0]) if np.any(tri > 0) else 1.0
        sigma_kernel = math.sqrt(max(med, 1e-12) / 2.0)

    sigma2 = 2.0 * sigma_kernel ** 2
    if sigma2 <= 0:
        sigma2 = 1e-12

    # Use batched computation for memory if n is large; n=1024 -> 1MB float64 -> fine
    # k(x_i, x_j) = exp(-(x_i - x_j)^2 / sigma2)
    def gram(a, b):
        d2 = (a[:, None] - b[None, :]) ** 2
        return np.exp(-d2 / sigma2)

    Kxx = gram(x, x)
    Kyy = gram(y, y)
    Kxy = gram(x, y)

    mmd2 = Kxx.mean() + Kyy.mean() - 2.0 * Kxy.mean()
    return float(math.sqrt(max(mmd2, 0.0)))


def sliced_wasserstein_1d(x: np.ndarray, y: np.ndarray) -> float:
    """1-Wasserstein distance between 1D samples x and y.

    Exact closed form: W1 = (1/n) sum_i |x_(i) - y_(i)| after sorting both.
    Resamples y by linear interpolation if len(x) != len(y).
    """
    xs = np.sort(np.asarray(x, dtype=np.float64).flatten())
    ys = np.sort(np.asarray(y, dtype=np.float64).flatten())
    n = len(xs)
    m = len(ys)
    if n == 0 or m == 0:
        return 0.0
    if n != m:
        # Interpolate ys onto xs quantile grid
        q = np.linspace(0, 1, n)
        q_y = np.linspace(0, 1, m)
        ys_resampled = np.interp(q, q_y, ys)
    else:
        ys_resampled = ys
    return float(np.mean(np.abs(xs - ys_resampled)))


def empirical_truth_from_amp_rel(amp_rel: float, fail_thresh: float = 0.10) -> str:
    return "AMP_OK" if amp_rel < fail_thresh else "VAMP_REQUIRED"


def best_routing_accuracy(scores: list[float], labels: list[str]) -> float:
    """Pick the tau that maximizes routing accuracy (route_from_score < tau -> AMP_OK).

    Returns (best_accuracy, best_tau).
    """
    if not scores:
        return 0.0
    candidates = sorted(scores) + [min(scores) - 1.0, max(scores) + 1.0]
    best = 0
    for tau in candidates:
        correct = sum(1 for s, y in zip(scores, labels)
                      if (s <= tau and y == "AMP_OK") or (s > tau and y == "VAMP_REQUIRED"))
        if correct > best:
            best = correct
    return float(best) / len(scores)


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

def compute_verdict(summary: dict) -> tuple[str, str]:
    cb_results = summary.get("codebook_results") or []
    if len(cb_results) < len(CODEBOOKS):
        return ("MMD_VS_MPKS_PRETEST_INCONCLUSIVE",
                f"Only {len(cb_results)} codebooks; need {len(CODEBOOKS)}.")

    # Extract per-codebook means
    ks_vals = [r["ks_mean"] for r in cb_results]
    mmd_vals = [r["mmd_mean"] for r in cb_results]
    w1_vals = [r["w1_mean"] for r in cb_results]
    amp_errs = [r["amp_rel_err_mean"] for r in cb_results]
    emp_labels = [r["empirical_label"] for r in cb_results]

    # Spearman correlation with AMP error
    def safe_rho(scores, errs):
        if any(not math.isfinite(s) for s in scores + errs):
            return float("nan")
        r = spearmanr(errs, scores)
        return float(r.statistic) if hasattr(r, "statistic") else float(r[0])

    rho_ks = safe_rho(ks_vals, amp_errs)
    rho_mmd = safe_rho(mmd_vals, amp_errs)
    rho_w1 = safe_rho(w1_vals, amp_errs)

    # Best-threshold routing accuracy for each score (5 codebooks)
    acc_ks = best_routing_accuracy(ks_vals, emp_labels)
    acc_mmd = best_routing_accuracy(mmd_vals, emp_labels)
    acc_w1 = best_routing_accuracy(w1_vals, emp_labels)

    summary["rho_ks"] = rho_ks
    summary["rho_mmd"] = rho_mmd
    summary["rho_w1"] = rho_w1
    summary["acc_ks"] = acc_ks
    summary["acc_mmd"] = acc_mmd
    summary["acc_w1"] = acc_w1
    summary["ks_vals"] = ks_vals
    summary["mmd_vals"] = mmd_vals
    summary["w1_vals"] = w1_vals
    summary["amp_errs"] = amp_errs

    # HARD PASS: rho_MMD >= 0.75 OR rho_W1 >= 0.75 (strictly > rho_KS=0.70 by 5%)
    # AND the corresponding routing accuracy at natural threshold >= 4/5 (MP-KS baseline).
    pass_mmd = rho_mmd >= 0.75 and acc_mmd >= 0.80
    pass_w1 = rho_w1 >= 0.75 and acc_w1 >= 0.80

    # HARD FAIL: both alternatives <= 0.70 AND their routing accuracies <= MP-KS's.
    fail_alt = (rho_mmd <= 0.70 and rho_w1 <= 0.70
                and acc_mmd <= acc_ks and acc_w1 <= acc_ks)

    if pass_mmd or pass_w1:
        winner = "MMD" if pass_mmd else "Wasserstein"
        winner_rho = rho_mmd if pass_mmd else rho_w1
        winner_acc = acc_mmd if pass_mmd else acc_w1
        return ("MMD_VS_MPKS_PRETEST_PASS",
                f"{winner} strictly out-performs MP-KS for Cap 12 pre-test: "
                f"rho_{winner}={winner_rho:.3f} >= 0.75 (vs MP-KS rho={rho_ks:.3f}); "
                f"routing accuracy {winner_acc:.2f} >= 0.80 baseline. "
                f"Strategy may swap or augment Cap 12 score in next revision. "
                f"Full scores: rho_KS={rho_ks:.3f} rho_MMD={rho_mmd:.3f} "
                f"rho_W1={rho_w1:.3f}; accs KS={acc_ks:.2f} MMD={acc_mmd:.2f} "
                f"W1={acc_w1:.2f}.")

    if fail_alt:
        return ("MMD_VS_MPKS_PRETEST_KILLED",
                f"MMD and Wasserstein add NOTHING over MP-KS: "
                f"rho_MMD={rho_mmd:.3f} rho_W1={rho_w1:.3f} both <= 0.70 "
                f"(vs MP-KS rho={rho_ks:.3f}); their routing accuracies "
                f"(MMD={acc_mmd:.2f}, W1={acc_w1:.2f}) <= MP-KS ({acc_ks:.2f}). "
                f"MP-KS is the best pre-test score from this family; Cap 12 "
                f"✅ claim is hardened by this falsification of alternatives.")

    # MIDDLE BAND
    return ("MMD_VS_MPKS_PRETEST_INCONCLUSIVE",
            f"Marginal: rho_KS={rho_ks:.3f} rho_MMD={rho_mmd:.3f} "
            f"rho_W1={rho_w1:.3f} (PASS>=0.75); accs KS={acc_ks:.2f} "
            f"MMD={acc_mmd:.2f} W1={acc_w1:.2f}. None strictly better by 5%; "
            f"none cleanly worse. Cap 12 stays at MP-KS.")


# ---------------------------------------------------------------------------
# Formula self-tests
# ---------------------------------------------------------------------------

def self_test() -> None:
    # Cell 1: sample_mp_reference returns samples in MP support
    samples = sample_mp_reference(c=1.0, n_samples=500, seed=0)
    assert samples.min() >= 0.0 and samples.max() <= 4.0 + 0.05, \
        f"MP samples out of support: [{samples.min()}, {samples.max()}]"
    # Mean should be near 1.0 (Marcenko-Pastur c=1 has mean = 1)
    assert 0.8 < samples.mean() < 1.2, f"MP samples mean {samples.mean()} far from 1"

    # Cell 2: mmd_rbf identity (same distribution should give small MMD)
    rng = np.random.default_rng(42)
    x1 = rng.standard_normal(200)
    x2 = rng.standard_normal(200)
    mmd_self = mmd_rbf(x1, x2)
    assert mmd_self < 0.1, f"MMD of two N(0,1) samples should be small, got {mmd_self}"

    # Cell 3: mmd_rbf on distinct distributions -> larger
    y = rng.standard_normal(200) + 3.0  # shifted
    mmd_diff = mmd_rbf(x1, y)
    assert mmd_diff > mmd_self, f"MMD(N(0,1), N(3,1)) should exceed MMD(N(0,1), N(0,1))"

    # Cell 4: sliced_wasserstein_1d identity
    w1_self = sliced_wasserstein_1d(x1, x2)
    assert w1_self < 0.5, f"W1 of two N(0,1) samples should be small, got {w1_self}"

    # Cell 5: sliced_wasserstein_1d shift -> equals shift magnitude
    a = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    b = a + 2.0
    w1 = sliced_wasserstein_1d(a, b)
    assert abs(w1 - 2.0) < 1e-9, f"W1 shift expected 2.0 got {w1}"

    # Cell 6: empirical_truth_from_amp_rel boundary
    assert empirical_truth_from_amp_rel(0.05) == "AMP_OK"
    assert empirical_truth_from_amp_rel(0.10) == "VAMP_REQUIRED"

    # Cell 7: best_routing_accuracy on perfectly-separable scores
    scores = [0.01, 0.02, 0.50, 0.60, 0.70]
    labels = ["AMP_OK", "AMP_OK", "VAMP_REQUIRED", "VAMP_REQUIRED", "VAMP_REQUIRED"]
    acc = best_routing_accuracy(scores, labels)
    assert abs(acc - 1.0) < 1e-9, f"perfect separation expected 1.0 got {acc}"

    # Cell 8: best_routing_accuracy on inseparable scores
    scores_bad = [0.50, 0.10, 0.30, 0.05, 0.40]
    labels_bad = ["AMP_OK", "VAMP_REQUIRED", "AMP_OK", "VAMP_REQUIRED", "AMP_OK"]
    acc_bad = best_routing_accuracy(scores_bad, labels_bad)
    assert acc_bad < 1.0, f"inseparable expected < 1.0 got {acc_bad}"

    # Cell 9: PASS verdict (MMD better than MP-KS)
    cb_pass = []
    for cb_name, ks, mmd, w1, ae, lbl in [
        ("iid_gauss", 0.02, 0.01, 0.01, 0.02, "AMP_OK"),
        ("srht",      0.59, 0.10, 0.05, 0.04, "AMP_OK"),
        ("hadamard",  0.59, 0.30, 0.15, 0.30, "VAMP_REQUIRED"),
        ("rm_1_m",    0.34, 0.40, 0.20, 0.40, "VAMP_REQUIRED"),
        ("kerdock",   0.70, 0.55, 0.35, 0.45, "VAMP_REQUIRED"),
    ]:
        cb_pass.append({"name": cb_name, "ks_mean": ks, "mmd_mean": mmd,
                        "w1_mean": w1, "amp_rel_err_mean": ae,
                        "empirical_label": lbl})
    # MMD scores monotone with AMP error; routing perfectly separable
    summary = {"codebook_results": cb_pass}
    v, msg = compute_verdict(summary)
    # MMD: scores in order of amp_errs (0.02, 0.04, 0.30, 0.40, 0.45);
    # MMD vals (0.01, 0.10, 0.30, 0.40, 0.55) are exactly co-ordered -> rho=1.0.
    # acc_mmd: scores sorted (0.01,0.10,0.30,0.40,0.55) with labels
    # (AMP_OK,AMP_OK,VAMP,VAMP,VAMP) -> perfectly separable -> acc=1.0.
    assert v == "MMD_VS_MPKS_PRETEST_PASS", f"expected PASS got {v}: {msg}"

    # Cell 10: HARD FAIL (alternatives no better)
    cb_fail = []
    for cb_name, ks, mmd, w1, ae, lbl in [
        ("iid_gauss", 0.02, 0.50, 0.50, 0.02, "AMP_OK"),
        ("srht",      0.59, 0.40, 0.45, 0.04, "AMP_OK"),
        ("hadamard",  0.59, 0.30, 0.30, 0.30, "VAMP_REQUIRED"),
        ("rm_1_m",    0.34, 0.20, 0.20, 0.40, "VAMP_REQUIRED"),
        ("kerdock",   0.70, 0.10, 0.10, 0.45, "VAMP_REQUIRED"),
    ]:
        cb_fail.append({"name": cb_name, "ks_mean": ks, "mmd_mean": mmd,
                        "w1_mean": w1, "amp_rel_err_mean": ae,
                        "empirical_label": lbl})
    # MMD and W1 are anti-monotone with AMP error -> rho negative.
    v, msg = compute_verdict({"codebook_results": cb_fail})
    assert v == "MMD_VS_MPKS_PRETEST_KILLED", f"expected KILLED got {v}: {msg}"

    # Cell 11: MIDDLE BAND -- amp ranks 1,2,3,4,5; MMD ranks 2,3,4,1,5 (rho=0.4)
    # W1 ranks 1,2,5,3,4 (rho=0.7); neither above 0.75 PASS, both above
    # rho_ks (which should be low here because srht has high ks but low amp_err).
    cb_mid = []
    for cb_name, ks, mmd, w1, ae, lbl in [
        ("iid_gauss", 0.02, 0.10, 0.05, 0.02, "AMP_OK"),
        ("srht",      0.59, 0.15, 0.10, 0.04, "AMP_OK"),
        ("hadamard",  0.59, 0.20, 0.50, 0.30, "VAMP_REQUIRED"),
        ("rm_1_m",    0.34, 0.05, 0.20, 0.40, "VAMP_REQUIRED"),
        ("kerdock",   0.70, 0.25, 0.30, 0.45, "VAMP_REQUIRED"),
    ]:
        cb_mid.append({"name": cb_name, "ks_mean": ks, "mmd_mean": mmd,
                       "w1_mean": w1, "amp_rel_err_mean": ae,
                       "empirical_label": lbl})
    # MMD vals [0.10, 0.15, 0.20, 0.05, 0.25] ranks [2,3,4,1,5]; amp ranks [1,2,3,4,5]
    # -> spearman rho < 0.75 (PASS bound); also routing acc for MMD: sort [0.05,0.10,
    # 0.15,0.20,0.25] with labels [VAMP,AMP_OK,AMP_OK,VAMP,VAMP] - not perfectly
    # separable (kerdock and rm intermix) -> acc < 0.80.
    v, _ = compute_verdict({"codebook_results": cb_mid})
    assert v == "MMD_VS_MPKS_PRETEST_INCONCLUSIVE", \
        f"expected INCONCLUSIVE got {v}"

    # Cell 12: missing codebooks
    v, _ = compute_verdict({"codebook_results": cb_pass[:3]})
    assert v == "MMD_VS_MPKS_PRETEST_INCONCLUSIVE"

    print("mmd_vs_mpks_pretest self-test passed (12/12 cases)", flush=True)


# ---------------------------------------------------------------------------
# Per-codebook measurement
# ---------------------------------------------------------------------------

def measure_codebook(name: str, builder, expected_label: str,
                     N: int, M: int, n_seeds: int, sigma_sq: float,
                     signal_var: float, n_iter: int,
                     mp_ref: np.ndarray) -> dict:
    alpha_ratio = M / N
    amp_se_pred = amp_se_scalar(alpha_ratio, sigma_sq, signal_var)

    ks_vals, mmd_vals, w1_vals, amp_rels = [], [], [], []
    for seed in range(n_seeds):
        seed_val = seed * 1000 + 17
        W = builder(N, M, seed_val)
        M_actual, N_actual = W.shape
        U, s, Vt = np.linalg.svd(W, full_matrices=False)
        eig = (s ** 2).astype(np.float64)

        ks_val, _, _ = mp_ks_stat(eig, M_actual, N_actual)
        mmd_val = mmd_rbf(eig, mp_ref)
        w1_val = sliced_wasserstein_1d(eig, mp_ref)

        rng_sig = np.random.default_rng(seed_val + 91)
        x_true = rng_sig.standard_normal(N_actual).astype(np.float64) * math.sqrt(signal_var)
        noise = rng_sig.standard_normal(M_actual).astype(np.float64) * math.sqrt(sigma_sq)
        y = (W.astype(np.float64) @ x_true) + noise
        amp_emp = run_amp(W, y, x_true, signal_var, sigma_sq, n_iter)
        amp_rel = abs(amp_emp - amp_se_pred) / max(amp_emp, amp_se_pred, 1e-12)

        ks_vals.append(ks_val)
        mmd_vals.append(mmd_val)
        w1_vals.append(w1_val)
        amp_rels.append(amp_rel)

        print(f"    {name:10s} seed={seed} ks={ks_val:.4f} mmd={mmd_val:.4f} "
              f"w1={w1_val:.4f} amp_rel={amp_rel:.3f}", flush=True)

    ks_mean = float(np.mean(ks_vals))
    mmd_mean = float(np.mean(mmd_vals))
    w1_mean = float(np.mean(w1_vals))
    amp_rel_mean = float(np.mean(amp_rels))
    empirical_label = empirical_truth_from_amp_rel(amp_rel_mean)
    return {
        "name": name,
        "expected_label": expected_label,
        "ks_mean": ks_mean,
        "mmd_mean": mmd_mean,
        "w1_mean": w1_mean,
        "amp_rel_err_mean": amp_rel_mean,
        "empirical_label": empirical_label,
        "per_seed_ks": ks_vals,
        "per_seed_mmd": mmd_vals,
        "per_seed_w1": w1_vals,
        "per_seed_amp_rel": amp_rels,
    }


def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    if smoke:
        config = {
            "mode": "smoke",
            "N": 64,
            "M_over_N": 1.0,
            "n_seeds": 1,
            "sigma_noise": 0.1,
            "signal_var": 1.0,
            "n_iter": 50,
            "n_ref_samples": 256,
            "codebooks": ["iid_gauss", "srht"],
        }
    else:
        config = {
            "mode": "full",
            "N": 1024,
            "M_over_N": 1.0,
            "n_seeds": 5,
            "sigma_noise": 0.1,
            "signal_var": 1.0,
            "n_iter": 300,
            "n_ref_samples": 1024,  # match N
            "codebooks": [nm for nm, _b, _l in CODEBOOKS],
        }

    N = config["N"]
    M = max(1, int(config["M_over_N"] * N))
    sigma_sq = config["sigma_noise"] ** 2
    signal_var = config["signal_var"]
    n_iter = config["n_iter"]
    n_seeds = config["n_seeds"]
    n_ref = config["n_ref_samples"]

    alpha_ratio = M / N

    print(f"[setup] N={N} M={M} M/N={alpha_ratio:.3f} sigma_sq={sigma_sq} "
          f"signal_var={signal_var} n_iter={n_iter} n_seeds={n_seeds} "
          f"n_ref={n_ref} codebooks={config['codebooks']}", flush=True)

    # MP reference samples (fixed across all codebooks)
    print("\n[stage 1/2] sampling MP reference distribution", flush=True)
    mp_ref = sample_mp_reference(c=alpha_ratio, n_samples=n_ref, seed=314159)
    print(f"  MP reference: n={len(mp_ref)} mean={mp_ref.mean():.4f} "
          f"min={mp_ref.min():.4f} max={mp_ref.max():.4f}", flush=True)

    builder_map = {nm: (b, lab) for nm, b, lab in CODEBOOKS}

    print(f"\n[stage 2/2] measuring 3 scores x {len(config['codebooks'])} codebooks "
          f"x {n_seeds} seeds", flush=True)
    codebook_results = []
    for nm in config["codebooks"]:
        builder, expected = builder_map[nm]
        print(f"\n  [codebook] {nm} (expected: {expected})", flush=True)
        result = measure_codebook(nm, builder, expected, N, M, n_seeds,
                                  sigma_sq, signal_var, n_iter, mp_ref)
        codebook_results.append(result)
        print(f"    AGG {nm}: ks={result['ks_mean']:.4f} mmd={result['mmd_mean']:.4f} "
              f"w1={result['w1_mean']:.4f} amp_rel={result['amp_rel_err_mean']:.4f} "
              f"empirical={result['empirical_label']}", flush=True)

    summary = {"codebook_results": codebook_results, "config": config}
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
    out_dir = get_output_dir("wave14_mmd_vs_mpks_pretest_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["codebook_results"]) >= 1, "smoke FAIL: no codebooks"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_mmd_vs_mpks_pretest_v1")
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
