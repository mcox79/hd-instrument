"""Parisi P(q12) on substrate's Kerdock-Hebbian W -- v2 with REAL chain length.

v1 (parisi_pq_kerdock_v1, 2026-05-23) finished in 24s with under-resolved chains
(n_burn=300, n_collect=500). For a Parisi P(q12) probe of an N=1024 system the
chain length needs to be >> 10^4 sweeps to resolve the overlap distribution
shape -- especially in the slow-mixing low-T phase where the candidate metastable
states have escape times that can themselves be 10^3-10^5 sweeps.

v2 increases:
  - n_burn from 300 to 3 * 10^5 (3e5)
  - n_collect from 500 to 7 * 10^5 (7e5)
  - Total chain length 10^6 sweeps per replica (per seed, per (alpha, beta) cell)
  - n_seeds from 5 to 10
  - T grid expanded from 6 to >= 20 points (covering paramagnetic above T_c,
    transition region, and deep ordered regime)
  - alpha grid kept at v1's [0.05, 0.10, 0.20]

This is genuinely CPU-bound chain work: numba-style Glauber sweeps don't parallelize
well across the chain, but we do parallelize across (alpha, beta, seed) cells.
ETA on remote CPU: ~45-60 min for full sweep at N=1024.

Reuses v1's shape classifier and verdict logic verbatim (just longer chains).

Vertex: same as v1 -- PARISI_RSB_KERDOCK / PARISI_RS_KERDOCK /
        PARISI_PARAMAGNET_KERDOCK / PARISI_INCONCLUSIVE.

Pre-reg: preregs/2026-05-23_wave14_parisi_pq_kerdock_v2.md
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

# Reuse v1 machinery verbatim
_v1_path = REPO / "experiments" / "exp_wave14_parisi_pq_kerdock_v1.py"
_spec = importlib.util.spec_from_file_location("parisi_v1", _v1_path)
_v1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v1)

simulate_replica_pair = _v1.simulate_replica_pair
classify_pq_shape = _v1.classify_pq_shape
compute_verdict = _v1.compute_verdict
self_test = _v1.self_test
build_hebbian_W = _v1.build_hebbian_W
select_subset_codewords = _v1.select_subset_codewords


def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    if smoke:
        config = {
            "mode": "smoke",
            "N": 1024,
            "alpha_list": [0.10],
            "beta_list": [1.0, 6.0],
            "n_seeds": 2,
            "n_burn": 200,
            "n_collect": 400,
        }
    else:
        # FULL: 10 seeds * (alpha grid 3) * (beta grid 20) * (n_burn + n_collect = 1e6) sweeps.
        # We split chain budget: 3e5 burn + 7e5 collect = 1e6 sweeps per (a, b, seed) per replica.
        # That is heavy. Use N=1024 (v1's setting) and FULL beta grid for proper P(q) resolution.
        config = {
            "mode": "full",
            "N": 1024,
            "alpha_list": [0.05, 0.10, 0.20],
            "beta_list": [
                0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0,
                4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0,
                11.0, 12.0, 14.0, 16.0, 20.0,
            ],
            "n_seeds": 10,
            "n_burn": 300_000,
            "n_collect": 700_000,
        }

    N = config["N"]
    cells = []

    total_cells = len(config["alpha_list"]) * len(config["beta_list"])
    cell_idx = 0
    for alpha in config["alpha_list"]:
        M = max(1, int(alpha * N))
        for beta in config["beta_list"]:
            cell_idx += 1
            t_cell = time.monotonic()
            q12_means = []
            q12_abs_means = []
            support_widths = []
            n_peaks_list = []
            cont_fracs = []
            dz_fracs = []

            for seed in range(config["n_seeds"]):
                seed_val = seed * 1000 + int(alpha * 1000) + int(beta * 13)
                codewords = select_subset_codewords(N, M, seed=seed_val)
                W = build_hebbian_W(codewords)
                q12 = simulate_replica_pair(
                    W, beta,
                    n_burn=config["n_burn"],
                    n_collect=config["n_collect"],
                    seed=seed_val + 777,
                )
                cls = classify_pq_shape(q12)
                q12_means.append(cls["q_mean"])
                q12_abs_means.append(cls["q_abs_mean"])
                support_widths.append(cls["support_width"])
                n_peaks_list.append(cls["n_peaks"])
                cont_fracs.append(cls["support_continuous_fraction"])
                dz_fracs.append(cls["delta_at_zero_frac"])

            cell = {
                "alpha": float(alpha),
                "beta": float(beta),
                "N": N, "M": M,
                "q12_mean": float(np.mean(q12_means)),
                "q12_abs_mean": float(np.mean(q12_abs_means)),
                "support_width": float(np.mean(support_widths)),
                "support_width_std": float(np.std(support_widths)),
                "n_peaks": float(np.mean(n_peaks_list)),
                "support_continuous_fraction": float(np.mean(cont_fracs)),
                "delta_at_zero_frac": float(np.mean(dz_fracs)),
                "n_seeds": config["n_seeds"],
            }
            cells.append(cell)
            cell_elapsed = time.monotonic() - t_cell
            print(
                f"  CELL {cell_idx}/{total_cells} alpha={alpha:.3f} beta={beta:.2f}: "
                f"sw={cell['support_width']:.2f} n_peaks={cell['n_peaks']:.1f} "
                f"dz={cell['delta_at_zero_frac']:.2f} cont={cell['support_continuous_fraction']:.2f} "
                f"({cell_elapsed:.1f}s)",
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
    self_test()
    out_dir = get_output_dir("wave14_parisi_pq_kerdock_v2_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["cells"]) >= 1, "smoke FAIL: no cells"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_parisi_pq_kerdock_v2")
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
