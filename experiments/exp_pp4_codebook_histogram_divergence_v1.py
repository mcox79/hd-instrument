"""PP-4 Codebook Histogram Divergence drift detector smoke (A3).

SCIENTIFIC QUESTION (A3):
  Does KL divergence of codebook access histogram (vs bootstrap 95th-pct
  null) detect workload distribution shift within 800 ops? <5% false-alarm.

PRE-REGISTERED BANDS:
  HARD-PASS: KL_divergence > bootstrap 95th-pct tau within 800 ops in
    >= 3/5 seeds AND false_alarm_rate < 0.05 on pre-drift baseline.
  HARD-FAIL: KL NOT above tau within 1600 ops in majority of seeds.
  MIDDLE: detection within 800-1600 ops.

DESIGN:
  Synthetic workload: 2000 ops baseline (uniform codebook access), then
  1000 ops shifted (Zipf alpha=2 skewed access), then 1000 recovery.
  Codebook size = 64 slots. Rolling histogram window = 200 ops.
  Bootstrap null: 1000 samples of rolling KL on baseline, take 95th pct.
  Seeds: [7,17,23,31,41].

PROT-018: no _n suffix; workload-only.
PROT-021: seed-tagged checkpoint keys.

Anchor: pp4_codebook_histogram_divergence_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_pp4_codebook_histogram_divergence.md
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_chd", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key
list_completed_keys = _ck.list_completed_keys

N_CODEBOOK    = 64
N_BASELINE    = 2000
N_DRIFT       = 1000
N_RECOVERY    = 1000
WINDOW        = 200
N_BOOTSTRAP   = 500
MAX_DETECT_OPS = 800   # must detect within 800 ops of drift start
HP_FA_MAX     = 0.05
ZIPF_ALPHA    = 2.0

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]


def kl_divergence(p: np.ndarray, q: np.ndarray) -> float:
    """KL(p||q) with Laplace smoothing to avoid log(0)."""
    eps = 1e-9
    p_s = p + eps; p_s /= p_s.sum()
    q_s = q + eps; q_s /= q_s.sum()
    return float(np.sum(p_s * np.log(p_s / q_s)))


def rolling_histogram(accesses: np.ndarray, n_slots: int,
                       window: int) -> np.ndarray:
    """Compute rolling histogram KL from uniform for each position."""
    n = len(accesses)
    kls = np.zeros(n, dtype=float)
    uniform = np.ones(n_slots) / n_slots
    for i in range(window, n):
        window_acc = accesses[i - window: i]
        hist = np.bincount(window_acc, minlength=n_slots).astype(float)
        hist /= hist.sum()
        kls[i] = kl_divergence(hist, uniform)
    return kls


def measure_seed(n_codebook: int, n_baseline: int, n_drift: int, n_recovery: int,
                 window: int, n_bootstrap: int, seed: int) -> Dict:
    """Simulate access-distribution shift and measure KL divergence detection."""
    rng = np.random.default_rng(seed)

    # Baseline: uniform access
    acc_baseline = rng.integers(0, n_codebook, size=n_baseline)
    # Drift: Zipf-skewed access
    weights = 1.0 / np.arange(1, n_codebook + 1) ** ZIPF_ALPHA
    weights /= weights.sum()
    acc_drift = rng.choice(n_codebook, size=n_drift, p=weights)
    # Recovery: uniform again
    acc_recovery = rng.integers(0, n_codebook, size=n_recovery)

    full_acc = np.concatenate([acc_baseline, acc_drift, acc_recovery])
    kls = rolling_histogram(full_acc, n_codebook, window)

    # Bootstrap null: sample from baseline to get 95th-pct threshold
    baseline_kls = kls[window:n_baseline]
    if len(baseline_kls) > n_bootstrap:
        baseline_kls = rng.choice(baseline_kls, size=n_bootstrap, replace=False)
    tau = float(np.percentile(baseline_kls, 95)) if len(baseline_kls) > 0 else 0.0

    # False alarm rate on baseline
    n_fa = int(np.sum(kls[window:n_baseline] > tau))
    fa_denom = max(n_baseline - window, 1)
    fa_rate = n_fa / fa_denom

    # Detection time in drift window
    drift_kls = kls[n_baseline: n_baseline + n_drift]
    detect_ops = 999999
    for i, kl_val in enumerate(drift_kls):
        if kl_val > tau:
            detect_ops = i + 1
            break

    detected = int(detect_ops <= MAX_DETECT_OPS)

    return {
        "seed": seed,
        "n_codebook": n_codebook,
        "tau": float(tau),
        "fa_rate": float(fa_rate),
        "detection_ops": int(detect_ops),
        "detected_within_limit": detected,
        "max_drift_kl": float(drift_kls.max()) if len(drift_kls) > 0 else 0.0,
        "ok": True,
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("CHD_DRIFT_INCONCLUSIVE", "no cells")
    ok = [c for c in cells if c.get("ok")]
    if not ok:
        return ("CHD_DRIFT_INCONCLUSIVE", "all cells failed")

    n_detected = sum(c["detected_within_limit"] for c in ok)
    n_fa_pass  = sum(1 for c in ok if c["fa_rate"] < HP_FA_MAX)
    majority = len(ok) // 2 + 1

    mean_tau = sum(c["tau"] for c in ok) / len(ok)
    detail = (
        f"n_detected={n_detected}/{len(ok)} n_fa_pass={n_fa_pass}/{len(ok)} "
        f"mean_tau={mean_tau:.4f} "
        f"detect_ops={[c['detection_ops'] for c in ok]}"
    )

    if n_detected < majority:
        return ("CHD_DRIFT_HARD_FAIL",
                f"KL_SHIFT_NOT_DETECTED: n_det={n_detected}/{len(ok)}. " + detail)
    if n_detected >= majority and n_fa_pass >= majority:
        return ("CHD_DRIFT_HARD_PASS",
                f"KL_SHIFT_DETECTED_LOW_FA: n_det={n_detected}/{len(ok)} "
                f"fa_ok={n_fa_pass}/{len(ok)}. " + detail)
    return ("CHD_DRIFT_MIDDLE_BAND", f"PARTIAL: " + detail)


def get_output_dir(default_name: str = "pp4_codebook_histogram_divergence_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _instrumentation_selftest() -> None:
    """Assert all metrics non-null/non-sentinel."""
    # Formula self-test 1: kl_divergence is >= 0
    p = np.array([0.5, 0.3, 0.2])
    q = np.array([0.33, 0.33, 0.33])
    kl = kl_divergence(p, q)
    assert kl >= 0, f"KL divergence < 0: {kl}"
    print(f"[selftest] formula-1 kl_divergence={kl:.4f} >= 0 PASS", flush=True)

    # Formula self-test 2: identical distributions have KL~0
    kl_same = kl_divergence(q, q)
    assert kl_same < 0.01, f"KL(q||q)={kl_same:.4f} should be ~0"
    print(f"[selftest] formula-2 KL(uniform||uniform)={kl_same:.6f} ~0 PASS",
          flush=True)

    # Formula self-test 3: rolling_histogram non-empty
    rng = np.random.default_rng(42)
    acc = rng.integers(0, 8, size=200)
    kls = rolling_histogram(acc, 8, 20)
    assert len(kls) == len(acc), "rolling_histogram length mismatch"
    assert kls[20:].min() >= 0, "KL values negative"
    assert kls[20:].max() > 0, "KL values all zero after window"
    print(f"[selftest] formula-3 rolling_histogram len={len(kls)} "
          f"max_kl={kls[20:].max():.4f} PASS", flush=True)

    # Formula self-test 4: live smoke at small scale
    out = measure_seed(16, 200, 100, 100, 20, 50, 42)
    assert out["ok"], f"measure_seed failed"
    assert out["tau"] >= 0, f"tau < 0: {out['tau']}"
    assert 0.0 <= out["fa_rate"] <= 1.0, f"fa_rate out of [0,1]: {out['fa_rate']}"
    assert out["detection_ops"] > 0, "detection_ops=0"
    print(f"[selftest] formula-4 smoke tau={out['tau']:.4f} "
          f"fa={out['fa_rate']:.4f} det_ops={out['detection_ops']} PASS",
          flush=True)

    # Formula self-test 5: verdict gates
    fake_hp = [{"ok": True, "detected_within_limit": 1, "fa_rate": 0.02,
                "detection_ops": 100, "max_drift_kl": 1.0, "tau": 0.5}
               for _ in range(5)]
    v, _ = compute_verdict(fake_hp)
    assert "HARD_PASS" in v, f"HP gate: {v}"
    fake_hf = [{"ok": True, "detected_within_limit": 0, "fa_rate": 0.01,
                "detection_ops": 999999, "max_drift_kl": 0.01, "tau": 0.5}
               for _ in range(5)]
    v, _ = compute_verdict(fake_hf)
    assert "HARD_FAIL" in v, f"HF gate: {v}"
    print("[selftest] formula-5 verdict gates PASS", flush=True)

    print("[selftest] pp4_codebook_histogram_divergence_v1 ALL PASS", flush=True)


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
    n_drft = N_DRIFT // (5 if smoke else 1)
    n_rec  = N_RECOVERY // (5 if smoke else 1)
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    run_config = {"run_mode": "smoke" if smoke else "full"}
    done = set(list_completed_keys(out_dir, run_config=run_config))

    t0 = time.time()
    print(f"[run] pp4_codebook_histogram_divergence_v1 smoke={smoke} "
          f"n_base={n_base} n_drift={n_drft} seeds={seeds} done={len(done)}",
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
            cell = measure_seed(N_CODEBOOK, n_base, n_drft, n_rec,
                                 WINDOW, N_BOOTSTRAP, seed)
            cell["run_mode"] = "smoke" if smoke else "full"
            write_partial_key(out_dir, ck, cell)
            cells.append(cell)
            print(f"  seed={seed} ok={cell.get('ok')} "
                  f"tau={cell.get('tau','n/a'):.4f} "
                  f"fa={cell.get('fa_rate','n/a'):.4f} "
                  f"detect_ops={cell.get('detection_ops','n/a')} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except Exception as e:
            print(f"  seed={seed} FAILED: {e}", flush=True)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor": "pp4_codebook_histogram_divergence_v1",
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
