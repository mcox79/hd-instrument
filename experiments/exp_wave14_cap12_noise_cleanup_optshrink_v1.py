"""OptShrink data-driven SVD-shrinkage codebook denoising (Cap 12 noise-cleanup).

Anchor name: wave14_cap12_noise_cleanup_optshrink_v1
Queue: remote_cpu_queue
ETA: 45-60 min CPU (5 codebooks * 5 eta * 5 seeds = 125 cells; 1 SVD per cell)

Hypothesis
----------
Applying Donoho-Gavish-Nadakuditi optimal-singular-value-hard-threshold to an
eta-bit-flip-corrupted codebook W_noisy reconstructs a denoised W_cleaned such
that:
  (a) eta_effective <= eta_input/3 across >=4/5 families at eta_input in
      {0.05, 0.10} (>=3x effective noise reduction); AND
  (b) Cap 12 routing accuracy on W_cleaned >= 4/5 at eta_input <= 0.10.
=> Portfolio Gap 1 closes; Cap 12 customer envelope extends from eta <= 0.01
   (v178 narrowed) to eta_input <= 0.10 with OptShrink preprocessing.

Math (Donoho-Gavish 2014 "Optimal hard threshold for singular values is 4/sqrt(3)")
------------------------------------------------------------------------------------
For Y = X + sigma * G with G iid N(0, 1) entries, M x N matrix with beta = M/N,
the optimal hard threshold for singular values (in the asymptotic Frobenius-loss
minimization sense) is:

  lambda*(beta) = sqrt( 2*(beta+1) + 8*beta / ((beta+1) + sqrt(beta^2 + 14*beta + 1)) )

  threshold = lambda*(beta) * sigma * sqrt(N)   (with the larger of M, N = N convention)

For square case beta=1: lambda*(1) = sqrt(8/3 * 2 + 8 * something) ... the closed-form
result is 4/sqrt(3) ~ 2.309 (per Donoho-Gavish Theorem 1).

For bit-flip noise on bipolar +/-1 codebook entries with flip probability eta:
  flip in {-1, +1} with P(-1)=eta, P(+1)=1-eta.  Noisy entry = W * flip.
  Per-entry noise Z = W * (flip - 1):
    flip - 1 in {-2, 0} with P(-2)=eta, P(0)=1-eta.
    E[Z] = -2*eta * W  (a small bias toward -W; symmetric across +/- entries so
                        the bias is mean-zero across the codebook but per-entry
                        nonzero).
    Var(Z) = 4*eta*(1-eta) * W^2 = 4*eta*(1-eta)  (since W in {+1,-1}).
  =>  sigma_noise (per entry, on the UNNORMALIZED +/-1 matrix) = 2*sqrt(eta*(1-eta))

So the OptShrink threshold on the unnormalized noisy matrix is:
  threshold = lambda*(beta) * 2*sqrt(eta*(1-eta)) * sqrt(N_larger)
where N_larger = max(M, N).

For beta = M/N = 1 (the substrate's canonical regime): threshold = (4/sqrt(3)) *
2*sqrt(eta*(1-eta)) * sqrt(N).

Algorithm
---------
  1. Build clean codebook W_clean (entries in {+/-1/sqrt(N)} after substrate
     normalization; we DENORMALIZE to +/-1 for noise application).
  2. Apply bit-flip noise: W_noisy_unorm = W_unorm * flip_mask.
  3. SVD: U, s, Vt = svd(W_noisy_unorm).
  4. Apply hard threshold: s_clean = s * (s > threshold).
  5. Reconstruct: W_cleaned_unorm = U @ diag(s_clean) @ Vt.
  6. Re-quantize to {+/-1}: W_cleaned_unorm_bipolar = sign(W_cleaned_unorm).
  7. Renormalize to substrate scale: W_cleaned = W_cleaned_unorm_bipolar / sqrt(N).
  8. Measure eta_effective = empirical sign-flip rate vs W_clean.
  9. Run MP-KS pre-test on W_noisy AND W_cleaned (substrate-normalized).
 10. Route via route_from_ks(ks_mean, tau=0.20) and compare to expected label.

Per-cell record: ks_noisy, ks_cleaned, eta_effective, routed_noisy, routed_cleaned,
                  expected_clean_label, correct_noisy, correct_cleaned.

Codebook families: iid_gauss, srht, hadamard, rm_1_m, kerdock (the 5 canonical
substrate codebooks). iid_gauss is NOT bipolar; for it we treat the noise model
as additive Gaussian (sigma = 2*sqrt(eta*(1-eta)) acts as an effective additive-
Gaussian SNR by analogy; sign-quantization is replaced with identity for
iid_gauss).

Pre-reg: preregs/2026-05-24_wave14_cap12_noise_cleanup_optshrink_v1.md

Smoke
-----
N=64, 1 seed, eta in {0.0, 0.05}, codebooks={iid_gauss, hadamard}.
Self-test: OptShrink on a clean Hadamard at eta=0 must preserve singular
values to floating-point (the threshold at eta=0 is 0, so all sigma_i > 0
survive; reconstruction is exact).
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

# Reuse cross-codebook v1 builders + MP-KS routine.
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

# Reuse noise model from envelope v1.
_env_path = REPO / "experiments" / "exp_wave14_mp_ks_noise_envelope_sweep_v1.py"
_spec_env = importlib.util.spec_from_file_location("env_v1", _env_path)
_env = importlib.util.module_from_spec(_spec_env)
_spec_env.loader.exec_module(_env)
apply_signflip_noise = _env.apply_signflip_noise
route_from_ks = _env.route_from_ks


CODEBOOKS = [
    # (name, builder, clean_expected_route, is_bipolar)
    ("iid_gauss", build_iid_gauss, "AMP_OK",        False),
    ("srht",      build_srht,      "AMP_OK",        True),
    ("hadamard",  build_hadamard,  "VAMP_REQUIRED", True),
    ("rm_1_m",    build_rm_1_m,    "VAMP_REQUIRED", True),
    ("kerdock",   build_kerdock,   "VAMP_REQUIRED", True),
]

TAU_FIXED = 0.20
ETA_GRID = (0.01, 0.02, 0.05, 0.10, 0.20)

# Hard-pass / hard-fail thresholds (per Research's pre-reg)
HARD_PASS_ETA_INPUTS = (0.05, 0.10)   # check >=3x reduction at these eta
HARD_PASS_REDUCTION_RATIO = 3.0       # eta_effective <= eta_input / 3
HARD_PASS_MIN_FAMILIES = 4            # >=4/5 families
HARD_PASS_ROUTING_MIN = 4             # >=4/5 routing accuracy on W_cleaned at eta <= 0.10

HF1_ETA = 0.05                        # at eta_input=0.05
HF1_ETA_EFF_CEILING = 0.02            # if eta_effective > 0.02 across >=4/5 families => HF1
HF1_THRESHOLD_FAMILIES = 4

HF2_RANK_COLLAPSE_FAMILIES = 1        # rank truncation drops codebook to zero at any eta>=0.05
HF2_ETA_FLOOR = 0.05

HF3_ROUTING_FLOOR = 0.50              # if mean routing fidelity < 0.50 even at eta=0.01 => HF3

MIDDLE_BAND_RATIO_LO = 2.0            # eta_effective in (eta/3, eta/2)


def optshrink_lambda_beta(beta: float) -> float:
    """Donoho-Gavish (2014) Theorem 1 universal threshold coefficient.

    For Y = X + sigma * G, M x N (M <= N convention; beta = M/N in (0, 1]),
    the optimal hard threshold is:
      lambda*(beta) = sqrt( 2*(beta+1) + 8*beta / ((beta+1) + sqrt(beta^2 + 14*beta + 1)) )

    Special case beta=1: lambda*(1) = 4/sqrt(3) ~ 2.30940.

    For beta > 1 (M > N), the formula is symmetric in beta <-> 1/beta convention;
    we always pass the smaller-dimension ratio (min(M,N)/max(M,N)).
    """
    if beta <= 0 or beta > 1:
        raise ValueError(f"beta must be in (0, 1]; got {beta} (caller must pass min/max)")
    radicand = beta ** 2 + 14 * beta + 1
    inner = 2 * (beta + 1) + 8 * beta / ((beta + 1) + math.sqrt(radicand))
    return math.sqrt(inner)


def optshrink_denoise(W_unorm_noisy: np.ndarray, sigma_noise: float
                      ) -> tuple[np.ndarray, dict]:
    """Apply Donoho-Gavish optimal hard-threshold SVD denoising.

    Args:
      W_unorm_noisy: M x N noisy matrix (entries roughly O(1); for bipolar
        codebooks, +/-1 plus flip noise; for iid_gauss, entries already O(1/sqrt(N))
        but we operate on the unnormalized scale (multiply by sqrt(N) before, divide
        after if needed -- caller's responsibility).
      sigma_noise: estimated per-entry noise std on the SAME scale as W_unorm_noisy.

    Returns:
      W_denoised_unorm: reconstructed matrix (continuous-valued).
      info: dict with {s_full, s_kept, threshold, beta_used, rank_kept,
                       lambda_beta, n_larger}.
    """
    M, N = W_unorm_noisy.shape
    # Donoho-Gavish convention: beta = smaller / larger; threshold = lambda(beta)*sigma*sqrt(larger).
    n_larger = max(M, N)
    n_smaller = min(M, N)
    beta = n_smaller / n_larger
    lam_b = optshrink_lambda_beta(beta)
    threshold = lam_b * sigma_noise * math.sqrt(n_larger)

    U, s, Vt = np.linalg.svd(W_unorm_noisy, full_matrices=False)
    keep_mask = (s > threshold)
    s_kept = s * keep_mask
    rank_kept = int(keep_mask.sum())

    W_denoised_unorm = U @ np.diag(s_kept) @ Vt

    info = {
        "s_full": s.tolist(),
        "s_kept": s_kept.tolist(),
        "threshold": float(threshold),
        "beta_used": float(beta),
        "rank_kept": rank_kept,
        "lambda_beta": float(lam_b),
        "n_larger": int(n_larger),
        "n_smaller": int(n_smaller),
    }
    return W_denoised_unorm, info


def bipolar_signnorm(W_unorm: np.ndarray, N: int) -> np.ndarray:
    """sign-quantize then renormalize to substrate scale 1/sqrt(N).

    Treat exact zeros as +1 (canonical tie-break); this only matters for the
    zero-rank-truncation corner case where every singular value got thresholded
    out (then W_denoised_unorm = 0 and sign(0) = 0, which would re-route as a
    pathological codebook). We map sign(0) -> +1 here.
    """
    signs = np.sign(W_unorm).astype(np.float32)
    signs[signs == 0] = 1.0
    return (signs / math.sqrt(N)).astype(np.float32)


def measure_eta_effective(W_clean_unorm_bipolar: np.ndarray,
                          W_cleaned_unorm_bipolar: np.ndarray) -> float:
    """Fraction of entries where sign(W_cleaned) != sign(W_clean).

    Both inputs assumed in {+/-1} (un-normalized bipolar). For iid_gauss
    (continuous-valued) callers should NOT use this; they should supply the
    bipolar reconstructions or be excluded from eta_effective.
    """
    diffs = (np.sign(W_clean_unorm_bipolar) != np.sign(W_cleaned_unorm_bipolar))
    return float(diffs.mean())


def measure_one_cell(name: str, builder, expected_route: str, is_bipolar: bool,
                     N: int, M: int, eta: float, seed: int) -> dict:
    """Run one (codebook, eta, seed) cell and return a metric row."""
    # 1. Build clean codebook at substrate scale (1/sqrt(N) entries for bipolar; 1/sqrt(N) iid Gauss).
    W_clean = builder(N, M, seed)  # shape (M, N), normalized to spectral scale 1.

    # Denormalize to unnormalized scale (so bipolar codebooks have +/-1 entries).
    sqrtN = math.sqrt(N)
    W_clean_unorm = W_clean * sqrtN  # bipolar codebooks now in {+/-1}; iid_gauss in O(1)

    # 2. Apply bit-flip noise on the unnormalized matrix.
    eta_offset = int(round(eta * 1_000_000))
    noise_seed = seed + 50_000 + eta_offset
    W_noisy_unorm = apply_signflip_noise(W_clean_unorm, eta, seed=noise_seed)

    # 3. Estimate noise std (per-entry, on the unnormalized scale).
    # For bipolar: sigma = 2 * sqrt(eta*(1-eta)).
    # For iid_gauss: the "sign-flip" model becomes Z = W*(flip-1); Var(Z) = 4*eta*(1-eta)*Var(W).
    # Var(W) for iid_gauss at unnormalized scale = sqrt(N)*standard_normal/sqrt(N) -> Var=1.
    # So sigma_noise on unnormalized iid_gauss is ALSO 2*sqrt(eta*(1-eta)). (Same formula.)
    sigma_noise = 2.0 * math.sqrt(max(eta * (1.0 - eta), 0.0))

    # 4. OptShrink denoise. Skip when eta=0 (threshold=0, identity reconstruction OK).
    W_denoised_unorm, optshrink_info = optshrink_denoise(W_noisy_unorm, sigma_noise)

    # 5. Re-quantize and renormalize to substrate scale.
    if is_bipolar:
        W_cleaned = bipolar_signnorm(W_denoised_unorm, N)
        # eta_effective on bipolar codebook
        eta_effective = measure_eta_effective(W_clean_unorm, W_cleaned * sqrtN)
    else:
        # iid_gauss: keep continuous-valued, just renormalize.
        W_cleaned = (W_denoised_unorm / sqrtN).astype(np.float32)
        # eta_effective for iid_gauss = Frobenius relative recovery error.
        # Map to a "noise level" by analogy: relative residual energy /
        # nominal noise level. We report this in the same field but flag it.
        clean_energy = float(np.sum(W_clean ** 2)) + 1e-12
        residual_energy = float(np.sum((W_cleaned - W_clean) ** 2))
        # For iid_gauss, eta_effective = relative residual amplitude.
        eta_effective = math.sqrt(residual_energy / clean_energy)

    # 6. Rank-collapse flag (when optshrink threshold kills all singular values).
    rank_collapsed = (optshrink_info["rank_kept"] == 0)

    # 7. MP-KS pre-test on BOTH noisy and cleaned codebooks (substrate-normalized).
    W_noisy = W_noisy_unorm / sqrtN
    U_n, s_n, Vt_n = np.linalg.svd(W_noisy, full_matrices=False)
    eig_n = (s_n ** 2).astype(np.float64)
    ks_noisy, _, _ = mp_ks_stat(eig_n, M, N)

    U_c, s_c, Vt_c = np.linalg.svd(W_cleaned, full_matrices=False)
    eig_c = (s_c ** 2).astype(np.float64)
    ks_cleaned, _, _ = mp_ks_stat(eig_c, M, N)

    routed_noisy = route_from_ks(float(ks_noisy), TAU_FIXED)
    routed_cleaned = route_from_ks(float(ks_cleaned), TAU_FIXED)

    correct_noisy = (routed_noisy == expected_route)
    correct_cleaned = (routed_cleaned == expected_route)

    return {
        "name": name,
        "is_bipolar": is_bipolar,
        "expected_route_clean": expected_route,
        "eta_input": float(eta),
        "seed": int(seed),
        "ks_noisy": float(ks_noisy),
        "ks_cleaned": float(ks_cleaned),
        "routed_noisy": routed_noisy,
        "routed_cleaned": routed_cleaned,
        "correct_noisy": bool(correct_noisy),
        "correct_cleaned": bool(correct_cleaned),
        "eta_effective": float(eta_effective),
        "rank_collapsed": bool(rank_collapsed),
        "optshrink_threshold": optshrink_info["threshold"],
        "optshrink_lambda_beta": optshrink_info["lambda_beta"],
        "optshrink_beta": optshrink_info["beta_used"],
        "optshrink_rank_kept": optshrink_info["rank_kept"],
        "sigma_noise_used": float(sigma_noise),
    }


# ---------------------------------------------------------------------------
# Aggregation + verdict
# ---------------------------------------------------------------------------

def aggregate_per_family_per_eta(cells: list) -> dict:
    """Bucket cells by (name, eta) and average across seeds. Returns
    {(name, eta): {ks_noisy_mean, ks_cleaned_mean, eta_effective_mean,
                    correct_cleaned_count, n_seeds, rank_collapsed_any}}.
    """
    buckets: dict = {}
    for c in cells:
        key = (c["name"], round(c["eta_input"], 4))
        b = buckets.setdefault(key, {"ks_noisy": [], "ks_cleaned": [],
                                      "eta_effective": [], "correct_cleaned": [],
                                      "correct_noisy": [],
                                      "rank_collapsed": [],
                                      "expected_route_clean": c["expected_route_clean"],
                                      "is_bipolar": c["is_bipolar"]})
        b["ks_noisy"].append(c["ks_noisy"])
        b["ks_cleaned"].append(c["ks_cleaned"])
        b["eta_effective"].append(c["eta_effective"])
        b["correct_cleaned"].append(c["correct_cleaned"])
        b["correct_noisy"].append(c["correct_noisy"])
        b["rank_collapsed"].append(c["rank_collapsed"])

    agg = {}
    for k, b in buckets.items():
        agg[k] = {
            "name": k[0],
            "eta_input": k[1],
            "ks_noisy_mean": float(np.mean(b["ks_noisy"])),
            "ks_cleaned_mean": float(np.mean(b["ks_cleaned"])),
            "eta_effective_mean": float(np.mean(b["eta_effective"])),
            "correct_cleaned_count": int(sum(b["correct_cleaned"])),
            "correct_noisy_count": int(sum(b["correct_noisy"])),
            "n_seeds": len(b["ks_noisy"]),
            "rank_collapsed_any": bool(any(b["rank_collapsed"])),
            "expected_route_clean": b["expected_route_clean"],
            "is_bipolar": b["is_bipolar"],
        }
    return agg


def compute_verdict(summary: dict) -> tuple[str, str]:
    """Per Research pre-reg HARD-FAIL and HARD-PASS thresholds.

    HF1: eta_effective > 0.02 at eta_input=0.05 across >=4/5 families => SUBSTRATE-BOUNDED
    HF2: rank truncation collapses codebook to rank=0 at any eta>=0.05 => switch families
    HF3: routing rho < 0.50 on cleaned codebook even at eta_input=0.01 => abandon

    HARD PASS: eta_effective <= eta_input/3 at eta_input in {0.05, 0.10} across
               >=4/5 families AND routing accuracy on W_cleaned >= 4/5 at eta<=0.10.

    MIDDLE: some noise reduction (eta_effective in (eta_input/3, eta_input/2)) but
            routing still degrades.
    """
    cells = summary.get("cells") or []
    expected_n_cells = len(ETA_GRID) * len(CODEBOOKS) * summary.get("n_seeds", 5)
    if len(cells) < expected_n_cells:
        return ("CAP12_NOISE_CLEANUP_OPTSHRINK_INCONCLUSIVE",
                f"Missing cells: have {len(cells)} need {expected_n_cells}.")

    agg = aggregate_per_family_per_eta(cells)
    summary["per_family_per_eta"] = {f"{k[0]}__{k[1]:.3f}": v for k, v in agg.items()}

    # HF2: rank-collapse at eta_input >= 0.05 in any family.
    collapsed = []
    for (name, eta), v in agg.items():
        if eta >= HF2_ETA_FLOOR and v["rank_collapsed_any"]:
            collapsed.append((name, eta))
    if collapsed:
        return ("CAP12_NOISE_CLEANUP_OPTSHRINK_KILLED_HF2",
                f"HF2: rank truncation COLLAPSED codebook at eta>={HF2_ETA_FLOOR}: "
                f"{collapsed}. OptShrink incompatible with bipolar regime in this band; "
                f"upstream-push to Research: try family-2 method (sparse soft-thresholding).")

    # HF3: at eta_input=0.01 (cleanest noisy band), if routing on W_cleaned <0.50 (< 2.5/5).
    eta_001_routing = []
    for (name, eta), v in agg.items():
        if abs(eta - 0.01) < 1e-9:
            eta_001_routing.append(v["correct_cleaned_count"] / max(1, v["n_seeds"]))
    if eta_001_routing:
        eta_001_mean = float(np.mean(eta_001_routing))
        if eta_001_mean < HF3_ROUTING_FLOOR:
            return ("CAP12_NOISE_CLEANUP_OPTSHRINK_KILLED_HF3",
                    f"HF3: cleaned-codebook routing fidelity at eta_input=0.01 = "
                    f"{eta_001_mean:.3f} < {HF3_ROUTING_FLOOR}. OptShrink actively "
                    f"HARMS clean substrate; abandon entirely.")

    # HF1: eta_effective > 0.02 at eta_input=0.05 across >=4/5 families.
    hf1_violators = []
    for (name, eta), v in agg.items():
        if abs(eta - HF1_ETA) < 1e-9 and v["eta_effective_mean"] > HF1_ETA_EFF_CEILING:
            hf1_violators.append(name)
    if len(hf1_violators) >= HF1_THRESHOLD_FAMILIES:
        return ("CAP12_NOISE_CLEANUP_OPTSHRINK_KILLED_HF1",
                f"HF1: eta_effective > {HF1_ETA_EFF_CEILING} at eta_input={HF1_ETA} "
                f"across {len(hf1_violators)}/5 families: {hf1_violators}. "
                f"OptShrink insufficient; Cap 12 customer envelope remains substrate-"
                f"bounded at eta_input <= 0.01. Customer must supply clean codebooks.")

    # HARD PASS check: eta_effective <= eta_input/3 across >=4/5 families at
    # eta_input in {0.05, 0.10}, AND routing on W_cleaned >=4/5 at eta<=0.10.
    hp_eta_effective_ok = True
    hp_breakdown = {}
    for eta_check in HARD_PASS_ETA_INPUTS:
        n_families_passing = 0
        family_etas_eff = {}
        for (name, eta), v in agg.items():
            if abs(eta - eta_check) < 1e-9:
                ratio_threshold = eta_check / HARD_PASS_REDUCTION_RATIO
                family_etas_eff[name] = v["eta_effective_mean"]
                if v["eta_effective_mean"] <= ratio_threshold:
                    n_families_passing += 1
        hp_breakdown[f"eta_{eta_check:.3f}"] = {
            "n_families_passing": n_families_passing,
            "family_etas_eff": family_etas_eff,
            "threshold": eta_check / HARD_PASS_REDUCTION_RATIO,
        }
        if n_families_passing < HARD_PASS_MIN_FAMILIES:
            hp_eta_effective_ok = False

    hp_routing_ok = True
    for (name, eta), v in agg.items():
        if eta <= 0.10 + 1e-9 and (v["correct_cleaned_count"] / max(1, v["n_seeds"])) < (HARD_PASS_ROUTING_MIN / 5.0):
            hp_routing_ok = False

    summary["hard_pass_breakdown"] = hp_breakdown
    summary["hp_eta_effective_ok"] = hp_eta_effective_ok
    summary["hp_routing_ok"] = hp_routing_ok

    if hp_eta_effective_ok and hp_routing_ok:
        return ("CAP12_NOISE_CLEANUP_OPTSHRINK_PASS",
                f"HARD PASS: OptShrink delivers >={HARD_PASS_REDUCTION_RATIO}x effective "
                f"noise reduction across >={HARD_PASS_MIN_FAMILIES}/5 families at "
                f"eta_input in {HARD_PASS_ETA_INPUTS}, AND cleaned-codebook routing "
                f">={HARD_PASS_ROUTING_MIN}/5 at eta_input <= 0.10. "
                f"Portfolio Gap 1 closes; Cap 12 customer envelope extends to "
                f"eta_input <= 0.10 with OptShrink preprocessing. "
                f"hp_breakdown={hp_breakdown}")

    # MIDDLE BAND
    return ("CAP12_NOISE_CLEANUP_OPTSHRINK_INCONCLUSIVE",
            f"MIDDLE BAND: OptShrink partially helpful but does not close Gap 1 fully. "
            f"hp_eta_effective_ok={hp_eta_effective_ok} hp_routing_ok={hp_routing_ok} "
            f"hp_breakdown={hp_breakdown}. "
            f"Cap 12 envelope extends to eta_input <= 0.03-0.05 with OptShrink "
            f"preprocessing (narrower than the aspirational 0.10).")


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------

def self_test() -> None:
    # Self-test 1: optshrink_lambda_beta at beta=1 returns 4/sqrt(3).
    lam_1 = optshrink_lambda_beta(1.0)
    expected = 4.0 / math.sqrt(3.0)
    assert abs(lam_1 - expected) < 1e-6, (
        f"lambda(beta=1) should be 4/sqrt(3)={expected}, got {lam_1}"
    )

    # Self-test 2: optshrink_lambda_beta is monotonic-decreasing on (0, 1].
    lams = [optshrink_lambda_beta(b) for b in (0.1, 0.2, 0.5, 0.8, 1.0)]
    # The DG paper Table 1 shows lambda(beta) starts at sqrt(4*1)=2 at beta=0+ and
    # ends at 4/sqrt(3)~2.31 at beta=1, monotonically INCREASING. Verify that.
    for i in range(1, len(lams)):
        assert lams[i] >= lams[i - 1] - 1e-9, (
            f"lambda(beta) should be non-decreasing on (0,1], got {lams}"
        )
    assert abs(lams[-1] - 4.0/math.sqrt(3.0)) < 1e-6

    # Self-test 3 (CRITICAL formula self-test per [[feedback-strategy-spec-formula-selftests]]):
    # OptShrink applied to a CLEAN Hadamard codebook at eta=0 should preserve all
    # singular values (threshold=0 since sigma_noise=0; all sigma_i > 0 retained;
    # reconstruction exact).
    N_st = 64
    M_st = 64
    W_clean = build_hadamard(N_st, M_st, seed=13)  # (M, N) normalized
    W_clean_unorm = W_clean * math.sqrt(N_st)  # in {+/-1}
    # At eta=0, sigma_noise=0, threshold=0; OptShrink should be identity-on-spectrum.
    W_denoised_unorm, info = optshrink_denoise(W_clean_unorm, sigma_noise=0.0)
    assert info["threshold"] == 0.0, f"threshold at sigma=0 should be 0, got {info['threshold']}"
    assert info["rank_kept"] == min(M_st, N_st), (
        f"all singular values should be kept at sigma=0; got rank_kept={info['rank_kept']}"
    )
    # Spectral preservation: singular values of W_denoised_unorm == those of W_clean_unorm.
    s_clean = np.linalg.svd(W_clean_unorm, compute_uv=False)
    s_denoi = np.linalg.svd(W_denoised_unorm, compute_uv=False)
    assert np.allclose(np.sort(s_clean), np.sort(s_denoi), atol=1e-4), (
        f"singular values diverged: max diff="
        f"{np.max(np.abs(np.sort(s_clean) - np.sort(s_denoi)))}"
    )
    # Frobenius preservation
    fro_err = np.linalg.norm(W_denoised_unorm - W_clean_unorm) / np.linalg.norm(W_clean_unorm)
    assert fro_err < 1e-4, f"Frobenius relative error at eta=0 should be tiny; got {fro_err}"

    # Self-test 4: apply_signflip_noise sanity at eta=0 -> identity.
    out = apply_signflip_noise(W_clean_unorm, 0.0, seed=42)
    assert np.allclose(out, W_clean_unorm)

    # Self-test 5: measure_eta_effective on identical inputs == 0.
    eta_eff = measure_eta_effective(W_clean_unorm, W_clean_unorm)
    assert eta_eff == 0.0

    # Self-test 6: bipolar_signnorm of a +/-1 matrix produces the substrate-normalized version.
    W_back = bipolar_signnorm(W_clean_unorm, N_st)
    assert np.allclose(W_back * math.sqrt(N_st), W_clean_unorm), (
        "sign+normalize roundtrip should recover W_clean for an exactly-+/-1 input"
    )

    # Self-test 7: aggregate_per_family_per_eta groups correctly.
    fake_cells = [
        {"name": "iid_gauss", "eta_input": 0.05, "seed": 0,
         "ks_noisy": 0.1, "ks_cleaned": 0.05, "eta_effective": 0.01,
         "correct_cleaned": True, "correct_noisy": False, "rank_collapsed": False,
         "expected_route_clean": "AMP_OK", "is_bipolar": False},
        {"name": "iid_gauss", "eta_input": 0.05, "seed": 1,
         "ks_noisy": 0.12, "ks_cleaned": 0.06, "eta_effective": 0.012,
         "correct_cleaned": True, "correct_noisy": False, "rank_collapsed": False,
         "expected_route_clean": "AMP_OK", "is_bipolar": False},
    ]
    agg = aggregate_per_family_per_eta(fake_cells)
    assert ("iid_gauss", 0.05) in agg
    assert agg[("iid_gauss", 0.05)]["n_seeds"] == 2
    assert abs(agg[("iid_gauss", 0.05)]["eta_effective_mean"] - 0.011) < 1e-9

    # Self-test 8: compute_verdict — HARD PASS branch.
    # Build synthetic cells: at every eta, eta_effective <= eta/3 across all 5 families,
    # routing 5/5 cleaned at every eta <= 0.10.
    cells_hp = []
    for eta in ETA_GRID:
        for nm, _b, exp_lbl, is_bip in CODEBOOKS:
            for seed in range(5):
                cells_hp.append({
                    "name": nm, "eta_input": eta, "seed": seed,
                    "ks_noisy": 0.10, "ks_cleaned": 0.05 if exp_lbl == "AMP_OK" else 0.50,
                    "eta_effective": eta / 5.0,  # well within /3 threshold
                    "correct_cleaned": True, "correct_noisy": False,
                    "rank_collapsed": False,
                    "expected_route_clean": exp_lbl, "is_bipolar": is_bip,
                })
    summary = {"cells": cells_hp, "n_seeds": 5}
    v, msg = compute_verdict(summary)
    assert v == "CAP12_NOISE_CLEANUP_OPTSHRINK_PASS", f"HP test: got {v}, msg={msg}"

    # Self-test 9: compute_verdict — HF1 branch (eta_effective stays high at eta_input=0.05).
    cells_hf1 = []
    for eta in ETA_GRID:
        for nm, _b, exp_lbl, is_bip in CODEBOOKS:
            for seed in range(5):
                # Set eta_effective at eta=0.05 to be above HF1_ETA_EFF_CEILING=0.02
                eta_eff = 0.04 if abs(eta - 0.05) < 1e-9 else eta / 5.0
                cells_hf1.append({
                    "name": nm, "eta_input": eta, "seed": seed,
                    "ks_noisy": 0.10, "ks_cleaned": 0.10,
                    "eta_effective": eta_eff,
                    "correct_cleaned": True, "correct_noisy": False,
                    "rank_collapsed": False,
                    "expected_route_clean": exp_lbl, "is_bipolar": is_bip,
                })
    summary = {"cells": cells_hf1, "n_seeds": 5}
    v, msg = compute_verdict(summary)
    assert v == "CAP12_NOISE_CLEANUP_OPTSHRINK_KILLED_HF1", f"HF1 test: got {v}, msg={msg}"

    # Self-test 10: compute_verdict — HF2 branch (rank collapse at eta_input=0.10).
    cells_hf2 = []
    for eta in ETA_GRID:
        for nm, _b, exp_lbl, is_bip in CODEBOOKS:
            for seed in range(5):
                collapse = (abs(eta - 0.10) < 1e-9 and nm == "hadamard")
                cells_hf2.append({
                    "name": nm, "eta_input": eta, "seed": seed,
                    "ks_noisy": 0.10, "ks_cleaned": 0.05,
                    "eta_effective": eta / 5.0,
                    "correct_cleaned": True, "correct_noisy": False,
                    "rank_collapsed": collapse,
                    "expected_route_clean": exp_lbl, "is_bipolar": is_bip,
                })
    summary = {"cells": cells_hf2, "n_seeds": 5}
    v, msg = compute_verdict(summary)
    assert v == "CAP12_NOISE_CLEANUP_OPTSHRINK_KILLED_HF2", f"HF2 test: got {v}, msg={msg}"

    # Self-test 11: compute_verdict — HF3 branch (routing fails at eta_input=0.01).
    cells_hf3 = []
    for eta in ETA_GRID:
        for nm, _b, exp_lbl, is_bip in CODEBOOKS:
            for seed in range(5):
                correct = False if abs(eta - 0.01) < 1e-9 else True
                cells_hf3.append({
                    "name": nm, "eta_input": eta, "seed": seed,
                    "ks_noisy": 0.10, "ks_cleaned": 0.05,
                    "eta_effective": eta / 5.0,
                    "correct_cleaned": correct, "correct_noisy": False,
                    "rank_collapsed": False,
                    "expected_route_clean": exp_lbl, "is_bipolar": is_bip,
                })
    summary = {"cells": cells_hf3, "n_seeds": 5}
    v, msg = compute_verdict(summary)
    assert v == "CAP12_NOISE_CLEANUP_OPTSHRINK_KILLED_HF3", f"HF3 test: got {v}, msg={msg}"

    # Self-test 12: compute_verdict — MIDDLE branch.
    # eta_effective at eta=0.05 = 0.018 (passes HF1 threshold of 0.02; under HARD_PASS of 0.05/3=0.0167)
    # so it should fall in middle band (not HARD PASS, not HF1).
    cells_mid = []
    for eta in ETA_GRID:
        for nm, _b, exp_lbl, is_bip in CODEBOOKS:
            for seed in range(5):
                if abs(eta - 0.05) < 1e-9:
                    eta_eff = 0.018  # > 0.05/3=0.0167 but <= HF1 ceiling 0.02
                elif abs(eta - 0.10) < 1e-9:
                    eta_eff = 0.04  # > 0.10/3=0.033 -> fails HP
                else:
                    eta_eff = eta / 5.0
                cells_mid.append({
                    "name": nm, "eta_input": eta, "seed": seed,
                    "ks_noisy": 0.10, "ks_cleaned": 0.05,
                    "eta_effective": eta_eff,
                    "correct_cleaned": True, "correct_noisy": False,
                    "rank_collapsed": False,
                    "expected_route_clean": exp_lbl, "is_bipolar": is_bip,
                })
    summary = {"cells": cells_mid, "n_seeds": 5}
    v, msg = compute_verdict(summary)
    assert v == "CAP12_NOISE_CLEANUP_OPTSHRINK_INCONCLUSIVE", f"MIDDLE test: got {v}, msg={msg}"

    # Self-test 13: missing cells -> INCONCLUSIVE.
    summary = {"cells": cells_mid[:10], "n_seeds": 5}
    v, _ = compute_verdict(summary)
    assert v == "CAP12_NOISE_CLEANUP_OPTSHRINK_INCONCLUSIVE"

    print("OptShrink self-test PASSED (13/13 cases)", flush=True)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()
    if smoke:
        config = {
            "mode": "smoke",
            "N": 64,
            "M_over_N": 1.0,
            "n_seeds": 1,
            "eta_grid": [0.0, 0.05],
            "codebooks": ["iid_gauss", "hadamard"],
        }
    else:
        config = {
            "mode": "full",
            "N": 1024,
            "M_over_N": 1.0,
            "n_seeds": 5,
            "eta_grid": list(ETA_GRID),
            "codebooks": [nm for nm, _b, _e, _i in CODEBOOKS],
        }

    N = config["N"]
    M = max(1, int(config["M_over_N"] * N))
    n_seeds = config["n_seeds"]

    print(f"[setup] N={N} M={M} n_seeds={n_seeds} eta_grid={config['eta_grid']} "
          f"codebooks={config['codebooks']}", flush=True)

    cb_map = {nm: (b, exp_lbl, is_bip) for nm, b, exp_lbl, is_bip in CODEBOOKS}

    cells = []
    for eta in config["eta_grid"]:
        print(f"\n[eta] {eta:.3f}", flush=True)
        for nm in config["codebooks"]:
            builder, exp_lbl, is_bip = cb_map[nm]
            print(f"  [codebook] {nm} (clean-route: {exp_lbl}, bipolar={is_bip})",
                  flush=True)
            for seed_idx in range(n_seeds):
                seed_val = seed_idx * 1000 + 17
                row = measure_one_cell(nm, builder, exp_lbl, is_bip,
                                       N, M, eta, seed_val)
                cells.append(row)
                print(f"    seed={seed_idx} eta_in={eta:.3f} "
                      f"ks_noisy={row['ks_noisy']:.4f} ks_clean={row['ks_cleaned']:.4f} "
                      f"eta_eff={row['eta_effective']:.4f} "
                      f"rank_kept={row['optshrink_rank_kept']} "
                      f"routed_clean={row['routed_cleaned']} "
                      f"correct={row['correct_cleaned']}", flush=True)

    summary = {
        "cells": cells,
        "n_seeds": n_seeds,
        "config": config,
        "tau_fixed": TAU_FIXED,
        "eta_grid": list(config["eta_grid"]),
    }
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
    out_dir = get_output_dir("wave14_cap12_noise_cleanup_optshrink_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["cells"]) >= 1, "smoke FAIL: no cells"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_cap12_noise_cleanup_optshrink_v1")
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
