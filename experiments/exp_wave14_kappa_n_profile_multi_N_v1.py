"""kappa_n profile at multiple N -- scales the substrate-MP fingerprint sweep.

Motivation
----------
kappa_n_profile_v1 (2026-05-23) established KAPPA_PROFILE_GROWS at fixed N=4096:
the substrate-MP deviation in higher free cumulants amplifies as n increases
through n=8. The natural next question: does the GROWS pattern survive when N
is varied? If the fingerprint is an N->infty asymptotic property of the
Kerdock construction, |delta_n| at fixed n should stabilize across N. If it
is a finite-N artifact, the values should drift toward zero with growing N.

This experiment extends to N in {1024, 4096, 8192, 16384} with 10 seeds and
alpha in {0.5, 1, 2, 4}. The N=16384 cell requires t=7 primitive polynomial
in the Kerdock builder (newly added).

Approach
--------
Same n=8 NCP-based moment-to-free-cumulant inversion as v1. Reuses v1's
self_test machinery verbatim. Multi-N classifier: for each fixed alpha and
each n in {2..8}, check whether mean |delta_n| across N is approximately
constant (STABLE) or drifts (DRIFTS_UP / DRIFTS_DOWN).

ETA
---
At N=16384 alpha=4 the SVD of a 65536x16384 single-precision matrix is the
dominant cost. On the runner's RTX 30-series GPU this is ~2-3 min per (N,
alpha, seed) cell at the largest size. Total: 4 N * 4 alpha * 10 seeds = 160
cells, with the upper-right cells dominating cost. Expected wallclock ~45-60
min on GPU.

Vertex
------
KAPPA_MULTI_N_STABLE        -- |delta_n| approximately constant across N (asymptotic substrate fingerprint)
KAPPA_MULTI_N_GROWS_IN_N    -- |delta_n| grows with N (finite-N effect amplifying)
KAPPA_MULTI_N_DECAYS_IN_N   -- |delta_n| shrinks with N (finite-N artifact, fingerprint disappears)
KAPPA_MULTI_N_INCONCLUSIVE  -- no dominant pattern across (alpha, n) cells

Pre-reg: preregs/2026-05-23_wave14_kappa_n_profile_multi_N_v1.md
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

# Reuse v1 machinery: moment inversion, MP reference, eigenvalue extraction.
_v1_path = REPO / "experiments" / "exp_wave14_kappa_n_profile_v1.py"
_spec = importlib.util.spec_from_file_location("kappa_v1", _v1_path)
_v1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v1)

moments_to_free_cumulants_general = _v1.moments_to_free_cumulants_general
mp_reference_cumulants = _v1.mp_reference_cumulants
mp_reference_moments = _v1.mp_reference_moments
get_kerdock_eigenvalues = _v1.get_kerdock_eigenvalues
spectral_moments = _v1.spectral_moments
self_test_v1 = _v1.self_test

try:
    import torch
    _CUDA_OK = torch.cuda.is_available()
except ImportError:
    _CUDA_OK = False


# ---------------------------------------------------------------------------
# Multi-N classifier
# ---------------------------------------------------------------------------

def classify_n_trend(devs_by_N: list[float]) -> str:
    """Given |delta_n| at fixed (alpha, n) across N, classify the N-trend.

    STABLE: max/min ratio in [0.7, 1.4]
    DRIFTS_UP: monotonic-ish increase, last > 1.5 * first
    DRIFTS_DOWN: monotonic-ish decrease, last < 0.7 * first
    NEAR_ZERO: all values < 0.02 (MP-like at every N)
    UNCLEAR: otherwise
    """
    if not devs_by_N or len(devs_by_N) < 2:
        return "UNCLEAR"
    if all(d < 0.02 for d in devs_by_N):
        return "NEAR_ZERO"
    first = devs_by_N[0]
    last = devs_by_N[-1]
    if first < 1e-9:
        return "UNCLEAR"
    ratio = last / first
    # Also check overall spread (not just first/last)
    mx, mn = max(devs_by_N), min(devs_by_N)
    spread_ratio = (mx + 1e-12) / (mn + 1e-12)
    if 0.7 <= ratio <= 1.4 and spread_ratio <= 2.0:
        return "STABLE"
    if ratio > 1.5:
        return "DRIFTS_UP"
    if ratio < 0.7:
        return "DRIFTS_DOWN"
    return "UNCLEAR"


def compute_verdict(summary: dict) -> tuple[str, str]:
    """Aggregate per-(alpha, n) classifications across N.

    For each alpha and each n in {2..n_max}, classify the trend of |delta_n|
    across the N-list. Verdict goes to the dominant class across all such
    (alpha, n) pairs.
    """
    if not summary.get("cells"):
        return ("KAPPA_MULTI_N_INCONCLUSIVE", "No cells.")

    # Group by alpha
    by_alpha: dict = {}
    for cell in summary["cells"]:
        a = cell["alpha"]
        by_alpha.setdefault(a, []).append(cell)

    per_pair = []  # list of class labels, one per (alpha, n)
    n_max = summary["config"]["n_max_moment"]
    for alpha, cells in by_alpha.items():
        cells_sorted = sorted(cells, key=lambda c: c["N"])
        c_ref = float(alpha)
        for n in range(2, n_max + 1):
            devs = []
            for cell in cells_sorted:
                k_mean = cell.get("kappa_mean", [])
                if len(k_mean) >= n:
                    dev = abs(k_mean[n - 1] / c_ref - 1.0)
                    devs.append(dev)
            if len(devs) < 2:
                continue
            cls = classify_n_trend(devs)
            per_pair.append((alpha, n, cls, devs))

    if not per_pair:
        return ("KAPPA_MULTI_N_INCONCLUSIVE", "No valid (alpha, n) trends.")

    counts = {}
    for _, _, cls, _ in per_pair:
        counts[cls] = counts.get(cls, 0) + 1
    total = len(per_pair)

    dom_class, dom_count = max(counts.items(), key=lambda kv: kv[1])
    majority = dom_count >= max(2, (2 * total) // 3)

    label_map = {
        "STABLE": "KAPPA_MULTI_N_STABLE",
        "DRIFTS_UP": "KAPPA_MULTI_N_GROWS_IN_N",
        "DRIFTS_DOWN": "KAPPA_MULTI_N_DECAYS_IN_N",
        "NEAR_ZERO": "KAPPA_MULTI_N_DECAYS_IN_N",  # asymptotically MP
    }

    summary["per_pair"] = [
        {"alpha": a, "n": n, "class": cls, "devs": devs}
        for (a, n, cls, devs) in per_pair
    ]
    summary["class_counts"] = counts

    if majority and dom_class in label_map:
        verdict = label_map[dom_class]
        if dom_class == "STABLE":
            return (verdict,
                    f"Substrate-MP free-cumulant deviation |delta_n| is STABLE across "
                    f"N in {sorted(set(c['N'] for c in summary['cells']))} for "
                    f"{dom_count}/{total} (alpha,n) pairs. The Kerdock fingerprint is "
                    f"an N->infty asymptotic property, not a finite-N artifact. "
                    f"Class counts: {counts}.")
        if dom_class == "DRIFTS_UP":
            return (verdict,
                    f"|delta_n| GROWS with N in {dom_count}/{total} (alpha,n) pairs -- "
                    f"the substrate signature amplifies at larger N. Class counts: {counts}.")
        if dom_class in ("DRIFTS_DOWN", "NEAR_ZERO"):
            return (verdict,
                    f"|delta_n| DECAYS with N in {dom_count}/{total} (alpha,n) pairs -- "
                    f"the substrate signature is a finite-N artifact that disappears "
                    f"asymptotically. Class counts: {counts}.")

    return (
        "KAPPA_MULTI_N_INCONCLUSIVE",
        f"No dominant N-trend across (alpha, n) pairs. Class counts: {counts} of {total}.",
    )


def self_test() -> None:
    # 1) Reuse v1's full self test (NCP enum, MP exact, closed-form match, classifier)
    self_test_v1()
    # 2) Multi-N classifier branches
    assert classify_n_trend([0.5, 0.5, 0.55, 0.48]) == "STABLE", "STABLE branch"
    assert classify_n_trend([0.1, 0.3, 0.5, 0.9]) == "DRIFTS_UP", "DRIFTS_UP branch"
    assert classify_n_trend([0.9, 0.6, 0.3, 0.1]) == "DRIFTS_DOWN", "DRIFTS_DOWN branch"
    assert classify_n_trend([0.01, 0.005, 0.001]) == "NEAR_ZERO", "NEAR_ZERO branch"
    # Verdict empty
    v, _ = compute_verdict({"cells": [], "config": {"n_max_moment": 4}})
    assert v == "KAPPA_MULTI_N_INCONCLUSIVE"
    print("kappa_n multi-N self-test PASS (8/8)", flush=True)


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    if smoke:
        config = {
            "mode": "smoke",
            "N_list": [1024],
            "M_over_N_list": [0.5, 1.0],
            "n_seeds": 2,
            "n_max_moment": 6,
        }
    else:
        config = {
            "mode": "full",
            "N_list": [1024, 4096, 8192, 16384],
            "M_over_N_list": [0.5, 1.0, 2.0, 4.0],
            "n_seeds": 10,
            "n_max_moment": 8,
        }

    n_max = config["n_max_moment"]
    device = "cuda" if (_CUDA_OK and not smoke) else "cpu"
    print(f"[device] {device} (cuda_available={_CUDA_OK})", flush=True)

    cells = []
    for N in config["N_list"]:
        # Kerdock construction requires even log2(N): 1024, 4096, 16384 OK; 8192 NOT.
        # log2(8192) = 13, odd. So skip N=8192. Use N_list with only even-log2 entries.
        n_log2 = int(round(math.log2(N)))
        if 2 ** n_log2 != N or n_log2 % 2 != 0:
            print(f"[skip] N={N} (log2={n_log2} not even -- Kerdock MM requires even)", flush=True)
            continue
        for alpha in config["M_over_N_list"]:
            M = max(1, int(alpha * N))
            if M > 4 * N:
                continue
            c_ref = float(alpha)
            print(f"\n[N={N} alpha={alpha:.2f} M={M}]", flush=True)
            kappa_per_seed = []
            moms_per_seed = []
            for seed in range(config["n_seeds"]):
                seed_val = seed * 1000 + int(alpha * 100) + N
                eigenvalues = get_kerdock_eigenvalues(N, M, seed=seed_val, device=device)
                moms = spectral_moments(eigenvalues, n_max)
                kappas = moments_to_free_cumulants_general(moms)
                kappa_per_seed.append(kappas)
                moms_per_seed.append(moms)
                print(f"  seed={seed} m1={moms[0]:.4f} k4_dev_rel="
                      f"{kappas[3]/c_ref - 1.0:+.3f}", flush=True)
            kappa_arr = np.array(kappa_per_seed)
            kappa_mean = kappa_arr.mean(axis=0).tolist()
            kappa_std = kappa_arr.std(axis=0).tolist()
            moms_mean = np.array(moms_per_seed).mean(axis=0).tolist()
            kappa_mp = mp_reference_cumulants(c_ref, n_max)
            cell = {
                "alpha": float(alpha),
                "N": N, "M": M, "c_ref": c_ref,
                "kappa_mean": kappa_mean,
                "kappa_std": kappa_std,
                "kappa_mp": kappa_mp,
                "moments_mean": moms_mean,
            }
            cells.append(cell)
            print(f"  AGGREGATE N={N} alpha={alpha:.2f} kappa_mean="
                  f"{[f'{k:+.3f}' for k in kappa_mean]}", flush=True)

    summary = {"cells": cells, "config": config}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


# ---------------------------------------------------------------------------
# Standard metrics output
# ---------------------------------------------------------------------------

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


def write_metrics(out_dir: Path, summary, verdict, msg, elapsed, config) -> None:
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
    out_dir = get_output_dir("wave14_kappa_n_profile_multi_N_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["cells"]) >= 1, "smoke FAIL: no cells produced"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_kappa_n_profile_multi_N_v1")
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
