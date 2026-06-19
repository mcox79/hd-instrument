"""Alpha_c characterization at LARGER N to test finite-size scaling.

wave14m_alpha_c measured alpha_c=0.153 at N=4096 (slope=1.45 super-linear).
Theory (AGS): asymptotic alpha_c=0.138, finite-N corrections scale ~ 1/sqrt(N).

This extends to N in {8192, 16384, 32768} on CPU (matmul-light, more sequential).
If 1/sqrt(N) correction holds: 0.153 at N=4096 -> ~0.146 at N=16384 -> 0.142 at N=32768.

Pre-reg: preregs/2026-05-20_wave14cpu_alpha_c_extended.md
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

import torch


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    repo_root = Path(__file__).resolve().parent.parent
    out = repo_root / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    if not all(k in d for k in required):
        raise ValueError("missing")
    if not d.get("verdict") or not d.get("verdict_msg"):
        raise ValueError("empty")


def compute_verdict(summary: dict) -> tuple[str, str]:
    rows = summary.get("per_N", [])
    if not rows:
        return ("EXT_ALPHAC_INCONCLUSIVE", "No data.")
    found = [(p["N"], p["alpha_c"]) for p in rows if p["alpha_c"] is not None]
    if not found:
        return ("EXT_ALPHAC_INCONCLUSIVE", "No K* found at any N.")
    last_N, last_alpha = found[-1]
    if last_alpha is None:
        return ("EXT_ALPHAC_INCONCLUSIVE",
                f"K* not found at largest N={last_N}.")
    # AGS asymptote: 0.138; finite-N correction empirically ~1.0/sqrt(N)
    # (wave14m at N=4096 gave alpha_c=0.153, deviation 0.015 = 1/sqrt(4096))
    deviation = last_alpha - 0.138
    expected_correction = 1.0 / math.sqrt(last_N)
    if abs(deviation) < expected_correction * 2:
        return ("EXT_ALPHAC_AGS_CONSISTENT",
                f"alpha_c={last_alpha:.4f} at N={last_N}. Deviation from AGS 0.138 is "
                f"{deviation:+.4f}, within 2x expected ~1/sqrt(N) correction "
                f"({expected_correction:.4f}). Substrate is canonical AGS Hopfield "
                f"with finite-N corrections. Spin-glass theory applies directly.")
    if last_alpha > 0.20:
        return ("EXT_ALPHAC_NOT_AGS",
                f"alpha_c={last_alpha:.4f} at N={last_N} - too high for AGS regime. "
                f"Substrate may not be canonical Hopfield.")
    return ("EXT_ALPHAC_DEVIATES",
            f"alpha_c={last_alpha:.4f} at N={last_N}. Deviation from AGS 0.138 "
            f"is {deviation:+.4f}, larger than 2x finite-N estimate ({expected_correction:.4f}). "
            f"Substrate has structural difference from canonical AGS.")


def self_test_verdict() -> None:
    cases = [
        ({"per_N": [{"N": 16384, "alpha_c": 0.140}]}, "EXT_ALPHAC_AGS_CONSISTENT"),
        ({"per_N": [{"N": 16384, "alpha_c": 0.25}]}, "EXT_ALPHAC_NOT_AGS"),
        ({"per_N": [{"N": 16384, "alpha_c": 0.180}]}, "EXT_ALPHAC_DEVIATES"),
        ({"per_N": []}, "EXT_ALPHAC_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: {actual} != {expected} for {s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def measure_recovery(N, K, n_trials, gen, device, M=16384):
    if M < 2 * K:
        return 0.0
    total = 0.0
    for _ in range(n_trials):
        codebook = 2.0 * (torch.rand((M, N), generator=gen) > 0.5).float() - 1.0
        codebook = codebook.to(device)
        bundle = codebook[:K].sum(dim=0)
        bundle = torch.sign(bundle)
        bundle = torch.where(bundle == 0, torch.ones_like(bundle), bundle)
        scores = codebook @ bundle
        top_k = torch.topk(scores, K).indices.tolist()
        recovered = sum(1 for i in top_k if i < K)
        total += recovered / K
    return total / n_trials


def find_k_star(N, K_grid, seeds, n_trials, device, M=16384, verbose=True):
    rows = []
    for K in K_grid:
        recs = []
        for seed in seeds:
            gen = torch.Generator().manual_seed(seed + 1000 * K + 7919 * N)
            recs.append(measure_recovery(N, K, n_trials, gen, device, M))
        m = sum(recs) / len(recs)
        rows.append({"K": K, "K_over_N": K / N, "mean_recovery": m})
        if verbose:
            print(f"    N={N} K={K:6d} K/N={K/N:.3f}  recovery={m:.3f}", flush=True)
    k_star = None
    for i in range(len(rows) - 1):
        a, b = rows[i], rows[i+1]
        if a["mean_recovery"] >= 0.5 >= b["mean_recovery"]:
            if a["mean_recovery"] == b["mean_recovery"]:
                k_star = float(a["K"])
            else:
                frac = (a["mean_recovery"] - 0.5) / (a["mean_recovery"] - b["mean_recovery"])
                k_star = float(a["K"] + frac * (b["K"] - a["K"]))
            break
    return k_star, rows


def main(smoke: bool = False) -> None:
    self_test_verdict()
    device = torch.device("cpu")  # CPU runner
    if smoke:
        config = {"mode": "smoke", "N_list": [512, 1024],
                  "K_factor_grid": [0.05, 0.10, 0.20, 0.30, 0.40],
                  "seeds": [17], "n_trials": 3, "M": 4096}
    else:
        config = {"mode": "full", "N_list": [8192, 16384],
                  "K_factor_grid": [0.05, 0.08, 0.10, 0.13, 0.16, 0.20, 0.25, 0.30, 0.40],
                  "seeds": [17, 23, 31], "n_trials": 15, "M": 32768}
    print(f"wave14cpu_alpha_c_extended. mode={config['mode']} device={device}", flush=True)

    t0 = time.monotonic()
    per_N = []
    for N in config["N_list"]:
        K_grid = sorted({max(2, int(round(N * f))) for f in config["K_factor_grid"]})
        # M must be at least 2*K_max
        M = max(config["M"], 2 * max(K_grid))
        print(f"  N={N} K_grid={K_grid} M={M}", flush=True)
        k_star, rows = find_k_star(N, K_grid, config["seeds"], config["n_trials"],
                                     device, M=M)
        alpha_c = (k_star / N) if k_star else None
        per_N.append({"N": N, "K_grid": K_grid, "k_star": k_star, "alpha_c": alpha_c,
                       "sweep": rows})
        print(f"  -> alpha_c = {alpha_c}", flush=True)
    elapsed = time.monotonic() - t0

    summary = {"per_N": per_N}
    verdict, msg = compute_verdict(summary)
    print(f"\n=== {verdict} ===\n{msg}", flush=True)
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "config": config, "device": str(device),
               "per_N": per_N, "summary": summary}
    validate_metrics(metrics)
    out_dir = get_output_dir("wave14cpu_alpha_c_extended")
    tmp = (out_dir / "metrics.json").with_suffix(".tmp")
    tmp.write_text(json.dumps(metrics, indent=2))
    os.replace(tmp, out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test_verdict()
        sys.exit(0)
    main(smoke="--smoke" in sys.argv)
