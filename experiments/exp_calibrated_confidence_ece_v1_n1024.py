"""CALIBRATED CONFIDENCE ECE gate smoke (A1).

SCIENTIFIC QUESTION (A1):
  Is the substrate's retrieval confidence (cosine similarity as probability
  proxy) calibrated? ECE<0.05 raw or post-temperature-scaling at N=1024,
  K=100 patterns, 200 test queries?

PRE-REGISTERED BANDS:
  HARD-PASS: ECE<0.05 raw OR post-temperature-scaling in >= 3/5 seeds.
  HARD-FAIL: ECE>0.20 post-temperature-scaling (not calibratable) in majority.
  MIDDLE: 0.05 <= ECE_calibrated <= 0.20.

DESIGN:
  N=1024, M=100 patterns, n_queries=200. Seeds [7,17,23,31,41].
  Confidence = cosine similarity between query and retrieved vector.
  Normalize to [0,1] via softmax temperature scaling.
  ECE = Expected Calibration Error with 10 equal-frequency bins.
  Temperature T* found by minimizing NLL on calibration half of queries.

PROT-018: no _n suffix; production N=1024 (small deliberate design).
PROT-021: M-tagged checkpoint keys.

Anchor: calibrated_confidence_ece_v1_n1024
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_calibrated_confidence_ece.md
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_ece", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key
list_completed_keys = _ck.list_completed_keys

N_FULL  = 1024
N_SMOKE = 256
M       = 100
N_QUERY = 200
N_QUERY_SMOKE = 50
N_BINS  = 10

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
HP_ECE_MAX  = 0.05   # ECE<0.05 to claim calibrated
HF_ECE_MIN  = 0.20   # ECE>0.20 even after temp-scaling = not calibratable


def compute_ece(confidences: np.ndarray, correct: np.ndarray,
                n_bins: int = 10) -> float:
    """Expected Calibration Error (equal-frequency bins)."""
    n = len(confidences)
    if n == 0:
        return 1.0
    # Sort by confidence
    order = np.argsort(confidences)
    conf_sorted = confidences[order]
    corr_sorted = correct[order].astype(float)
    # Split into n_bins equal-count bins
    bin_size = max(1, n // n_bins)
    ece = 0.0
    for b in range(n_bins):
        start = b * bin_size
        end = (b + 1) * bin_size if b < n_bins - 1 else n
        if start >= n:
            break
        bin_conf = conf_sorted[start:end]
        bin_corr = corr_sorted[start:end]
        mean_conf = float(np.mean(bin_conf))
        mean_acc = float(np.mean(bin_corr))
        weight = (end - start) / n
        ece += weight * abs(mean_conf - mean_acc)
    return ece


def temperature_scale(logits: np.ndarray, T: float) -> np.ndarray:
    """Apply temperature scaling to logits (similarity scores)."""
    scaled = logits / max(T, 1e-6)
    # Softmax to probabilities, return max-class probability
    exp_s = np.exp(scaled - scaled.max(axis=1, keepdims=True))
    probs = exp_s / exp_s.sum(axis=1, keepdims=True)
    return probs.max(axis=1)  # confidence = max probability


def find_optimal_T(logits: np.ndarray, labels: np.ndarray) -> float:
    """Binary search for T* minimizing NLL."""
    best_T, best_nll = 1.0, float("inf")
    for T in np.logspace(-1, 1, 50):
        probs = temperature_scale(logits, T)
        # NLL = -mean log P(correct class)
        n = len(labels)
        if n == 0:
            continue
        nll = 0.0
        for i, lbl in enumerate(labels):
            p_correct = float(logits[i, lbl] / T)
            # log-sum-exp normalization
            row = logits[i] / T
            lse = float(row.max() + math.log(np.sum(np.exp(row - row.max()))))
            nll -= (p_correct - lse)
        nll /= n
        if nll < best_nll:
            best_nll = nll
            best_T = float(T)
    return best_T


def measure_seed(N: int, M_count: int, n_query: int, seed: int) -> Dict:
    """Measure raw and calibrated ECE for substrate retrieval confidence."""
    rng = np.random.default_rng(seed)
    patterns = rng.choice([-1.0, 1.0], size=(M_count, N)).astype(np.float32)
    # Hebbian: W = P^T P / N (auto-associative for simplicity)
    W = (patterns.T @ patterns) / N

    n_q = min(n_query, M_count)
    q_idx = rng.choice(M_count, size=n_q, replace=False)
    # Noisy queries
    noise_level = 0.1
    queries = patterns[q_idx] + rng.standard_normal((n_q, N)).astype(np.float32) * noise_level

    # Retrieval: logits = W @ q, similarity scores vs all M patterns
    retrieved = queries @ W.T  # n_q x N
    logits = retrieved @ patterns.T / N  # n_q x M (similarity scores)

    # Confidence = argmax similarity (calibration target: is max-sim correct?)
    pred_idx = np.argmax(logits, axis=1)
    correct = (pred_idx == q_idx).astype(float)
    confidences_raw = logits[np.arange(n_q), pred_idx]
    # Normalize raw similarities to [0,1]
    conf_min = confidences_raw.min()
    conf_max = confidences_raw.max()
    if conf_max > conf_min:
        conf_norm = (confidences_raw - conf_min) / (conf_max - conf_min)
    else:
        conf_norm = np.ones(n_q) * 0.5

    ece_raw = compute_ece(conf_norm, correct, N_BINS)

    # Temperature scaling on calibration half
    n_cal = n_q // 2
    cal_logits = logits[:n_cal]
    cal_labels = q_idx[:n_cal]
    T_star = find_optimal_T(cal_logits, cal_labels)
    # Apply T* to test half
    test_logits = logits[n_cal:]
    test_labels = q_idx[n_cal:]
    test_correct = (np.argmax(test_logits, axis=1) == test_labels).astype(float)
    if len(test_logits) > 0:
        conf_ts = temperature_scale(test_logits, T_star)
        ece_ts = compute_ece(conf_ts, test_correct, N_BINS)
    else:
        ece_ts = ece_raw

    return {
        "seed": seed,
        "N": N,
        "M": M_count,
        "n_query": n_q,
        "acc": float(np.mean(correct)),
        "ece_raw": float(ece_raw),
        "ece_temp_scaled": float(ece_ts),
        "T_star": float(T_star),
        "passes_hp": int(ece_raw < HP_ECE_MAX or ece_ts < HP_ECE_MAX),
        "ok": True,
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("ECE_INCONCLUSIVE", "no cells")
    ok = [c for c in cells if c.get("ok")]
    if not ok:
        return ("ECE_INCONCLUSIVE", "all cells failed")

    n_hp = sum(c["passes_hp"] for c in ok)
    n_hf = sum(1 for c in ok if c["ece_temp_scaled"] > HF_ECE_MIN)
    majority = len(ok) // 2 + 1

    mean_ece_raw = sum(c["ece_raw"] for c in ok) / len(ok)
    mean_ece_ts  = sum(c["ece_temp_scaled"] for c in ok) / len(ok)
    mean_acc = sum(c["acc"] for c in ok) / len(ok)

    detail = (
        f"N={ok[0]['N']} M={ok[0]['M']} mean_acc={mean_acc:.4f} "
        f"mean_ece_raw={mean_ece_raw:.4f} mean_ece_ts={mean_ece_ts:.4f} "
        f"n_hp={n_hp}/{len(ok)}"
    )

    if n_hf >= majority:
        return ("ECE_HARD_FAIL",
                f"NOT_CALIBRATABLE: ece_ts>{HF_ECE_MIN} "
                f"in {n_hf}/{len(ok)} seeds. " + detail)
    if n_hp >= majority:
        return ("ECE_HARD_PASS",
                f"CALIBRATED: ece<{HP_ECE_MAX} "
                f"in {n_hp}/{len(ok)} seeds. " + detail)
    return ("ECE_MIDDLE_BAND",
            f"PARTIAL_CALIBRATION: n_hp={n_hp}/{len(ok)}. " + detail)


def get_output_dir(default_name: str = "calibrated_confidence_ece_v1_n1024") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _instrumentation_selftest() -> None:
    """Assert all metrics non-null/non-sentinel at small scale."""
    # Formula self-test 1: compute_ece on known data
    confs = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
    corr = np.array([0, 0, 1, 1, 1], dtype=float)
    ece = compute_ece(confs, corr, n_bins=5)
    assert 0.0 <= ece <= 1.0, f"ECE out of range: {ece}"
    print(f"[selftest] formula-1 compute_ece={ece:.4f} in [0,1] PASS", flush=True)

    # Formula self-test 2: temperature_scale returns [0,1] probabilities
    logits = np.array([[1.0, 0.5, 0.3], [0.8, 0.9, 0.2]])
    probs = temperature_scale(logits, 1.0)
    assert len(probs) == 2, f"probs length wrong: {len(probs)}"
    assert all(0.0 <= p <= 1.0 for p in probs), f"probs out of [0,1]: {probs}"
    print(f"[selftest] formula-2 temperature_scale PASS", flush=True)

    # Formula self-test 3: live small smoke
    out = measure_seed(128, 20, 30, 42)
    assert out["ok"], f"measure_seed failed"
    assert 0.0 <= out["ece_raw"] <= 1.0, f"ece_raw sentinel: {out['ece_raw']}"
    assert 0.0 <= out["ece_temp_scaled"] <= 1.0, f"ece_ts sentinel"
    assert 0.0 <= out["acc"] <= 1.0, f"acc sentinel"
    assert out["n_query"] >= 1, "n_query=0"
    print(f"[selftest] formula-3 live smoke N=128 M=20 "
          f"ece_raw={out['ece_raw']:.4f} ece_ts={out['ece_temp_scaled']:.4f} "
          f"acc={out['acc']:.4f} PASS", flush=True)

    # Formula self-test 4: verdict gates
    fake_hp = [{"ok": True, "N": 1024, "M": 100, "n_query": 200,
                "acc": 0.9, "ece_raw": 0.03, "ece_temp_scaled": 0.03,
                "T_star": 1.0, "passes_hp": 1}
               for _ in range(5)]
    v, _ = compute_verdict(fake_hp)
    assert "HARD_PASS" in v, f"HP gate failed: {v}"
    fake_hf = [{"ok": True, "N": 1024, "M": 100, "n_query": 200,
                "acc": 0.5, "ece_raw": 0.30, "ece_temp_scaled": 0.25,
                "T_star": 0.5, "passes_hp": 0}
               for _ in range(5)]
    v, _ = compute_verdict(fake_hf)
    assert "HARD_FAIL" in v, f"HF gate failed: {v}"
    print("[selftest] formula-4 verdict gates PASS", flush=True)

    print("[selftest] calibrated_confidence_ece_v1_n1024 ALL PASS", flush=True)


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
    n_q    = N_QUERY_SMOKE if smoke else N_QUERY
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    run_config = {"N": N_cfg, "M": M, "run_mode": "smoke" if smoke else "full"}
    done = set(list_completed_keys(out_dir, run_config=run_config))

    t0 = time.time()
    print(f"[run] calibrated_confidence_ece_v1 smoke={smoke} "
          f"N={N_cfg} M={M} n_query={n_q} seeds={seeds} "
          f"done={len(done)}", flush=True)

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
            cell = measure_seed(N_cfg, M, n_q, seed)
            cell["run_mode"] = "smoke" if smoke else "full"
            write_partial_key(out_dir, ck, cell)
            cells.append(cell)
            print(f"  seed={seed} ok={cell.get('ok')} "
                  f"acc={cell.get('acc','n/a'):.4f} "
                  f"ece_raw={cell.get('ece_raw','n/a'):.4f} "
                  f"ece_ts={cell.get('ece_temp_scaled','n/a'):.4f} "
                  f"T*={cell.get('T_star','n/a'):.3f} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except Exception as e:
            print(f"  seed={seed} FAILED: {e}", flush=True)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor": "calibrated_confidence_ece_v1_n1024",
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
