"""S4 MODERN HOPFIELD n16384 v7 RESILIENT (EC1).

Modern Hopfield activation test at N=16384 with three resilient codebook
construction strategies tried in order. Robust to v6 outcome.

CODEBOOK STRATEGIES (first success wins):
  (a) 256-codeword chunks on GPU, generated chunk-by-chunk and concatenated.
  (b) Single-codeword streaming with explicit empty_cache between codewords.
  (c) CPU codebook construction + chunked GPU upload.

SCIENTIFIC QUESTION:
  At N=16384, BSC codebook, M in {N/8, N/4, N/2, N}, does at least one
  strategy succeed AND identify max_M_at_95_recall AND exceed N/4?

PRE-REGISTERED BANDS:
  HP = construction succeeds AND max_M_at_95_recall exceeds N/4.
       (Modern Hopfield activation bend.)
  HF = all 3 strategies OOM across all M.
  MB = construction works at smaller M but OOMs at N cell.

PROT-018: _n16384 binds N = 16384.
Anchor: modern_hopfield_n16384_v7_resilient
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_modern_hopfield_n16384_v7_resilient.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import os
import time
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_s4", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n16384 binds N = 16384
N = 16384
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 16384, f"PROT-018: N_FULL must be 16384; got {N_FULL}"

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]
N_PROBE = 200
RECALL_THRESHOLD = 0.95

MEM_HARD_CEILING_GB = 6.0   # smoke gate at 6 GiB


def _m_sweep_full(N_use: int) -> List[int]:
    return [N_use // 8, N_use // 4, N_use // 2, N_use]


M_SWEEP_FULL  = _m_sweep_full(N_FULL)       # [2048, 4096, 8192, 16384]
M_SWEEP_SMOKE = [N_SMOKE // 4, N_SMOKE // 2]  # [256, 512]


def get_output_dir(default_name: str = "modern_hopfield_n16384_v7_resilient") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _mem_gb(device: torch.device) -> float:
    if device.type == "cuda":
        return float(torch.cuda.memory_allocated() / (1024**3))
    return 0.0


def _safe_clear(device: torch.device) -> None:
    if device.type == "cuda":
        try:
            torch.cuda.empty_cache()
        except Exception:
            pass


# -------- Codebook construction strategies --------

def _bsc_chunk(n_codewords: int, N_use: int, seed: int,
                 device: torch.device) -> torch.Tensor:
    """Generate a chunk of BSC codewords on `device`."""
    g = torch.Generator(device=device).manual_seed(seed)
    return (torch.rand(n_codewords, N_use, generator=g, device=device) > 0.5).to(torch.float32) * 2 - 1


def strategy_a_chunked(N_use: int, C: int, seed: int,
                        device: torch.device, chunk: int = 256) -> torch.Tensor:
    """Strategy (a): 256-codeword chunks on GPU."""
    parts: List[torch.Tensor] = []
    for i in range(0, C, chunk):
        n = min(chunk, C - i)
        parts.append(_bsc_chunk(n, N_use, seed + i, device))
    return torch.cat(parts, dim=0)


def strategy_b_streaming(N_use: int, C: int, seed: int,
                           device: torch.device) -> torch.Tensor:
    """Strategy (b): single-codeword streaming with empty_cache."""
    out = torch.empty(C, N_use, dtype=torch.float32, device=device)
    for i in range(C):
        out[i] = _bsc_chunk(1, N_use, seed + i, device)[0]
        if i % 64 == 0:
            _safe_clear(device)
    return out


def strategy_c_cpu_upload(N_use: int, C: int, seed: int,
                            device: torch.device, chunk: int = 256) -> torch.Tensor:
    """Strategy (c): CPU construction + chunked upload."""
    cpu = torch.device("cpu")
    cb_cpu = _bsc_chunk(C, N_use, seed, cpu)
    if device.type == "cpu":
        return cb_cpu
    out = torch.empty(C, N_use, dtype=torch.float32, device=device)
    for i in range(0, C, chunk):
        n = min(chunk, C - i)
        out[i:i+n] = cb_cpu[i:i+n].to(device)
    return out


def try_codebook(N_use: int, C: int, seed: int,
                   device: torch.device) -> Tuple[Optional[torch.Tensor], str, Dict]:
    """Try strategies (a), (b), (c) in order. Return (codebook, strategy, log)."""
    log: Dict[str, Dict] = {}
    for name, fn in [("a_chunked", strategy_a_chunked),
                       ("b_streaming", strategy_b_streaming),
                       ("c_cpu_upload", strategy_c_cpu_upload)]:
        t0 = time.time()
        try:
            cb = fn(N_use, C, seed, device)
            log[name] = {"success": True,
                          "elapsed_s": round(time.time() - t0, 2),
                          "mem_gb_post": round(_mem_gb(device), 3)}
            return cb, name, log
        except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
            log[name] = {"success": False,
                          "error": str(e)[:300],
                          "elapsed_s": round(time.time() - t0, 2)}
            _safe_clear(device)
    return None, "none", log


# -------- Substrate ops with BSC codebook --------

def store_facts(codebook: torch.Tensor, M: int, seed: int,
                  N_use: int, device: torch.device):
    """Sample M (key_idx, val_idx) pairs; build W from outer products."""
    C = codebook.shape[0]
    g = torch.Generator(device=device).manual_seed(seed + 1000)
    perm = torch.randperm(C, generator=g, device=device)
    key_idx = perm[:M].to(torch.long)
    g2 = torch.Generator(device=device).manual_seed(seed + 2000)
    val_idx = torch.randint(0, C, (M,), generator=g2, device=device,
                              dtype=torch.long)
    keys = codebook[key_idx]
    vals = codebook[val_idx]
    W = (vals.T @ keys) / N_use
    return W, keys, vals, key_idx, val_idx


def measure_recall_at_M(codebook: torch.Tensor, M: int, seed: int,
                          N_use: int, device: torch.device) -> Dict:
    t0 = time.time()
    pre_mem = _mem_gb(device)
    try:
        W, keys, vals, key_idx, val_idx = store_facts(codebook, M, seed,
                                                        N_use, device)
        n = min(N_PROBE, M)
        probe_keys = keys[:n]
        probe_tgt = val_idx[:n]
        out_resp = probe_keys @ W.T
        sims = (codebook @ out_resp.T) / N_use
        pred = torch.argmax(sims, dim=0)
        recall = float((pred == probe_tgt).float().mean().item())
        post_mem = _mem_gb(device)
        del W, keys, vals, out_resp, sims, pred
        _safe_clear(device)
        return {"M": int(M), "success": True, "recall": round(recall, 5),
                "pre_mem_gb": round(pre_mem, 3),
                "post_mem_gb": round(post_mem, 3),
                "elapsed_s": round(time.time() - t0, 2)}
    except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
        _safe_clear(device)
        return {"M": int(M), "success": False,
                "error": str(e)[:300],
                "elapsed_s": round(time.time() - t0, 2)}


def run_one_seed(N_use: int, seed: int, M_sweep: List[int],
                  device: torch.device) -> Dict:
    """Build codebook with first-success strategy; sweep M; measure recall."""
    C = N_use * 3  # standard 3x oversample (matches t1_beta_sweep convention)
    cb, strategy, strat_log = try_codebook(N_use, C, seed, device)
    if cb is None:
        return {"seed": int(seed), "construction_success": False,
                "strategy_log": strat_log, "per_M": []}

    per_M: List[Dict] = []
    max_M_pass = 0
    for M in M_sweep:
        cell = measure_recall_at_M(cb, M, seed, N_use, device)
        per_M.append(cell)
        if cell.get("success") and cell.get("recall", 0.0) >= RECALL_THRESHOLD:
            max_M_pass = max(max_M_pass, M)
    del cb
    _safe_clear(device)
    return {"seed": int(seed),
            "construction_success": True,
            "strategy_used": strategy,
            "strategy_log": strat_log,
            "per_M": per_M,
            "max_M_at_95_recall": int(max_M_pass)}


def compute_verdict(cells: List[Dict], N_use: int) -> Tuple[str, str]:
    if not cells:
        return ("S4_INCONCLUSIVE", "no cells")

    constructed = [c for c in cells if c.get("construction_success")]
    if not constructed:
        return ("S4_HARD_FAIL", f"ALL_STRATEGIES_OOM n={len(cells)}")

    max_M_per_seed = [c.get("max_M_at_95_recall", 0) for c in constructed]
    median_max_M = sorted(max_M_per_seed)[len(max_M_per_seed) // 2]
    target = N_use // 4
    n_strong = sum(1 for m in max_M_per_seed if m > target)

    # OOM at N cell? (any seed succeeded at smaller M but failed at N)
    n_seeds = len(cells)
    n_full_M_pass = sum(1 for c in constructed
                          if any(cell.get("M") == N_use and cell.get("success")
                                 for cell in c.get("per_M", [])))

    detail = (f"constructed={len(constructed)}/{n_seeds} "
              f"max_M={max_M_per_seed} target>{target} "
              f"n_strong={n_strong} n_full_M_pass={n_full_M_pass}")

    if n_strong >= max(1, len(constructed) // 2 + 1):
        return ("S4_HARD_PASS", "MODERN_HOPFIELD_ACTIVATION: " + detail)
    if n_full_M_pass == 0 and n_strong == 0:
        return ("S4_MIDDLE_BAND", "PARTIAL_M_OOM_AT_N: " + detail)
    return ("S4_MIDDLE_BAND", "PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 16384
    device = torch.device("cpu")
    cell = run_one_seed(N_SMOKE, 17, M_SWEEP_SMOKE, device)
    assert "construction_success" in cell
    assert cell["construction_success"] is True
    assert len(cell["per_M"]) > 0
    print(f"[selftest] modern_hopfield_n16384_v7_resilient PASS "
          f"strategy={cell.get('strategy_used')} "
          f"max_M={cell.get('max_M_at_95_recall')}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    M_sweep = M_SWEEP_SMOKE if smoke else M_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] modern_hopfield_n16384_v7_resilient smoke={smoke} N={N_cfg} "
          f"M_sweep={M_sweep} seeds={seeds} done={len(done)} "
          f"device={device.type}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body); continue
        try:
            cell = run_one_seed(N_cfg, seed, M_sweep, device)
            write_partial_key(out_dir, ck, cell)
            cells.append(cell)
            print(f"  seed={seed} ok={cell.get('construction_success')} "
                  f"strategy={cell.get('strategy_used')} "
                  f"max_M={cell.get('max_M_at_95_recall', 'n/a')} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
            print(f"  seed={seed} FAILED: {e}", flush=True)
            _safe_clear(device)

    verdict, vm = compute_verdict(cells, N_cfg)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "modern_hopfield_n16384_v7_resilient",
               "N": N_cfg, "smoke": smoke,
               "M_sweep": M_sweep, "seeds": seeds,
               "cells": cells, "verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
