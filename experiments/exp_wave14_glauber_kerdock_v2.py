"""D1 Glauber dynamics on Kerdock codeword space -- v2 with finer T + longer chains.

Re-run of v1 after GLAUBER_INCONCLUSIVE at smoke-config FULL (20.7s elapsed,
max_bimodal_score=0.000 indicating chains did not reach the bimodal stationary
P(q) regime). v2 addresses the under-resolution:

  - Finer T grid: 12 beta values densely covering the substrate-internal Hopfield
    transition window (beta in [1.0, 12.0] inclusive, focused on the critical
    region beta ~ 3-8 where AGS theory predicts bimodal retrieval).
  - Longer chains: n_burn=400, n_collect=600 sweeps (4x v1 FULL collect; 13x
    v1 smoke).
  - Sub-critical loading focus: alpha in {0.05, 0.10, 0.20} -- BELOW classical
    AGS critical alpha_c ~ 0.138 so bimodal retrieval is theoretically present
    if Kerdock-Hebbian W supports the same phenomenology.
  - Same synchronous heat-bath update (parallel Peretto 1984) as v1, justified
    in v1 module docstring; equilibrium structure is the same as sequential
    Glauber for symmetric diag-zero W (Hertz-Krogh-Palmer Ch. 4).

Pre-reg: preregs/2026-05-23_wave14_glauber_kerdock_v2.md
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

# Reuse v1 helpers (Kerdock builder, glauber_sweep, bimodality detector, verdict logic)
_v1_path = REPO / "experiments" / "exp_wave14_glauber_kerdock_v1.py"
_spec = importlib.util.spec_from_file_location("glauber_v1", _v1_path)
_v1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v1)

build_hebbian_W = _v1.build_hebbian_W
glauber_sweep = _v1.glauber_sweep
measure_overlap = _v1.measure_overlap
detect_bimodality = _v1.detect_bimodality
compute_verdict = _v1.compute_verdict
self_test_verdict = _v1.self_test_verdict
select_subset_codewords = _v1.select_subset_codewords


def simulate_cell_v2(
    codewords: np.ndarray,
    target_idx: int,
    beta: float,
    n_burn: int,
    n_collect: int,
    seed: int,
) -> dict:
    """Single chain: burn-in then collect P(q) samples. v2 increases chain length
    and uses 10% init noise (closer to target, more sensitive to retrieval basin).
    """
    M, N = codewords.shape
    rng = np.random.default_rng(seed)
    target = codewords[target_idx].astype(np.float64)

    # Lighter init noise (10% bit-flips) -- start IN the retrieval basin so we
    # measure whether the basin is stable under thermal noise rather than whether
    # Glauber recovers from heavy perturbation. This is the "stationary in basin"
    # version of the probe (complementary to v1's "recover from heavy noise").
    mask = rng.random(N) < 0.10
    s = target.copy()
    s[mask] = -s[mask]

    W = build_hebbian_W(codewords)

    for _ in range(n_burn):
        s = glauber_sweep(s, W, beta, rng, n_sweeps=1)

    q_samples = np.empty(n_collect, dtype=np.float64)
    for i in range(n_collect):
        s = glauber_sweep(s, W, beta, rng, n_sweeps=1)
        q_samples[i] = measure_overlap(s, target)

    stats = detect_bimodality(q_samples)
    stats["q_samples"] = q_samples.tolist()
    stats["beta"] = beta
    stats["target_idx"] = int(target_idx)
    stats["seed"] = seed
    return stats


def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    if smoke:
        config = {
            "mode": "smoke",
            "N": 1024,
            "alpha_list": [0.10],
            "beta_list": [2.0, 6.0],
            "n_seeds": 2,
            "n_burn": 50,
            "n_collect": 80,
        }
    else:
        # 12-beta grid: dense around the predicted T_c (beta ~ 3-6 for AGS-like)
        config = {
            "mode": "full",
            "N": 1024,
            "alpha_list": [0.05, 0.10, 0.20],  # sub-critical: alpha_c (AGS) ~ 0.138
            "beta_list": [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0],
            "n_seeds": 5,
            "n_burn": 400,
            "n_collect": 600,
        }

    N = config["N"]
    cells = []

    for alpha in config["alpha_list"]:
        M = max(1, int(alpha * N))
        for beta in config["beta_list"]:
            bimodal_scores = []
            abs_mean_qs = []
            mean_qs = []
            all_q = []
            for seed in range(config["n_seeds"]):
                seed_val = seed * 1000 + int(alpha * 1000) + int(beta * 7)
                codewords = select_subset_codewords(N, M, seed=seed_val)
                target_idx = seed_val % M
                stats = simulate_cell_v2(
                    codewords, target_idx, beta,
                    n_burn=config["n_burn"],
                    n_collect=config["n_collect"],
                    seed=seed_val + 999,
                )
                bimodal_scores.append(stats["bimodal_score"])
                abs_mean_qs.append(stats["abs_mean_q"])
                mean_qs.append(stats["mean_q"])
                all_q.extend(stats["q_samples"])
                print(
                    f"  alpha={alpha:.3f} beta={beta:.2f} seed={seed} "
                    f"mean_q={stats['mean_q']:+.3f} abs_mean={stats['abs_mean_q']:.3f} "
                    f"bimodal={stats['bimodal_score']:.3f}",
                    flush=True,
                )

            cell = {
                "alpha": float(alpha),
                "beta": float(beta),
                "T": 1.0 / float(beta) if beta > 0 else float("inf"),
                "N": N,
                "M": M,
                "bimodal_score": float(np.mean(bimodal_scores)),
                "bimodal_score_std": float(np.std(bimodal_scores)),
                "abs_mean_q": float(np.mean(abs_mean_qs)),
                "abs_mean_q_std": float(np.std(abs_mean_qs)),
                "mean_q": float(np.mean(mean_qs)),
                "n_seeds": config["n_seeds"],
            }
            cells.append(cell)
            print(
                f"  AGGREGATE alpha={alpha:.3f} beta={beta:.2f}: "
                f"bimodal={cell['bimodal_score']:.3f}+-{cell['bimodal_score_std']:.3f} "
                f"abs_mean_q={cell['abs_mean_q']:.3f}+-{cell['abs_mean_q_std']:.3f}",
                flush=True,
            )

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
    self_test_verdict()
    out_dir = get_output_dir("wave14_glauber_kerdock_v2_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["cells"]) >= 1, "smoke FAIL: no cells produced"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test_verdict()
    out_dir = get_output_dir("wave14_glauber_kerdock_v2")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
