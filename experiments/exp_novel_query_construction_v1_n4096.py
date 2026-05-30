"""S13 NOVEL QUERY CONSTRUCTION v1 at N=4096 (E3.5).

Can substrate construct novel multi-hop combinations from stored
single-hop facts? Tests combinatorial reasoning over stored facts.

SETUP:
  Store (k_A, v_B), (k_C, v_D) pairs (single-hop only; NO explicit
  A->B->C->D chains).

QUERIES:
  Ask substrate to construct novel chains (A->B->C->D combinations)
  at depths 3 and 4.

NOTE: P=0.30-0.50 prior per user msg (speculative but enabling if
positive). Annotated in prereg.

PRE-REGISTERED BANDS:
  HP = at least one path achieves >=60% accuracy on novel-query
       construction at depth 3-4.
  HF = all paths < 20% (no combinatorial reasoning).
  MB = otherwise.

PROT-018: _n4096.
Anchor: novel_query_construction_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_novel_query_construction_v1_n4096.md
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

from experiments._multi_hop_mechanisms import (  # noqa: E402
    build_shared, path_b_run, path_d_run, path_e_run,
)
from experiments._relation_graph import (  # noqa: E402
    sample_coherent_starts, sample_incoherent_paths,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_s13", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


N = 4096
N_FULL  = N
N_SMOKE = 1024
M_PROD = 2048
M_SMOKE = 256
DEPTHS = [3, 4]
DEPTHS_SMOKE = [3]
K_PATHS = 100
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_NOVEL_QUERIES = 16

HP_ACC = 0.60
HF_ACC = 0.20


def get_output_dir(default_name: str = "novel_query_construction_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def construct_novel_queries(relation: Dict[int, int], depth: int, n_q: int,
                              seed: int) -> List[Tuple[int, int]]:
    """Sample (start, expected_end) pairs where the path exists in `relation`
    transitively (depth hops). The substrate stores single-hop facts only;
    the test is whether multi-hop COMBINATION succeeds."""
    g = torch.Generator().manual_seed(seed + 13)
    keys = list(relation.keys())
    out = []
    for _ in range(n_q * 20):
        if len(out) >= n_q: break
        i = int(torch.randint(0, len(keys), (1,), generator=g).item())
        start = keys[i]
        cur = start
        ok = True
        for _ in range(depth):
            nxt = relation.get(cur)
            if nxt is None:
                ok = False
                break
            cur = int(nxt)
        if ok:
            out.append((int(start), int(cur)))
    return out


def measure_seed(N_use: int, M: int, depth: int, K: int, seed: int,
                  device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)
    C = codebook.shape[0]

    queries = construct_novel_queries(relation, depth, N_NOVEL_QUERIES, seed)
    if not queries:
        return {"seed": int(seed), "M": int(M), "depth": int(depth),
                "n_queries": 0,
                "path_b_acc": 0.0, "path_d_acc": 0.0, "path_e_auc": 0.5}

    starts = torch.tensor([q[0] for q in queries], dtype=torch.long, device=device)
    targets = torch.tensor([q[1] for q in queries], dtype=torch.long, device=device)

    # Path B: continuous propagation through stored single-hop facts
    pred_b = path_b_run(codebook, W, starts, depth, N_use)
    acc_b = float((pred_b == targets).float().mean().item())

    # Path D: Bayesian posterior over candidate paths
    correct_d = path_d_run(codebook, W, starts, relation, depth, K, seed, N_use)
    acc_d = float(correct_d.mean().item())

    # Path E: spectral coherence
    pos = sample_coherent_starts(relation, depth, N_NOVEL_QUERIES, seed)
    neg = sample_incoherent_paths(C, depth, N_NOVEL_QUERIES, seed, relation=relation)
    if pos and neg:
        auc_e = path_e_run(codebook, W, pos, neg, N_use)
    else:
        auc_e = 0.5

    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {"seed": int(seed), "M": int(M), "depth": int(depth),
            "n_queries": int(len(queries)),
            "path_b_acc": round(acc_b, 5),
            "path_d_acc": round(acc_d, 5),
            "path_e_auc": round(auc_e, 5)}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("S13_INCONCLUSIVE", "no cells")

    means_b = []
    means_d = []
    means_e = []
    by_depth: Dict[int, List[Dict]] = {}
    for c in cells:
        by_depth.setdefault(c["depth"], []).append(c)

    # per-depth path accuracy
    path_b_pass = False; path_d_pass = False; path_e_pass = False
    for d, cs in by_depth.items():
        m_b = sum(c["path_b_acc"] for c in cs) / len(cs)
        m_d = sum(c["path_d_acc"] for c in cs) / len(cs)
        m_e = sum(c["path_e_auc"] for c in cs) / len(cs)
        means_b.append(m_b); means_d.append(m_d); means_e.append(m_e)
        if m_b >= HP_ACC: path_b_pass = True
        if m_d >= HP_ACC: path_d_pass = True
        if max(0.0, (m_e - 0.5) * 2.0) >= HP_ACC: path_e_pass = True

    max_b = max(means_b) if means_b else 0.0
    max_d = max(means_d) if means_d else 0.0
    max_e = max(means_e) if means_e else 0.5

    detail = (f"max_b={max_b:.3f} max_d={max_d:.3f} max_e={max_e:.3f} "
              f"depths={list(by_depth.keys())}")

    if path_b_pass or path_d_pass or path_e_pass:
        return ("S13_HARD_PASS", "NOVEL_QUERY_OPEN: " + detail)
    if max_b < HF_ACC and max_d < HF_ACC and max(0.0, (max_e - 0.5) * 2.0) < HF_ACC:
        return ("S13_HARD_FAIL", "NO_COMBINATORIAL_REASONING: " + detail)
    return ("S13_MIDDLE_BAND", "PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    device = torch.device("cpu")
    out = measure_seed(N_SMOKE, 64, 2, 20, 17, device)
    assert "path_b_acc" in out
    print(f"[selftest] novel_query_construction_v1_n4096 PASS "
          f"path_b={out['path_b_acc']:.3f} path_d={out['path_d_acc']:.3f} "
          f"path_e={out['path_e_auc']:.3f}", flush=True)


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
    M = M_SMOKE if smoke else M_PROD
    depths = DEPTHS_SMOKE if smoke else DEPTHS
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] novel_query_construction smoke={smoke} N={N_cfg} M={M} "
          f"depths={depths} K={K_PATHS} seeds={seeds} done={len(done)} "
          f"device={device.type}", flush=True)

    cells: List[Dict] = []
    for depth in depths:
        for seed in seeds:
            ck = f"d{depth}_seed{seed}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    cells.append(body); continue
            try:
                out = measure_seed(N_cfg, M, depth, K_PATHS, seed, device)
                write_partial_key(out_dir, ck, out)
                cells.append(out)
                print(f"  d={depth} s={seed} done ({time.time()-t0:.1f}s)",
                      flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  d={depth} s={seed} FAILED: {e}", flush=True)
                if device.type == "cuda":
                    torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "novel_query_construction_v1_n4096",
               "N": N_cfg, "smoke": smoke,
               "M": M, "depths": depths, "K_paths": K_PATHS, "seeds": seeds,
               "cells": cells, "verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
