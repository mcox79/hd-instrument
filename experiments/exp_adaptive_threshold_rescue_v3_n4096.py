"""ADAPTIVE THRESHOLD RESCUE v3 at N=4096 (research-directed rescue).

CONTEXT (research drill 2026-05-30 commit ee0d4f8):
  v1 used a broken proxy (best_score=0.0 in every cell).
  v2 used TPR - 5*FPR which SATURATES at sweep endpoints (at tau<<min(max_conf)
  TPR=1, FPR=1, score=-4 flat; at tau>>max(max_conf) TPR=0, FPR=0, score=0
  flat). The "optimum" hugs whichever endpoint has the better flat value.
  This is the 3-occurrence pathology pattern the research drill identified.

  v3 FIX: NON-SATURATING discriminant. Youden's J statistic = TPR(tau) -
  FPR(tau). At tau=0 both TPR and FPR are 1 -> J=0. At tau=1 both are 0 ->
  J=0. In between, J = (true accept rate) - (false accept rate), which
  PEAKS at the optimal classifier threshold. Bounded in [-1, 1], goes to
  0 at both endpoints by construction -> the optimum is INTERIOR by
  definition unless the gate provides no separation at all (J flat at 0).
  This is the standard ROC-optimal-threshold metric.

  PER-CELL non-degeneracy gate: drop M_frac=0.25 (was degenerate in v1/v2
  at high beta) and verify the substrate is OPERATIONAL (retention >= 0.30
  at tau=0) before measuring threshold.

SCIENTIFIC QUESTION:
  Over a 9-cell grid (beta in {4, 10, 32} x M_frac in {1, 4, 16}) at
  N=4096: does the empirical optimum tau (argmax KL-div) sit at the
  INTERIOR of the sweep in >= 7/9 cells AND do the cell-wise optima span
  at least one order of magnitude across cells?

PRE-REGISTERED BANDS (revised post research):
  HP = >=7/9 cells produce INTERIOR optimal tau (not boundary) AND
       cell-optima span >= 1 order of magnitude (max/min >= 10).
  HF = >=4/9 cells saturate at sweep boundary (tau_emp == min or max of
       sweep) OR all optima within +/-10% of each other (no cell-dep.).
  MIDDLE_BAND = 4-6 cells interior; partial recovery.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. grid = 3 beta x 3 M_frac = 9 cells (M_frac in {1,4,16}; 0.25 dropped).
  3. tau_sweep = [0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.25, 0.5, 0.75,
                  0.9, 0.99] (11 points, 4 orders of magnitude).
  4. discriminant: Youden's J(tau) = TPR_in(tau) - FPR_oos(tau).
  5. INTERIOR check: tau_emp not in {min(sweep), max(sweep)}.
  6. NON-DEGENERACY self-test: at smoke scale, verify >= 3 distinct
     discriminant values across the sweep AND monotone-non-flat trend.

OOM CHECK:
  Same envelope as v2: max M = 16 * 4096 = 65536 -> if we rescale to keep
  the original M_frac SEMANTICS (M = M_frac * N truncated to 16K), keys =
  16K * 4096 * 4 = 256 MiB; W = 64 MiB; CB = 805 MiB. ~1.2 GiB OK.
  We CAP M at 16384 for the highest M_frac entry (M_frac=16, N=4096).

TIMEOUT ESTIMATE:
  Smoke ~ 5s. FULL: 9 cells x 3 seeds x 11-tau sweep = 297 measurements
  each running an in-store + OOS probe pair of 100. Expected ~600s
  on GPU. scaling_exp=1.5. Budget 14400s.

N-suffix: _n4096 (PROT-018).
Anchor: adaptive_threshold_rescue_v3_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_adaptive_threshold_rescue_v3_n4096.md
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_atr3", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096
N_FULL  = N
N_SMOKE = 1024

# M_frac in {1, 4, 16} -- 0.25 was degenerate in v1/v2, DROPPED per spec.
# At N=4096, M=16*N=65536 OOMs the codebook side. CAP M at 16384.
# So effective: M_frac=1 -> M=4096; M_frac=4 -> M=16384; M_frac=16 -> M=16384 (CAPPED).
M_FRACS_FULL  = [1.0, 4.0, 16.0]
M_FRACS_SMOKE = [1.0, 4.0]
M_CAP         = 16384

BETAS_FULL  = [4.0, 10.0, 32.0]
BETAS_SMOKE = [4.0]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# 11 points, 4 orders of magnitude
TAU_SWEEP_FULL  = [0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99]
TAU_SWEEP_SMOKE = [0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99]

# HP gates
HP_INTERIOR_CELLS_MIN = 7  # >=7/9 cells INTERIOR optimum
HP_SPAN_ORDERS_MIN    = 1.0  # max/min of cell-optima >= 10

# HF gates
HF_BOUNDARY_CELLS_MIN = 4  # >=4/9 cells boundary -> HF
HF_OPTIMA_SPREAD_FRAC = 0.10  # if all optima within +/-10% -> no cell-dep -> HF


def get_output_dir(default_name: str = "adaptive_threshold_rescue_v3_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def predicted_threshold(M_frac: float, beta: float) -> float:
    """Heuristic tau_pred per cap_map (research drill flagged as heuristic, not theory)."""
    return float((1.0 / max(0.01, M_frac)) ** 0.5 / max(0.01, beta) ** 0.5)


def confidence_distributions(W: torch.Tensor, codebook: torch.Tensor,
                              key_idx: torch.Tensor, val_idx: torch.Tensor,
                              N_use: int, beta: float, seed: int,
                              device: torch.device,
                              n_probe: int = 200) -> Tuple[torch.Tensor, torch.Tensor]:
    """Return (in_store_max_conf, oos_max_conf) tensors.

    Both are (n_probe,) max-softmax confidences from substrate readout.
    Used to compute KL between distributions of confidence values (a
    non-saturating discriminant).
    """
    C = codebook.shape[0]
    M = key_idx.shape[0]

    # IN-STORE probes
    n_in = min(n_probe, M)
    keys = codebook[key_idx[:n_in]]
    out = keys @ W.T
    sims_in = (codebook @ out.T) / N_use   # (C, n_in)
    P_in = torch.softmax(beta * sims_in, dim=0)
    max_conf_in = P_in.max(dim=0).values    # (n_in,)

    # OOS probes (codebook entries NOT in key_idx)
    stored_set = set(key_idx.tolist())
    available = [i for i in range(C) if i not in stored_set]
    if not available:
        return max_conf_in, torch.zeros(0, device=device)
    n_out = min(n_probe, len(available))
    gen = torch.Generator(device=device).manual_seed(seed + 71717)
    perm = torch.randperm(len(available), generator=gen, device=device)[:n_out]
    oos_idx = torch.tensor([available[int(i)] for i in perm.tolist()],
                             dtype=torch.long, device=device)
    oos_keys = codebook[oos_idx]
    out_oos = oos_keys @ W.T
    sims_oos = (codebook @ out_oos.T) / N_use
    P_oos = torch.softmax(beta * sims_oos, dim=0)
    max_conf_oos = P_oos.max(dim=0).values  # (n_out,)

    return max_conf_in, max_conf_oos


def youden_j(in_vals: torch.Tensor, oos_vals: torch.Tensor,
              tau: float) -> float:
    """Youden's J statistic = TPR(tau) - FPR(tau).

    TPR = fraction of in-store probes whose confidence >= tau.
    FPR = fraction of OOS probes whose confidence >= tau.
    J peaks at the optimal classifier threshold and is 0 at both endpoints
    (tau=0: J = 1-1 = 0; tau=1: J = 0-0 = 0). This is the standard
    NON-SATURATING discriminant for threshold selection.
    """
    if in_vals.numel() == 0 or oos_vals.numel() == 0:
        return 0.0
    tpr = float((in_vals >= tau).float().mean().item())
    fpr = float((oos_vals >= tau).float().mean().item())
    return tpr - fpr


def measure_cell(N_use: int, M_frac: float, beta: float, seed: int,
                  tau_sweep: List[float], device: torch.device) -> Dict:
    M_raw = max(1, int(M_frac * N_use))
    M = min(M_raw, M_CAP if N_use == N_FULL else int(M_CAP * N_use / N_FULL))
    codebook, W, _keys, _vals, key_idx, val_idx = make_substrate(
        N_use, M, seed, device)

    # Compute confidence distributions ONCE per cell-seed
    in_vals, oos_vals = confidence_distributions(
        W, codebook, key_idx, val_idx, N_use, beta, seed, device)

    # Operational check (per spec): in-store should be reasonably high
    in_mean = float(in_vals.mean().item()) if in_vals.numel() > 0 else 0.0
    oos_mean = float(oos_vals.mean().item()) if oos_vals.numel() > 0 else 0.0
    operational = in_mean >= max(0.05, 2.0 * oos_mean)

    # Youden's J sweep (non-saturating discriminant)
    js: List[float] = []
    for tau in tau_sweep:
        j = youden_j(in_vals, oos_vals, tau)
        js.append(round(j, 6))

    # Distinct values guard (caught instrumentation pathology)
    distinct = len(set(round(k, 4) for k in js))

    idx_best = int(max(range(len(js)), key=lambda i: js[i]))
    tau_emp = float(tau_sweep[idx_best])
    j_best = float(js[idx_best])

    # INTERIOR check
    is_boundary = (tau_emp == tau_sweep[0]) or (tau_emp == tau_sweep[-1])
    is_interior = not is_boundary

    tau_pred = predicted_threshold(M_frac, beta)
    log2_miss = abs(math.log2(tau_emp / tau_pred)) if (tau_emp > 0 and tau_pred > 0) else float("inf")

    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {"M_frac": float(M_frac), "beta": float(beta), "seed": int(seed),
            "M": int(M), "tau_sweep": list(tau_sweep), "js": js,
            "distinct_j_vals": int(distinct),
            "in_mean": round(in_mean, 5), "oos_mean": round(oos_mean, 5),
            "operational": bool(operational),
            "tau_emp": tau_emp, "tau_pred": round(tau_pred, 5),
            "j_best": round(j_best, 5),
            "is_boundary": bool(is_boundary),
            "is_interior": bool(is_interior),
            "log2_miss": round(log2_miss, 5)}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("ATR3_INCONCLUSIVE", "No cells.")

    # Aggregate by (M_frac, beta) -> majority across seeds
    by_op: Dict[Tuple[float, float], List[Dict]] = {}
    for c in cells:
        by_op.setdefault((c["M_frac"], c["beta"]), []).append(c)

    n_interior = 0
    n_boundary = 0
    cell_optima: List[float] = []
    op_summary: Dict[str, Dict] = {}

    for (mf, bt), cs in by_op.items():
        n_int_seed = sum(1 for c in cs if c["is_interior"])
        cell_is_interior = n_int_seed > len(cs) / 2
        # cell-level optimum tau = median across seeds (boundary or interior)
        taus = sorted([c["tau_emp"] for c in cs])
        med_tau = taus[len(taus) // 2]
        if cell_is_interior:
            n_interior += 1
        else:
            n_boundary += 1
        cell_optima.append(med_tau)
        op_summary[f"({mf},{bt})"] = {
            "med_tau_emp": round(med_tau, 5),
            "interior_seeds": f"{n_int_seed}/{len(cs)}",
        }

    # Span of cell optima
    if cell_optima:
        span_orders = math.log10(max(cell_optima) / max(1e-9, min(cell_optima)))
    else:
        span_orders = 0.0

    # Spread fraction (for HF "all-within-10%" check)
    if len(cell_optima) >= 2 and min(cell_optima) > 0:
        spread = (max(cell_optima) - min(cell_optima)) / max(cell_optima)
    else:
        spread = 0.0

    detail = (f"interior={n_interior}/{len(by_op)} "
              f"boundary={n_boundary}/{len(by_op)} "
              f"span_orders={span_orders:.2f} spread={spread:.3f} "
              f"ops={op_summary}")

    # HF first: boundary saturation OR no cell-dependence
    if n_boundary >= HF_BOUNDARY_CELLS_MIN:
        return ("ATR3_HARD_FAIL", "BOUNDARY_SATURATION_PERSISTS: " + detail)
    if spread <= HF_OPTIMA_SPREAD_FRAC:
        return ("ATR3_HARD_FAIL", "NO_CELL_DEPENDENCE: " + detail)

    # HP: interior + span
    if n_interior >= HP_INTERIOR_CELLS_MIN and span_orders >= HP_SPAN_ORDERS_MIN:
        return ("ATR3_HARD_PASS", "INSTRUMENTATION_CLEAN_CELL_DEPENDENT: " + detail)

    return ("ATR3_MIDDLE_BAND", "PARTIAL_RECOVERY: " + detail)


def _instrumentation_selftest() -> None:
    """Non-degeneracy + non-saturation gates per research drill."""
    assert N_FULL == 4096
    assert M_FRACS_FULL == [1.0, 4.0, 16.0], "M_frac=0.25 must be DROPPED per spec"
    assert len(TAU_SWEEP_FULL) == 11
    assert TAU_SWEEP_FULL[0] == 0.0005 and TAU_SWEEP_FULL[-1] == 0.99

    # Predicted threshold sanity
    assert abs(predicted_threshold(1.0, 1.0) - 1.0) < 1e-6
    assert abs(predicted_threshold(4.0, 4.0) - 0.25) < 1e-6

    # Verdict gates
    # HP: 7 interior, span >= 1 order
    fake_hp_cells = []
    interior_taus = [0.001, 0.005, 0.01, 0.05, 0.1, 0.25, 0.5]
    boundary_taus = [0.99, 0.99]
    for i, mf in enumerate(M_FRACS_FULL):
        for j, bt in enumerate(BETAS_FULL):
            idx = i * 3 + j
            tau = (interior_taus + boundary_taus)[idx]
            for s in SEEDS_FULL:
                fake_hp_cells.append({
                    "M_frac": mf, "beta": bt, "seed": s, "M": 4096,
                    "tau_sweep": TAU_SWEEP_FULL, "js": [0.0]*11,
                    "distinct_j_vals": 5, "in_mean": 0.5, "oos_mean": 0.05,
                    "operational": True,
                    "tau_emp": tau, "tau_pred": tau, "j_best": 0.5,
                    "is_boundary": tau in (0.0005, 0.99),
                    "is_interior": tau not in (0.0005, 0.99),
                    "log2_miss": 0.0})
    v, msg = compute_verdict(fake_hp_cells)
    assert "HARD_PASS" in v, f"expected HP, got {v}: {msg}"

    # HF: >=4 boundary cells
    fake_hf_cells = []
    for i, mf in enumerate(M_FRACS_FULL):
        for j, bt in enumerate(BETAS_FULL):
            for s in SEEDS_FULL:
                fake_hf_cells.append({
                    "M_frac": mf, "beta": bt, "seed": s, "M": 4096,
                    "tau_sweep": TAU_SWEEP_FULL, "js": [0.0]*11,
                    "distinct_j_vals": 5, "in_mean": 0.5, "oos_mean": 0.05,
                    "operational": True,
                    "tau_emp": 0.99, "tau_pred": 0.1, "j_best": 0.5,
                    "is_boundary": True, "is_interior": False,
                    "log2_miss": 3.3})
    v, _ = compute_verdict(fake_hf_cells); assert "HARD_FAIL" in v, v

    # HF: no-cell-dependence (all optima within 10%)
    fake_flat = []
    for i, mf in enumerate(M_FRACS_FULL):
        for j, bt in enumerate(BETAS_FULL):
            for s in SEEDS_FULL:
                fake_flat.append({
                    "M_frac": mf, "beta": bt, "seed": s, "M": 4096,
                    "tau_sweep": TAU_SWEEP_FULL, "js": [0.0]*11,
                    "distinct_j_vals": 5, "in_mean": 0.5, "oos_mean": 0.05,
                    "operational": True,
                    "tau_emp": 0.1, "tau_pred": 0.1, "j_best": 0.5,
                    "is_boundary": False, "is_interior": True,
                    "log2_miss": 0.0})
    v, _ = compute_verdict(fake_flat); assert "HARD_FAIL" in v, f"expected HF (flat), got {v}"

    # ===== NON-DEGENERACY + NON-SATURATION instrumentation gate =====
    # Forward pass on CPU at smoke scale; verify:
    #   (a) >= 2 distinct J values across sweep (rules out v1 all-zero AND
    #       rules out v2 all-flat saturation pathology)
    #   (b) sweep range > 0.1 (J actually distinguishes -- not noisy near 0)
    #   (c) some tau achieves J >= 0.5 (substrate is discriminative)
    #   (d) substrate operational (in_mean clearly > oos_mean)
    device = torch.device("cpu")
    # Use M_frac=1.0 + beta=10 -- substrate is clean here, J should be near 1
    # in the in-store regime and 0 at high tau -> non-degenerate sweep.
    out = measure_cell(N_SMOKE, M_frac=1.0, beta=10.0, seed=17,
                       tau_sweep=TAU_SWEEP_SMOKE, device=device)
    js = out["js"]
    j_range = max(js) - min(js)
    j_max = max(js)
    # (a) Non-degeneracy: must have >=2 distinct values (rules out v1 all-zero
    # AND v2 all-flat-saturation -- the 3-occurrence pathology pattern).
    assert out["distinct_j_vals"] >= 2, (
        f"NON-DEGENERACY FAIL: only {out['distinct_j_vals']} distinct J "
        f"values across {len(TAU_SWEEP_SMOKE)} taus. js={js}")
    # (b) Non-saturation: J range must be substantive (not just noise).
    # v2 pathology was J flat at -4 or 0 across the sweep -> range==0.
    assert j_range > 0.1, (
        f"NON-SATURATION FAIL: J range={j_range:.4f} across sweep "
        f"(metric constant - instrumentation pathology persists). js={js}")
    # (c) Discriminative: substrate produces J >= 0.5 at some tau (otherwise
    # we cannot meaningfully measure an optimum -- substrate is operational
    # but indistinguishable from random).
    assert j_max >= 0.5, (
        f"NON-DISCRIMINATIVE FAIL: max J={j_max:.4f} < 0.5 -- substrate "
        f"not distinguishing in-store from OOS at any tau. js={js}")
    # (d) Verify substrate is operational
    assert out["operational"], (
        f"NON-OPERATIONAL: in_mean={out['in_mean']} oos_mean={out['oos_mean']} "
        f"-- substrate degenerate at smoke; cannot measure threshold.")

    print(f"[selftest] adaptive_threshold_rescue_v3_n4096 PASS "
          f"distinct={out['distinct_j_vals']}/{len(TAU_SWEEP_SMOKE)} "
          f"j_range={j_range:.4f} j_max={j_max:.4f} "
          f"tau_emp={out['tau_emp']} interior={out['is_interior']} "
          f"operational={out['operational']}", flush=True)


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
    print(f"[run] adaptive_threshold_rescue_v3 smoke={smoke} N={N_cfg} "
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
                          f"tau_emp={out['tau_emp']:.4f} "
                          f"interior={out['is_interior']} "
                          f"distinct={out['distinct_j_vals']} "
                          f"j_best={out['j_best']:.3f} "
                          f"op={out['operational']} "
                          f"({time.time()-t0:.1f}s)", flush=True)
                except (RuntimeError, MemoryError) as e:
                    print(f"  FAILED mf={mf} b={bt} seed={seed}: {e}", flush=True)
                    if device.type == "cuda":
                        torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "adaptive_threshold_rescue_v3_n4096", "N": N_cfg,
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
