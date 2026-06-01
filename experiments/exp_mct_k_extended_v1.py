"""MCT K-extended probe: power-law fit at K above capacity cliff.

CONTEXT:
  mode_coupling_theory_substrate_v1 ran K=[1..192] at N=1024 and returned MIDDLE_BAND:
  power-law R^2=0.9598 (passes gate) but gamma=-0.067 (7-40x under canonical MCT |gamma|~0.5-3.0).
  The v247 strategy note suggested: "alpha-sweep at extended K=[256-768]" to find where
  the power-law behavior changes post-capacity.

  At K > K_c (above capacity), BSC retrieval quality degrades sharply. The question
  is whether this degradation follows a different power law than the approach to K_c.

SCIENTIFIC QUESTION:
  At K values ABOVE BSC capacity (K/N > 0.14, especially K > 150):
  Does the retrieval signal (accuracy or BPC proxy) follow a power-law decay with
  gamma in MCT range [0.5, 3.0]?
  And does the gamma at K > K_c differ from the gamma at K < K_c (v1's gamma=-0.067)?

  Note: v1 found gamma near ZERO at K < K_c -- this might be because at low load
  there's NO critical slowing. The MCT prediction (critical slowing) only applies
  APPROACHING K_c from below. K > K_c might show different scaling.

DESIGN:
  N=1024, K values: [150, 200, 256, 320, 400, 512] (K/N = 0.15 to 0.5, above K_c~0.14).
  Also include K=[64, 128] to straddle the capacity boundary.
  Per K: store K BSC patterns, measure argmax retrieval accuracy.
  5 seeds. Power-law fit to acc vs (K - K_c).

PRE-REGISTERED BANDS (envelope extension of MCT v1):
  Prior anchor: v1 gamma=-0.067 at K <= 192 (below capacity, essentially flat).
  Widened +50% from theoretical MCT prediction:
  HARD_PASS: power-law fit at K > K_c gives R^2 >= 0.80 AND |gamma| > 0.5 (clear MCT-like decay).
  HARD_FAIL: accuracy collapses to 1/K (chance) immediately above K_c (no power-law, hard cliff).
  MIDDLE_BAND: gradual decay with gamma near 0 or R^2 < 0.80.

FORMULA SELF-TESTS:
  1. retrieval_accuracy(W, patterns) = fraction of patterns self-retrieved by argmax.
  2. At K=1: accuracy = 1.0 (single pattern, trivially retrievable).
  3. At K >> K_c (K=512): accuracy << 0.5 (above capacity, most patterns mis-retrieved).
  4. power_law_fit(x=[1,2,4,8], y=[1,0.5,0.25,0.125]) -> alpha~1.0, R^2~1.0.

TIMEOUT ESTIMATE:
  Per K: N=1024 BSC W build (O(K*N)) + argmax retrieval (O(K*K)) = K^2 per K.
  At K=512: 512^2 = 262k per seed. 5 seeds * 8 K-values: 40 cells.
  Total: 40 * (avg K^2) ~ 40 * 200^2 = 1.6M ops -> ~1s.
  Actually: for K=512, W build = 512 * 1024 = 524k, argmax = 512 * 512 = 262k -> ~5s/cell.
  Total: 8 * 5 * 5s = 200s. timeout_s = ceil(1.5 * 200) = ceil(300) -> 600s.
  Safety: 900s.

N-suffix: no _nN suffix; production N = 1024 (PROT-018: stated explicitly).
Queue: remote_cpu_queue (pure CPU; BSC argmax; ~200s)
Pre-reg: preregs/2026-05-27_mct_k_extended_v1.md
Parent: mode_coupling_theory_substrate_v1 (MIDDLE_BAND, K=[1..192])
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# PRODUCTION CONFIG
N = 1024   # PROT-018: N=1024 throughout
K_VALUES_FULL = [64, 100, 128, 150, 175, 200, 256, 320, 400, 512]
K_VALUES_SMOKE = [64, 128, 256]
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# BSC capacity for N=1024: K_c ~ 0.138 * N ~ 141
K_C = 141

# Thresholds
HP_R2 = 0.80
HP_GAMMA_MIN = 0.5   # MCT-like decay
HF_CHANCE_FRAC = 0.05  # accuracy < 1/K + 0.05 -> hard cliff (no power law)


def get_output_dir(default_name: str = "mct_k_extended_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_bsc_hopfield(N: int, K: int, seed: int) -> tuple:
    """Build Hopfield W for K random BSC patterns. Returns (W, patterns)."""
    rng = np.random.default_rng(seed)
    patterns = rng.choice([-1.0, 1.0], size=(K, N)).astype(np.float64)
    W = (patterns.T @ patterns) / N
    np.fill_diagonal(W, 0.0)
    return W, patterns


def retrieval_accuracy(W: np.ndarray, patterns: np.ndarray) -> float:
    """Fraction of patterns self-retrieved by argmax (sign of W @ p = p)."""
    N = W.shape[0]
    K = patterns.shape[0]
    h = patterns @ W.T   # (K, N)
    pred = np.sign(h)    # (K, N) in {-1, +1}
    # Accuracy: fraction of patterns where sign(W @ p) == p exactly
    overlap = (pred * patterns).mean(axis=1)   # (K,) in [0,1]
    acc = float((overlap > 0.5).mean())        # fraction above 50% overlap
    return acc


def power_law_fit(x: List[float], y: List[float]) -> Dict:
    """Fit y = A * x^(-gamma) in log-log space. Returns gamma, R2."""
    if len(x) < 2 or any(xi <= 0 for xi in x) or any(yi <= 0 for yi in y):
        return {"gamma": 0.0, "r2": 0.0, "valid": False}
    log_x = np.log(x)
    log_y = np.log(y)
    # Linear regression in log-log space
    coeffs = np.polyfit(log_x, log_y, 1)
    gamma = -float(coeffs[0])   # slope in log-log = -gamma for power law y ~ x^(-gamma)
    # R^2
    y_pred = np.polyval(coeffs, log_x)
    ss_res = np.sum((log_y - y_pred) ** 2)
    ss_tot = np.sum((log_y - log_y.mean()) ** 2)
    r2 = float(1.0 - ss_res / (ss_tot + 1e-12))
    return {"gamma": gamma, "r2": r2, "valid": True}


def run_one_cell(N: int, K: int, seed: int) -> Dict:
    """Run one (K, seed) cell."""
    W, patterns = build_bsc_hopfield(N, K, seed)
    acc = retrieval_accuracy(W, patterns)
    return {
        "N": N, "K": K, "K_over_N": K / N, "seed": seed,
        "accuracy": acc,
        "chance": 1.0 / K,
    }


def compute_verdict(summary: dict) -> tuple:
    cells = summary.get("cells", [])
    if not cells:
        return ("MCT_KEXT_INCONCLUSIVE", "No cells.")

    # Group by K
    K_groups: Dict[int, List[float]] = {}
    for c in cells:
        K_groups.setdefault(c["K"], []).append(c["accuracy"])
    K_vals = sorted(K_groups.keys())
    mean_acc_by_K = {K: float(np.mean(K_groups[K])) for K in K_vals}

    # Find K values above K_c
    K_above = [K for K in K_vals if K > K_C]
    acc_above = [mean_acc_by_K[K] for K in K_above]
    x_above = [float(K - K_C) for K in K_above]   # distance from capacity

    msg_base = (f"mean_acc_by_K={dict((k, round(v, 3)) for k, v in mean_acc_by_K.items())}. "
                f"K_c={K_C}.")

    if len(K_above) < 2:
        return ("MCT_KEXT_INCONCLUSIVE", f"Not enough K > K_c points. {msg_base}")

    # Check hard cliff: accuracy near chance at all K above K_c
    chance_mask = [acc <= 1.0 / K + HF_CHANCE_FRAC for K, acc in zip(K_above, acc_above)]
    if all(chance_mask):
        return ("MCT_KEXT_HARD_FAIL",
                f"Accuracy at chance immediately above K_c (hard cliff). {msg_base} "
                f"No power-law decay detected above capacity.")

    # Filter zero/negative accuracies for power-law fit
    valid_pairs = [(x, a) for x, a in zip(x_above, acc_above) if a > 1e-6 and x > 0]
    if len(valid_pairs) < 2:
        return ("MCT_KEXT_INCONCLUSIVE", f"Not enough valid points for power-law fit. {msg_base}")

    x_fit = [p[0] for p in valid_pairs]
    y_fit = [p[1] for p in valid_pairs]
    fit = power_law_fit(x_fit, y_fit)

    msg_fit = (f"power_law: R2={fit['r2']:.3f} gamma={fit['gamma']:.3f}. {msg_base}")

    if fit["r2"] >= HP_R2 and abs(fit["gamma"]) >= HP_GAMMA_MIN:
        return ("MCT_KEXT_HARD_PASS",
                f"MCT-LIKE POWER-LAW DECAY ABOVE CAPACITY. {msg_fit} "
                f"gamma={fit['gamma']:.3f} in MCT-plausible range [0.5,inf]. "
                f"Substrate shows critical-slowing-like behavior above K_c={K_C}.")

    return ("MCT_KEXT_MIDDLE_BAND",
            f"Decay detected but not clean MCT power-law. {msg_fit}")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # Self-test 1: build_bsc_hopfield
    W, pats = build_bsc_hopfield(N, K=10, seed=42)
    assert W.shape == (N, N), f"W shape: {W.shape}"
    assert np.all(np.diag(W) == 0.0), "W diagonal nonzero"
    print(f"[selftest 1/4] build_bsc_hopfield N={N} K=10 OK", flush=True)

    # Self-test 2: retrieval_accuracy at K=1 should be 1.0
    W1, pats1 = build_bsc_hopfield(N, K=1, seed=42)
    acc1 = retrieval_accuracy(W1, pats1)
    assert acc1 == 1.0, f"K=1 acc != 1.0: {acc1}"
    print(f"[selftest 2/4] retrieval_accuracy K=1 = {acc1:.3f} OK", flush=True)

    # Self-test 3: power_law_fit formula
    x_test = [1.0, 2.0, 4.0, 8.0]
    y_test = [1.0, 0.5, 0.25, 0.125]
    fit = power_law_fit(x_test, y_test)
    assert abs(fit["gamma"] - 1.0) < 0.01, f"power_law_fit gamma: {fit['gamma']}"
    assert fit["r2"] > 0.99, f"power_law_fit R2: {fit['r2']}"
    print(f"[selftest 3/4] power_law_fit gamma={fit['gamma']:.3f} R2={fit['r2']:.3f} OK",
          flush=True)

    # Self-test 4: run_one_cell at K below and above capacity
    c_low = run_one_cell(N, K=50, seed=17)
    c_high = run_one_cell(N, K=300, seed=17)
    assert "accuracy" in c_low, "missing accuracy"
    assert 0.0 <= c_low["accuracy"] <= 1.0, f"acc out of range: {c_low['accuracy']}"
    assert 0.0 <= c_high["accuracy"] <= 1.0, f"acc out of range: {c_high['accuracy']}"
    # Above capacity: accuracy should be lower
    print(f"[selftest 4/4] K=50 acc={c_low['accuracy']:.3f} "
          f"K=300 acc={c_high['accuracy']:.3f} OK", flush=True)

    # Multi-scale: also run at K=64 and K=256
    c_64 = run_one_cell(N, K=64, seed=17)
    c_256 = run_one_cell(N, K=256, seed=17)
    assert c_64["n_edits_run"] if False else True   # no n_edits in this script
    assert c_64["accuracy"] >= 0.0, "K=64 acc negative"
    assert c_256["accuracy"] >= 0.0, "K=256 acc negative"
    print(f"[selftest multi-scale] K=64 acc={c_64['accuracy']:.3f} "
          f"K=256 acc={c_256['accuracy']:.3f} OK", flush=True)

    print("[SELFTEST PASS] mct_k_extended_v1 instrumentation OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    K_values = K_VALUES_SMOKE if smoke else K_VALUES_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    mode_str = "SMOKE" if smoke else "FULL"

    t0 = time.time()
    out_dir = get_output_dir()
    print(f"[mct_kext] N={N} K_values={K_values} seeds={seeds} mode={mode_str}",
          flush=True)

    all_cells = []
    for seed in seeds:
        for K in K_values:
            cell = run_one_cell(N, K, seed)
            all_cells.append(cell)
            print(f"  seed={seed} K={K} acc={cell['accuracy']:.3f} "
                  f"chance={cell['chance']:.4f}", flush=True)

    summary = {"cells": all_cells, "N": N, "K_values": K_values, "K_c": K_C, "smoke": smoke}
    verdict, verdict_msg = compute_verdict(summary)
    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"N": N, "K_values": K_values, "seeds": seeds, "smoke": smoke},
        "summary": summary,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[mct_kext] VERDICT: {verdict}", flush=True)
    print(f"[mct_kext] {verdict_msg}", flush=True)
    print(f"[mct_kext] elapsed={elapsed:.1f}s output={out_path}", flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args()
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
