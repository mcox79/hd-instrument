"""E3 Gold-family stress gate for Cap 12 ✅ predictor.

Cap 12 (AMP-vs-VAMP routing) was promoted to ✅ at v175 on the 5-codebook
basis {iid_gauss, SRHT, Hadamard, RM(1,m), Kerdock}. E3 hardens by adding a
5TH-family stress test using GOLD sequences -- a separate algebraic family
that shares Kerdock's GF(2^m)-trace machinery but uses distinct combinatorics
(3-valued cross-correlation, no 4-coset of Reed-Muller).

The Gold quickprobe earlier this session returned BBMD_CANDIDATE (kappa_n
diverges from MP, but spectrum stays bulk-bounded). E3 promotes that probe
to the full Cap 12 predictor test: does the AMP-error vs sum-|delta-kappa_n|
predictor hold on the iid-Gauss -> Gold interpolation family?

Design (mirrors interp_family_hadamard/srht_v1)
-----------------------------------------------
- m = 10, N_eff = 1023 (Gold family natural length), padded to N=1024 by
  appending a zero column to the Gold construction; the padded column does
  not contribute to the spectrum but allows alignment with the Cap-12 v175
  N=1024 standard.
- alpha grid {0.0, 0.25, 0.5, 0.75, 1.0}; 5 alpha cells; 10 seeds per cell
  (Research drilled-down spec; matches v175 base resolution).
- W_alpha = ((1-alpha) * G + alpha * W_gold_unnorm) / sqrt(N).
- Per (alpha, seed): SVD; kappa profile k_2..k_6 via free-cumulant inversion;
  BBMD distance d = sum_{n=2..6} |kappa_n - M/N|; AMP-SE prediction; empirical
  AMP; AMP rel-err; VAMP-SE closed-form; empirical VAMP; VAMP rel-err.

Padding rationale
-----------------
The Gold family has N_eff = 2^m - 1 = 1023 sequences of length 1023. To plug
into the Cap-12 N=1024 pipeline without re-derivation, we pad by appending
a single all-zero column. The resulting (M, 1024) matrix has rank-deficient
spectrum WITH a guaranteed zero eigenvalue from the padded column, plus the
1023 Gold eigenvalues. Since we measure spectral moments and free cumulants
on the empirical eigenvalue distribution (which now includes one trivial
zero), the BBMD distance is slightly perturbed; we account for this by
documenting M/N = 1024/1024 = 1.0 but knowing the "effective" rank is 1023.

ALTERNATIVE considered: use N=1023 directly. Rejected because (a) v175
baseline is N=1024 power-of-2 (SRHT/Hadamard require power-of-2) and (b)
the cross-codebook predictor test compares across families at the SAME N;
padding is the cleanest reconciliation.

Honest framing
--------------
PASS hardens Cap 12 ✅ with a 5th independent family beyond the original 4
interpolation families (SRHT, Hadamard, RM, Kerdock). The threshold here
(rho >= 0.50) is WEAKER than the 0.70 PASS used for the primary gate
(Hadamard, SRHT) because:
  - E3 is a 5th-family hardening, not the primary gate.
  - Gold uses a separate algebraic family than the SRHT/Hadamard tested.
  - Quickprobe already showed BBMD_CANDIDATE (kappa_n nontrivial).

HARD PASS (E3 5th-family gate satisfied)
----------------------------------------
- Spearman rho(amp_rel_err, bbmd_distance) >= 0.50 across 5 alpha cells
- AND max VAMP rel-err < 0.15.

HARD FAIL (E3 breaks the predictor; reverts Cap 12 to 🟢 with annotation)
--------------------------------------------------------------------------
- Spearman rho < 0.30
- OR max VAMP rel-err > 0.30.

MIDDLE BAND
-----------
- rho in [0.30, 0.50) OR vamp rel-err in [0.15, 0.30) -- predictor weakens
  but doesn't collapse; Cap 12 ✅ holds with Gold-family annotation.

Vertex: KAPPA_GOLD_FULL_E3_PASS / KILLED / INCONCLUSIVE

Pre-reg: preregs/2026-05-24_wave14_kappa_gold_full_e3_v1.md
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

# Reuse Gold family generator from quickprobe v1
_qp_path = REPO / "experiments" / "exp_wave14_kappa_gold_quickprobe_v1.py"
_spec_qp = importlib.util.spec_from_file_location("gold_quickprobe_v1", _qp_path)
_qp = importlib.util.module_from_spec(_spec_qp)
_spec_qp.loader.exec_module(_qp)
gold_sequence_family = _qp.gold_sequence_family

# Reuse BBMD-VAMP AMP/VAMP loops + closed-form predictions
_bv_path = REPO / "experiments" / "exp_wave14_bbmd_vamp_correspondence_sweep_v1.py"
_spec_bv = importlib.util.spec_from_file_location("bbmd_vamp_v1", _bv_path)
_bv = importlib.util.module_from_spec(_spec_bv)
_spec_bv.loader.exec_module(_bv)
amp_se_scalar = _bv.amp_se_scalar
vamp_se_closed = _bv.vamp_se_closed
run_amp = _bv.run_amp
run_vamp = _bv.run_vamp

# Reuse kappa-profile inversion
_v1_path = REPO / "experiments" / "exp_wave14_kappa_n_profile_v1.py"
_spec_v1 = importlib.util.spec_from_file_location("kappa_v1", _v1_path)
_v1 = importlib.util.module_from_spec(_spec_v1)
_spec_v1.loader.exec_module(_v1)
moments_to_free_cumulants_general = _v1.moments_to_free_cumulants_general


FAMILY = "gold"


def build_gold_unnormalized(N: int, M: int, seed: int, m: int = 10) -> np.ndarray:
    """Gold codebook at m=10 (N_eff=1023) padded to N=1024 with zero column.

    Returns (M, N) bipolar entries in {+1, -1, 0} (the zero column is the
    padding); UNNORMALIZED (no 1/sqrt(N) post-normalize).

    For N=1024: m=10 -> N_eff=1023, pad with 1 zero column.
    For N=64 (smoke): m=6 -> N_eff=63, pad with 1 zero column.
    """
    if N == 1024:
        m_eff = 10
        N_eff = 1023
    elif N == 64:
        m_eff = 6
        N_eff = 63
    else:
        # Find largest valid m such that 2^m - 1 <= N
        m_eff = int(math.log2(N + 1))
        while (1 << m_eff) - 1 > N:
            m_eff -= 1
        if m_eff < 6:
            raise ValueError(f"N={N} too small for Gold (need m>=6)")
        N_eff = (1 << m_eff) - 1

    fam = gold_sequence_family(m_eff)  # (N_eff + 2, N_eff) in {0, 1}
    bipolar = (1 - 2 * fam.astype(np.float32))  # {+1, -1}

    rng = np.random.default_rng(seed)
    row_perm = rng.permutation(fam.shape[0])
    A = bipolar[row_perm[:M], :]  # (M, N_eff)

    # Pad to N columns with zeros
    if N > N_eff:
        pad = np.zeros((M, N - N_eff), dtype=np.float32)
        A = np.concatenate([A, pad], axis=1)

    return A.astype(np.float32)  # (M, N) bipolar/zero


def build_W_alpha_gold(alpha: float, N: int, M: int, seed: int,
                       struct_cache: dict) -> np.ndarray:
    """W_alpha = ((1-alpha) * G + alpha * W_gold_unnorm) / sqrt(N).

    G entries iid N(0, 1) (un-normalized; same scale as +/-1 Gold entries).
    Caches the Gold block per (N, M, seed). Gaussian seed offset by 1_000_000.
    """
    cache_key = (N, M, seed)
    if cache_key not in struct_cache:
        struct_cache[cache_key] = build_gold_unnormalized(N, M, seed)
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
        return ("KAPPA_GOLD_FULL_E3_INCONCLUSIVE",
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
        return ("KAPPA_GOLD_FULL_E3_INCONCLUSIVE",
                f"Only {len(dists)} valid cells with finite metrics.")

    rho_result = spearmanr(amp_errs, dists)
    rho = float(rho_result.statistic) if hasattr(rho_result, "statistic") else float(rho_result[0])
    if not math.isfinite(rho):
        return ("KAPPA_GOLD_FULL_E3_INCONCLUSIVE",
                f"Spearman rho not finite.")

    max_vamp = max(vamp_errs)
    summary["spearman_rho"] = rho
    summary["max_vamp_rel_err"] = max_vamp
    summary["bbmd_distances"] = dists
    summary["amp_rel_errs"] = amp_errs
    summary["vamp_rel_errs"] = vamp_errs

    # HARD PASS (E3 weaker thresholds because 5th-family hardening)
    if rho >= 0.50 and max_vamp < 0.15:
        return ("KAPPA_GOLD_FULL_E3_PASS",
                f"E3 5th-family gate satisfied on Gold interpolation: "
                f"Spearman rho(amp_rel_err, sum|delta_kappa_n|) = {rho:.3f} "
                f">= 0.50 across {len(dists)} alpha cells; max VAMP rel-err = "
                f"{max_vamp:.4f} < 0.15. Cap 12 ✅ predictor generalizes to "
                f"a 5th independent algebraic family (Gold sequences, "
                f"GF(2^10)-trace machinery, 3-valued cross-correlation).")

    # HARD FAIL
    if rho < 0.30 or max_vamp > 0.30:
        return ("KAPPA_GOLD_FULL_E3_KILLED",
                f"E3 BREAKS the Cap 12 predictor on Gold: rho = {rho:.3f} "
                f"(HARD FAIL if < 0.30); max VAMP rel-err = {max_vamp:.4f} "
                f"(HARD FAIL if > 0.30). Cap 12 reverts to 🟢 with annotation "
                f"that Gold-family codebooks are outside the AMP-vs-VAMP "
                f"routing envelope. dists={dists} amp_errs={amp_errs} "
                f"vamp_errs={vamp_errs}.")

    # MIDDLE BAND
    return ("KAPPA_GOLD_FULL_E3_INCONCLUSIVE",
            f"Borderline: rho = {rho:.3f} (PASS>=0.50, FAIL<0.30), "
            f"max VAMP rel-err = {max_vamp:.4f} (PASS<0.15, FAIL>0.30). "
            f"E3 weakens the predictor but doesn't collapse; Cap 12 ✅ "
            f"holds with Gold-family middle-band annotation.")


def self_test() -> None:
    # Cell 1: bbmd_distance on MP-reference (kappas == c) -> 0
    c = 1.0
    d = bbmd_distance([c] * 6, c, 2, 6)
    assert abs(d) < 1e-12, f"bbmd on MP should be 0, got {d}"

    # Cell 2: bbmd on deviating cumulants -> exact sum
    devs = [c, c + 0.1, c + 0.2, c + 0.3, c + 0.4, c + 0.5]
    d = bbmd_distance(devs, c, 2, 6)
    assert abs(d - 1.5) < 1e-9, f"bbmd want 1.5 got {d}"

    # Cell 3: spearmanr on monotone -> 1.0
    rho_r = spearmanr([0.01, 0.05, 0.10, 0.20, 0.30],
                      [0.0, 0.5, 1.0, 1.5, 2.0])
    rho_val = float(rho_r.statistic) if hasattr(rho_r, "statistic") else float(rho_r[0])
    assert abs(rho_val - 1.0) < 1e-9

    # Cell 4: PASS scenario (rho=1.0, max_vamp=0.06)
    cells_pass = [
        {"alpha_interp": 0.0,  "bbmd_distance_mean": 0.05, "amp_rel_err_mean": 0.02, "vamp_rel_err_mean": 0.02},
        {"alpha_interp": 0.25, "bbmd_distance_mean": 0.10, "amp_rel_err_mean": 0.05, "vamp_rel_err_mean": 0.03},
        {"alpha_interp": 0.50, "bbmd_distance_mean": 0.20, "amp_rel_err_mean": 0.10, "vamp_rel_err_mean": 0.04},
        {"alpha_interp": 0.75, "bbmd_distance_mean": 0.40, "amp_rel_err_mean": 0.15, "vamp_rel_err_mean": 0.05},
        {"alpha_interp": 1.0,  "bbmd_distance_mean": 0.60, "amp_rel_err_mean": 0.25, "vamp_rel_err_mean": 0.06},
    ]
    v, msg = compute_verdict({"cells": cells_pass})
    assert v == "KAPPA_GOLD_FULL_E3_PASS", f"expected PASS got {v}: {msg}"

    # Cell 5: KILLED via low rho (anti-monotone)
    cells_killed = [
        {"alpha_interp": 0.0,  "bbmd_distance_mean": 0.05, "amp_rel_err_mean": 0.30, "vamp_rel_err_mean": 0.02},
        {"alpha_interp": 0.25, "bbmd_distance_mean": 0.10, "amp_rel_err_mean": 0.25, "vamp_rel_err_mean": 0.03},
        {"alpha_interp": 0.50, "bbmd_distance_mean": 0.20, "amp_rel_err_mean": 0.20, "vamp_rel_err_mean": 0.04},
        {"alpha_interp": 0.75, "bbmd_distance_mean": 0.40, "amp_rel_err_mean": 0.10, "vamp_rel_err_mean": 0.05},
        {"alpha_interp": 1.0,  "bbmd_distance_mean": 0.60, "amp_rel_err_mean": 0.05, "vamp_rel_err_mean": 0.06},
    ]
    v, _ = compute_verdict({"cells": cells_killed})
    assert v == "KAPPA_GOLD_FULL_E3_KILLED"

    # Cell 6: KILLED via VAMP blowup
    cells_killed_v = [
        {"alpha_interp": 0.0,  "bbmd_distance_mean": 0.05, "amp_rel_err_mean": 0.02, "vamp_rel_err_mean": 0.02},
        {"alpha_interp": 0.50, "bbmd_distance_mean": 0.20, "amp_rel_err_mean": 0.10, "vamp_rel_err_mean": 0.04},
        {"alpha_interp": 1.0,  "bbmd_distance_mean": 0.60, "amp_rel_err_mean": 0.25, "vamp_rel_err_mean": 0.40},
    ]
    v, _ = compute_verdict({"cells": cells_killed_v})
    assert v == "KAPPA_GOLD_FULL_E3_KILLED"

    # Cell 7: MIDDLE BAND (rho ~ 0.4 in [0.30, 0.50))
    # dists ranked 1,2,3,4,5; amp ranks 2,3,4,1,5; rho = 0.4 exactly
    cells_mid = [
        {"alpha_interp": 0.0,  "bbmd_distance_mean": 0.05, "amp_rel_err_mean": 0.10, "vamp_rel_err_mean": 0.02},
        {"alpha_interp": 0.25, "bbmd_distance_mean": 0.10, "amp_rel_err_mean": 0.15, "vamp_rel_err_mean": 0.03},
        {"alpha_interp": 0.50, "bbmd_distance_mean": 0.20, "amp_rel_err_mean": 0.20, "vamp_rel_err_mean": 0.04},
        {"alpha_interp": 0.75, "bbmd_distance_mean": 0.40, "amp_rel_err_mean": 0.05, "vamp_rel_err_mean": 0.05},
        {"alpha_interp": 1.0,  "bbmd_distance_mean": 0.60, "amp_rel_err_mean": 0.25, "vamp_rel_err_mean": 0.06},
    ]
    v, _ = compute_verdict({"cells": cells_mid})
    assert v == "KAPPA_GOLD_FULL_E3_INCONCLUSIVE", f"expected INCONCLUSIVE got {v}"

    # Cell 8: MIDDLE BAND via VAMP in (0.15, 0.30)
    cells_mid_v = [
        {"alpha_interp": 0.0,  "bbmd_distance_mean": 0.05, "amp_rel_err_mean": 0.02, "vamp_rel_err_mean": 0.05},
        {"alpha_interp": 0.50, "bbmd_distance_mean": 0.20, "amp_rel_err_mean": 0.10, "vamp_rel_err_mean": 0.12},
        {"alpha_interp": 1.0,  "bbmd_distance_mean": 0.60, "amp_rel_err_mean": 0.25, "vamp_rel_err_mean": 0.20},
    ]
    v, _ = compute_verdict({"cells": cells_mid_v})
    assert v == "KAPPA_GOLD_FULL_E3_INCONCLUSIVE"

    # Cell 9: too-few cells INCONCLUSIVE
    v, _ = compute_verdict({"cells": cells_pass[:1]})
    assert v == "KAPPA_GOLD_FULL_E3_INCONCLUSIVE"

    print("gold full E3 self-test passed (9/9 cases)", flush=True)


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
            "m_gold": 6,
            "N_eff_gold": 63,
        }
    else:
        config = {
            "mode": "full",
            "N": 1024,
            "M_over_N": 1.0,
            "alpha_interp_list": [0.0, 0.25, 0.5, 0.75, 1.0],
            "sigma_noise": 0.1,
            "signal_var": 1.0,
            "n_seeds": 10,
            "n_iter": 300,
            "n_max_moment": 6,
            "family": FAMILY,
            "m_gold": 10,
            "N_eff_gold": 1023,
        }

    N = config["N"]
    M = max(1, int(config["M_over_N"] * N))
    sigma = config["sigma_noise"]
    sigma_sq = sigma ** 2
    signal_var = config["signal_var"]
    alpha_ratio = M / N
    n_max = config["n_max_moment"]

    print(f"[setup] family={FAMILY} N={N} M={M} M/N={alpha_ratio:.3f} sigma={sigma} "
          f"alpha_interp={config['alpha_interp_list']} seeds={config['n_seeds']} "
          f"m_gold={config['m_gold']} N_eff_gold={config['N_eff_gold']}",
          flush=True)

    amp_se_pred = amp_se_scalar(alpha_ratio, sigma_sq, signal_var)
    struct_cache: dict = {}

    cells = []
    for alpha_int in config["alpha_interp_list"]:
        seed_records = []
        for seed in range(config["n_seeds"]):
            seed_val = seed * 1000 + 31  # offset to differ from Hadamard family
            W = build_W_alpha_gold(alpha_int, N, M, seed_val, struct_cache)

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
    out_dir = get_output_dir("wave14_kappa_gold_full_e3_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["cells"]) >= 1, "smoke FAIL: no cells"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_kappa_gold_full_e3_v1")
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
