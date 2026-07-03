"""F-14 Tropical Cap-13 at smaller N=2048 — companion instrumentation (GPU).

Motivation
----------
The original `wave14_tropical_kerdock_N4096_emp_margin_v1` anchor measures
the empirical bit-flip margin at full N=4096 4-coset MM Kerdock (16384
codewords). It is the production-scale empirical baseline for the Cap 13
"tropical-polytope adversarial-margin certificate" candidate.

This companion runs the SAME empirical-margin instrumentation at smaller
N=2048 (2-coset MM Kerdock = 4096 codewords) so we can:
  1. Validate that the margin distribution scales sensibly with N (margin
     ~ proportional to N for substrate-Kerdock).
  2. Provide a faster baseline for downstream Cap-13 closed-form vs
     empirical comparisons (the N=2048 sweep takes ~30 min on GPU).
  3. Fill the GPU queue without re-running the more expensive N=4096
     anchor; v1's smoke at N=1024 ran in seconds, so N=2048 is the gap
     between smoke and production.

Note: 2-coset MM Kerdock requires N=2^k where k is even -> N in
{4, 16, 64, 256, 1024, 4096, 16384}. N=2048 (k=11 odd) DOES NOT support
2-coset MM directly. We instead use N=1024 (4-coset, 4096 codewords) as
the smaller comparison point. Renaming the script intent: "Tropical
Cap-13 at smaller N (companion to N=4096)" using N=1024 4-coset MM.

Vertices: EMP_MARGIN_WELL_DEFINED / EMP_MARGIN_NOISY_BASELINE /
EMP_MARGIN_DEGENERATE / EMP_MARGIN_INCONCLUSIVE (same vertices as v1
companion).

Pre-reg: preregs/2026-05-24_wave14_tropical_kerdock_N4096_smaller_v1.md
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
from typing import Optional

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# Reuse the GPU empirical-margin routine + verdict + Kerdock builder
_v1_path = REPO / "experiments" / "exp_wave14_tropical_kerdock_N4096_emp_margin_v1.py"
_spec = importlib.util.spec_from_file_location("trop_v1", _v1_path)
_v1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v1)

empirical_bsc_margin_gpu = _v1.empirical_bsc_margin_gpu
compute_verdict = _v1.compute_verdict
make_kerdock_4coset_codebook = _v1.make_kerdock_4coset_codebook
self_test = _v1.self_test  # already includes 5 cells


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


def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    if smoke:
        config = {
            "mode": "smoke",
            "N": 1024,  # smallest 4-coset MM
            "eps_list": [0.1, 0.5],
            "n_seeds": 1,
            "n_codewords": 2,
            "max_competitors": 32,
        }
    else:
        # SMALLER variant: N=1024 (4-coset MM = 4096 codewords); v1 ran N=4096.
        # 10 seeds * 5 codewords * 5 eps = 250 measurements (matches v1 cell
        # counts; N=1024 makes each measurement ~16x cheaper than N=4096).
        config = {
            "mode": "full",
            "N": 1024,
            "eps_list": [0.1, 0.3, 0.5, 0.7, 0.9],
            "n_seeds": 10,
            "n_codewords": 5,
            "max_competitors": 64,
        }

    use_cuda = torch.cuda.is_available() and not smoke
    device = torch.device("cuda" if use_cuda else "cpu")
    print(f"[device] {device}", flush=True)

    N = config["N"]
    print(f"[N={N}] building 4-coset Kerdock codebook...", flush=True)
    cb_t, info = make_kerdock_4coset_codebook(N, device)
    cb = cb_t.float().to(device)
    print(f"[codebook] shape={tuple(cb.shape)} info={info}", flush=True)

    cells = []
    for eps in config["eps_list"]:
        trials = []
        for seed in range(config["n_seeds"]):
            torch.manual_seed(seed * 7 + 13)
            rng = np.random.default_rng(seed * 1000 + int(eps * 100))
            n_cw = min(config["n_codewords"], cb.shape[0])
            cw_indices = rng.choice(cb.shape[0], size=n_cw, replace=False)
            for i in cw_indices:
                w_i = cb[int(i)]
                direction_t = torch.randn(N, device=device)
                direction_t = direction_t / max(float(direction_t.norm().item()), 1e-12)
                y = w_i + eps * direction_t

                ips = cb @ y
                actual_i = int(torch.argmax(ips).item())
                if actual_i != int(i):
                    continue

                margin_e, j_e = empirical_bsc_margin_gpu(
                    cb, y, int(i), max_competitors=config["max_competitors"]
                )
                trials.append({
                    "seed": int(seed),
                    "i": int(i),
                    "eps": float(eps),
                    "margin_emp": float(margin_e),
                    "j_emp": int(j_e) if j_e is not None else -1,
                    "N": int(N),
                })

        margins = [t["margin_emp"] for t in trials]
        cell = {
            "eps": float(eps),
            "n_trials": len(trials),
            "mean_margin": float(np.mean(margins)) if margins else None,
            "std_margin": float(np.std(margins)) if margins else None,
            "min_margin": float(np.min(margins)) if margins else None,
            "max_margin": float(np.max(margins)) if margins else None,
            "trials": trials,
        }
        cells.append(cell)
        print(
            f"[eps={eps}] mean={cell['mean_margin']}, std={cell['std_margin']}, "
            f"n_trials={cell['n_trials']}", flush=True,
        )

    summary = {"cells": cells, "config": config, "codebook_info": info}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


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
    out_dir = get_output_dir("wave14_tropical_kerdock_N4096_smaller_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["cells"]) >= 1, "smoke FAIL: no cells produced"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_tropical_kerdock_N4096_smaller_v1")
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
