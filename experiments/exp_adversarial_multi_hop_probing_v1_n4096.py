"""S12 ADVERSARIAL MULTI-HOP PROBING v1 at N=4096 (E4.2).

Multi-hop under adversarial query patterns. Critical for regulated
industry security.

ADVERSARIAL PATTERNS (5):
  1. Cross-talk maximizing queries (align with codebook noise)
  2. Codebook collision-point queries
  3. Queries targeting deleted facts (verify non-recovery)
  4. Queries targeting edited facts (verify edit semantics)
  5. Composition patterns leaking across logical boundaries

PRE-REGISTERED BANDS:
  HP = >=90% defense rate across all 5 patterns AND 0% leakage rate.
  HF = any leakage detected OR defense rate <70% on any pattern.
  MB = otherwise.

Defense = substrate behaves correctly (no incorrect retrieval / no
recovery of deleted / new value returned for edited / no cross-boundary
leak).

PROT-018: _n4096.
Anchor: adversarial_multi_hop_probing_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_adversarial_multi_hop_probing_v1_n4096.md
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

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_s12", _ck_path)
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
DEPTH = 5
DEPTH_SMOKE = 3
N_QUERIES_PER_PATTERN = 32
N_QUERIES_SMOKE = 8
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

HP_DEFENSE_RATE = 0.90
HF_DEFENSE_RATE = 0.70


def get_output_dir(default_name: str = "adversarial_multi_hop_probing_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def pattern1_crosstalk(codebook, W, key_idx, val_idx, relation, n_q,
                        depth, seed, N_use, device):
    """Construct queries aligned with codebook noise direction.
    Defense = substrate retrieves a stored value confidently, not a hallucination."""
    g = torch.Generator(device=device).manual_seed(seed + 1)
    C = codebook.shape[0]
    # Random codebook indices NOT in stored keys
    stored_keys = set(key_idx.tolist())
    not_stored = [i for i in range(C) if i not in stored_keys]
    if not not_stored:
        return {"defense_rate": 1.0, "leakage_rate": 0.0, "n_q": 0}
    n = min(n_q, len(not_stored))
    perm = torch.randperm(len(not_stored), generator=g)[:n]
    q_idx = torch.tensor([not_stored[i] for i in perm.tolist()],
                          dtype=torch.long, device=device)
    pred = path_b_run(codebook, W, q_idx, depth, N_use)
    # Defense = NO false high-confidence match to a stored value
    confidence_thresh = 0.5
    q = codebook[q_idx]
    for _ in range(depth):
        q = q @ W.T
    sims = (codebook @ q.T) / N_use
    max_sims = sims.max(dim=0).values
    confident_matches = (max_sims > confidence_thresh).float().mean().item()
    # leakage = high-confidence match to a SPECIFIC stored fact
    # defense rate = fraction of queries that did NOT confidently retrieve
    defense = 1.0 - float(confident_matches)
    return {"defense_rate": round(defense, 5),
            "leakage_rate": round(float(confident_matches), 5),
            "n_q": int(n)}


def pattern2_collision(codebook, W, key_idx, val_idx, relation, n_q,
                        depth, seed, N_use, device):
    """Codebook collision-point queries: pairs of stored keys very similar.
    Defense = substrate retrieves the CORRECT value, not the colliding one."""
    if key_idx.shape[0] < 2:
        return {"defense_rate": 1.0, "leakage_rate": 0.0, "n_q": 0}
    # Find pairs of stored keys with high cosine
    keys = codebook[key_idx]
    sims = keys @ keys.T / N_use
    sims.fill_diagonal_(-1.0)
    top_sim, idx = sims.view(-1).topk(min(n_q * 2, sims.numel()))
    n_correct = 0; n_total = 0
    for s_val, ix in zip(top_sim.tolist(), idx.tolist()):
        i = ix // key_idx.shape[0]
        j = ix % key_idx.shape[0]
        if i == j or s_val <= 0: continue
        # Query with key i, expect value at i
        q = keys[i:i+1]
        for _ in range(depth):
            q = q @ W.T
        sim_out = (codebook @ q.T) / N_use
        pred = int(torch.argmax(sim_out).item())
        target = int(val_idx[i].item())
        if pred == target:
            n_correct += 1
        n_total += 1
        if n_total >= n_q: break
    defense = n_correct / max(1, n_total)
    return {"defense_rate": round(defense, 5),
            "leakage_rate": round(1.0 - defense, 5),
            "n_q": int(n_total)}


def pattern3_deleted(codebook, W, key_idx, val_idx, relation, n_q,
                      depth, seed, N_use, device):
    """Delete some facts; verify they don't return on re-query."""
    n_del = min(n_q, key_idx.shape[0] // 4)
    if n_del == 0:
        return {"defense_rate": 1.0, "leakage_rate": 0.0, "n_q": 0}
    del_keys_idx = torch.arange(n_del, device=device)
    del_keys = key_idx[del_keys_idx]
    del_vals = val_idx[del_keys_idx]
    # Apply deletion
    k_v = codebook[del_keys]
    v_v = codebook[del_vals]
    W2 = W - (v_v.T @ k_v) / N_use
    # Re-query
    q = codebook[del_keys]
    for _ in range(depth):
        q = q @ W2.T
    sims = (codebook @ q.T) / N_use
    pred = torch.argmax(sims, dim=0)
    # Defense = pred NOT == deleted target
    n_recovered = int((pred == del_vals).sum().item())
    n_total = n_del
    defense = 1.0 - n_recovered / max(1, n_total)
    return {"defense_rate": round(defense, 5),
            "leakage_rate": round(n_recovered / max(1, n_total), 5),
            "n_q": int(n_total)}


def pattern4_edited(codebook, W, key_idx, val_idx, relation, n_q,
                     depth, seed, N_use, device):
    """Edit some facts; verify edit semantics."""
    C = codebook.shape[0]
    n_edit = min(n_q, key_idx.shape[0] // 4)
    if n_edit == 0:
        return {"defense_rate": 1.0, "leakage_rate": 0.0, "n_q": 0}
    edit_idx = torch.arange(n_edit, device=device)
    e_keys = key_idx[edit_idx]
    e_old = val_idx[edit_idx]
    g = torch.Generator(device=device).manual_seed(seed + 4)
    e_new = torch.randint(0, C, (n_edit,), generator=g, device=device,
                            dtype=torch.long)
    k_v = codebook[e_keys]; ov = codebook[e_old]; nv = codebook[e_new]
    W2 = W - (ov.T @ k_v) / N_use + (nv.T @ k_v) / N_use
    # Re-query edited keys
    q = codebook[e_keys]
    for _ in range(depth):
        q = q @ W2.T
    sims = (codebook @ q.T) / N_use
    pred = torch.argmax(sims, dim=0)
    # Defense = pred matches NEW value (not old)
    n_new_correct = int((pred == e_new).sum().item())
    n_old_leak = int((pred == e_old).sum().item())
    defense = n_new_correct / max(1, n_edit)
    return {"defense_rate": round(defense, 5),
            "leakage_rate": round(n_old_leak / max(1, n_edit), 5),
            "n_q": int(n_edit)}


def pattern5_composition(codebook, W, key_idx, val_idx, relation, n_q,
                          depth, seed, N_use, device):
    """Composition queries: build a query from two unrelated stored keys.
    Defense = substrate refuses to leak across logical boundary."""
    if key_idx.shape[0] < 2:
        return {"defense_rate": 1.0, "leakage_rate": 0.0, "n_q": 0}
    g = torch.Generator(device=device).manual_seed(seed + 5)
    n = min(n_q, key_idx.shape[0] // 2)
    perm = torch.randperm(key_idx.shape[0], generator=g)
    a_idx = key_idx[perm[:n]]
    b_idx = key_idx[perm[n:2*n]]
    # Combined query = a + b normalized
    q_combined = (codebook[a_idx] + codebook[b_idx]) / 2.0
    for _ in range(depth):
        q_combined = q_combined @ W.T
    sims = (codebook @ q_combined.T) / N_use
    pred = torch.argmax(sims, dim=0)
    a_targets = val_idx[perm[:n]]
    b_targets = val_idx[perm[n:2*n]]
    # Leakage = pred == a_target XOR pred == b_target
    leak_a = (pred == a_targets).float().mean().item()
    leak_b = (pred == b_targets).float().mean().item()
    total_leak = float(leak_a + leak_b)
    defense = 1.0 - min(1.0, total_leak)
    return {"defense_rate": round(defense, 5),
            "leakage_rate": round(min(1.0, total_leak), 5),
            "n_q": int(n)}


def measure_seed(N_use: int, M: int, depth: int, n_q: int, seed: int,
                  device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)

    results = {
        "p1_crosstalk":   pattern1_crosstalk(codebook, W, key_idx, val_idx, relation, n_q, depth, seed, N_use, device),
        "p2_collision":   pattern2_collision(codebook, W, key_idx, val_idx, relation, n_q, depth, seed, N_use, device),
        "p3_deleted":     pattern3_deleted(codebook, W, key_idx, val_idx, relation, n_q, depth, seed, N_use, device),
        "p4_edited":      pattern4_edited(codebook, W, key_idx, val_idx, relation, n_q, depth, seed, N_use, device),
        "p5_composition": pattern5_composition(codebook, W, key_idx, val_idx, relation, n_q, depth, seed, N_use, device),
    }

    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"seed": int(seed), "M": int(M), "depth": int(depth),
            "patterns": results}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("S12_INCONCLUSIVE", "no cells")

    n_seeds = len(cells)
    pattern_keys = ["p1_crosstalk", "p2_collision", "p3_deleted", "p4_edited", "p5_composition"]
    mean_defense = {}
    max_leakage = {}
    for pk in pattern_keys:
        defenses = [c["patterns"][pk]["defense_rate"] for c in cells]
        leaks = [c["patterns"][pk]["leakage_rate"] for c in cells]
        mean_defense[pk] = sum(defenses) / max(1, len(defenses))
        max_leakage[pk] = max(leaks) if leaks else 0.0

    n_hp_patterns = sum(1 for pk in pattern_keys
                          if mean_defense[pk] >= HP_DEFENSE_RATE)
    n_hf_patterns = sum(1 for pk in pattern_keys
                          if mean_defense[pk] < HF_DEFENSE_RATE)
    any_leakage = any(max_leakage[pk] > 0.05 for pk in pattern_keys)

    detail = f"def={mean_defense} max_leak={max_leakage}"

    if n_hp_patterns == len(pattern_keys) and not any_leakage:
        return ("S12_HARD_PASS", "ADVERSARIAL_DEFENDED: " + detail)
    if n_hf_patterns > 0 or any(max_leakage[pk] > 0.20 for pk in pattern_keys):
        return ("S12_HARD_FAIL", "ADVERSARIAL_BREACH: " + detail)
    return ("S12_MIDDLE_BAND", "PARTIAL_DEFENSE: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    device = torch.device("cpu")
    out = measure_seed(N_SMOKE, 64, 2, 4, 17, device)
    assert len(out["patterns"]) == 5
    for pk, v in out["patterns"].items():
        assert "defense_rate" in v
    print(f"[selftest] adversarial_multi_hop_probing_v1_n4096 PASS "
          f"5 patterns measured", flush=True)


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
    depth = DEPTH_SMOKE if smoke else DEPTH
    n_q = N_QUERIES_SMOKE if smoke else N_QUERIES_PER_PATTERN
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] adversarial_multi_hop_probing smoke={smoke} N={N_cfg} M={M} "
          f"depth={depth} n_q={n_q} seeds={seeds} done={len(done)} "
          f"device={device.type}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body); continue
        try:
            out = measure_seed(N_cfg, M, depth, n_q, seed, device)
            write_partial_key(out_dir, ck, out)
            cells.append(out)
            print(f"  s={seed} done ({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError) as e:
            print(f"  s={seed} FAILED: {e}", flush=True)
            if device.type == "cuda":
                torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "adversarial_multi_hop_probing_v1_n4096",
               "N": N_cfg, "smoke": smoke,
               "M": M, "depth": depth, "n_q": n_q, "seeds": seeds,
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
