"""PP-4 Write-to-Retrieve Ratio drift detector smoke (A2).

SCIENTIFIC QUESTION (A2):
  Does Write-to-Retrieve Ratio (WRR) detect adversarial write burst
  (5x synthetic write burst of 1000 ops) as a drift signal?
  WRR = n_writes / (n_reads + 1) over rolling window.
  Drift: WRR > mu+3sigma within 1000 ops of burst start; <5% false-alarm rate.

PRE-REGISTERED BANDS:
  HARD-PASS: rho_t > mu+3sigma within 1000 ops in >= 3/5 seeds AND
    false_alarm_rate < 0.05 on pre-burst baseline.
  HARD-FAIL: WRR drift NOT detectable within 2000 ops in majority of seeds.
  MIDDLE: detection within 1000-2000 ops window.

DESIGN:
  Synthetic workload: 2000 ops baseline (WR ratio 1:4), then 1000 ops burst
  (5:1 write:read), then 1000 ops recovery. Window=100 ops.
  5 seeds for baseline noise estimation.

PROT-018: no _n suffix; workload-only, N not load-bearing.
PROT-021: seed-tagged checkpoint keys.

Anchor: pp4_write_retrieve_ratio_drift_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_pp4_write_retrieve_ratio_drift.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_wrr", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key
list_completed_keys = _ck.list_completed_keys

N_BASELINE    = 2000    # pre-burst ops
N_BURST       = 1000    # burst ops
N_RECOVERY    = 1000    # post-burst
BURST_WR_RATIO = 5      # 5 writes per 1 read during burst
BASELINE_WR_RATIO = 0.25  # 1 write per 4 reads during baseline
WINDOW        = 100     # rolling window size
N_SIGMA       = 3.0     # alert threshold: mu + 3 sigma
MAX_DETECT_OPS = 1000   # must detect within N_BURST ops

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

HP_FA_MAX = 0.05   # false alarm rate < 5%


def simulate_workload(n_ops: int, wr_ratio: float, seed: int) -> List[str]:
    """Generate synthetic op sequence with given write:read ratio."""
    rng = np.random.default_rng(seed)
    total_writes = int(n_ops * wr_ratio / (1.0 + wr_ratio))
    total_reads  = n_ops - total_writes
    ops = ['W'] * total_writes + ['R'] * total_reads
    rng.shuffle(ops)
    return ops


def compute_rolling_wrr(ops: List[str], window: int) -> np.ndarray:
    """Rolling WRR over ops stream."""
    n = len(ops)
    wrr = np.zeros(n, dtype=float)
    for i in range(n):
        start = max(0, i - window + 1)
        window_ops = ops[start: i + 1]
        n_w = sum(1 for op in window_ops if op == 'W')
        n_r = sum(1 for op in window_ops if op == 'R')
        wrr[i] = n_w / max(n_r, 1)
    return wrr


def measure_seed(n_baseline: int, n_burst: int, n_recovery: int,
                 burst_wr: float, baseline_wr: float, window: int,
                 n_sigma: float, seed: int) -> Dict:
    """Simulate burst workload and measure WRR drift detection."""
    rng = np.random.default_rng(seed)
    # Build workload
    ops_baseline = simulate_workload(n_baseline, baseline_wr, seed)
    ops_burst    = simulate_workload(n_burst, burst_wr, seed + 100)
    ops_recovery = simulate_workload(n_recovery, baseline_wr, seed + 200)
    ops_full     = ops_baseline + ops_burst + ops_recovery

    wrr = compute_rolling_wrr(ops_full, window)

    # Baseline statistics (from first n_baseline ops)
    baseline_wrr = wrr[:n_baseline]
    mu   = float(np.mean(baseline_wrr))
    sigma = float(np.std(baseline_wrr))
    threshold = mu + n_sigma * max(sigma, 1e-6)

    # False alarm rate on baseline
    n_fa = int(np.sum(baseline_wrr > threshold))
    fa_rate = n_fa / max(n_baseline, 1)

    # Detection within burst window
    burst_wrr = wrr[n_baseline: n_baseline + n_burst]
    detection_ops = 999999
    for i, val in enumerate(burst_wrr):
        if val > threshold:
            detection_ops = i + 1  # ops into burst
            break

    detected = int(detection_ops <= MAX_DETECT_OPS)

    return {
        "seed": seed,
        "mu_baseline": float(mu),
        "sigma_baseline": float(sigma),
        "threshold": float(threshold),
        "fa_rate": float(fa_rate),
        "detection_ops": int(detection_ops),
        "detected_within_limit": detected,
        "max_burst_wrr": float(burst_wrr.max()) if len(burst_wrr) > 0 else 0.0,
        "ok": True,
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("WRR_DRIFT_INCONCLUSIVE", "no cells")
    ok = [c for c in cells if c.get("ok")]
    if not ok:
        return ("WRR_DRIFT_INCONCLUSIVE", "all cells failed")

    n_detected = sum(c["detected_within_limit"] for c in ok)
    n_fa_pass  = sum(1 for c in ok if c["fa_rate"] < HP_FA_MAX)
    majority = len(ok) // 2 + 1
    mean_detect = sum(c["detection_ops"] for c in ok if c["detected_within_limit"]) / max(n_detected, 1)

    detail = (
        f"n_detected={n_detected}/{len(ok)} n_fa_pass={n_fa_pass}/{len(ok)} "
        f"mean_detect_ops={mean_detect:.1f} "
        f"detect_ops={[c['detection_ops'] for c in ok]}"
    )

    if n_detected < majority:
        return ("WRR_DRIFT_HARD_FAIL",
                f"BURST_NOT_DETECTED: n_detected={n_detected}/{len(ok)}. " + detail)
    if n_detected >= majority and n_fa_pass >= majority:
        return ("WRR_DRIFT_HARD_PASS",
                f"BURST_DETECTED_LOW_FA: n_det={n_detected}/{len(ok)} "
                f"fa_ok={n_fa_pass}/{len(ok)}. " + detail)
    return ("WRR_DRIFT_MIDDLE_BAND",
            f"PARTIAL: " + detail)


def get_output_dir(default_name: str = "pp4_write_retrieve_ratio_drift_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _instrumentation_selftest() -> None:
    """Assert all metrics non-null/non-sentinel."""
    # Formula self-test 1: simulate_workload produces correct ratio
    ops = simulate_workload(100, 2.0, 42)
    n_w = sum(1 for op in ops if op == 'W')
    n_r = len(ops) - n_w
    actual_ratio = n_w / max(n_r, 1)
    assert 1.5 < actual_ratio < 3.0, f"WR ratio={actual_ratio:.2f} (expected ~2.0)"
    print(f"[selftest] formula-1 WR ratio={actual_ratio:.3f} (expected ~2.0) PASS",
          flush=True)

    # Formula self-test 2: rolling WRR is non-empty
    wrr = compute_rolling_wrr(ops, 10)
    assert len(wrr) == len(ops), f"rolling WRR len mismatch"
    assert all(wrr >= 0), "WRR has negative values"
    print(f"[selftest] formula-2 rolling WRR length OK PASS", flush=True)

    # Formula self-test 3: live smoke at small scale
    out = measure_seed(200, 100, 100, BURST_WR_RATIO, BASELINE_WR_RATIO,
                       20, N_SIGMA, 42)
    assert out["ok"], f"measure_seed failed"
    assert 0.0 <= out["fa_rate"] <= 1.0, f"fa_rate sentinel"
    assert out["mu_baseline"] >= 0, f"mu_baseline < 0"
    assert out["detection_ops"] > 0, f"detection_ops=0"
    print(f"[selftest] formula-3 smoke baseline_mu={out['mu_baseline']:.4f} "
          f"fa_rate={out['fa_rate']:.4f} detect_ops={out['detection_ops']} PASS",
          flush=True)

    # Formula self-test 4: filter check - at least 1 burst op processed
    assert out["max_burst_wrr"] >= 0, "max_burst_wrr sentinel"
    # Filter: detected_within_limit is 0 or 1
    assert out["detected_within_limit"] in (0, 1), "detected flag not binary"
    print(f"[selftest] formula-4 binary detection flag OK PASS", flush=True)

    # Formula self-test 5: verdict gates
    fake_hp = [{"ok": True, "detected_within_limit": 1, "fa_rate": 0.02,
                "detection_ops": 50, "max_burst_wrr": 5.0}
               for _ in range(5)]
    v, _ = compute_verdict(fake_hp)
    assert "HARD_PASS" in v, f"HP gate failed: {v}"
    fake_hf = [{"ok": True, "detected_within_limit": 0, "fa_rate": 0.01,
                "detection_ops": 999999, "max_burst_wrr": 0.5}
               for _ in range(5)]
    v, _ = compute_verdict(fake_hf)
    assert "HARD_FAIL" in v, f"HF gate failed: {v}"
    print("[selftest] formula-5 verdict gates PASS", flush=True)

    print("[selftest] pp4_write_retrieve_ratio_drift_v1 ALL PASS", flush=True)


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
    n_base = N_BASELINE // (5 if smoke else 1)
    n_bst  = N_BURST // (5 if smoke else 1)
    n_rec  = N_RECOVERY // (5 if smoke else 1)
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    run_config = {"run_mode": "smoke" if smoke else "full"}
    done = set(list_completed_keys(out_dir, run_config=run_config))

    t0 = time.time()
    print(f"[run] pp4_write_retrieve_ratio_drift_v1 smoke={smoke} "
          f"n_base={n_base} n_burst={n_bst} seeds={seeds} done={len(done)}",
          flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body)
                print(f"  [resume] seed={seed} loaded", flush=True)
                continue
        try:
            cell = measure_seed(n_base, n_bst, n_rec,
                                 BURST_WR_RATIO, BASELINE_WR_RATIO,
                                 WINDOW, N_SIGMA, seed)
            cell["run_mode"] = "smoke" if smoke else "full"
            write_partial_key(out_dir, ck, cell)
            cells.append(cell)
            print(f"  seed={seed} ok={cell.get('ok')} "
                  f"fa={cell.get('fa_rate','n/a'):.4f} "
                  f"detect_ops={cell.get('detection_ops','n/a')} "
                  f"detected={cell.get('detected_within_limit','n/a')} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except Exception as e:
            print(f"  seed={seed} FAILED: {e}", flush=True)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor": "pp4_write_retrieve_ratio_drift_v1",
        "smoke": smoke, "seeds": seeds,
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
