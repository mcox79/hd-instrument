"""FREE PROBABILITY: K_max(alpha) formula crossover smoke (B3).

SCIENTIFIC QUESTION (B3):
  Does K_max(alpha) ~ log(1/alpha)/(2*sqrt(alpha)) predict the empirical
  K-hop depth at which Path D retrieval accuracy drops below 50%?
  At alpha=0.10, K_max ~ log(10)/(2*sqrt(0.1)) ~ 2.303/0.632 ~ 3.64.
  Predicted: 3-4 hops before accuracy drops below 50% at alpha=0.10.

PRE-REGISTERED BANDS:
  HARD-PASS: K_max crossover (acc_K < 50%) at alpha=0.10 within +/-1 hop
    of predicted K~3.6 (i.e., K_crossover in {3, 4, 5}) in >= 3/5 seeds.
  HARD-FAIL: K_crossover < 2 OR K_crossover > 8 in majority of seeds.
  MIDDLE: K_crossover in {2} or {6,7,8} (detectable but out of +-1 band).

CALIBRATION NOTE: no prior empirical anchor for K_max(alpha) formula.
  Bands widened per calibration-probe policy (theoretical +-50%).

DESIGN:
  N=4096, alpha=0.10 -> M=410 patterns. K_sweep: [1,2,3,4,5,6,7,8].
  Multi-hop depth-K retrieval: W^K @ k (K applications of W).
  Seeds: [7,17,23,31,41].
  For each seed and each K, measure retrieval accuracy (cosine argmax).

PROT-018: no _n suffix; production N=4096.
PROT-019: timeout >= 14400s.
PROT-020: CPU only.
PROT-021: M-tagged checkpoint keys.

Anchor: free_prob_kmax_formula_v1_n4096
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_free_prob_kmax_formula.md
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_fp_kmax", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key
list_completed_keys = _ck.list_completed_keys

# PROT-018: production N=4096
N_FULL  = 4096
N_SMOKE = 1024
ALPHA   = 0.10
M_FULL  = int(N_FULL * ALPHA)   # 409
M_SMOKE = int(N_SMOKE * ALPHA)  # 102

K_SWEEP = [1, 2, 3, 4, 5, 6, 7, 8]
N_QUERY = 100

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# K_max formula: K_max(alpha) = log(1/alpha) / (2 * sqrt(alpha))
K_MAX_PREDICTED = math.log(1.0 / ALPHA) / (2.0 * math.sqrt(ALPHA))  # ~3.64

# Pre-registered thresholds
HP_K_CROSS_MIN = 3
HP_K_CROSS_MAX = 5   # within +-1 of K_max ~ 3.64 -> {3,4,5}
HF_K_CROSS_LO  = 2   # < 2 hops = fails too fast
HF_K_CROSS_HI  = 8   # > 8 hops = no crossover found
ACC_CROSSOVER   = 0.50  # K_crossover = first K where acc < 0.50


def k_crossover(acc_by_k: Dict[int, float]) -> int:
    """Return first K where acc < ACC_CROSSOVER, or 999 if none in sweep."""
    for k in sorted(acc_by_k.keys()):
        if acc_by_k[k] < ACC_CROSSOVER:
            return k
    return 999  # no crossover found in sweep


def measure_seed(N: int, M: int, K_sweep: List[int],
                 n_query: int, seed: int) -> Dict:
    """Measure multi-hop accuracy at each K for W=W_hebbian at alpha=M/N."""
    rng = np.random.default_rng(seed)
    alpha_actual = M / N

    # Build Hebbian W: W = X^T X / N, X is M x N bipolar
    patterns = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)
    vals = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)
    # Hetero-associative: W = sum_i v_i x_i^T / N
    W = (vals.T @ patterns) / N  # N x N

    # Test queries: use stored keys with tiny noise
    n_q = min(n_query, M)
    q_idx = rng.choice(M, size=n_q, replace=False)
    test_keys = patterns[q_idx] + rng.standard_normal((n_q, N)).astype(np.float32) * 0.05
    test_vals = vals[q_idx]

    acc_by_k: Dict[int, float] = {}
    # Apply W iteratively: retrieved = W @ q, then W @ retrieved, etc.
    current = test_keys.copy()  # n_q x N
    for k in range(1, max(K_sweep) + 1):
        current = current @ W.T  # n_q x N
        if k in K_sweep:
            # Accuracy: cosine argmax over val bank
            sims = current @ test_vals.T  # n_q x n_q
            pred = np.argmax(sims, axis=1)
            acc_by_k[k] = float(np.mean(pred == np.arange(n_q)))

    kx = k_crossover(acc_by_k)
    return {
        "seed": seed,
        "N": N,
        "M": M,
        "alpha": float(alpha_actual),
        "K_max_predicted": float(K_MAX_PREDICTED),
        "K_crossover_empirical": int(kx),
        "crossover_within_band": int(HP_K_CROSS_MIN <= kx <= HP_K_CROSS_MAX),
        "acc_by_k": {str(k): float(v) for k, v in acc_by_k.items()},
        "ok": True,
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("FP_KMAX_INCONCLUSIVE", "no cells")
    ok = [c for c in cells if c.get("ok")]
    if not ok:
        return ("FP_KMAX_INCONCLUSIVE", "all cells failed")

    kxs = [c["K_crossover_empirical"] for c in ok]
    n_in_band = sum(1 for k in kxs if HP_K_CROSS_MIN <= k <= HP_K_CROSS_MAX)
    n_fail_lo = sum(1 for k in kxs if k < HF_K_CROSS_LO)
    n_fail_hi = sum(1 for k in kxs if k > HF_K_CROSS_HI)
    majority = len(ok) // 2 + 1

    detail = (
        f"N={ok[0]['N']} M={ok[0]['M']} alpha={ok[0]['alpha']:.3f} "
        f"K_max_predicted={ok[0]['K_max_predicted']:.2f} "
        f"K_crossovers={kxs} n_in_band={n_in_band}/{len(ok)} "
        f"HP_band=[{HP_K_CROSS_MIN},{HP_K_CROSS_MAX}]"
    )

    if n_fail_lo + n_fail_hi >= majority:
        return ("FP_KMAX_HARD_FAIL",
                f"K_CROSSOVER_OUT_OF_RANGE n_fail={n_fail_lo+n_fail_hi}/{len(ok)}. "
                + detail)
    if n_in_band >= majority:
        return ("FP_KMAX_HARD_PASS",
                f"K_MAX_FORMULA_VALIDATED in_band={n_in_band}/{len(ok)}. " + detail)
    return ("FP_KMAX_MIDDLE_BAND",
            f"PARTIAL: n_in_band={n_in_band}/{len(ok)}. " + detail)


def get_output_dir(default_name: str = "free_prob_kmax_formula_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at smoke scale."""
    # Formula self-test 1: K_max formula at alpha=0.10
    k_max = math.log(1.0 / 0.10) / (2.0 * math.sqrt(0.10))
    assert 3.0 < k_max < 4.5, f"K_max formula out of range: {k_max:.4f}"
    print(f"[selftest] formula-1 K_max(alpha=0.10)={k_max:.4f} in (3.0, 4.5) PASS",
          flush=True)

    # Formula self-test 2: k_crossover returns valid int
    fake_acc = {1: 0.9, 2: 0.8, 3: 0.6, 4: 0.4, 5: 0.2}
    kx = k_crossover(fake_acc)
    assert kx == 4, f"k_crossover should be 4, got {kx}"
    print(f"[selftest] formula-2 k_crossover=4 PASS", flush=True)

    # Formula self-test 3: live smoke at tiny N
    out = measure_seed(256, 25, [1, 2, 3, 4], 30, 42)
    assert out["ok"], f"measure_seed failed"
    assert out["K_crossover_empirical"] > 0 or out["K_crossover_empirical"] == 999, \
        f"crossover out of range: {out['K_crossover_empirical']}"
    assert len(out["acc_by_k"]) >= 1, "acc_by_k empty"
    # At least one K has valid acc in [0,1]
    for k, acc in out["acc_by_k"].items():
        assert 0.0 <= acc <= 1.0, f"acc[{k}]={acc} out of [0,1]"
    print(f"[selftest] formula-3 live smoke N=256 M=25 "
          f"K_crossover={out['K_crossover_empirical']} "
          f"acc_K1={out['acc_by_k'].get('1','n/a')} PASS", flush=True)

    # Formula self-test 4: verdict gates
    fake_hp = [{"ok": True, "N": 4096, "M": 409, "alpha": 0.1,
                "K_max_predicted": 3.64, "K_crossover_empirical": 4,
                "crossover_within_band": 1, "acc_by_k": {"3": 0.6, "4": 0.3}}
               for _ in range(5)]
    v, msg = compute_verdict(fake_hp)
    assert "HARD_PASS" in v, f"HP gate failed: {v}"
    print(f"[selftest] formula-4 HP gate PASS: {v}", flush=True)

    fake_hf = [{"ok": True, "N": 4096, "M": 409, "alpha": 0.1,
                "K_max_predicted": 3.64, "K_crossover_empirical": 1,
                "crossover_within_band": 0, "acc_by_k": {"1": 0.3}}
               for _ in range(5)]
    v, msg = compute_verdict(fake_hf)
    assert "HARD_FAIL" in v, f"HF gate failed: {v}"
    print(f"[selftest] formula-4 HF gate PASS: {v}", flush=True)

    print("[selftest] free_prob_kmax_formula_v1_n4096 ALL PASS", flush=True)


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
    M_cfg  = M_SMOKE if smoke else M_FULL
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    run_config = {"N": N_cfg, "M": M_cfg, "run_mode": "smoke" if smoke else "full"}
    done = set(list_completed_keys(out_dir, run_config=run_config))

    t0 = time.time()
    print(f"[run] free_prob_kmax_formula_v1 smoke={smoke} "
          f"N={N_cfg} M={M_cfg} alpha={ALPHA:.2f} K_max_pred={K_MAX_PREDICTED:.2f} "
          f"K_sweep={K_SWEEP} seeds={seeds} done={len(done)}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"M{M_cfg}_seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body)
                print(f"  [resume] seed={seed} loaded", flush=True)
                continue
        try:
            cell = measure_seed(N_cfg, M_cfg, K_SWEEP, N_QUERY, seed)
            cell["run_mode"] = "smoke" if smoke else "full"
            write_partial_key(out_dir, ck, cell)
            cells.append(cell)
            kxs = cell.get('K_crossover_empirical', 'n/a')
            print(f"  seed={seed} ok={cell.get('ok')} "
                  f"K_crossover={kxs} "
                  f"acc_K3={cell['acc_by_k'].get('3','n/a')} "
                  f"acc_K4={cell['acc_by_k'].get('4','n/a')} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except Exception as e:
            print(f"  seed={seed} FAILED: {e}", flush=True)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor": "free_prob_kmax_formula_v1_n4096",
        "N": N_cfg, "M": M_cfg, "alpha": ALPHA, "smoke": smoke,
        "K_max_predicted": K_MAX_PREDICTED, "K_sweep": K_SWEEP, "seeds": seeds,
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
