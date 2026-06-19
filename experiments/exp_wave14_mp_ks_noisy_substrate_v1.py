"""MP-KS pre-test tau-robustness under noisy substrate: Cap 12 ✅ E1 STRESS.

Motivation
----------
Cap 12 was just promoted to ✅ at cap_map v175 (commit 7ef35a2) on the strength
of three pre-registered anchors:
  - MP_KS_PRETEST_PIPELINE_PASS (5/5 routing at tau=0.20)
  - INTERP_FAMILY_SRHT_PASS (rho=0.700 borderline)
  - MP_KS_TAU_ROBUSTNESS_PASS (>=4/5 at each tau in {0.15, 0.20, 0.25})
plus two ✅ extension gates (Hadamard + RM PASS).

The ✅ promotion exposes Cap 12 to envelope-expansion stress per
[[feedback-envelope-expansion-fail-bands]]: the customer-facing claim is that
the MP-KS pre-flight diagnostic is robust across REAL customer matrix
conditions, not just clean idealized codebooks. This E1 STRESS injects
bit-flip noise (eta=0.10) into the codebook BEFORE MP-KS evaluation: does the
routing decision still land correctly when the entries are 10%-corrupted by
sign flips (the standard real-world depolarization noise model)?

Honest framing
--------------
If E1 PASSes, Cap 12 ✅ survives a substantive real-world envelope expansion:
the MP-KS pre-test is not a fragile clean-codebook artifact. If E1 FAILs, the
✅ claim collapses for noisy substrates and Cap 12 reverts to 🟢 with a
"clean-only" annotation. If E1 lands in the MIDDLE BAND (1-3/5 at one or two
tau values), Cap 12 ✅ stays with a noise-sensitivity annotation.

Design
------
- Reuse the v174 tau-robustness measurement loop, but inject bit-flip noise
  into the codebook AFTER it is built (so the noisy codebook is what MP-KS
  evaluates and AMP/VAMP see).
- Noise model: for each codebook entry, flip its SIGN independently with
  probability eta=0.10. This is the canonical depolarization channel for
  bipolar codebooks (Hadamard, RM, Kerdock) and a calibrated equivalent for
  iid Gauss / SRHT (sign-flip changes the entry magnitude distribution
  identically since the Gauss / SRHT entries are symmetric around 0).
- Same 5 codebooks at N=1024, M/N=1.0, 5 seeds.
- For each codebook + seed: build clean W -> apply noise (per-entry sign flip
  with prob eta) -> measure MP-KS once on noisy W -> run AMP + VAMP once on
  noisy (W_noisy, y) to establish empirical truth label.
- At each tau in {0.15, 0.20, 0.25}: route_from_ks(ks_noisy, tau)
  -> per-codebook per-tau routing decision.

Note on noise vs truth label: noise is added to BOTH the matrix the routing
decision is computed on AND the matrix the empirical truth is measured on.
This is the customer-facing setting (noise = part of the channel; the operator
sees only the noisy matrix). The routing claim is "given the noisy matrix you
observe, the MP-KS pre-test routes to the algorithm that is empirically
faithful on that noisy matrix."

HARD PASS (Cap 12 ✅ survives E1 STRESS)
----------------------------------------
  >=4/5 codebooks routed correctly at EACH of tau in {0.15, 0.20, 0.25}
  under eta=0.10 noise.

HARD FAIL (Cap 12 ✅ reverts to 🟢, "clean-only" annotation)
------------------------------------------------------------
  0/5 routed correctly at ANY tau value under eta=0.10 noise.
  (Infrastructure FRAGILE to noise; the customer-facing claim collapses.)

MIDDLE BAND (Cap 12 ✅ stays with noise-sensitivity annotation)
---------------------------------------------------------------
  1-3/5 correct at one or two tau values; partial robustness.

Vertex: MP_KS_NOISY_SUBSTRATE_PASS / KILLED / INCONCLUSIVE

Pre-reg: preregs/2026-05-24_wave14_mp_ks_noisy_substrate_v1.md
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

# Reuse BBMD-VAMP correspondence v1 AMP/VAMP loops + closed-form predictions.
_bv_path = REPO / "experiments" / "exp_wave14_bbmd_vamp_correspondence_sweep_v1.py"
_spec_bv = importlib.util.spec_from_file_location("bbmd_vamp_v1", _bv_path)
_bv = importlib.util.module_from_spec(_spec_bv)
_spec_bv.loader.exec_module(_bv)
amp_se_scalar = _bv.amp_se_scalar
vamp_se_closed = _bv.vamp_se_closed
run_amp = _bv.run_amp
run_vamp = _bv.run_vamp


CODEBOOKS = [
    ("iid_gauss", build_iid_gauss, "AMP_OK"),
    ("srht",      build_srht,      "AMP_OK"),
    ("hadamard",  build_hadamard,  "VAMP_REQUIRED"),
    ("rm_1_m",    build_rm_1_m,    "VAMP_REQUIRED"),
    ("kerdock",   build_kerdock,   "VAMP_REQUIRED"),
]

TAU_GRID = (0.15, 0.20, 0.25)
ETA_NOISE = 0.10  # bit-flip rate


def apply_signflip_noise(W: np.ndarray, eta: float, seed: int) -> np.ndarray:
    """Per-entry sign-flip with probability eta. This is the canonical
    depolarization channel for bipolar codebooks; for Gaussian / SRHT entries
    it's a symmetric distortion that does not alter the marginal distribution
    of magnitudes (only joint sign structure).

    flips[i,j] = -1 with prob eta, +1 otherwise.
    Returns W * flips (entry-wise).
    """
    rng = np.random.default_rng(seed)
    mask = (rng.random(size=W.shape) < eta)
    signs = np.where(mask, -1.0, 1.0).astype(W.dtype)
    return W * signs


def route_from_ks(ks: float, tau: float) -> str:
    return "AMP_OK" if ks <= tau else "VAMP_REQUIRED"


def empirical_truth_from_errs(amp_rel: float, vamp_rel: float,
                              fail_thresh: float = 0.10) -> str:
    return "AMP_OK" if amp_rel < fail_thresh else "VAMP_REQUIRED"


def measure_codebook_noisy(name: str, builder, expected_label: str,
                           N: int, M: int, n_seeds: int, sigma_sq: float,
                           signal_var: float, n_iter: int,
                           eta: float) -> dict:
    alpha_ratio = M / N
    amp_se_pred = amp_se_scalar(alpha_ratio, sigma_sq, signal_var)

    ks_vals, amp_rels, vamp_rels = [], [], []
    for seed in range(n_seeds):
        seed_val = seed * 1000 + 17
        W_clean = builder(N, M, seed_val)

        # Inject sign-flip noise (eta) into the codebook BEFORE MP-KS / AMP / VAMP.
        # Noise seed offset by 50_000 so the same codebook seed yields a stable
        # noisy realization across reruns (reproducible).
        W = apply_signflip_noise(W_clean, eta, seed=seed_val + 50_000)

        M_actual, N_actual = W.shape

        U, s, Vt = np.linalg.svd(W, full_matrices=False)
        eig = (s ** 2).astype(np.float64)

        ks_val, _, _ = mp_ks_stat(eig, M_actual, N_actual)
        ks_vals.append(ks_val)

        rng_sig = np.random.default_rng(seed_val + 91)
        x_true = rng_sig.standard_normal(N_actual).astype(np.float64) * math.sqrt(signal_var)
        noise = rng_sig.standard_normal(M_actual).astype(np.float64) * math.sqrt(sigma_sq)
        y = (W.astype(np.float64) @ x_true) + noise

        amp_emp = run_amp(W, y, x_true, signal_var, sigma_sq, n_iter)
        vamp_se_pred = vamp_se_closed(s, N_actual, M_actual, sigma_sq, signal_var)
        vamp_emp = run_vamp(U, s, Vt, y, x_true, signal_var, sigma_sq, n_iter)

        amp_rel = abs(amp_emp - amp_se_pred) / max(amp_emp, amp_se_pred, 1e-12)
        vamp_rel = abs(vamp_emp - vamp_se_pred) / max(vamp_emp, vamp_se_pred, 1e-12)
        amp_rels.append(amp_rel)
        vamp_rels.append(vamp_rel)

        print(f"    {name:10s} seed={seed} eta={eta} ks={ks_val:.4f} "
              f"amp_emp={amp_emp:.5f} amp_rel={amp_rel:.3f} "
              f"vamp_emp={vamp_emp:.5f} vamp_rel={vamp_rel:.3f}",
              flush=True)

    ks_mean = float(np.mean(ks_vals))
    amp_rel_mean = float(np.mean(amp_rels))
    vamp_rel_mean = float(np.mean(vamp_rels))
    empirical_label = empirical_truth_from_errs(amp_rel_mean, vamp_rel_mean)
    return {
        "name": name,
        "expected_label_clean": expected_label,
        "ks_mean": ks_mean,
        "ks_std": float(np.std(ks_vals)),
        "amp_rel_mean": amp_rel_mean,
        "vamp_rel_mean": vamp_rel_mean,
        "empirical_label": empirical_label,
        "per_seed_ks": ks_vals,
    }


def compute_verdict(summary: dict) -> tuple[str, str]:
    """E1 STRESS bands:
       HARD PASS: >=4/5 correct at EACH tau in TAU_GRID under eta=0.10.
       HARD FAIL: 0/5 at ANY tau value under eta=0.10.
       MIDDLE BAND: 1-3/5 at one or two tau values (partial robustness).
    """
    cbs = summary.get("codebook_results") or []
    if len(cbs) < len(CODEBOOKS):
        return ("MP_KS_NOISY_SUBSTRATE_INCONCLUSIVE",
                f"Missing codebooks: have {len(cbs)} need {len(CODEBOOKS)}.")

    per_tau = {}
    routing_matrix = []
    for tau in TAU_GRID:
        correct = 0
        row = []
        for r in cbs:
            routed = route_from_ks(r["ks_mean"], tau)
            ok = routed == r["empirical_label"]
            row.append({
                "name": r["name"], "ks_mean": r["ks_mean"],
                "routed": routed, "truth": r["empirical_label"], "correct": ok,
            })
            if ok:
                correct += 1
        per_tau[f"{tau:.2f}"] = correct
        routing_matrix.append({"tau": tau, "correct": correct, "rows": row})
    summary["per_tau_correct"] = per_tau
    summary["routing_matrix"] = routing_matrix
    summary["eta"] = ETA_NOISE

    min_correct = min(per_tau.values())
    max_correct = max(per_tau.values())
    summary["min_correct_across_tau"] = min_correct
    summary["max_correct_across_tau"] = max_correct

    # HARD FAIL: 0/5 at any tau
    if min_correct == 0:
        bad_taus = [t for t, c in per_tau.items() if c == 0]
        return ("MP_KS_NOISY_SUBSTRATE_KILLED",
                f"Routing collapses to 0/5 at tau in {bad_taus}: per_tau={per_tau}. "
                f"Infrastructure FRAGILE to eta={ETA_NOISE} noise; the customer-facing "
                f"claim collapses for noisy substrates. Cap 12 reverts to 🟢 with "
                f"clean-only annotation.")

    # HARD PASS: all tau >= 4
    if min_correct >= 4:
        return ("MP_KS_NOISY_SUBSTRATE_PASS",
                f"Routing survives eta={ETA_NOISE} noise across tau in "
                f"{[f'{t:.2f}' for t in TAU_GRID]}: per_tau={per_tau}. >=4/5 correct "
                f"at every tau. Cap 12 ✅ survives E1 STRESS; MP-KS pre-flight is "
                f"robust to real-world depolarization noise.")

    # MIDDLE BAND: between 1 and 3 at some tau
    return ("MP_KS_NOISY_SUBSTRATE_INCONCLUSIVE",
            f"Partial robustness under eta={ETA_NOISE}: per_tau={per_tau}. "
            f"Degraded but partial; Cap 12 ✅ stands with noise-sensitivity "
            f"annotation. Routing matrix: {routing_matrix}.")


def self_test() -> None:
    # Self-test 1: apply_signflip_noise at eta=0 leaves matrix unchanged.
    W0 = np.array([[1.0, 2.0], [-3.0, 4.0]], dtype=np.float32)
    out = apply_signflip_noise(W0, 0.0, seed=42)
    assert np.allclose(out, W0), f"eta=0 should be identity, got {out}"

    # Self-test 2: apply_signflip_noise at eta=1.0 negates the entire matrix.
    out = apply_signflip_noise(W0, 1.0, seed=42)
    assert np.allclose(out, -W0), f"eta=1.0 should negate, got {out}"

    # Self-test 3: empirical flip fraction at eta=0.10 lands near 0.10 (large mat).
    rng = np.random.default_rng(123)
    W_big = rng.standard_normal(size=(200, 200)).astype(np.float32)
    W_noisy = apply_signflip_noise(W_big, 0.10, seed=99)
    flip_frac = float(np.mean(np.sign(W_big) != np.sign(W_noisy)))
    assert 0.07 < flip_frac < 0.13, f"eta=0.10 flip-fraction should be ~0.10, got {flip_frac}"

    # Self-test 4: route_from_ks formula (inherits from tau-robustness v1)
    assert route_from_ks(0.10, 0.15) == "AMP_OK"
    assert route_from_ks(0.16, 0.15) == "VAMP_REQUIRED"
    assert route_from_ks(0.25, 0.25) == "AMP_OK"
    assert route_from_ks(0.26, 0.25) == "VAMP_REQUIRED"

    # Self-test 5: empirical_truth_from_errs
    assert empirical_truth_from_errs(0.05, 0.02) == "AMP_OK"
    assert empirical_truth_from_errs(0.50, 0.02) == "VAMP_REQUIRED"

    # Self-test 6: HARD PASS verdict (>=4/5 at each tau under noise)
    fake_pass = [
        {"name": "iid_gauss", "ks_mean": 0.02, "empirical_label": "AMP_OK"},
        {"name": "srht",      "ks_mean": 0.10, "empirical_label": "AMP_OK"},
        {"name": "hadamard",  "ks_mean": 0.50, "empirical_label": "VAMP_REQUIRED"},
        {"name": "rm_1_m",    "ks_mean": 0.40, "empirical_label": "VAMP_REQUIRED"},
        {"name": "kerdock",   "ks_mean": 0.70, "empirical_label": "VAMP_REQUIRED"},
    ]
    # tau=0.15: iid AMP correct, srht AMP correct, hadamard VAMP correct, rm VAMP correct, kerdock VAMP correct -> 5
    # tau=0.20: same -> 5
    # tau=0.25: same -> 5
    summary = {"codebook_results": fake_pass}
    v, msg = compute_verdict(summary)
    assert v == "MP_KS_NOISY_SUBSTRATE_PASS", f"expected PASS got {v}: {msg}"

    # Self-test 7: HARD FAIL (0/5 at one tau)
    fake_fail = [
        # all 5 codebooks have ks=0.50, truth label AMP_OK
        # at tau=0.15: all routed VAMP, all truth AMP -> 0 correct
        # at tau=0.20: all routed VAMP, all truth AMP -> 0 correct
        # at tau=0.25: all routed VAMP, all truth AMP -> 0 correct
        {"name": "iid_gauss", "ks_mean": 0.50, "empirical_label": "AMP_OK"},
        {"name": "srht",      "ks_mean": 0.50, "empirical_label": "AMP_OK"},
        {"name": "hadamard",  "ks_mean": 0.50, "empirical_label": "AMP_OK"},
        {"name": "rm_1_m",    "ks_mean": 0.50, "empirical_label": "AMP_OK"},
        {"name": "kerdock",   "ks_mean": 0.50, "empirical_label": "AMP_OK"},
    ]
    v, msg = compute_verdict({"codebook_results": fake_fail})
    assert v == "MP_KS_NOISY_SUBSTRATE_KILLED", f"expected KILLED got {v}: {msg}"

    # Self-test 8: MIDDLE BAND (3-correct at one tau)
    fake_mid = [
        {"name": "iid_gauss", "ks_mean": 0.18, "empirical_label": "AMP_OK"},
        # tau=0.15: VAMP wrong; tau=0.20: AMP correct; tau=0.25: AMP correct
        {"name": "srht",      "ks_mean": 0.17, "empirical_label": "AMP_OK"},
        # tau=0.15: VAMP wrong; tau=0.20: AMP correct; tau=0.25: AMP correct
        {"name": "hadamard",  "ks_mean": 0.50, "empirical_label": "VAMP_REQUIRED"},
        {"name": "rm_1_m",    "ks_mean": 0.40, "empirical_label": "VAMP_REQUIRED"},
        {"name": "kerdock",   "ks_mean": 0.70, "empirical_label": "VAMP_REQUIRED"},
    ]
    # tau=0.15: iid wrong, srht wrong, hadamard correct, rm correct, kerdock correct = 3
    # tau=0.20: all correct = 5
    # tau=0.25: all correct = 5
    v, msg = compute_verdict({"codebook_results": fake_mid})
    assert v == "MP_KS_NOISY_SUBSTRATE_INCONCLUSIVE", f"expected INCONCLUSIVE got {v}: {msg}"

    # Self-test 9: missing codebooks
    v, _ = compute_verdict({"codebook_results": fake_pass[:3]})
    assert v == "MP_KS_NOISY_SUBSTRATE_INCONCLUSIVE"

    print("MP-KS noisy-substrate self-test passed (9/9 cases)", flush=True)


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
            "tau_grid": list(TAU_GRID),
            "eta": ETA_NOISE,
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
            "tau_grid": list(TAU_GRID),
            "eta": ETA_NOISE,
            "codebooks": [nm for nm, _b, _l in CODEBOOKS],
        }

    N = config["N"]
    M = max(1, int(config["M_over_N"] * N))
    sigma_sq = config["sigma_noise"] ** 2
    signal_var = config["signal_var"]
    n_iter = config["n_iter"]
    n_seeds = config["n_seeds"]
    eta = config["eta"]

    print(f"[setup] N={N} M={M} n_seeds={n_seeds} eta={eta} tau_grid={config['tau_grid']} "
          f"codebooks={config['codebooks']}", flush=True)

    builder_map = {nm: (b, lab) for nm, b, lab in CODEBOOKS}
    codebook_results = []
    for nm in config["codebooks"]:
        builder, expected = builder_map[nm]
        print(f"\n[codebook] {nm} (clean-expected: {expected})", flush=True)
        result = measure_codebook_noisy(nm, builder, expected, N, M, n_seeds,
                                        sigma_sq, signal_var, n_iter, eta)
        codebook_results.append(result)
        print(f"  AGG {nm}: ks_mean={result['ks_mean']:.4f} "
              f"amp_rel={result['amp_rel_mean']:.4f} "
              f"vamp_rel={result['vamp_rel_mean']:.4f} "
              f"empirical={result['empirical_label']}", flush=True)

    summary = {"codebook_results": codebook_results, "config": config,
               "tau_grid": list(TAU_GRID), "eta": eta}
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
    out_dir = get_output_dir("wave14_mp_ks_noisy_substrate_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["codebook_results"]) >= 1, "smoke FAIL: no codebooks"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_mp_ks_noisy_substrate_v1")
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
