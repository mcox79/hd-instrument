"""G8 ADVERSARIAL CODEBOOK COLLISION DEFENSE PROBE v1 at N=4096.

CONTEXT (v290 cap_map follow-on):
  U2 adversarial probing found pattern_2 (codebook-collision) achieved
  defense=0.000 with 100% breach. G8 tests 2 simple defense mechanisms
  against the same attack pattern.

DEFENSE A "query-similarity-threshold":
  reject queries with cosine_sim < 0.5 to ANY stored key. Heuristic; may
  have false positives on legitimate queries that happen to fall in the
  threshold neighborhood.

DEFENSE B "codebook-distance-check":
  for retrieved candidate, verify its codebook-distance to the query is
  below a learned threshold; if above threshold, return null (refuse).

SCIENTIFIC QUESTION:
  At N=4096, M=2048, BSC, does at least one defense achieve >=85% defense
  rate against pattern_2 AND false_positive_rate <=10% on legitimate
  queries?

PRE-REGISTERED BANDS:
  HP = at least one defense has defense_rate >=0.85 AND fp_rate <=0.10.
  HF = both defenses fail (defense_rate <0.50 OR fp_rate >0.25).
  MB = otherwise.

NOTE: smoke probe; successful candidates routed to engineering.

PROT-018: _n4096 binds N = 4096.
PROT-020: torch + cuda available.
PROT-021: per-cell-seed checkpointing.

Anchor: adversarial_codebook_collision_defense_probe_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_adversarial_codebook_collision_defense_probe_v1_n4096.md
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_g8", _ck_path)
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
N_ADV_QUERIES_FULL = 32
N_ADV_QUERIES_SMOKE = 8
N_LEG_QUERIES_FULL = 64
N_LEG_QUERIES_SMOKE = 16
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

DEFENSE_A_SIM_THRESH = 0.5  # query rejected if max-sim to any stored key < 0.5
DEFENSE_B_DIST_THRESH = 0.4  # retrieved cand rejected if cos(q, cand) < 0.4

HP_DEFENSE_RATE = 0.85
HP_MAX_FP_RATE = 0.10
HF_DEFENSE_RATE = 0.50
HF_MAX_FP_RATE = 0.25


def get_output_dir(default_name: str = "adversarial_codebook_collision_defense_probe_v1_n4096") -> Path:
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
    """Pattern 2: take pairs of stored keys with highest cosine; queries are
    the FIRST of each pair, target is OTHER key's value (collision target)."""
    if key_idx.shape[0] < 2:
        return None, None
    keys = codebook[key_idx]
    sims_kk = keys @ keys.T / N_use
    sims_kk.fill_diagonal_(-1.0)
    top_sim, idx = sims_kk.view(-1).topk(min(n_q * 2, sims_kk.numel()))
    qs, true_targets, collision_targets = [], [], []
    seen = set()
    for s_val, ix in zip(top_sim.tolist(), idx.tolist()):
        i = ix // key_idx.shape[0]
        j = ix % key_idx.shape[0]
        if i == j or s_val <= 0: continue
        if (i, j) in seen or (j, i) in seen: continue
        seen.add((i, j))
        qs.append(keys[i])
        true_targets.append(int(val_idx[i].item()))
        collision_targets.append(int(val_idx[j].item()))
        if len(qs) >= n_q: break
    if not qs:
        return None, None
    q_tensor = torch.stack(qs)
    return q_tensor, {"true": torch.tensor(true_targets, device=device),
                       "collision": torch.tensor(collision_targets, device=device)}


def _legitimate_queries(codebook, key_idx, val_idx, n_q, seed, device):
    """Legitimate queries: random subset of stored keys."""
    g = torch.Generator(device='cpu').manual_seed(seed + 100)
    perm = torch.randperm(key_idx.shape[0], generator=g)[:n_q].to(device)
    q = codebook[key_idx[perm]]
    targets = val_idx[perm]
    return q, targets


def _retrieve(W, q, codebook, N_use):
    """Single-hop retrieval: q -> W -> argmax over codebook."""
    out = q @ W.T
    sims = (codebook @ out.T) / N_use  # (C, n_q)
    pred = torch.argmax(sims, dim=0)
    max_sims = sims.max(dim=0).values
    return pred, max_sims


def defense_a_query_sim(W, q, codebook, keys, N_use):
    """Defense A: reject query if max cosine_sim to stored keys < threshold.
    Returns (pred, accepted_mask). Rejected queries get pred=-1."""
    sims_q_keys = q @ keys.T / N_use  # (n_q, M)
    max_sim = sims_q_keys.max(dim=-1).values
    accepted = max_sim >= DEFENSE_A_SIM_THRESH
    pred_raw, _ = _retrieve(W, q, codebook, N_use)
    pred = torch.where(accepted, pred_raw, torch.full_like(pred_raw, -1))
    return pred, accepted


def defense_b_dist_check(W, q, codebook, N_use):
    """Defense B: retrieve, then verify cos(q, candidate) >= threshold;
    else return -1. Returns (pred, accepted_mask)."""
    pred_raw, _ = _retrieve(W, q, codebook, N_use)
    # Sim between query q and the retrieved value codeword
    cand = codebook[pred_raw]
    cos = (q * cand).sum(dim=-1) / N_use
    accepted = cos >= DEFENSE_B_DIST_THRESH
    pred = torch.where(accepted, pred_raw, torch.full_like(pred_raw, -1))
    return pred, accepted


def measure_seed(N_use: int, M: int, n_adv: int, n_leg: int,
                   seed: int, device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)
    keys = codebook[key_idx]

    # Adversarial: codebook-collision pattern
    adv_q, adv_targets = _collision_queries(
        codebook, key_idx, val_idx, n_adv, N_use, device)
    if adv_q is None:
        del codebook, W
        _safe_clear(device)
        return {"seed": int(seed), "M": int(M), "ok": False,
                "error": "no adversarial queries constructed"}

    # Legitimate
    leg_q, leg_targets = _legitimate_queries(
        codebook, key_idx, val_idx, n_leg, seed, device)

    # Baseline (no defense)
    baseline_pred, _ = _retrieve(W, adv_q, codebook, N_use)
    baseline_correct = (baseline_pred == adv_targets["true"]).float().mean().item()

    # Defense A
    a_adv_pred, a_adv_accepted = defense_a_query_sim(W, adv_q, codebook, keys, N_use)
    # Defense rate: query rejected OR pred == true
    a_correct = ((a_adv_pred == -1) | (a_adv_pred == adv_targets["true"])).float().mean().item()
    # FP rate on legit
    a_leg_pred, a_leg_accepted = defense_a_query_sim(W, leg_q, codebook, keys, N_use)
    # FP = rejected legit OR returns wrong answer
    a_fp = ((a_leg_pred == -1) | (a_leg_pred != leg_targets)).float().mean().item()

    # Defense B
    b_adv_pred, _ = defense_b_dist_check(W, adv_q, codebook, N_use)
    b_correct = ((b_adv_pred == -1) | (b_adv_pred == adv_targets["true"])).float().mean().item()
    b_leg_pred, _ = defense_b_dist_check(W, leg_q, codebook, N_use)
    b_fp = ((b_leg_pred == -1) | (b_leg_pred != leg_targets)).float().mean().item()

    del codebook, W
    _safe_clear(device)
    return {"seed": int(seed), "M": int(M), "ok": True,
            "baseline_correct_on_adv": round(float(baseline_correct), 5),
            "defenses": {
                "a_query_sim": {"defense_rate": round(float(a_correct), 5),
                                 "fp_rate": round(float(a_fp), 5)},
                "b_dist_check": {"defense_rate": round(float(b_correct), 5),
                                  "fp_rate": round(float(b_fp), 5)},
            },
            "n_adv": int(adv_q.shape[0]), "n_leg": int(leg_q.shape[0])}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("G8_INCONCLUSIVE", "no cells")
    ok = [c for c in cells if c.get("ok")]
    if not ok:
        return ("G8_INCONCLUSIVE", f"all {len(cells)} cells failed")

    defense_names = ["a_query_sim", "b_dist_check"]
    summaries = {}
    for d in defense_names:
        d_rates = [c["defenses"][d]["defense_rate"] for c in ok]
        fp_rates = [c["defenses"][d]["fp_rate"] for c in ok]
        summaries[d] = {"mean_def": sum(d_rates) / len(d_rates),
                        "mean_fp": sum(fp_rates) / len(fp_rates)}

    detail = " | ".join(
        f"{d}: def={summaries[d]['mean_def']:.3f} fp={summaries[d]['mean_fp']:.3f}"
        for d in defense_names)

    n_hp = sum(1 for d in defense_names
               if summaries[d]["mean_def"] >= HP_DEFENSE_RATE
               and summaries[d]["mean_fp"] <= HP_MAX_FP_RATE)
    n_hf = sum(1 for d in defense_names
               if summaries[d]["mean_def"] < HF_DEFENSE_RATE
               or summaries[d]["mean_fp"] > HF_MAX_FP_RATE)

    if n_hp >= 1:
        return ("G8_HARD_PASS", f"DEFENSE_VIABLE n_hp={n_hp}/{len(defense_names)}. " + detail)
    if n_hf == len(defense_names):
        return ("G8_HARD_FAIL", f"ALL_DEFENSES_FAIL. " + detail)
    return ("G8_MIDDLE_BAND", f"PARTIAL n_hp=0 n_hf={n_hf}/{len(defense_names)}. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, "PROT-018: _n4096"
    assert len(SEEDS_FULL) == 5

    # Verdict gate HP
    fake_hp = [{"seed": s, "M": M_PROD, "ok": True,
                "baseline_correct_on_adv": 0.05,
                "defenses": {
                    "a_query_sim": {"defense_rate": 0.90, "fp_rate": 0.05},
                    "b_dist_check": {"defense_rate": 0.50, "fp_rate": 0.10}},
                "n_adv": 32, "n_leg": 64}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    # Verdict gate HF
    fake_hf = [{"seed": s, "M": M_PROD, "ok": True,
                "baseline_correct_on_adv": 0.05,
                "defenses": {
                    "a_query_sim": {"defense_rate": 0.30, "fp_rate": 0.30},
                    "b_dist_check": {"defense_rate": 0.20, "fp_rate": 0.40}},
                "n_adv": 32, "n_leg": 64}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Verdict gate MB
    fake_mb = [{"seed": s, "M": M_PROD, "ok": True,
                "baseline_correct_on_adv": 0.05,
                "defenses": {
                    "a_query_sim": {"defense_rate": 0.70, "fp_rate": 0.15},
                    "b_dist_check": {"defense_rate": 0.65, "fp_rate": 0.12}},
                "n_adv": 32, "n_leg": 64}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_mb); assert "MIDDLE_BAND" in v, v

    # Live smoke on CPU (N_SMOKE=1024 min for Kerdock)
    device = torch.device("cpu")
    out = measure_seed(N_SMOKE, 128, 4, 8, 17, device)
    assert out["ok"], f"selftest measure_seed failed: {out.get('error')}"
    assert "a_query_sim" in out["defenses"]
    assert "b_dist_check" in out["defenses"]
    print(f"[selftest] adversarial_codebook_collision_defense_probe_v1_n4096 PASS "
          f"baseline_correct={out['baseline_correct_on_adv']:.3f} "
          f"A_def={out['defenses']['a_query_sim']['defense_rate']:.3f} "
          f"B_def={out['defenses']['b_dist_check']['defense_rate']:.3f}",
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
    M = M_SMOKE if smoke else M_PROD
    n_adv = N_ADV_QUERIES_SMOKE if smoke else N_ADV_QUERIES_FULL
    n_leg = N_LEG_QUERIES_SMOKE if smoke else N_LEG_QUERIES_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] adversarial_codebook_collision_defense_probe_v1_n4096 "
          f"smoke={smoke} N={N_cfg} M={M} n_adv={n_adv} n_leg={n_leg} "
          f"seeds={seeds} done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body); continue
        try:
            cell = measure_seed(N_cfg, M, n_adv, n_leg, seed, device)
            write_partial_key(out_dir, ck, cell)
            cells.append(cell)
            print(f"  seed={seed} ok={cell.get('ok')} "
                  f"def_A={cell.get('defenses', {}).get('a_query_sim', {}).get('defense_rate', 'n/a')} "
                  f"def_B={cell.get('defenses', {}).get('b_dist_check', {}).get('defense_rate', 'n/a')} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
            print(f"  seed={seed} FAILED: {e}", flush=True)
            _safe_clear(device)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "adversarial_codebook_collision_defense_probe_v1_n4096",
               "N": N_cfg, "smoke": smoke, "M": M, "seeds": seeds, "cells": cells,
               "verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
