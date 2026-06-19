"""C9 MODERN HOPFIELD CPU EXTENDED v10 at N=16384.

CONTEXT (v295 cap_map ceiling-extension follow-on to C9 v9 HARD_PASS):
  v9 HARD_PASS'd M in {4N, 8N, 16N} = {65536, 131072, 262144} at N=16384 BSC
  with 9/9 cells unanimous recall=1.0. Cap_map LIFT to 0.78-0.92. The actual
  M-ceiling remains hidden past 16N=262144.
  v10 uses a wide sparse cliff-locator grid {20N, 32N, 64N} to either locate
  the cliff or confirm it is past 64N=1048576 (a 64x linear capacity multiple).

M-GRID RATIONALE:
  20N = 327680  -- just past v9's top; tells us if 16N was borderline or easy
  32N = 524288  -- 2x past 16N; significant jump
  64N = 1048576 -- probe upper extreme; locates cliff or forces another LIFT

SCIENTIFIC QUESTION:
  At N=16384, CPU, BSC bipolar, M in {20N, 32N, 64N}, what is the largest M
  at which 95% recall holds in 3/5+ seeds?

PRE-REGISTERED BANDS:
  HP = max_M_per_seed includes 64N (=1048576) in 3/5+ seeds
       (ceiling past 64N confirmed: row lifts to 0.85-0.95+).
  HF = construction OOMs at 20N or 32N in 3/5+ seeds before recall measured
       (memory wall; informative but cannot distinguish cliff from RAM limit).
  MB = max_M between 20N and 32N in 3/5+ seeds, OR cliff located at 64N
       (ceiling identified within sweep range).

NOTE on HF: HARD_FAIL here is NOT a scientific failure -- it reports the
system RAM limit as the effective ceiling, which is itself a substrate fact.

PROT-018: _n16384 binds N=16384.
PROT-019: timeout >= 14400s.
PROT-021: per-seed checkpointing.

Anchor: modern_hopfield_cpu_extended_v10_n16384
Queue: remote_cpu_queue
Pre-reg: preregs/2026-05-31_modern_hopfield_cpu_extended_v10_n16384.md
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_c9v10", _ck_path)
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

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_PROBE = 100
RECALL_THRESHOLD = 0.95

# Wide sparse cliff-locator: 20N, 32N, 64N
M_SWEEP_FULL  = [20 * N_FULL, 32 * N_FULL, 64 * N_FULL]   # [327680, 524288, 1048576]
# Smoke at N_SMOKE=1024: proportional small grid
M_SWEEP_SMOKE = [20 * N_SMOKE, 32 * N_SMOKE]              # [20480, 32768]

assert M_SWEEP_FULL == [327680, 524288, 1048576], f"M_SWEEP_FULL mismatch: {M_SWEEP_FULL}"


def get_output_dir(default_name: str = "modern_hopfield_cpu_extended_v10_n16384") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _bsc_chunk_cpu(n_codewords: int, N_use: int, seed: int) -> torch.Tensor:
    g = torch.Generator(device='cpu').manual_seed(seed)
    return (torch.rand(n_codewords, N_use, generator=g) > 0.5).to(torch.float32) * 2 - 1


def make_codebook(N_use: int, C: int, seed: int, chunk: int = 256) -> torch.Tensor:
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
        # Build W: (N, N) = (M, N)^T @ (M, N) / N -- ~1 GiB at N=16384 float32
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
        print(f"    [seed={seed}] M={M} recall={cell.get('recall','OOM')} "
              f"elapsed={cell.get('elapsed_s','?')}s", flush=True)
    del cb
    return {"seed": int(seed), "construction_success": True,
            "construction_s": construction_s,
            "per_M": per_M, "max_M_at_95_recall": int(max_M_pass)}


def compute_verdict(cells: List[Dict], N_use: int) -> Tuple[str, str]:
    if not cells:
        return ("V10_INCONCLUSIVE", "no cells")
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

    n_total = len(cells)
    hp_threshold = max(3, (n_total * 3 + 4) // 5)   # 3/5 majority

    # HF: construction OOMs at or before 32N in 3+/5 seeds
    if len(construction_failures) >= hp_threshold:
        return ("V10_HARD_FAIL",
                "CONSTRUCTION_OOM_AT_OR_BEFORE_32N: " + detail)

    if not constructed:
        return ("V10_HARD_FAIL", "ALL_CONSTRUCTION_FAILED: " + detail)

    max_M_per_seed = [c.get("max_M_at_95_recall", 0) for c in constructed]
    target_hp = 64 * N_use  # 1048576

    n_hp = sum(1 for m in max_M_per_seed if m >= target_hp)
    if n_hp >= hp_threshold:
        return ("V10_HARD_PASS",
                f"CEILING_PAST_64N (target>={target_hp}): " + detail)

    # MB: cliff located within sweep (20N..64N range, at least 20N succeeded
    # in hp_threshold seeds)
    target_mb = 20 * N_use  # 327680
    n_mb = sum(1 for m in max_M_per_seed if m >= target_mb)
    if n_mb >= hp_threshold:
        return ("V10_MIDDLE_BAND",
                f"CEILING_BETWEEN_20N_AND_64N: " + detail)

    return ("V10_MIDDLE_BAND", "CEILING_AT_OR_BELOW_20N: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 16384, "PROT-018: _n16384"
    assert M_SWEEP_FULL == [327680, 524288, 1048576], f"M_SWEEP_FULL: {M_SWEEP_FULL}"
    assert len(SEEDS_FULL) == 5

    # Verdict gate HP (3+/5 seeds reach 64N)
    fake_hp = [{"seed": s, "construction_success": True,
                "max_M_at_95_recall": 64 * N_FULL, "per_M": []}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hp, N_FULL)
    assert "HARD_PASS" in v, f"HP gate failed: {v}"

    # Verdict gate HF (3/5 seeds OOM at construction)
    fake_hf = [
        {"seed": 7,  "construction_success": False, "construction_error": "MemoryError"},
        {"seed": 17, "construction_success": False, "construction_error": "MemoryError"},
        {"seed": 23, "construction_success": False, "construction_error": "MemoryError"},
        {"seed": 31, "construction_success": True,  "max_M_at_95_recall": 20 * N_FULL, "per_M": []},
        {"seed": 41, "construction_success": True,  "max_M_at_95_recall": 20 * N_FULL, "per_M": []},
    ]
    v, _ = compute_verdict(fake_hf, N_FULL)
    assert "HARD_FAIL" in v, f"HF gate failed: {v}"

    # Verdict gate MB (all reach 20N but not 64N)
    fake_mb = [{"seed": s, "construction_success": True,
                "max_M_at_95_recall": 32 * N_FULL, "per_M": []}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_mb, N_FULL)
    assert "MIDDLE_BAND" in v, f"MB gate failed: {v}"

    # Live smoke on CPU at small scale
    cell = run_one_seed(N_SMOKE, 17, M_SWEEP_SMOKE)
    assert cell["construction_success"] is True, \
        f"selftest: construction failed: {cell.get('construction_error')}"
    assert len(cell["per_M"]) == len(M_SWEEP_SMOKE), \
        f"expected {len(M_SWEEP_SMOKE)} M cells, got {len(cell['per_M'])}"
    assert any(c.get("success") for c in cell["per_M"]), \
        "selftest: no M-cell succeeded"
    print(f"[selftest] modern_hopfield_cpu_extended_v10_n16384 PASS "
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
    print(f"[run] modern_hopfield_cpu_extended_v10_n16384 smoke={smoke} "
          f"N={N_cfg} M_sweep={M_sweep} seeds={seeds} done={len(done)}",
          flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body)
                continue
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
    summary = {"anchor": "modern_hopfield_cpu_extended_v10_n16384",
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
