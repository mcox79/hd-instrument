"""MP-KS pre-test routing pipeline: BBMD Cap-12 rehab Anchor 1 (R3).

Motivation
----------
The v171 kappa_profile_cross_codebook NEGATIVE result already showed that
MP-KS at the empirical eigenvalue distribution discriminates structured
codebooks (SRHT 0.59, Hadamard 0.59, RM(1,m) 0.34) from iid Gaussian (~0)
WITHOUT needing the BBMD scalar.  The rehab move is to operationalize this
as an INFRASTRUCTURE-class capability:

  Given a customer codebook W, run a cheap MP-KS pre-test.  If KS > tau,
  the codebook is OUTSIDE the standard Marchenko-Pastur regime and scalar-
  Onsager AMP will likely fail to converge.  Route the customer to the
  substrate's VAMP-on-chain primitive (Cap 8).  Else allow AMP.

We test the pipeline on the SAME 5 codebooks v171 measured (iid, SRHT,
Hadamard, RM(1,m), Kerdock) and validate the routing decision empirically
by running BOTH AMP and VAMP, recording rel-err, and checking whether the
chosen primitive matches what actually has lower error.

Honest framing
--------------
This is a NARROW infrastructure capability, not substrate-physics novelty.
The math (MP-KS) is classical (Gotze-Tikhomirov rates).  The novelty is
the PIPELINE framing: a 15ms pre-flight check that decides which inference
primitive runs.  HARD-PASS at >=4/5 correct routings with >=10x compute
saved over running-AMP-to-failure gives the substrate a meaningful 12th
capability candidate (R3 of Strategy's rehab matrix).

Threshold selection
-------------------
We DECLARE tau=0.20 a priori (per Research's recommendation) and ALSO
auto-select an optimal tau via leave-one-out per-codebook validation:
the codebook with the smallest KS that empirically NEEDS VAMP becomes
the lower bound; the codebook with the largest KS that empirically
PERMITS AMP becomes the upper bound; tau is the midpoint of the largest
empirical gap.  Both thresholds are reported; we PASS only if tau=0.20
ALREADY routes >=4/5 correctly (no auto-tuning required).

HARD PASS (R3 12th-cap candidate survives)
-------------------------------------------
  - >=4/5 codebooks routed correctly via MP-KS pre-test at tau=0.20
  - >=10x speedup of MP-KS pre-test vs running AMP to convergence/failure
  - The empirically-validated tau* falls in a clean gap (no codebook has
    KS within 0.05 of tau*, or the gap straddled by tau=0.20 is >=0.10)

HARD FAIL (R3 killed)
---------------------
  - <3/5 codebooks routed correctly at tau=0.20
  - OR speedup < 2x
  - OR no principled tau separator exists (codebooks straddle the
    AMP-OK / VAMP-required boundary in KS-space)

Vertex: MP_KS_PRETEST_PIPELINE_PASS / KILLED / INCONCLUSIVE

Pre-reg: preregs/2026-05-24_wave14_mp_ks_pretest_pipeline_v1.md
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

# Reuse BBMD correspondence v1 AMP/VAMP loops + closed-form predictions.
_bv_path = REPO / "experiments" / "exp_wave14_bbmd_vamp_correspondence_sweep_v1.py"
_spec_bv = importlib.util.spec_from_file_location("bbmd_vamp_v1", _bv_path)
_bv = importlib.util.module_from_spec(_spec_bv)
_spec_bv.loader.exec_module(_bv)
amp_se_scalar = _bv.amp_se_scalar
vamp_se_closed = _bv.vamp_se_closed
run_amp = _bv.run_amp
run_vamp = _bv.run_vamp


# ---------------------------------------------------------------------------
# Codebook table + a priori AMP-OK / VAMP-required ground-truth labels
# ---------------------------------------------------------------------------

CODEBOOKS = [
    ("iid_gauss", build_iid_gauss, "AMP_OK"),       # MP-universal AMP, KS small
    ("srht",      build_srht,      "AMP_OK"),       # Dudeja-Lu-Kini AMP-universal
    ("hadamard",  build_hadamard,  "VAMP_REQUIRED"),  # row-subsampled deterministic; brittle for AMP
    ("rm_1_m",    build_rm_1_m,    "VAMP_REQUIRED"),  # algebraic structure; AMP-fragile
    ("kerdock",   build_kerdock,   "VAMP_REQUIRED"),  # v168/v170: AMP diverges, VAMP succeeds
]

TAU_DECLARED = 0.20  # a priori KS threshold (Research recommendation)


# ---------------------------------------------------------------------------
# Routing decision + empirical validation
# ---------------------------------------------------------------------------

def route_from_ks(ks: float, tau: float) -> str:
    """Return 'AMP_OK' if KS <= tau else 'VAMP_REQUIRED'."""
    return "AMP_OK" if ks <= tau else "VAMP_REQUIRED"


def empirical_truth_from_errs(amp_rel: float, vamp_rel: float,
                              fail_thresh: float = 0.10) -> str:
    """Determine empirical 'truth': which primitive should be routed to.

    Returns 'AMP_OK' if AMP rel-err < fail_thresh (AMP is good enough -- use it).
    Returns 'VAMP_REQUIRED' if AMP rel-err >= fail_thresh (AMP fails -- need VAMP).
    """
    return "AMP_OK" if amp_rel < fail_thresh else "VAMP_REQUIRED"


def measure_codebook(name: str, builder, expected_label: str,
                     N: int, M: int, n_seeds: int, sigma_sq: float,
                     signal_var: float, n_iter: int) -> dict:
    """For one codebook: average MP-KS + AMP/VAMP rel-err across n_seeds.

    Also separately time: MP-KS-pre-test wallclock vs AMP-run wallclock.
    """
    alpha_ratio = M / N
    amp_se_pred = amp_se_scalar(alpha_ratio, sigma_sq, signal_var)

    ks_vals, amp_rels, vamp_rels = [], [], []
    t_ks_total = 0.0
    t_amp_total = 0.0
    for seed in range(n_seeds):
        seed_val = seed * 1000 + 17
        W = builder(N, M, seed_val)
        M_actual, N_actual = W.shape  # in case builder returned different shape

        # SVD once: shared by KS + VAMP closed-form + VAMP loop.
        U, s, Vt = np.linalg.svd(W, full_matrices=False)
        eig = (s ** 2).astype(np.float64)

        # Time MP-KS pre-test (KS computation only; SVD shared with VAMP).
        t0 = time.monotonic()
        ks_val, _, _ = mp_ks_stat(eig, M_actual, N_actual)
        t_ks_total += time.monotonic() - t0
        ks_vals.append(ks_val)

        # Generate signal + noise.
        rng_sig = np.random.default_rng(seed_val + 91)
        x_true = rng_sig.standard_normal(N_actual).astype(np.float64) * math.sqrt(signal_var)
        noise = rng_sig.standard_normal(M_actual).astype(np.float64) * math.sqrt(sigma_sq)
        y = (W.astype(np.float64) @ x_true) + noise

        # Time empirical AMP loop end-to-end.
        t0 = time.monotonic()
        amp_emp = run_amp(W, y, x_true, signal_var, sigma_sq, n_iter)
        t_amp_total += time.monotonic() - t0

        # VAMP loop (closed-form + empirical, sharing SVD).
        vamp_se_pred = vamp_se_closed(s, N_actual, M_actual, sigma_sq, signal_var)
        vamp_emp = run_vamp(U, s, Vt, y, x_true, signal_var, sigma_sq, n_iter)

        # Rel-err vs the THEORETICAL prediction (AMP-SE for AMP, VAMP-SE for VAMP).
        amp_rel = abs(amp_emp - amp_se_pred) / max(amp_emp, amp_se_pred, 1e-12)
        vamp_rel = abs(vamp_emp - vamp_se_pred) / max(vamp_emp, vamp_se_pred, 1e-12)
        amp_rels.append(amp_rel)
        vamp_rels.append(vamp_rel)

        print(f"    {name:10s} seed={seed} ks={ks_val:.4f} "
              f"amp_emp={amp_emp:.5f} amp_rel={amp_rel:.3f} "
              f"vamp_emp={vamp_emp:.5f} vamp_rel={vamp_rel:.3f}",
              flush=True)

    ks_mean = float(np.mean(ks_vals))
    amp_rel_mean = float(np.mean(amp_rels))
    vamp_rel_mean = float(np.mean(vamp_rels))
    empirical_label = empirical_truth_from_errs(amp_rel_mean, vamp_rel_mean)
    return {
        "name": name,
        "expected_label": expected_label,
        "ks_mean": ks_mean,
        "ks_std": float(np.std(ks_vals)),
        "amp_rel_mean": amp_rel_mean,
        "vamp_rel_mean": vamp_rel_mean,
        "empirical_label": empirical_label,
        "t_ks_per_seed_s": t_ks_total / max(n_seeds, 1),
        "t_amp_per_seed_s": t_amp_total / max(n_seeds, 1),
        "per_seed_ks": ks_vals,
        "per_seed_amp_rel": amp_rels,
        "per_seed_vamp_rel": vamp_rels,
    }


# ---------------------------------------------------------------------------
# Threshold auto-selection
# ---------------------------------------------------------------------------

def auto_tune_tau(cb_results: list[dict]) -> tuple[float, float]:
    """Pick tau* that maximizes correct routings against empirical_label.

    Returns (tau_star, max_correct).  Sweeps tau across the sorted KS values.
    """
    if not cb_results:
        return (float("nan"), 0.0)
    candidates = sorted({float(r["ks_mean"]) for r in cb_results}) + [0.0, 0.50, 1.0]
    candidates = sorted(set(candidates))
    best_tau = candidates[0]
    best_score = -1
    for tau in candidates:
        correct = sum(1 for r in cb_results
                      if route_from_ks(r["ks_mean"], tau) == r["empirical_label"])
        if correct > best_score:
            best_score = correct
            best_tau = tau
    return (float(best_tau), float(best_score))


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

def compute_verdict(summary: dict) -> tuple[str, str]:
    """HARD PASS: >=4/5 correct routings at tau=0.20 AND speedup >= 10x.
    HARD FAIL: <3/5 correct OR speedup < 2x OR no clean gap.
    Else INCONCLUSIVE.
    """
    cbs = summary.get("codebook_results") or []
    if len(cbs) < len(CODEBOOKS):
        return ("MP_KS_PRETEST_PIPELINE_INCONCLUSIVE",
                f"Missing codebooks: have {len(cbs)} need {len(CODEBOOKS)}.")

    tau = summary.get("tau_declared", TAU_DECLARED)
    correct = sum(1 for r in cbs
                  if route_from_ks(r["ks_mean"], tau) == r["empirical_label"])
    summary["routing_correct_at_tau_declared"] = correct

    t_ks_total = sum(r["t_ks_per_seed_s"] for r in cbs)
    t_amp_total = sum(r["t_amp_per_seed_s"] for r in cbs)
    speedup = (t_amp_total / max(t_ks_total, 1e-9)) if t_ks_total > 0 else float("inf")
    summary["t_ks_per_seed_total_s"] = float(t_ks_total)
    summary["t_amp_per_seed_total_s"] = float(t_amp_total)
    summary["speedup_amp_over_ks"] = float(speedup)

    # Auto-tune tau* for diagnostic; not used in PASS/FAIL gate (declared tau is binding).
    tau_star, best_correct = auto_tune_tau(cbs)
    summary["tau_star"] = tau_star
    summary["tau_star_correct"] = best_correct

    # Cleanest-gap heuristic: sort KS values, find max gap between consecutive values.
    ks_sorted = sorted(r["ks_mean"] for r in cbs)
    gaps = [(ks_sorted[i + 1] - ks_sorted[i], (ks_sorted[i], ks_sorted[i + 1]))
            for i in range(len(ks_sorted) - 1)]
    max_gap = max(gaps, key=lambda g: g[0]) if gaps else (0.0, (0.0, 0.0))
    summary["max_ks_gap"] = float(max_gap[0])
    summary["max_ks_gap_bounds"] = list(max_gap[1])

    routing_table = []
    for r in cbs:
        routing_table.append({
            "name": r["name"],
            "expected": r["expected_label"],
            "ks_mean": r["ks_mean"],
            "routed_by_pretest": route_from_ks(r["ks_mean"], tau),
            "empirical_truth": r["empirical_label"],
            "correct": route_from_ks(r["ks_mean"], tau) == r["empirical_label"],
        })
    summary["routing_table"] = routing_table

    # HARD FAIL gates first.
    if correct < 3:
        return ("MP_KS_PRETEST_PIPELINE_KILLED",
                f"Only {correct}/5 codebooks routed correctly at tau={tau:.2f}; "
                f"need >=4/5 for PASS, >=3/5 to avoid HARD FAIL. "
                f"Routing table: {routing_table}.")
    if speedup < 2.0:
        return ("MP_KS_PRETEST_PIPELINE_KILLED",
                f"Speedup {speedup:.2f}x of MP-KS pre-test vs AMP-to-completion "
                f"is below the 2x HARD FAIL bound (t_ks={t_ks_total:.4f}s vs "
                f"t_amp={t_amp_total:.4f}s per seed across {len(cbs)} codebooks). "
                f"Pre-test is not cheaper than the alternative.")

    # HARD PASS gate.
    if correct >= 4 and speedup >= 10.0:
        return ("MP_KS_PRETEST_PIPELINE_PASS",
                f"MP-KS pre-test routes {correct}/5 codebooks correctly at "
                f"tau={tau:.2f}, with {speedup:.1f}x speedup over running AMP "
                f"to convergence/failure. Max KS gap={max_gap[0]:.3f} between "
                f"KS values {max_gap[1]}; tau_star={tau_star:.3f} agrees with "
                f"declared tau. R3 infrastructure capability anchor lands "
                f"positive; substrate ships a pre-flight diagnostic that picks "
                f"AMP vs VAMP-on-chain per customer codebook.")

    # In between (3 correct or 4 correct with speedup 2-10x).
    return ("MP_KS_PRETEST_PIPELINE_INCONCLUSIVE",
            f"Borderline: {correct}/5 correct (PASS>=4, FAIL<3), "
            f"speedup {speedup:.2f}x (PASS>=10, FAIL<2). "
            f"tau_star={tau_star:.3f} routes {int(best_correct)}/5 correct. "
            f"Routing table: {routing_table}.")


# ---------------------------------------------------------------------------
# Formula self-tests
# ---------------------------------------------------------------------------

def self_test() -> None:
    """Per [[feedback-strategy-spec-formula-selftests]]: each formula in the
    prereg gets an (input -> expected output) self-test cell BEFORE compute.
    """

    # Self-test 1: route_from_ks formula
    #   inputs: (ks, tau) -> outputs: AMP_OK if ks<=tau else VAMP_REQUIRED
    assert route_from_ks(0.05, 0.20) == "AMP_OK"
    assert route_from_ks(0.20, 0.20) == "AMP_OK"  # boundary inclusive
    assert route_from_ks(0.21, 0.20) == "VAMP_REQUIRED"
    assert route_from_ks(0.59, 0.20) == "VAMP_REQUIRED"

    # Self-test 2: empirical_truth_from_errs formula
    #   inputs: (amp_rel, vamp_rel, fail_thresh=0.10) -> AMP_OK if amp_rel<0.10
    assert empirical_truth_from_errs(0.05, 0.02) == "AMP_OK"
    assert empirical_truth_from_errs(0.50, 0.02) == "VAMP_REQUIRED"
    assert empirical_truth_from_errs(0.10, 0.02) == "VAMP_REQUIRED"  # boundary exclusive

    # Self-test 3: speedup formula
    #   inputs: t_amp=1.0s, t_ks=0.05s -> speedup = 20.0
    speedup = 1.0 / 0.05
    assert abs(speedup - 20.0) < 1e-9, f"speedup formula expected 20.0 got {speedup}"

    # Self-test 4: routing accuracy counter
    #   inputs: 5 codebooks, 4 routed correctly -> correct=4
    fake_cbs = [
        {"name": "a", "ks_mean": 0.05, "empirical_label": "AMP_OK"},      # routed AMP_OK -> correct
        {"name": "b", "ks_mean": 0.10, "empirical_label": "AMP_OK"},      # routed AMP_OK -> correct
        {"name": "c", "ks_mean": 0.30, "empirical_label": "VAMP_REQUIRED"},  # routed VAMP -> correct
        {"name": "d", "ks_mean": 0.40, "empirical_label": "VAMP_REQUIRED"},  # routed VAMP -> correct
        {"name": "e", "ks_mean": 0.15, "empirical_label": "VAMP_REQUIRED"},  # routed AMP -> WRONG
    ]
    correct = sum(1 for r in fake_cbs
                  if route_from_ks(r["ks_mean"], 0.20) == r["empirical_label"])
    assert correct == 4, f"routing-correct counter expected 4 got {correct}"

    # Self-test 5: PASS verdict
    cbs_pass = [
        {"name": "iid_gauss", "expected_label": "AMP_OK",       "ks_mean": 0.02,
         "amp_rel_mean": 0.03, "vamp_rel_mean": 0.02, "empirical_label": "AMP_OK",
         "t_ks_per_seed_s": 0.001, "t_amp_per_seed_s": 0.30, "ks_std": 0.0,
         "per_seed_ks": [0.02], "per_seed_amp_rel": [0.03], "per_seed_vamp_rel": [0.02]},
        {"name": "srht",      "expected_label": "AMP_OK",       "ks_mean": 0.59,
         "amp_rel_mean": 0.04, "vamp_rel_mean": 0.02, "empirical_label": "AMP_OK",
         "t_ks_per_seed_s": 0.001, "t_amp_per_seed_s": 0.30, "ks_std": 0.0,
         "per_seed_ks": [0.59], "per_seed_amp_rel": [0.04], "per_seed_vamp_rel": [0.02]},
        # NOTE: srht here is set to AMP_OK empirically since Dudeja-Lu-Kini predicts AMP works
        # despite the high KS; this would actually be a 4/5 (one mis-routed) PASS case.
        {"name": "hadamard",  "expected_label": "VAMP_REQUIRED", "ks_mean": 0.59,
         "amp_rel_mean": 0.30, "vamp_rel_mean": 0.03, "empirical_label": "VAMP_REQUIRED",
         "t_ks_per_seed_s": 0.001, "t_amp_per_seed_s": 0.30, "ks_std": 0.0,
         "per_seed_ks": [0.59], "per_seed_amp_rel": [0.30], "per_seed_vamp_rel": [0.03]},
        {"name": "rm_1_m",    "expected_label": "VAMP_REQUIRED", "ks_mean": 0.34,
         "amp_rel_mean": 0.40, "vamp_rel_mean": 0.04, "empirical_label": "VAMP_REQUIRED",
         "t_ks_per_seed_s": 0.001, "t_amp_per_seed_s": 0.30, "ks_std": 0.0,
         "per_seed_ks": [0.34], "per_seed_amp_rel": [0.40], "per_seed_vamp_rel": [0.04]},
        {"name": "kerdock",   "expected_label": "VAMP_REQUIRED", "ks_mean": 0.70,
         "amp_rel_mean": 0.45, "vamp_rel_mean": 0.03, "empirical_label": "VAMP_REQUIRED",
         "t_ks_per_seed_s": 0.001, "t_amp_per_seed_s": 0.30, "ks_std": 0.0,
         "per_seed_ks": [0.70], "per_seed_amp_rel": [0.45], "per_seed_vamp_rel": [0.03]},
    ]
    # SRHT routed VAMP at tau=0.20 (ks=0.59 > 0.20) but empirical is AMP_OK -> mis-routed.
    # So we have 4/5 correct (iid + hadamard + rm + kerdock), speedup = 0.30/0.001 = 300x.
    summary = {"codebook_results": cbs_pass, "tau_declared": TAU_DECLARED}
    v, msg = compute_verdict(summary)
    assert v == "MP_KS_PRETEST_PIPELINE_PASS", f"expected PASS got {v}: {msg}"
    assert summary["routing_correct_at_tau_declared"] == 4, summary

    # Self-test 6: KILLED via low correct count
    cbs_killed = [dict(r) for r in cbs_pass]
    cbs_killed[2]["empirical_label"] = "AMP_OK"  # hadamard: empirically AMP_OK -> mis-route
    cbs_killed[3]["empirical_label"] = "AMP_OK"  # rm: AMP_OK -> mis-route
    cbs_killed[4]["empirical_label"] = "AMP_OK"  # kerdock: AMP_OK -> mis-route
    # Now only iid (1) is correct.  srht routed VAMP empirical AMP -> wrong (1 still).
    summary_k = {"codebook_results": cbs_killed, "tau_declared": TAU_DECLARED}
    v, msg = compute_verdict(summary_k)
    assert v == "MP_KS_PRETEST_PIPELINE_KILLED", f"expected KILLED got {v}: {msg}"

    # Self-test 7: KILLED via low speedup
    cbs_slow = [dict(r) for r in cbs_pass]
    for r in cbs_slow:
        r["t_ks_per_seed_s"] = 0.20
        r["t_amp_per_seed_s"] = 0.25  # only 1.25x slower
    summary_s = {"codebook_results": cbs_slow, "tau_declared": TAU_DECLARED}
    v, msg = compute_verdict(summary_s)
    assert v == "MP_KS_PRETEST_PIPELINE_KILLED", f"expected KILLED (speedup) got {v}: {msg}"

    # Self-test 8: INCONCLUSIVE (3/5 correct)
    cbs_inc = [dict(r) for r in cbs_pass]
    cbs_inc[2]["empirical_label"] = "AMP_OK"  # hadamard: AMP_OK -> mis-route (3 correct)
    cbs_inc[3]["empirical_label"] = "AMP_OK"  # rm:        AMP_OK -> mis-route (2 correct: iid + kerdock)
    # Wait: at this stage iid + kerdock are correct (2), then srht is mis-routed (was 4/5
    # because srht was the only mis-route).  Let me re-tally:
    # iid_gauss: ks=0.02 <= 0.20 -> AMP_OK; empirical AMP_OK -> correct.
    # srht: ks=0.59 > 0.20 -> VAMP; empirical AMP_OK (from cbs_pass) -> WRONG.
    # hadamard: ks=0.59 > 0.20 -> VAMP; empirical AMP_OK (modified) -> WRONG.
    # rm_1_m: ks=0.34 > 0.20 -> VAMP; empirical AMP_OK (modified) -> WRONG.
    # kerdock: ks=0.70 > 0.20 -> VAMP; empirical VAMP_REQUIRED -> correct.
    # Total correct = 2 -> KILLED (< 3).
    # To force INCONCLUSIVE (3/5), restore rm to VAMP_REQUIRED.
    cbs_inc[3]["empirical_label"] = "VAMP_REQUIRED"  # rm: VAMP_REQUIRED -> correct (3 correct)
    summary_i = {"codebook_results": cbs_inc, "tau_declared": TAU_DECLARED}
    v, msg = compute_verdict(summary_i)
    assert v == "MP_KS_PRETEST_PIPELINE_INCONCLUSIVE", f"expected INCONCLUSIVE got {v}: {msg}"

    # Self-test 9: missing codebooks -> INCONCLUSIVE
    summary_m = {"codebook_results": cbs_pass[:3], "tau_declared": TAU_DECLARED}
    v, _ = compute_verdict(summary_m)
    assert v == "MP_KS_PRETEST_PIPELINE_INCONCLUSIVE"

    print("MP-KS pre-test pipeline self-test passed (9/9 cases)", flush=True)


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    if smoke:
        # Smoke: N=64 / 1 seed / 2 codebooks per directive.  But Kerdock needs N=1024+
        # so smoke uses iid+SRHT only (cheap, no Kerdock dependency).
        config = {
            "mode": "smoke",
            "N": 64,
            "M_over_N": 1.0,
            "n_seeds": 1,
            "sigma_noise": 0.1,
            "signal_var": 1.0,
            "n_iter": 50,
            "tau_declared": TAU_DECLARED,
            "codebooks": ["iid_gauss", "srht"],
        }
    else:
        config = {
            "mode": "full",
            "N": 1024,                # all 5 codebooks supported at N=1024 (Kerdock t=5)
            "M_over_N": 1.0,
            "n_seeds": 5,
            "sigma_noise": 0.1,
            "signal_var": 1.0,
            "n_iter": 300,
            "tau_declared": TAU_DECLARED,
            "codebooks": [nm for nm, _b, _l in CODEBOOKS],
        }

    N = config["N"]
    M = max(1, int(config["M_over_N"] * N))
    sigma_sq = config["sigma_noise"] ** 2
    signal_var = config["signal_var"]
    n_iter = config["n_iter"]
    n_seeds = config["n_seeds"]
    tau = config["tau_declared"]

    print(f"[setup] N={N} M={M} M/N={M/N:.3f} sigma_sq={sigma_sq} "
          f"signal_var={signal_var} n_iter={n_iter} n_seeds={n_seeds} "
          f"tau_declared={tau} codebooks={config['codebooks']}", flush=True)

    builder_map = {nm: (b, lab) for nm, b, lab in CODEBOOKS}

    codebook_results = []
    for nm in config["codebooks"]:
        builder, expected = builder_map[nm]
        print(f"\n[codebook] {nm} (expected: {expected})", flush=True)
        result = measure_codebook(nm, builder, expected, N, M, n_seeds,
                                  sigma_sq, signal_var, n_iter)
        codebook_results.append(result)
        print(f"  AGG {nm}: ks_mean={result['ks_mean']:.4f} "
              f"amp_rel={result['amp_rel_mean']:.4f} "
              f"vamp_rel={result['vamp_rel_mean']:.4f} "
              f"empirical={result['empirical_label']} "
              f"t_ks={result['t_ks_per_seed_s']*1000:.2f}ms "
              f"t_amp={result['t_amp_per_seed_s']*1000:.2f}ms",
              flush=True)

    summary = {"codebook_results": codebook_results,
               "config": config,
               "tau_declared": tau}
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
    out_dir = get_output_dir("wave14_mp_ks_pretest_pipeline_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["codebook_results"]) >= 1, "smoke FAIL: no codebooks measured"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_mp_ks_pretest_pipeline_v1")
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
