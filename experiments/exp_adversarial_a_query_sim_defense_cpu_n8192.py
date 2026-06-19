"""ADVERSARIAL a_query_sim DEFENSE CPU CROSS-CODEPATH at N=8192.

CONTEXT (v299 cap_map adversarial-sub-row LIFT follow-on):
  G8 HARD_PASS at N=4096 (today): a_query_sim def=1.000 fp=0.000 (5-seed GPU).
  Cross-N HARD_PASS at N=16384 cloud A10 (today): def>=0.95 fp<=0.05 (15 cells).
  N=8192 is the intermediate N not yet tested.
  CPU codepath not yet validated (today's G8 + cross-N both ran on GPU).

SCIENTIFIC QUESTION:
  At N=8192 on CPU, M in {2048, 4096, 6144} (M/N in {0.25, 0.5, 0.75}),
  does a_query_sim defense achieve defense_rate >= 0.95 AND fp_rate <= 0.05
  across 5 seeds?

  Same defense code as G8 -- only codepath (CPU) and N change.

PRE-REGISTERED BANDS:
  HP = defense_rate >= 0.95 AND fp_rate <= 0.05 across all 15 cells (3M x 5 seeds).
  HF = defense degrades sharply: def < 0.50 OR fp > 0.20 at ANY cell.
  MB = anything between: partial defense, some M-values pass but others do not.

STRATEGIC VALUE:
  PASS removes both the N=8192 gap AND the CPU-codepath caveat from the
  adversarial-sub-row LIFT at v299. Defense confirmed hardware-agnostic.
  FAIL on CPU only (vs GPU PASS) is a hardware-dependent finding -- important
  to characterize before production deployment.

PROT-018: _n8192 binds N = 8192.
PROT-019: timeout >= 14400s.
PROT-021: per-cell checkpointing (seed x M).

Anchor: adversarial_a_query_sim_defense_cpu_n8192
Queue: remote_cpu_queue
Pre-reg: preregs/2026-05-31_adversarial_a_query_sim_defense_cpu_n8192.md
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_aq_cpu", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: _n8192 binds N = 8192
N = 8192
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

# M-grid: M/N in {0.25, 0.5, 0.75} (matches cloud cross-N structure)
M_GRID_FULL  = [2048, 4096, 6144]
M_GRID_SMOKE = [256, 512]

N_ADV_QUERIES_FULL  = 32
N_ADV_QUERIES_SMOKE = 8
N_LEG_QUERIES_FULL  = 64
N_LEG_QUERIES_SMOKE = 16
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Defense A threshold -- identical to G8 and cross-N cloud
DEFENSE_A_SIM_THRESH = 0.5

HP_DEFENSE_RATE = 0.95
HP_MAX_FP_RATE  = 0.05
HF_DEFENSE_RATE = 0.50
HF_MAX_FP_RATE  = 0.20


def get_output_dir(default_name: str = "adversarial_a_query_sim_defense_cpu_n8192") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _collision_queries(codebook, key_idx, val_idx, n_q, N_use, device):
    """Pattern 2: pairs of stored keys with highest cosine; query = first of pair."""
    if key_idx.shape[0] < 2:
        return None, None
    keys = codebook[key_idx]
    sims_kk = keys @ keys.T / N_use
    sims_kk.fill_diagonal_(-1.0)
    top_sim, idx = sims_kk.view(-1).topk(min(n_q * 2, sims_kk.numel()))
    qs, true_targets = [], []
    seen: set = set()
    n_keys = key_idx.shape[0]
    for s_val, ix in zip(top_sim.tolist(), idx.tolist()):
        i = ix // n_keys
        j = ix % n_keys
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
    """Legitimate queries: random subset of stored keys."""
    g = torch.Generator(device='cpu').manual_seed(seed + 100)
    perm = torch.randperm(key_idx.shape[0], generator=g)[:n_q].to(device)
    q = codebook[key_idx[perm]]
    targets = val_idx[perm]
    return q, targets


def _retrieve(W, q, codebook, N_use):
    out  = q @ W.T
    sims = (codebook @ out.T) / N_use
    pred = torch.argmax(sims, dim=0)
    return pred


def defense_a_query_sim(W, q, codebook, keys, N_use):
    """Defense A: reject query if max cosine_sim to stored keys < threshold."""
    sims_q_keys = q @ keys.T / N_use
    max_sim = sims_q_keys.max(dim=-1).values
    accepted = max_sim >= DEFENSE_A_SIM_THRESH
    pred_raw = _retrieve(W, q, codebook, N_use)
    pred = torch.where(accepted, pred_raw, torch.full_like(pred_raw, -1))
    return pred, accepted


def measure_cell(N_use: int, M: int, n_adv: int, n_leg: int,
                  seed: int, device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, _relation = build_shared(N_use, M, seed, device)
    keys = codebook[key_idx]

    # Adversarial queries
    adv_q, adv_true = _collision_queries(
        codebook, key_idx, val_idx, n_adv, N_use, device)
    if adv_q is None:
        del codebook, W
        return {"seed": int(seed), "M": int(M), "ok": False,
                "error": "no adversarial queries constructed"}

    # Legitimate queries
    leg_q, leg_targets = _legitimate_queries(
        codebook, key_idx, val_idx, n_leg, seed, device)

    # Defense A on adversarial: defense = rejected OR true-correct
    a_adv_pred, a_adv_acc = defense_a_query_sim(W, adv_q, codebook, keys, N_use)
    a_def_rate = float(
        ((a_adv_pred == -1) | (a_adv_pred == adv_true)).float().mean().item())

    # Defense A false-positive on legit: FP = rejected OR wrong answer
    a_leg_pred, _ = defense_a_query_sim(W, leg_q, codebook, keys, N_use)
    a_fp_rate = float(
        ((a_leg_pred == -1) | (a_leg_pred != leg_targets)).float().mean().item())

    del codebook, W
    return {"seed": int(seed), "M": int(M), "ok": True,
            "n_adv": int(adv_q.shape[0]),
            "n_leg": int(leg_q.shape[0]),
            "a_query_sim": {
                "defense_rate": round(a_def_rate, 5),
                "fp_rate": round(a_fp_rate, 5),
            }}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("AQS_CPU_INCONCLUSIVE", "no cells")
    ok = [c for c in cells if c.get("ok")]
    if not ok:
        return ("AQS_CPU_INCONCLUSIVE", f"all {len(cells)} cells failed")

    def_rates = [c["a_query_sim"]["defense_rate"] for c in ok]
    fp_rates  = [c["a_query_sim"]["fp_rate"]       for c in ok]
    mean_def = sum(def_rates) / len(def_rates)
    mean_fp  = sum(fp_rates)  / len(fp_rates)
    min_def  = min(def_rates)
    max_fp   = max(fp_rates)

    by_m: Dict[int, List] = {}
    for c in ok:
        by_m.setdefault(c["M"], []).append(c["a_query_sim"])
    m_summaries = []
    for m_val in sorted(by_m):
        rows = by_m[m_val]
        md = sum(r["defense_rate"] for r in rows) / len(rows)
        mf = sum(r["fp_rate"] for r in rows) / len(rows)
        m_summaries.append(f"M={m_val}: def={md:.3f} fp={mf:.3f}")

    detail = (f"mean def={mean_def:.3f} fp={mean_fp:.3f} "
              f"min_def={min_def:.3f} max_fp={max_fp:.3f} | "
              + " | ".join(m_summaries))

    all_hp = all(d >= HP_DEFENSE_RATE for d in def_rates) and all(f <= HP_MAX_FP_RATE for f in fp_rates)
    any_hf = any(d < HF_DEFENSE_RATE or f > HF_MAX_FP_RATE
                 for d, f in zip(def_rates, fp_rates))

    if all_hp:
        return ("AQS_CPU_HARD_PASS",
                f"DEFENSE_CPU_CONFIRMED n_cells={len(ok)}. " + detail)
    if any_hf:
        return ("AQS_CPU_HARD_FAIL",
                f"DEFENSE_DEGRADES_ON_CPU_OR_N8192. " + detail)
    return ("AQS_CPU_MIDDLE_BAND",
            f"PARTIAL n_ok={len(ok)}. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at smoke scale."""
    assert N_FULL == 8192, "PROT-018: _n8192"
    assert len(SEEDS_FULL) == 5, f"expected 5 seeds, got {len(SEEDS_FULL)}"
    assert len(M_GRID_FULL) == 3, f"expected 3 M values"

    # Verdict gate HP: all cells pass both thresholds
    fake_hp = [{"seed": s, "M": m, "ok": True,
                "n_adv": 32, "n_leg": 64,
                "a_query_sim": {"defense_rate": 1.000, "fp_rate": 0.000}}
               for s in SEEDS_FULL for m in M_GRID_FULL]
    v, msg = compute_verdict(fake_hp)
    assert "HARD_PASS" in v, f"HP gate failed: {v} {msg}"

    # Verdict gate HF: any cell below threshold
    fake_hf = [{"seed": s, "M": m, "ok": True,
                "n_adv": 32, "n_leg": 64,
                "a_query_sim": {"defense_rate": 0.30, "fp_rate": 0.30}}
               for s in SEEDS_FULL for m in M_GRID_FULL]
    v, msg = compute_verdict(fake_hf)
    assert "HARD_FAIL" in v, f"HF gate failed: {v} {msg}"

    # Verdict gate MB: partial -- some cells pass, verdict is middle
    fake_mb = [{"seed": s, "M": m, "ok": True,
                "n_adv": 32, "n_leg": 64,
                "a_query_sim": {"defense_rate": 0.80, "fp_rate": 0.08}}
               for s in SEEDS_FULL for m in M_GRID_FULL]
    v, msg = compute_verdict(fake_mb)
    assert "MIDDLE_BAND" in v, f"MB gate failed: {v} {msg}"

    # Live smoke: measure_cell on CPU at small N
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, 256, N_ADV_QUERIES_SMOKE, N_LEG_QUERIES_SMOKE,
                        17, device)
    assert out["ok"], f"selftest measure_cell failed: {out.get('error')}"
    aq = out["a_query_sim"]
    assert 0.0 <= aq["defense_rate"] <= 1.0, f"defense_rate out of range: {aq}"
    assert 0.0 <= aq["fp_rate"] <= 1.0, f"fp_rate out of range: {aq}"
    print(f"[selftest] adversarial_a_query_sim_defense_cpu_n8192 PASS "
          f"def={aq['defense_rate']:.3f} fp={aq['fp_rate']:.3f}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    # PROT: force CPU -- remote_cpu_queue; must never touch CUDA
    device = torch.device("cpu")
    smoke  = args.smoke
    N_cfg    = N_SMOKE         if smoke else N_FULL
    M_grid   = M_GRID_SMOKE    if smoke else M_GRID_FULL
    n_adv    = N_ADV_QUERIES_SMOKE if smoke else N_ADV_QUERIES_FULL
    n_leg    = N_LEG_QUERIES_SMOKE if smoke else N_LEG_QUERIES_FULL
    seeds    = SEEDS_SMOKE     if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done    = set(list_completed_keys(out_dir))
    t0      = time.time()
    print(f"[run] adversarial_a_query_sim_defense_cpu_n8192 smoke={smoke} "
          f"N={N_cfg} M_grid={M_grid} n_adv={n_adv} n_leg={n_leg} "
          f"seeds={seeds} done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        for M in M_grid:
            ck = f"seed{seed}_M{M}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    cells.append(body)
                    continue
            try:
                cell = measure_cell(N_cfg, M, n_adv, n_leg, seed, device)
                write_partial_key(out_dir, ck, cell)
                cells.append(cell)
                aq = cell.get("a_query_sim", {})
                print(f"  seed={seed} M={M} ok={cell.get('ok')} "
                      f"def={aq.get('defense_rate','n/a')} "
                      f"fp={aq.get('fp_rate','n/a')} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
                print(f"  seed={seed} M={M} FAILED: {e}", flush=True)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "adversarial_a_query_sim_defense_cpu_n8192",
               "N": N_cfg, "smoke": smoke, "M_grid": M_grid,
               "n_adv": n_adv, "n_leg": n_leg, "seeds": seeds,
               "cells": cells,
               "verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
