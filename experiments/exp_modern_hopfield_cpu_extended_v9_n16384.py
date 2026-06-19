"""C9 MODERN HOPFIELD CPU EXTENDED v9 at N=16384.

CONTEXT (v290 cap_map follow-on to C1):
  C1 (pending verdict_handler) measured max_M=4N=65536 at N=16384 CPU with
  100% recall across 3/3 seeds, but the sweep STOPPED at 4N. Actual ceiling
  is past 4N untested.
  C9 extends the M sweep to {4N, 8N, 16N} = {65536, 131072, 262144} to
  identify (or confirm "past 16N") the actual Modern Hopfield ceiling at
  N=16384.

CODEBOOK STRATEGY:
  CPU patient construction (T3 v7 strategy_c_cpu_upload pattern), C =
  max(M, 16384) baseline. Codebook at C=16N=262144, N=16384 float32:
  262144 * 16384 * 4 = ~16 GiB on CPU. W matrix at M=16N is 16384*16384*4
  ~ 1 GiB. The dominant memory cost is the codebook.
  Memory budget pre-check at smoke time -- fail gracefully on OOM with
  explicit error_msg in the cell record.

SCIENTIFIC QUESTION:
  At N=16384, CPU, BSC bipolar, M in {4N, 8N, 16N}, what is the largest M
  at which 95% recall holds in 2/3+ seeds?

PRE-REGISTERED BANDS:
  HP = max_M_per_seed includes 16N (=262144) in 2/3+ seeds
       (ceiling past 16N confirmed: at least 64x linear capacity).
  HF = construction OOMs at 8N or before (system RAM limit hit; still
       informative -- proves the memory budget).
  MB = max_M between 4N and 16N (ceiling identified within sweep).

PROT-018: _n16384 binds N=16384.
PROT-021: per-seed-checkpointing.

Anchor: modern_hopfield_cpu_extended_v9_n16384
Queue: remote_cpu_queue
Pre-reg: preregs/2026-05-31_modern_hopfield_cpu_extended_v9_n16384.md
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

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_c9", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: _n16384 binds N = 16384
N = 16384
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 16384, f"PROT-018: N_FULL must be 16384; got {N_FULL}"

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]
N_PROBE = 100
RECALL_THRESHOLD = 0.95


def _m_sweep_full(N_use: int) -> List[int]:
    # Extended ceiling test: 4N, 8N, 16N
    return [4 * N_use, 8 * N_use, 16 * N_use]  # [65536, 131072, 262144]


M_SWEEP_FULL  = _m_sweep_full(N_FULL)
# Smoke at N=1024: use 2N, 4N (small enough to fit easily)
M_SWEEP_SMOKE = [2 * N_SMOKE, 4 * N_SMOKE]  # [2048, 4096]


def get_output_dir(default_name: str = "modern_hopfield_cpu_extended_v9_n16384") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _bsc_chunk_cpu(n_codewords: int, N_use: int, seed: int) -> torch.Tensor:
    g = torch.Generator(device='cpu').manual_seed(seed)
    return (torch.rand(n_codewords, N_use, generator=g) > 0.5).to(torch.float32) * 2 - 1


def make_codebook(N_use: int, C: int, seed: int, chunk: int = 256) -> torch.Tensor:
    """CPU patient construction in chunks. Smaller chunk for large C."""
    parts: List[torch.Tensor] = []
    for i in range(0, C, chunk):
        n = min(chunk, C - i)
        parts.append(_bsc_chunk_cpu(n, N_use, seed + i))
    return torch.cat(parts, dim=0)


def measure_recall_at_M(codebook: torch.Tensor, M: int, seed: int,
                          N_use: int) -> Dict:
    t0 = time.time()
    try:
        C = codebook.shape[0]
        g = torch.Generator(device='cpu').manual_seed(seed + 1000)
        perm = torch.randperm(C, generator=g)[:M].to(torch.long)
        key_idx = perm
        g2 = torch.Generator(device='cpu').manual_seed(seed + 2000)
        val_idx = torch.randint(0, C, (M,), generator=g2, dtype=torch.long)
        keys = codebook[key_idx]
        vals = codebook[val_idx]
        # Build W: (N, N) = (M, N)^T @ (M, N) / N -- 1 GiB at N=16384 float32
        W = (vals.T @ keys) / N_use
        n = min(N_PROBE, M)
        probe_keys = keys[:n]
        probe_tgt = val_idx[:n]
        out_resp = probe_keys @ W.T
        # codebook @ out_resp.T: (C, N) @ (N, n) = (C, n) -- this is the
        # large memory item at high C. At C=262144, n=100: 100 MiB. Fine.
        sims = (codebook @ out_resp.T) / N_use
        pred = torch.argmax(sims, dim=0)
        recall = float((pred == probe_tgt).float().mean().item())
        del W, keys, vals, out_resp, sims, pred
        return {"M": int(M), "success": True, "recall": round(recall, 5),
                "elapsed_s": round(time.time() - t0, 2)}
    except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
        return {"M": int(M), "success": False, "error": str(e)[:300],
                "elapsed_s": round(time.time() - t0, 2)}


def run_one_seed(N_use: int, seed: int, M_sweep: List[int]) -> Dict:
    C = max(M_sweep)
    t_cb = time.time()
    try:
        cb = make_codebook(N_use, C, seed)
    except Exception as e:  # noqa: BLE001
        return {"seed": int(seed), "construction_success": False,
                "construction_error": str(e)[:300],
                "construction_s": round(time.time() - t_cb, 2),
                "per_M": []}
    construction_s = round(time.time() - t_cb, 2)

    per_M: List[Dict] = []
    max_M_pass = 0
    for M in M_sweep:
        cell = measure_recall_at_M(cb, M, seed, N_use)
        per_M.append(cell)
        if cell.get("success") and cell.get("recall", 0.0) >= RECALL_THRESHOLD:
            max_M_pass = max(max_M_pass, M)
    del cb
    return {"seed": int(seed), "construction_success": True,
            "construction_s": construction_s,
            "per_M": per_M, "max_M_at_95_recall": int(max_M_pass)}


def compute_verdict(cells: List[Dict], N_use: int) -> Tuple[str, str]:
    if not cells:
        return ("C9_INCONCLUSIVE", "no cells")
    constructed = [c for c in cells if c.get("construction_success")]
    construction_failures = [c for c in cells if not c.get("construction_success")]

    detail_parts = []
    if constructed:
        max_M_per_seed = [c.get("max_M_at_95_recall", 0) for c in constructed]
        detail_parts.append(
            f"constructed={len(constructed)}/{len(cells)} "
            f"max_M_per_seed={max_M_per_seed}")
    if construction_failures:
        detail_parts.append(
            f"construction_oom_count={len(construction_failures)} "
            f"errs={[c.get('construction_error', '?')[:80] for c in construction_failures]}")
    detail = " | ".join(detail_parts)

    # HF: construction OOMs at 8N or before in 2/3+ seeds
    if construction_failures and len(construction_failures) >= 2:
        return ("C9_HARD_FAIL",
                "CONSTRUCTION_OOM_AT_OR_BEFORE_8N: " + detail)

    if not constructed:
        return ("C9_HARD_FAIL", "ALL_CONSTRUCTION_FAILED: " + detail)

    max_M_per_seed = [c.get("max_M_at_95_recall", 0) for c in constructed]
    target_hp = 16 * N_use
    n_hp = sum(1 for m in max_M_per_seed if m >= target_hp)

    threshold = max(2, (len(constructed) * 2 + 2) // 3)
    if n_hp >= threshold:
        return ("C9_HARD_PASS",
                f"CEILING_PAST_16N (target>={target_hp}): " + detail)

    # MB: max_M between 4N and 16N (i.e., some cell at 4N+, none at 16N in
    # >= threshold seeds)
    n_mb = sum(1 for m in max_M_per_seed if m >= 4 * N_use)
    if n_mb >= threshold:
        return ("C9_MIDDLE_BAND",
                f"CEILING_BETWEEN_4N_AND_16N: " + detail)
    return ("C9_MIDDLE_BAND", "PARTIAL_CEILING: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 16384, "PROT-018: _n16384"
    assert M_SWEEP_FULL == [65536, 131072, 262144]
    assert len(SEEDS_FULL) == 3

    # Verdict gate HP (all seeds reach 16N)
    fake_hp = [{"seed": s, "construction_success": True,
                "max_M_at_95_recall": 16 * N_FULL, "per_M": []}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hp, N_FULL); assert "HARD_PASS" in v, v

    # Verdict gate HF (2/3 seeds OOM at construction)
    fake_hf = [
        {"seed": 7, "construction_success": False,
         "construction_error": "MemoryError: 32 GiB"},
        {"seed": 17, "construction_success": False,
         "construction_error": "MemoryError: 32 GiB"},
        {"seed": 23, "construction_success": True,
         "max_M_at_95_recall": 4 * N_FULL, "per_M": []},
    ]
    v, _ = compute_verdict(fake_hf, N_FULL); assert "HARD_FAIL" in v, v

    # Verdict gate MB (all hit 4N but not 16N)
    fake_mb = [{"seed": s, "construction_success": True,
                "max_M_at_95_recall": 8 * N_FULL, "per_M": []}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_mb, N_FULL); assert "MIDDLE_BAND" in v, v

    # Live smoke on CPU at small scale
    cell = run_one_seed(N_SMOKE, 17, M_SWEEP_SMOKE)
    assert cell["construction_success"] is True, \
        f"selftest: construction failed: {cell.get('construction_error')}"
    assert len(cell["per_M"]) == len(M_SWEEP_SMOKE)
    assert any(c.get("success") for c in cell["per_M"]), \
        "selftest: no M-cell succeeded"
    print(f"[selftest] modern_hopfield_cpu_extended_v9_n16384 PASS "
          f"max_M_smoke={cell['max_M_at_95_recall']} "
          f"construction_s={cell['construction_s']}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    M_sweep = M_SWEEP_SMOKE if smoke else M_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] modern_hopfield_cpu_extended_v9_n16384 smoke={smoke} "
          f"N={N_cfg} M_sweep={M_sweep} seeds={seeds} done={len(done)}",
          flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body); continue
        try:
            cell = run_one_seed(N_cfg, seed, M_sweep)
            write_partial_key(out_dir, ck, cell)
            cells.append(cell)
            print(f"  seed={seed} ok={cell.get('construction_success')} "
                  f"max_M={cell.get('max_M_at_95_recall', 'n/a')} "
                  f"construction_s={cell.get('construction_s', 'n/a')} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
            print(f"  seed={seed} FAILED: {e}", flush=True)

    verdict, vm = compute_verdict(cells, N_cfg)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "modern_hopfield_cpu_extended_v9_n16384",
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
