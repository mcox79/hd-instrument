"""LARGE-K PATH SCALING v1 at N=4096 (per user msg 2026-05-30).

CONTEXT (K_paths scaling of B + D + E):
  Bayesian propagation (D) enumerates K paths (combinatorics matter).
  Continuous-output (B) and spectral (E) don't enumerate explicitly per
  candidate -- they propagate state or compute signatures.
  HYPOTHESIS (user): B and E should scale better than D as K grows toward
  production-realistic values.

  We measure both ACCURACY scaling (does retrieval degrade as K grows?)
  and LATENCY scaling (how does wall-time grow with K?).

  This anchor uses M=512 (sub-capacity, comparable to N-batch base) and
  depth=4 (a "real multi-hop" depth). The sweep is across K alone.

SCIENTIFIC QUESTION:
  At N=4096, M=512, depth=4: how does each path's top-1 accuracy and
  latency scale as K_paths grows from 10 to 1000?

PRE-REGISTERED BANDS:
  HP = at least one path maintains accuracy >= 0.65 at K=1000 in >=3/5
       seeds AND has latency scaling SUB-QUADRATIC in K
       (latency(K=1000)/latency(K=100) < 100).
  HF = all 3 paths drop below 0.30 accuracy at K >= 250 (no production
       scale viability).
  MIDDLE_BAND = otherwise.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. M == 512 (sub-capacity).
  3. depth == 4.
  4. K_paths grid = [10, 50, 100, 250, 500, 1000].
  5. Each (path, K) cell: score K candidates (1 coherent + K-1 decoys);
     top-1 = correct iff argmax_path picks index 0.
  6. Latency: ns per K-candidate scoring; reported per-path.
  7. Sub-quadratic test: latency_ratio = lat(K=1000)/lat(K=100) < 100
     (a quadratic process would have ratio ~100; sub-quadratic < 100).

OOM CHECK:
  M=512, N=4096: keys+vals = 16 MiB. W = 64 MiB. CB = 805 MiB. ~900 MiB.
  K_paths=1000 candidates each scored 5 hops = 5000 N-dim ops per query.
  Memory-light per query; 5 seeds x 6 K x 3 paths = 90 cells, each with
  ~5 queries -> fine. OK.

TIMEOUT ESTIMATE:
  Smoke ~ 90s. FULL: 5 seeds x 6 K x 3 paths * latency. Worst K=1000
  per path ~ 30s/query x 5 queries = 150s per path per K=1000. Sum
  across K_sweep < 200s/path. 3 paths x 5 seeds = 15. Total ~ 3000s.
  scaling_exp=1.5. Budget 21600s.

N-suffix: _n4096 (PROT-018).
Anchor: large_k_path_scaling_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_large_k_path_scaling_v1_n4096.md
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

from experiments._metric_battery import make_substrate  # noqa: E402
from experiments._relation_graph import (  # noqa: E402
    build_relation_facts,
    sample_coherent_starts,
    sample_incoherent_paths,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_lkps", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096
N_FULL  = N
N_SMOKE = 1024
M_FULL  = 512
M_SMOKE = 64
DEPTH_FULL  = 4
DEPTH_SMOKE = 3
K_PATHS_FULL  = [10, 50, 100, 250, 500, 1000]
K_PATHS_SMOKE = [10, 100]
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_QUERIES_FULL  = 5  # per (path, K) cell; 5 queries is enough to estimate accuracy
N_QUERIES_SMOKE = 2
BETA = 4.0
TOP_K_SIG = 16

HP_ACC_AT_K1000     = 0.65
HP_K_TARGET         = 1000
HP_SEEDS_MIN        = 3
HP_LAT_RATIO_MAX    = 100.0   # sub-quadratic (K=1000 / K=100 < 100)
HF_ACC_AT_K_HIGH    = 0.30
HF_K_HIGH_MIN       = 250
HF_SEEDS_MIN        = 3


# ---------- mechanism scorers (reused from composition) ----------

def build_substrate_with_relation(N_use: int, M: int, seed: int,
                                    device: torch.device):
    codebook, _W, _keys, _vals, _ki, _vi = make_substrate(
        N_use, M, seed, device)
    key_idx, val_idx, relation = build_relation_facts(
        n_idx=codebook.shape[0], M=M, seed=seed, device=device, closed=True)
    keys_vec = codebook[key_idx]
    vals_vec = codebook[val_idx]
    W = (vals_vec.T @ keys_vec) / N_use
    return codebook, W, key_idx, val_idx, relation


def score_path_continuous(codebook: torch.Tensor, W: torch.Tensor,
                            path: List[int], N_use: int) -> float:
    q = codebook[path[0]].clone()
    depth = len(path) - 1
    for _ in range(depth):
        q = q @ W.T
    target = codebook[path[-1]]
    return float((q @ target).item() / N_use)


def score_path_bayesian(codebook: torch.Tensor, W: torch.Tensor,
                          path: List[int], N_use: int, beta: float) -> float:
    depth = len(path) - 1
    if depth <= 0:
        return 0.0
    src_idx = torch.tensor(path[:-1], dtype=torch.long, device=codebook.device)
    dst_idx = torch.tensor(path[1:], dtype=torch.long, device=codebook.device)
    src = codebook[src_idx]
    dst = codebook[dst_idx]
    out = src @ W.T
    sims = (out * dst).sum(dim=1) / N_use
    logits = beta * sims
    log_lik = -torch.nn.functional.softplus(-logits)
    return float(log_lik.sum().item())


def score_path_spectral(codebook: torch.Tensor, W: torch.Tensor,
                         path: List[int], N_use: int, top_k: int) -> float:
    depth = len(path) - 1
    if depth < 1:
        return 0.0
    src_idx = torch.tensor(path[:-1], dtype=torch.long, device=codebook.device)
    src = codebook[src_idx]
    responses = src @ W.T
    sigs = []
    for i in range(depth):
        sims = (codebook @ responses[i]) / N_use
        sig = torch.topk(sims, top_k).values
        sigs.append(sig)
    if len(sigs) < 2:
        dst = codebook[path[-1]]
        sims = (codebook @ dst) / N_use
        s_dst = torch.topk(sims, top_k).values
        c = torch.nn.functional.cosine_similarity(
            sigs[0].unsqueeze(0), s_dst.unsqueeze(0)).item()
        return float(c)
    cohs = []
    for i in range(len(sigs) - 1):
        c = torch.nn.functional.cosine_similarity(
            sigs[i].unsqueeze(0), sigs[i + 1].unsqueeze(0)).item()
        cohs.append(c)
    return float(sum(cohs) / len(cohs))


def measure_path_at_K(codebook: torch.Tensor, W: torch.Tensor,
                       relation: Dict[int, int], path_name: str,
                       depth: int, K: int, n_queries: int, seed: int,
                       N_use: int, device: torch.device
                       ) -> Tuple[float, float, int]:
    """Run n_queries queries; for each, score K candidates with `path_name`
    mechanism. Returns (accuracy, mean_latency_ns, n_eval).
    """
    C = codebook.shape[0]
    pos_paths = sample_coherent_starts(relation, depth=depth,
                                         n_paths=n_queries, seed=seed + depth)
    if not pos_paths:
        return (0.0, 0.0, 0)

    n_correct = 0
    latencies: List[float] = []

    for q_idx, pos in enumerate(pos_paths):
        decoys = sample_incoherent_paths(
            C, depth=depth, n_paths=K - 1,
            seed=seed + depth + q_idx * 31, relation=relation)
        if len(decoys) < K - 1:
            need = (K - 1) - len(decoys)
            extra = sample_incoherent_paths(
                C, depth=depth, n_paths=need,
                seed=seed + 991 + q_idx, relation=relation)
            decoys = decoys + extra
        candidates = [pos] + decoys[:K - 1]

        t0 = time.perf_counter_ns()
        if path_name == "B":
            scores = [score_path_continuous(codebook, W, p, N_use)
                      for p in candidates]
        elif path_name == "D":
            scores = [score_path_bayesian(codebook, W, p, N_use, BETA)
                      for p in candidates]
        elif path_name == "E":
            scores = [score_path_spectral(codebook, W, p, N_use, TOP_K_SIG)
                      for p in candidates]
        else:
            raise ValueError(f"Unknown path: {path_name}")
        t1 = time.perf_counter_ns()
        latencies.append(t1 - t0)

        top = int(max(range(len(scores)), key=lambda i: scores[i]))
        if top == 0:
            n_correct += 1

    n_eval = len(pos_paths)
    acc = n_correct / n_eval
    mean_lat = float(sum(latencies) / len(latencies)) if latencies else 0.0
    return (acc, mean_lat, n_eval)


def measure_cell(N_use: int, M: int, depth: int, K: int, seed: int,
                  n_queries: int, device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_substrate_with_relation(
        N_use, M, seed, device)
    out_paths: Dict[str, Dict] = {}
    for pn in ("B", "D", "E"):
        acc, lat, n_eval = measure_path_at_K(
            codebook, W, relation, pn, depth, K, n_queries, seed, N_use, device)
        out_paths[pn] = {"acc": round(acc, 5),
                          "lat_ns": int(lat),
                          "n_eval": int(n_eval)}
    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"depth": int(depth), "M": int(M), "K": int(K), "seed": int(seed),
            "B": out_paths["B"], "D": out_paths["D"], "E": out_paths["E"]}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("LKPS_INCONCLUSIVE", "No cells.")

    # Group by K
    by_K: Dict[int, List[Dict]] = {}
    for c in cells:
        by_K.setdefault(c["K"], []).append(c)

    # ---- HP eligibility ----
    target = by_K.get(HP_K_TARGET, [])
    hp_path_winners: Dict[str, int] = {"B": 0, "D": 0, "E": 0}
    for c in target:
        for pn in ("B", "D", "E"):
            if c[pn]["acc"] >= HP_ACC_AT_K1000:
                hp_path_winners[pn] += 1
    hp_any_path = max(hp_path_winners.values()) if target else 0
    hp_path_named = max(hp_path_winners, key=lambda k: hp_path_winners[k]) if target else None

    # Sub-quadratic latency check: lat(K=1000)/lat(K=100) < 100
    base_K = 100
    target_K = 1000
    base_cells = by_K.get(base_K, [])
    targ_cells = by_K.get(target_K, [])
    lat_ratios: Dict[str, float] = {}
    if base_cells and targ_cells:
        for pn in ("B", "D", "E"):
            base_lat = sum(c[pn]["lat_ns"] for c in base_cells) / len(base_cells)
            targ_lat = sum(c[pn]["lat_ns"] for c in targ_cells) / len(targ_cells)
            ratio = targ_lat / max(1.0, base_lat)
            lat_ratios[pn] = round(ratio, 2)
    sub_quad_paths = [pn for pn, r in lat_ratios.items() if r < HP_LAT_RATIO_MAX]

    # ---- HF: all 3 paths drop below 0.30 at K >= 250 ----
    high_K_cells = [c for c in cells if c["K"] >= HF_K_HIGH_MIN]
    hf_all_paths_dropped = False
    if high_K_cells:
        # Per path: count seeds where acc <= HF threshold
        seed_fail = {"B": 0, "D": 0, "E": 0}
        for c in high_K_cells:
            for pn in ("B", "D", "E"):
                if c[pn]["acc"] <= HF_ACC_AT_K_HIGH:
                    seed_fail[pn] += 1
        # Per path: dominant fail across the slice if seed_fail >= HF_SEEDS_MIN
        all_three_dropped = all(seed_fail[pn] >= HF_SEEDS_MIN
                                  for pn in ("B", "D", "E"))
        hf_all_paths_dropped = all_three_dropped

    # Summary
    accs_by_K: Dict[int, Dict[str, float]] = {}
    for K, cs in by_K.items():
        accs_by_K[K] = {
            pn: round(sum(c[pn]["acc"] for c in cs) / len(cs), 4)
            for pn in ("B", "D", "E")
        }

    detail = (f"accs_by_K={accs_by_K} lat_ratios_K1000/K100={lat_ratios} "
              f"hp_path_winners@K{HP_K_TARGET}={hp_path_winners} "
              f"sub_quad_paths={sub_quad_paths} "
              f"hf_all_paths_dropped={hf_all_paths_dropped}")

    # HF first
    if hf_all_paths_dropped:
        return ("LKPS_HARD_FAIL", "NO_PRODUCTION_SCALE_VIABILITY: " + detail)

    # HP: best path has >=HP_SEEDS_MIN seeds with high acc at K=1000 AND
    # has sub-quadratic latency
    if (hp_path_named is not None
            and hp_path_winners[hp_path_named] >= HP_SEEDS_MIN
            and hp_path_named in sub_quad_paths):
        return ("LKPS_HARD_PASS", f"PATH_{hp_path_named}_SCALES: " + detail)

    return ("LKPS_MIDDLE_BAND", "PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    assert M_FULL == 512
    assert DEPTH_FULL == 4
    assert K_PATHS_FULL == [10, 50, 100, 250, 500, 1000]
    assert 100 in K_PATHS_FULL and 1000 in K_PATHS_FULL, "need 100 and 1000 for ratio"

    # Verdict gate HP: best path has acc>=0.65 at K=1000 in >=3/5 seeds
    # AND sub-quadratic latency
    fake_hp_cells = []
    for K in K_PATHS_FULL:
        for s in SEEDS_FULL:
            # B: stays high at K=1000, latency grows linearly (K=1000 is 10x K=100)
            b_acc = 0.70 if K <= HP_K_TARGET else 0.70
            b_lat = K * 1000  # linear in K
            # D: drops at large K
            d_acc = 0.70 - 0.20 * (K / 1000)
            d_lat = K * K * 100  # quadratic
            # E: middling
            e_acc = 0.50
            e_lat = K * 500
            fake_hp_cells.append({"depth": 4, "M": 512, "K": K, "seed": s,
                                    "B": {"acc": b_acc, "lat_ns": b_lat, "n_eval": 5},
                                    "D": {"acc": d_acc, "lat_ns": d_lat, "n_eval": 5},
                                    "E": {"acc": e_acc, "lat_ns": e_lat, "n_eval": 5}})
    v, msg = compute_verdict(fake_hp_cells)
    assert "HARD_PASS" in v, f"expected HP, got {v}: {msg}"

    # HF: all 3 drop below 0.30 at K >= 250
    fake_hf = []
    for K in K_PATHS_FULL:
        for s in SEEDS_FULL:
            acc = 0.50 if K < HF_K_HIGH_MIN else 0.15
            fake_hf.append({"depth": 4, "M": 512, "K": K, "seed": s,
                              "B": {"acc": acc, "lat_ns": K * 1000, "n_eval": 5},
                              "D": {"acc": acc, "lat_ns": K * K * 100, "n_eval": 5},
                              "E": {"acc": acc, "lat_ns": K * 500, "n_eval": 5}})
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Forward pass on CPU
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, M_SMOKE, depth=3, K=10, seed=17,
                       n_queries=2, device=device)
    assert "B" in out and "D" in out and "E" in out
    for pn in ("B", "D", "E"):
        assert 0.0 <= out[pn]["acc"] <= 1.0
        assert out[pn]["lat_ns"] >= 0
    print(f"[selftest] large_k_path_scaling_v1_n4096 PASS "
          f"smoke d=3 K=10 B_acc={out['B']['acc']:.2f} "
          f"D_acc={out['D']['acc']:.2f} E_acc={out['E']['acc']:.2f} "
          f"B_lat={out['B']['lat_ns']}ns D_lat={out['D']['lat_ns']}ns "
          f"E_lat={out['E']['lat_ns']}ns", flush=True)


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
    M_cfg = M_SMOKE if smoke else M_FULL
    depth = DEPTH_SMOKE if smoke else DEPTH_FULL
    K_grid = K_PATHS_SMOKE if smoke else K_PATHS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    n_q = N_QUERIES_SMOKE if smoke else N_QUERIES_FULL

    out_dir = REPO / "data" / "exp_large_k_path_scaling_v1_n4096"
    out_dir.mkdir(parents=True, exist_ok=True)
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] large_k_path_scaling_v1 smoke={smoke} N={N_cfg} M={M_cfg} "
          f"depth={depth} K_paths={K_grid} seeds={seeds} n_queries={n_q} "
          f"done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for K in K_grid:
        for seed in seeds:
            ck = f"K{K}_seed{seed}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    cells.append(body); continue
            try:
                out = measure_cell(N_cfg, M_cfg, depth, K, seed, n_q, device)
                write_partial_key(out_dir, ck, out)
                cells.append(out)
                print(f"  K={K} seed={seed} "
                      f"B=({out['B']['acc']:.2f},{out['B']['lat_ns']:.0f}ns) "
                      f"D=({out['D']['acc']:.2f},{out['D']['lat_ns']:.0f}ns) "
                      f"E=({out['E']['acc']:.2f},{out['E']['lat_ns']:.0f}ns) "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  K={K} seed={seed} FAILED: {e}", flush=True)
                if device.type == "cuda":
                    torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "large_k_path_scaling_v1_n4096", "N": N_cfg,
               "smoke": smoke, "M": M_cfg, "depth": depth, "K_paths": K_grid,
               "seeds": seeds, "n_queries": n_q, "cells": cells,
               "verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
