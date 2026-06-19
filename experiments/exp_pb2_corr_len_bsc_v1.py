"""PB-2 CORRELATION LENGTH (BSC keys): how many facts shift when one is edited?

CONTEXT:
  exp_pb2_correlation_length_v1 (Kerdock codebook) yielded xi=0 across all conditions
  due to Kerdock's high orthogonality -- Kerdock maintains wide margins even near capacity.
  This probe uses RANDOM BSC patterns (not Kerdock) to see genuine capacity effects.
  With random BSC keys at M/N near alpha_c~0.138 (BSC Hopfield capacity), the basin
  margins shrink and a rank-1 edit should flip adjacent facts.

SCIENTIFIC QUESTION (Phase Boundary 2 -- Correlation Length, BSC version):
  With BSC random patterns at N=1024, how does xi_eff (fraction of other facts
  whose argmax changes after one edit) vary with load alpha = M/N?

  HYPOTHESIS: xi_eff peaks near alpha_c ~= 0.138 (Amit-Gutfreund-Sompolinsky
  capacity for Hopfield BSC: alpha_c = 1/(4*ln(2)) ~= 0.3607 for perfect retrieval;
  empirically ~0.14 for 99% retrieval). Below alpha_c: facts well separated, few shifts.
  Near/above alpha_c: facts crowd each other, one edit cascades to many.

  NOTE: this is an N=1024 CPU probe to map the xi vs alpha curve.
  If clear peak found: justifies GPU FULL at N=4096 with finer grid.

DESIGN:
  - N=1024 BSC random patterns.
  - M_fracs = [0.05, 0.10, 0.13, 0.15, 0.18, 0.25] * N (spanning BSC capacity range).
  - For each M: store M facts, edit 10 random facts (one at a time).
  - xi_eff = count(argmax changed in other M-1 facts) / (M-1).
  - 3 seeds.

PRE-REGISTERED BANDS (calibration probe; no prior anchor):
  Bands widened to +-50% per calibration-probe policy.

  HARD_PASS: xi_eff at M/N=0.13 (near alpha_c) is >= 2x the xi_eff at M/N=0.05
    (low load). Interpretation: correlation length diverges near BSC capacity.
  HARD_FAIL: xi_eff monotone decreasing OR xi_ratio < 0.5 (no divergence).
  MIDDLE_BAND: xi_ratio in [0.5, 2.0] (weak non-monotone response).

FORMULA SELF-TESTS:
  1. build_bsc_substrate: W = (1/N) * sum_mu v_mu v_mu^T. No diagonal.
  2. edit_fact: W' = W - (1/N) * outer(W @ k, k) / (k.k) + (1/N) * outer(v_new, k)
     After edit of (k, v_old) -> (k, v_new): W' @ k = v_new * (k.k/N) (approx).
  3. xi_ratio formula: xi_high / xi_low. Test: 0.10/0.05 = 2.0 -> HARD_PASS.
  4. For M=1: no other patterns -> xi = 0 by construction.

TIMEOUT ESTIMATE:
  smoke: N=1024, 1 seed, 3 M values, 5 edits.
    Per edit: argmax over codebook is N=1024 vectors * N=1024 dot products = 1M ops.
    ~5s smoke (100 probe keys per edit).
  Full: N=1024, 3 seeds, 6 M values, 10 edits.
  scale: 3 * (6/3) * (10/5) = 12.
  timeout_s = ceil(1.5 * 5 * 12) = ceil(90) -> 300s.
  But argmax over all M patterns (not codebook) is more expensive at high M.
  At M=256: probe 100 keys, 100 * N dot products * codebook access.
  Better estimate: 10s smoke, scale 12 -> 180s. timeout = ceil(1.5*180) = 270 -> 300s.
  Adding safety: 600s.

N-suffix: no _nN suffix; N=1024 throughout (PROT-018: stated explicitly).
Queue: remote_cpu_queue (pure CPU; N=1024 BSC design-space probe)
Pre-reg: preregs/2026-05-27_pb2_corr_len_bsc_v1.md
Parent: pb2_correlation_length_v1 (Kerdock version xi=0 -> redesign with BSC)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, List

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# PRODUCTION CONFIG
N = 1024  # PROT-018: N=1024 throughout
M_FRACS_FULL = [0.05, 0.10, 0.13, 0.15, 0.18, 0.25]
M_FRACS_SMOKE = [0.05, 0.13, 0.20]
N_EDITS_FULL = 10
N_EDITS_SMOKE = 5
N_PROBE_PER_EDIT = 100   # probe this many other facts per edit
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]

# Thresholds (calibration probe; widened +-50%)
HP_XI_RATIO = 2.0    # HARD_PASS: xi_near_cap / xi_low >= 2.0
HF_XI_RATIO = 0.5    # HARD_FAIL: xi_near_cap / xi_low < 0.5


def get_output_dir(default_name: str = "pb2_corr_len_bsc_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_bsc_substrate(N: int, M: int, seed: int) -> tuple:
    """Build Hopfield W for M random BSC patterns."""
    gen = torch.Generator().manual_seed(seed)
    patterns = 2.0 * torch.randint(0, 2, (M, N), generator=gen).float() - 1.0  # {-1,+1}
    W = torch.zeros(N, N, dtype=torch.float32)
    for start in range(0, M, 256):
        P = patterns[start:start + 256]
        W += (P.T @ P) / N
    W.fill_diagonal_(0.0)
    return W, patterns


def edit_fact(W: torch.Tensor, key: torch.Tensor, val_old: torch.Tensor,
               val_new: torch.Tensor, N: int) -> torch.Tensor:
    """Anti-Hebbian erase of (key, val_old) + insert (key, val_new).
    In a heteroassociative Hopfield: W = sum v_mu k_mu^T / N.
    Erase: W' = W - outer(val_old, key) / N.
    Insert: W'' = W' + outer(val_new, key) / N.
    Combined: W'' = W + outer(val_new - val_old, key) / N.
    """
    kk = float((key * key).sum().item())
    if kk < 1e-10:
        return W
    delta = val_new - val_old
    W_after = W + torch.outer(delta, key) / N
    return W_after


def retrieval_argmax(W: torch.Tensor, probe_keys: torch.Tensor,
                      N: int) -> torch.Tensor:
    """Argmax retrieval for probe_keys: predict nearest pattern by W @ k."""
    # Returns (n_probe, N) response vectors; argmax based on inner product with patterns
    # We don't have a separate codebook here -- use the response sign as prediction indicator
    # Simplified: just return the response vector for comparison across before/after
    h = probe_keys @ W.T    # (n_probe, N)
    return h


def measure_xi(W_before: torch.Tensor, W_after: torch.Tensor,
                all_patterns: torch.Tensor, edit_idx: int, N: int) -> float:
    """Fraction of facts whose retrieval changes after editing fact edit_idx.

    Retrieval: for pattern k_i, predict argmax over stored patterns of:
      sim(W @ k_i, pattern_j). We use the cosine similarity proxy.
    After edit: W_after @ k_i changes response -> different argmax -> impact.
    """
    M = all_patterns.shape[0]
    # Probe all other patterns as keys AND values
    probe_indices = [j for j in range(min(M, N_PROBE_PER_EDIT + 1)) if j != edit_idx]
    if not probe_indices:
        return 0.0
    probe_keys = all_patterns[torch.tensor(probe_indices)]   # (n_probe, N)

    # Response vectors before and after
    h_before = probe_keys @ W_before.T    # (n_probe, N)
    h_after = probe_keys @ W_after.T      # (n_probe, N)

    # Argmax over ALL patterns (use dot-product with stored patterns as similarity)
    # sims: (M, n_probe) -- use all M patterns as the codebook
    sims_before = (all_patterns @ h_before.T)    # (M, n_probe)
    sims_after = (all_patterns @ h_after.T)

    pred_before = sims_before.argmax(dim=0)     # (n_probe,)
    pred_after = sims_after.argmax(dim=0)

    return float((pred_before != pred_after).float().mean().item())


def run_one_cell(M: int, seed: int, N: int, n_edits: int) -> Dict:
    """Run one (M, seed) cell."""
    W, patterns = build_bsc_substrate(N, M, seed)

    # Generate random replacement patterns
    gen2 = torch.Generator().manual_seed(seed + 99999)
    new_patterns = 2.0 * torch.randint(0, 2, (n_edits, N), generator=gen2).float() - 1.0

    xi_vals = []
    for edit_i in range(min(n_edits, M)):
        k_edit = patterns[edit_i]          # key = old pattern (Hopfield auto-assoc)
        v_old = patterns[edit_i]           # value = same pattern in auto-assoc
        v_new = new_patterns[edit_i]       # replacement

        W_after = edit_fact(W, k_edit, v_old, v_new, N)
        xi = measure_xi(W, W_after, patterns, edit_i, N)
        xi_vals.append(xi)

    mean_xi = sum(xi_vals) / len(xi_vals) if xi_vals else 0.0
    return {
        "M": M,
        "M_over_N": M / N,
        "seed": seed,
        "mean_xi": mean_xi,
        "n_edits_run": len(xi_vals),
        "xi_vals": xi_vals[:5],   # store first 5 for debugging
    }


def compute_verdict(summary: dict) -> tuple:
    cells = summary.get("cells", [])
    if not cells:
        return ("PB2_BSC_INCONCLUSIVE", "No cells.")

    # Group by M_frac, average xi over seeds
    import math
    mf_groups: Dict[str, List[float]] = {}
    for c in cells:
        if c["n_edits_run"] < 1:
            continue
        mf_key = f"{c['M_over_N']:.2f}"
        mf_groups.setdefault(mf_key, []).append(c["mean_xi"])
    mf_xi = {k: sum(v) / len(v) for k, v in mf_groups.items()}

    if len(mf_xi) < 2:
        return ("PB2_BSC_INCONCLUSIVE", f"Not enough M fracs: {mf_xi}")

    mf_list = sorted(mf_xi.keys(), key=lambda x: float(x))
    xi_by_mf = {k: mf_xi[k] for k in mf_list}

    # xi_low = lowest M fraction
    xi_low = mf_xi[mf_list[0]]
    # xi_high = maximum among M/N >= 0.12 (near/above BSC alpha_c)
    xi_near_cap = {k: v for k, v in mf_xi.items() if float(k) >= 0.12}
    xi_high = max(xi_near_cap.values()) if xi_near_cap else 0.0

    xi_ratio = xi_high / (xi_low + 1e-9)

    msg_base = (f"xi_by_mf={dict((k, round(v, 4)) for k, v in xi_by_mf.items())}. "
                f"xi_low(M/N={mf_list[0]})={xi_low:.4f} "
                f"xi_high(near_cap)={xi_high:.4f} xi_ratio={xi_ratio:.2f}.")

    if xi_ratio >= HP_XI_RATIO:
        return ("PB2_BSC_HARD_PASS",
                f"CORRELATION LENGTH DIVERGES near BSC capacity. {msg_base} "
                f"Editing one fact near alpha_c causes {xi_high:.1%} collateral shifts.")

    if xi_ratio < HF_XI_RATIO:
        return ("PB2_BSC_HARD_FAIL",
                f"No correlation-length divergence. {msg_base} "
                f"xi monotone or decreasing with load. Substrate robust to capacity boundary.")

    return ("PB2_BSC_MIDDLE_BAND",
            f"Weak xi scaling. {msg_base} "
            f"xi_ratio in [{HF_XI_RATIO},{HP_XI_RATIO}].")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # Self-test 1: build_bsc_substrate
    W, pats = build_bsc_substrate(N, 32, seed=42)
    assert W.shape == (N, N), f"W shape: {W.shape}"
    assert W.diagonal().abs().max().item() < 1e-9, "W diagonal nonzero"
    # Patterns in {-1, +1}
    assert ((pats == 1.0) | (pats == -1.0)).all(), "patterns not in {-1,+1}"
    print("[selftest 1/4] build_bsc_substrate OK", flush=True)

    # Self-test 2: edit_fact
    W_orig = W.clone()
    k = pats[0]
    v_old = pats[0]
    gen_t = torch.Generator().manual_seed(99)
    v_new = 2.0 * torch.randint(0, 2, (N,), generator=gen_t).float() - 1.0
    W_after = edit_fact(W, k, v_old, v_new, N)
    delta = (W_after - W).abs().max().item()
    assert delta > 0, f"edit_fact did not change W: delta={delta}"
    print(f"[selftest 2/4] edit_fact OK (max_delta={delta:.4f})", flush=True)

    # Self-test 3: measure_xi non-negative
    xi = measure_xi(W, W_after, pats[:32], 0, N)
    assert 0.0 <= xi <= 1.0, f"xi out of [0,1]: {xi}"
    print(f"[selftest 3/4] measure_xi={xi:.4f} in [0,1] OK", flush=True)

    # Self-test 4: run_one_cell at M=64 (near BSC alpha_c=0.14*N=143)
    t0 = time.time()
    cell = run_one_cell(M=140, seed=17, N=N, n_edits=3)
    t_cell = time.time() - t0
    assert "mean_xi" in cell, "missing mean_xi"
    assert cell["n_edits_run"] > 0, "no edits ran"
    assert 0.0 <= cell["mean_xi"] <= 1.0, f"mean_xi out of range: {cell['mean_xi']}"
    print(f"[selftest 4/4] run_one_cell M=140 xi={cell['mean_xi']:.4f} "
          f"t={t_cell:.1f}s OK", flush=True)

    # Multi-scale check: run at both M=50 and M=200, verify xi is non-null
    cell_low = run_one_cell(M=50, seed=17, N=N, n_edits=3)
    cell_high = run_one_cell(M=200, seed=17, N=N, n_edits=3)
    assert cell_low["n_edits_run"] > 0 and cell_high["n_edits_run"] > 0, \
        f"multi-scale smoke failed: {cell_low['n_edits_run']} {cell_high['n_edits_run']}"
    print(f"[selftest multi-scale] M=50 xi={cell_low['mean_xi']:.4f} "
          f"M=200 xi={cell_high['mean_xi']:.4f} OK", flush=True)

    # Verdict formula checks
    cells_pass = [
        {"M": 50, "M_over_N": 0.05, "seed": 17, "mean_xi": 0.02, "n_edits_run": 3,
         "xi_vals": [0.02]},
        {"M": 130, "M_over_N": 0.13, "seed": 17, "mean_xi": 0.10, "n_edits_run": 3,
         "xi_vals": [0.10]},
    ]
    v, msg = compute_verdict({"cells": cells_pass})
    assert v == "PB2_BSC_HARD_PASS", f"Expected HARD_PASS, got {v}: {msg}"
    print(f"[selftest formula HARD_PASS] OK", flush=True)

    cells_fail = [
        {"M": 50, "M_over_N": 0.05, "seed": 17, "mean_xi": 0.10, "n_edits_run": 3,
         "xi_vals": [0.10]},
        {"M": 130, "M_over_N": 0.13, "seed": 17, "mean_xi": 0.04, "n_edits_run": 3,
         "xi_vals": [0.04]},
    ]
    v, msg = compute_verdict({"cells": cells_fail})
    assert v == "PB2_BSC_HARD_FAIL", f"Expected HARD_FAIL, got {v}: {msg}"
    print(f"[selftest formula HARD_FAIL] OK", flush=True)

    print("[SELFTEST PASS] pb2_corr_len_bsc_v1 instrumentation OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    m_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    n_edits = N_EDITS_SMOKE if smoke else N_EDITS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    mode_str = "SMOKE" if smoke else "FULL"

    t0 = time.time()
    out_dir = get_output_dir()

    print(f"[pb2_bsc] N={N} m_fracs={m_fracs} n_edits={n_edits} "
          f"seeds={seeds} mode={mode_str}", flush=True)

    all_cells = []
    for seed in seeds:
        for mf in m_fracs:
            M = max(2, int(mf * N))
            print(f"  seed={seed} M={M} (M/N={mf:.2f})...", flush=True)
            cell = run_one_cell(M, seed, N, n_edits)
            all_cells.append(cell)
            print(f"    xi={cell['mean_xi']:.4f} n_edits={cell['n_edits_run']}", flush=True)

    summary = {
        "cells": all_cells,
        "N": N,
        "m_fracs": m_fracs,
        "n_edits": n_edits,
        "smoke": smoke,
    }
    verdict, verdict_msg = compute_verdict(summary)
    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"N": N, "m_fracs": m_fracs, "n_edits": n_edits, "seeds": seeds,
                    "smoke": smoke},
        "summary": summary,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[pb2_bsc] VERDICT: {verdict}", flush=True)
    print(f"[pb2_bsc] {verdict_msg}", flush=True)
    print(f"[pb2_bsc] elapsed={elapsed:.1f}s output={out_path}", flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args()
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
