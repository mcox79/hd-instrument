"""MP-KS pre-test tau-robustness sweep: Cap 12 Gate A pre-reg.

Motivation
----------
Cap 12 (AMP-vs-VAMP inference routing infrastructure) was promoted to GREEN
at cap_map v174 with the MP-KS pre-test landing 4/5 codebooks at tau=0.20
(verdict MP_KS_PRETEST_PIPELINE_PASS, 1383x speedup). The composite framing
is "MP-KS pre-flight + kappa_n divergence explainer". Promotion from GREEN
to GREEN-CHECK requires TWO pre-registered ✅ gates:

  Gate A (this experiment): tau-robustness across tau in {0.15, 0.20, 0.25}.
      HARD PASS: >=4/5 codebooks routed correctly at EACH of the three tau values.
      HARD FAIL: <3/5 routed correctly at ANY tau value.
      MIDDLE BAND: 3-4/5 at one or two tau values (marginal; investigate).

  Gate B (separate experiment): iid-Gauss -> Hadamard interpolation family.

The question Gate A asks: is the tau=0.20 routing threshold ROBUST (a clean
gap in KS-space between AMP-OK and VAMP-required codebooks), or was tau=0.20
a hand-picked fragile threshold that fails on either side?

Honest framing
--------------
This is narrow infrastructure capability hardening, not substrate physics
novelty. The math (MP-KS) is classical (Gotze-Tikhomirov rates). The novelty
remains the PIPELINE framing. PASS at Gate A means the substrate ships a
robust pre-flight: pre-flight is not a fragile-threshold artifact.

Design
------
Same 5 codebooks as the v174 pretest pipeline (iid_gauss, SRHT, hadamard,
RM(1,m), kerdock) at N=1024, 5 seeds, M/N=1.0.

For EACH codebook:
  - Compute MP-KS once per seed.
  - Run AMP + VAMP once per seed -> establishes empirical truth label.
  - At each of tau in {0.15, 0.20, 0.25}: route_from_ks(ks, tau)
    -> per-codebook per-tau routing decision -> per-tau routing accuracy.

Output: routing-accuracy matrix [5 codebooks x 3 tau values]. Per-tau correct
count. Verdict from the per-tau matrix.

Vertex: MP_KS_TAU_ROBUSTNESS_PASS / KILLED / INCONCLUSIVE

Pre-reg: preregs/2026-05-24_wave14_mp_ks_pretest_tau_robustness_v1.md
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

# Reuse BBMD correspondence v1 AMP/VAMP loops + closed-form predictions.
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


def route_from_ks(ks: float, tau: float) -> str:
    return "AMP_OK" if ks <= tau else "VAMP_REQUIRED"


def empirical_truth_from_errs(amp_rel: float, vamp_rel: float,
                              fail_thresh: float = 0.10) -> str:
    return "AMP_OK" if amp_rel < fail_thresh else "VAMP_REQUIRED"


def measure_codebook(name: str, builder, expected_label: str,
                     N: int, M: int, n_seeds: int, sigma_sq: float,
                     signal_var: float, n_iter: int) -> dict:
    alpha_ratio = M / N
    amp_se_pred = amp_se_scalar(alpha_ratio, sigma_sq, signal_var)

    ks_vals, amp_rels, vamp_rels = [], [], []
    for seed in range(n_seeds):
        seed_val = seed * 1000 + 17
        W = builder(N, M, seed_val)
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
        "per_seed_ks": ks_vals,
    }


def compute_verdict(summary: dict) -> tuple[str, str]:
    """HARD PASS: >=4/5 correct at EACH tau in TAU_GRID.
    HARD FAIL: <3/5 correct at ANY tau in TAU_GRID.
    MIDDLE BAND: 3-4/5 at one or two tau values.
    """
    cbs = summary.get("codebook_results") or []
    if len(cbs) < len(CODEBOOKS):
        return ("MP_KS_TAU_ROBUSTNESS_INCONCLUSIVE",
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

    min_correct = min(per_tau.values())
    max_correct = max(per_tau.values())
    summary["min_correct_across_tau"] = min_correct
    summary["max_correct_across_tau"] = max_correct

    # HARD FAIL: any tau drops below 3
    if min_correct < 3:
        bad_taus = [t for t, c in per_tau.items() if c < 3]
        return ("MP_KS_TAU_ROBUSTNESS_KILLED",
                f"Routing collapses at tau in {bad_taus}: per_tau={per_tau}. "
                f"<3/5 correct at one or more tau values means the threshold "
                f"is fragile, not robust. Cap 12 Gate A FAILS.")

    # HARD PASS: ALL tau values >= 4
    if min_correct >= 4:
        return ("MP_KS_TAU_ROBUSTNESS_PASS",
                f"Routing is robust across tau in {[f'{t:.2f}' for t in TAU_GRID]}: "
                f"per_tau={per_tau}. >=4/5 correct at every tau. Cap 12 Gate A "
                f"PASSES; the routing threshold is not a fragile hand-picked "
                f"artifact.")

    # MIDDLE BAND: any tau in {3} (marginal)
    return ("MP_KS_TAU_ROBUSTNESS_INCONCLUSIVE",
            f"Marginal: per_tau={per_tau}. Some tau values land at 3/5 (middle "
            f"band); further investigation needed before Gate A can be called "
            f"PASS. Routing matrix: {routing_matrix}.")


def self_test() -> None:
    # Self-test 1: route_from_ks formula
    assert route_from_ks(0.10, 0.15) == "AMP_OK"
    assert route_from_ks(0.15, 0.15) == "AMP_OK"
    assert route_from_ks(0.16, 0.15) == "VAMP_REQUIRED"
    assert route_from_ks(0.20, 0.20) == "AMP_OK"
    assert route_from_ks(0.25, 0.25) == "AMP_OK"
    assert route_from_ks(0.26, 0.25) == "VAMP_REQUIRED"

    # Self-test 2: empirical_truth_from_errs
    assert empirical_truth_from_errs(0.05, 0.02) == "AMP_OK"
    assert empirical_truth_from_errs(0.50, 0.02) == "VAMP_REQUIRED"

    # Self-test 3: per-tau correct counter
    # Build a case where iid (ks=0.02), srht (ks=0.59 but truth=AMP_OK), hadamard,
    # rm, kerdock route at tau=0.20. The threshold-dependent codebook is iid (ks=0.02,
    # always in AMP_OK regardless of tau) vs the others. Use a synthetic mix where
    # only srht is mis-routed at tau=0.20.
    fake_cbs = [
        {"name": "iid_gauss", "ks_mean": 0.02, "empirical_label": "AMP_OK"},
        {"name": "srht",      "ks_mean": 0.59, "empirical_label": "AMP_OK"},      # mis-routed at all tau in (0.20, 0.25)
        {"name": "hadamard",  "ks_mean": 0.59, "empirical_label": "VAMP_REQUIRED"},
        {"name": "rm_1_m",    "ks_mean": 0.34, "empirical_label": "VAMP_REQUIRED"},
        {"name": "kerdock",   "ks_mean": 0.70, "empirical_label": "VAMP_REQUIRED"},
    ]
    # Expected per_tau:
    #   tau=0.15: iid->AMP correct; srht->VAMP wrong; hadamard->VAMP correct;
    #             rm->VAMP correct; kerdock->VAMP correct. 4 correct.
    #   tau=0.20: same as above. 4 correct.
    #   tau=0.25: same as above. 4 correct.
    summary = {"codebook_results": fake_cbs}
    v, msg = compute_verdict(summary)
    assert v == "MP_KS_TAU_ROBUSTNESS_PASS", f"expected PASS got {v}: {msg}"
    assert summary["per_tau_correct"] == {"0.15": 4, "0.20": 4, "0.25": 4}

    # Self-test 4: HARD FAIL at one tau
    fake_fail = [
        {"name": "iid_gauss", "ks_mean": 0.18, "empirical_label": "AMP_OK"},
        # at tau=0.15: ks=0.18 > 0.15 -> VAMP, wrong; at tau=0.20: ks=0.18 <= 0.20 -> AMP correct
        {"name": "srht",      "ks_mean": 0.18, "empirical_label": "AMP_OK"},
        # same pattern as iid (both AMP_OK with ks=0.18) -- at tau=0.15 both wrong
        {"name": "hadamard",  "ks_mean": 0.10, "empirical_label": "VAMP_REQUIRED"},
        # at all tau: ks=0.10 < tau -> AMP, but truth is VAMP -> always wrong
        {"name": "rm_1_m",    "ks_mean": 0.10, "empirical_label": "VAMP_REQUIRED"},
        # always wrong
        {"name": "kerdock",   "ks_mean": 0.10, "empirical_label": "VAMP_REQUIRED"},
        # always wrong
    ]
    # tau=0.15: iid wrong, srht wrong, hadamard wrong, rm wrong, kerdock wrong = 0
    # tau=0.20: iid correct, srht correct, hadamard wrong, rm wrong, kerdock wrong = 2
    # tau=0.25: iid correct, srht correct, hadamard wrong, rm wrong, kerdock wrong = 2
    v, msg = compute_verdict({"codebook_results": fake_fail})
    assert v == "MP_KS_TAU_ROBUSTNESS_KILLED", f"expected KILLED got {v}: {msg}"

    # Self-test 5: MIDDLE BAND (3-correct at one tau)
    fake_mid = [
        {"name": "iid_gauss", "ks_mean": 0.18, "empirical_label": "AMP_OK"},
        # tau=0.15: VAMP wrong; tau=0.20: AMP correct; tau=0.25: AMP correct
        {"name": "srht",      "ks_mean": 0.05, "empirical_label": "AMP_OK"},
        # always correct
        {"name": "hadamard",  "ks_mean": 0.50, "empirical_label": "VAMP_REQUIRED"},
        # always correct
        {"name": "rm_1_m",    "ks_mean": 0.40, "empirical_label": "VAMP_REQUIRED"},
        # always correct
        {"name": "kerdock",   "ks_mean": 0.70, "empirical_label": "VAMP_REQUIRED"},
        # always correct
    ]
    # tau=0.15: iid wrong (only), rest correct -> 4 correct (NOT 3)
    # Make it true 3-correct: have srht also mis-route at tau=0.15
    fake_mid[1]["ks_mean"] = 0.17  # tau=0.15: VAMP wrong (truth AMP_OK); tau=0.20/0.25: AMP correct
    # tau=0.15: iid wrong, srht wrong, hadamard correct, rm correct, kerdock correct = 3
    # tau=0.20: all correct = 5
    # tau=0.25: all correct = 5
    v, msg = compute_verdict({"codebook_results": fake_mid})
    assert v == "MP_KS_TAU_ROBUSTNESS_INCONCLUSIVE", f"expected INCONCLUSIVE got {v}: {msg}"

    # Self-test 6: missing codebooks
    v, _ = compute_verdict({"codebook_results": fake_cbs[:3]})
    assert v == "MP_KS_TAU_ROBUSTNESS_INCONCLUSIVE"

    print("MP-KS tau-robustness self-test passed (6/6 cases)", flush=True)


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
            "codebooks": [nm for nm, _b, _l in CODEBOOKS],
        }

    N = config["N"]
    M = max(1, int(config["M_over_N"] * N))
    sigma_sq = config["sigma_noise"] ** 2
    signal_var = config["signal_var"]
    n_iter = config["n_iter"]
    n_seeds = config["n_seeds"]

    print(f"[setup] N={N} M={M} n_seeds={n_seeds} tau_grid={config['tau_grid']} "
          f"codebooks={config['codebooks']}", flush=True)

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
              f"empirical={result['empirical_label']}", flush=True)

    summary = {"codebook_results": codebook_results, "config": config,
               "tau_grid": list(TAU_GRID)}
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
    out_dir = get_output_dir("wave14_mp_ks_pretest_tau_robustness_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["codebook_results"]) >= 1, "smoke FAIL: no codebooks"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_mp_ks_pretest_tau_robustness_v1")
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
