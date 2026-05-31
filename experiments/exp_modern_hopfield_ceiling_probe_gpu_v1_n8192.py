"""G5 MODERN HOPFIELD CEILING PROBE GPU v1 at N=8192.

CONTEXT (v290 cap_map follow-on):
  T3 (modern_hopfield_n16384_v7_resilient) confirmed max_M >= N at N=16384
  CPU but the sweep stopped at M=N. P2 sub1 confirmed N=8192 GPU works.
  G5 extends the M sweep past N at the GPU-feasible regime to identify the
  actual ceiling (or confirm no ceiling within 8N).

SCIENTIFIC QUESTION:
  At N=8192, BSC codebook, M in {N, 2N, 4N, 8N}, what is the actual
  max_M_at_95_recall? Is the Modern Hopfield activation linear-with-N or
  super-linear?

PRE-REGISTERED BANDS:
  HP = max_M_at_95_recall >= 2N (= 16384) on >=2/3 seeds.
       Extends past linear, ceiling within sweep.
  HF = max_M_at_95_recall = N (= 8192) on >=2/3 seeds.
       T3 finding at N=16384 doesn't generalize to N=8192.
  MB = otherwise.

PROT-018: _n8192 binds N = 8192.
PROT-020: torch + cuda available (GPU runner).
PROT-021: per-cell-seed checkpointing.

Anchor: modern_hopfield_ceiling_probe_gpu_v1_n8192
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_modern_hopfield_ceiling_probe_gpu_v1_n8192.md
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
from typing import Dict, List, Optional, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_g5", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: _n8192 binds N = 8192
N = 8192
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]
N_PROBE = 200
RECALL_THRESHOLD = 0.95


def _m_sweep_full(N_use: int) -> List[int]:
    # M in {N, 2N, 4N, 8N}
    return [N_use, 2 * N_use, 4 * N_use, 8 * N_use]


M_SWEEP_FULL  = _m_sweep_full(N_FULL)       # [8192, 16384, 32768, 65536]
M_SWEEP_SMOKE = [N_SMOKE // 2, N_SMOKE]     # [512, 1024]


def get_output_dir(default_name: str = "modern_hopfield_ceiling_probe_gpu_v1_n8192") -> Path:
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


def _bsc_chunk(n_codewords: int, N_use: int, seed: int,
                 device: torch.device) -> torch.Tensor:
    g = torch.Generator(device=device).manual_seed(seed)
    return (torch.rand(n_codewords, N_use, generator=g, device=device) > 0.5).to(torch.float32) * 2 - 1


def make_codebook(N_use: int, C: int, seed: int,
                    device: torch.device, chunk: int = 256) -> torch.Tensor:
    """Build codebook of C codewords in chunks (to avoid peak alloc spike)."""
    parts: List[torch.Tensor] = []
    for i in range(0, C, chunk):
        n = min(chunk, C - i)
        parts.append(_bsc_chunk(n, N_use, seed + i, device))
    return torch.cat(parts, dim=0)


def store_facts(codebook: torch.Tensor, M: int, seed: int,
                  N_use: int, device: torch.device):
    """Sample M (key, val) pairs; build W from outer products."""
    C = codebook.shape[0]
    # CPU-gen randperm for safety
    g = torch.Generator(device='cpu').manual_seed(seed + 1000)
    perm = torch.randperm(C, generator=g)[:M].to(device)
    key_idx = perm.to(torch.long)
    g2 = torch.Generator(device='cpu').manual_seed(seed + 2000)
    val_idx = torch.randint(0, C, (M,), generator=g2, dtype=torch.long).to(device)
    keys = codebook[key_idx]
    vals = codebook[val_idx]
    W = (vals.T @ keys) / N_use
    return W, keys, vals, key_idx, val_idx


def measure_recall_at_M(codebook: torch.Tensor, M: int, seed: int,
                          N_use: int, device: torch.device) -> Dict:
    t0 = time.time()
    pre_mem = _mem_gb(device)
    try:
        W, keys, vals, key_idx, val_idx = store_facts(
            codebook, M, seed, N_use, device)
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
    # C must >= max(M_sweep). 8N=65536 codewords at N=8192 = 64*8192 float32 = 2 GiB
    # which is at the edge. Use C = max(M_sweep) (no extra slack) on FULL run.
    C = max(M_sweep)
    try:
        cb = make_codebook(N_use, C, seed, device)
    except Exception as e:  # noqa: BLE001
        _safe_clear(device)
        return {"seed": int(seed), "construction_success": False,
                "construction_error": str(e)[:300], "per_M": []}

    per_M: List[Dict] = []
    max_M_pass = 0
    for M in M_sweep:
        cell = measure_recall_at_M(cb, M, seed, N_use, device)
        per_M.append(cell)
        if cell.get("success") and cell.get("recall", 0.0) >= RECALL_THRESHOLD:
            max_M_pass = max(max_M_pass, M)
    del cb
    _safe_clear(device)
    return {"seed": int(seed), "construction_success": True,
            "per_M": per_M, "max_M_at_95_recall": int(max_M_pass)}


def compute_verdict(cells: List[Dict], N_use: int) -> Tuple[str, str]:
    if not cells:
        return ("G5_INCONCLUSIVE", "no cells")
    constructed = [c for c in cells if c.get("construction_success")]
    if not constructed:
        return ("G5_HARD_FAIL", f"ALL_CONSTRUCTION_FAILED n={len(cells)}")

    max_M_per_seed = [c.get("max_M_at_95_recall", 0) for c in constructed]
    n_seeds = len(constructed)
    n_hp = sum(1 for m in max_M_per_seed if m >= 2 * N_use)
    n_hf = sum(1 for m in max_M_per_seed if m == N_use)

    detail = (f"constructed={n_seeds}/{len(cells)} "
              f"max_M_per_seed={max_M_per_seed} target_hp>={2*N_use} target_hf={N_use}")

    if n_hp >= max(2, (n_seeds * 2 + 2) // 3):
        return ("G5_HARD_PASS", "CEILING_EXTENDS_PAST_2N: " + detail)
    if n_hf >= max(2, (n_seeds * 2 + 2) // 3):
        return ("G5_HARD_FAIL", "CEILING_AT_N_LINEAR: " + detail)
    return ("G5_MIDDLE_BAND", "PARTIAL_CEILING: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 8192, "PROT-018: _n8192"
    assert M_SWEEP_FULL == [8192, 16384, 32768, 65536]
    assert len(SEEDS_FULL) == 3

    # Verdict gate HP (all seeds max_M >= 16384)
    fake_hp = [{"seed": s, "construction_success": True,
                "max_M_at_95_recall": 32768, "per_M": []}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hp, N_FULL); assert "HARD_PASS" in v, v

    # Verdict gate HF (all seeds max_M = N)
    fake_hf = [{"seed": s, "construction_success": True,
                "max_M_at_95_recall": 8192, "per_M": []}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hf, N_FULL); assert "HARD_FAIL" in v, v

    # Verdict gate MB (mixed)
    fake_mb = [{"seed": 7, "construction_success": True,
                "max_M_at_95_recall": 16384, "per_M": []},
               {"seed": 17, "construction_success": True,
                "max_M_at_95_recall": 8192, "per_M": []},
               {"seed": 23, "construction_success": True,
                "max_M_at_95_recall": 4096, "per_M": []}]
    v, _ = compute_verdict(fake_mb, N_FULL); assert "MIDDLE_BAND" in v, v

    # Live smoke on CPU
    device = torch.device("cpu")
    cell = run_one_seed(N_SMOKE, 17, M_SWEEP_SMOKE, device)
    assert cell["construction_success"] is True, \
        f"selftest: construction failed: {cell.get('construction_error')}"
    assert len(cell["per_M"]) == len(M_SWEEP_SMOKE)
    assert any(c.get("success") for c in cell["per_M"]), \
        "selftest: no M-cell succeeded"
    print(f"[selftest] modern_hopfield_ceiling_probe_gpu_v1_n8192 PASS "
          f"max_M_smoke={cell['max_M_at_95_recall']}", flush=True)


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
    print(f"[run] modern_hopfield_ceiling_probe_gpu_v1_n8192 smoke={smoke} "
          f"N={N_cfg} M_sweep={M_sweep} seeds={seeds} done={len(done)} "
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
                  f"max_M={cell.get('max_M_at_95_recall', 'n/a')} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
            print(f"  seed={seed} FAILED: {e}", flush=True)
            _safe_clear(device)

    verdict, vm = compute_verdict(cells, N_cfg)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "modern_hopfield_ceiling_probe_gpu_v1_n8192",
               "N": N_cfg, "smoke": smoke, "M_sweep": M_sweep,
               "seeds": seeds, "cells": cells,
               "verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
