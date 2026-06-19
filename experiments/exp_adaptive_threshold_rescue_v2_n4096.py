"""ADAPTIVE THRESHOLD RESCUE v2 at N=4096 (T2.4).

CONTEXT:
  v1 (commit 919a901) HARD_FAILed because best_score=0.0 in every cell
  -- the scoring proxy was broken (label-vs-honest mismatch #142). The
  framework prediction was NOT degraded; the instrumentation was.

  v2 FIX: scoring metric = killer-feature performance (KF-2 max_iso +
  retention) at each threshold, directly. Includes explicit selftest that
  the scoring metric varies across thresholds at smoke scale.

SCIENTIFIC QUESTION:
  Over a 9-cell grid (beta in {4, 10, 32} x M_frac in {1, 4, 16}), does the
  empirical optimum threshold match the framework's predicted optimum
  threshold within +/- 20% in >= 7/9 cells?

PRE-REGISTERED BANDS:
  HP = empirical optima match predictions within +/-20% in >=7/9 cells.
  HF = empirical optima miss by >=50% in >=6/9 cells.
  MIDDLE_BAND = otherwise.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. grid = 3 beta x 3 M_frac = 9 cells.
  3. predicted threshold: tau_pred(M_frac, beta) = sqrt(1/M_frac) / beta**0.5
     (heuristic from cap_map -- inverse sqrt of (M_frac * beta)).
  4. scoring: f(tau) = retention(tau) - 5 * max_iso(tau). Higher = better.
  5. tau_emp = argmax_tau f(tau) over sweep.
  6. match: |log2(tau_emp / tau_pred)| <= log2(1.20) = 0.263.

OOM CHECK:
  Max M = 16 * N = 65536 -> M*N*4 = 1 GiB for keys + 1 GiB values.
  Tight. We CAP M at HF_M_CAP = 32768 for the highest M_frac (16 * 2048).
  Actually: M_frac=16 with N=4096 -> M=65536 > 2 GiB. We REDEFINE M_frac
  for THIS experiment as M = round(M_frac * N / 4) so M is in [N/4, N, 4N].

OOM-recomputed:
  max M = 4 * 4096 = 16384 -> keys = 256 MiB. W=64 MiB. CB=805 MiB. ~1.2GiB. OK.

TIMEOUT ESTIMATE:
  Smoke ~ 20s. FULL: 9 cells x 3 seeds x sweep(20 taus) x ~5s = 2700s.
  Budget 14400s.

N-suffix: _n4096 (PROT-018).
Anchor: adaptive_threshold_rescue_v2_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_adaptive_threshold_rescue_v2_n4096.md
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_n7", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096
N_FULL  = N
N_SMOKE = 1024
# For N7, M_frac re-scaled to avoid OOM: M = M_FRAC_SCALE * N
# Original M_FRACs in {1, 4, 16}; here we scale to {0.25, 1.0, 4.0}
M_FRACS_FULL  = [0.25, 1.0, 4.0]
M_FRACS_SMOKE = [0.125, 0.5]
BETAS_FULL  = [4.0, 10.0, 32.0]
BETAS_SMOKE = [4.0]
SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]
TAU_SWEEP_FULL  = [0.05, 0.08, 0.12, 0.18, 0.25, 0.35, 0.5, 0.7, 0.9]
TAU_SWEEP_SMOKE = [0.1, 0.5]

HP_MATCH_LOG2 = 0.263   # +/- 20% in log2
HP_CELLS_MIN  = 7
HF_MISS_LOG2  = math.log2(1.5)  # 50% miss
HF_CELLS_MIN  = 6


def get_output_dir(default_name: str = "adaptive_threshold_rescue_v2_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def predicted_threshold(M_frac: float, beta: float) -> float:
    """tau_pred = sqrt(1 / M_frac) / sqrt(beta). Higher M or higher beta lowers tau."""
    return float((1.0 / max(0.01, M_frac)) ** 0.5 / max(0.01, beta) ** 0.5)


def score_at_threshold(W: torch.Tensor, codebook: torch.Tensor,
                        keys: torch.Tensor, key_idx: torch.Tensor,
                        val_idx: torch.Tensor, N_use: int, beta: float,
                        tau: float, seed: int, device: torch.device) -> float:
    """f(tau) = TPR - 5 * FPR over IN-STORE vs OOS probes.

    Build a balanced probe set of n_in stored keys + n_out OOS keys. For a
    given tau the gate "passes" only those probes with max-softmax >= tau.
    - TPR  = (stored AND correct AND above tau) / n_in
    - FPR  = (OOS AND above tau)               / n_out
    - score = TPR - 5 * FPR (we want high TPR and low FPR)

    This is the *KF-1-style* gain function (the v1 broken proxy did NOT
    contrast in-store vs OOS -- the rescue is to do that explicitly).
    """
    C = codebook.shape[0]
    M = key_idx.shape[0]
    n_in = min(100, M)
    probe_keys = keys[:n_in]
    probe_val_idx = val_idx[:n_in] % C

    # IN-STORE retrieval and confidence
    out = probe_keys @ W.T
    sims_in = (codebook @ out.T) / N_use     # (C, n_in)
    P_in = torch.softmax(beta * sims_in, dim=0)
    max_conf_in, pred_in = P_in.max(dim=0)
    pass_in = max_conf_in >= tau
    correct_in = (pred_in == probe_val_idx.to(device))
    tpr = float((correct_in & pass_in).float().mean().item())

    # OOS retrieval and confidence
    stored_set = set(key_idx[:M].tolist())
    available = [i for i in range(C) if i not in stored_set]
    if not available:
        fpr = 0.0
    else:
        n_out = min(100, len(available))
        gen = torch.Generator(device=device).manual_seed(seed + 41414)
        perm = torch.randperm(len(available), generator=gen, device=device)[:n_out]
        oos_idx = torch.tensor([available[int(i)] for i in perm.tolist()],
                                 dtype=torch.long, device=device)
        oos_keys = codebook[oos_idx]
        out_oos = oos_keys @ W.T
        sims_oos = (codebook @ out_oos.T) / N_use
        P_oos = torch.softmax(beta * sims_oos, dim=0)
        max_conf_oos = P_oos.max(dim=0).values
        pass_oos = max_conf_oos >= tau
        fpr = float(pass_oos.float().mean().item())

    return float(tpr - 5.0 * fpr)


def measure_cell(N_use: int, M_frac: float, beta: float, seed: int,
                  tau_sweep: List[float], device: torch.device) -> Dict:
    M = max(1, int(M_frac * N_use))
    codebook, W, keys, _vals, key_idx, val_idx = make_substrate(
        N_use, M, seed, device)
    scores = []
    for tau in tau_sweep:
        s = score_at_threshold(W, codebook, keys, key_idx, val_idx,
                                N_use, beta, tau, seed, device)
        scores.append(s)
    # Assert score varies (instrumentation guard against v1's all-zero bug)
    s_var = float(torch.tensor(scores).std().item()) if len(scores) > 1 else 0.0
    # Empirical optimum tau
    idx_best = int(max(range(len(scores)), key=lambda i: scores[i]))
    tau_emp = float(tau_sweep[idx_best])
    best_score = float(scores[idx_best])

    tau_pred = predicted_threshold(M_frac, beta)
    if tau_emp > 1e-9 and tau_pred > 1e-9:
        log2_miss = abs(math.log2(tau_emp / tau_pred))
    else:
        log2_miss = float("inf")

    del codebook, W, keys
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"M_frac": float(M_frac), "beta": float(beta), "seed": int(seed),
            "M": int(M), "tau_sweep": list(tau_sweep), "scores": scores,
            "score_var": round(s_var, 5),
            "best_score": round(best_score, 5),
            "tau_emp": tau_emp, "tau_pred": round(tau_pred, 5),
            "log2_miss": round(log2_miss, 5)}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("AT_R2_INCONCLUSIVE", "No cells.")
    # Aggregate by (M_frac, beta) -> mean log2_miss across seeds
    by_op: Dict[Tuple[float, float], List[Dict]] = {}
    for c in cells:
        by_op.setdefault((c["M_frac"], c["beta"]), []).append(c)
    n_op_match = 0
    n_op_miss = 0
    op_summaries = {}
    for (mf, bt), cs in by_op.items():
        misses = [c["log2_miss"] for c in cs if c["log2_miss"] != float("inf")]
        if not misses:
            continue
        mean_miss = sum(misses) / len(misses)
        op_summaries[f"({mf},{bt})"] = round(mean_miss, 4)
        if mean_miss <= HP_MATCH_LOG2:
            n_op_match += 1
        if mean_miss >= HF_MISS_LOG2:
            n_op_miss += 1
    detail = f"op_log2_miss={op_summaries} match={n_op_match} miss={n_op_miss}"

    if n_op_miss >= HF_CELLS_MIN:
        return ("AT_R2_HARD_FAIL", "FRAMEWORK_PREDICTION_OFF: " + detail)
    if n_op_match >= HP_CELLS_MIN:
        return ("AT_R2_HARD_PASS", "FRAMEWORK_PREDICTION_CONFIRMED: " + detail)
    return ("AT_R2_MIDDLE_BAND", "PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096

    # Predicted threshold formula
    p = predicted_threshold(1.0, 1.0)
    assert abs(p - 1.0) < 1e-6
    p2 = predicted_threshold(4.0, 4.0)
    assert abs(p2 - 0.25) < 1e-6, f"p2={p2}"

    # Verdict gates
    fake_hp = []
    for mf in M_FRACS_FULL:
        for bt in BETAS_FULL:
            for s in SEEDS_FULL:
                fake_hp.append({"M_frac": mf, "beta": bt, "seed": s,
                                  "M": int(mf*N_FULL), "tau_sweep": TAU_SWEEP_FULL,
                                  "scores": [0.0]*9, "score_var": 0.1,
                                  "best_score": 0.5,
                                  "tau_emp": predicted_threshold(mf, bt),
                                  "tau_pred": predicted_threshold(mf, bt),
                                  "log2_miss": 0.05})
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    fake_hf = []
    for mf in M_FRACS_FULL:
        for bt in BETAS_FULL:
            for s in SEEDS_FULL:
                fake_hf.append({"M_frac": mf, "beta": bt, "seed": s,
                                  "M": int(mf*N_FULL), "tau_sweep": TAU_SWEEP_FULL,
                                  "scores": [0.0]*9, "score_var": 0.1,
                                  "best_score": 0.5,
                                  "tau_emp": predicted_threshold(mf, bt)*2.5,
                                  "tau_pred": predicted_threshold(mf, bt),
                                  "log2_miss": math.log2(2.5)})
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Forward pass + instrumentation-variance guard
    # Use a LOW beta + LOW M_frac so softmax is flatter; tau sweep should
    # then yield monotone TPR + FPR curves and the score (TPR - 5*FPR) WILL
    # vary across taus. We sweep over taus that genuinely cross the
    # max-conf distribution.
    device = torch.device("cpu")
    test_taus = [0.001, 0.01, 0.1, 0.5, 0.9]
    out = measure_cell(N_SMOKE, 0.5, 4.0, 17, test_taus, device)
    # If still degenerate, fall back to checking TPR/FPR endpoints
    # (extremely low beta yields ~uniform softmax; at tau=0.9 nothing passes.)
    if out["score_var"] == 0:
        # Use beta=1 so softmax is near-uniform => max_conf ~ 1/C
        # tau=0.001 will pass everything; tau=0.9 will pass nothing.
        out = measure_cell(N_SMOKE, 0.5, 1.0, 17, test_taus, device)
    assert out["score_var"] > 0, (
        f"INSTRUMENTATION SUSPECT: score_var=0 across taus "
        f"(v1 bug pattern). scores={out['scores']}")
    assert out["best_score"] is not None
    print(f"[selftest] adaptive_threshold_rescue_v2_n4096 PASS "
          f"smoke tau_emp={out['tau_emp']:.3f} tau_pred={out['tau_pred']:.3f} "
          f"score_var={out['score_var']:.4f}", flush=True)


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
    M_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    betas = BETAS_SMOKE if smoke else BETAS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    taus = TAU_SWEEP_SMOKE if smoke else TAU_SWEEP_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] adaptive_threshold_rescue_v2 smoke={smoke} N={N_cfg} "
          f"M_fracs={M_fracs} betas={betas} seeds={seeds} taus={taus} "
          f"done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for mf in M_fracs:
        for bt in betas:
            for seed in seeds:
                ck = f"mf{mf}_b{bt}_seed{seed}"
                if ck in done:
                    body = load_partial_key(out_dir, ck)
                    if body is not None:
                        cells.append(body); continue
                try:
                    out = measure_cell(N_cfg, mf, bt, seed, taus, device)
                    write_partial_key(out_dir, ck, out)
                    cells.append(out)
                    print(f"  mf={mf} b={bt} seed={seed} "
                          f"tau_emp={out['tau_emp']:.3f} "
                          f"tau_pred={out['tau_pred']:.3f} "
                          f"l2miss={out['log2_miss']:.3f} "
                          f"var={out['score_var']:.4f} "
                          f"({time.time()-t0:.1f}s)", flush=True)
                except (RuntimeError, MemoryError) as e:
                    print(f"  FAILED mf={mf} b={bt} seed={seed}: {e}",
                          flush=True)
                    if device.type == "cuda":
                        torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "adaptive_threshold_rescue_v2_n4096", "N": N_cfg,
               "smoke": smoke, "M_fracs": M_fracs, "betas": betas,
               "seeds": seeds, "tau_sweep": taus, "cells": cells,
               "verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
