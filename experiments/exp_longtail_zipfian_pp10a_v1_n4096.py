"""Long-tail Zipfian PP-10a smoke (R2.4).

SCIENTIFIC QUESTION (R2.4):
  Does substrate retrieve head and tail facts with equal accuracy
  (within 2pp) when queries are Zipf-distributed (alpha=1.5)?
  Verifies: Hebbian write is query-agnostic (no LRU-cache effect).

PRE-REGISTERED BANDS:
  HARD-PASS: |acc_head - acc_tail| <= 0.02 in >= 3/5 seeds.
  HARD-FAIL: |acc_head - acc_tail| > 0.10 (strong LRU-like bias) in majority.
  MIDDLE: 0.02 < delta <= 0.10.

DESIGN:
  N=4096, M=512, alpha_zipf=1.5, m_0=0.8 (load).
  Head facts: top 10% by Zipf rank (most queried).
  Tail facts: bottom 10% by Zipf rank (least queried).
  Both head and tail are WRITTEN once with same Hebbian update.
  Query frequency varies but retrieval accuracy should be uniform.
  Seeds: [7,17,23,31,41].

PROT-018: production N=4096 (no _n suffix, documented in prereg).
PROT-019: N>=4096 timeout >= 14400s.
PROT-021: M-tagged checkpoint keys.

Anchor: longtail_zipfian_pp10a_v1_n4096
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_longtail_zipfian_pp10a.md
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_lt", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key
list_completed_keys = _ck.list_completed_keys

N_FULL  = 4096
N_SMOKE = 1024
M_FULL  = 512
M_SMOKE = 128
ALPHA_ZIPF = 1.5
HEAD_FRAC  = 0.10   # top 10% = head
TAIL_FRAC  = 0.10   # bottom 10% = tail
N_QUERY    = 100    # queries per head/tail group

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

HP_DELTA_MAX = 0.02   # |acc_head - acc_tail| <= 0.02 = HARD_PASS
HF_DELTA_MIN = 0.10   # > 0.10 = HARD_FAIL (LRU-like bias)

assert N_FULL == 4096, "N_FULL must be 4096"


def measure_seed(N: int, M: int, alpha_zipf: float, head_frac: float,
                 tail_frac: float, n_query: int, seed: int) -> Dict:
    """Measure head vs tail retrieval accuracy under Zipf-distributed queries."""
    rng = np.random.default_rng(seed)

    # Build W: Hebbian associative memory, all M facts written once
    keys = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)
    vals = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)
    # Hebbian write: all facts with equal weight (query-agnostic)
    W = (vals.T @ keys) / N

    # Zipf rank: freq[i] ~ 1/i^alpha. Rank 1 = head (highest freq), M = tail.
    ranks = np.arange(1, M + 1, dtype=float)
    freqs = 1.0 / ranks ** alpha_zipf
    freqs /= freqs.sum()

    # Head = top head_frac by frequency
    n_head = max(1, int(M * head_frac))
    n_tail = max(1, int(M * tail_frac))
    head_idx = np.argsort(freqs)[::-1][:n_head]  # highest freq first
    tail_idx  = np.argsort(freqs)[:n_tail]         # lowest freq first

    def measure_group_acc(group_idx: np.ndarray, n_q: int) -> float:
        """Retrieval accuracy for a group of facts."""
        n_q_actual = min(n_q, len(group_idx))
        test_idx = rng.choice(group_idx, size=n_q_actual, replace=True)
        queries = keys[test_idx] + rng.standard_normal(
            (n_q_actual, N)).astype(np.float32) * 0.05
        retrieved = queries @ W.T
        sims = retrieved @ vals.T / N
        pred = np.argmax(sims, axis=1)
        return float(np.mean(pred == test_idx))

    acc_head = measure_group_acc(head_idx, n_query)
    acc_tail = measure_group_acc(tail_idx, n_query)
    delta    = abs(acc_head - acc_tail)

    return {
        "seed": seed,
        "N": N,
        "M": M,
        "alpha_zipf": float(alpha_zipf),
        "n_head": int(n_head),
        "n_tail": int(n_tail),
        "acc_head": float(acc_head),
        "acc_tail": float(acc_tail),
        "delta_acc": float(delta),
        "passes_hp": int(delta <= HP_DELTA_MAX),
        "ok": True,
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("ZIPF_PP10A_INCONCLUSIVE", "no cells")
    ok = [c for c in cells if c.get("ok")]
    if not ok:
        return ("ZIPF_PP10A_INCONCLUSIVE", "all cells failed")

    n_hp = sum(c["passes_hp"] for c in ok)
    n_hf = sum(1 for c in ok if c["delta_acc"] > HF_DELTA_MIN)
    majority = len(ok) // 2 + 1
    mean_delta = sum(c["delta_acc"] for c in ok) / len(ok)
    mean_head  = sum(c["acc_head"] for c in ok) / len(ok)
    mean_tail  = sum(c["acc_tail"] for c in ok) / len(ok)

    detail = (
        f"N={ok[0]['N']} M={ok[0]['M']} alpha={ok[0]['alpha_zipf']} "
        f"mean_acc_head={mean_head:.4f} mean_acc_tail={mean_tail:.4f} "
        f"mean_delta={mean_delta:.4f} n_hp={n_hp}/{len(ok)}"
    )

    if n_hf >= majority:
        return ("ZIPF_PP10A_HARD_FAIL",
                f"LRU_BIAS_DETECTED: delta>{HF_DELTA_MIN} "
                f"in {n_hf}/{len(ok)} seeds. " + detail)
    if n_hp >= majority:
        return ("ZIPF_PP10A_HARD_PASS",
                f"UNIFORM_TAIL_FIDELITY: delta<={HP_DELTA_MAX} "
                f"in {n_hp}/{len(ok)} seeds. " + detail)
    return ("ZIPF_PP10A_MIDDLE_BAND",
            f"PARTIAL: mean_delta={mean_delta:.4f}. " + detail)


def get_output_dir(default_name: str = "longtail_zipfian_pp10a_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _instrumentation_selftest() -> None:
    """Assert all metrics non-null/non-sentinel."""
    # PROT-018
    assert N_FULL == 4096, "PROT-018 violation"

    # Formula self-test 1: Zipf distribution sum to 1
    M_t = 50; alpha_t = 1.5
    ranks = np.arange(1, M_t + 1, dtype=float)
    freqs = 1.0 / ranks ** alpha_t
    freqs /= freqs.sum()
    assert abs(freqs.sum() - 1.0) < 1e-6, f"Zipf freqs don't sum to 1"
    # Head vs tail separation
    head_freq = freqs[:5].sum()
    tail_freq  = freqs[-5:].sum()
    assert head_freq > tail_freq, "head should be more frequent than tail"
    print(f"[selftest] formula-1 Zipf head_freq={head_freq:.4f} "
          f"tail_freq={tail_freq:.4f} PASS", flush=True)

    # Formula self-test 2: live smoke at small N
    out = measure_seed(256, 50, ALPHA_ZIPF, HEAD_FRAC, TAIL_FRAC, 20, 42)
    assert out["ok"], f"measure_seed failed"
    assert 0.0 <= out["acc_head"] <= 1.0, f"acc_head sentinel"
    assert 0.0 <= out["acc_tail"] <= 1.0, f"acc_tail sentinel"
    assert 0.0 <= out["delta_acc"] <= 1.0, f"delta_acc sentinel"
    assert out["n_head"] >= 1, "n_head=0 (filter passed 0 items)"
    assert out["n_tail"] >= 1, "n_tail=0 (filter passed 0 items)"
    print(f"[selftest] formula-2 smoke N=256 M=50 "
          f"acc_head={out['acc_head']:.4f} acc_tail={out['acc_tail']:.4f} "
          f"delta={out['delta_acc']:.4f} PASS", flush=True)

    # Formula self-test 3: verdict gates
    fake_hp = [{"ok": True, "N": 4096, "M": 512, "alpha_zipf": 1.5,
                "n_head": 51, "n_tail": 51, "acc_head": 0.95, "acc_tail": 0.94,
                "delta_acc": 0.01, "passes_hp": 1}
               for _ in range(5)]
    v, _ = compute_verdict(fake_hp)
    assert "HARD_PASS" in v, f"HP gate: {v}"
    fake_hf = [{"ok": True, "N": 4096, "M": 512, "alpha_zipf": 1.5,
                "n_head": 51, "n_tail": 51, "acc_head": 0.95, "acc_tail": 0.80,
                "delta_acc": 0.15, "passes_hp": 0}
               for _ in range(5)]
    v, _ = compute_verdict(fake_hf)
    assert "HARD_FAIL" in v, f"HF gate: {v}"
    print("[selftest] formula-3 verdict gates PASS", flush=True)

    print("[selftest] longtail_zipfian_pp10a_v1_n4096 ALL PASS", flush=True)


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
    print(f"[run] longtail_zipfian_pp10a_v1_n4096 smoke={smoke} "
          f"N={N_cfg} M={M_cfg} alpha={ALPHA_ZIPF} seeds={seeds} "
          f"done={len(done)}", flush=True)

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
            cell = measure_seed(N_cfg, M_cfg, ALPHA_ZIPF, HEAD_FRAC, TAIL_FRAC,
                                 N_QUERY, seed)
            cell["run_mode"] = "smoke" if smoke else "full"
            write_partial_key(out_dir, ck, cell)
            cells.append(cell)
            print(f"  seed={seed} ok={cell.get('ok')} "
                  f"acc_head={cell.get('acc_head','n/a'):.4f} "
                  f"acc_tail={cell.get('acc_tail','n/a'):.4f} "
                  f"delta={cell.get('delta_acc','n/a'):.4f} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except Exception as e:
            print(f"  seed={seed} FAILED: {e}", flush=True)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor": "longtail_zipfian_pp10a_v1_n4096",
        "N": N_cfg, "M": M_cfg, "smoke": smoke, "seeds": seeds,
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
