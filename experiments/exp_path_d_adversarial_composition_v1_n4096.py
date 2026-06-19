"""PATH D UNDER ADVERSARIAL CODEBOOK-COLLISION COMPOSITION v1 at N=4096.

CONTEXT (composition of today's two HARD_PASSes):
  G7EXT HARD_PASS: Path D no-ceiling at depth=5, N=4096, 64N (v299).
  G8 HARD_PASS: a_query_sim defense defeats codebook-collision (def=1.000) (v299).
  These two results COMPOSE under interleaved workload?

COMPOSITIONAL QUESTION:
  Under 50/50 legitimate/adversarial interleaved workload at depth=5:
  (1) Does a_query_sim defense gate reject adversarial queries
      (defense_rate >= 0.85)?
  (2) Does Path D maintain acc >= 0.95 on the LEGITIMATE 50% that pass
      through the defense gate?

  If both YES: production deployment story is coherent -- defense gate
  + Path D co-exist without mutual interference.

  If Path D fails on guarded queries (defense interferes with Path D): the
  defense gate and the mechanism interact badly. Must be resolved before
  deployment.

  If defense fails to reject adversarial under Path D load: adversarial
  interleaving degrades the defense.

DESIGN:
  N=4096, M=2048 (nominal), depth=5, K_paths=100.
  For each seed: build substrate. Create 50/50 batch:
    - 50 starts: legitimate (valid relation keys, coherent Path D paths)
    - 50 queries: adversarial (codebook-collision pattern from G8)
  Apply defense gate to BOTH halves:
    - Measure: defense_rate on adversarial (how many rejected)
    - Measure: path_d_acc on legitimate queries that PASS the gate
    - Measure: path_d_acc on legitimate queries WITHOUT gate (baseline)

PRE-REGISTERED BANDS:
  HP = defense_rate on adversarial >= 0.85 AND path_d_acc on gated_legit >= 0.95
       in 4/5+ seeds.
  HF = either path_d_acc on gated_legit < 0.70 (gate interferes with Path D)
       OR defense_rate < 0.50 (defense degrades under Path D load) in majority.
  MB = otherwise (partial, some conditions met).

PROT-018: _n4096 binds N = 4096.
PROT-020: torch.device("cuda") -- GPU queue.
PROT-021: per-seed checkpointing.

Anchor: path_d_adversarial_composition_v1_n4096
Queue: overnight_queue (GPU)
Pre-reg: preregs/2026-05-31_path_d_adversarial_composition_v1_n4096.md
Total cells: 5 seeds x 1 M value = 5 cells.
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

from experiments._multi_hop_mechanisms import build_shared, path_d_run  # noqa: E402

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_pdac", _ck_path)
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

M_PROD  = 2048
M_SMOKE = 256
DEPTH   = 5
K_PATHS = 100

N_LEG_FULL  = 50   # legitimate starts
N_LEG_SMOKE = 12
N_ADV_FULL  = 50   # adversarial queries
N_ADV_SMOKE = 12

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

DEFENSE_A_SIM_THRESH = 0.5  # identical to G8

HP_DEF_RATE   = 0.85
HP_PATH_D_ACC = 0.95
HF_PATH_D_ACC = 0.70
HF_DEF_RATE   = 0.50
HP_MIN_SEEDS  = 4


def get_output_dir(default_name: str = "path_d_adversarial_composition_v1_n4096") -> Path:
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


def _adversarial_queries(codebook, key_idx, val_idx, n_q, N_use, device):
    """Build adversarial queries via codebook-collision pattern (same as G8)."""
    if key_idx.shape[0] < 2:
        return None, None
    keys = codebook[key_idx]
    sims = keys @ keys.T / N_use
    sims.fill_diagonal_(-1.0)
    top_sim, idx = sims.view(-1).topk(min(n_q * 2, sims.numel()))
    qs, true_t = [], []
    seen: set = set()
    n_keys = key_idx.shape[0]
    for sv, ix in zip(top_sim.tolist(), idx.tolist()):
        i = ix // n_keys
        j = ix % n_keys
        if i == j or sv <= 0:
            continue
        if (i, j) in seen or (j, i) in seen:
            continue
        seen.add((i, j))
        qs.append(keys[i])
        true_t.append(int(val_idx[i].item()))
        if len(qs) >= n_q:
            break
    if not qs:
        return None, None
    return torch.stack(qs), torch.tensor(true_t, device=device)


def _defense_a_gate(q, codebook, key_idx, N_use):
    """Return boolean mask: True = accepted by defense gate."""
    keys = codebook[key_idx]
    sims_q_keys = q @ keys.T / N_use
    max_sim = sims_q_keys.max(dim=-1).values
    return max_sim >= DEFENSE_A_SIM_THRESH


def measure_seed(N_use: int, M: int, depth: int, K_paths: int,
                  n_leg: int, n_adv: int, seed: int,
                  device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)

    # --- Legitimate starts: valid relation keys
    leg_keys_list = [k for k in list(relation.keys()) if relation.get(k) is not None]
    n_leg_avail = min(n_leg, len(leg_keys_list))
    if n_leg_avail < depth + 1:
        del codebook, W
        _safe_clear(device)
        return {"seed": int(seed), "M": int(M), "ok": False,
                "error": f"not enough relation keys: {n_leg_avail}"}

    leg_starts = torch.tensor(leg_keys_list[:n_leg_avail],
                               dtype=torch.long, device=device)
    leg_q = codebook[leg_starts]

    # --- Adversarial queries
    adv_q, adv_true = _adversarial_queries(codebook, key_idx, val_idx, n_adv, N_use, device)
    if adv_q is None:
        del codebook, W
        _safe_clear(device)
        return {"seed": int(seed), "M": int(M), "ok": False,
                "error": "no adversarial queries constructed"}

    # --- Defense gate on adversarial
    adv_accepted = _defense_a_gate(adv_q, codebook, key_idx, N_use)
    defense_rate = float((~adv_accepted).float().mean().item())  # fraction REJECTED

    # --- Defense gate on legitimate (false-positive check)
    leg_gate_accepted = _defense_a_gate(leg_q, codebook, key_idx, N_use)
    leg_pass_mask = leg_gate_accepted
    n_leg_pass = int(leg_pass_mask.sum().item())

    # --- Path D on ALL legitimate starts (baseline, no gate)
    path_d_baseline_correct = path_d_run(
        codebook, W, leg_starts, relation, depth, K_paths, seed, N_use)
    acc_baseline = float(path_d_baseline_correct.mean().item())

    # --- Path D on legitimate starts that PASS the gate
    if n_leg_pass > 0:
        gated_starts = leg_starts[leg_pass_mask]
        path_d_gated_correct = path_d_run(
            codebook, W, gated_starts, relation, depth, K_paths, seed + 5000, N_use)
        acc_gated = float(path_d_gated_correct.mean().item())
    else:
        acc_gated = float("nan")

    # FP rate on legitimate: fraction rejected by gate
    fp_rate = float((~leg_gate_accepted).float().mean().item())

    del codebook, W
    _safe_clear(device)
    return {"seed": int(seed), "M": int(M), "ok": True,
            "n_leg": int(leg_starts.shape[0]),
            "n_adv": int(adv_q.shape[0]),
            "n_leg_pass_gate": n_leg_pass,
            "defense_rate": round(defense_rate, 5),
            "fp_rate": round(fp_rate, 5),
            "acc_path_d_baseline": round(acc_baseline, 5),
            "acc_path_d_gated": round(acc_gated, 5) if not isinstance(acc_gated, float) or not (acc_gated != acc_gated) else None}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("PDAC_INCONCLUSIVE", "no cells")
    ok = [c for c in cells if c.get("ok")]
    if not ok:
        return ("PDAC_INCONCLUSIVE", f"all {len(cells)} cells failed")

    def_rates   = [c["defense_rate"] for c in ok]
    gated_accs  = [c["acc_path_d_gated"] for c in ok if c.get("acc_path_d_gated") is not None]
    base_accs   = [c["acc_path_d_baseline"] for c in ok]
    fp_rates    = [c["fp_rate"] for c in ok]

    mean_def  = sum(def_rates) / len(def_rates)
    mean_gated = sum(gated_accs) / len(gated_accs) if gated_accs else float("nan")
    mean_base = sum(base_accs) / len(base_accs)
    mean_fp   = sum(fp_rates) / len(fp_rates)

    detail = (f"mean_def_rate={mean_def:.3f} mean_acc_gated={mean_gated:.3f} "
              f"mean_acc_baseline={mean_base:.3f} mean_fp={mean_fp:.3f} "
              f"n_cells={len(ok)}")

    # HP: defense_rate >= 0.85 AND acc_gated >= 0.95 in HP_MIN_SEEDS seeds
    n_hp = sum(
        1 for c in ok
        if (c["defense_rate"] >= HP_DEF_RATE
            and c.get("acc_path_d_gated") is not None
            and c["acc_path_d_gated"] >= HP_PATH_D_ACC))

    # HF: either path_d_acc_gated < 0.70 (gate breaks mechanism)
    #     OR defense_rate < 0.50 (defense degraded) in majority of cells
    n_path_d_fail = sum(
        1 for c in ok
        if (c.get("acc_path_d_gated") is not None
            and c["acc_path_d_gated"] < HF_PATH_D_ACC))
    n_def_fail = sum(1 for c in ok if c["defense_rate"] < HF_DEF_RATE)

    majority = len(ok) // 2 + 1
    is_hf = (n_path_d_fail >= majority or n_def_fail >= majority)

    if n_hp >= HP_MIN_SEEDS:
        return ("PDAC_HARD_PASS",
                f"COMPOSITION_COHERENT n_hp={n_hp}/{len(ok)}. " + detail)
    if is_hf:
        return ("PDAC_HARD_FAIL",
                f"COMPOSITION_FAILS n_path_d_fail={n_path_d_fail} "
                f"n_def_fail={n_def_fail} n_cells={len(ok)}. " + detail)
    return ("PDAC_MIDDLE_BAND",
            f"PARTIAL n_hp={n_hp}/{len(ok)}. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at smoke scale."""
    assert N_FULL == 4096, "PROT-018: _n4096"
    assert len(SEEDS_FULL) == 5, f"expected 5 seeds, got {len(SEEDS_FULL)}"

    # Verdict gate HP
    fake_hp = [{"seed": s, "M": M_PROD, "ok": True,
                "n_leg": 50, "n_adv": 50, "n_leg_pass_gate": 48,
                "defense_rate": 0.92, "fp_rate": 0.04,
                "acc_path_d_baseline": 1.000, "acc_path_d_gated": 0.97}
               for s in SEEDS_FULL]
    v, msg = compute_verdict(fake_hp)
    assert "HARD_PASS" in v, f"HP gate failed: {v} {msg}"

    # Verdict gate HF: gate breaks Path D (acc_gated very low)
    fake_hf = [{"seed": s, "M": M_PROD, "ok": True,
                "n_leg": 50, "n_adv": 50, "n_leg_pass_gate": 30,
                "defense_rate": 0.80, "fp_rate": 0.40,
                "acc_path_d_baseline": 0.95, "acc_path_d_gated": 0.50}
               for s in SEEDS_FULL]
    v, msg = compute_verdict(fake_hf)
    assert "HARD_FAIL" in v, f"HF gate failed: {v} {msg}"

    # Verdict gate MB: partial -- 2 HP seeds only
    fake_mb = ([{"seed": s, "M": M_PROD, "ok": True,
                 "n_leg": 50, "n_adv": 50, "n_leg_pass_gate": 40,
                 "defense_rate": 0.90, "fp_rate": 0.05,
                 "acc_path_d_baseline": 0.99, "acc_path_d_gated": 0.96}
                for s in [7, 17]]
               + [{"seed": s, "M": M_PROD, "ok": True,
                   "n_leg": 50, "n_adv": 50, "n_leg_pass_gate": 35,
                   "defense_rate": 0.75, "fp_rate": 0.10,
                   "acc_path_d_baseline": 0.90, "acc_path_d_gated": 0.78}
                  for s in [23, 31, 41]])
    v, msg = compute_verdict(fake_mb)
    assert "MIDDLE_BAND" in v, f"MB gate failed: {v} {msg}"

    # Live smoke on CPU (selftest uses CPU regardless of FULL device)
    device = torch.device("cpu")
    out = measure_seed(N_SMOKE, M_SMOKE, DEPTH, K_PATHS,
                        N_LEG_SMOKE, N_ADV_SMOKE, 17, device)
    assert out["ok"], f"selftest measure_seed failed: {out.get('error')}"
    assert 0.0 <= out["defense_rate"] <= 1.0, f"defense_rate sentinel: {out}"
    assert 0.0 <= out["acc_path_d_baseline"] <= 1.0, f"acc_baseline sentinel: {out}"
    # acc_path_d_gated may be None if all legit rejected; accept either
    if out.get("acc_path_d_gated") is not None:
        assert 0.0 <= out["acc_path_d_gated"] <= 1.0, f"acc_gated sentinel: {out}"
    assert out["n_leg"] >= 1, f"n_leg=0: {out}"
    assert out["n_adv"] >= 1, f"n_adv=0: {out}"
    print(f"[selftest] path_d_adversarial_composition_v1_n4096 PASS "
          f"def_rate={out['defense_rate']:.3f} "
          f"acc_base={out['acc_path_d_baseline']:.3f} "
          f"acc_gated={out.get('acc_path_d_gated','n/a')}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    # ANCHOR D: overnight_queue (GPU)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    smoke  = args.smoke
    N_cfg  = N_SMOKE    if smoke else N_FULL
    M      = M_SMOKE    if smoke else M_PROD
    n_leg  = N_LEG_SMOKE if smoke else N_LEG_FULL
    n_adv  = N_ADV_SMOKE if smoke else N_ADV_FULL
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done    = set(list_completed_keys(out_dir))
    t0      = time.time()
    print(f"[run] path_d_adversarial_composition_v1_n4096 smoke={smoke} "
          f"N={N_cfg} M={M} depth={DEPTH} K_paths={K_PATHS} "
          f"n_leg={n_leg} n_adv={n_adv} seeds={seeds} "
          f"done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body)
                continue
        try:
            cell = measure_seed(N_cfg, M, DEPTH, K_PATHS,
                                  n_leg, n_adv, seed, device)
            write_partial_key(out_dir, ck, cell)
            cells.append(cell)
            print(f"  seed={seed} ok={cell.get('ok')} "
                  f"def_rate={cell.get('defense_rate','n/a')} "
                  f"acc_gated={cell.get('acc_path_d_gated','n/a')} "
                  f"acc_base={cell.get('acc_path_d_baseline','n/a')} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
            print(f"  seed={seed} FAILED: {e}", flush=True)
            _safe_clear(device)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "path_d_adversarial_composition_v1_n4096",
               "N": N_cfg, "smoke": smoke, "M": M,
               "depth": DEPTH, "K_paths": K_PATHS,
               "n_leg": n_leg, "n_adv": n_adv, "seeds": seeds,
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
