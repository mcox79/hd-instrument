"""MECHANISM COMPOSITION v1 at N=4096 (per user msg 2026-05-30).

CONTEXT (composition of B + D + E multi-hop mechanisms):
  Path B (continuous-output state propagation), Path D (Bayesian
  per-hop log-posterior product), and Path E (spectral coherence) have
  independent assumptions and DIFFERENT failure modes:
    - B fails when noise compounds in state-domain at deep depth
    - D fails when path probabilities collapse to ambiguity
    - E fails when spectral signature is dominated by codebook geometry
  HYPOTHESIS (user): "if mechanisms make DIFFERENT errors, composing them
  should give error-correction at depths/M where individual mechanisms
  struggle."

  Test in the BOUNDARY REGIME (M=2048) where individual paths may start
  degrading -- this is where composition CAN help. At low M (256) all 3
  mechanisms work and composition is trivially equivalent; at very high M
  all fail and composition can't recover.

SCIENTIFIC QUESTION:
  At N=4096, M=2048, depths {3, 4, 5}: does any of {Composition A, B, C}
  outperform the best individual mechanism at depth=5 by >= 10% in
  >= 3/5 seeds, while keeping Composition C inconclusive-rate <= 15%?

COMPOSITION DESIGNS:
  Composition A "intersection": for each query, compute top-1 candidate
    from each of B, D, E. Output only if ALL 3 top-1 picks AGREE.
    (Selective; trades coverage for precision.)
  Composition B "weighted vote": each mechanism returns top-K candidates
    with confidence weights. Aggregate weighted votes across mechanisms.
    Output argmax of total weight.
  Composition C "consensus check": if >= 2 of {B, D, E} top-1 agree,
    output that. Else mark inconclusive.

PRE-REGISTERED BANDS:
  HP = at depth=5, at least one composition design improves accuracy by
       >=10% over best individual mechanism in >=3/5 seeds AND
       Composition C inconclusive-rate <= 15%.
  HF = all 3 composition designs perform WORSE than the best individual
       mechanism at every depth (composition introduces noise).
  MIDDLE_BAND = otherwise.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. M_FULL == 2048 (boundary regime).
  3. depths = [3, 4, 5].
  4. K_candidates = 50 per query (1 coherent + 49 decoys).
  5. Each mechanism score function: B = cos(q_d, codebook[p_last]);
     D = sum log P(p[i] -> p[i+1]); E = mean cos(spec_i, spec_{i+1}).
  6. Composition A: agree iff argmax_B == argmax_D == argmax_E.
  7. Composition B: weights = softmax(scores); vote = sum across mech.
  8. Composition C: at least 2 of 3 argmaxes agree.

OOM CHECK:
  M=2048, N=4096: keys+vals = 64 MiB. W = 64 MiB. CB = 805 MiB. ~1.0 GiB.
  K_candidates=50, n_queries=40, depth<=5: 50*5*40 = 10K pair scores per
  cell, all batched. Memory negligible above substrate. OK.

TIMEOUT ESTIMATE:
  Smoke ~ 60s. FULL: 3 depths x 5 seeds x ~120s per cell = 1800s.
  scaling_exp=1.5. Budget 14400s.

N-suffix: _n4096 (PROT-018).
Anchor: mechanism_composition_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_mechanism_composition_v1_n4096.md
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_mcomp", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096
N_FULL  = N
N_SMOKE = 1024
M_FULL  = 2048
M_SMOKE = 256
DEPTHS_FULL  = [3, 4, 5]
DEPTHS_SMOKE = [3]
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
K_CANDIDATES_FULL  = 50
K_CANDIDATES_SMOKE = 16
N_QUERIES_FULL  = 40
N_QUERIES_SMOKE = 8
BETA = 4.0
TOP_K_SIG = 16

HP_IMPROVEMENT = 0.10          # >=10% absolute lift
HP_DEPTH       = 5
HP_SEEDS_MIN   = 3
HP_INCONC_MAX  = 0.15
HF_SEEDS_MIN   = 3


# ---------- mechanism scorers ----------

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
    """Mechanism B: continuous propagate q from start; score = cos(q_d, codebook[end])."""
    q = codebook[path[0]].clone()
    depth = len(path) - 1
    for _ in range(depth):
        q = q @ W.T
    target = codebook[path[-1]]
    sim = float((q @ target).item() / N_use)
    return sim


def score_path_bayesian(codebook: torch.Tensor, W: torch.Tensor,
                          path: List[int], N_use: int, beta: float) -> float:
    """Mechanism D: sum of per-hop log-sigmoid(beta * similarity)."""
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
    """Mechanism E: mean cos-sim of consecutive-hop spectral signatures."""
    depth = len(path) - 1
    if depth < 1:
        return 0.0
    src_idx = torch.tensor(path[:-1], dtype=torch.long, device=codebook.device)
    src = codebook[src_idx]
    responses = src @ W.T   # (depth, N)
    sigs = []
    for i in range(depth):
        sims = (codebook @ responses[i]) / N_use
        sig = torch.topk(sims, top_k).values
        sigs.append(sig)
    if len(sigs) < 2:
        # depth=1 -> compare to dst
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


def score_all_mechanisms(codebook: torch.Tensor, W: torch.Tensor,
                          candidates: List[List[int]], N_use: int,
                          beta: float, top_k: int
                          ) -> Tuple[List[float], List[float], List[float]]:
    """Score K candidate paths under B, D, E. Returns 3 lists of len K."""
    s_b = [score_path_continuous(codebook, W, p, N_use) for p in candidates]
    s_d = [score_path_bayesian(codebook, W, p, N_use, beta) for p in candidates]
    s_e = [score_path_spectral(codebook, W, p, N_use, top_k) for p in candidates]
    return s_b, s_d, s_e


# ---------- composition decisions ----------

def argmax_idx(scores: List[float]) -> int:
    return int(max(range(len(scores)), key=lambda i: scores[i]))


def softmax_weights(scores: List[float], temp: float = 1.0) -> List[float]:
    t = torch.tensor(scores, dtype=torch.float32)
    # Stabilize: subtract max before scaling
    t = t - t.max()
    w = torch.softmax(t / temp, dim=0)
    return w.tolist()


def decide_composition_A(s_b, s_d, s_e) -> Tuple[int, bool]:
    """Intersection: pick top-1 only if all 3 mechanisms agree.

    Returns (picked_idx, is_decision_made).
    """
    a = argmax_idx(s_b); b = argmax_idx(s_d); c = argmax_idx(s_e)
    if a == b == c:
        return (a, True)
    return (-1, False)


def decide_composition_B(s_b, s_d, s_e) -> Tuple[int, bool]:
    """Weighted vote: softmax weights summed across mechanisms; argmax."""
    K = len(s_b)
    w_b = softmax_weights(s_b)
    w_d = softmax_weights(s_d)
    w_e = softmax_weights(s_e)
    total = [w_b[i] + w_d[i] + w_e[i] for i in range(K)]
    return (argmax_idx(total), True)


def decide_composition_C(s_b, s_d, s_e) -> Tuple[int, bool]:
    """Consensus: output top-1 only if >= 2 of 3 mechanisms agree on top-1."""
    a = argmax_idx(s_b); b = argmax_idx(s_d); c = argmax_idx(s_e)
    # >= 2 agreement
    if a == b:
        return (a, True)
    if a == c:
        return (a, True)
    if b == c:
        return (b, True)
    return (-1, False)


# ---------- per-cell measurement ----------

def measure_cell(N_use: int, M: int, depth: int, K_cands: int,
                  n_queries: int, seed: int, device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_substrate_with_relation(
        N_use, M, seed, device)
    C = codebook.shape[0]

    # Sample n_queries coherent paths (positives)
    pos_paths = sample_coherent_starts(relation, depth=depth,
                                         n_paths=n_queries,
                                         seed=seed + depth)
    n_eval = len(pos_paths)
    if n_eval == 0:
        return {"depth": int(depth), "M": int(M), "seed": int(seed),
                "n_eval": 0, "acc_B": 0.0, "acc_D": 0.0, "acc_E": 0.0,
                "acc_compA": 0.0, "acc_compB": 0.0, "acc_compC": 0.0,
                "inconc_A": 1.0, "inconc_C": 1.0}

    # Per-query metrics
    n_correct_B = 0; n_correct_D = 0; n_correct_E = 0
    n_correct_compA = 0; n_correct_compB = 0; n_correct_compC = 0
    n_inconc_A = 0; n_inconc_C = 0
    n_covered_A = 0; n_covered_C = 0

    for q_idx, pos in enumerate(pos_paths):
        decoys = sample_incoherent_paths(
            C, depth=depth, n_paths=K_cands - 1,
            seed=seed + depth + (q_idx * 101) % 997, relation=relation)
        if len(decoys) < K_cands - 1:
            # Pad with random walks (already incoherent by construction)
            need = (K_cands - 1) - len(decoys)
            extra = sample_incoherent_paths(C, depth=depth, n_paths=need,
                                              seed=seed + 313 + q_idx,
                                              relation=relation)
            decoys = decoys + extra
        candidates = [pos] + decoys[:K_cands - 1]
        # By construction, the correct index in candidates is 0.

        s_b, s_d, s_e = score_all_mechanisms(
            codebook, W, candidates, N_use, BETA, TOP_K_SIG)

        # Individual mechanism top-1
        top_b = argmax_idx(s_b); top_d = argmax_idx(s_d); top_e = argmax_idx(s_e)
        if top_b == 0: n_correct_B += 1
        if top_d == 0: n_correct_D += 1
        if top_e == 0: n_correct_E += 1

        # Composition A
        pick_A, ok_A = decide_composition_A(s_b, s_d, s_e)
        if ok_A:
            n_covered_A += 1
            if pick_A == 0: n_correct_compA += 1
        else:
            n_inconc_A += 1

        # Composition B (always decides)
        pick_B, _ = decide_composition_B(s_b, s_d, s_e)
        if pick_B == 0: n_correct_compB += 1

        # Composition C
        pick_C, ok_C = decide_composition_C(s_b, s_d, s_e)
        if ok_C:
            n_covered_C += 1
            if pick_C == 0: n_correct_compC += 1
        else:
            n_inconc_C += 1

    # Accuracies (compA, compC accuracies are over the SUBSET that returned a
    # decision; "incnoc" reflects the abstention rate)
    acc_B = n_correct_B / n_eval
    acc_D = n_correct_D / n_eval
    acc_E = n_correct_E / n_eval
    acc_compA = n_correct_compA / max(1, n_covered_A)
    acc_compB = n_correct_compB / n_eval
    acc_compC = n_correct_compC / max(1, n_covered_C)
    inconc_A = n_inconc_A / n_eval
    inconc_C = n_inconc_C / n_eval

    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {"depth": int(depth), "M": int(M), "seed": int(seed),
            "n_eval": int(n_eval),
            "acc_B": round(acc_B, 5), "acc_D": round(acc_D, 5),
            "acc_E": round(acc_E, 5),
            "acc_compA": round(acc_compA, 5),
            "acc_compB": round(acc_compB, 5),
            "acc_compC": round(acc_compC, 5),
            "inconc_A": round(inconc_A, 5),
            "inconc_C": round(inconc_C, 5)}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("MCOMP_INCONCLUSIVE", "No cells.")
    # Group by depth
    by_depth: Dict[int, List[Dict]] = {}
    for c in cells:
        by_depth.setdefault(c["depth"], []).append(c)

    # HP eligibility: at depth=HP_DEPTH=5
    hp_seeds_winning = 0  # any composition >= best_indiv + HP_IMPROVEMENT
    hp_seeds_with_low_inconc = 0
    target = by_depth.get(HP_DEPTH, [])
    for c in target:
        best_indiv = max(c["acc_B"], c["acc_D"], c["acc_E"])
        best_comp = max(c["acc_compA"], c["acc_compB"], c["acc_compC"])
        if best_comp >= best_indiv + HP_IMPROVEMENT:
            hp_seeds_winning += 1
        if c["inconc_C"] <= HP_INCONC_MAX:
            hp_seeds_with_low_inconc += 1

    # HF: at every depth, ALL 3 compositions WORSE than best individual
    hf_depths_failing = 0
    for d, cs in by_depth.items():
        n_worse = 0
        for c in cs:
            best_indiv = max(c["acc_B"], c["acc_D"], c["acc_E"])
            worst_comp = max(c["acc_compA"], c["acc_compB"], c["acc_compC"])
            # If even the BEST composition is WORSE than best individual
            if worst_comp < best_indiv:
                n_worse += 1
        if n_worse >= HF_SEEDS_MIN:
            hf_depths_failing += 1

    # Means
    means_by_depth: Dict[int, Dict[str, float]] = {}
    for d, cs in by_depth.items():
        means_by_depth[d] = {
            "B": round(sum(c["acc_B"] for c in cs) / len(cs), 4),
            "D": round(sum(c["acc_D"] for c in cs) / len(cs), 4),
            "E": round(sum(c["acc_E"] for c in cs) / len(cs), 4),
            "cA": round(sum(c["acc_compA"] for c in cs) / len(cs), 4),
            "cB": round(sum(c["acc_compB"] for c in cs) / len(cs), 4),
            "cC": round(sum(c["acc_compC"] for c in cs) / len(cs), 4),
            "inconc_C": round(sum(c["inconc_C"] for c in cs) / len(cs), 4),
        }

    detail = (f"depth_means={means_by_depth} "
              f"hp_winning@d{HP_DEPTH}={hp_seeds_winning}/{len(target)} "
              f"hp_inconc_ok@d{HP_DEPTH}={hp_seeds_with_low_inconc}/{len(target)} "
              f"hf_depths_failing={hf_depths_failing}/{len(by_depth)}")

    if hf_depths_failing >= len(by_depth):
        return ("MCOMP_HARD_FAIL", "COMPOSITION_INTRODUCES_NOISE: " + detail)
    if (hp_seeds_winning >= HP_SEEDS_MIN
            and hp_seeds_with_low_inconc >= HP_SEEDS_MIN):
        return ("MCOMP_HARD_PASS", "COMPOSITION_CORRECTS_ERRORS: " + detail)
    return ("MCOMP_MIDDLE_BAND", "PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    assert M_FULL == 2048
    assert DEPTHS_FULL == [3, 4, 5]

    # Composition decision sanity
    s_b = [1.0, 0.5, 0.2]; s_d = [10.0, 5.0, 1.0]; s_e = [0.9, 0.4, 0.1]
    pick, ok = decide_composition_A(s_b, s_d, s_e)
    assert pick == 0 and ok, f"compA agree should pick 0: {pick} {ok}"
    pick, ok = decide_composition_A([1.0, 0, 0], [0, 1.0, 0], [0, 0, 1.0])
    assert not ok, f"compA disagree should be inconclusive: {pick} {ok}"
    pick, ok = decide_composition_C([1.0, 0, 0], [0, 1.0, 0], [1.0, 0, 0])
    assert pick == 0 and ok, f"compC 2-agree (B+E) should pick 0: {pick} {ok}"
    pick, ok = decide_composition_C([1.0, 0, 0], [0, 1.0, 0], [0, 0, 1.0])
    assert not ok, f"compC all-disagree should be inconclusive: {pick} {ok}"
    pick, ok = decide_composition_B([2.0, 0, 0], [2.0, 0, 0], [2.0, 0, 0])
    assert pick == 0, f"compB all-agree should pick 0: {pick}"

    # Verdict gates -- HP: at d=5 compositions beat best individual by >=10%
    fake_hp_cells = []
    for d in DEPTHS_FULL:
        for s in SEEDS_FULL:
            if d == HP_DEPTH:
                c = {"depth": d, "M": M_FULL, "seed": s, "n_eval": 40,
                     "acc_B": 0.50, "acc_D": 0.55, "acc_E": 0.45,
                     "acc_compA": 0.70, "acc_compB": 0.72, "acc_compC": 0.68,
                     "inconc_A": 0.30, "inconc_C": 0.10}
            else:
                c = {"depth": d, "M": M_FULL, "seed": s, "n_eval": 40,
                     "acc_B": 0.60, "acc_D": 0.65, "acc_E": 0.55,
                     "acc_compA": 0.65, "acc_compB": 0.68, "acc_compC": 0.65,
                     "inconc_A": 0.25, "inconc_C": 0.08}
            fake_hp_cells.append(c)
    v, _ = compute_verdict(fake_hp_cells); assert "HARD_PASS" in v, v

    # HF: all compositions strictly worse at every depth
    fake_hf_cells = []
    for d in DEPTHS_FULL:
        for s in SEEDS_FULL:
            fake_hf_cells.append({"depth": d, "M": M_FULL, "seed": s,
                                    "n_eval": 40,
                                    "acc_B": 0.60, "acc_D": 0.55, "acc_E": 0.50,
                                    "acc_compA": 0.40, "acc_compB": 0.30,
                                    "acc_compC": 0.20,
                                    "inconc_A": 0.50, "inconc_C": 0.40})
    v, _ = compute_verdict(fake_hf_cells); assert "HARD_FAIL" in v, v

    # Forward pass on CPU
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, M_SMOKE, depth=3, K_cands=8,
                       n_queries=4, seed=17, device=device)
    assert out["n_eval"] >= 0
    assert 0.0 <= out["acc_B"] <= 1.0
    assert 0.0 <= out["acc_D"] <= 1.0
    assert 0.0 <= out["acc_E"] <= 1.0
    assert 0.0 <= out["acc_compB"] <= 1.0
    print(f"[selftest] mechanism_composition_v1_n4096 PASS "
          f"smoke d=3 n_eval={out['n_eval']} "
          f"accB={out['acc_B']:.2f} accD={out['acc_D']:.2f} "
          f"accE={out['acc_E']:.2f} cA={out['acc_compA']:.2f} "
          f"cB={out['acc_compB']:.2f} cC={out['acc_compC']:.2f} "
          f"inconcA={out['inconc_A']:.2f} inconcC={out['inconc_C']:.2f}",
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
    M_cfg = M_SMOKE if smoke else M_FULL
    depths = DEPTHS_SMOKE if smoke else DEPTHS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    K_cands = K_CANDIDATES_SMOKE if smoke else K_CANDIDATES_FULL
    n_q = N_QUERIES_SMOKE if smoke else N_QUERIES_FULL

    out_dir = REPO / "data" / "exp_mechanism_composition_v1_n4096"
    out_dir.mkdir(parents=True, exist_ok=True)
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] mechanism_composition_v1 smoke={smoke} N={N_cfg} M={M_cfg} "
          f"depths={depths} K_cands={K_cands} n_queries={n_q} seeds={seeds} "
          f"done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for d in depths:
        for seed in seeds:
            ck = f"d{d}_seed{seed}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    cells.append(body); continue
            try:
                out = measure_cell(N_cfg, M_cfg, d, K_cands, n_q, seed, device)
                write_partial_key(out_dir, ck, out)
                cells.append(out)
                print(f"  d={d} seed={seed} "
                      f"B={out['acc_B']:.2f} D={out['acc_D']:.2f} "
                      f"E={out['acc_E']:.2f} | "
                      f"cA={out['acc_compA']:.2f}(inc={out['inconc_A']:.2f}) "
                      f"cB={out['acc_compB']:.2f} "
                      f"cC={out['acc_compC']:.2f}(inc={out['inconc_C']:.2f}) "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  d={d} seed={seed} FAILED: {e}", flush=True)
                if device.type == "cuda":
                    torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "mechanism_composition_v1_n4096", "N": N_cfg,
               "smoke": smoke, "M": M_cfg, "depths": depths, "seeds": seeds,
               "K_candidates": K_cands, "n_queries": n_q,
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
