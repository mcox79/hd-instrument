"""MP-KS noise-envelope sweep (E1'): map eta-critical for Cap 12 routing.

Motivation
----------
E1 (`exp_wave14_mp_ks_noisy_substrate_v1`) tested a SINGLE noise level
(eta=0.10) at three tau values. The verdict_handler landed E1 in the
MIDDLE-BAND and pre-registered this follow-up sub-probe: instead of
sweeping tau at fixed eta, FIX tau=0.20 (the v175 / E1 anchor) and SWEEP
eta to map the noise envelope. Goal: identify eta_critical, the noise
level at which MP-KS routing accuracy drops below 4/5.

Honest framing
--------------
This is an envelope-mapping sub-probe under
[[feedback-envelope-expansion-fail-bands]]. The expectation is to find a
threshold eta_critical somewhere in (0, 0.10] such that the customer-
facing claim can be tightened to "Cap 12 routes correctly up to noise
level eta_critical."
- If routing survives up through eta=0.05 and beyond, Cap 12 ✅ envelope
  extends to eta<=0.05 (substantial robustness; production noise is
  almost always below 5%).
- If routing breaks at eta=0.01 already, Cap 12 reverts to 🟢 "clean-
  only" — the v175 promotion was an artifact of clean conditions.
- Otherwise: middle band with explicit narrow noise envelope (1% < eta <
  5%); ✅ stands with annotation.

Design
------
- Sweep eta in {0.0, 0.01, 0.025, 0.05, 0.075, 0.10}.
- For each eta: run the SAME v174/v175/E1 protocol (5 codebooks ×
  N=1024 × M/N=1.0 × 5 seeds × n_iter=300) at fixed tau=0.20.
- For each (eta, codebook): build clean W, apply sign-flip noise with
  this eta, MP-KS once on noisy W, AMP+VAMP once on (W_noisy, y) for
  empirical truth label, route_from_ks(ks_mean, tau=0.20),
  per_eta_correct ∈ {0..5}.
- Plot routing accuracy as a function of eta.
- Identify eta_critical = the smallest eta where per_eta_correct < 4.
  If no such eta in the grid → eta_critical = ">0.10" (the envelope
  extends past the grid).

Noise model (inherited from noisy_substrate_v1)
-----------------------------------------------
Per-entry sign flip with probability eta (canonical depolarization
channel for bipolar codebooks; symmetric distortion of joint sign
structure for iid Gauss / SRHT). Implemented as W * signs, with
signs[i,j] = -1 with prob eta, +1 else.

HARD PASS (Cap 12 ✅ envelope extends to eta <= 0.05)
-----------------------------------------------------
Routing accuracy >= 4/5 at eta=0.05 AND at every smaller eta in the grid
(i.e. >= 4/5 at eta in {0.0, 0.01, 0.025, 0.05}). Substrate-product
claim: "Cap 12 tolerates noise up to eta = 5% before degrading."

HARD FAIL (Cap 12 ✅ reverts to 🟢, clean-only annotation)
----------------------------------------------------------
Routing accuracy < 4/5 at eta=0.01. Substrate-product claim collapses
to "clean-only routing"; the v175 ✅ was an artifact of clean
conditions.

MIDDLE BAND (narrow noise tolerance window, ✅ with annotation)
---------------------------------------------------------------
>= 4/5 at eta=0.01 but < 4/5 at eta=0.05 (envelope is positive but
narrow: 1% < eta_critical < 5%). Cap 12 ✅ stays with explicit
noise-envelope annotation.

Vertex: MP_KS_NOISE_ENVELOPE_SWEEP_PASS / KILLED / INCONCLUSIVE

Pre-reg: preregs/2026-05-24_wave14_mp_ks_noise_envelope_sweep_v1.md
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

TAU_FIXED = 0.20
ETA_GRID = (0.0, 0.01, 0.025, 0.05, 0.075, 0.10)
PASS_THRESHOLD = 4  # >=4/5 correct
HARD_PASS_ETA_CEILING = 0.05  # envelope must extend to this eta to HARD PASS
HARD_FAIL_ETA_FLOOR = 0.01    # routing fails at this eta -> HARD FAIL


def apply_signflip_noise(W: np.ndarray, eta: float, seed: int) -> np.ndarray:
    """Per-entry sign-flip with probability eta. Inherited verbatim from
    noisy_substrate_v1: flips[i,j] = -1 with prob eta, +1 otherwise.
    Returns W * flips (entry-wise). eta=0 returns W unchanged; eta=1 returns -W.
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


def measure_codebook_at_eta(name: str, builder, expected_label: str,
                            N: int, M: int, n_seeds: int, sigma_sq: float,
                            signal_var: float, n_iter: int,
                            eta: float) -> dict:
    """Run 5 seeds at one (codebook, eta) cell. Returns aggregate ks_mean +
    empirical_label for routing decision."""
    alpha_ratio = M / N
    amp_se_pred = amp_se_scalar(alpha_ratio, sigma_sq, signal_var)

    ks_vals, amp_rels, vamp_rels = [], [], []
    for seed in range(n_seeds):
        seed_val = seed * 1000 + 17
        W_clean = builder(N, M, seed_val)

        # Noise seed offset by 50_000 (same convention as noisy_substrate_v1)
        # for stable, reproducible noisy realizations per (codebook, seed, eta).
        # Add eta-derived offset so different eta values produce different
        # noise realizations (otherwise eta=0.01 and eta=0.10 would share the
        # same uniform draws and just threshold differently — that would still
        # be valid but the offset gives independent draws per eta cell).
        eta_offset = int(round(eta * 1_000_000))
        noise_seed = seed_val + 50_000 + eta_offset
        W = apply_signflip_noise(W_clean, eta, seed=noise_seed)

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

        print(f"    {name:10s} eta={eta:.3f} seed={seed} ks={ks_val:.4f} "
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
        "eta": eta,
        "ks_mean": ks_mean,
        "ks_std": float(np.std(ks_vals)),
        "amp_rel_mean": amp_rel_mean,
        "vamp_rel_mean": vamp_rel_mean,
        "empirical_label": empirical_label,
        "per_seed_ks": ks_vals,
    }


def identify_eta_critical(per_eta_correct: dict, eta_grid: tuple) -> str:
    """Return smallest eta in grid where per_eta_correct < PASS_THRESHOLD.
    If none in grid, return f'>{max(eta_grid)}' (envelope extends past grid)."""
    for eta in sorted(eta_grid):
        key = f"{eta:.3f}"
        if per_eta_correct.get(key, PASS_THRESHOLD) < PASS_THRESHOLD:
            return key
    return f">{max(eta_grid):.3f}"


def compute_verdict(summary: dict) -> tuple[str, str]:
    """E1' noise-envelope sweep bands (tau fixed at TAU_FIXED=0.20):
       HARD PASS: >=4/5 correct at EVERY eta in {0.0, 0.01, 0.025, 0.05}.
                  (Envelope extends to eta=HARD_PASS_ETA_CEILING=0.05.)
       HARD FAIL: <4/5 correct at eta=0.01 (HARD_FAIL_ETA_FLOOR).
                  (Envelope is zero; routing breaks on any noise.)
       MIDDLE BAND: >=4/5 at eta=0.01 but <4/5 at eta=0.05.
                    (Narrow envelope; 1% < eta_critical < 5%.)
    """
    cells = summary.get("envelope_cells") or []
    expected_n_cells = len(ETA_GRID) * len(CODEBOOKS)
    if len(cells) < expected_n_cells:
        return ("MP_KS_NOISE_ENVELOPE_SWEEP_INCONCLUSIVE",
                f"Missing envelope cells: have {len(cells)} need {expected_n_cells}.")

    per_eta_correct = {}
    routing_matrix = []
    for eta in ETA_GRID:
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
    summary["eta_grid"] = list(ETA_GRID)

    eta_critical = identify_eta_critical(per_eta_correct, ETA_GRID)
    summary["eta_critical"] = eta_critical

    eta_001_correct = per_eta_correct[f"{HARD_FAIL_ETA_FLOOR:.3f}"]
    eta_005_correct = per_eta_correct[f"{HARD_PASS_ETA_CEILING:.3f}"]
    eta_000_correct = per_eta_correct[f"{0.0:.3f}"]
    eta_0025_correct = per_eta_correct[f"{0.025:.3f}"]

    # HARD FAIL: <4 at eta=0.01 (envelope is essentially zero)
    if eta_001_correct < PASS_THRESHOLD:
        return ("MP_KS_NOISE_ENVELOPE_SWEEP_KILLED",
                f"Routing fails at eta={HARD_FAIL_ETA_FLOOR}: "
                f"per_eta_correct[{HARD_FAIL_ETA_FLOOR:.3f}]={eta_001_correct}<{PASS_THRESHOLD}. "
                f"per_eta_correct={per_eta_correct}. "
                f"Cap 12 envelope is essentially zero — routing breaks on any meaningful "
                f"noise. Cap 12 ✅ reverts to 🟢 with clean-only annotation; the v175 "
                f"✅ promotion was an artifact of clean-codebook conditions. "
                f"eta_critical={eta_critical}.")

    # HARD PASS: >=4 at every eta up through HARD_PASS_ETA_CEILING (=0.05)
    if (eta_000_correct >= PASS_THRESHOLD and
        eta_001_correct >= PASS_THRESHOLD and
        eta_0025_correct >= PASS_THRESHOLD and
        eta_005_correct >= PASS_THRESHOLD):
        return ("MP_KS_NOISE_ENVELOPE_SWEEP_PASS",
                f"Routing envelope extends through eta=0.05: "
                f"per_eta_correct={per_eta_correct}. "
                f"Cap 12 ✅ envelope extends to eta <= {HARD_PASS_ETA_CEILING}; "
                f"substrate-product claim: 'Cap 12 tolerates noise up to eta = 5% "
                f"before degrading.' eta_critical={eta_critical}.")

    # MIDDLE BAND: >=4 at eta=0.01 but <4 at eta=0.05 (or at one of the intermediate cells)
    return ("MP_KS_NOISE_ENVELOPE_SWEEP_INCONCLUSIVE",
            f"Narrow noise envelope: per_eta_correct={per_eta_correct}. "
            f"Routing tolerates eta=0.01 (>={PASS_THRESHOLD}/5) but degrades before "
            f"eta=0.05. Cap 12 ✅ stays with explicit noise-envelope annotation "
            f"(envelope is {HARD_FAIL_ETA_FLOOR} <= eta_critical < {HARD_PASS_ETA_CEILING}). "
            f"eta_critical={eta_critical}.")


def self_test() -> None:
    # Self-test 1: apply_signflip_noise at eta=0 leaves matrix unchanged.
    W0 = np.array([[1.0, 2.0], [-3.0, 4.0]], dtype=np.float32)
    out = apply_signflip_noise(W0, 0.0, seed=42)
    assert np.allclose(out, W0), f"eta=0 should be identity, got {out}"

    # Self-test 2: apply_signflip_noise at eta=1.0 negates the entire matrix.
    out = apply_signflip_noise(W0, 1.0, seed=42)
    assert np.allclose(out, -W0), f"eta=1.0 should negate, got {out}"

    # Self-test 3: empirical flip fraction at eta=0.025 lands near 0.025 (large mat).
    rng = np.random.default_rng(123)
    W_big = rng.standard_normal(size=(400, 400)).astype(np.float32)
    W_noisy = apply_signflip_noise(W_big, 0.025, seed=99)
    flip_frac = float(np.mean(np.sign(W_big) != np.sign(W_noisy)))
    assert 0.018 < flip_frac < 0.034, f"eta=0.025 flip-fraction should be ~0.025, got {flip_frac}"

    # Self-test 4: route_from_ks formula at fixed tau=0.20
    assert route_from_ks(0.10, 0.20) == "AMP_OK"
    assert route_from_ks(0.20, 0.20) == "AMP_OK"  # <= boundary
    assert route_from_ks(0.21, 0.20) == "VAMP_REQUIRED"

    # Self-test 5: empirical_truth_from_errs boundary
    assert empirical_truth_from_errs(0.05, 0.02) == "AMP_OK"
    assert empirical_truth_from_errs(0.50, 0.02) == "VAMP_REQUIRED"

    # Self-test 6: identify_eta_critical — first sub-threshold eta
    per_eta = {"0.000": 5, "0.010": 5, "0.025": 5, "0.050": 3, "0.075": 1, "0.100": 0}
    assert identify_eta_critical(per_eta, ETA_GRID) == "0.050", \
        f"expected 0.050 got {identify_eta_critical(per_eta, ETA_GRID)}"

    # Self-test 7: identify_eta_critical — no failure in grid
    per_eta_all_pass = {f"{e:.3f}": 5 for e in ETA_GRID}
    assert identify_eta_critical(per_eta_all_pass, ETA_GRID) == ">0.100"

    # Self-test 8: identify_eta_critical — failure at very first eta
    per_eta_fail0 = {f"{e:.3f}": 0 for e in ETA_GRID}
    assert identify_eta_critical(per_eta_fail0, ETA_GRID) == "0.000"

    # Build synthetic envelope_cells for verdict tests. Per codebook truth label:
    # iid_gauss/srht = AMP_OK (clean expectation); hadamard/rm_1_m/kerdock = VAMP_REQUIRED.
    def synth_cells(ks_by_eta: dict) -> list:
        """ks_by_eta: {eta_float: {name: ks_value}} → cells list."""
        truth = {"iid_gauss": "AMP_OK", "srht": "AMP_OK",
                 "hadamard": "VAMP_REQUIRED", "rm_1_m": "VAMP_REQUIRED",
                 "kerdock": "VAMP_REQUIRED"}
        cells = []
        for eta, ks_map in ks_by_eta.items():
            for name, ks in ks_map.items():
                cells.append({
                    "name": name, "eta": eta, "ks_mean": ks,
                    "empirical_label": truth[name],
                })
        return cells

    # Self-test 9: HARD PASS — all etas show correct routing
    # At every eta: iid/srht have ks<=0.20 → AMP_OK match; hadamard/rm/kerdock have ks>0.20
    # → VAMP_REQUIRED match. So 5/5 at every eta.
    clean_ks_pattern = {"iid_gauss": 0.05, "srht": 0.10, "hadamard": 0.50,
                        "rm_1_m": 0.45, "kerdock": 0.70}
    pass_cells = synth_cells({e: clean_ks_pattern for e in ETA_GRID})
    summary = {"envelope_cells": pass_cells}
    v, msg = compute_verdict(summary)
    assert v == "MP_KS_NOISE_ENVELOPE_SWEEP_PASS", f"expected PASS got {v}: {msg}"
    # eta_critical should be >0.100 (no failure in grid)
    assert summary["eta_critical"] == ">0.100", \
        f"expected >0.100 got {summary['eta_critical']}"

    # Self-test 10: HARD FAIL — routing breaks at eta=0.01 already
    # iid_gauss has ks=0.50 at eta=0.01, truth=AMP_OK → mismatch
    # Set up so every codebook mis-routes at eta=0.01 → 0/5
    fail_ks_at_001 = {"iid_gauss": 0.50, "srht": 0.50, "hadamard": 0.05,
                      "rm_1_m": 0.05, "kerdock": 0.05}
    ks_by_eta = {e: clean_ks_pattern for e in ETA_GRID}
    ks_by_eta[0.01] = fail_ks_at_001
    fail_cells = synth_cells(ks_by_eta)
    summary = {"envelope_cells": fail_cells}
    v, msg = compute_verdict(summary)
    assert v == "MP_KS_NOISE_ENVELOPE_SWEEP_KILLED", f"expected KILLED got {v}: {msg}"
    assert summary["eta_critical"] == "0.010", \
        f"expected 0.010 got {summary['eta_critical']}"

    # Self-test 11: MIDDLE BAND — passes at eta=0.01, fails at eta=0.05
    # At eta=0.05 set iid+srht to ks=0.50 → 2 wrong (5-2=3 correct, <4)
    mid_ks_at_005 = {"iid_gauss": 0.50, "srht": 0.50, "hadamard": 0.55,
                     "rm_1_m": 0.45, "kerdock": 0.70}
    ks_by_eta = {e: clean_ks_pattern for e in ETA_GRID}
    ks_by_eta[0.05] = mid_ks_at_005
    mid_cells = synth_cells(ks_by_eta)
    summary = {"envelope_cells": mid_cells}
    v, msg = compute_verdict(summary)
    assert v == "MP_KS_NOISE_ENVELOPE_SWEEP_INCONCLUSIVE", f"expected INCONCLUSIVE got {v}: {msg}"
    assert summary["eta_critical"] == "0.050", \
        f"expected 0.050 got {summary['eta_critical']}"

    # Self-test 12: missing cells -> INCONCLUSIVE
    v, _ = compute_verdict({"envelope_cells": pass_cells[:5]})
    assert v == "MP_KS_NOISE_ENVELOPE_SWEEP_INCONCLUSIVE"

    # Self-test 13: ETA_GRID monotonic and contains required pillars
    assert tuple(sorted(ETA_GRID)) == ETA_GRID, "ETA_GRID must be sorted ascending"
    assert 0.0 in ETA_GRID and HARD_FAIL_ETA_FLOOR in ETA_GRID and HARD_PASS_ETA_CEILING in ETA_GRID

    print("MP-KS noise-envelope-sweep self-test passed (13/13 cases)", flush=True)


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
            "eta_grid": [0.0, 0.05],   # 2 eta values for smoke
            "codebooks": ["iid_gauss", "srht"],  # 2 codebooks for smoke
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
            "tau_fixed": TAU_FIXED,
            "eta_grid": list(ETA_GRID),
            "codebooks": [nm for nm, _b, _l in CODEBOOKS],
        }

    N = config["N"]
    M = max(1, int(config["M_over_N"] * N))
    sigma_sq = config["sigma_noise"] ** 2
    signal_var = config["signal_var"]
    n_iter = config["n_iter"]
    n_seeds = config["n_seeds"]
    tau = config["tau_fixed"]

    print(f"[setup] N={N} M={M} n_seeds={n_seeds} tau_fixed={tau} "
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
               "tau_fixed": tau, "eta_grid": list(config["eta_grid"])}
    # In smoke mode, verdict will be INCONCLUSIVE due to fewer cells; that's expected.
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
    out_dir = get_output_dir("wave14_mp_ks_noise_envelope_sweep_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["envelope_cells"]) >= 1, "smoke FAIL: no envelope cells"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_mp_ks_noise_envelope_sweep_v1")
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
