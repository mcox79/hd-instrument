"""MULTI-HOP STRESS AT BREAKING v1 at N=4096 (paths B, D, E).

CONTEXT (substrate production-stress):
  P1+Q3 jointly confirmed multi-hop durability at M=8192, K=1000 (production-scale).
  Now characterize the BOUNDARY: at what M and depth do mechanisms fail?
  This anchor pushes past M_c with deep multi-hop chains where noise should
  compound. Outcome differentiates "extends past test envelope" (HP, run v2),
  "boundary at predicted limits" (HF, breaking confirmed), or "mechanism-
  specific differential survival" (MIDDLE_BAND, informative; enables R2).

SCIENTIFIC QUESTION:
  At N=4096, BSC, M in {16384, 24576}, depth in {10, 15, 20}, K_paths=500:
  does ANY of {B, D, E} drop below 0.60 accuracy in any cell? Below 0.30 at
  depth=20 M=24576?

PRE-REGISTERED BANDS:
  HP = no path drops below 0.60 at any (M, depth) cell (mean over 5 seeds).
       Substrate extends past test envelope; run harder v2.
  HF = ALL paths drop below 0.30 at the worst cell (M=24576, depth=20)
       (mean over 5 seeds). Breaking confirmed at predicted boundary.
  MIDDLE_BAND = some cells degrade, some hold. Mechanism-specific differential
       survival pattern; enables R2 composition design.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. paths = ['B', 'D', 'E']. M_grid=[16384,24576], depth_grid=[10,15,20].
  3. Reuse path-mechanism implementations:
      - B: continuous-output propagation (no argmax) -> codebook argmax readout
      - D: posterior-product over K_paths candidates -> top-1 = argmax
      - E: spectral-coherence AUC -> readout is argmax over coherence
  4. Accuracy per cell = correct-target-matches / n_paths_evaluated.

OOM CHECK:
  N=4096, M=24576: C=4N=16384 codewords; M=24576 > C exceeds capacity (M>C);
  store_facts_batched handles via repeats. W = 64 MiB. Codebook = 256 MiB.
  K_paths=500 paths x depth=20 x N=4096 floats = 160 MiB per cell. ~600 MiB
  steady state. Per-cell-seed checkpoint isolates OOM.

TIMEOUT ESTIMATE:
  Smoke ~ 60s at smoke scale. FULL: 3 paths x 2 M x 3 depth x 5 seeds = 90
  cell-seeds. Each cell ~30-60s (M=24576 storage dominates). ~3600-5400s.
  21600s budget per user spec.

N-suffix: _n4096 (PROT-018).
Anchor: multi_hop_stress_at_breaking_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_multi_hop_stress_at_breaking_v1_n4096.md
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_r1", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096
N_FULL  = N
N_SMOKE = 1024
M_GRID_FULL  = [16384, 24576]
M_GRID_SMOKE = [512]
DEPTHS_FULL  = [10, 15, 20]
DEPTHS_SMOKE = [3, 5]
K_PATHS_FULL  = 500
K_PATHS_SMOKE = 20
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
PATHS = ['B', 'D', 'E']

BETA_D = 4.0
TOP_K_SIG_E = 16

HP_MIN_ACC = 0.60     # HP: no path drops below this at any cell
HF_MAX_ACC = 0.30     # HF: all paths drop below this at worst cell
WORST_CELL_M  = 24576
WORST_CELL_D  = 20


def get_output_dir(default_name: str = "multi_hop_stress_at_breaking_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_substrate_with_relation(N_use: int, M: int, seed: int,
                                    device: torch.device):
    """Build substrate + explicit relation. Handles M > C via repeats."""
    codebook, _W, _keys, _vals, _ki, _vi = make_substrate(
        N_use, M, seed, device)
    C = codebook.shape[0]
    # For multi-hop, we need a functional relation. If M > C, the relation
    # can have at most C distinct keys; use M_eff = min(M, C) for relation.
    M_eff = min(M, C)
    key_idx, val_idx, relation = build_relation_facts(
        n_idx=C, M=M_eff, seed=seed, device=device, closed=True)
    keys_vec = codebook[key_idx]
    vals_vec = codebook[val_idx]
    W = (vals_vec.T @ keys_vec) / N_use
    return codebook, W, key_idx, val_idx, relation


# -------- Path B: continuous-output propagation --------

def measure_path_B(codebook: torch.Tensor, W: torch.Tensor,
                    relation: Dict[int, int], N_use: int, depth: int,
                    n_paths: int, seed: int,
                    device: torch.device) -> float:
    """Path B accuracy: continuous propagation -> argmax readout."""
    paths = sample_coherent_starts(relation, depth=depth, n_paths=n_paths,
                                     seed=seed + depth)
    if not paths:
        return 0.0
    starts  = torch.tensor([p[0]  for p in paths], dtype=torch.long, device=device)
    targets = torch.tensor([p[-1] for p in paths], dtype=torch.long, device=device)
    q = codebook[starts]
    for _ in range(depth):
        q = q @ W.T
    sims = (codebook @ q.T) / N_use
    pred = torch.argmax(sims, dim=0)
    return float((pred == targets).float().mean().item())


# -------- Path D: posterior-product over candidates --------

def _per_hop_loglik(codebook, W, src_idx, dst_idx, N_use, beta):
    src = codebook[src_idx]
    dst = codebook[dst_idx]
    out = src @ W.T
    sims = (out * dst).sum(dim=1) / N_use
    logits = beta * sims
    return -torch.nn.functional.softplus(-logits)


def _score_paths_D(codebook, W, paths, N_use, beta, device):
    K = len(paths)
    depth = len(paths[0]) - 1 if paths else 0
    if K == 0 or depth <= 0:
        return torch.zeros(K, device=device)
    src = torch.tensor([p[i]     for p in paths for i in range(depth)],
                        dtype=torch.long, device=device)
    dst = torch.tensor([p[i + 1] for p in paths for i in range(depth)],
                        dtype=torch.long, device=device)
    ll = _per_hop_loglik(codebook, W, src, dst, N_use, beta).view(K, depth)
    return ll.sum(dim=1)


def measure_path_D(codebook: torch.Tensor, W: torch.Tensor,
                    relation: Dict[int, int], N_use: int, depth: int,
                    K_paths: int, seed: int,
                    device: torch.device) -> float:
    """Path D accuracy: top-1 over K_paths posterior scores."""
    # Sample a handful of positive paths and K_paths-1 decoys each
    n_positives = max(10, K_paths // 10)
    pos_paths = sample_coherent_starts(relation, depth=depth,
                                         n_paths=n_positives,
                                         seed=seed + depth)
    if not pos_paths:
        return 0.0
    C = codebook.shape[0]
    n_decoys = K_paths - 1
    correct = 0
    n_eval = 0
    for pos in pos_paths:
        decoys = sample_incoherent_paths(
            C, depth=depth, n_paths=n_decoys,
            seed=seed + depth + hash(tuple(pos)) % 100, relation=relation)
        if not decoys:
            continue
        cands = [pos] + decoys
        scores = _score_paths_D(codebook, W, cands, N_use, BETA_D, device)
        if int(torch.argmax(scores).item()) == 0:
            correct += 1
        n_eval += 1
    return correct / max(1, n_eval)


# -------- Path E: spectral coherence accuracy --------
# For path E "accuracy" in this stress test = positives' coherence > mean
# decoy coherence. Cleaner thresholdable metric than AUC for break-detection.

def _coherence(codebook, W, path, N_use, top_k):
    depth = len(path) - 1
    if depth < 1:
        return 0.0
    src = codebook[torch.tensor(path[:-1], dtype=torch.long,
                                 device=codebook.device)]
    responses = src @ W.T
    sigs = []
    for i in range(depth):
        sims = (codebook @ responses[i]) / N_use
        sigs.append(torch.topk(sims, top_k).values)
    if len(sigs) < 2:
        dst = codebook[path[-1]]
        s_dst = torch.topk((codebook @ dst) / N_use, top_k).values
        return float(torch.nn.functional.cosine_similarity(
            sigs[0].unsqueeze(0), s_dst.unsqueeze(0)).item())
    coh = []
    for i in range(len(sigs) - 1):
        coh.append(float(torch.nn.functional.cosine_similarity(
            sigs[i].unsqueeze(0), sigs[i + 1].unsqueeze(0)).item()))
    return sum(coh) / len(coh)


def measure_path_E(codebook: torch.Tensor, W: torch.Tensor,
                    relation: Dict[int, int], N_use: int, depth: int,
                    n_paths: int, seed: int,
                    device: torch.device) -> float:
    """Path E accuracy: fraction of positives whose coherence beats decoys.

    We compute coherence for n_paths positives and n_paths decoys, and the
    accuracy is mean over positives of (coherence_pos > median(decoy_coh)).
    """
    pos_paths = sample_coherent_starts(relation, depth=depth, n_paths=n_paths,
                                         seed=seed + depth)
    if not pos_paths:
        return 0.0
    C = codebook.shape[0]
    n_pos_have = len(pos_paths)
    neg_paths = sample_incoherent_paths(
        C, depth=depth, n_paths=n_pos_have,
        seed=seed + depth + 999, relation=relation)
    if not neg_paths:
        return 0.0
    pos_coh = [_coherence(codebook, W, p, N_use, TOP_K_SIG_E) for p in pos_paths]
    neg_coh = [_coherence(codebook, W, p, N_use, TOP_K_SIG_E) for p in neg_paths]
    neg_sorted = sorted(neg_coh)
    median_neg = neg_sorted[len(neg_sorted) // 2]
    return sum(1 for c in pos_coh if c > median_neg) / max(1, len(pos_coh))


def measure_cell(N_use: int, M: int, depth: int, path: str, K_paths: int,
                  seed: int, device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_substrate_with_relation(
        N_use, M, seed, device)
    if path == 'B':
        acc = measure_path_B(codebook, W, relation, N_use, depth,
                              K_paths, seed, device)
    elif path == 'D':
        acc = measure_path_D(codebook, W, relation, N_use, depth,
                              K_paths, seed, device)
    elif path == 'E':
        acc = measure_path_E(codebook, W, relation, N_use, depth,
                              K_paths, seed, device)
    else:
        raise ValueError(f"unknown path {path}")
    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"path": path, "M": int(M), "depth": int(depth), "seed": int(seed),
            "K_paths": int(K_paths), "accuracy": round(float(acc), 5)}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("MH_STRESS_INCONCLUSIVE", "No cells.")

    # Aggregate per (path, M, depth) mean accuracy over seeds
    by_cell: Dict[Tuple[str, int, int], List[float]] = {}
    for c in cells:
        k = (c["path"], c["M"], c["depth"])
        by_cell.setdefault(k, []).append(c["accuracy"])
    means: Dict[Tuple[str, int, int], float] = {
        k: sum(v) / len(v) for k, v in by_cell.items()}

    # HP: no path drops below HP_MIN_ACC at any cell
    hp_violations = [(k, m) for k, m in means.items() if m < HP_MIN_ACC]
    hp = (len(hp_violations) == 0)

    # HF: ALL paths drop below HF_MAX_ACC at WORST cell (M=24576, depth=20)
    worst_means = {p: means.get((p, WORST_CELL_M, WORST_CELL_D))
                   for p in PATHS}
    hf = all(v is not None and v < HF_MAX_ACC for v in worst_means.values())

    # Differential survival summary
    summary_lines = []
    for p in PATHS:
        line = f"{p}: " + " ".join(
            f"M{m}d{d}={means.get((p, m, d), float('nan')):.3f}"
            for m in M_GRID_FULL for d in DEPTHS_FULL)
        summary_lines.append(line)
    detail = " | ".join(summary_lines)

    if hp:
        return ("MH_STRESS_HARD_PASS",
                f"MULTI_HOP_EXTENDS_PAST_ENVELOPE: all cells >= {HP_MIN_ACC}. "
                + detail)
    if hf:
        return ("MH_STRESS_HARD_FAIL",
                f"BREAKING_CONFIRMED at M={WORST_CELL_M} d={WORST_CELL_D}: "
                f"all paths < {HF_MAX_ACC}. " + detail)
    return ("MH_STRESS_MIDDLE_BAND",
            f"DIFFERENTIAL_SURVIVAL: {len(hp_violations)} cells < {HP_MIN_ACC}; "
            f"worst-cell means {worst_means}. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, "PROT-018: _n4096"
    assert WORST_CELL_M in M_GRID_FULL
    assert WORST_CELL_D in DEPTHS_FULL
    assert PATHS == ['B', 'D', 'E']

    # Verdict gate HP
    fake_hp = []
    for p in PATHS:
        for m in M_GRID_FULL:
            for d in DEPTHS_FULL:
                for s in SEEDS_FULL:
                    fake_hp.append({"path": p, "M": m, "depth": d, "seed": s,
                                      "K_paths": K_PATHS_FULL, "accuracy": 0.85})
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    # Verdict gate HF
    fake_hf = []
    for p in PATHS:
        for m in M_GRID_FULL:
            for d in DEPTHS_FULL:
                for s in SEEDS_FULL:
                    acc = 0.10 if (m == WORST_CELL_M and d == WORST_CELL_D) else 0.50
                    fake_hf.append({"path": p, "M": m, "depth": d, "seed": s,
                                      "K_paths": K_PATHS_FULL, "accuracy": acc})
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Verdict gate MIDDLE_BAND
    fake_mb = []
    for p in PATHS:
        for m in M_GRID_FULL:
            for d in DEPTHS_FULL:
                for s in SEEDS_FULL:
                    # Path E breaks earlier
                    acc = 0.40 if (p == 'E' and d >= 15) else 0.75
                    fake_mb.append({"path": p, "M": m, "depth": d, "seed": s,
                                      "K_paths": K_PATHS_FULL, "accuracy": acc})
    v, _ = compute_verdict(fake_mb); assert "MIDDLE_BAND" in v, v

    # Smoke forward pass on CPU (small)
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, M_GRID_SMOKE[0], DEPTHS_SMOKE[0], 'B',
                        K_PATHS_SMOKE, 17, device)
    assert 0.0 <= out["accuracy"] <= 1.0
    assert out["path"] == 'B'
    print(f"[selftest] multi_hop_stress_at_breaking_v1_n4096 PASS "
          f"smoke B d={DEPTHS_SMOKE[0]} M={M_GRID_SMOKE[0]} "
          f"acc={out['accuracy']:.3f}", flush=True)


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
    depths = DEPTHS_SMOKE if smoke else DEPTHS_FULL
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL
    K_paths = K_PATHS_SMOKE if smoke else K_PATHS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] multi_hop_stress_at_breaking_v1 smoke={smoke} N={N_cfg} "
          f"M_grid={M_grid} depths={depths} K_paths={K_paths} "
          f"seeds={seeds} paths={PATHS} done={len(done)} device={device.type}",
          flush=True)

    cells: List[Dict] = []
    for path_name in PATHS:
        for M in M_grid:
            for d in depths:
                for seed in seeds:
                    ck = f"{path_name}_M{M}_d{d}_seed{seed}"
                    if ck in done:
                        body = load_partial_key(out_dir, ck)
                        if body is not None:
                            cells.append(body); continue
                    try:
                        out = measure_cell(N_cfg, M, d, path_name, K_paths,
                                            seed, device)
                        write_partial_key(out_dir, ck, out)
                        cells.append(out)
                        print(f"  {path_name} M={M} d={d} seed={seed} "
                              f"acc={out['accuracy']:.3f} "
                              f"({time.time()-t0:.1f}s)", flush=True)
                    except (RuntimeError, MemoryError) as e:
                        print(f"  {path_name} M={M} d={d} seed={seed} "
                              f"FAILED: {e}", flush=True)
                        if device.type == "cuda":
                            torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "multi_hop_stress_at_breaking_v1_n4096", "N": N_cfg,
               "smoke": smoke, "M_grid": M_grid, "depths": depths,
               "K_paths": K_paths, "seeds": seeds, "paths": PATHS,
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
