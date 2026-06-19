"""MULTI-HOP HIGHER-M STRESS v1 at N=4096 (paths B/D/E composite).

CONTEXT:
  N-batch (commit e457f1e, 947b22e) returned all 3 multi-hop paths
  (B continuous-output, D Bayesian path-probability, E spectral) HARD_PASS
  at M=256 with unanimous 1.000 accuracy across depths 2-5.
  Trivialization caveat: M=256 << N=4096 substrate capacity ~16K-20K.

SCIENTIFIC QUESTION:
  Does the triple-path multi-hop rescue (Paths B, D, E) sustain accuracy at
  production-relevant M (>= N/2), or was M=256 a sub-capacity trivialization?
  Differential survival across paths IS the informative signal.

PRE-REGISTERED BANDS (per user msg):
  HP = at least one path achieves:
        M=2048 depth-5 >= 0.80 in >=3/5 seeds AND
        M=4096 depth-5 >= 0.70 in >=3/5 seeds AND
        M=8192 depth-5 >= 0.60 in >=3/5 seeds
  HF = no path achieves >= 0.50 accuracy at any (M, depth) cell with M >= 2048.
       (trivialization confirmed; sub-capacity-only claim stands)
  MIDDLE_BAND = otherwise.

REUSE:
  Imports propagate_continuous (Path B), score_paths/per_hop_loglik (Path D),
  coherence_score/roc_auc (Path E) from the N-batch single-path scripts.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. paths = ['B', 'D', 'E']; M_grid = [2048, 4096, 8192]; depths = [3, 4, 5].
  3. Path B: uniform-accuracy from argmax-of-continuous propagation.
  4. Path D: top-1 = argmax(log-posterior of candidate paths).
  5. Path E: AUC of coherence score across coherent vs incoherent paths
     (Path E reports AUC; we convert to a comparable accuracy by using
     thresholded-AUC >= 0.80 as "path identified" similar to its v1 HP gate).
     For uniform per-path-per-M-per-depth accuracy reporting, we report
     min(1.0, max(0.0, 2*(auc - 0.5))) as Path E's accuracy field.
  6. HP/HF gate triggered correctly by synthetic survival patterns.

OOM CHECK:
  M=8192, N=4096: keys+vals = 8192*4096*4*2 = 256 MiB.
  W = 4096^2 * 4 = 64 MiB. CB = 4096*4096*4 = 64 MiB (C=N here).
  Path D K_paths up to 500 per query, depth=5: 2500 hops/query, ~50 queries.
  Peak ~ 1 GiB. OK on 8 GiB GPU.

TIMEOUT ESTIMATE (per-experiment timeout):
  smoke_wall_s ~ 60s (small-N path-D dominates).
  Cells: 3 paths x 3 M x 3 depths x 5 seeds = 135 cell-seeds.
  Path B scaling exp ~1.5 (matmul-dominant per cell).
  FULL/smoke ratios: N 4 (1024->4096), seeds 5 (1->5), paths 3.
  ceil(1.5 * 60 * 4^1.5 * 5 * 3) = ceil(10800) = 10800.
  Round up + pad for path D's K_paths inner loop -> 21600s.
  Within 14400 limit? 21600 > 14400. The user explicitly approved >14400 in
  the dispatch (135 cell-seeds across 3 path mechanisms at production M is
  the load-bearing scope of this whole shipment); the prereg flags this.
  Use 21600s, document as user-approved.

N-suffix: _n4096 (PROT-018; N production = 4096).
Anchor: multi_hop_higher_m_stress_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_multi_hop_higher_m_stress_v1_n4096.md
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

from experiments._metric_battery import make_substrate  # noqa: E402
from experiments._relation_graph import (  # noqa: E402
    build_relation_facts,
    sample_coherent_starts,
    sample_incoherent_paths,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_mh", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key

# Path-mechanism imports (reuse N-batch scripts)
_b_path = REPO / "experiments" / "exp_continuous_output_multi_hop_v1_n4096.py"
# We avoid executing the source module (it runs its own selftest at import).
# Instead, we re-implement the small kernels here, derived from those scripts.


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096
N_FULL  = N
N_SMOKE = 1024
M_GRID_FULL  = [2048, 4096, 8192]
M_GRID_SMOKE = [128]
DEPTHS_FULL  = [3, 4, 5]
DEPTHS_SMOKE = [3]
SEEDS_FULL   = [7, 17, 23, 31, 41]
SEEDS_SMOKE  = [17]
PATHS = ["B", "D", "E"]
N_PATHS_QUERY_FULL = 80     # Path B / E sample size per cell
N_PATHS_QUERY_SMOKE = 16
K_PATHS_D_FULL  = 100        # Path D candidate-set size per query
K_PATHS_D_SMOKE = 20
N_POS_E_FULL = 80            # Path E positives per cell
N_NEG_E_FULL = 80
N_POS_E_SMOKE = 16
N_NEG_E_SMOKE = 16
TOP_K_SIG = 16
BETA = 4.0

# HP thresholds per-M (depth 5 specifically per user spec)
HP_THRESH = {2048: 0.80, 4096: 0.70, 8192: 0.60}
HP_SEEDS_MIN = 3
HP_DEPTH = 5
HF_THRESH = 0.50
HF_M_MIN = 2048


def get_output_dir(default_name: str = "multi_hop_higher_m_stress_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_substrate_with_relation(N_use: int, M: int, seed: int,
                                    device: torch.device):
    """Build substrate AND coherent relation graph (closed) at this (N, M, seed)."""
    codebook, _W, _keys, _vals, _ki, _vi = make_substrate(
        N_use, M, seed, device)
    key_idx, val_idx, relation = build_relation_facts(
        n_idx=codebook.shape[0], M=M, seed=seed, device=device, closed=True)
    keys_vec = codebook[key_idx]
    vals_vec = codebook[val_idx]
    W = (vals_vec.T @ keys_vec) / N_use
    return codebook, W, key_idx, val_idx, relation


# Path B kernel ------------------------------------------------------------
def path_b_accuracy(codebook, W, relation, depth, n_paths, seed, N_use, device):
    paths = sample_coherent_starts(relation, depth=depth, n_paths=n_paths,
                                     seed=seed + depth)
    if not paths:
        return 0.0, 0
    starts = torch.tensor([p[0] for p in paths], dtype=torch.long, device=device)
    targets = torch.tensor([p[-1] for p in paths], dtype=torch.long, device=device)
    q = codebook[starts]
    for _ in range(depth):
        q = q @ W.T
    sims = (codebook @ q.T) / N_use
    pred = torch.argmax(sims, dim=0)
    acc = float((pred == targets).float().mean().item())
    return acc, len(paths)


# Path D kernel ------------------------------------------------------------
def _per_hop_loglik(codebook, W, src_idx, dst_idx, N_use, beta):
    src = codebook[src_idx]
    dst = codebook[dst_idx]
    out = src @ W.T
    sims = (out * dst).sum(dim=1) / N_use
    logits = beta * sims
    return -torch.nn.functional.softplus(-logits)


def _score_paths(codebook, W, paths, N_use, beta, device):
    K = len(paths)
    depth = len(paths[0]) - 1 if paths else 0
    if K == 0 or depth <= 0:
        return torch.zeros(K, device=device)
    src = torch.tensor([p[i]     for p in paths for i in range(depth)],
                        dtype=torch.long, device=device)
    dst = torch.tensor([p[i + 1] for p in paths for i in range(depth)],
                        dtype=torch.long, device=device)
    ll = _per_hop_loglik(codebook, W, src, dst, N_use, beta)
    return ll.view(K, depth).sum(dim=1)


def path_d_accuracy(codebook, W, relation, depth, K_paths, n_queries, seed,
                     N_use, beta, device):
    """Path D top-1 accuracy: for each of n_queries coherent positives,
    rank against (K_paths - 1) decoys. Return fraction correct."""
    pos_paths = sample_coherent_starts(relation, depth=depth,
                                         n_paths=n_queries, seed=seed + depth)
    if not pos_paths:
        return 0.0, 0
    C = codebook.shape[0]
    correct = 0
    n_eval = 0
    for pos in pos_paths:
        decoys = sample_incoherent_paths(C, depth=depth,
                                           n_paths=K_paths - 1,
                                           seed=seed + depth + hash(tuple(pos)) % 100,
                                           relation=relation)
        if not decoys:
            continue
        candidates = [pos] + decoys
        scores = _score_paths(codebook, W, candidates, N_use, beta, device)
        idx_top = int(torch.argmax(scores).item())
        if idx_top == 0:
            correct += 1
        n_eval += 1
    if n_eval == 0:
        return 0.0, 0
    return correct / n_eval, n_eval


# Path E kernel ------------------------------------------------------------
def _spectral_signature(response, codebook, N_use, top_k):
    sims = (codebook @ response) / N_use
    return torch.topk(sims, top_k).values


def _coherence_score(codebook, W, path, N_use, top_k):
    depth = len(path) - 1
    if depth < 1:
        return 0.0
    src = codebook[torch.tensor(path[:-1], dtype=torch.long, device=codebook.device)]
    responses = src @ W.T
    sigs = [_spectral_signature(responses[i], codebook, N_use, top_k) for i in range(depth)]
    if len(sigs) < 2:
        dst = codebook[path[-1]]
        s_dst = _spectral_signature(dst, codebook, N_use, top_k)
        return float(torch.nn.functional.cosine_similarity(
            sigs[0].unsqueeze(0), s_dst.unsqueeze(0)).item())
    coh = []
    for i in range(len(sigs) - 1):
        coh.append(float(torch.nn.functional.cosine_similarity(
            sigs[i].unsqueeze(0), sigs[i + 1].unsqueeze(0)).item()))
    return sum(coh) / len(coh)


def _roc_auc(labels, scores):
    n_pos = sum(labels)
    n_neg = len(labels) - n_pos
    if n_pos == 0 or n_neg == 0:
        return 0.5
    pairs = sorted(zip(scores, labels), key=lambda x: x[0])
    sum_pos = 0
    for rank, (_, lab) in enumerate(pairs, start=1):
        if lab == 1:
            sum_pos += rank
    return float((sum_pos - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def path_e_accuracy(codebook, W, relation, depth, n_pos, n_neg, seed,
                     N_use, device):
    """Path E accuracy mapping: substrate identifies coherent paths via
    spectral coherence. We compute AUC and map to accuracy-like scale:
        acc_E := clip(2 * (AUC - 0.5), 0, 1)
    so AUC=0.5 -> 0.0 (chance), AUC=1.0 -> 1.0 (perfect)."""
    pos_paths = sample_coherent_starts(relation, depth=depth, n_paths=n_pos,
                                         seed=seed + depth)
    if not pos_paths:
        return 0.0, 0
    neg_paths = sample_incoherent_paths(codebook.shape[0], depth=depth,
                                          n_paths=n_neg, seed=seed + depth,
                                          relation=relation)
    if not neg_paths:
        return 0.0, 0
    scores = []
    labels = []
    for p in pos_paths:
        scores.append(_coherence_score(codebook, W, p, N_use, TOP_K_SIG))
        labels.append(1)
    for p in neg_paths:
        scores.append(_coherence_score(codebook, W, p, N_use, TOP_K_SIG))
        labels.append(0)
    auc = _roc_auc(labels, scores)
    acc_e = max(0.0, min(1.0, 2.0 * (auc - 0.5)))
    return acc_e, len(pos_paths) + len(neg_paths)


# Per-cell harness --------------------------------------------------------
def measure_cell(path: str, N_use: int, M: int, depth: int, seed: int,
                  device: torch.device, smoke: bool) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_substrate_with_relation(
        N_use, M, seed, device)
    n_q = N_PATHS_QUERY_SMOKE if smoke else N_PATHS_QUERY_FULL
    if path == "B":
        acc, n_used = path_b_accuracy(codebook, W, relation, depth, n_q,
                                        seed, N_use, device)
        extra = {}
    elif path == "D":
        K = K_PATHS_D_SMOKE if smoke else K_PATHS_D_FULL
        acc, n_used = path_d_accuracy(codebook, W, relation, depth, K,
                                        n_q, seed, N_use, BETA, device)
        extra = {"K_paths": K}
    elif path == "E":
        n_pos = N_POS_E_SMOKE if smoke else N_POS_E_FULL
        n_neg = N_NEG_E_SMOKE if smoke else N_NEG_E_FULL
        acc, n_used = path_e_accuracy(codebook, W, relation, depth, n_pos,
                                        n_neg, seed, N_use, device)
        extra = {"acc_definition": "2*(AUC-0.5) clipped to [0,1]"}
    else:
        raise ValueError(f"unknown path {path!r}")

    out = {"path": path, "N": int(N_use), "M": int(M), "depth": int(depth),
           "seed": int(seed), "accuracy": round(acc, 5),
           "n_used": int(n_used)}
    out.update(extra)

    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return out


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("MH_M_STRESS_INCONCLUSIVE", "No cells.")

    # Per-(path, M, depth) seed counts
    by_pmd: Dict[Tuple[str, int, int], List[Dict]] = {}
    for c in cells:
        by_pmd.setdefault((c["path"], c["M"], c["depth"]), []).append(c)

    # HP per-path: requires all three (M=2048, M=4096, M=8192) at depth=HP_DEPTH=5
    paths_passing: List[str] = []
    per_path_pass_record: Dict[str, Dict[int, int]] = {}
    for p in PATHS:
        rec: Dict[int, int] = {}
        ok_path = True
        for M in [2048, 4096, 8192]:
            key = (p, M, HP_DEPTH)
            cs = by_pmd.get(key, [])
            n_pass = sum(1 for c in cs if c["accuracy"] >= HP_THRESH[M])
            rec[M] = n_pass
            if n_pass < HP_SEEDS_MIN:
                ok_path = False
        per_path_pass_record[p] = rec
        if ok_path:
            paths_passing.append(p)

    # HF: no path achieves >= HF_THRESH at any (M>=HF_M_MIN, depth) cell
    any_path_M_d_pass = False
    for (p, M, d), cs in by_pmd.items():
        if M < HF_M_MIN:
            continue
        for c in cs:
            if c["accuracy"] >= HF_THRESH:
                any_path_M_d_pass = True
                break
        if any_path_M_d_pass:
            break

    # Per-path-per-M-per-depth accuracy summary
    detail_parts: List[str] = []
    for p in PATHS:
        for M in [2048, 4096, 8192]:
            for d in [3, 4, 5]:
                key = (p, M, d)
                cs = by_pmd.get(key, [])
                if not cs:
                    continue
                vals = [c["accuracy"] for c in cs]
                mean = sum(vals) / len(vals)
                detail_parts.append(f"{p}_{M}_{d}={mean:.3f}")
    detail = (f"path_M_depth_acc: " + " ".join(detail_parts) +
              f" | paths_passing={paths_passing} hp_record={per_path_pass_record} "
              f"any_path_M_d_pass={any_path_M_d_pass}")

    if not any_path_M_d_pass:
        return ("MH_M_STRESS_HARD_FAIL",
                "TRIVIALIZATION_CONFIRMED_SUB_CAPACITY_ONLY: " + detail)
    if paths_passing:
        return ("MH_M_STRESS_HARD_PASS",
                f"DURABLE_AT_PRODUCTION_M_PATHS={','.join(paths_passing)}: " +
                detail)
    return ("MH_M_STRESS_MIDDLE_BAND",
            "PARTIAL_M_DURABILITY: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096, got {N_FULL}"
    assert M_GRID_FULL == [2048, 4096, 8192]
    assert DEPTHS_FULL == [3, 4, 5]
    assert HP_DEPTH == 5

    # HP gate: synthetic accuracy where ONE path passes all 3 M at depth 5
    fake_hp: List[Dict] = []
    for p in PATHS:
        for M in M_GRID_FULL:
            for d in DEPTHS_FULL:
                for s in SEEDS_FULL:
                    if p == "B":
                        acc = HP_THRESH[M] + 0.05 if d == HP_DEPTH else 0.50
                    else:
                        acc = 0.20    # other paths don't pass
                    fake_hp.append({"path": p, "N": N_FULL, "M": M, "depth": d,
                                      "seed": s, "accuracy": acc, "n_used": 50})
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, f"HP gate failed: {v}"

    # HF gate: all cells at M>=2048 below HF_THRESH
    fake_hf: List[Dict] = []
    for p in PATHS:
        for M in M_GRID_FULL:
            for d in DEPTHS_FULL:
                for s in SEEDS_FULL:
                    fake_hf.append({"path": p, "N": N_FULL, "M": M, "depth": d,
                                      "seed": s, "accuracy": 0.20, "n_used": 50})
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, f"HF gate failed: {v}"

    # Middle band: at least one cell passes HF but no path passes HP
    fake_mb: List[Dict] = []
    for p in PATHS:
        for M in M_GRID_FULL:
            for d in DEPTHS_FULL:
                for s in SEEDS_FULL:
                    fake_mb.append({"path": p, "N": N_FULL, "M": M, "depth": d,
                                      "seed": s, "accuracy": 0.55, "n_used": 50})
    v, _ = compute_verdict(fake_mb); assert "MIDDLE_BAND" in v, f"MB gate failed: {v}"

    # AUC sanity
    auc = _roc_auc([1, 1, 0, 0], [0.9, 0.8, 0.4, 0.2])
    assert auc == 1.0, f"AUC sanity: {auc}"

    # Forward pass on CPU at tiny scale for each path
    device = torch.device("cpu")
    for p in PATHS:
        out = measure_cell(p, N_SMOKE, 32, 3, 17, device, smoke=True)
        assert out["accuracy"] is not None
        assert 0.0 <= out["accuracy"] <= 1.0
        assert out["n_used"] >= 0
    print(f"[selftest] multi_hop_higher_m_stress_v1_n4096 PASS "
          f"all 3 paths instrumented; verdict gates HP/HF/MB OK",
          flush=True)


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
    Ms     = M_GRID_SMOKE if smoke else M_GRID_FULL
    depths = DEPTHS_SMOKE if smoke else DEPTHS_FULL
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] multi_hop_higher_m_stress_v1 smoke={smoke} N={N_cfg} "
          f"Ms={Ms} depths={depths} seeds={seeds} paths={PATHS} "
          f"done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for path in PATHS:
        for M in Ms:
            for d in depths:
                for seed in seeds:
                    ck = f"p{path}_M{M}_d{d}_seed{seed}"
                    if ck in done:
                        body = load_partial_key(out_dir, ck)
                        if body is not None:
                            cells.append(body); continue
                    try:
                        out = measure_cell(path, N_cfg, M, d, seed,
                                             device, smoke=smoke)
                        write_partial_key(out_dir, ck, out)
                        cells.append(out)
                        print(f"  p={path} M={M} d={d} seed={seed} "
                              f"acc={out['accuracy']:.3f} "
                              f"n_used={out['n_used']} "
                              f"({time.time()-t0:.1f}s)", flush=True)
                    except (RuntimeError, MemoryError) as e:
                        print(f"  p={path} M={M} d={d} seed={seed} "
                              f"FAILED: {e}", flush=True)
                        if device.type == "cuda":
                            torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "multi_hop_higher_m_stress_v1_n4096", "N": N_cfg,
               "smoke": smoke, "Ms": Ms, "depths": depths, "seeds": seeds,
               "paths": PATHS, "cells": cells,
               "verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
