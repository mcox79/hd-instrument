"""C1 MODERN HOPFIELD CPU BACKUP EXTENDED v1 at N=16384.

CONTEXT (v290 cap_map follow-on):
  T3 confirmed max_M >= N at N=16384 CPU but the sweep stopped at M=N.
  C1 extends to 2N, 4N on CPU as insurance + ceiling-identification.

CODEBOOK STRATEGY: CPU patient construction (T3 v7 strategy_c_cpu_upload
pattern). At N=16384, M=4N=65536: codebook 65536 x 16384 float32 = 4 GiB on
CPU. We oversample C = max(M, 16384 baseline).

SCIENTIFIC QUESTION:
  At N=16384, CPU, BSC, M in {N, 2N, 4N}, what is max_M_at_95_recall?

PRE-REGISTERED BANDS:
  HP = max_M_at_95_recall >= 2N (= 32768) on >=2/3 seeds.
       (Ceiling identified within sweep; T3 finding extends.)
  HF = max_M_at_95_recall = N on >=2/3 seeds.
       T3 finding was at the test ceiling; actual capacity bend untested.
  MB = otherwise.

PROT-018: _n16384 binds N = 16384.

Anchor: modern_hopfield_cpu_backup_extended_v1_n16384
Queue: remote_cpu_queue
Pre-reg: preregs/2026-05-30_modern_hopfield_cpu_backup_extended_v1_n16384.md
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_c1", _ck_path)
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
    return [N_use, 2 * N_use, 4 * N_use]  # [16384, 32768, 65536]


M_SWEEP_FULL  = _m_sweep_full(N_FULL)
M_SWEEP_SMOKE = [N_SMOKE // 2, N_SMOKE]  # [512, 1024]


def get_output_dir(default_name: str = "modern_hopfield_cpu_backup_extended_v1_n16384") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _bsc_chunk_cpu(n_codewords: int, N_use: int, seed: int) -> torch.Tensor:
    g = torch.Generator(device='cpu').manual_seed(seed)
    return (torch.rand(n_codewords, N_use, generator=g) > 0.5).to(torch.float32) * 2 - 1


def make_codebook(N_use: int, C: int, seed: int, chunk: int = 512) -> torch.Tensor:
    """CPU patient construction in chunks."""
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
        W = (vals.T @ keys) / N_use
        n = min(N_PROBE, M)
        probe_keys = keys[:n]
        probe_tgt = val_idx[:n]
        out_resp = probe_keys @ W.T
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
    try:
        cb = make_codebook(N_use, C, seed)
    except Exception as e:  # noqa: BLE001
        return {"seed": int(seed), "construction_success": False,
                "construction_error": str(e)[:300], "per_M": []}

    per_M: List[Dict] = []
    max_M_pass = 0
    for M in M_sweep:
        cell = measure_recall_at_M(cb, M, seed, N_use)
        per_M.append(cell)
        if cell.get("success") and cell.get("recall", 0.0) >= RECALL_THRESHOLD:
            max_M_pass = max(max_M_pass, M)
    del cb
    return {"seed": int(seed), "construction_success": True,
            "per_M": per_M, "max_M_at_95_recall": int(max_M_pass)}


def compute_verdict(cells: List[Dict], N_use: int) -> Tuple[str, str]:
    if not cells:
        return ("C1_INCONCLUSIVE", "no cells")
    constructed = [c for c in cells if c.get("construction_success")]
    if not constructed:
        return ("C1_HARD_FAIL", f"ALL_CONSTRUCTION_FAILED n={len(cells)}")

    max_M_per_seed = [c.get("max_M_at_95_recall", 0) for c in constructed]
    n_hp = sum(1 for m in max_M_per_seed if m >= 2 * N_use)
    n_hf = sum(1 for m in max_M_per_seed if m == N_use)

    detail = (f"constructed={len(constructed)}/{len(cells)} "
              f"max_M_per_seed={max_M_per_seed} target_hp>={2*N_use} target_hf={N_use}")

    threshold = max(2, (len(constructed) * 2 + 2) // 3)
    if n_hp >= threshold:
        return ("C1_HARD_PASS", "CEILING_EXTENDS_PAST_2N: " + detail)
    if n_hf >= threshold:
        return ("C1_HARD_FAIL", "CEILING_AT_N_LINEAR: " + detail)
    return ("C1_MIDDLE_BAND", "PARTIAL_CEILING: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 16384, "PROT-018: _n16384"
    assert M_SWEEP_FULL == [16384, 32768, 65536]
    assert len(SEEDS_FULL) == 3

    # Verdict gate HP
    fake_hp = [{"seed": s, "construction_success": True,
                "max_M_at_95_recall": 2 * N_FULL, "per_M": []}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hp, N_FULL); assert "HARD_PASS" in v, v

    # Verdict gate HF (all stuck at N)
    fake_hf = [{"seed": s, "construction_success": True,
                "max_M_at_95_recall": N_FULL, "per_M": []}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hf, N_FULL); assert "HARD_FAIL" in v, v

    # Live smoke on CPU
    cell = run_one_seed(N_SMOKE, 17, M_SWEEP_SMOKE)
    assert cell["construction_success"] is True, \
        f"selftest: construction failed: {cell.get('construction_error')}"
    assert len(cell["per_M"]) == len(M_SWEEP_SMOKE)
    assert any(c.get("success") for c in cell["per_M"]), \
        "selftest: no M-cell succeeded"
    print(f"[selftest] modern_hopfield_cpu_backup_extended_v1_n16384 PASS "
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
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    M_sweep = M_SWEEP_SMOKE if smoke else M_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] modern_hopfield_cpu_backup_extended_v1_n16384 smoke={smoke} "
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
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
            print(f"  seed={seed} FAILED: {e}", flush=True)

    verdict, vm = compute_verdict(cells, N_cfg)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "modern_hopfield_cpu_backup_extended_v1_n16384",
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
