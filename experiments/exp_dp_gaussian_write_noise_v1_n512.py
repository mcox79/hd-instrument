"""DP Mechanism 1: Gaussian write noise smoke (R2.2).

SCIENTIFIC QUESTION (R2.2):
  At sigma corresponding to epsilon=1 (DP budget), does substrate maintain
  unbinding accuracy >= 95% at N=512? Verifies intrinsic algebraic DP at
  write time is compatible with useful accuracy.

PRE-REGISTERED BANDS:
  HARD-PASS: unbinding accuracy >= 0.95 at sigma corresponding to epsilon=1
    (sigma ~ 0.1 from DP formula at delta=1e-5) in >= 3/5 seeds.
  HARD-FAIL: accuracy < 0.85 at sigma=0.1 in majority of seeds.
  MIDDLE: 0.85 <= accuracy < 0.95.

DP FORMULA (Gaussian mechanism):
  epsilon = sqrt(2*ln(1.25/delta)) * sensitivity / sigma
  sensitivity = 1/N (for L2-normalized patterns / N)
  At epsilon=1, delta=1e-5: sigma = sqrt(2*ln(25000)) / N ~ 4.44/N
  For N=512: sigma ~ 0.00867.
  More conservative practical sigma ~ 0.1 (epsilon~0.04 at N=512, but
  allows margin for pattern-level sensitivity).

CALIBRATION NOTE: no prior empirical anchor at sigma=0.1 with N=512.
  Bands widened per calibration-probe policy.

PROT-018: production N=512 (deliberate small design; no _n suffix).
PROT-021: M-tagged checkpoint keys.

Anchor: dp_gaussian_write_noise_v1_n512
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_dp_gaussian_write_noise.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_dp", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key
list_completed_keys = _ck.list_completed_keys

N_FULL  = 512
N_SMOKE = 256
M       = 50
N_QUERY = 100

# DP noise levels to sweep
SIGMA_SWEEP = [0.0, 0.01, 0.05, 0.10, 0.20, 0.50]
# Primary sigma for HP/HF: sigma=0.1 (epsilon~1 practical budget)
SIGMA_PRIMARY = 0.10

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

HP_ACC  = 0.95
HF_ACC  = 0.85


def build_noisy_w(keys: np.ndarray, vals: np.ndarray, N: int,
                  sigma: float, rng: np.random.Generator) -> np.ndarray:
    """Hebbian W with Gaussian noise on each write."""
    W = np.zeros((N, N), dtype=np.float32)
    for i in range(len(keys)):
        # Outer product with DP noise added to the stored pattern
        noisy_val = vals[i] + rng.standard_normal(N).astype(np.float32) * sigma
        W += np.outer(noisy_val, keys[i]) / N
    return W


def measure_accuracy(W: np.ndarray, keys: np.ndarray, vals: np.ndarray,
                     n_query: int, N: int, rng: np.random.Generator) -> float:
    """Retrieval accuracy: cosine argmax over val bank."""
    n_q = min(n_query, len(keys))
    q_idx = rng.choice(len(keys), size=n_q, replace=False)
    queries = keys[q_idx]
    retrieved = queries @ W.T  # n_q x N
    sims = retrieved @ vals.T / N  # n_q x M
    pred = np.argmax(sims, axis=1)
    return float(np.mean(pred == q_idx))


def measure_seed(N: int, M: int, sigma_sweep: List[float],
                 n_query: int, seed: int) -> Dict:
    """Measure accuracy at each sigma level."""
    rng = np.random.default_rng(seed)
    keys = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)
    vals = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)

    acc_by_sigma: Dict[float, float] = {}
    for sigma in sigma_sweep:
        rng_s = np.random.default_rng(seed + int(sigma * 10000))
        W = build_noisy_w(keys, vals, N, sigma, rng_s)
        acc = measure_accuracy(W, keys, vals, n_query, N, rng_s)
        acc_by_sigma[sigma] = acc

    acc_primary = acc_by_sigma.get(SIGMA_PRIMARY, acc_by_sigma.get(0.1, 0.0))

    return {
        "seed": seed,
        "N": N,
        "M": M,
        "sigma_primary": float(SIGMA_PRIMARY),
        "acc_at_sigma_primary": float(acc_primary),
        "acc_by_sigma": {str(k): float(v) for k, v in acc_by_sigma.items()},
        "passes_hp": int(acc_primary >= HP_ACC),
        "ok": True,
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("DP_GAUSS_INCONCLUSIVE", "no cells")
    ok = [c for c in cells if c.get("ok")]
    if not ok:
        return ("DP_GAUSS_INCONCLUSIVE", "all cells failed")

    n_hp = sum(c["passes_hp"] for c in ok)
    n_hf = sum(1 for c in ok if c["acc_at_sigma_primary"] < HF_ACC)
    majority = len(ok) // 2 + 1
    mean_acc = sum(c["acc_at_sigma_primary"] for c in ok) / len(ok)

    detail = (
        f"N={ok[0]['N']} M={ok[0]['M']} sigma={SIGMA_PRIMARY} "
        f"mean_acc={mean_acc:.4f} n_hp={n_hp}/{len(ok)} n_hf={n_hf}/{len(ok)}"
    )

    if n_hf >= majority:
        return ("DP_GAUSS_HARD_FAIL",
                f"ACCURACY_TOO_LOW_AT_DP_SIGMA: acc<{HF_ACC} "
                f"in {n_hf}/{len(ok)} seeds. " + detail)
    if n_hp >= majority:
        return ("DP_GAUSS_HARD_PASS",
                f"DP_COMPATIBLE: acc>={HP_ACC} at sigma={SIGMA_PRIMARY} "
                f"in {n_hp}/{len(ok)} seeds. " + detail)
    return ("DP_GAUSS_MIDDLE_BAND",
            f"PARTIAL: mean_acc={mean_acc:.4f}. " + detail)


def get_output_dir(default_name: str = "dp_gaussian_write_noise_v1_n512") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _instrumentation_selftest() -> None:
    """Assert all metrics non-null/non-sentinel."""
    # Formula self-test 1: DP sigma formula
    # epsilon=1, delta=1e-5 -> sigma_formula
    epsilon = 1.0; delta = 1e-5
    sensitivity = 1.0 / N_FULL  # per-pattern L2 norm contribution
    sigma_dp = math.sqrt(2.0 * math.log(1.25 / delta)) * sensitivity / epsilon
    print(f"[selftest] formula-1 DP sigma at eps=1,delta=1e-5: {sigma_dp:.5f} "
          f"(pattern-level; test sigma={SIGMA_PRIMARY})", flush=True)

    # Formula self-test 2: noisy W still retrieves at sigma=0
    rng = np.random.default_rng(42)
    N_t, M_t = 128, 10
    k_t = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float32)
    v_t = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float32)
    W_t = build_noisy_w(k_t, v_t, N_t, 0.0, rng)
    acc_0 = measure_accuracy(W_t, k_t, v_t, 10, N_t, rng)
    assert acc_0 >= 0.5, f"sigma=0 accuracy too low: {acc_0:.4f}"
    print(f"[selftest] formula-2 sigma=0 acc={acc_0:.4f} >= 0.5 PASS", flush=True)

    # Formula self-test 3: live smoke at small N
    out = measure_seed(N_SMOKE, M, SIGMA_SWEEP, 30, 42)
    assert out["ok"], f"measure_seed failed"
    assert 0.0 <= out["acc_at_sigma_primary"] <= 1.0, \
        f"acc_at_sigma_primary sentinel: {out['acc_at_sigma_primary']}"
    assert len(out["acc_by_sigma"]) >= 1, "acc_by_sigma empty"
    for sig_str, acc in out["acc_by_sigma"].items():
        assert 0.0 <= acc <= 1.0, f"acc[{sig_str}]={acc} out of range"
    print(f"[selftest] formula-3 smoke N={N_SMOKE} M={M} "
          f"acc_sigma0.1={out['acc_at_sigma_primary']:.4f} PASS", flush=True)

    # Formula self-test 4: verdict gates
    fake_hp = [{"ok": True, "N": 512, "M": 50, "sigma_primary": 0.1,
                "acc_at_sigma_primary": 0.97, "passes_hp": 1}
               for _ in range(5)]
    v, _ = compute_verdict(fake_hp)
    assert "HARD_PASS" in v, f"HP gate: {v}"
    fake_hf = [{"ok": True, "N": 512, "M": 50, "sigma_primary": 0.1,
                "acc_at_sigma_primary": 0.80, "passes_hp": 0}
               for _ in range(5)]
    v, _ = compute_verdict(fake_hf)
    assert "HARD_FAIL" in v, f"HF gate: {v}"
    print("[selftest] formula-4 verdict gates PASS", flush=True)

    print("[selftest] dp_gaussian_write_noise_v1_n512 ALL PASS", flush=True)


_instrumentation_selftest()


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    smoke  = args.smoke
    N_cfg  = N_SMOKE if smoke else N_FULL
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    run_config = {"N": N_cfg, "M": M, "run_mode": "smoke" if smoke else "full"}
    done = set(list_completed_keys(out_dir, run_config=run_config))

    t0 = time.time()
    print(f"[run] dp_gaussian_write_noise_v1_n512 smoke={smoke} "
          f"N={N_cfg} M={M} sigma_primary={SIGMA_PRIMARY} "
          f"seeds={seeds} done={len(done)}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"M{M}_seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body)
                print(f"  [resume] seed={seed} loaded", flush=True)
                continue
        try:
            cell = measure_seed(N_cfg, M, SIGMA_SWEEP, N_QUERY, seed)
            cell["run_mode"] = "smoke" if smoke else "full"
            write_partial_key(out_dir, ck, cell)
            cells.append(cell)
            print(f"  seed={seed} ok={cell.get('ok')} "
                  f"acc_sigma0.1={cell.get('acc_at_sigma_primary','n/a'):.4f} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except Exception as e:
            print(f"  seed={seed} FAILED: {e}", flush=True)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor": "dp_gaussian_write_noise_v1_n512",
        "N": N_cfg, "M": M, "smoke": smoke, "seeds": seeds,
        "cells": cells, "verdict": verdict, "verdict_msg": vm,
        "elapsed_s": elapsed,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
