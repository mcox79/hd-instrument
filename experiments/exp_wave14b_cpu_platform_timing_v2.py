"""Wave 14.B CPU platform timing v2 — realistic deployment patterns.

v1 was overly pessimistic: it timed retrieve-top-4 + decompose-all-4.
Real deployment does retrieve-only (most queries) or retrieve + 1 decompose
(when agent asks "what's in memory"). v2 times those patterns.

Three modes:
  A. retrieval-only: retrieve top-M, return ranked list. No decomposition.
  B. retrieve + single decompose: retrieve top-1, decompose it.
  C. decompose-only: time JUST a single decomposition (isolated cost).

Reports p50 + p99 latency per mode.

Also tests with N up to 8192 since that's the realistic substrate
dimension (4096 is the byte-LM number, 8192 is the workstation tier).
"""

from __future__ import annotations

import json
import math
import time
import os
from pathlib import Path

import torch


torch.set_num_threads(max(1, os.cpu_count() or 1))
DEVICE = torch.device("cpu")
SEED = 17
N_VALUES = [2048, 4096, 8192]
POOL_SIZES = [1024, 10000, 100000, 1000000]
BUNDLE_SLOTS = [2, 4, 8]
NUM_QUERIES = 30
CODEBOOK_K = 256


def _say(msg: str) -> None:
    print(msg, flush=True)


def build_codebook(gen, K, N):
    bits = torch.randint(0, 2, (K, N), generator=gen)
    return (bits * 2 - 1).to(torch.float32)


def build_positions(gen, B, N):
    bits = torch.randint(0, 2, (B, N), generator=gen)
    return (bits * 2 - 1).to(torch.float32)


def build_pool(gen, P, B, N, codebook, positions):
    pool = torch.zeros((P, N), dtype=torch.float32)
    K = codebook.shape[0]
    for i in range(P):
        atom_ids = torch.randint(0, K, (B,), generator=gen)
        atoms = codebook[atom_ids]
        pool[i] = (atoms * positions).sum(dim=0)
    return pool


def retrieve_top_M(query, pool, M):
    pool_norms = pool.norm(dim=1).clamp(min=1e-12)
    qnorm = query.norm().clamp(min=1e-12)
    scores = (pool @ query) / (pool_norms * qnorm)
    top_idx = scores.topk(min(M, pool.shape[0])).indices
    return top_idx


def decompose_single(bundle, positions, codebook, N, num_restarts=2, max_iter=15):
    B = positions.shape[0]
    K = codebook.shape[0]
    best_score = -float("inf")
    best_idx = [-1] * B
    BETA_MAX = 20.0
    for restart in range(num_restarts):
        init_indices = torch.randint(0, K, (B,))
        atoms_hat = codebook[init_indices].clone()
        beta = 1.0
        for it in range(max_iter):
            for s in range(B):
                contribution_others = (atoms_hat * positions).sum(dim=0) - atoms_hat[s] * positions[s]
                candidate = (bundle - contribution_others) * positions[s]
                scores = (codebook @ candidate) / math.sqrt(N)
                weights = torch.softmax(beta * scores, dim=0)
                atoms_hat[s] = weights @ codebook
            beta = min(beta * 1.5, BETA_MAX)
        pred_idx = []
        for s in range(B):
            scores = codebook @ atoms_hat[s]
            pred_idx.append(int(scores.argmax().item()))
        pred_atoms = codebook[torch.tensor(pred_idx)]
        c_recon = (pred_atoms * positions).sum(dim=0)
        score = float((bundle @ c_recon) / (bundle.norm() * c_recon.norm() + 1e-12))
        if score > best_score:
            best_score = score
            best_idx = pred_idx
    return best_idx


def stats(arr):
    arr_sorted = sorted(arr)
    n = len(arr_sorted)
    return {"median_ms": arr_sorted[n // 2],
            "p99_ms": arr_sorted[int(0.99 * (n - 1))],
            "mean_ms": sum(arr_sorted) / n}


def time_mode(mode, N, P, B, codebook, positions, pool, query_bundles):
    latencies = []
    for query in query_bundles:
        t0 = time.perf_counter()
        if mode == "A_retrieve_only":
            _ = retrieve_top_M(query, pool, 4)
        elif mode == "B_retrieve_plus_one":
            top_idx = retrieve_top_M(query, pool, 1)
            _ = decompose_single(pool[top_idx[0]], positions, codebook, N)
        elif mode == "C_decompose_only":
            _ = decompose_single(query, positions, codebook, N)
        else:
            raise ValueError(mode)
        latencies.append((time.perf_counter() - t0) * 1000)
    return stats(latencies)


def main():
    _say(f"Wave 14.B CPU platform timing v2 — realistic patterns")
    _say(f"  device={DEVICE}, threads={torch.get_num_threads()}, NUM_QUERIES={NUM_QUERIES}")
    _say(f"  Platform target: <100 ms p99")

    all_results = []
    t_start = time.perf_counter()

    for N in N_VALUES:
        for P in POOL_SIZES:
            for B in BUNDLE_SLOTS:
                # Avoid running the worst-case 1M pools at N=8K (would take ages)
                if P * N >= 6_000_000_000:
                    _say(f"  SKIP N={N} P={P} B={B}: pool too large")
                    continue
                _say(f"\n  N={N}, P={P}, B={B}")
                gen = torch.Generator().manual_seed(SEED + N + P + B)
                codebook = build_codebook(gen, CODEBOOK_K, N)
                positions = build_positions(gen, B, N)
                pool = build_pool(gen, P, B, N, codebook, positions)
                query_bundles = []
                for q in range(NUM_QUERIES):
                    qg = torch.Generator().manual_seed(SEED + 10000 + q)
                    atom_ids = torch.randint(0, CODEBOOK_K, (B,), generator=qg)
                    atoms = codebook[atom_ids]
                    query_bundles.append((atoms * positions).sum(dim=0))
                try:
                    res = {}
                    for mode in ["A_retrieve_only", "B_retrieve_plus_one", "C_decompose_only"]:
                        s = time_mode(mode, N, P, B, codebook, positions, pool, query_bundles)
                        res[mode] = s
                        target_met = s["p99_ms"] < 100.0
                        marker = "MET" if target_met else "MISSED"
                        _say(f"    {mode}: p50={s['median_ms']:.2f}ms p99={s['p99_ms']:.2f}ms [{marker}]")
                    all_results.append({"N": N, "P": P, "B": B, "modes": res})
                except Exception as e:
                    _say(f"    ERROR: {e}")
                    all_results.append({"N": N, "P": P, "B": B, "error": str(e)})
                # Incremental save
                out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_cpu_platform_timing_v2"
                out_dir.mkdir(parents=True, exist_ok=True)
                (out_dir / "metrics.json").write_text(json.dumps(
                    {"results_so_far": all_results,
                     "elapsed_s": time.perf_counter() - t_start},
                    indent=2, default=str))

    _say(f"\n========= SUMMARY =========")
    for mode in ["A_retrieve_only", "B_retrieve_plus_one", "C_decompose_only"]:
        met = sum(1 for r in all_results
                  if not r.get("error") and r["modes"][mode]["p99_ms"] < 100.0)
        total = sum(1 for r in all_results if not r.get("error"))
        _say(f"  {mode}: {met}/{total} configs met <100ms p99")
    _say(f"  Total wall: {(time.perf_counter() - t_start)/60:.1f} min")


if __name__ == "__main__":
    main()
