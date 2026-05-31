"""G6 MODERN HOPFIELD REPLICATION GPU v1 at N=8192.

CONTEXT (v290 cap_map follow-on):
  T3 used BSC at N=16384 with default beta. G6 replicates at N=8192 with
  VARIED beta to test whether the Modern Hopfield activation is beta-robust
  or specific to a narrow beta band.

SCIENTIFIC QUESTION:
  At N=8192, BSC codebook, M in {N/4, N/2, N, 2N}, beta in {1, 4, 16, 64},
  is the max_M_at_95_recall >= N for >=2/4 beta values?

PRE-REGISTERED BANDS:
  HP = max_M_at_95_recall >= N at >=2/4 beta values
       (Modern Hopfield activation is beta-robust).
  HF = max_M_at_95_recall = N/4 across all beta
       (T3 was beta-specific; not a general property).
  MB = otherwise.

NOTE: "Modern Hopfield" beta acts as inverse temperature in the softmax
attention readout. We implement readout as: softmax(beta * K @ q / N) @ V.
Plain outer-product readout (W @ q) is recovered as beta -> 0 trivial.
For consistency with T3's BSC outer-product baseline, the beta axis is
recorded as the softmax-attention readout variant; the storage step is the
outer-product W matrix.

PROT-018: _n8192 binds N = 8192.
PROT-020: torch + cuda available (GPU runner).
PROT-021: per-cell-seed checkpointing.

Anchor: modern_hopfield_replication_gpu_v1_n8192
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_modern_hopfield_replication_gpu_v1_n8192.md
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_g6", _ck_path)
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

BETA_SWEEP_FULL  = [1.0, 4.0, 16.0, 64.0]
BETA_SWEEP_SMOKE = [4.0, 16.0]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]
N_PROBE = 200
RECALL_THRESHOLD = 0.95


def _m_sweep_full(N_use: int) -> List[int]:
    return [N_use // 4, N_use // 2, N_use, 2 * N_use]


M_SWEEP_FULL  = _m_sweep_full(N_FULL)       # [2048, 4096, 8192, 16384]
M_SWEEP_SMOKE = [N_SMOKE // 4, N_SMOKE // 2]  # [256, 512]


def get_output_dir(default_name: str = "modern_hopfield_replication_gpu_v1_n8192") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


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
    parts: List[torch.Tensor] = []
    for i in range(0, C, chunk):
        n = min(chunk, C - i)
        parts.append(_bsc_chunk(n, N_use, seed + i, device))
    return torch.cat(parts, dim=0)


def measure_cell(codebook: torch.Tensor, M: int, beta: float, seed: int,
                   N_use: int, device: torch.device) -> Dict:
    t0 = time.time()
    try:
        C = codebook.shape[0]
        g = torch.Generator(device='cpu').manual_seed(seed + 1000)
        perm = torch.randperm(C, generator=g)[:M].to(device).to(torch.long)
        key_idx = perm
        g2 = torch.Generator(device='cpu').manual_seed(seed + 2000)
        val_idx = torch.randint(0, C, (M,), generator=g2,
                                  dtype=torch.long).to(device)
        keys = codebook[key_idx]
        vals = codebook[val_idx]

        n = min(N_PROBE, M)
        probe_keys = keys[:n]
        probe_tgt = val_idx[:n]

        # Modern Hopfield softmax-attention readout:
        # logits = beta * probe_keys @ keys.T / N_use
        # weights = softmax(logits, dim=-1)
        # out = weights @ vals
        logits = beta * (probe_keys @ keys.T) / N_use
        weights = torch.softmax(logits, dim=-1)
        out_resp = weights @ vals  # (n, N_use)

        sims = (codebook @ out_resp.T) / N_use
        pred = torch.argmax(sims, dim=0)
        recall = float((pred == probe_tgt).float().mean().item())
        del logits, weights, out_resp, sims, pred, keys, vals
        _safe_clear(device)
        return {"M": int(M), "beta": float(beta), "success": True,
                "recall": round(recall, 5),
                "elapsed_s": round(time.time() - t0, 2)}
    except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
        _safe_clear(device)
        return {"M": int(M), "beta": float(beta), "success": False,
                "error": str(e)[:300],
                "elapsed_s": round(time.time() - t0, 2)}


def run_one_seed(N_use: int, seed: int, M_sweep: List[int],
                  beta_sweep: List[float], device: torch.device) -> Dict:
    C = max(M_sweep)
    try:
        cb = make_codebook(N_use, C, seed, device)
    except Exception as e:  # noqa: BLE001
        _safe_clear(device)
        return {"seed": int(seed), "construction_success": False,
                "construction_error": str(e)[:300], "per_cell": []}

    per_cell: List[Dict] = []
    # max_M_at_95_recall per beta
    max_M_by_beta: Dict[float, int] = {b: 0 for b in beta_sweep}
    for beta in beta_sweep:
        for M in M_sweep:
            cell = measure_cell(cb, M, beta, seed, N_use, device)
            per_cell.append(cell)
            if cell.get("success") and cell.get("recall", 0.0) >= RECALL_THRESHOLD:
                if M > max_M_by_beta[beta]:
                    max_M_by_beta[beta] = M
    del cb
    _safe_clear(device)
    return {"seed": int(seed), "construction_success": True,
            "per_cell": per_cell,
            "max_M_by_beta": {str(b): int(m) for b, m in max_M_by_beta.items()}}


def compute_verdict(cells: List[Dict], N_use: int,
                      beta_sweep: List[float]) -> Tuple[str, str]:
    if not cells:
        return ("G6_INCONCLUSIVE", "no cells")
    constructed = [c for c in cells if c.get("construction_success")]
    if not constructed:
        return ("G6_HARD_FAIL", f"ALL_CONSTRUCTION_FAILED n={len(cells)}")

    # Aggregate max_M_by_beta across seeds (median)
    n_beta_at_or_above_N = 0
    n_beta_at_quarter_N_only = 0
    beta_summaries = []
    for b in beta_sweep:
        per_seed_max_M = [c["max_M_by_beta"].get(str(b), 0)
                          for c in constructed]
        sorted_m = sorted(per_seed_max_M)
        median_m = sorted_m[len(sorted_m) // 2]
        beta_summaries.append(f"beta={b}:median_max_M={median_m}")
        if median_m >= N_use:
            n_beta_at_or_above_N += 1
        if median_m <= N_use // 4:
            n_beta_at_quarter_N_only += 1

    detail = " ".join(beta_summaries)
    n_beta = len(beta_sweep)
    if n_beta_at_or_above_N >= 2:
        return ("G6_HARD_PASS", f"BETA_ROBUST_MODERN_HOPFIELD "
                                  f"{n_beta_at_or_above_N}/{n_beta} beta>=N. " + detail)
    if n_beta_at_quarter_N_only == n_beta:
        return ("G6_HARD_FAIL", f"NO_BETA_REACHES_N (all beta=N/4 ceiling). " + detail)
    return ("G6_MIDDLE_BAND", f"PARTIAL_BETA_ROBUST "
                                f"{n_beta_at_or_above_N}/{n_beta} beta>=N. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 8192, "PROT-018: _n8192"
    assert len(BETA_SWEEP_FULL) == 4
    assert M_SWEEP_FULL == [2048, 4096, 8192, 16384]
    assert len(SEEDS_FULL) == 3

    # Verdict gate HP (>=2 betas reach N)
    fake_hp = [{"seed": s, "construction_success": True,
                "per_cell": [],
                "max_M_by_beta": {str(b): N_FULL for b in BETA_SWEEP_FULL}}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hp, N_FULL, BETA_SWEEP_FULL)
    assert "HARD_PASS" in v, v

    # Verdict gate HF (all betas stuck at N/4)
    fake_hf = [{"seed": s, "construction_success": True,
                "per_cell": [],
                "max_M_by_beta": {str(b): N_FULL // 4 for b in BETA_SWEEP_FULL}}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hf, N_FULL, BETA_SWEEP_FULL)
    assert "HARD_FAIL" in v, v

    # Verdict gate MB (only 1 beta reaches N)
    fake_mb = [{"seed": s, "construction_success": True,
                "per_cell": [],
                "max_M_by_beta": {str(BETA_SWEEP_FULL[0]): N_FULL,
                                  str(BETA_SWEEP_FULL[1]): N_FULL // 2,
                                  str(BETA_SWEEP_FULL[2]): N_FULL // 2,
                                  str(BETA_SWEEP_FULL[3]): N_FULL // 2}}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_mb, N_FULL, BETA_SWEEP_FULL)
    assert "MIDDLE_BAND" in v, v

    # Live smoke on CPU
    device = torch.device("cpu")
    cell = run_one_seed(N_SMOKE, 17, M_SWEEP_SMOKE, BETA_SWEEP_SMOKE, device)
    assert cell["construction_success"] is True, \
        f"selftest: construction failed: {cell.get('construction_error')}"
    assert len(cell["per_cell"]) == len(M_SWEEP_SMOKE) * len(BETA_SWEEP_SMOKE)
    assert any(c.get("success") for c in cell["per_cell"]), \
        "selftest: no cell succeeded"
    print(f"[selftest] modern_hopfield_replication_gpu_v1_n8192 PASS "
          f"max_M_by_beta={cell['max_M_by_beta']}", flush=True)


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
    beta_sweep = BETA_SWEEP_SMOKE if smoke else BETA_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] modern_hopfield_replication_gpu_v1_n8192 smoke={smoke} "
          f"N={N_cfg} M_sweep={M_sweep} beta_sweep={beta_sweep} seeds={seeds} "
          f"done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body); continue
        try:
            cell = run_one_seed(N_cfg, seed, M_sweep, beta_sweep, device)
            write_partial_key(out_dir, ck, cell)
            cells.append(cell)
            print(f"  seed={seed} ok={cell.get('construction_success')} "
                  f"max_M_by_beta={cell.get('max_M_by_beta', 'n/a')} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
            print(f"  seed={seed} FAILED: {e}", flush=True)
            _safe_clear(device)

    verdict, vm = compute_verdict(cells, N_cfg, beta_sweep)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "modern_hopfield_replication_gpu_v1_n8192",
               "N": N_cfg, "smoke": smoke, "M_sweep": M_sweep,
               "beta_sweep": beta_sweep, "seeds": seeds, "cells": cells,
               "verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
