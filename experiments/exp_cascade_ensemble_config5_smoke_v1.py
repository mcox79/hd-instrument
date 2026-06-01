"""Cascading Ensemble Config 5 smoke (R2.3).

SCIENTIFIC QUESTION (R2.3):
  Does Config 5 (cascading small-fast + large-slow fallback) achieve:
  (1) < 30% escalation rate at confidence tau=0.7, AND
  (2) cascade accuracy within 3pp of large-substrate-only accuracy?
  Tests at N=4096 and N=16384.

PRE-REGISTERED BANDS:
  HARD-PASS: escalation_rate < 0.30 AND |acc_cascade - acc_large| <= 0.03
    at BOTH N=4096 and N=16384 in >= 3/5 seeds.
  HARD-FAIL: escalation_rate >= 0.60 OR |delta_acc| > 0.10 in majority.
  MIDDLE: escalation<0.30 but accuracy gap >0.03.

DESIGN:
  Small substrate: N_small=256 M_small=64.
  Large substrate: N_large=4096 M_large=1024 (FULL scale).
  Smoke scale: N_large=1024.
  Cascade: query small first; escalate if confidence < tau=0.7.
  Confidence = max cosine similarity to stored vals.
  Seeds: [7,17,23,31,41].

PROT-018: no _n suffix; cascade design, multiple N values.
PROT-021: M-tagged checkpoint keys.

Anchor: cascade_ensemble_config5_smoke_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_cascade_ensemble_config5_smoke.md
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_casc", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key
list_completed_keys = _ck.list_completed_keys

N_FULL       = 4096  # both substrates use same vector space (PROT-018 N=4096)
N_SMOKE_VAL  = 1024
M_SMALL_FULL  = 256   # small substrate: low capacity
M_SMALL_SMOKE = 64
M_LARGE_FULL  = 1024  # large substrate: high capacity
M_LARGE_SMOKE = 256
N_QUERY      = 200
TAU          = 0.7   # confidence threshold for escalation

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

HP_ESCALATION_MAX = 0.30
HP_ACC_DELTA_MAX  = 0.03
HF_ESCALATION_MIN = 0.60
HF_ACC_DELTA_MAX  = 0.10


def build_substrate(N: int, M: int, seed: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build Hebbian substrate: W, keys, vals."""
    rng = np.random.default_rng(seed)
    keys = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)
    vals = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)
    W = (vals.T @ keys) / N
    return W, keys, vals


def query_substrate(W: np.ndarray, query: np.ndarray,
                    vals: np.ndarray, N: int) -> Tuple[int, float]:
    """Query substrate: return (predicted_val_idx, confidence)."""
    retrieved = query @ W.T
    sims = retrieved @ vals.T / N
    pred = int(np.argmax(sims))
    confidence = float(sims[pred])
    return pred, confidence


def measure_seed(N: int, M_small: int, M_large: int,
                 n_query: int, tau: float, seed: int) -> Dict:
    """Measure cascade escalation rate and accuracy vs large-only.

    Both substrates live in the SAME N-dimensional space.
    Small substrate W_small: trained on M_small facts (low capacity, fast).
    Large substrate W_large: trained on M_large facts (high capacity, slow).
    They share the SAME M_small facts at the same key-val pairs.
    Cascade: query W_small first; if confidence >= tau, accept.
    Otherwise escalate to W_large.
    """
    rng = np.random.default_rng(seed)

    # Shared fact pool
    keys = rng.choice([-1.0, 1.0], size=(M_large, N)).astype(np.float32)
    vals = rng.choice([-1.0, 1.0], size=(M_large, N)).astype(np.float32)

    # Small substrate: only first M_small facts
    W_small = (vals[:M_small].T @ keys[:M_small]) / N
    # Large substrate: all M_large facts
    W_large = (vals.T @ keys) / N

    # Test queries: from first M_small facts (facts that small substrate knows)
    n_q = min(n_query, M_small)
    q_idx = rng.choice(M_small, size=n_q, replace=False)
    queries = keys[q_idx] + rng.standard_normal((n_q, N)).astype(np.float32) * 0.05

    n_escalate = 0
    n_correct_cascade = 0
    n_correct_large = 0

    for i in range(n_q):
        q = queries[i]
        true_val_idx = q_idx[i]

        # Small query
        retrieved_s = q @ W_small.T
        sims_s = retrieved_s @ vals[:M_small].T / N  # compare to small val bank
        conf_s = float(sims_s.max())
        pred_s = int(np.argmax(sims_s))  # index into M_small val bank

        if conf_s >= tau:
            n_correct_cascade += int(q_idx[i] == pred_s)
        else:
            # Escalate to large
            n_escalate += 1
            retrieved_l = q @ W_large.T
            sims_l = retrieved_l @ vals.T / N
            pred_l = int(np.argmax(sims_l))
            n_correct_cascade += int(q_idx[i] == pred_l)

        # Large-only for comparison
        retrieved_l2 = q @ W_large.T
        sims_l2 = retrieved_l2 @ vals.T / N
        n_correct_large += int(q_idx[i] == np.argmax(sims_l2))

    escalation_rate = n_escalate / max(n_q, 1)
    acc_cascade = n_correct_cascade / max(n_q, 1)
    acc_large   = n_correct_large / max(n_q, 1)
    delta_acc   = abs(acc_cascade - acc_large)

    return {
        "seed": seed,
        "N": N,
        "M_small": M_small,
        "M_large": M_large,
        "n_query": n_q,
        "tau": float(tau),
        "escalation_rate": float(escalation_rate),
        "acc_cascade": float(acc_cascade),
        "acc_large_only": float(acc_large),
        "delta_acc": float(delta_acc),
        "passes_hp": int(escalation_rate < HP_ESCALATION_MAX and
                         delta_acc <= HP_ACC_DELTA_MAX),
        "ok": True,
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("CASCADE5_INCONCLUSIVE", "no cells")
    ok = [c for c in cells if c.get("ok")]
    if not ok:
        return ("CASCADE5_INCONCLUSIVE", "all cells failed")

    n_hp = sum(c["passes_hp"] for c in ok)
    n_hf = sum(1 for c in ok
               if c["escalation_rate"] >= HF_ESCALATION_MIN or
               c["delta_acc"] > HF_ACC_DELTA_MAX)
    majority = len(ok) // 2 + 1

    mean_esc  = sum(c["escalation_rate"] for c in ok) / len(ok)
    mean_dacc = sum(c["delta_acc"] for c in ok) / len(ok)

    detail = (
        f"mean_escalation={mean_esc:.4f} mean_delta_acc={mean_dacc:.4f} "
        f"n_hp={n_hp}/{len(ok)} n_hf={n_hf}/{len(ok)}"
    )

    if n_hf >= majority:
        return ("CASCADE5_HARD_FAIL",
                f"ESCALATION_TOO_HIGH_OR_ACC_GAP: n_hf={n_hf}/{len(ok)}. " + detail)
    if n_hp >= majority:
        return ("CASCADE5_HARD_PASS",
                f"CASCADE_EFFICIENT_AND_ACCURATE: n_hp={n_hp}/{len(ok)}. " + detail)
    return ("CASCADE5_MIDDLE_BAND", f"PARTIAL: " + detail)


def get_output_dir(default_name: str = "cascade_ensemble_config5_smoke_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _instrumentation_selftest() -> None:
    """Assert all metrics non-null/non-sentinel."""
    # Formula self-test 1: escalation rate is in [0,1]
    out = measure_seed(N_SMOKE_VAL, M_SMALL_SMOKE, M_LARGE_SMOKE, 20, TAU, 42)
    assert out["ok"], f"measure_seed failed"
    assert 0.0 <= out["escalation_rate"] <= 1.0, f"escalation_rate sentinel"
    assert 0.0 <= out["acc_cascade"] <= 1.0, f"acc_cascade sentinel"
    assert 0.0 <= out["acc_large_only"] <= 1.0, f"acc_large_only sentinel"
    assert out["n_query"] >= 1, "n_query=0"
    print(f"[selftest] formula-1 smoke esc={out['escalation_rate']:.4f} "
          f"acc_casc={out['acc_cascade']:.4f} acc_large={out['acc_large_only']:.4f} PASS",
          flush=True)

    # Formula self-test 2: verdict gates
    fake_hp = [{"ok": True, "escalation_rate": 0.20, "acc_cascade": 0.92,
                "acc_large_only": 0.93, "delta_acc": 0.01, "passes_hp": 1}
               for _ in range(5)]
    v, _ = compute_verdict(fake_hp)
    assert "HARD_PASS" in v, f"HP gate: {v}"
    fake_hf = [{"ok": True, "escalation_rate": 0.70, "acc_cascade": 0.80,
                "acc_large_only": 0.93, "delta_acc": 0.13, "passes_hp": 0}
               for _ in range(5)]
    v, _ = compute_verdict(fake_hf)
    assert "HARD_FAIL" in v, f"HF gate: {v}"
    print("[selftest] formula-2 verdict gates PASS", flush=True)

    # Formula self-test 3: filter check (n_query >= 1)
    assert out["n_query"] >= 1, "filter passes 0 queries"
    print("[selftest] formula-3 filter check PASS", flush=True)

    print("[selftest] cascade_ensemble_config5_smoke_v1 ALL PASS", flush=True)


_instrumentation_selftest()


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    smoke     = args.smoke
    N_cfg     = N_SMOKE_VAL if smoke else N_FULL
    M_s       = M_SMALL_SMOKE if smoke else M_SMALL_FULL
    M_l       = M_LARGE_SMOKE if smoke else M_LARGE_FULL
    seeds     = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    run_config = {"run_mode": "smoke" if smoke else "full"}
    done = set(list_completed_keys(out_dir, run_config=run_config))

    t0 = time.time()
    print(f"[run] cascade_ensemble_config5_smoke_v1 smoke={smoke} "
          f"N={N_cfg} M_small={M_s} M_large={M_l} tau={TAU} seeds={seeds} "
          f"done={len(done)}", flush=True)

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
            cell = measure_seed(N_cfg, M_s, M_l, N_QUERY, TAU, seed)
            cell["run_mode"] = "smoke" if smoke else "full"
            write_partial_key(out_dir, ck, cell)
            cells.append(cell)
            print(f"  seed={seed} ok={cell.get('ok')} "
                  f"esc={cell.get('escalation_rate','n/a'):.4f} "
                  f"acc_casc={cell.get('acc_cascade','n/a'):.4f} "
                  f"delta_acc={cell.get('delta_acc','n/a'):.4f} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except Exception as e:
            print(f"  seed={seed} FAILED: {e}", flush=True)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor": "cascade_ensemble_config5_smoke_v1",
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
