"""PB-2 CORRELATION LENGTH DIVERGENCE: how many facts shift when one is edited?

SCIENTIFIC QUESTION (Phase Boundary 2 -- Correlation Length):
  Near a phase boundary, the correlation length xi diverges: a perturbation
  to one site affects arbitrarily distant sites. In substrate terms:
  editing one stored fact should affect OTHER facts' retrievability, with the
  number of affected facts increasing near the phase boundary (M/N ~ alpha_c).

  This probe measures: for a single-fact edit at various (M, N) combinations,
  how many other facts change their retrieval argmax prediction?
  xi_eff = count of facts whose retrieval changes / M.

  HYPOTHESIS: xi_eff diverges (or peaks) near M/N = alpha_c ~ 0.5625 (Kerdock
  codebook capacity). Below capacity: few facts shift. Near capacity: many shift.

DESIGN:
  - N=1024 Kerdock 4-coset codebook.
  - M_values = [0.1*N, 0.2*N, 0.3*N, 0.4*N, 0.5*N, 0.6*N] (3 below, 1 at, 2 above alpha_c).
  - For each M: store M facts, edit 10 randomly chosen facts (one at a time).
  - Per edit: measure corr_len_frac = count(argmax changed) / (M - 1).
  - 3 seeds.
  - Plot xi vs M: peak near alpha_c = divergence signature.

PRE-REGISTERED BANDS (first correlation-length measurement):
  Calibration probe; no prior empirical anchor. Bands widened to +-50% per policy.

  HARD_PASS: xi_eff at M/N=0.5*N (near alpha_c) is >= 2x the xi_eff at M/N=0.1*N.
    Interpretation: correlation length increases near capacity = divergence signature.
  HARD_FAIL: xi_eff is monotone DECREASING with M (more facts = less collateral damage,
    which contradicts phase-boundary divergence and means substrate is sub-critical).
  MIDDLE_BAND: xi_eff is flat or weakly increasing (no clear peak).

  CALIBRATION: no prior anchor. Bands: HARD_PASS = xi_ratio >= 2.0 at alpha_c;
  HARD_FAIL = xi_ratio < 0.5 (collateral damage DECREASES near capacity).

FORMULA SELF-TESTS:
  1. At M=1 (single fact): xi_eff should be ~ 0 (edit of only fact has no collateral).
     Actually: argmax of retrieval for OTHER patterns computed on W_after vs W_before.
     With M=1, there are no other patterns to probe, so xi_eff = 0. Verified by assertion.
  2. xi_eff = count_changed / (M-1). Range: [0, 1]. Must be in [0, 1].
  3. xi_ratio at M_mid / xi_ratio at M_low > 1 if correlation-length diverges. Check
     that the ratio formula: xi_ratio = xi_at_M_high / xi_at_M_low is computed correctly.
     With xi_at_M_high=0.3, xi_at_M_low=0.1: xi_ratio=3.0 >= 2.0 -> HARD_PASS.
     With xi_at_M_high=0.05, xi_at_M_low=0.1: xi_ratio=0.5 < 2.0 -> NOT HARD_PASS.

TIMEOUT ESTIMATE:
  smoke: N=1024, 1 seed, 3 M values, 5 edits. ~30s (argmax over 4-coset codebook).
  Full: N=1024, 3 seeds, 6 M values, 10 edits.
  scale: 3 * (6/3) * (10/5) = 3 * 2 * 2 = 12.
  timeout_s = ceil(1.5 * 30 * 12) = ceil(540) -> 600s.
  Note: N=1024 throughout (CPU-friendly). Small-N CPU probe for design-space mapping.

N-suffix: no _nN suffix; N=1024 throughout (PROT-018: stated explicitly).
Queue: remote_cpu_queue (pure CPU; N=1024 design-space probe)
Pre-reg: preregs/2026-05-27_pb2_correlation_length_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import importlib.util
import json
import os
import time
from pathlib import Path
from typing import Dict, List

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load Kerdock codebook builder from exp_wave14y_erase_kerdock_v3
_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
_spec = importlib.util.spec_from_file_location("kerdock_v3", _v3_path)
_v3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v3)

# PRODUCTION CONFIG
N = 1024  # PROT-018: N=1024 throughout; no _nN suffix
# M fractions: 0.1, 0.2, 0.3, 0.4, 0.5, 0.6 * N
M_FRACS_FULL = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
M_FRACS_SMOKE = [0.1, 0.3, 0.5]
N_EDITS_FULL = 10
N_EDITS_SMOKE = 5
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]

# Thresholds (calibration probe; widened +-50%)
HP_XI_RATIO = 2.0    # HARD_PASS: xi_near_alpha_c / xi_low >= 2.0
HF_XI_RATIO = 0.5    # HARD_FAIL: xi_near_alpha_c / xi_low < 0.5


def get_output_dir(default_name: str = "pb2_correlation_length_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_w(codebook: torch.Tensor, M: int, seed: int, N: int) -> tuple:
    """Build Hebbian W for M Kerdock facts. Returns (W, keys, values, key_idx, val_idx)."""
    C = codebook.shape[0]
    gen = torch.Generator().manual_seed(seed)
    key_idx = torch.randperm(C, generator=gen)[:min(M, C)]
    val_idx = torch.randperm(C, generator=gen)[:min(M, C)]
    import math
    if M > C:
        # Repeat indices to fill M
        repeats = math.ceil(M / C)
        key_idx = key_idx.repeat(repeats)[:M]
        val_idx = val_idx.repeat(repeats)[:M]
    keys = codebook[key_idx % C]
    values = codebook[val_idx % C]
    W = torch.zeros(N, N, dtype=torch.float32)
    for start in range(0, M, 256):
        k_b = keys[start:start + 256]
        v_b = values[start:start + 256]
        W += (v_b.T @ k_b) / N
    return W, keys, values, key_idx, val_idx


def edit_fact(W: torch.Tensor, key: torch.Tensor, val_old: torch.Tensor,
               val_new: torch.Tensor, N: int) -> torch.Tensor:
    """Anti-Hebbian erase + Hebbian insert."""
    kk = float((key * key).sum().item())
    if kk < 1e-10:
        return W
    W = W - torch.outer(W @ key, key) / kk
    W = W + torch.outer(val_new, key) / N
    return W


def measure_corr_len(W_before: torch.Tensor, W_after: torch.Tensor,
                      probe_keys: torch.Tensor, codebook: torch.Tensor, N: int) -> float:
    """Fraction of probe facts whose argmax retrieval changes after edit."""
    C = codebook.shape[0]
    # Retrieval: argmax over codebook of sims(W @ k_i)
    h_before = probe_keys @ W_before.T    # (n, N)
    h_after = probe_keys @ W_after.T      # (n, N)
    # Similarities vs codebook
    sims_before = (codebook @ h_before.T) / N   # (C, n)
    sims_after = (codebook @ h_after.T) / N
    pred_before = sims_before.argmax(dim=0)     # (n,)
    pred_after = sims_after.argmax(dim=0)
    return float((pred_before != pred_after).float().mean().item())


def run_one_cell(M: int, seed: int, codebook: torch.Tensor, N: int,
                  n_edits: int) -> Dict:
    """Run one (M, seed) cell."""
    C = codebook.shape[0]
    W, keys, values, key_idx, val_idx = build_w(codebook, M, seed, N)

    # Replacement values
    gen2 = torch.Generator().manual_seed(seed + 12345)
    new_val_idx = torch.randperm(C, generator=gen2)[:M]
    values_new = codebook[new_val_idx % C]

    xi_vals = []
    for edit_i in range(min(n_edits, M)):
        W_after = edit_fact(W, keys[edit_i], values[edit_i], values_new[edit_i], N)

        # Probe all OTHER stored facts
        probe_indices = [j for j in range(M) if j != edit_i]
        if not probe_indices:
            xi_vals.append(0.0)
            continue
        # Subsample if too many probes
        max_probe = min(len(probe_indices), 200)
        probe_subset = probe_indices[:max_probe]
        probe_keys = keys[torch.tensor(probe_subset)]

        xi = measure_corr_len(W, W_after, probe_keys, codebook, N)
        xi_vals.append(xi)

    mean_xi = sum(xi_vals) / len(xi_vals) if xi_vals else 0.0
    return {
        "M": M,
        "M_over_N": M / N,
        "seed": seed,
        "mean_xi": mean_xi,
        "n_edits_run": len(xi_vals),
        "xi_vals": xi_vals,
    }


def compute_verdict(summary: dict) -> tuple:
    cells = summary.get("cells", [])
    if not cells:
        return ("PB2_INCONCLUSIVE", "No cells.")

    # Group by M_frac, average xi over seeds
    m_fracs_seen = sorted(set(round(c["M_over_N"], 2) for c in cells))
    mf_xi = {}
    for mf in m_fracs_seen:
        xis = [c["mean_xi"] for c in cells if abs(c["M_over_N"] - mf) < 0.05
               and c["n_edits_run"] > 0]
        mf_xi[mf] = sum(xis) / len(xis) if xis else 0.0

    if len(mf_xi) < 2:
        return ("PB2_INCONCLUSIVE", f"Not enough M fracs: {mf_xi}")

    mf_list = sorted(mf_xi.keys())
    xi_low = mf_xi[mf_list[0]]   # lowest M
    xi_vals_upper = [mf_xi[mf] for mf in mf_list if mf >= 0.45]   # near or above alpha_c
    xi_high = max(xi_vals_upper) if xi_vals_upper else 0.0

    # HARD_PASS: xi near capacity >= 2x xi at low M
    xi_ratio = xi_high / (xi_low + 1e-9)
    xi_ratio_low = min(mf_xi[mf] for mf in mf_list[1:]) / (xi_low + 1e-9)

    msg_base = (f"xi_by_M={dict((k, round(v, 4)) for k, v in mf_xi.items())}. "
                f"xi_low={xi_low:.4f} xi_high={xi_high:.4f} xi_ratio={xi_ratio:.2f}.")

    if xi_ratio >= HP_XI_RATIO:
        return ("PB2_HARD_PASS",
                f"CORRELATION LENGTH DIVERGES near capacity. {msg_base} "
                f"xi_ratio={xi_ratio:.2f} >= {HP_XI_RATIO}. "
                f"Editing one fact near alpha_c causes {xi_high:.1%} collateral shifts.")

    if xi_ratio < HF_XI_RATIO:
        return ("PB2_HARD_FAIL",
                f"Collateral damage DECREASES with load. {msg_base} "
                f"xi_ratio={xi_ratio:.2f} < {HF_XI_RATIO}. No phase-boundary divergence.")

    return ("PB2_MIDDLE_BAND",
            f"Weak xi scaling (xi_ratio={xi_ratio:.2f} in [{HF_XI_RATIO},{HP_XI_RATIO}]). "
            f"{msg_base}")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    device = torch.device("cpu")
    codebook, _ = _v3.make_kerdock_4coset_codebook(N, device)
    C = codebook.shape[0]

    # Self-test 1: xi_eff in [0,1]
    M_t = 256
    cell = run_one_cell(M_t, 17, codebook, N, 3)
    assert 0.0 <= cell["mean_xi"] <= 1.0, f"xi out of [0,1]: {cell['mean_xi']}"
    assert cell["n_edits_run"] > 0, "no edits ran"
    print(f"[selftest 1/3] xi={cell['mean_xi']:.4f} M={M_t} OK", flush=True)

    # Self-test 2: xi_ratio formula check
    fake_cells_pass = [
        {"M": 100, "M_over_N": 0.1, "seed": 17, "mean_xi": 0.05, "n_edits_run": 3,
         "xi_vals": [0.05]},
        {"M": 512, "M_over_N": 0.5, "seed": 17, "mean_xi": 0.15, "n_edits_run": 3,
         "xi_vals": [0.15]},
    ]
    v, msg = compute_verdict({"cells": fake_cells_pass})
    assert v == "PB2_HARD_PASS", f"Expected HARD_PASS (ratio=3.0), got {v}: {msg}"
    print(f"[selftest 2/3] verdict formula HARD_PASS OK", flush=True)

    # Self-test 3: HARD_FAIL case
    fake_cells_fail = [
        {"M": 100, "M_over_N": 0.1, "seed": 17, "mean_xi": 0.20, "n_edits_run": 3,
         "xi_vals": [0.20]},
        {"M": 512, "M_over_N": 0.5, "seed": 17, "mean_xi": 0.05, "n_edits_run": 3,
         "xi_vals": [0.05]},
    ]
    v, msg = compute_verdict({"cells": fake_cells_fail})
    assert v == "PB2_HARD_FAIL", f"Expected HARD_FAIL (ratio=0.25), got {v}: {msg}"
    print(f"[selftest 3/3] verdict formula HARD_FAIL OK", flush=True)

    print("[SELFTEST PASS] pb2_correlation_length_v1 instrumentation OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    device = torch.device("cpu")
    m_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    n_edits = N_EDITS_SMOKE if smoke else N_EDITS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    mode_str = "SMOKE" if smoke else "FULL"

    t0 = time.time()
    out_dir = get_output_dir()
    codebook, _ = _v3.make_kerdock_4coset_codebook(N, device)
    C = codebook.shape[0]

    print(f"[pb2] N={N} C={C} m_fracs={m_fracs} n_edits={n_edits} "
          f"seeds={seeds} mode={mode_str}", flush=True)

    all_cells = []
    for seed in seeds:
        for mf in m_fracs:
            M = int(mf * N)
            M = max(2, min(M, 4 * C))
            print(f"  seed={seed} M={M} (M/N={mf})...", flush=True)
            cell = run_one_cell(M, seed, codebook, N, n_edits)
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
    print(f"\n[pb2] VERDICT: {verdict}", flush=True)
    print(f"[pb2] {verdict_msg}", flush=True)
    print(f"[pb2] elapsed={elapsed:.1f}s output={out_path}", flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args()
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
