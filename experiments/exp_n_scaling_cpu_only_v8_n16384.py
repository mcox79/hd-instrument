"""T3 N-SCALING CPU-ONLY v8 at N=16384 (Test 22-alt).

Modern Hopfield activation test via CPU-only patient codebook construction.
v4/v5/v6/v7 all GPU-OOM. v8 abandons GPU codebook construction entirely;
uses CPU with explicit memory management (numpy / torch.cpu allocation +
deletion of intermediates between chunks).

DESIGN:
  - BSC codebook (bipolar +/-1 sign tensor) constructed chunkwise on CPU.
    BSC at N=16384 with C=N codewords: C * N bytes float32 = 1 GiB. Built
    one chunk at a time to keep peak well under 4 GiB.
  - Substrate W stays on CPU; all operations on CPU.
  - M sweep [N/8, N/4, N/2, N] = [2048, 4096, 8192, 16384] (4 points).
  - 3 seeds. RSS logged at every chunk allocation.

INSTRUMENTATION:
  Peak RSS (via psutil if available, else 'n/a') logged before/after each
  major allocation. The check at smoke-time asserts peak stays under 12 GiB
  system RAM budget (8 GB GPU is irrelevant here; CPU has 16-32 GiB).

PRE-REGISTERED BANDS:
  HP = construction succeeds across all 4 M-points AND max_M_at_95_recall
       identified AND exceeds N/4=4096 (exponential bend = Modern Hopfield
       activation).
  HF = construction OOMs at system RAM OR linear pattern holds (max_M_at_95
       within +/-20% of N/4).
  MB = construction succeeds at smaller M but OOMs at N=16384 cell.

PROT-018: _n16384 binds N = 16384.
Anchor: n_scaling_cpu_only_v8_n16384
Queue: remote_cpu_queue (CPU-only by design)
Pre-reg: preregs/2026-05-30_n_scaling_cpu_only_v8_n16384.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import gc
import importlib.util
import json
import os
import time
import traceback
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_t3v8", _ck_path)
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

SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]
N_PROBE = 200
RECALL_THRESHOLD = 0.95

# Multi-scale smoke: do the smoke at N_smoke AND N_smoke*4 to catch
# intermediate-scale failures.
N_SMOKE_LARGE = 4096

MEM_HARD_CEILING_GB = 12.0   # system-RAM hard ceiling (the runner has >=16 GB).

# Codebook chunk size in rows. 256 rows of N=16384 floats = 16 MiB per chunk.
CB_CHUNK_ROWS = 256

# Storage batch size (rows of keys processed per outer-product W update).
W_BATCH = 64


def _m_sweep(N_use: int) -> List[int]:
    return [N_use // 8, N_use // 4, N_use // 2, N_use]


M_SWEEP_FULL  = _m_sweep(N_FULL)        # [2048, 4096, 8192, 16384]
M_SWEEP_SMOKE = _m_sweep(N_SMOKE)       # [128, 256, 512, 1024]
M_SWEEP_SMOKE_LARGE = _m_sweep(N_SMOKE_LARGE)  # [512, 1024, 2048, 4096]


def get_output_dir(default_name: str = "n_scaling_cpu_only_v8_n16384") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _rss_gb() -> float:
    """Return current process RSS in GiB; -1.0 if psutil unavailable."""
    try:
        import psutil
        return float(psutil.Process().memory_info().rss / (1024 ** 3))
    except Exception:
        return -1.0


def make_bsc_codebook_cpu_chunked(N_use: int, C: int, seed: int) -> Tuple[torch.Tensor, List[Dict]]:
    """Build a BSC bipolar codebook (C rows x N_use cols) on CPU in chunks.

    Each chunk is generated as random +/-1 float32 and concatenated. RSS
    logged before each chunk. Returns (codebook, rss_log_per_chunk).
    """
    gen = torch.Generator(device='cpu').manual_seed(seed + 91234)
    parts: List[torch.Tensor] = []
    rss_log: List[Dict] = []
    rss_log.append({"event": "pre_codebook", "rss_gb": round(_rss_gb(), 3)})
    n_chunks = (C + CB_CHUNK_ROWS - 1) // CB_CHUNK_ROWS
    for ci in range(n_chunks):
        rs = ci * CB_CHUNK_ROWS
        re = min(C, rs + CB_CHUNK_ROWS)
        rows = re - rs
        # Sample +/-1 directly (no float intermediate larger than needed)
        bits = torch.randint(0, 2, (rows, N_use), generator=gen, dtype=torch.int8)
        chunk = bits.to(torch.float32) * 2.0 - 1.0
        del bits
        parts.append(chunk)
        if ci % max(1, n_chunks // 8) == 0 or ci == n_chunks - 1:
            rss_log.append({"event": f"chunk_{ci}", "rss_gb": round(_rss_gb(), 3)})
        if _rss_gb() > MEM_HARD_CEILING_GB:
            raise MemoryError(
                f"RSS exceeded {MEM_HARD_CEILING_GB} GiB during codebook chunk {ci}/{n_chunks}")
    codebook = torch.cat(parts, dim=0).contiguous()
    del parts
    gc.collect()
    rss_log.append({"event": "post_codebook_cat", "rss_gb": round(_rss_gb(), 3)})
    return codebook, rss_log


def store_facts_cpu(codebook: torch.Tensor, M: int, seed: int,
                    N_use: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, List[Dict]]:
    """Store M random (key, value) facts into W = sum_m (v_m k_m^T) / N.

    Returns (W, key_idx, val_idx, rss_log).
    """
    C = codebook.shape[0]
    gen = torch.Generator(device='cpu').manual_seed(seed)
    k_perm = torch.randperm(C, generator=gen)
    v_perm = torch.randperm(C, generator=gen)
    if M <= C:
        key_idx = k_perm[:M]
        val_idx = v_perm[:M]
    else:
        repeats = (M + C - 1) // C
        key_parts = [torch.randperm(C, generator=gen) for _ in range(repeats)]
        val_parts = [torch.randperm(C, generator=gen) for _ in range(repeats)]
        key_idx = torch.cat(key_parts)[:M]
        val_idx = torch.cat(val_parts)[:M]
        del key_parts, val_parts

    rss_log: List[Dict] = []
    rss_log.append({"event": "pre_W_alloc", "rss_gb": round(_rss_gb(), 3)})
    W = torch.zeros(N_use, N_use, dtype=torch.float32)
    rss_log.append({"event": "post_W_alloc", "rss_gb": round(_rss_gb(), 3)})
    inv_N = 1.0 / float(N_use)
    n_batches = (M + W_BATCH - 1) // W_BATCH
    for bi in range(n_batches):
        s = bi * W_BATCH
        e = min(M, s + W_BATCH)
        ki = key_idx[s:e] % C
        vi = val_idx[s:e] % C
        # Gather batches (small; lives briefly)
        k_b = codebook[ki]  # (b, N)
        v_b = codebook[vi]  # (b, N)
        # W += (v_b.T @ k_b) * inv_N
        torch.addmm(W, v_b.T, k_b, beta=1.0, alpha=inv_N, out=W)
        del k_b, v_b, ki, vi
        if bi % max(1, n_batches // 8) == 0 or bi == n_batches - 1:
            rss_log.append({"event": f"W_batch_{bi}", "rss_gb": round(_rss_gb(), 3)})
        if _rss_gb() > MEM_HARD_CEILING_GB:
            raise MemoryError(
                f"RSS exceeded {MEM_HARD_CEILING_GB} GiB during W store batch {bi}/{n_batches}")
    return W, key_idx, val_idx, rss_log


def measure_recall(W: torch.Tensor, codebook: torch.Tensor,
                   key_idx: torch.Tensor, val_idx: torch.Tensor,
                   N_use: int) -> float:
    C = codebook.shape[0]
    n = min(N_PROBE, key_idx.shape[0])
    pk = codebook[key_idx[:n] % C]                # (n, N)
    target = val_idx[:n] % C                       # (n,)
    response = pk @ W.T                            # (n, N)
    # Score response against codebook; argmax row index = predicted val.
    sims = (codebook @ response.T) / N_use         # (C, n)
    pred = torch.argmax(sims, dim=0)               # (n,)
    return float((pred == target).float().mean().item())


def measure_cell(N_use: int, M: int, seed: int) -> Dict:
    """One (N, M, seed) cell: build CB on CPU, store M facts, measure recall."""
    t0 = time.time()
    pre_rss = _rss_gb()
    try:
        C = N_use   # Modern Hopfield activation test: C = N
        codebook, cb_rss = make_bsc_codebook_cpu_chunked(N_use, C, seed)
        W, key_idx, val_idx, store_rss = store_facts_cpu(codebook, M, seed, N_use)
        recall = measure_recall(W, codebook, key_idx, val_idx, N_use)
        peak_events = cb_rss + store_rss
        peak_rss = max((e["rss_gb"] for e in peak_events if e["rss_gb"] >= 0), default=-1.0)
        out = {
            "N": int(N_use), "M": int(M), "seed": int(seed),
            "success": True, "recall": round(recall, 5),
            "pre_rss_gb": round(pre_rss, 3),
            "peak_rss_gb": round(peak_rss, 3),
            "elapsed_s": round(time.time() - t0, 2),
            "rss_log": peak_events[:24],   # Truncate for log compactness
        }
        del W, codebook, key_idx, val_idx
        gc.collect()
        return out
    except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
        tb = traceback.format_exc(limit=12)
        gc.collect()
        return {
            "N": int(N_use), "M": int(M), "seed": int(seed),
            "success": False,
            "error_type": type(e).__name__,
            "error_msg": str(e),
            "traceback": tb,
            "pre_rss_gb": round(pre_rss, 3),
            "fail_rss_gb": round(_rss_gb(), 3),
            "elapsed_s": round(time.time() - t0, 2),
        }


def compute_verdict(cells: List[Dict], N_use: int) -> Tuple[str, str]:
    if not cells:
        return ("T3_INCONCLUSIVE", "no cells")

    # Group by M; compute mean recall across seeds.
    by_M: Dict[int, List[Dict]] = {}
    for c in cells:
        by_M.setdefault(c["M"], []).append(c)

    M_recall = {}
    for M, v in by_M.items():
        succ = [c for c in v if c.get("success")]
        if succ:
            M_recall[M] = sum(c["recall"] for c in succ) / len(succ)
        else:
            M_recall[M] = None

    Ms_present = sorted(M_recall.keys())
    all_M_ok = all(c.get("success") for c in cells)
    max_M_at_95 = 0
    for M in Ms_present:
        r = M_recall.get(M)
        if r is not None and r >= RECALL_THRESHOLD:
            if M > max_M_at_95:
                max_M_at_95 = M

    quarter_N = N_use // 4
    half_N = N_use // 2

    detail = (f"N={N_use} Ms={Ms_present} M_recall={M_recall} "
              f"max_M_at_95={max_M_at_95} all_M_ok={all_M_ok}")

    # HP: all 4 succeed AND max_M_at_95 > N/4
    if all_M_ok and max_M_at_95 > quarter_N:
        return ("T3_HARD_PASS", "MODERN_HOPFIELD_BEND_CPU: " + detail)
    # HF: all 3 strategies OOM across all M (no success) OR linear (max_M within +/-20% of N/4)
    if not any(c.get("success") for c in cells):
        return ("T3_HARD_FAIL", "CPU_OOM_OR_ALL_FAIL: " + detail)
    if max_M_at_95 > 0 and abs(max_M_at_95 - quarter_N) <= int(quarter_N * 0.2):
        return ("T3_HARD_FAIL", "LINEAR_PATTERN_NO_BEND: " + detail)
    # MB: smaller M succeed but N or N/2 cells OOM
    return ("T3_MIDDLE_BAND", "PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    """Smoke-scale forward pass: codebook build + store + recall."""
    assert N_FULL == 16384
    # Tiny test: N=128, C=128, M=16 -- under 5 MB.
    cell = measure_cell(N_use=128, M=16, seed=17)
    assert cell["success"], f"selftest cell failed: {cell}"
    assert cell["recall"] is not None
    assert cell["pre_rss_gb"] >= -1.0  # psutil may be missing; -1 sentinel acceptable.
    # Verify verdict can be computed without TypeError.
    v, msg = compute_verdict([cell], 128)
    assert "T3_" in v
    print(f"[selftest] n_scaling_cpu_only_v8_n16384 PASS "
          f"N=128 M=16 recall={cell['recall']:.3f} "
          f"peak_rss={cell.get('peak_rss_gb', -1)} verdict={v}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--smoke-large", action="store_true",
                   help="run multi-scale smoke at N_SMOKE_LARGE (4096)")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    smoke = args.smoke or args.smoke_large
    if args.smoke_large:
        N_cfg = N_SMOKE_LARGE
        M_sweep = M_SWEEP_SMOKE_LARGE
        seeds = SEEDS_SMOKE
    elif args.smoke:
        N_cfg = N_SMOKE
        M_sweep = M_SWEEP_SMOKE
        seeds = SEEDS_SMOKE
    else:
        N_cfg = N_FULL
        M_sweep = M_SWEEP_FULL
        seeds = SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] n_scaling_cpu_only_v8 smoke={smoke} N={N_cfg} "
          f"M_sweep={M_sweep} seeds={seeds} done={len(done)} CPU-only", flush=True)

    cells: List[Dict] = []
    for M in M_sweep:
        for seed in seeds:
            ck = f"M{M}_s{seed}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    cells.append(body)
                    continue
            cell = measure_cell(N_use=N_cfg, M=M, seed=seed)
            write_partial_key(out_dir, ck, cell)
            cells.append(cell)
            print(f"  M={M} s={seed} success={cell.get('success')} "
                  f"recall={cell.get('recall', 'FAIL')} "
                  f"peak_rss={cell.get('peak_rss_gb', cell.get('fail_rss_gb', -1))} "
                  f"({time.time() - t0:.1f}s)", flush=True)

    verdict, vm = compute_verdict(cells, N_cfg)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "n_scaling_cpu_only_v8_n16384",
               "N": N_cfg, "smoke": smoke,
               "M_sweep": M_sweep, "seeds": seeds,
               "cells": cells,
               "verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
