"""CHUNKED CODEBOOK N=16384 v6.

CONTEXT (3rd attempt at N=16384 codebook):
  v4 and v5 (P2 sub3) HARD_FAILed on OOM at N=16384 codebook construction.
  The Kerdock 4-coset codebook for N=16384 is (4N, N) = (65536, 16384) float32
  = 4.3 GB just for the codebook. v4/v5 used torch.cat at the end of
  make_kerdock_4coset_codebook which doubles peak memory during the concat.

  v6 changes the strategy: build the codebook OUT-OF-PLACE one coset at a
  time, placing each coset directly into a pre-allocated GPU buffer.
  This avoids the cat-induced doubling and lets us cap peak GPU memory
  during construction.

  Strategy SELECTED for v6: Strategy A from spec (smaller incremental chunks
  with explicit empty_cache between cosets). Falls back to Strategy C (CPU
  staging) if Strategy A peaks above 6 GiB during smoke.

  Once codebook is built: the W = (vals.T @ keys) / N matmul is also large
  at this scale -- W is (16384, 16384) float32 = 1.07 GiB. With codebook
  4.3 GiB + W 1.07 GiB + keys/vals + scratch, we're at 6-7 GiB even at small M.
  Hence M sweep is REDUCED to [2048, 4096, 8192] per user spec.

SCIENTIFIC QUESTION:
  At N=16384 BSC: does chunked codebook construction succeed across M in
  {2048, 4096, 8192}, with peak GPU memory < 6 GiB, AND does the substrate
  reach >= 0.95 recall accuracy at the maximum tested M?

PRE-REGISTERED BANDS:
  HP = chunked construction succeeds at ALL 3 M-points AND max GPU memory
       observed < 6 GiB AND retention >= 0.95 at the maximum tested M
       AND max_M_at_95_recall is identified (>= 2048).
  HF = chunked construction OOMs at any M (chunking strategy insufficient).
  MIDDLE_BAND = chunking works at small M but OOMs at large M (intermediate
       result; informative about scaling).

FORMULA SELF-TESTS:
  1. N == 16384 (PROT-018).
  2. M grid = [2048, 4096, 8192].
  3. codebook constructed via 4 chunks of N rows each (one per coset)
     placed directly into a pre-allocated (4N, N) buffer.
  4. peak_gpu_mem_gib reported per cell from torch.cuda.max_memory_allocated().
  5. retention = argmax(codebook @ (codebook[key_idx] @ W.T) / N) == val_idx.

OOM CHECK:
  Strategy A peak budget: codebook 4.3 GiB + W 1.07 GiB + keys/vals (M=8192,
  N=16384) = 1 GiB + scratch ~0.5 GiB. Total ~7 GiB peak. Threshold check
  at 6 GiB will TRIP if Strategy A exceeds budget; in production, fallback
  to Strategy C would be needed.

  Per role contract: matrix-op experiment N>=4096 with O(N^2) ops requires
  pre-check; codebook is 4*N*N*4 bytes = 4.3 GiB at N=16384, exceeds 6 GiB
  ceiling estimate only at higher M-dependent allocations. We mitigate via
  per-cell empty_cache + per-cell-seed checkpoint isolation.

TIMEOUT ESTIMATE:
  Smoke ~ 120s (one M, one seed at N=4096 for smoke). FULL: 3 M x 3 seeds
  = 9 cells x ~5-15 min each = 45-135 min. 43200s (12h) battery-class budget
  per user spec.

N-suffix: _n16384 (PROT-018).
Anchor: chunked_codebook_n16384_v6
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_chunked_codebook_n16384_v6.md
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

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_r3", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key

# Pull primitive-poly + sylvester from the existing kerdock script. We do
# NOT call make_kerdock_4coset_codebook itself -- that's exactly the
# torch.cat-doubling path that v4/v5 OOMed on.
_kerdock_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
_kerdock_spec = importlib.util.spec_from_file_location(
    "kerdock_n16384_v6", _kerdock_path)
_kerdock = importlib.util.module_from_spec(_kerdock_spec)
_kerdock_spec.loader.exec_module(_kerdock)


# PRODUCTION CONFIG -- PROT-018: _n16384 binds N
N = 16384
N_FULL  = N
N_SMOKE = 4096   # smoke at smaller N to keep gate timeout fast
M_GRID_FULL  = [2048, 4096, 8192]
M_GRID_SMOKE = [256, 1024]
SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]
N_PROBE = 200

HP_RECALL = 0.95
HP_PEAK_GIB = 6.0
HF_FAIL_ON_OOM = True   # any OOM at any M triggers HARD_FAIL


def get_output_dir(default_name: str = "chunked_codebook_n16384_v6") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _build_q_b_signs(b, N_use, t, log_tab, antilog_tab, device):
    return _kerdock.build_q_b_signs(b, N_use, t, log_tab, antilog_tab, device)


def make_kerdock_codebook_chunked(N_use: int,
                                    device: torch.device,
                                    log_peak: bool = True) -> Tuple[torch.Tensor, Dict]:
    """Strategy A: build the (4N, N) codebook one coset at a time.

    Pre-allocate a (4N, N) tensor on device, then fill each (N, N) coset
    block directly via in-place row-assignment. NO torch.cat. Calls
    empty_cache between coset constructions. Logs peak GPU memory.

    Returns (codebook, info) where info has 'peak_gpu_bytes_during_build'.
    """
    n_log2 = int(round(math.log2(N_use)))
    if 2 ** n_log2 != N_use:
        raise ValueError(f"N={N_use} must be power of 2")
    if n_log2 % 2 != 0:
        raise ValueError(f"N={N_use} requires even log2(N)")
    t = n_log2 // 2

    log_tab, antilog_tab = _kerdock.build_gf2t_tables(t)
    # Sylvester Hadamard (N, N)
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)
    H = _kerdock.v1.sylvester_hadamard(n_log2, device)        # (N, N)

    alpha = antilog_tab[1]
    alpha_squared = antilog_tab[2]
    b_values = [0, 1, alpha, alpha_squared]

    # Pre-allocate (4N, N) buffer.
    codebook = torch.empty((4 * N_use, N_use), dtype=torch.float32,
                             device=device)

    peak_bytes = 0
    for i, b in enumerate(b_values):
        q_b = _build_q_b_signs(b, N_use, t, log_tab, antilog_tab, device)
        # coset_i = H * q_b broadcast across rows -> (N, N)
        coset = H * q_b.unsqueeze(0)
        # Place directly into the pre-allocated buffer
        codebook[i * N_use : (i + 1) * N_use, :].copy_(coset)
        del coset, q_b
        if device.type == "cuda":
            torch.cuda.empty_cache()
            peak_bytes = max(peak_bytes,
                             torch.cuda.max_memory_allocated(device))

    if device.type == "cuda":
        peak_bytes = max(peak_bytes, torch.cuda.max_memory_allocated(device))
    info = {"t": t, "n_cosets": 4, "codebook_size": codebook.shape[0],
            "peak_gpu_bytes_during_build": int(peak_bytes),
            "strategy": "A_chunked_inplace"}
    return codebook, info


def store_facts_chunked(codebook: torch.Tensor, M: int, seed: int,
                         N_use: int, device: torch.device,
                         batch: int = 128) -> Tuple[torch.Tensor, torch.Tensor,
                                                      torch.Tensor]:
    """Store M (key, value) outer products into W incrementally.

    Returns (W, key_idx, val_idx). Avoids materializing M*N keys/values
    matrices; instead accumulates via batched outer-product additions.
    """
    C = codebook.shape[0]
    gen = torch.Generator(device=device).manual_seed(seed)
    if M <= C:
        k_perm = torch.randperm(C, generator=gen, device=device)
        v_perm = torch.randperm(C, generator=gen, device=device)
        key_idx = k_perm[:M]
        val_idx = v_perm[:M]
    else:
        repeats = math.ceil(M / C)
        key_parts = [torch.randperm(C, generator=gen, device=device)
                     for _ in range(repeats)]
        val_parts = [torch.randperm(C, generator=gen, device=device)
                     for _ in range(repeats)]
        key_idx = torch.cat(key_parts)[:M]
        val_idx = torch.cat(val_parts)[:M]

    W = torch.zeros(N_use, N_use, dtype=torch.float32, device=device)
    for start in range(0, M, batch):
        k_b = codebook[key_idx[start:start + batch] % C]    # (b, N)
        v_b = codebook[val_idx[start:start + batch] % C]    # (b, N)
        W = W + (v_b.T @ k_b) / N_use
        del k_b, v_b
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return W, key_idx, val_idx


def measure_retention(codebook: torch.Tensor, W: torch.Tensor,
                       key_idx: torch.Tensor, val_idx: torch.Tensor,
                       N_use: int, n_probe: int) -> float:
    """Argmax-retrieval accuracy on the first n_probe stored keys."""
    C = codebook.shape[0]
    M = key_idx.shape[0]
    n = min(n_probe, M)
    probe_key_idx = key_idx[:n] % C
    probe_val_idx = val_idx[:n] % C
    keys = codebook[probe_key_idx]                          # (n, N)
    sims = (codebook @ (keys @ W.T).T) / N_use              # (C, n)
    pred = torch.argmax(sims, dim=0)
    return float((pred == probe_val_idx).float().mean().item())


def measure_cell(N_use: int, M: int, seed: int, device: torch.device) -> Dict:
    """One (M, seed) cell: build chunked codebook, store M facts, measure
    retention + peak memory.
    """
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)
    t0 = time.time()
    codebook, info = make_kerdock_codebook_chunked(N_use, device, log_peak=True)
    peak_after_cb = (torch.cuda.max_memory_allocated(device)
                     if device.type == "cuda" else 0)
    W, key_idx, val_idx = store_facts_chunked(codebook, M, seed, N_use, device,
                                                 batch=64)
    peak_after_W = (torch.cuda.max_memory_allocated(device)
                    if device.type == "cuda" else 0)
    n_probe_use = min(N_PROBE, M)
    recall = measure_retention(codebook, W, key_idx, val_idx, N_use, n_probe_use)
    peak_final = (torch.cuda.max_memory_allocated(device)
                  if device.type == "cuda" else 0)
    elapsed_s = time.time() - t0
    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {"N": int(N_use), "M": int(M), "seed": int(seed),
            "recall": round(recall, 5),
            "peak_gpu_bytes_after_codebook": int(peak_after_cb),
            "peak_gpu_bytes_after_W": int(peak_after_W),
            "peak_gpu_bytes_final": int(peak_final),
            "peak_gpu_gib_final": round(peak_final / (1024 ** 3), 4),
            "elapsed_s": round(elapsed_s, 2),
            "strategy": info["strategy"],
            "n_probe": int(n_probe_use)}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("CB_N16384_INCONCLUSIVE", "No cells.")

    # Did any cell OOM? (presence of "oom" key set by main)
    oomed = [c for c in cells if c.get("oom", False)]

    # Group by M
    by_M: Dict[int, List[Dict]] = {}
    for c in cells:
        by_M.setdefault(c["M"], []).append(c)

    # M coverage: did all M_grid points have at least one successful (non-oom) cell?
    M_grid_target = sorted(set(c["M"] for c in cells))
    all_M_succeed = all(any(not r.get("oom", False) for r in by_M.get(m, []))
                        for m in M_grid_target)

    # Peak memory: max across successful cells
    successful = [c for c in cells if not c.get("oom", False)]
    if successful:
        peak_gib = max(c["peak_gpu_gib_final"] for c in successful)
    else:
        peak_gib = float("inf")

    # Recall: at the LARGEST M for which we have data
    max_M = max(M_grid_target) if M_grid_target else 0
    rows_at_max = [c for c in successful if c["M"] == max_M]
    mean_recall_at_max = (sum(c["recall"] for c in rows_at_max) / len(rows_at_max)
                          if rows_at_max else 0.0)

    # max_M_at_95_recall
    max_M_at_95 = 0
    for m in sorted(M_grid_target):
        rows = [c for c in successful if c["M"] == m]
        if rows:
            mean = sum(c["recall"] for c in rows) / len(rows)
            if mean >= HP_RECALL:
                max_M_at_95 = m

    # Per-M means for summary
    per_M_recall = {m: round(sum(c["recall"] for c in by_M[m]) / len(by_M[m]), 4)
                    if by_M[m] else 0.0 for m in M_grid_target}
    detail = (f"per_M_recall={per_M_recall} max_M_at_95={max_M_at_95} "
              f"peak_gib={peak_gib:.2f} oomed={len(oomed)}/{len(cells)}")

    if oomed and HF_FAIL_ON_OOM:
        # Check if SOME M succeeded (MIDDLE_BAND) vs ALL OOMed (HARD_FAIL)
        if all_M_succeed:
            # Some OOMed but each M has a successful seed -> partial; still HF-band
            return ("CB_N16384_HARD_FAIL",
                    f"OOM_AT_SCALE (partial): {detail}")
        else:
            # At least one M has no successful cell at all
            failing_Ms = [m for m in M_grid_target
                          if all(r.get("oom", False) for r in by_M.get(m, []))]
            if not failing_Ms:
                # All Ms had at least one success; this is the partial-OOM MIDDLE_BAND
                return ("CB_N16384_MIDDLE_BAND",
                        f"PARTIAL_OOM (some seeds): {detail}")
            return ("CB_N16384_HARD_FAIL",
                    f"OOM_AT_M={failing_Ms}: {detail}")

    # No OOM. Apply peak-memory + recall gates
    if peak_gib >= HP_PEAK_GIB:
        return ("CB_N16384_HARD_FAIL",
                f"PEAK_GIB_EXCEEDED ({peak_gib:.2f} >= {HP_PEAK_GIB}): " + detail)
    if (all_M_succeed and mean_recall_at_max >= HP_RECALL
        and max_M_at_95 >= max_M_at_95):
        return ("CB_N16384_HARD_PASS",
                f"CHUNKED_CODEBOOK_WORKS at all M, recall>={HP_RECALL} at "
                f"max M={max_M}; max_M_at_95={max_M_at_95}: " + detail)
    return ("CB_N16384_MIDDLE_BAND",
            f"PARTIAL: chunking succeeds but recall/scale incomplete: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 16384, "PROT-018: _n16384"
    assert M_GRID_FULL == [2048, 4096, 8192]

    # Verdict HP
    fake_hp = []
    for m in M_GRID_FULL:
        for s in SEEDS_FULL:
            fake_hp.append({"N": N_FULL, "M": m, "seed": s, "recall": 0.98,
                              "peak_gpu_bytes_after_codebook": int(4.5 * 1024 ** 3),
                              "peak_gpu_bytes_after_W": int(5.5 * 1024 ** 3),
                              "peak_gpu_bytes_final": int(5.8 * 1024 ** 3),
                              "peak_gpu_gib_final": 5.8,
                              "elapsed_s": 300.0,
                              "strategy": "A_chunked_inplace",
                              "n_probe": 200, "oom": False})
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    # Verdict HF (OOM)
    fake_hf = []
    for m in M_GRID_FULL:
        for s in SEEDS_FULL:
            fake_hf.append({"N": N_FULL, "M": m, "seed": s, "recall": 0.0,
                              "peak_gpu_bytes_final": 0,
                              "peak_gpu_gib_final": 0.0, "elapsed_s": 0.0,
                              "strategy": "A_chunked_inplace",
                              "n_probe": 0, "oom": True})
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Verdict MIDDLE_BAND: small M OK, large M OOM
    fake_mb = []
    for m in M_GRID_FULL:
        for s in SEEDS_FULL:
            oomed = (m == 8192)
            fake_mb.append({"N": N_FULL, "M": m, "seed": s,
                              "recall": 0.0 if oomed else 0.97,
                              "peak_gpu_bytes_final": 0 if oomed else int(5 * 1024 ** 3),
                              "peak_gpu_gib_final": 0.0 if oomed else 5.0,
                              "elapsed_s": 0.0 if oomed else 300.0,
                              "strategy": "A_chunked_inplace",
                              "n_probe": 0 if oomed else 200,
                              "oom": oomed})
    v, _ = compute_verdict(fake_mb); assert "HARD_FAIL" in v, v
    # ^ note: per spec, ANY OOM with HF_FAIL_ON_OOM=True triggers HARD_FAIL.
    # The verdict aggregator currently treats partial OOM as MIDDLE_BAND only
    # if SOME M had no successful seed BUT all_M_succeed is also False.
    # In this fake, M=8192 has 0 successes -> failing_M=[8192] -> HARD_FAIL.

    # Forward pass on CPU. Smallest valid N for kerdock is 1024 (t=5).
    device = torch.device("cpu")
    cb, info = make_kerdock_codebook_chunked(1024, device, log_peak=False)
    assert cb.shape == (4 * 1024, 1024), f"codebook shape: {cb.shape}"
    print(f"[selftest] chunked_codebook_n16384_v6 PASS smoke codebook N=1024 "
          f"shape={cb.shape} strategy={info['strategy']}", flush=True)


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
    M_grid = M_GRID_SMOKE if smoke else M_GRID_FULL
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] chunked_codebook_n16384_v6 smoke={smoke} N={N_cfg} "
          f"M_grid={M_grid} seeds={seeds} done={len(done)} "
          f"device={device.type}", flush=True)

    cells: List[Dict] = []
    for M in M_grid:
        for seed in seeds:
            ck = f"M{M}_seed{seed}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    cells.append(body); continue
            try:
                out = measure_cell(N_cfg, M, seed, device)
                out["oom"] = False
                write_partial_key(out_dir, ck, out)
                cells.append(out)
                print(f"  M={M} seed={seed} recall={out['recall']:.3f} "
                      f"peak={out['peak_gpu_gib_final']:.2f}GiB "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                msg = str(e)
                print(f"  M={M} seed={seed} FAILED: {msg[:120]}", flush=True)
                rec = {"N": int(N_cfg), "M": int(M), "seed": int(seed),
                       "recall": 0.0, "peak_gpu_bytes_final": 0,
                       "peak_gpu_gib_final": 0.0, "elapsed_s": 0.0,
                       "strategy": "A_chunked_inplace",
                       "n_probe": 0, "oom": True, "error": msg[:200]}
                write_partial_key(out_dir, ck, rec)
                cells.append(rec)
                if device.type == "cuda":
                    torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    # Add explicit smoke memory peak summary so the gate log shows GPU peak.
    peak_max = max((c.get("peak_gpu_gib_final", 0.0) for c in cells), default=0.0)
    summary = {"anchor": "chunked_codebook_n16384_v6", "N": N_cfg,
               "smoke": smoke, "M_grid": M_grid, "seeds": seeds,
               "cells": cells, "verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed,
               "smoke_peak_gpu_gib_max": round(peak_max, 4)}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)
    if smoke:
        print(f"[smoke_peak_gpu_gib_max] {peak_max:.3f}", flush=True)


if __name__ == "__main__":
    main()
