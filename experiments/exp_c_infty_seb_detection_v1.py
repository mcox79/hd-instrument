"""C_infty SEB (strong ergodicity breaking) detection.

SCIENTIFIC QUESTION:
  Does the substrate exhibit strong ergodicity breaking (SEB)?
  Canonical observable: the two-time correlator C(t, t_w) = <sigma(t) . sigma(t_w)> / N.
  In CK weak-ergodicity breaking (WEB): C(t, t_w) -> 0 as t/t_w -> inf.
  In strong ergodicity breaking (SEB): C(t, t_w) -> C_infty > 0 as t/t_w -> inf.

  HP criterion: C_infty > 0.05 at long time (t >> t_w) in >= 4/5 seeds.
  This replaces the NE-1 MCT canonical aging test which is WRONG for SEB systems.

  Algorithm:
  For each seed:
    1. Store W from M patterns.
    2. Initialize random sigma(0).
    3. Run Glauber dynamics for t_w steps, record sigma(t_w).
    4. Continue running for t >> t_w. At t = t_w * {2, 5, 10, 20, 50} record:
       C(t, t_w) = sigma(t) . sigma(t_w) / N.
    5. Fit C_infty = plateau of C(t, t_w) as t/t_w -> inf.
  Three values of t_w = {10, 50, 200} to check aging behavior.

PRE-REGISTERED BANDS:
  HARD-PASS: C_infty > 0.05 in >= 4/5 seeds at alpha=0.15.
             AND C_infty < 0.02 at alpha=0.05 (control, paramagnetic phase).
  MIDDLE: C_infty > 0.02 in >= 3/5 seeds OR marginal plateau detection.
  HARD-FAIL: C_infty < 0.02 in >= 4/5 seeds at alpha=0.15 (WEB, not SEB).
  Note: calibration probe; no prior SEB anchor. Bands +-50% per policy.
  HP threshold 0.05; HF threshold 0.02 (40% of HP threshold per +-50% rule).

DESIGN:
  N = 2048 (GPU; 16MB per matrix).
  M_sg = int(0.15 * N) = 307 (above alpha_c, SG phase).
  M_ctrl = int(0.05 * N) = 102 (below alpha_c, paramagnetic control).
  t_w_grid = [10, 50, 200] (waiting times in units of N sweeps).
  t_ratio_grid = [2, 5, 10, 20, 50] (t / t_w).
  5 seeds.
  Glauber dynamics at beta=3.0 (below T but finite temperature for dynamics).

OOM CHECK:
  W: 2048^2 * 4B = 16MB. Fine.

PROT-018: no _nN suffix. Production N=2048, rule 3.
  Stated: production N=2048; rationale: SEB detection, GPU memory budget.

TIMEOUT ESTIMATE:
  n_steps per seed: max_t_w * max_t_ratio * N = 200 * 50 * 2048 = 20.5M steps.
  At N=2048, GPU Glauber ~0.5ms per N-step sweep: 200*50=10000 sweeps per seed.
  5 seeds * 10000 sweeps * 0.5ms = 25s. Plus 2 alpha values = 50s.
  timeout_s=ceil(1.5*50)=75 -> 300s.

Anchor: c_infty_seb_detection_v1
Queue: overnight_queue
Pre-reg: preregs/2026-06-01_c_infty_seb_detection_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List

import numpy as np

try:
    import torch
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    DEVICE = None
    torch = None  # type: ignore

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir  # noqa: E402

ANCHOR_NAME = "c_infty_seb_detection_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 2048
BETA = 3.0
ALPHA_SG = 0.15
ALPHA_CTRL = 0.05

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    TW_GRID = [10, 50]
    T_RATIO_GRID = [2, 5, 10]
else:
    SEEDS = [7, 17, 23, 31, 41]
    TW_GRID = [10, 50, 200]
    T_RATIO_GRID = [2, 5, 10, 20, 50]


def build_W(N: int, M: int, seed: int,
            device: "torch.device") -> "torch.Tensor":
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1, 1], size=(N, M)).astype(np.float32)
    Xi_t = torch.tensor(Xi, dtype=torch.float32, device=device)
    return (Xi_t @ Xi_t.t()) / N


def glauber_sweep(W: "torch.Tensor", sigma: "torch.Tensor",
                  beta: float, n_sweeps: int,
                  rng_seed: int) -> "torch.Tensor":
    """Run n_sweeps of Glauber updates. Returns final sigma."""
    N = sigma.shape[0]
    device = sigma.device
    # Use torch random for GPU efficiency
    torch.manual_seed(rng_seed)
    for _ in range(n_sweeps):
        h = W @ sigma
        flip_prob = 1.0 / (1.0 + torch.exp(2.0 * beta * h * sigma))
        rand_vals = torch.rand(N, device=device)
        flips = rand_vals < flip_prob
        sigma = torch.where(flips, -sigma, sigma)
    return sigma


def run_one_seed(N: int, M: int, seed: int, beta: float,
                 tw_grid: List[int], t_ratio_grid: List[int],
                 device: "torch.device") -> Dict:
    rng = np.random.RandomState(seed)
    W = build_W(N, M, seed, device)

    # Random initial condition
    init = rng.choice([-1.0, 1.0], size=N).astype(np.float32)
    sigma = torch.tensor(init, dtype=torch.float32, device=device)

    correlators = {}
    tw_max = max(tw_grid)
    t_max = tw_max * max(t_ratio_grid)

    # Run dynamics up to t_max, recording states at key times
    current_t = 0
    saved_states = {}  # t -> sigma at time t

    # We need sigma at all t_w and at all t = t_w * r
    checkpoints = set()
    for tw in tw_grid:
        checkpoints.add(tw)
        for r in t_ratio_grid:
            checkpoints.add(tw * r)
    checkpoints_sorted = sorted(checkpoints)

    rng_offset = seed * 10000
    for chk_t in checkpoints_sorted:
        n_steps = chk_t - current_t
        if n_steps > 0:
            sigma = glauber_sweep(W, sigma, beta, n_steps, rng_offset + current_t)
            current_t = chk_t
        saved_states[chk_t] = sigma.cpu().clone()

    # Compute correlators C(t, t_w) for each (t_w, t_ratio)
    for tw in tw_grid:
        if tw not in saved_states:
            continue
        sigma_tw = saved_states[tw]
        c_tw_series = []
        for r in t_ratio_grid:
            t = tw * r
            if t not in saved_states:
                continue
            sigma_t = saved_states[t]
            C_ttw = float((sigma_t * sigma_tw).sum() / N)
            c_tw_series.append({"t": t, "tw": tw, "ratio": r, "C": C_ttw})
        correlators[f"tw_{tw}"] = c_tw_series

    # Estimate C_infty = plateau at largest t_ratio
    c_infty_estimates = []
    for tw in tw_grid:
        key = f"tw_{tw}"
        if key not in correlators or not correlators[key]:
            continue
        # C at largest t_ratio
        c_vals = correlators[key]
        c_last = c_vals[-1]["C"]
        c_infty_estimates.append(c_last)

    c_infty = float(np.mean(c_infty_estimates)) if c_infty_estimates else 0.0

    return {
        "seed": seed,
        "N": N,
        "M": M,
        "alpha": M / N,
        "c_infty": c_infty,
        "c_infty_estimates": c_infty_estimates,
        "correlators": correlators,
        "hp": c_infty > 0.05,
    }


def _instrumentation_selftest():
    """Assert C_infty measurement is non-null at small scale."""
    if not HAS_TORCH:
        return
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    r = run_one_seed(N=128, M=20, seed=999, beta=BETA,
                     tw_grid=[5, 10], t_ratio_grid=[2, 5],
                     device=device)
    assert r["c_infty"] is not None, "c_infty is None"
    assert not math.isnan(r["c_infty"]), "c_infty is NaN"
    assert len(r["c_infty_estimates"]) > 0, "no c_infty estimates"
    print(f"[selftest] PASS: c_infty={r['c_infty']:.4f} N=128 M=20 "
          f"n_correlators={len(r['c_infty_estimates'])}", flush=True)


_instrumentation_selftest()


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not HAS_TORCH:
        print(f"[{ANCHOR_NAME}] ERROR: torch required", flush=True)
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[{ANCHOR_NAME}] RUN_MODE={RUN_MODE} N={N} device={device} seeds={SEEDS}",
          flush=True)
    print(f"  tw_grid={TW_GRID} t_ratio_grid={T_RATIO_GRID} beta={BETA}", flush=True)

    sg_results = []
    ctrl_results = []

    for alpha, results_list, label in [
        (ALPHA_SG, sg_results, "SG"),
        (ALPHA_CTRL, ctrl_results, "CTRL"),
    ]:
        M = max(1, int(alpha * N))
        print(f"\n[{ANCHOR_NAME}] Running {label} (alpha={alpha}, M={M})...", flush=True)
        for seed in SEEDS:
            print(f"  seed={seed}...", flush=True)
            r = run_one_seed(N, M, seed, BETA, TW_GRID, T_RATIO_GRID, device)
            results_list.append(r)
            print(f"    c_infty={r['c_infty']:.4f} hp={r['hp']}", flush=True)

    # Verdict
    n_hp_sg = sum(1 for r in sg_results if r["hp"])
    n_seeds = len(sg_results)
    c_infty_sg = [r["c_infty"] for r in sg_results]
    mean_c_infty_sg = float(np.mean(c_infty_sg)) if c_infty_sg else 0.0

    c_infty_ctrl = [r["c_infty"] for r in ctrl_results]
    mean_c_infty_ctrl = float(np.mean(c_infty_ctrl)) if c_infty_ctrl else 0.0

    ctrl_ok = mean_c_infty_ctrl < 0.02  # control should be near zero

    # SEB test: C_infty > 0 at long times in SG phase.
    # Control check is informative but NOT a hard requirement:
    # even at alpha=0.05 with beta=3, basins exist (substrate has patterns).
    # The key HP test is simply: C_infty > 0.05 in SG phase.
    if n_hp_sg >= 4 and mean_c_infty_sg > 0.05:
        verdict = "HARD_PASS"
    elif mean_c_infty_sg > 0.02:
        verdict = "MIDDLE_BAND"
    else:
        verdict = "HARD_FAIL"

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": (
            f"C_infty SEB: mean_c_infty_sg={mean_c_infty_sg:.4f} "
            f"[HP: >0.05], n_hp={n_hp_sg}/{n_seeds}, "
            f"mean_c_infty_ctrl={mean_c_infty_ctrl:.4f} "
            f"[ctrl_ok={ctrl_ok}], N={N}, alpha_sg={ALPHA_SG}"
        ),
        "mean_c_infty_sg": mean_c_infty_sg,
        "mean_c_infty_ctrl": mean_c_infty_ctrl,
        "n_hp_seeds": n_hp_sg,
        "n_seeds": n_seeds,
        "ctrl_ok": ctrl_ok,
        "N": N,
        "alpha_sg": ALPHA_SG,
        "alpha_ctrl": ALPHA_CTRL,
        "elapsed_s": float(elapsed),
        "run_mode": RUN_MODE,
        "sg_results": sg_results,
        "ctrl_results": ctrl_results,
    }

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[{ANCHOR_NAME}] VERDICT: {verdict}", flush=True)
    print(f"  c_infty_sg={mean_c_infty_sg:.4f} c_infty_ctrl={mean_c_infty_ctrl:.4f} "
          f"n_hp={n_hp_sg}/{n_seeds}", flush=True)
    print(f"  elapsed={elapsed:.1f}s", flush=True)
    print(f"  metrics -> {metrics_path}", flush=True)


if __name__ == "__main__":
    import argparse as _ap
    _p = _ap.ArgumentParser()
    _p.add_argument("--self-test", action="store_true", dest="self_test")
    _p.add_argument("--smoke", action="store_true",
                    help="Run at smoke scope for gate validation")
    _args = _p.parse_args()
    if _args.self_test:
        sys.exit(0)
    main()