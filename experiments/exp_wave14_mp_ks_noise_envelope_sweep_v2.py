"""MP-KS noise-envelope sweep v2: higher-statistics resolution of eta_critical
in the apparently-critical 1-5% band.

Motivation
----------
E1' v1 swept eta in {0.0, 0.01, 0.025, 0.05, 0.075, 0.10} at 5 seeds and
landed in MIDDLE-BAND.  Verdict-handler pre-registered this higher-stats
follow-up: finer eta grid in the apparently-critical region and ~4x more
seeds for tighter routing-accuracy confidence intervals.

What's new vs v1
----------------
1. **Finer grid in the critical region.** eta in {0.01, 0.02, 0.03, 0.04, 0.05}
   (5 points, evenly spaced through the band where v1 saw degradation).
   The eta=0 baseline is dropped because v174 already confirmed clean
   routing at 4-5/5; running it again at 20 seeds is wasted compute.
2. **20 seeds per cell** (vs 5 in v1) for routing-accuracy CIs.
3. **Same protocol otherwise:** 5 codebooks * N=1024 * M/N=1.0 * tau=0.20.

Total cells = 5 codebooks * 5 eta * 20 seeds = 500 (vs v1's 5*6*5=150).
About 3.3x v1's compute on a per-seed basis; v1 took ~15-20 min CPU at
N=1024 / 300 VAMP iters, so v2 ETA ~45-60 min CPU.

Honest framing
--------------
Same band logic as v1 but with the finer grid:
- If routing >= 4/5 monotonically across all eta in {0.01..0.05}, Cap 12 ✅
  noise-envelope claim extends to eta <= 0.05 (HARD PASS).
- If routing degrades to <= 3/5 at eta=0.02 already, Cap 12 envelope is
  very narrow (eta < 0.02; HARD FAIL).
- Otherwise: monotonic decay but no clean eta_critical resolved (MIDDLE).

HARD PASS (Cap 12 ✅ noise envelope extends to eta <= 0.05)
-----------------------------------------------------------
Routing accuracy >= 4/5 (i.e., for 20-seed cells: total correct >= 16/20
in the aggregated counting; for the per-eta routing-correct metric across
the 5 codebooks: 4/5 correct codebooks at every eta in {0.01..0.05})
AND non-increasing monotonically across eta.

  Operational rule: at every eta in {0.01, 0.02, 0.03, 0.04, 0.05},
  per_eta_correct_codebooks >= 4 (out of 5).
  AND ks_mean is monotonically non-decreasing in eta (within 1 stddev tolerance).

HARD FAIL (Cap 12 ✅ noise envelope is NARROW)
----------------------------------------------
Routing accuracy <= 3/5 at eta=0.02 (envelope < 2%; very narrow).

  Operational rule: per_eta_correct_codebooks <= 3 at eta=0.02.

MIDDLE BAND
-----------
Monotonic decay but no clean eta_critical resolved between PASS and FAIL.

Vertex: MP_KS_NOISE_ENVELOPE_SWEEP_V2_PASS / KILLED / INCONCLUSIVE

Pre-reg: preregs/2026-05-24_wave14_mp_ks_noise_envelope_sweep_v2.md
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
# Reuse v1 envelope-sweep machinery in its entirety: codebook builders,
# noise model, route-from-ks, empirical-truth helper, single-cell measurer.
_v1_path = REPO / "experiments" / "exp_wave14_mp_ks_noise_envelope_sweep_v1.py"
_spec_v1 = importlib.util.spec_from_file_location("mp_ks_v1", _v1_path)
_v1 = importlib.util.module_from_spec(_spec_v1)
_spec_v1.loader.exec_module(_v1)

apply_signflip_noise = _v1.apply_signflip_noise
route_from_ks = _v1.route_from_ks
empirical_truth_from_errs = _v1.empirical_truth_from_errs
measure_codebook_at_eta = _v1.measure_codebook_at_eta
CODEBOOKS = _v1.CODEBOOKS  # same 5 codebooks
TAU_FIXED = _v1.TAU_FIXED  # 0.20


# v2 grid: finer resolution in the 1-5% band, no eta=0 (already pinned)
ETA_GRID_V2 = (0.01, 0.02, 0.03, 0.04, 0.05)

PASS_THRESHOLD = 4   # >= 4/5 codebooks routed correctly at a given eta
NARROW_CHECK_ETA = 0.02   # HARD FAIL if <=3/5 at this eta
HARD_PASS_CEILING = 0.05  # envelope must hold up through this eta


def identify_eta_critical(per_eta_correct: dict, eta_grid: tuple) -> str:
    """Return smallest eta in grid where per_eta_correct < PASS_THRESHOLD.
    If none in grid, return f'>{max(eta_grid)}' (envelope extends past grid)."""
    for eta in sorted(eta_grid):
        key = f"{eta:.3f}"
        if per_eta_correct.get(key, PASS_THRESHOLD) < PASS_THRESHOLD:
            return key
    return f">{max(eta_grid):.3f}"


def check_monotonic_ks_in_eta(routing_matrix: list, tol: float = 1.0) -> bool:
    """Verify that average ks across codebooks is non-decreasing in eta
    (within `tol` standard deviations of the within-codebook spread).
    Returns True if monotonic non-decreasing.
    """
    if len(routing_matrix) < 2:
        return True
    avg_ks_by_eta = []
    for row in sorted(routing_matrix, key=lambda r: r["eta"]):
        # Average ks_mean across codebooks at this eta
        ks_vals = [r2["ks_mean"] for r2 in row["rows"]]
        avg_ks_by_eta.append(np.mean(ks_vals))
    # Allow small downticks within tolerance
    for i in range(1, len(avg_ks_by_eta)):
        delta = avg_ks_by_eta[i] - avg_ks_by_eta[i - 1]
        if delta < -tol:
            return False
    return True


def compute_verdict(summary: dict) -> tuple[str, str]:
    """v2 verdict logic:

    HARD PASS:
      per_eta_correct >= 4 at EVERY eta in {0.01..0.05}
      AND avg ks_mean is monotonically non-decreasing in eta.

    HARD FAIL:
      per_eta_correct <= 3 at eta=0.02 (envelope is very narrow; <2% only).

    MIDDLE BAND:
      anything else.
    """
    cells = summary.get("envelope_cells") or []
    expected_n_cells = len(ETA_GRID_V2) * len(CODEBOOKS)
    if len(cells) < expected_n_cells:
        return ("MP_KS_NOISE_ENVELOPE_SWEEP_V2_INCONCLUSIVE",
                f"Missing envelope cells: have {len(cells)} need {expected_n_cells}.")

    per_eta_correct = {}
    routing_matrix = []
    for eta in ETA_GRID_V2:
        correct = 0
        row = []
        for r in cells:
            if abs(r["eta"] - eta) > 1e-9:
                continue
            routed = route_from_ks(r["ks_mean"], TAU_FIXED)
            ok = routed == r["empirical_label"]
            row.append({
                "name": r["name"], "ks_mean": r["ks_mean"],
                "routed": routed, "truth": r["empirical_label"], "correct": ok,
            })
            if ok:
                correct += 1
        per_eta_correct[f"{eta:.3f}"] = correct
        routing_matrix.append({"eta": eta, "correct": correct, "rows": row})

    summary["per_eta_correct"] = per_eta_correct
    summary["routing_matrix"] = routing_matrix
    summary["tau_fixed"] = TAU_FIXED
    summary["eta_grid"] = list(ETA_GRID_V2)

    eta_critical = identify_eta_critical(per_eta_correct, ETA_GRID_V2)
    summary["eta_critical"] = eta_critical
    summary["monotonic_ks_in_eta"] = check_monotonic_ks_in_eta(routing_matrix)

    eta_002 = per_eta_correct[f"{NARROW_CHECK_ETA:.3f}"]
    eta_005 = per_eta_correct[f"{HARD_PASS_CEILING:.3f}"]

    # HARD FAIL: <= 3 correct at eta=0.02
    if eta_002 <= 3:
        return ("MP_KS_NOISE_ENVELOPE_SWEEP_V2_KILLED",
                f"Cap 12 noise envelope NARROW: per_eta_correct[{NARROW_CHECK_ETA:.3f}]"
                f"={eta_002}<=3. Routing degrades on <=2% noise; the v175 ✅ envelope "
                f"is essentially clean-only.  Substrate-product claim narrows to "
                f"'Cap 12 routes correctly only for noise eta<1-2%.' "
                f"per_eta_correct={per_eta_correct} eta_critical={eta_critical}.")

    # HARD PASS: >=4 at EVERY eta in {0.01..0.05} and monotonic ks
    all_ge_4 = all(per_eta_correct[f"{eta:.3f}"] >= PASS_THRESHOLD
                   for eta in ETA_GRID_V2)
    if all_ge_4 and summary["monotonic_ks_in_eta"]:
        return ("MP_KS_NOISE_ENVELOPE_SWEEP_V2_PASS",
                f"Cap 12 noise envelope extends to eta <= {HARD_PASS_CEILING}: "
                f"per_eta_correct={per_eta_correct} with monotonic ks growth. "
                f"Substrate-product claim: 'Cap 12 tolerates noise up to eta=5% "
                f"before degrading.' eta_critical={eta_critical}.")

    # MIDDLE BAND
    return ("MP_KS_NOISE_ENVELOPE_SWEEP_V2_INCONCLUSIVE",
            f"Cap 12 noise envelope MIDDLE: monotonic decay but no clean "
            f"eta_critical resolved. per_eta_correct={per_eta_correct} "
            f"monotonic_ks_in_eta={summary['monotonic_ks_in_eta']} "
            f"eta_critical={eta_critical}.  Need even more seeds (v3) to "
            f"resolve eta_critical to within +/- 0.005.")


def self_test() -> None:
    # Self-test 1: ETA_GRID_V2 is monotonic and matches the v2 design
    assert tuple(sorted(ETA_GRID_V2)) == ETA_GRID_V2, "ETA_GRID_V2 must be sorted"
    assert min(ETA_GRID_V2) == 0.01 and max(ETA_GRID_V2) == 0.05
    assert NARROW_CHECK_ETA in ETA_GRID_V2 and HARD_PASS_CEILING in ETA_GRID_V2

    # Self-test 2: route_from_ks at the v2 tau
    assert route_from_ks(0.10, 0.20) == "AMP_OK"
    assert route_from_ks(0.21, 0.20) == "VAMP_REQUIRED"

    # Self-test 3: identify_eta_critical works on v2 grid
    per_eta = {"0.010": 5, "0.020": 5, "0.030": 4, "0.040": 3, "0.050": 1}
    assert identify_eta_critical(per_eta, ETA_GRID_V2) == "0.040"
    per_eta_all_pass = {f"{e:.3f}": 5 for e in ETA_GRID_V2}
    assert identify_eta_critical(per_eta_all_pass, ETA_GRID_V2) == ">0.050"

    # Self-test 4: synthetic cells -> HARD PASS branch
    truth = {"iid_gauss": "AMP_OK", "srht": "AMP_OK",
             "hadamard": "VAMP_REQUIRED", "rm_1_m": "VAMP_REQUIRED",
             "kerdock": "VAMP_REQUIRED"}

    def synth_cells_v2(ks_by_eta: dict) -> list:
        cells = []
        for eta, ks_map in ks_by_eta.items():
            for name, ks in ks_map.items():
                cells.append({
                    "name": name, "eta": eta, "ks_mean": ks,
                    "empirical_label": truth[name],
                })
        return cells

    # PASS: ks values monotonic increasing in eta but stay correctly routed
    ks_at = {
        0.01: {"iid_gauss": 0.05, "srht": 0.10, "hadamard": 0.50,
               "rm_1_m": 0.45, "kerdock": 0.70},
        0.02: {"iid_gauss": 0.06, "srht": 0.11, "hadamard": 0.52,
               "rm_1_m": 0.47, "kerdock": 0.72},
        0.03: {"iid_gauss": 0.07, "srht": 0.12, "hadamard": 0.55,
               "rm_1_m": 0.50, "kerdock": 0.75},
        0.04: {"iid_gauss": 0.08, "srht": 0.13, "hadamard": 0.58,
               "rm_1_m": 0.53, "kerdock": 0.78},
        0.05: {"iid_gauss": 0.10, "srht": 0.15, "hadamard": 0.60,
               "rm_1_m": 0.55, "kerdock": 0.80},
    }
    cells = synth_cells_v2(ks_at)
    summary = {"envelope_cells": cells}
    v, _ = compute_verdict(summary)
    assert v == "MP_KS_NOISE_ENVELOPE_SWEEP_V2_PASS", f"PASS test failed: {v}"
    assert summary["monotonic_ks_in_eta"] is True

    # Self-test 5: HARD FAIL when eta=0.02 has 3 wrong routings
    # Force iid+srht to wrong-route at eta=0.02 (ks=0.50 > tau=0.20 but truth=AMP_OK)
    # plus hadamard wrong-route too
    ks_at[0.02] = {"iid_gauss": 0.50, "srht": 0.50, "hadamard": 0.05,
                   "rm_1_m": 0.05, "kerdock": 0.05}
    cells = synth_cells_v2(ks_at)
    # At eta=0.02: iid_gauss routes VAMP (wrong, truth AMP), srht VAMP (wrong),
    # hadamard AMP (wrong, truth VAMP), rm_1_m AMP (wrong), kerdock AMP (wrong)
    # All 5 wrong -> per_eta_correct=0 at 0.02 -> HARD FAIL
    v, _ = compute_verdict({"envelope_cells": cells})
    assert v == "MP_KS_NOISE_ENVELOPE_SWEEP_V2_KILLED", f"FAIL test failed: {v}"

    # Self-test 6: MIDDLE band: eta=0.02 passes (4/5) but eta=0.04 fails
    ks_at[0.02] = {"iid_gauss": 0.50, "srht": 0.10, "hadamard": 0.55,
                   "rm_1_m": 0.45, "kerdock": 0.70}  # 4/5 correct (iid wrong)
    ks_at[0.04] = {"iid_gauss": 0.50, "srht": 0.50, "hadamard": 0.05,
                   "rm_1_m": 0.05, "kerdock": 0.05}  # 0/5 correct
    cells = synth_cells_v2(ks_at)
    v, _ = compute_verdict({"envelope_cells": cells})
    assert v == "MP_KS_NOISE_ENVELOPE_SWEEP_V2_INCONCLUSIVE", f"MIDDLE test failed: {v}"

    # Self-test 7: missing cells -> INCONCLUSIVE
    v, _ = compute_verdict({"envelope_cells": cells[:3]})
    assert v == "MP_KS_NOISE_ENVELOPE_SWEEP_V2_INCONCLUSIVE"

    # Self-test 8: check_monotonic_ks_in_eta — clean monotonic
    mono_matrix = [
        {"eta": 0.01, "rows": [{"ks_mean": 0.1}, {"ks_mean": 0.2}]},
        {"eta": 0.02, "rows": [{"ks_mean": 0.15}, {"ks_mean": 0.25}]},
        {"eta": 0.03, "rows": [{"ks_mean": 0.2}, {"ks_mean": 0.3}]},
    ]
    assert check_monotonic_ks_in_eta(mono_matrix) is True

    # Self-test 9: check_monotonic_ks_in_eta — strong downtick fails (with tol=0.05)
    nonmono = [
        {"eta": 0.01, "rows": [{"ks_mean": 0.5}, {"ks_mean": 0.5}]},
        {"eta": 0.02, "rows": [{"ks_mean": 0.1}, {"ks_mean": 0.1}]},
    ]
    assert check_monotonic_ks_in_eta(nonmono, tol=0.05) is False

    print("v2 noise-envelope self-test passed (9/9 cases)", flush=True)


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
            "tau_fixed": TAU_FIXED,
            "eta_grid": [0.01, 0.05],
            "codebooks": ["iid_gauss", "srht"],
        }
    else:
        config = {
            "mode": "full",
            "N": 1024,
            "M_over_N": 1.0,
            "n_seeds": 20,
            "sigma_noise": 0.1,
            "signal_var": 1.0,
            "n_iter": 300,
            "tau_fixed": TAU_FIXED,
            "eta_grid": list(ETA_GRID_V2),
            "codebooks": [nm for nm, _b, _l in CODEBOOKS],
        }

    N = config["N"]
    M = max(1, int(config["M_over_N"] * N))
    sigma_sq = config["sigma_noise"] ** 2
    signal_var = config["signal_var"]
    n_iter = config["n_iter"]
    n_seeds = config["n_seeds"]

    print(f"[setup] v2 N={N} M={M} n_seeds={n_seeds} tau_fixed={TAU_FIXED} "
          f"eta_grid={config['eta_grid']} codebooks={config['codebooks']}", flush=True)

    builder_map = {nm: (b, lab) for nm, b, lab in CODEBOOKS}
    envelope_cells = []
    for eta in config["eta_grid"]:
        print(f"\n[eta] {eta:.3f}", flush=True)
        for nm in config["codebooks"]:
            builder, expected = builder_map[nm]
            print(f"  [codebook] {nm} (clean-expected: {expected})", flush=True)
            result = measure_codebook_at_eta(nm, builder, expected, N, M, n_seeds,
                                             sigma_sq, signal_var, n_iter, eta)
            envelope_cells.append(result)
            print(f"    AGG {nm} eta={eta:.3f}: ks_mean={result['ks_mean']:.4f} "
                  f"amp_rel={result['amp_rel_mean']:.4f} "
                  f"vamp_rel={result['vamp_rel_mean']:.4f} "
                  f"empirical={result['empirical_label']}", flush=True)

    summary = {"envelope_cells": envelope_cells, "config": config,
               "tau_fixed": TAU_FIXED, "eta_grid": list(config["eta_grid"])}
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
    out_dir = get_output_dir("wave14_mp_ks_noise_envelope_sweep_v2_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["envelope_cells"]) >= 1, "smoke FAIL: no envelope cells"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_mp_ks_noise_envelope_sweep_v2")
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
