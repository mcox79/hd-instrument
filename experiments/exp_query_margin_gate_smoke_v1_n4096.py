"""D1 QUERY MARGIN GATE SMOKE v1 at N=4096.

CONTEXT (v290 follow-up to U2 HARD_FAIL):
  U2 found Pattern-2 codebook-collision attacks breach the substrate at
  100% under outer-product Hopfield + Path-D depth-5 retrieval. Research
  drill notes/research_adversarial_defense_analysis_v1_2026-05-30.md
  identifies D1 (query-similarity-margin gate) as the highest-priority
  defense candidate (~1 day eng cost, P_deflated 0.55-0.70 for breach drop
  below 0.05 at small false-reject).

  D1 MECHANISM: at retrieval, compute argmax_1 and argmax_2 cosine over
  the codebook against the retrieved q'. If (cos_top1 - cos_top2) <
  delta_margin, REJECT the query as adversarial-suspect (return None /
  flag).

  Natural delta scale: 2/sqrt(N) = 0.0313 at N=4096. Sweep delta in
  {0, 0.031, 0.063, 0.125} to characterize Pareto frontier.

SCIENTIFIC QUESTION:
  At N=4096, M=2048, depth=5, does ANY delta_margin in the sweep achieve
  >=85% defense rate against pattern_2 (codebook-collision) AND <=10%
  false-positive rate on legitimate (in-distribution) queries?

PRE-REGISTERED BANDS:
  HP = at least one threshold achieves defense >= 0.85 against pattern_2
       AND false-positive <= 0.10 on legit queries (Pareto point exists).
  HF = NO threshold achieves the Pareto target across all sweep points;
       D1 mechanism is fundamentally weak.
  MB = some threshold defends partially (>= 0.50) but cannot hit Pareto
       (e.g. high defense but too-high false-positive).

LEGITIMATE QUERIES: 100 in-distribution queries are the stored keys
  themselves (key_idx[:100] from codebook), retrieved through W and
  judged against val_idx[:100]. These should pass the margin gate (legit
  retrievals are NOT codebook-collision-tied).

PROT-018: _n4096 binds N=4096.
PROT-021: per-cell-seed checkpointing.

Anchor: query_margin_gate_smoke_v1_n4096
Queue: remote_cpu_queue
Pre-reg: preregs/2026-05-31_query_margin_gate_smoke_v1_n4096.md
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

from experiments._multi_hop_mechanisms import build_shared  # noqa: E402

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_d1", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: _n4096 binds N = 4096
N = 4096
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_PROD = 2048
M_SMOKE = 256
DEPTH = 5
DEPTH_SMOKE = 3
N_QUERIES = 64
N_QUERIES_SMOKE = 16
N_LEGIT_QUERIES = 100
N_LEGIT_QUERIES_SMOKE = 32
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Margin thresholds (delta) - natural scale is k/sqrt(N) for k=0,2,4,8
DELTA_SWEEP_FULL = [0.0, 0.031, 0.063, 0.125]
DELTA_SWEEP_SMOKE = [0.0, 0.031, 0.063, 0.125]  # same: cheap, 4 small dim

# Pareto target
HP_DEFENSE_RATE = 0.85
HP_MAX_FPR = 0.10
MB_MIN_DEFENSE = 0.50


def get_output_dir(default_name: str = "query_margin_gate_smoke_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _classify_retrieve(sims: torch.Tensor, deltas: List[float]
                        ) -> Dict[float, torch.Tensor]:
    """For each delta, return mask of queries whose top-2 margin >= delta.
    sims: (C, n_q) cosine matrix. Returns dict delta -> bool mask (n_q,).
    """
    # Top-2 per query
    top2 = torch.topk(sims, k=2, dim=0)  # (2, n_q)
    cos_top1 = top2.values[0]
    cos_top2 = top2.values[1]
    margin = cos_top1 - cos_top2  # (n_q,)
    out = {}
    for d in deltas:
        out[d] = (margin >= d)  # True = ACCEPT (pass gate)
    return out


def pattern2_collision_with_gate(codebook: torch.Tensor, W: torch.Tensor,
                                   key_idx: torch.Tensor,
                                   val_idx: torch.Tensor, n_q: int,
                                   depth: int, N_use: int,
                                   deltas: List[float]) -> Dict[float, Dict]:
    """Pattern 2 attack: codebook-collision queries.
    Returns per-delta defense_rate.
    Defense = (ACCEPTED & correct) + REJECTED considered DEFENDED.
    A REJECTED query is defended (gate fired correctly).
    Leak = ACCEPTED & wrong target.
    """
    if key_idx.shape[0] < 2:
        return {d: {"defense_rate": 1.0, "leak_rate": 0.0,
                    "reject_rate": 0.0, "n_q": 0} for d in deltas}
    M_stored = key_idx.shape[0]
    keys = codebook[key_idx]
    sims_kk = keys @ keys.T / N_use
    sims_kk.fill_diagonal_(-1.0)
    # Take a larger top-k pool to ensure distinct-i candidates after dedup.
    # At BSC + Kerdock, sims_kk has many ties; without dedup all top-k pairs
    # cluster on row 0 (instrumentation pitfall observed during D1 smoke).
    pool_k = min(max(n_q * 64, n_q * 2), sims_kk.numel())
    top_sim, idx = sims_kk.view(-1).topk(pool_k)

    # Collect adversarial query indices: distinct stored-key i, paired with
    # its highest-overlap partner j.
    q_list: List[int] = []
    target_list: List[int] = []
    seen_i: set = set()
    for s_val, ix in zip(top_sim.tolist(), idx.tolist()):
        i = ix // M_stored
        j = ix % M_stored
        if i == j or s_val <= 0:
            continue
        if i in seen_i:
            continue
        seen_i.add(i)
        q_list.append(i)
        target_list.append(int(val_idx[i].item()))
        if len(q_list) >= n_q:
            break

    if not q_list:
        return {d: {"defense_rate": 1.0, "leak_rate": 0.0,
                    "reject_rate": 0.0, "n_q": 0} for d in deltas}

    q_idx_t = torch.tensor(q_list, dtype=torch.long)
    targets = torch.tensor(target_list, dtype=torch.long)
    q = keys[q_idx_t]  # (n, N)
    for _ in range(depth):
        q = q @ W.T
    # Cosine similarity against full codebook
    # Normalize for cosine (codebook has unit norm under BSC; q does not after iterations)
    sims = (codebook @ q.T) / N_use  # (C, n)
    # Apply margin gate per delta
    accept_masks = _classify_retrieve(sims, deltas)
    pred = torch.argmax(sims, dim=0)  # (n,)
    n_total = q.shape[0]

    out = {}
    for d, accept in accept_masks.items():
        n_accept = int(accept.sum().item())
        n_reject = n_total - n_accept
        # Accepted: correct if pred == target
        accepted_idx = accept.nonzero(as_tuple=True)[0]
        n_correct = int((pred[accepted_idx] == targets[accepted_idx]).sum().item())
        n_leak = n_accept - n_correct
        # Defense = rejected + accepted-correct (the substrate did NOT serve
        # the adversary's intended wrong-target).
        n_defended = n_reject + n_correct
        out[d] = {
            "defense_rate": round(n_defended / max(1, n_total), 5),
            "leak_rate": round(n_leak / max(1, n_total), 5),
            "reject_rate": round(n_reject / max(1, n_total), 5),
            "n_q": int(n_total),
        }
    return out


def legitimate_queries_with_gate(codebook: torch.Tensor, W: torch.Tensor,
                                   key_idx: torch.Tensor,
                                   val_idx: torch.Tensor,
                                   n_legit: int, depth: int, N_use: int,
                                   deltas: List[float]) -> Dict[float, Dict]:
    """Legitimate queries: use stored keys directly (in-distribution).
    Measure false-positive rate = legit query REJECTED by gate.
    """
    M = key_idx.shape[0]
    n = min(n_legit, M)
    q = codebook[key_idx[:n]]
    for _ in range(depth):
        q = q @ W.T
    sims = (codebook @ q.T) / N_use
    accept_masks = _classify_retrieve(sims, deltas)
    pred = torch.argmax(sims, dim=0)
    targets = val_idx[:n]
    n_total = n

    out = {}
    for d, accept in accept_masks.items():
        n_reject = n_total - int(accept.sum().item())
        # Recall of accepted queries: did pred==target among accepted?
        accepted_idx = accept.nonzero(as_tuple=True)[0]
        if accepted_idx.numel() > 0:
            n_correct = int((pred[accepted_idx] == targets[accepted_idx]).sum().item())
            recall_accepted = n_correct / accepted_idx.numel()
        else:
            recall_accepted = 0.0
        out[d] = {
            "fpr": round(n_reject / max(1, n_total), 5),
            "recall_accepted": round(recall_accepted, 5),
            "n_q": int(n_total),
        }
    return out


def measure_seed(N_use: int, M: int, depth: int, n_q_attack: int,
                  n_legit: int, seed: int, device: torch.device,
                  deltas: List[float]) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)
    p2 = pattern2_collision_with_gate(codebook, W, key_idx, val_idx,
                                       n_q_attack, depth, N_use, deltas)
    legit = legitimate_queries_with_gate(codebook, W, key_idx, val_idx,
                                          n_legit, depth, N_use, deltas)
    # Per-delta combined view
    per_delta = {}
    for d in deltas:
        per_delta[str(d)] = {
            "delta": d,
            "p2_defense_rate": p2[d]["defense_rate"],
            "p2_leak_rate": p2[d]["leak_rate"],
            "p2_reject_rate": p2[d]["reject_rate"],
            "p2_n": p2[d]["n_q"],
            "legit_fpr": legit[d]["fpr"],
            "legit_recall_accepted": legit[d]["recall_accepted"],
            "legit_n": legit[d]["n_q"],
        }
    del codebook, W
    return {"seed": int(seed), "M": int(M), "depth": int(depth),
            "ok": True, "per_delta": per_delta}


def compute_verdict(cells: List[Dict], deltas: List[float]) -> Tuple[str, str]:
    if not cells:
        return ("D1_INCONCLUSIVE", "no cells")
    ok = [c for c in cells if c.get("ok")]
    if not ok:
        return ("D1_INCONCLUSIVE", f"all {len(cells)} cells failed")

    # Aggregate per delta across seeds
    per_delta_agg: Dict[float, Dict[str, float]] = {}
    for d in deltas:
        defenses = [c["per_delta"][str(d)]["p2_defense_rate"] for c in ok]
        fprs = [c["per_delta"][str(d)]["legit_fpr"] for c in ok]
        per_delta_agg[d] = {
            "mean_defense": sum(defenses) / len(defenses),
            "mean_fpr": sum(fprs) / len(fprs),
        }

    detail = " | ".join(
        f"delta={d}: def={per_delta_agg[d]['mean_defense']:.3f} "
        f"fpr={per_delta_agg[d]['mean_fpr']:.3f}" for d in deltas)

    # HP: any delta hits BOTH defense >= HP_DEFENSE_RATE AND fpr <= HP_MAX_FPR
    hp_deltas = [d for d in deltas
                 if per_delta_agg[d]["mean_defense"] >= HP_DEFENSE_RATE
                 and per_delta_agg[d]["mean_fpr"] <= HP_MAX_FPR]
    if hp_deltas:
        return ("D1_HARD_PASS",
                f"PARETO_HIT delta={hp_deltas[0]}: " + detail)

    # MB: any delta with defense >= MB_MIN_DEFENSE
    mb_deltas = [d for d in deltas
                 if per_delta_agg[d]["mean_defense"] >= MB_MIN_DEFENSE]
    if mb_deltas:
        return ("D1_MIDDLE_BAND",
                f"PARTIAL_DEFENSE: " + detail)

    return ("D1_HARD_FAIL", "NO_DELTA_DEFENDS: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, "PROT-018: _n4096"
    assert len(SEEDS_FULL) == 5
    assert 0.0 in DELTA_SWEEP_FULL  # baseline (gate off) must be included

    # Verdict gate HP (delta=0.063 hits Pareto)
    fake_hp = []
    for s in SEEDS_FULL:
        per_delta = {}
        for d in DELTA_SWEEP_FULL:
            per_delta[str(d)] = {
                "delta": d,
                "p2_defense_rate": 0.0 if d == 0.0 else (
                    0.50 if d == 0.031 else (0.92 if d == 0.063 else 0.99)),
                "p2_leak_rate": 0.05,
                "p2_reject_rate": 0.20,
                "p2_n": 32,
                "legit_fpr": 0.0 if d == 0.0 else (
                    0.02 if d == 0.031 else (0.05 if d == 0.063 else 0.30)),
                "legit_recall_accepted": 0.98,
                "legit_n": 100,
            }
        fake_hp.append({"seed": s, "ok": True, "M": M_PROD, "depth": DEPTH,
                        "per_delta": per_delta})
    v, _ = compute_verdict(fake_hp, DELTA_SWEEP_FULL)
    assert "HARD_PASS" in v, f"selftest HP fail: {v}"

    # Verdict gate HF (no delta defends >50%)
    fake_hf = []
    for s in SEEDS_FULL:
        per_delta = {}
        for d in DELTA_SWEEP_FULL:
            per_delta[str(d)] = {
                "delta": d,
                "p2_defense_rate": 0.10,
                "p2_leak_rate": 0.50,
                "p2_reject_rate": 0.05,
                "p2_n": 32,
                "legit_fpr": 0.30 if d > 0 else 0.0,
                "legit_recall_accepted": 0.5,
                "legit_n": 100,
            }
        fake_hf.append({"seed": s, "ok": True, "M": M_PROD, "depth": DEPTH,
                        "per_delta": per_delta})
    v, _ = compute_verdict(fake_hf, DELTA_SWEEP_FULL)
    assert "HARD_FAIL" in v, f"selftest HF fail: {v}"

    # Verdict gate MB (defense in 50-85% range, fpr too high)
    fake_mb = []
    for s in SEEDS_FULL:
        per_delta = {}
        for d in DELTA_SWEEP_FULL:
            per_delta[str(d)] = {
                "delta": d,
                "p2_defense_rate": 0.70,
                "p2_leak_rate": 0.20,
                "p2_reject_rate": 0.10,
                "p2_n": 32,
                "legit_fpr": 0.30,  # too high
                "legit_recall_accepted": 0.7,
                "legit_n": 100,
            }
        fake_mb.append({"seed": s, "ok": True, "M": M_PROD, "depth": DEPTH,
                        "per_delta": per_delta})
    v, _ = compute_verdict(fake_mb, DELTA_SWEEP_FULL)
    assert "MIDDLE_BAND" in v, f"selftest MB fail: {v}"

    # Live smoke
    device = torch.device("cpu")
    out = measure_seed(N_SMOKE, 128, DEPTH_SMOKE, N_QUERIES_SMOKE,
                        N_LEGIT_QUERIES_SMOKE, 17, device, DELTA_SWEEP_SMOKE)
    assert out.get("ok"), f"selftest measure_seed failed"
    assert "per_delta" in out
    for d in DELTA_SWEEP_SMOKE:
        assert str(d) in out["per_delta"]
        assert "p2_defense_rate" in out["per_delta"][str(d)]
        assert "legit_fpr" in out["per_delta"][str(d)]
    print(f"[selftest] query_margin_gate_smoke_v1_n4096 PASS "
          f"d=0.063 p2_def={out['per_delta']['0.063']['p2_defense_rate']:.3f} "
          f"fpr={out['per_delta']['0.063']['legit_fpr']:.3f}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    device = torch.device("cpu")  # D1 is a CPU smoke
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    M = M_SMOKE if smoke else M_PROD
    depth = DEPTH_SMOKE if smoke else DEPTH
    n_q_attack = N_QUERIES_SMOKE if smoke else N_QUERIES
    n_legit = N_LEGIT_QUERIES_SMOKE if smoke else N_LEGIT_QUERIES
    deltas = DELTA_SWEEP_SMOKE if smoke else DELTA_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] query_margin_gate_smoke_v1_n4096 smoke={smoke} N={N_cfg} "
          f"M={M} depth={depth} n_q_attack={n_q_attack} n_legit={n_legit} "
          f"deltas={deltas} seeds={seeds} done={len(done)} device={device.type}",
          flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body); continue
        try:
            cell = measure_seed(N_cfg, M, depth, n_q_attack, n_legit,
                                  seed, device, deltas)
            write_partial_key(out_dir, ck, cell)
            cells.append(cell)
            # Best Pareto point for this seed
            best_d = max(deltas, key=lambda d:
                          cell["per_delta"][str(d)]["p2_defense_rate"]
                          if cell["per_delta"][str(d)]["legit_fpr"] <= 0.10
                          else -1.0)
            best = cell["per_delta"][str(best_d)]
            print(f"  seed={seed} best_d={best_d} def={best['p2_defense_rate']:.3f} "
                  f"fpr={best['legit_fpr']:.3f} ({time.time()-t0:.1f}s)",
                  flush=True)
        except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
            print(f"  seed={seed} FAILED: {e}", flush=True)

    verdict, vm = compute_verdict(cells, deltas)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "query_margin_gate_smoke_v1_n4096",
               "N": N_cfg, "smoke": smoke, "M": M, "depth": depth,
               "deltas": deltas, "seeds": seeds, "cells": cells,
               "verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
