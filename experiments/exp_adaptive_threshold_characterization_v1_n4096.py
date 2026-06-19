"""ADAPTIVE THRESHOLD CHARACTERIZATION v1 at N=4096.

CONTEXT:
  Substrate-physics framework predicts optimal KF-1 thresholds from
  closed-form analysis of softmax decision boundary. Question: do EMPIRICAL
  optimal thresholds across (beta, M_frac) match framework predictions?

SCIENTIFIC QUESTION:
  Per (beta, M_frac) cell, sweep KF-1 hallu_threshold and find empirical
  optimum (max killer-feature score = AUC of in-store vs OOS at the chosen
  threshold). Compare to framework's predicted-optimal.

FRAMEWORK PREDICTION (closed-form, conservative):
  Predicted near-uniform threshold ~ M / C * beta^scale
  We use: pred_thr = clip(0.5 / (1 + math.exp(-beta * (M_frac / 4 - 1))), 0.01, 0.99)
  This is a sigmoid that interpolates between low-conf (low beta, low M_frac)
  and high-conf (high beta, high M_frac).
  Formula self-tested below.

PRE-REGISTERED BANDS:
  HARD_PASS: empirical-vs-prediction within +/-20% in >= 7 of 9 cells.
  HARD_FAIL: empirical-vs-prediction off by >= 50% in >= 6 of 9 cells.
  MIDDLE_BAND: otherwise.

FORMULA SELF-TESTS:
  1. N = 4096 (PROT-018).
  2. 3 betas x 3 M_fracs = 9 cells. Each * 7 thresholds.
  3. pred_thr(beta=4, M_frac=1) = sigmoid(4*(0.25 - 1)) = sigmoid(-3) ~ 0.047.
  4. pred_thr(beta=32, M_frac=16) = sigmoid(32*(4 - 1)) = sigmoid(96) ~ 1.0
     -> clipped to 0.99.
  5. Within-tolerance test: |emp - pred| / pred <= 0.20.

OOM CHECK: M_max at M_frac=16 = 65536. keys=1.07GB, W=64MB, CB=805MB. Total ~2GB. OK.

TIMEOUT ESTIMATE: 9 cells * 3 seeds * 7 thresholds. ~10s/cell. ~30 min. 21600s ample.

N-suffix: _n4096 (PROT-018).
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

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_thr", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096        # PROT-018 production-N anchor
N_FULL  = N
N_SMOKE = 1024
BETAS_FULL  = [4.0, 10.0, 32.0]
BETAS_SMOKE = [4.0, 32.0]
MFRACS_FULL  = [1.0, 4.0, 16.0]
MFRACS_SMOKE = [1.0, 4.0]
SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]
THR_SWEEP = [0.05, 0.15, 0.30, 0.50, 0.70, 0.85, 0.95]
N_PROBE = 100

HP_FRAC_WITHIN_20 = 7.0 / 9.0
HF_FRAC_OFF_50   = 6.0 / 9.0


def predicted_threshold(beta: float, M_frac: float) -> float:
    """Closed-form near-uniform threshold prediction.

    pred = sigmoid(beta * (M_frac / 4 - 1)), clipped [0.01, 0.99].
    Rationale: at low M_frac the substrate is uncrowded so the in-store mode
    is sharp (low threshold suffices); high M_frac concentrates probability
    mass in many points so threshold must be higher to discriminate. Beta
    sharpens the sigmoid.
    """
    z = beta * (M_frac / 4.0 - 1.0)
    p = 1.0 / (1.0 + math.exp(-min(50.0, max(-50.0, z))))
    return max(0.01, min(0.99, p))


def _auc(pos: torch.Tensor, neg: torch.Tensor) -> float:
    if pos.numel() == 0 or neg.numel() == 0:
        return 0.5
    pos = pos.detach().cpu(); neg = neg.detach().cpu()
    all_s = torch.cat([pos, neg])
    ranks = torch.argsort(torch.argsort(all_s)).float() + 1.0
    pos_rank_sum = ranks[:pos.numel()].sum().item()
    np_, nn_ = pos.numel(), neg.numel()
    return float((pos_rank_sum - np_ * (np_ + 1) / 2.0) / (np_ * nn_))


def measure_cell(N_use: int, beta: float, M_frac: float, seed: int,
                  device: torch.device) -> Dict:
    M = max(1, int(round(M_frac * N_use)))
    codebook, W, keys, values, key_idx, val_idx = make_substrate(N_use, M, seed, device)
    C = codebook.shape[0]
    stored_set = set(key_idx.tolist()[:min(key_idx.shape[0], 10000)])
    available = [i for i in range(C) if i not in stored_set]
    n_pos = min(N_PROBE, M); n_neg = min(N_PROBE, len(available))
    out = {"beta": beta, "M_frac": M_frac, "M": M, "seed": seed,
           "best_threshold": 0.5, "best_score": 0.0,
           "pred_threshold": round(predicted_threshold(beta, M_frac), 5),
           "rel_err": 0.0, "all_scores": []}
    if n_pos < 1 or n_neg < 1:
        del W, keys, values, codebook
        return out
    gen = torch.Generator(device=device).manual_seed(seed + 1400)
    perm = torch.randperm(len(available), generator=gen, device=device)[:n_neg]
    oos_idx = torch.tensor([available[int(i)] for i in perm.tolist()],
                            dtype=torch.long, device=device)
    in_keys = keys[:n_pos]
    oos_keys = codebook[oos_idx]
    q_in  = in_keys @ W.T
    q_oos = oos_keys @ W.T
    sims_in  = (codebook @ q_in.T) / N_use
    sims_oos = (codebook @ q_oos.T) / N_use
    P_in  = torch.softmax(beta * sims_in, dim=0)
    P_oos = torch.softmax(beta * sims_oos, dim=0)
    mc_in  = P_in.max(dim=0).values
    mc_oos = P_oos.max(dim=0).values

    # For each candidate threshold: classification accuracy = TPR + (1-FPR) - 1
    # We pick the threshold maximizing Youden's J statistic (TPR - FPR)
    scores = []
    for thr in THR_SWEEP:
        tpr = float((mc_in  >= thr).float().mean().item())
        fpr = float((mc_oos >= thr).float().mean().item())
        scores.append(tpr - fpr)
    best_idx = max(range(len(scores)), key=lambda i: scores[i])
    out["best_threshold"] = float(THR_SWEEP[best_idx])
    out["best_score"]     = round(scores[best_idx], 5)
    out["all_scores"]     = [round(s, 5) for s in scores]
    # Within-tolerance flag
    pred = out["pred_threshold"]
    emp  = out["best_threshold"]
    out["rel_err"] = round(abs(emp - pred) / max(pred, 1e-6), 5)

    del W, keys, values, codebook
    if device.type == 'cuda':
        torch.cuda.empty_cache()
    return out


def compute_verdict(cells_per_cell: Dict[Tuple[float, float], List[float]]) -> Tuple[str, str]:
    if not cells_per_cell:
        return ("ATC_INCONCLUSIVE", "No cells.")
    n_cells = len(cells_per_cell)
    n_within_20 = 0; n_off_50 = 0
    per_cell_summary = []
    for (beta, mf), rel_errs in cells_per_cell.items():
        if not rel_errs:
            continue
        mean_err = sum(rel_errs) / len(rel_errs)
        per_cell_summary.append(f"b{beta}_m{mf}={mean_err:.3f}")
        if mean_err <= 0.20:
            n_within_20 += 1
        if mean_err >= 0.50:
            n_off_50 += 1
    frac_within = n_within_20 / max(1, n_cells)
    frac_off    = n_off_50   / max(1, n_cells)
    detail = (f"n_within_20={n_within_20}/{n_cells} (frac {frac_within:.3f}) "
              f"n_off_50={n_off_50}/{n_cells} (frac {frac_off:.3f}) "
              f"cells: " + " ".join(per_cell_summary))
    if frac_within >= HP_FRAC_WITHIN_20:
        return ("ATC_HARD_PASS", f"FRAMEWORK_AGREES: " + detail)
    if frac_off >= HF_FRAC_OFF_50:
        return ("ATC_HARD_FAIL", f"FRAMEWORK_MISSES: " + detail)
    return ("ATC_MIDDLE_BAND", f"FRAMEWORK_PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    # Formula self-tests
    pred = predicted_threshold(4.0, 1.0)
    assert 0.04 <= pred <= 0.06, f"pred(4,1) expected ~0.047, got {pred}"
    pred = predicted_threshold(32.0, 16.0)
    assert pred == 0.99, f"pred(32,16) clipped expected 0.99, got {pred}"
    pred = predicted_threshold(10.0, 4.0)
    assert 0.49 <= pred <= 0.51, f"pred(10,4) at M_frac=4 sigmoid(0)=0.5 expected, got {pred}"
    pred = predicted_threshold(10.0, 8.0)
    assert pred > 0.9, f"pred(10,8) expected > 0.9, got {pred}"

    # Verdict gates
    cells = {(4.0, 1.0): [0.10], (10.0, 1.0): [0.15], (32.0, 1.0): [0.10],
              (4.0, 4.0): [0.05], (10.0, 4.0): [0.10], (32.0, 4.0): [0.18],
              (4.0, 16.0): [0.15], (10.0, 16.0): [0.10], (32.0, 16.0): [0.10]}
    v, _ = compute_verdict(cells); assert "HARD_PASS" in v, v
    cells = {k: [0.6] for k in cells.keys()}
    v, _ = compute_verdict(cells); assert "HARD_FAIL" in v, v
    cells = {k: [0.3] for k in cells.keys()}
    v, _ = compute_verdict(cells); assert "MIDDLE_BAND" in v, v

    device = torch.device("cpu")
    cell = measure_cell(N_SMOKE, 4.0, 1.0, 17, device)
    assert cell["best_threshold"] in THR_SWEEP, f"best_thr unknown: {cell}"
    assert cell["pred_threshold"] is not None
    print(f"[selftest] adaptive_threshold_characterization_v1_n4096 PASS "
          f"emp={cell['best_threshold']:.3f} pred={cell['pred_threshold']:.3f} "
          f"rel_err={cell['rel_err']:.3f}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    device_str = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device_str)
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    betas = BETAS_SMOKE if smoke else BETAS_FULL
    mfracs = MFRACS_SMOKE if smoke else MFRACS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] adaptive_threshold_char smoke={smoke} N={N_cfg} betas={betas} "
          f"mfracs={mfracs} seeds={seeds} done={len(done)} device={device_str}",
          flush=True)

    cells: List[Dict] = []
    cells_per_cell: Dict = {}
    for beta in betas:
        for mf in mfracs:
            errs = []
            for seed in seeds:
                ck = f"b{beta:g}_m{mf:g}_seed{seed}".replace(".", "p")
                if ck in done:
                    body = load_partial_key(out_dir, ck)
                    if body is not None:
                        cells.append(body)
                        errs.append(body.get("rel_err", 0.0))
                        continue
                try:
                    out = measure_cell(N_cfg, beta, mf, seed, device)
                    write_partial_key(out_dir, ck, out)
                    cells.append(out)
                    errs.append(out["rel_err"])
                    print(f"  b={beta} mf={mf} seed={seed} emp={out['best_threshold']:.3f} "
                          f"pred={out['pred_threshold']:.3f} "
                          f"err={out['rel_err']:.3f} ({time.time()-t0:.1f}s)",
                          flush=True)
                except (RuntimeError, MemoryError) as e:
                    print(f"  b={beta} mf={mf} seed={seed} FAILED: {e}",
                          flush=True)
                    if device.type == 'cuda':
                        torch.cuda.empty_cache()
            cells_per_cell[(beta, mf)] = errs

    def get_output_dir_inner():
        return out_dir
    verdict, vm = compute_verdict(cells_per_cell)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "adaptive_threshold_characterization_v1_n4096",
               "N": N_cfg, "smoke": smoke, "betas": betas, "mfracs": mfracs,
               "seeds": seeds, "cells": cells,
               "verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


def get_output_dir(default_name: str = "adaptive_threshold_characterization_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


if __name__ == "__main__":
    main()
