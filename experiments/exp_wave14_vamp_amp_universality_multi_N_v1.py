"""VAMP-vs-AMP universality contrast on Kerdock at multiple N (scale-stress).

Motivation
----------
v164a v2 VAMP_AMP_CONTRAST_PASS at N=4096 promoted the row "VAMP-on-Kerdock
holds where AMP fails." The next step is to stress-test that contrast across
N to confirm it is an asymptotic statement, not a single-N coincidence. If
the contrast is the asymptotic substrate-product story, the VAMP-close rate
should remain >= 2/3 and AMP-close rate <= 1/3 at every N tested.

This experiment sweeps N in {1024, 4096, 16384} with 10 seeds and alpha in
{0.5, 1, 2, 4} per N. The N=16384 cell requires t=7 primitive polynomial
support (now added to kerdock builder). N=8192 is skipped (odd log2; Kerdock
MM requires even log2(N)).

Approach
--------
Reuses v1's get_kerdock_svd, run_vamp, run_amp, vamp_se_spectrum, amp_se_scalar,
and compute_verdict for per-cell classification. Aggregates by N and emits a
multi-N classifier on top.

ETA
---
At N=16384 alpha=4 the SVD of a 65536x16384 matrix dominates -- ~3-4 min per
seed even on GPU. 10 seeds at the upper cell alone = ~30 min. Across 4 alpha,
3 N, 10 seeds total = ~120 cells but with most of the budget at the larger N.
Expected wallclock: ~45-60 min on GPU.

Vertex
------
VAMP_AMP_CONTRAST_HOLDS_AT_SCALE -- contrast PASS in >= 2/3 N
VAMP_AMP_CONTRAST_BREAKS_AT_SCALE -- contrast fails at large N (substrate
    falls outside VAMP class as N grows)
VAMP_AMP_BOTH_MATCH_AT_SCALE -- both work at large N (asymptotic SE recovers)
VAMP_AMP_MULTI_N_INCONCLUSIVE

Pre-reg: preregs/2026-05-23_wave14_vamp_amp_universality_multi_N_v1.md
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

_v1_path = REPO / "experiments" / "exp_wave14_vamp_amp_universality_contrast_v1.py"
_spec = importlib.util.spec_from_file_location("vamp_amp_v1", _v1_path)
_v1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v1)

get_kerdock_svd = _v1.get_kerdock_svd
run_vamp = _v1.run_vamp
run_amp = _v1.run_amp
vamp_se_spectrum = _v1.vamp_se_spectrum
amp_se_scalar = _v1.amp_se_scalar
compute_verdict_v1 = _v1.compute_verdict
self_test_v1 = _v1.self_test

try:
    import torch
    _CUDA_OK = torch.cuda.is_available()
except ImportError:
    _CUDA_OK = False


def classify_per_N(cells_at_N: list[dict]) -> str:
    """Run v1's verdict classifier on the slice of cells at one N."""
    summary = {"cells": cells_at_N}
    v, _ = compute_verdict_v1(summary)
    # Map to short tokens
    if v == "VAMP_AMP_CONTRAST_PASS":
        return "CONTRAST_PASS"
    if v == "VAMP_AMP_BOTH_MATCH":
        return "BOTH_MATCH"
    if v == "VAMP_AMP_BOTH_DIVERGE":
        return "BOTH_DIVERGE"
    return "INCONCLUSIVE"


def compute_verdict(summary: dict) -> tuple[str, str]:
    if not summary.get("cells"):
        return ("VAMP_AMP_MULTI_N_INCONCLUSIVE", "No cells.")

    by_N: dict = {}
    for cell in summary["cells"]:
        by_N.setdefault(cell["N"], []).append(cell)
    if len(by_N) < 2:
        return ("VAMP_AMP_MULTI_N_INCONCLUSIVE",
                f"Only {len(by_N)} N-cell(s); need >=2 for multi-N classification.")

    per_N_class = {}
    for N, cells in by_N.items():
        per_N_class[N] = classify_per_N(cells)

    total = len(per_N_class)
    counts: dict = {}
    for cls in per_N_class.values():
        counts[cls] = counts.get(cls, 0) + 1
    summary["per_N_class"] = per_N_class
    summary["class_counts"] = counts

    dom, dom_count = max(counts.items(), key=lambda kv: kv[1])
    majority = dom_count >= max(2, (2 * total) // 3)

    Ns_sorted = sorted(by_N.keys())
    largest_N_cls = per_N_class[Ns_sorted[-1]]

    if majority and dom == "CONTRAST_PASS":
        return (
            "VAMP_AMP_CONTRAST_HOLDS_AT_SCALE",
            f"VAMP-vs-AMP contrast PASS in {dom_count}/{total} N-cells. "
            f"Largest N tested = {Ns_sorted[-1]} with class {largest_N_cls}. "
            f"The substrate-product story (VAMP works on Kerdock; AMP fails) is "
            f"asymptotic, not a single-N artifact. Class counts: {counts}.",
        )
    if dom == "CONTRAST_PASS" and largest_N_cls != "CONTRAST_PASS":
        return (
            "VAMP_AMP_CONTRAST_BREAKS_AT_SCALE",
            f"Contrast PASS at small N but FAILS at large N (N={Ns_sorted[-1]} -> "
            f"{largest_N_cls}). Substrate may fall outside VAMP universality "
            f"asymptotically. Class counts: {counts}.",
        )
    if majority and dom == "BOTH_MATCH":
        return (
            "VAMP_AMP_BOTH_MATCH_AT_SCALE",
            f"BOTH AMP-SE and VAMP-SE track empirics at scale ({dom_count}/{total} N). "
            f"v163 AMP_SE_DIVERGES finding may not survive at N >= 4096. "
            f"Class counts: {counts}.",
        )
    return (
        "VAMP_AMP_MULTI_N_INCONCLUSIVE",
        f"No dominant N-class. {counts} over {total} N.",
    )


def self_test() -> None:
    self_test_v1()
    # Build fake summary: contrast pass at N=1024, contrast pass at N=4096, contrast pass at N=16384
    fake_cell = lambda N, a: {"alpha": a, "N": N, "M": int(a * N),
                              "vamp_se_mse": 0.10, "vamp_emp_mse": 0.11,
                              "amp_se_mse": 0.10, "amp_emp_mse": 0.90}
    cells = [fake_cell(N, a) for N in (1024, 4096, 16384) for a in (0.5, 1.0, 2.0)]
    v, _ = compute_verdict({"cells": cells, "config": {}})
    assert v == "VAMP_AMP_CONTRAST_HOLDS_AT_SCALE", f"expected HOLDS got {v}"
    # Only one N -> inconclusive
    v2, _ = compute_verdict({"cells": [fake_cell(1024, 0.5)], "config": {}})
    assert v2 == "VAMP_AMP_MULTI_N_INCONCLUSIVE", v2
    print("vamp_amp multi-N self-test PASS", flush=True)


def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()
    if smoke:
        config = {
            "mode": "smoke",
            "N_list": [1024],
            "M_over_N_list": [0.5, 1.0],
            "sigma_noise": 0.1,
            "signal_var": 1.0,
            "n_seeds": 2,
            "n_iter": 100,
        }
    else:
        config = {
            "mode": "full",
            "N_list": [1024, 4096, 16384],
            "M_over_N_list": [0.5, 1.0, 2.0, 4.0],
            "sigma_noise": 0.1,
            "signal_var": 1.0,
            "n_seeds": 10,
            "n_iter": 300,
        }
    sigma_sq = config["sigma_noise"] ** 2
    signal_var = config["signal_var"]
    device = "cuda" if (_CUDA_OK and not smoke) else "cpu"
    print(f"[device] {device} (cuda_available={_CUDA_OK})", flush=True)

    cells = []
    for N in config["N_list"]:
        n_log2 = int(round(math.log2(N)))
        if 2 ** n_log2 != N or n_log2 % 2 != 0:
            print(f"[skip] N={N} (log2={n_log2} not even)", flush=True)
            continue
        for alpha in config["M_over_N_list"]:
            M = max(1, int(alpha * N))
            if M > 4 * N:
                continue
            print(f"\n[N={N} alpha={alpha:.2f} M={M}]", flush=True)
            amp_se_mse = amp_se_scalar(alpha, sigma_sq, signal_var)
            vamp_se_vals, vamp_emp_vals, amp_emp_vals = [], [], []
            for seed in range(config["n_seeds"]):
                seed_val = seed * 1000 + int(alpha * 100) + N
                U, s, Vt, A_norm = get_kerdock_svd(N, M, seed=seed_val, device=device)
                vamp_se_mse = vamp_se_spectrum(alpha, sigma_sq, signal_var, s, N, M,
                                               n_iter=config["n_iter"])
                rng_sig = np.random.default_rng(seed_val + 77)
                x_true = rng_sig.standard_normal(N) * math.sqrt(signal_var)
                noise = rng_sig.standard_normal(A_norm.shape[0]) * config["sigma_noise"]
                y = A_norm @ x_true + noise
                vamp_emp_mse = run_vamp(U, s, Vt, y, x_true, signal_var, sigma_sq,
                                        n_iter=config["n_iter"])
                amp_emp_mse = run_amp(A_norm, y, x_true, signal_var, sigma_sq,
                                      n_iter=config["n_iter"])
                vamp_se_vals.append(vamp_se_mse)
                vamp_emp_vals.append(vamp_emp_mse)
                amp_emp_vals.append(amp_emp_mse)
                print(f"  seed={seed} VAMP_SE={vamp_se_mse:.5f} "
                      f"VAMP_emp={vamp_emp_mse:.5f} AMP_SE={amp_se_mse:.5f} "
                      f"AMP_emp={amp_emp_mse:.5f}", flush=True)
            cell = {
                "alpha": float(alpha), "N": N, "M": M,
                "vamp_se_mse": float(np.mean(vamp_se_vals)),
                "vamp_emp_mse": float(np.mean(vamp_emp_vals)),
                "amp_se_mse": float(amp_se_mse),
                "amp_emp_mse": float(np.mean(amp_emp_vals)),
                "vamp_se_std": float(np.std(vamp_se_vals)),
                "vamp_emp_std": float(np.std(vamp_emp_vals)),
                "amp_emp_std": float(np.std(amp_emp_vals)),
            }
            cells.append(cell)

    summary = {"cells": cells, "config": config}
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


def write_metrics(out_dir, summary, verdict, msg, elapsed, config) -> None:
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


def run_smoke() -> None:
    self_test()
    out_dir = get_output_dir("wave14_vamp_amp_universality_multi_N_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["cells"]) >= 1, "smoke FAIL"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_vamp_amp_universality_multi_N_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test(); return 0
    if args.smoke:
        run_smoke(); return 0
    run_main(); return 0


if __name__ == "__main__":
    sys.exit(main())
