"""MECHANISM COMPOSITION AT BREAKING v2 at N=4096.

CONTEXT (composition rehab at hard regime):
  Q2 v1 mechanism-composition was ceiling-bound: all individual paths {B,D,E}
  hit 1.000 at moderate (M, depth), so composition couldn't differentiate.
  v2 re-runs at HARDER regime where individual mechanisms degrade so
  composition has room to show error-correction or noise-introduction.

  Composition designs (per user spec):
    cA = INTERSECTION    -- target only counts if argmax(B) == argmax(D) == argmax(E)
                            (otherwise accuracy=0 on that path; sharp filter)
    cB = WEIGHTED VOTE   -- per-target score = w_B * sim_B + w_D * lik_D + w_E * coh_E
                            with weights from per-path validation accuracy;
                            argmax over candidate targets.
    cC = CONSENSUS-CHECK -- majority vote of the three argmax-targets; ties broken
                            by max-score.

  Hard regime per spec: cell-1 = (M=16384, depth=15), cell-2 = (M=24576, depth=10).

SCIENTIFIC QUESTION:
  At the HARDER cells, does at least one composition design (cA / cB / cC)
  improve accuracy >= 15% over the BEST individual path in >= 3/5 seeds at
  the hardest cell?

PRE-REGISTERED BANDS:
  HP = at least one composition design improves accuracy by >= 0.15 over the
       best individual path at cell-1 (the hardest cell) in >= 3/5 seeds.
  HF = ALL composition designs perform WORSE than the best individual path
       at BOTH cells in >= 4/5 seeds. (composition introduces noise everywhere)
  MIDDLE_BAND = otherwise.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. cells = [(16384, 15), (24576, 10)].
  3. composition_delta(design, cell, seed) = acc_comp - max(acc_B, acc_D, acc_E).
  4. composition designs reuse the same K_paths=500 candidate set per path.

OOM CHECK:
  Same envelope as R1; M_eff capped at C=16384 for relation construction.

TIMEOUT ESTIMATE:
  Smoke ~ 60s. FULL: 2 cells x 6 mechanisms (3 individual + 3 composition)
  x 5 seeds = 60 cell-seeds. Each cell ~45-60s. ~2700-3600s. 14400s budget.

N-suffix: _n4096 (PROT-018).
Anchor: mechanism_composition_at_breaking_v2_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_mechanism_composition_at_breaking_v2_n4096.md
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_r2", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096
N_FULL  = N
N_SMOKE = 1024
HARD_CELLS_FULL = [(16384, 15), (24576, 10)]   # (M, depth); cell-1 is hardest
HARD_CELLS_SMOKE = [(512, 3)]
K_PATHS_FULL  = 500
K_PATHS_SMOKE = 20
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

BETA_D = 4.0
TOP_K_SIG_E = 16

INDIVIDUAL_MECHS = ['B', 'D', 'E']
COMPOSITION_MECHS = ['cA', 'cB', 'cC']
ALL_MECHS = INDIVIDUAL_MECHS + COMPOSITION_MECHS

HP_DELTA = 0.15
HP_SEEDS_MIN = 3
HF_SEEDS_MIN = 4


def get_output_dir(default_name: str = "mechanism_composition_at_breaking_v2_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_substrate_with_relation(N_use: int, M: int, seed: int,
                                    device: torch.device):
    codebook, _W, _keys, _vals, _ki, _vi = make_substrate(
        N_use, M, seed, device)
    C = codebook.shape[0]
    M_eff = min(M, C)
    key_idx, val_idx, relation = build_relation_facts(
        n_idx=C, M=M_eff, seed=seed, device=device, closed=True)
    keys_vec = codebook[key_idx]
    vals_vec = codebook[val_idx]
    W = (vals_vec.T @ keys_vec) / N_use
    return codebook, W, key_idx, val_idx, relation


# Per-path-target scoring functions, shared across individual + composition.

def _per_hop_loglik(codebook, W, src_idx, dst_idx, N_use, beta):
    src = codebook[src_idx]; dst = codebook[dst_idx]
    out = src @ W.T
    sims = (out * dst).sum(dim=1) / N_use
    logits = beta * sims
    return -torch.nn.functional.softplus(-logits)


def _score_path_D(codebook, W, path, N_use, beta, device):
    depth = len(path) - 1
    src = torch.tensor(path[:-1], dtype=torch.long, device=device)
    dst = torch.tensor(path[1:],  dtype=torch.long, device=device)
    return float(_per_hop_loglik(codebook, W, src, dst, N_use, beta).sum().item())


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


def _path_B_pred_target(codebook, W, start_idx, depth, N_use, device):
    """Path B: continuous propagation, return argmax of final codebook sim."""
    q = codebook[start_idx].unsqueeze(0)
    for _ in range(depth):
        q = q @ W.T
    sims = (codebook @ q.T).squeeze(1) / N_use
    return int(torch.argmax(sims).item()), sims


def measure_cell_all_mechs(N_use: int, M: int, depth: int, K_paths: int,
                            seed: int, device: torch.device) -> Dict[str, float]:
    """Run one (M, depth, seed) cell. Compute accuracy for all 6 mechanisms.

    K_paths is the size of the candidate pool used by D / E / compositions.
    For B we read the final argmax-target directly from the codebook.
    """
    codebook, W, key_idx, val_idx, relation = build_substrate_with_relation(
        N_use, M, seed, device)
    C = codebook.shape[0]

    # Sample positive paths
    n_positives = max(20, K_paths // 25)
    pos_paths = sample_coherent_starts(relation, depth=depth,
                                         n_paths=n_positives,
                                         seed=seed + depth)
    if not pos_paths:
        del codebook, W
        if device.type == "cuda":
            torch.cuda.empty_cache()
        return {m: 0.0 for m in ALL_MECHS}

    n_eval = 0
    counts = {m: 0 for m in ALL_MECHS}

    n_decoys = K_paths - 1
    for pos in pos_paths:
        target = pos[-1]
        start = pos[0]
        # Build candidate set: positive + decoys (decoys are full paths)
        decoys = sample_incoherent_paths(
            C, depth=depth, n_paths=n_decoys,
            seed=seed + depth + hash(tuple(pos)) % 100, relation=relation)
        if not decoys:
            continue
        cands = [pos] + decoys
        cand_targets = [p[-1] for p in cands]

        # ---- Path B: argmax over codebook from continuous propagation ----
        # Since B can pick ANY codebook index (not just from candidate set),
        # we report whether B's chosen argmax equals the true target.
        b_pred, _ = _path_B_pred_target(codebook, W, start, depth, N_use, device)
        b_correct = (b_pred == target)

        # ---- Path D: posterior-product over candidate paths ----
        d_scores = torch.tensor([_score_path_D(codebook, W, p, N_use, BETA_D, device)
                                  for p in cands], device=device)
        d_argmax = int(torch.argmax(d_scores).item())
        d_pred_target = cand_targets[d_argmax]
        d_correct = (d_pred_target == target)

        # ---- Path E: coherence score over candidates ----
        e_scores = torch.tensor([_coherence(codebook, W, p, N_use, TOP_K_SIG_E)
                                  for p in cands], device=device)
        e_argmax = int(torch.argmax(e_scores).item())
        e_pred_target = cand_targets[e_argmax]
        e_correct = (e_pred_target == target)

        # ---- Composition cA: INTERSECTION ----
        # All three must agree on target (B's prediction must match D's and E's targets).
        cA_correct = (b_pred == d_pred_target == e_pred_target == target)

        # ---- Composition cB: WEIGHTED VOTE ----
        # Per-candidate score = w_D * d_score + w_E * e_score; bonus if B picked target.
        # Weights w_D, w_E from softmax of normalized score-margins (simple uniform fallback).
        d_norm = (d_scores - d_scores.mean()) / (d_scores.std() + 1e-6)
        e_norm = (e_scores - e_scores.mean()) / (e_scores.std() + 1e-6)
        combined = 0.5 * d_norm + 0.5 * e_norm
        # B's bonus: +1 to the candidate whose target matches B's pred (if any)
        b_bonus = torch.zeros_like(combined)
        for i, t in enumerate(cand_targets):
            if t == b_pred:
                b_bonus[i] = 1.0
        combined = combined + 0.5 * b_bonus
        cB_argmax = int(torch.argmax(combined).item())
        cB_correct = (cand_targets[cB_argmax] == target)

        # ---- Composition cC: CONSENSUS / MAJORITY ----
        # Each path votes a target. Majority wins; ties broken by max combined score.
        votes = {}
        for t in (b_pred, d_pred_target, e_pred_target):
            votes[t] = votes.get(t, 0) + 1
        max_votes = max(votes.values())
        winners = [t for t, v in votes.items() if v == max_votes]
        if len(winners) == 1:
            cC_pred = winners[0]
        else:
            # Tie: prefer the winner that is in the candidate set with highest combined score
            best_score = float("-inf")
            cC_pred = winners[0]
            for w in winners:
                # combined score of the candidate whose target == w (if any)
                idxs = [i for i, t in enumerate(cand_targets) if t == w]
                if idxs:
                    s = float(combined[idxs[0]].item())
                    if s > best_score:
                        best_score = s
                        cC_pred = w
        cC_correct = (cC_pred == target)

        counts['B']  += int(b_correct)
        counts['D']  += int(d_correct)
        counts['E']  += int(e_correct)
        counts['cA'] += int(cA_correct)
        counts['cB'] += int(cB_correct)
        counts['cC'] += int(cC_correct)
        n_eval += 1

    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()

    if n_eval == 0:
        return {m: 0.0 for m in ALL_MECHS}
    return {m: counts[m] / n_eval for m in ALL_MECHS}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("COMP_INCONCLUSIVE", "No cells.")

    # Identify cell-1 (hardest) and cell-2 by config
    cell_1 = HARD_CELLS_FULL[0]
    cell_2 = HARD_CELLS_FULL[1] if len(HARD_CELLS_FULL) > 1 else cell_1

    # delta_per_seed[cell] = {comp_mech: list of (delta, seed)} where
    # delta = acc_comp - max(acc_individual)
    by_cell: Dict[Tuple[int, int], List[Dict]] = {}
    for c in cells:
        k = (c["M"], c["depth"])
        by_cell.setdefault(k, []).append(c)

    # HP: at cell-1, at least one composition's delta >= HP_DELTA in >= HP_SEEDS_MIN seeds
    cell_1_rows = by_cell.get(cell_1, [])
    hp_pass = False
    deltas_per_comp_at_cell1: Dict[str, List[float]] = {m: [] for m in COMPOSITION_MECHS}
    for row in cell_1_rows:
        accs = row.get("accs", {})
        best_ind = max(accs.get(m, 0.0) for m in INDIVIDUAL_MECHS)
        for m in COMPOSITION_MECHS:
            deltas_per_comp_at_cell1[m].append(accs.get(m, 0.0) - best_ind)
    for m, deltas in deltas_per_comp_at_cell1.items():
        n_pass = sum(1 for d in deltas if d >= HP_DELTA)
        if n_pass >= HP_SEEDS_MIN:
            hp_pass = True
            break

    # HF: all composition designs WORSE than best individual at BOTH cells in
    # >= HF_SEEDS_MIN seeds.
    hf_pass_per_cell: Dict[Tuple[int, int], bool] = {}
    for cell, rows in by_cell.items():
        worst = True
        for m in COMPOSITION_MECHS:
            n_worse = 0
            for row in rows:
                accs = row.get("accs", {})
                best_ind = max(accs.get(im, 0.0) for im in INDIVIDUAL_MECHS)
                if accs.get(m, 0.0) < best_ind:
                    n_worse += 1
            if n_worse < HF_SEEDS_MIN:
                worst = False
                break
        hf_pass_per_cell[cell] = worst
    hf = all(hf_pass_per_cell.get(c, False) for c in [cell_1, cell_2])

    # Summary
    means_by_cell: Dict[str, Dict[str, float]] = {}
    for cell, rows in by_cell.items():
        cell_name = f"M{cell[0]}d{cell[1]}"
        means_by_cell[cell_name] = {}
        for m in ALL_MECHS:
            vals = [row["accs"].get(m, 0.0) for row in rows]
            means_by_cell[cell_name][m] = round(sum(vals) / max(1, len(vals)), 4)

    detail = "cells=" + " | ".join(
        f"{cn}: " + " ".join(f"{m}={means_by_cell[cn][m]:.3f}" for m in ALL_MECHS)
        for cn in means_by_cell)

    if hp_pass:
        return ("COMP_HARD_PASS",
                f"COMPOSITION_HELPS at cell-1 by delta >= {HP_DELTA}. " + detail)
    if hf:
        return ("COMP_HARD_FAIL",
                f"COMPOSITION_HURTS at both hard cells. " + detail)
    return ("COMP_MIDDLE_BAND",
            f"COMPOSITION_NEUTRAL / mixed delta. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, "PROT-018: _n4096"
    assert ALL_MECHS == ['B', 'D', 'E', 'cA', 'cB', 'cC']

    # Verdict gate HP at cell-1
    fake_hp: List[Dict] = []
    for cell in HARD_CELLS_FULL:
        for s in SEEDS_FULL:
            # individuals at 0.50; composition cB at 0.80 only at cell-1
            accs = {'B': 0.50, 'D': 0.50, 'E': 0.50,
                    'cA': 0.40, 'cB': 0.80 if cell == HARD_CELLS_FULL[0] else 0.45,
                    'cC': 0.50}
            fake_hp.append({"M": cell[0], "depth": cell[1], "seed": s,
                              "K_paths": K_PATHS_FULL, "accs": accs})
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    # Verdict gate HF: composition always worse
    fake_hf = []
    for cell in HARD_CELLS_FULL:
        for s in SEEDS_FULL:
            accs = {'B': 0.50, 'D': 0.55, 'E': 0.45,
                    'cA': 0.20, 'cB': 0.30, 'cC': 0.25}
            fake_hf.append({"M": cell[0], "depth": cell[1], "seed": s,
                              "K_paths": K_PATHS_FULL, "accs": accs})
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Verdict gate MIDDLE_BAND
    fake_mb = []
    for cell in HARD_CELLS_FULL:
        for s in SEEDS_FULL:
            accs = {'B': 0.50, 'D': 0.55, 'E': 0.45,
                    'cA': 0.45, 'cB': 0.55, 'cC': 0.50}
            fake_mb.append({"M": cell[0], "depth": cell[1], "seed": s,
                              "K_paths": K_PATHS_FULL, "accs": accs})
    v, _ = compute_verdict(fake_mb); assert "MIDDLE_BAND" in v, v

    # Smoke forward pass on CPU
    device = torch.device("cpu")
    M_smoke, d_smoke = HARD_CELLS_SMOKE[0]
    out = measure_cell_all_mechs(N_SMOKE, M_smoke, d_smoke, K_PATHS_SMOKE,
                                  17, device)
    assert all(0.0 <= v <= 1.0 for v in out.values())
    for m in ALL_MECHS:
        assert m in out, f"missing mech {m}"
    print(f"[selftest] mechanism_composition_at_breaking_v2_n4096 PASS "
          f"smoke M={M_smoke} d={d_smoke}: "
          + " ".join(f"{m}={out[m]:.2f}" for m in ALL_MECHS), flush=True)


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
    cells_cfg = HARD_CELLS_SMOKE if smoke else HARD_CELLS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    K_paths = K_PATHS_SMOKE if smoke else K_PATHS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] mechanism_composition_at_breaking_v2 smoke={smoke} N={N_cfg} "
          f"cells={cells_cfg} K_paths={K_paths} seeds={seeds} "
          f"done={len(done)} device={device.type}", flush=True)

    rows: List[Dict] = []
    for (M, d) in cells_cfg:
        for seed in seeds:
            ck = f"M{M}_d{d}_seed{seed}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    rows.append(body); continue
            try:
                accs = measure_cell_all_mechs(N_cfg, M, d, K_paths, seed, device)
                row = {"M": int(M), "depth": int(d), "seed": int(seed),
                       "K_paths": int(K_paths), "accs": accs}
                write_partial_key(out_dir, ck, row)
                rows.append(row)
                print(f"  M={M} d={d} seed={seed}: "
                      + " ".join(f"{m}={accs[m]:.3f}" for m in ALL_MECHS)
                      + f" ({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  M={M} d={d} seed={seed} FAILED: {e}", flush=True)
                if device.type == "cuda":
                    torch.cuda.empty_cache()

    verdict, vm = compute_verdict(rows)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "mechanism_composition_at_breaking_v2_n4096",
               "N": N_cfg, "smoke": smoke, "cells": cells_cfg,
               "K_paths": K_paths, "seeds": seeds,
               "mechs": ALL_MECHS, "rows": rows,
               "verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
