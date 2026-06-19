"""T1.7: Retrieval explainability -- counterfactual probe smoke.

SCIENTIFIC QUESTION:
  "If atom X is removed from W, how much does the retrieval score change?"
  Claim: counterfactual score-delta matches per-atom contribution within
  5% relative error.

  Algebraic identity: W = sum_i k_i v_i^T / N
  W_minus_i = W - k_i v_i^T / N
  s_without_i = q^T W_minus_i target / N  = s_total - c_i
  So: delta_i = s_total - s_without_i = c_i  (exactly, by linearity)
  Claim: |delta_i - c_i| / max(|s_total|, 1e-9) <= 0.05

PRE-REGISTERED BANDS (smoke IS the primary test):
  HARD-PASS: counterfactual delta matches c_i within 5% relative error
             in >= 4/5 atom probes per trial, >= 4/5 trials.
  HARD-FAIL: error > 20% in majority of probes.
  MIDDLE: between HP and HF.

  No prior empirical anchor: bands widened per calibration-probe policy.
  Theoretical prediction: relative error ~ float32 epsilon / |s_total| ~0.
  HP 5% relative is 50000x more lenient than theory.

DESIGN:
  N=1024, M in {64, 128}, 5 trials, 5 atom probes per trial, 1 seed.
  Pure CPU. Expected wall: <5s.

PROT-018: no _nN suffix (N not primary axis). Production N=1024 stated here.
TIMEOUT ESTIMATE:
  Wall < 5s. PROT-019 floor for CPU: 3600s.
  timeout_s = 3600.

FORMULA SELF-TESTS:
  1. Linearity: W_minus_i vs W delta exact at N=8 M=4.
  2. Relative error formula: rel_err = |delta-c| / |s_total|.
  3. HP threshold 0.05 >> float32_eps = 1e-7.

Anchor: retrieval_explainability_counterfactual_probe_smoke_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_retrieval_explainability_counterfactual_probe_smoke_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# --- Config ---
N = 1024
M_GRID = [64, 128]
N_TRIALS = 5
N_ATOM_PROBES = 5
SEED = 23

# Pre-registered thresholds
HP_REL_ERR = 0.05      # relative error <= 5% for HARD-PASS
HF_REL_ERR = 0.20      # relative error >= 20% for HARD-FAIL
HP_MIN_PROBE_FRAC = 4  # out of N_ATOM_PROBES passing per trial
HP_MIN_TRIALS = 4      # out of N_TRIALS passing


def get_output_dir(name: str = "retrieval_explainability_counterfactual_probe_smoke_v1") -> Path:
    n = os.environ.get("HDLAB_EXP_NAME", name)
    d = REPO / "data" / f"exp_{n}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def measure_cell(N_use: int, M: int, seed: int) -> Dict:
    """Measure counterfactual probe delta vs per-atom contribution."""
    g = torch.Generator().manual_seed(seed)
    codebook_raw = torch.sign(torch.randn(M, N_use, generator=g))
    codebook_raw[codebook_raw == 0] = 1.0
    codebook = codebook_raw.float()

    # Hebbian W = sum_i k_i v_i^T / N
    key_idx = torch.arange(M)
    val_idx = (key_idx + 1) % M
    keys = codebook[key_idx]   # M x N
    vals = codebook[val_idx]   # M x N
    W = (keys.T @ vals) / N_use   # N x N

    trial_results = []
    for trial in range(N_TRIALS):
        g_trial = torch.Generator().manual_seed(seed + trial * 1000)
        q_raw = torch.sign(torch.randn(N_use, generator=g_trial))
        q_raw[q_raw == 0] = 1.0
        q = q_raw.float()
        target_val = vals[0]

        # Total score
        s_total = float((q @ W @ target_val).item() / N_use)

        # Per-atom contributions c_i
        q_dot_ki = (q @ keys.T)           # M
        vtgt_dot_vi = (target_val @ vals.T)  # M
        contribs = (q_dot_ki * vtgt_dot_vi) / (N_use * N_use)  # M

        # Counterfactual: for N_ATOM_PROBES atoms, compute score without atom i
        # W_minus_i = W - k_i v_i^T / N
        # s_without_i = q^T W_minus_i target / N = s_total - c_i (exact)
        atom_probe_errors = []
        probe_atom_indices = torch.arange(min(N_ATOM_PROBES, M))
        for atom_idx in probe_atom_indices.tolist():
            k_i = keys[atom_idx]   # N
            v_i = vals[atom_idx]   # N
            W_minus_i = W - torch.outer(k_i, v_i) / N_use
            s_without_i = float((q @ W_minus_i @ target_val).item() / N_use)
            delta_counterfactual = s_total - s_without_i
            c_i_predicted = float(contribs[atom_idx].item())
            err_abs = abs(delta_counterfactual - c_i_predicted)
            denom = max(abs(s_total), 1e-9)
            rel_err = err_abs / denom
            atom_probe_errors.append({
                "atom_idx": atom_idx,
                "c_i":      round(c_i_predicted, 8),
                "delta_cf": round(delta_counterfactual, 8),
                "rel_err":  round(rel_err, 8),
                "pass":     rel_err <= HP_REL_ERR,
            })

        n_pass = sum(1 for a in atom_probe_errors if a["pass"])
        trial_results.append({
            "trial":          trial,
            "s_total":        round(s_total, 6),
            "n_atoms_pass":   n_pass,
            "n_atoms_probed": len(atom_probe_errors),
            "max_rel_err":    round(max(a["rel_err"] for a in atom_probe_errors), 8),
            "mean_rel_err":   round(
                sum(a["rel_err"] for a in atom_probe_errors) / len(atom_probe_errors), 8),
            "atom_probes":    atom_probe_errors,
            "trial_pass":     n_pass >= HP_MIN_PROBE_FRAC,
        })

    return {"M": M, "seed": seed, "N": N_use, "ok": True, "trials": trial_results}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("REXCF_INCONCLUSIVE", "no cells")

    ok_cells = [c for c in cells if c.get("ok")]
    if not ok_cells:
        return ("REXCF_INCONCLUSIVE", "all cells failed")

    all_trials = []
    for c in ok_cells:
        all_trials.extend(c["trials"])

    if not all_trials:
        return ("REXCF_INCONCLUSIVE", "no trials")

    n_trial_pass = sum(1 for t in all_trials if t["trial_pass"])
    all_rel_errs = [t["max_rel_err"] for t in all_trials]
    max_rel_err = max(all_rel_errs)
    mean_rel_err = sum(all_rel_errs) / len(all_rel_errs)

    n_hf_trials = sum(1 for t in all_trials
                      if t["max_rel_err"] >= HF_REL_ERR)
    majority = len(all_trials) // 2 + 1

    detail = (
        f"N={N} M_grid={[c['M'] for c in ok_cells]} "
        f"n_trials={len(all_trials)} n_trial_pass={n_trial_pass} "
        f"max_rel_err={max_rel_err:.2e} mean_rel_err={mean_rel_err:.2e}"
    )

    if n_hf_trials >= majority:
        return ("REXCF_HARD_FAIL",
                f"COUNTERFACTUAL_FAILS n_hf_trials={n_hf_trials}/{len(all_trials)}. " + detail)
    if n_trial_pass >= HP_MIN_TRIALS:
        return ("REXCF_HARD_PASS",
                f"COUNTERFACTUAL_VALIDATED n_trial_pass={n_trial_pass}/{len(all_trials)}. "
                + detail)
    return ("REXCF_MIDDLE_BAND",
            f"PARTIAL n_trial_pass={n_trial_pass}/{len(all_trials)}. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at smoke scale.

    Formula self-tests:
    1. Counterfactual delta = c_i exactly (linearity) at N=8 M=4.
    2. Relative error formula: rel_err = |delta-c| / |s_total|.
    3. HP 5% >> theoretical epsilon (1e-7).
    4. Live smoke: all metrics non-null at N=1024 M=64.
    5. Verdict gates correct.
    """
    # Formula self-test 1: exact algebra N=8 M=4
    N_t, M_t = 8, 4
    g = torch.Generator().manual_seed(1)
    k = torch.sign(torch.randn(M_t, N_t, generator=g)).float()
    k[k == 0] = 1.0
    v = torch.sign(torch.randn(M_t, N_t, generator=g)).float()
    v[v == 0] = 1.0
    W_t = (k.T @ v) / N_t
    q_t = torch.sign(torch.randn(N_t, generator=g)).float()
    q_t[q_t == 0] = 1.0
    target_v = v[0]
    s_total_t = float((q_t @ W_t @ target_v).item() / N_t)
    q_dot_k = (q_t @ k.T)
    vtgt_dot_v = (target_v @ v.T)
    c = (q_dot_k * vtgt_dot_v) / (N_t * N_t)
    # Test atom 0 counterfactual
    W_m0 = W_t - torch.outer(k[0], v[0]) / N_t
    s_without_0 = float((q_t @ W_m0 @ target_v).item() / N_t)
    delta_cf = s_total_t - s_without_0
    c_0 = float(c[0].item())
    rel_err_t = abs(delta_cf - c_0) / max(abs(s_total_t), 1e-9)
    assert rel_err_t < HP_REL_ERR, (
        f"selftest formula-1 FAIL: rel_err={rel_err_t:.2e} >= HP={HP_REL_ERR}")
    print(f"[selftest] formula-1 counterfactual delta rel_err={rel_err_t:.2e} PASS",
          flush=True)

    # Formula self-test 2: HP 5% >> float32 epsilon
    assert HP_REL_ERR > 1e-5, f"HP_REL_ERR={HP_REL_ERR} too tight"
    print(f"[selftest] formula-2 HP_REL_ERR={HP_REL_ERR:.0%} >> float32_eps PASS",
          flush=True)

    # Formula self-test 3: live smoke
    cell = measure_cell(N, 64, 42)
    assert cell["ok"], f"selftest live smoke FAIL: {cell}"
    assert len(cell["trials"]) > 0, "validity filter eliminated all trials"
    t0_ = cell["trials"][0]
    assert t0_["max_rel_err"] is not None, "max_rel_err null"
    assert not math.isnan(t0_["max_rel_err"]), "max_rel_err NaN"
    assert t0_["n_atoms_probed"] >= 1, "n_atoms_probed = 0"
    assert t0_["max_rel_err"] < HP_REL_ERR, (
        f"live smoke max_rel_err={t0_['max_rel_err']:.2e} >= HP={HP_REL_ERR}")
    print(f"[selftest] live smoke N={N} M=64 max_rel_err={t0_['max_rel_err']:.2e} PASS",
          flush=True)

    # Formula self-test 4: verdict gates
    fake_hp = [{"M": M_v, "seed": SEED, "N": N, "ok": True, "trials": [
        {"trial": i, "s_total": 1.0, "n_atoms_pass": N_ATOM_PROBES,
         "n_atoms_probed": N_ATOM_PROBES, "max_rel_err": 1e-6, "mean_rel_err": 1e-6,
         "atom_probes": [], "trial_pass": True}
        for i in range(N_TRIALS)
    ]} for M_v in M_GRID]
    v, msg = compute_verdict(fake_hp)
    assert "HARD_PASS" in v, f"HP gate failed: {v} {msg}"
    print(f"[selftest] formula-4a HP gate PASS: {v}", flush=True)

    fake_hf = [{"M": M_v, "seed": SEED, "N": N, "ok": True, "trials": [
        {"trial": i, "s_total": 1.0, "n_atoms_pass": 0,
         "n_atoms_probed": N_ATOM_PROBES, "max_rel_err": 0.50, "mean_rel_err": 0.50,
         "atom_probes": [], "trial_pass": False}
        for i in range(N_TRIALS)
    ]} for M_v in M_GRID]
    v, msg = compute_verdict(fake_hf)
    assert "HARD_FAIL" in v, f"HF gate failed: {v} {msg}"
    print(f"[selftest] formula-4b HF gate PASS: {v}", flush=True)

    print("[selftest] retrieval_explainability_counterfactual_probe_smoke_v1 ALL PASS",
          flush=True)


_instrumentation_selftest()


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    out_dir = get_output_dir()
    t0 = time.time()
    print(f"[run] retrieval_explainability_counterfactual_probe_smoke_v1 "
          f"N={N} M_grid={M_GRID} n_trials={N_TRIALS} n_atom_probes={N_ATOM_PROBES} "
          f"seed={SEED} [COUNTERFACTUAL_PROBE algebraic delta test]",
          flush=True)

    cells: List[Dict] = []
    for M in M_GRID:
        cell = measure_cell(N, M, SEED)
        cells.append(cell)
        for t in cell["trials"]:
            print(f"  M={M} trial={t['trial']} n_pass={t['n_atoms_pass']}/{t['n_atoms_probed']} "
                  f"max_rel_err={t['max_rel_err']:.2e} "
                  f"trial_pass={t['trial_pass']} "
                  f"({time.time()-t0:.2f}s)", flush=True)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor":    "retrieval_explainability_counterfactual_probe_smoke_v1",
        "N":         N, "M_grid": M_GRID, "seed": SEED,
        "cells":     cells, "verdict": verdict, "verdict_msg": vm,
        "elapsed_s": elapsed,
    }
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s", flush=True)


if __name__ == "__main__":
    main()
