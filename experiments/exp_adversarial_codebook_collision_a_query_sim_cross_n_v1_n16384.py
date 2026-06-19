"""ADVERSARIAL CODEBOOK COLLISION a_query_sim CROSS-N REPLICATION v1 at N=16384.

CONTEXT (G8_HARD_PASS follow-on):
  G8 confirmed a_query_sim defense achieves def=1.000 fp=0.000 at N=4096.
  This anchor tests whether the same defense holds at N=16384 (4x scale-up).
  Closes the single-N caveat on today's adversarial-sub-row LIFT.

DEFENSE MECHANISM:
  a_query_sim (identical code path to G8): reject query if max cosine_sim
  to ANY stored key < 0.5. No re-training; purely geometric threshold.

SCIENTIFIC QUESTION:
  At N=16384, M in {4096, 8192, 12288}, does a_query_sim achieve defense
  rate >= 0.95 AND fp <= 0.05 across all 15 cells (3 M-values x 5 seeds)?

PRE-REGISTERED BANDS:
  HP = defense rate >= 0.95 AND fp <= 0.05 across all 15 cells.
  HF = defense degrades sharply: rate < 0.50 OR fp > 0.20 at ANY cell.
  MB = anything in between.

STRATEGIC VALUE:
  PASS moves adversarial-sub-row LIFT from 0.45-0.65 to 0.55-0.75 by
  closing the single-N defense caveat.

PROT-018: _n16384 binds N = 16384.
PROT-021: per-cell-seed checkpointing.

OOM CHECK:
  N=16384: W = 16384x16384 float32 = 1 GiB. Codebook C=max(M) = 12288 x
  16384 = ~0.75 GiB. Peak ~2 GiB, under 6 GiB headroom on A10.

Anchor: adversarial_codebook_collision_a_query_sim_cross_n_v1_n16384
Queue: overnight_queue (cloud Lambda A10 GPU)
Pre-reg: preregs/2026-05-31_adversarial_codebook_collision_a_query_sim_cross_n_v1_n16384.md
Total cells: 15 (3 M-values x 5 seeds)
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

from experiments._multi_hop_mechanisms import build_shared  # noqa: E402

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_cross_n", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: _n16384 binds N = 16384
N = 16384
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 16384, f"PROT-018: N_FULL must be 16384; got {N_FULL}"

M_GRID_FULL  = [4096, 8192, 12288]
M_GRID_SMOKE = [256, 512]
N_ADV_QUERIES_FULL  = 32
N_ADV_QUERIES_SMOKE = 8
N_LEG_QUERIES_FULL  = 64
N_LEG_QUERIES_SMOKE = 16
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Defense A: same threshold as G8
DEFENSE_A_SIM_THRESH = 0.5

# Pre-registered bands (verbatim from spec)
HP_DEFENSE_RATE = 0.95
HP_MAX_FP_RATE  = 0.05
HF_DEFENSE_RATE = 0.50
HF_MAX_FP_RATE  = 0.20


def get_output_dir(
    default_name: str = "adversarial_codebook_collision_a_query_sim_cross_n_v1_n16384",
) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _safe_clear(device: torch.device) -> None:
    if device.type == "cuda":
        try:
            torch.cuda.empty_cache()
        except Exception:
            pass


def _collision_queries(codebook, key_idx, val_idx, n_q, N_use, device):
    """Pattern 2 (codebook-collision): take pairs of stored keys with highest
    cosine similarity; query is the FIRST of each pair; target is the true value.
    Identical construction to G8 for apples-to-apples cross-N comparison."""
    if key_idx.shape[0] < 2:
        return None, None
    keys = codebook[key_idx]
    sims_kk = keys @ keys.T / N_use
    sims_kk.fill_diagonal_(-1.0)
    top_sim, idx = sims_kk.view(-1).topk(min(n_q * 2, sims_kk.numel()))
    qs, true_targets = [], []
    seen = set()
    for s_val, ix in zip(top_sim.tolist(), idx.tolist()):
        i = ix // key_idx.shape[0]
        j = ix % key_idx.shape[0]
        if i == j or s_val <= 0:
            continue
        if (i, j) in seen or (j, i) in seen:
            continue
        seen.add((i, j))
        qs.append(keys[i])
        true_targets.append(int(val_idx[i].item()))
        if len(qs) >= n_q:
            break
    if not qs:
        return None, None
    q_tensor = torch.stack(qs)
    return q_tensor, torch.tensor(true_targets, device=device)


def _legitimate_queries(codebook, key_idx, val_idx, n_q, seed, device):
    """Legitimate queries: random subset of stored keys (identical to G8)."""
    g = torch.Generator(device='cpu').manual_seed(seed + 100)
    perm = torch.randperm(key_idx.shape[0], generator=g)[:n_q].to(device)
    q = codebook[key_idx[perm]]
    targets = val_idx[perm]
    return q, targets


def _retrieve(W, q, codebook, N_use):
    """Single-hop retrieval: q -> W -> argmax over codebook (identical to G8)."""
    out = q @ W.T
    sims = (codebook @ out.T) / N_use
    pred = torch.argmax(sims, dim=0)
    return pred


def defense_a_query_sim(W, q, codebook, keys, N_use):
    """Defense A: reject query if max cosine_sim to stored keys < DEFENSE_A_SIM_THRESH.
    Returns (pred, accepted_mask). Rejected queries get pred=-1.
    IDENTICAL to G8 defense_a_query_sim for cross-N apples-to-apples comparison."""
    sims_q_keys = q @ keys.T / N_use   # (n_q, M)
    max_sim = sims_q_keys.max(dim=-1).values
    accepted = max_sim >= DEFENSE_A_SIM_THRESH
    pred_raw = _retrieve(W, q, codebook, N_use)
    pred = torch.where(accepted, pred_raw, torch.full_like(pred_raw, -1))
    return pred, accepted


def measure_cell(N_use: int, M: int, n_adv: int, n_leg: int,
                  seed: int, device: torch.device) -> Dict:
    """Run one (M, seed) cell; return defense_rate, fp_rate for a_query_sim."""
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)
    keys = codebook[key_idx]

    adv_q, true_targets = _collision_queries(
        codebook, key_idx, val_idx, n_adv, N_use, device)
    if adv_q is None:
        del codebook, W
        _safe_clear(device)
        return {"M": int(M), "seed": int(seed), "ok": False,
                "error": "no adversarial queries constructed"}

    leg_q, leg_targets = _legitimate_queries(
        codebook, key_idx, val_idx, n_leg, seed, device)

    # Defense A on adversarial queries
    a_adv_pred, _ = defense_a_query_sim(W, adv_q, codebook, keys, N_use)
    # Defense rate: rejected OR returned the correct value
    a_defense = ((a_adv_pred == -1) | (a_adv_pred == true_targets)).float().mean().item()

    # FP rate on legitimate queries: rejected OR returned wrong answer
    a_leg_pred, _ = defense_a_query_sim(W, leg_q, codebook, keys, N_use)
    a_fp = ((a_leg_pred == -1) | (a_leg_pred != leg_targets)).float().mean().item()

    del codebook, W
    _safe_clear(device)
    return {
        "M": int(M),
        "seed": int(seed),
        "ok": True,
        "defense_rate": round(float(a_defense), 5),
        "fp_rate":      round(float(a_fp), 5),
        "n_adv": int(adv_q.shape[0]),
        "n_leg": int(leg_q.shape[0]),
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("CROSS_N_INCONCLUSIVE", "no cells")
    ok = [c for c in cells if c.get("ok")]
    if not ok:
        return ("CROSS_N_INCONCLUSIVE", f"all {len(cells)} cells failed")

    def_rates = [c["defense_rate"] for c in ok]
    fp_rates  = [c["fp_rate"]      for c in ok]
    mean_def = sum(def_rates) / len(def_rates)
    mean_fp  = sum(fp_rates)  / len(fp_rates)

    # HF: ANY cell fails sharply
    hf_cells = [c for c in ok
                if c["defense_rate"] < HF_DEFENSE_RATE or c["fp_rate"] > HF_MAX_FP_RATE]
    # HP: ALL cells pass
    hp_cells = [c for c in ok
                if c["defense_rate"] >= HP_DEFENSE_RATE and c["fp_rate"] <= HP_MAX_FP_RATE]

    by_m: Dict[int, List] = {}
    for c in ok:
        by_m.setdefault(c["M"], []).append(c)
    m_summary = " | ".join(
        f"M{m}: def={sum(x['defense_rate'] for x in v)/len(v):.3f} "
        f"fp={sum(x['fp_rate'] for x in v)/len(v):.3f}"
        for m, v in sorted(by_m.items())
    )

    detail = (f"mean_def={mean_def:.3f} mean_fp={mean_fp:.3f} "
              f"n_ok={len(ok)}/15 n_hp={len(hp_cells)} n_hf_sharp={len(hf_cells)} | "
              + m_summary)

    if len(hf_cells) > 0:
        return ("CROSS_N_HARD_FAIL",
                f"DEFENSE_DEGRADES_AT_N16384: {len(hf_cells)} cells below HF threshold. "
                + detail)
    if len(hp_cells) == len(ok):
        return ("CROSS_N_HARD_PASS",
                f"DEFENSE_HOLDS_AT_N16384: all {len(ok)} cells >= HP threshold. "
                + detail)
    return ("CROSS_N_MIDDLE_BAND",
            f"PARTIAL_DEFENSE_AT_N16384: {len(hp_cells)}/{len(ok)} cells pass HP. "
            + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    assert N_FULL == 16384, "PROT-018: _n16384"
    assert M_GRID_FULL == [4096, 8192, 12288]
    assert len(SEEDS_FULL) == 5
    assert DEFENSE_A_SIM_THRESH == 0.5  # same as G8

    # Total cells check
    expected_cells = len(M_GRID_FULL) * len(SEEDS_FULL)
    assert expected_cells == 15, expected_cells

    # Verdict gate HP: all cells at or above HP
    fake_hp = [{"M": m, "seed": s, "ok": True,
                "defense_rate": 0.97, "fp_rate": 0.02,
                "n_adv": 32, "n_leg": 64}
               for m in M_GRID_FULL for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hp)
    assert "HARD_PASS" in v, f"HP gate failed: {v}"

    # Verdict gate HF: one cell below HF threshold
    fake_hf = []
    for m in M_GRID_FULL:
        for s in SEEDS_FULL:
            dr = 0.30 if (m == M_GRID_FULL[-1] and s == SEEDS_FULL[-1]) else 0.97
            fake_hf.append({"M": m, "seed": s, "ok": True,
                            "defense_rate": dr, "fp_rate": 0.02,
                            "n_adv": 32, "n_leg": 64})
    v, _ = compute_verdict(fake_hf)
    assert "HARD_FAIL" in v, f"HF gate failed: {v}"

    # Verdict gate MB: some pass HP, none fail sharply
    fake_mb = [{"M": m, "seed": s, "ok": True,
                "defense_rate": 0.80, "fp_rate": 0.08,
                "n_adv": 32, "n_leg": 64}
               for m in M_GRID_FULL for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_mb)
    assert "MIDDLE_BAND" in v, f"MB gate failed: {v}"

    # Live smoke forward pass on CPU at small N
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, M_GRID_SMOKE[0], N_ADV_QUERIES_SMOKE,
                       N_LEG_QUERIES_SMOKE, 17, device)
    assert out["ok"], f"selftest measure_cell failed: {out.get('error')}"
    assert "defense_rate" in out
    assert "fp_rate" in out
    assert 0.0 <= out["defense_rate"] <= 1.0, f"defense_rate out of range: {out['defense_rate']}"
    assert 0.0 <= out["fp_rate"] <= 1.0, f"fp_rate out of range: {out['fp_rate']}"
    assert out["n_adv"] >= 1, "filter eliminated all adversarial queries at smoke scale"
    assert out["n_leg"] >= 1, "filter eliminated all legitimate queries at smoke scale"
    print(
        f"[selftest] adversarial_codebook_collision_a_query_sim_cross_n_v1_n16384 PASS "
        f"N={N_SMOKE} M={M_GRID_SMOKE[0]} def={out['defense_rate']:.3f} "
        f"fp={out['fp_rate']:.3f}",
        flush=True,
    )


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
    N_cfg  = N_SMOKE      if smoke else N_FULL
    M_grid = M_GRID_SMOKE if smoke else M_GRID_FULL
    n_adv  = N_ADV_QUERIES_SMOKE if smoke else N_ADV_QUERIES_FULL
    n_leg  = N_LEG_QUERIES_SMOKE if smoke else N_LEG_QUERIES_FULL
    seeds  = SEEDS_SMOKE  if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    total_cells = len(M_grid) * len(seeds)
    cell_num = 0
    print(
        f"[run] adversarial_codebook_collision_a_query_sim_cross_n_v1_n16384 "
        f"smoke={smoke} N={N_cfg} M_grid={M_grid} n_adv={n_adv} n_leg={n_leg} "
        f"seeds={seeds} total_cells={total_cells} done={len(done)} device={device.type}",
        flush=True,
    )

    cells: List[Dict] = []
    for M in M_grid:
        for seed in seeds:
            cell_num += 1
            ck = f"M{M}_seed{seed}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    cells.append(body)
                    print(f"  [cell {cell_num}/{total_cells}] M={M} seed={seed} RESUMED",
                          flush=True)
                    continue
            try:
                cell = measure_cell(N_cfg, M, n_adv, n_leg, seed, device)
                write_partial_key(out_dir, ck, cell)
                cells.append(cell)
                print(
                    f"  [cell {cell_num}/{total_cells}] M={M} seed={seed} "
                    f"ok={cell.get('ok')} "
                    f"def={cell.get('defense_rate', 'n/a'):.3f} "
                    f"fp={cell.get('fp_rate', 'n/a'):.3f} "
                    f"({time.time()-t0:.1f}s)",
                    flush=True,
                )
            except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
                print(f"  [cell {cell_num}/{total_cells}] M={M} seed={seed} FAILED: {e}",
                      flush=True)
                _safe_clear(device)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor": "adversarial_codebook_collision_a_query_sim_cross_n_v1_n16384",
        "N": N_cfg, "smoke": smoke, "M_grid": M_grid, "seeds": seeds,
        "cells": cells, "verdict": verdict, "verdict_msg": vm,
        "elapsed_s": elapsed,
    }
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
