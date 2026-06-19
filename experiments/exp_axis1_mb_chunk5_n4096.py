"""AXIS-1 Phase Diagram M x beta SCAN: chunk 5 -- SOFTMAX CONFIDENCE SURFACE.

CONTEXT:
  chunks 1-3 at N=4096 COMPLETED (remote).
  KEY INSIGHT: argmax retention is beta-invariant (argmax is a monotone transform; beta
  just scales logits, argmax is scale-invariant). To probe the BETA AXIS, we need a
  beta-sensitive metric: softmax confidence P(correct) = softmax(beta*sims)[val_idx].

  This chunk maps the 2D softmax confidence surface P(M/N, beta) in the transition zone.
  At low beta: P(correct) ~ 1/C (chance=6e-5 for C=16384).
  At high beta: P(correct) ~ argmax accuracy.
  At intermediate beta: joint (M, beta) structure.
  This is the substrate analog of the BPC curve from the byte-LM experiments.

SCIENTIFIC QUESTION (Axis 1 -- softmax confidence surface):
  (a) At what (M/N, beta) does P(correct) rise above chance level significantly?
  (b) Does the iso-confidence line (P=0.5) show a non-trivial shape in (M,beta) space?
  (c) Is there a beta threshold below which P(correct) stays near chance even at low M?

  M/N in {4, 5, 6, 7, 8, 12} (transition zone from chunk2+3).
  beta in {0.5, 1, 2, 4, 6, 8, 12, 16, 24, 32, 64, 96, 128, 192, 256} (15-point grid).
  Seeds: 3. Total: 6x15x3 = 270 cells.
  Metric: mean softmax(beta*sims)[val_idx] (probability of correct answer).

PRE-REGISTERED BANDS:
  Calibration probe (first softmax-confidence surface measurement).
  No prior empirical anchor for this metric. Bands widened to +-50%.

  HARD_PASS: softmax surface shows JOINT (M, beta) structure:
    (a) At M/N=4 and beta>=32: mean P(correct) >= 0.5.
    (b) At M/N=8 and beta<=4: mean P(correct) < 0.10.
    Interpretation: the 2D confidence surface has non-trivial structure on both axes.
  HARD_FAIL: P(correct) < 0.001 across ALL cells (below chance level even at low M/high beta).
    Would indicate codebook is too sparse / metric broken.
  MIDDLE_BAND: P(correct) shows M-dependence but beta-dependence only at extreme beta.

FORMULA SELF-TESTS:
  1. softmax_conf = mean(softmax(beta*sims)[val_idx]). At beta=0: uniform -> conf=1/C.
  2. At very high beta: softmax -> argmax; conf ~ argmax_accuracy.
  3. At M/N=4 and high beta: conf > M/N=12 conf (M modulates confidence).
  4. At fixed M, conf increases monotonically with beta (higher temperature = more confident).
  5. N == 4096 (PROT-018).

OOM CHECK:
  W float32 at N=4096: 64MB. Codebook 16384x4096=256MB. Peak: ~320MB. Under 6GB. OK.

TIMEOUT ESTIMATE:
  6 M values x 15 betas x 3 seeds = 270 cells. Per cell: ~1-2s at N=4096 (sim matrix C*n).
  Sim matrix: C=16384 x n_probe=100 x float32 = 6.5MB per cell. Manageable.
  Total: 270 * 1.5s = 405s. Safety 3x: 1215s.
  PROT-019: _n4096 -> floor 3600s. timeout_s = 3600.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: axis1_mb_chunk5_n4096
Queue: overnight_queue (GPU; N=4096 M-x-beta 2D softmax-confidence surface)
Pre-reg: preregs/2026-05-28_axis1_mb_chunk5_n4096.md
Parent: axis1_mb_chunk3_v1_n4096 (COMPLETED)
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

import torch
import torch.nn.functional as F

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load chunk-1 base (store_facts_batched, Kerdock codebook builder)
_c1_path = REPO / "experiments" / "exp_axis1_mb_chunk1_v1.py"
_c1_spec = importlib.util.spec_from_file_location("axis1c1_c5", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)
v3 = c1.v3  # Kerdock codebook builder

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL = 4096       # PROT-018 binding contract
N_SMOKE = 1024      # smoke scale (Kerdock requires even log2; N=1024 -> log2=10 OK)
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_FRACS_FULL = [4.0, 5.0, 6.0, 7.0, 8.0, 12.0]
M_FRACS_SMOKE = [4.0, 7.0, 12.0]

BETA_FULL = [0.5, 1.0, 2.0, 4.0, 6.0, 8.0, 12.0, 16.0, 24.0, 32.0, 64.0, 96.0, 128.0, 192.0, 256.0]
BETA_SMOKE = [1.0, 8.0, 64.0]

SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]

N_PROBE = 100       # number of stored facts to probe per cell

# Thresholds
HP_P_CORRECT_HIGH_REGIME = 0.50   # P(correct) at M/N=4, beta>=32 -> HARD_PASS
HP_P_CORRECT_LOW_REGIME = 0.10    # P(correct) at M/N=8, beta<=4 -> HARD_PASS requires < this
HF_P_CORRECT_MAX = 0.001          # P(correct) < this everywhere -> HARD_FAIL


def get_output_dir(default_name: str = "axis1_mb_chunk5_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def compute_softmax_confidence(W: torch.Tensor, keys: torch.Tensor,
                                 val_idx: torch.Tensor, codebook: torch.Tensor,
                                 beta: float, N: int, n_probe: int = 100) -> float:
    """Mean softmax probability assigned to correct answer.

    sims (C, n) = codebook @ W @ keys.T / N
    prob_correct = mean_i(softmax(beta * sims[:, i])[val_idx[i]])
    This is the beta-SENSITIVE version of retention.
    """
    C = codebook.shape[0]
    M = keys.shape[0]
    n = min(n_probe, M)
    if n == 0:
        return 0.0
    probe_keys = keys[:n]                      # (n, N)
    probe_val_idx = val_idx[:n] % C             # (n,)

    sims = (codebook @ (probe_keys @ W.T).T) / N  # (C, n)
    # Apply softmax with temperature beta along class axis
    log_probs = F.log_softmax(beta * sims, dim=0)  # (C, n)
    # Extract log_prob of correct class for each probe
    # probe_val_idx shape: (n,); need to gather
    correct_log_probs = log_probs[probe_val_idx,
                                   torch.arange(n, device=W.device)]  # (n,)
    mean_prob = float(correct_log_probs.exp().mean().item())
    return mean_prob


def run_one_cell_chunk5(M: int, beta: float, seed: int,
                         codebook: torch.Tensor, N: int,
                         device: torch.device) -> dict:
    """Run one (M, beta, seed) cell; returns softmax confidence."""
    W, keys, values, key_idx, val_idx = c1.store_facts_batched(codebook, M, seed, N, device)
    softmax_conf = compute_softmax_confidence(W, keys, val_idx, codebook, beta, N, N_PROBE)
    # Also compute argmax retention for reference (beta-invariant)
    argmax_ret = c1.compute_retention(W, keys, val_idx, codebook, beta, N, N_PROBE)
    return {
        "M": M,
        "M_over_N": round(M / N, 4),
        "beta": beta,
        "seed": seed,
        "softmax_conf": softmax_conf,
        "argmax_ret": argmax_ret,
    }


def compute_verdict_chunk5(summary: dict) -> tuple:
    """Verdict: test joint (M, beta) structure in softmax confidence surface."""
    cells = summary.get("cells", [])
    if not cells:
        return ("AXIS1C5_INCONCLUSIVE", "No cells computed.")

    N_use = summary.get("N_used", N_FULL)
    confs = [c["softmax_conf"] for c in cells]
    max_conf = max(confs) if confs else 0.0
    min_conf = min(confs) if confs else 0.0

    # HARD_FAIL: all confs below floor (metric broken)
    if max_conf < HF_P_CORRECT_MAX:
        return ("AXIS1C5_HARD_FAIL",
                f"METRIC_FAIL: max softmax_conf={max_conf:.2e} < {HF_P_CORRECT_MAX}. "
                f"All cells below chance level. Metric or codebook issue.")

    # Check HARD_PASS conditions using nearest-M matching (handles smoke vs full grid)
    # (a) M/N near 4, beta>=32: mean conf >= 0.50
    M_set = sorted(set(c["M"] for c in cells))
    M4_target = int(4.0 * N_use)
    M4 = min(M_set, key=lambda m: abs(m - M4_target)) if M_set else M4_target
    cells_M4_high_beta = [c["softmax_conf"] for c in cells
                          if c["M"] == M4 and c["beta"] >= 32.0]
    mean_conf_M4_hb = (sum(cells_M4_high_beta) / len(cells_M4_high_beta)
                        if cells_M4_high_beta else 0.0)

    # (b) M/N near 8 (or highest tested M), beta<=4: mean conf < 0.10
    M8_target = int(8.0 * N_use)
    M8 = min(M_set, key=lambda m: abs(m - M8_target)) if M_set else M8_target
    cells_M8_low_beta = [c["softmax_conf"] for c in cells
                          if c["M"] == M8 and c["beta"] <= 4.0]
    mean_conf_M8_lb = (sum(cells_M8_low_beta) / len(cells_M8_low_beta)
                        if cells_M8_low_beta else 1.0)

    # Summarize by (M/N, beta) grid
    from collections import defaultdict
    conf_by_M = defaultdict(list)
    for c in cells:
        conf_by_M[round(c["M"] / N_use, 2)].append(c["softmax_conf"])
    mean_conf_by_M = {k: round(sum(v) / len(v), 6) for k, v in sorted(conf_by_M.items())}

    detail = {
        "max_conf": round(max_conf, 6),
        "min_conf": round(min_conf, 6),
        "mean_conf_M4_highbeta": round(mean_conf_M4_hb, 6),
        "mean_conf_M8_lowbeta": round(mean_conf_M8_lb, 6),
        "mean_conf_by_M": mean_conf_by_M,
        "N_cells": len(cells),
    }

    cond_a = mean_conf_M4_hb >= HP_P_CORRECT_HIGH_REGIME
    cond_b = mean_conf_M8_lb < HP_P_CORRECT_LOW_REGIME

    if cond_a and cond_b:
        return ("AXIS1C5_HARD_PASS",
                f"JOINT (M,beta) STRUCTURE: M4_hb={mean_conf_M4_hb:.4f}>={HP_P_CORRECT_HIGH_REGIME} "
                f"AND M8_lb={mean_conf_M8_lb:.4f}<{HP_P_CORRECT_LOW_REGIME}. "
                f"Softmax confidence surface has structure on both M and beta axes. "
                f"details={detail}.")

    return ("AXIS1C5_MIDDLE_BAND",
            f"Partial structure. M4_hb={mean_conf_M4_hb:.4f} M8_lb={mean_conf_M8_lb:.4f}. "
            f"details={detail}.")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Test softmax_confidence formula
    # At beta=0: near-uniform distribution, prob ~ 1/C
    device = torch.device("cpu")
    N_t = N_SMOKE
    codebook_small, _info = v3.make_kerdock_4coset_codebook(N_t, device)
    C = codebook_small.shape[0]

    M_test = int(4.0 * N_t)
    W, keys, vals, k_idx, v_idx = c1.store_facts_batched(codebook_small, M_test, 17, N_t, device)

    # Test softmax conf at high beta (should be higher than low beta)
    conf_high = compute_softmax_confidence(W, keys, v_idx, codebook_small, 32.0, N_t, 30)
    conf_low = compute_softmax_confidence(W, keys, v_idx, codebook_small, 1.0, N_t, 30)
    assert isinstance(conf_high, float), f"softmax_conf not float: {type(conf_high)}"
    assert 0.0 <= conf_high <= 1.0, f"softmax_conf out of [0,1]: {conf_high}"
    assert 0.0 <= conf_low <= 1.0, f"softmax_conf low_beta out of [0,1]: {conf_low}"
    # High beta should give higher conf (more peaked distribution)
    assert conf_high >= conf_low, \
        f"Monotone test failed: conf_high={conf_high} < conf_low={conf_low}"

    # Validity filter: at least 1 cell produces non-zero softmax conf
    assert conf_high > HF_P_CORRECT_MAX, \
        f"Validity filter: softmax_conf={conf_high} below floor {HF_P_CORRECT_MAX}"

    # Test run_one_cell_chunk5 callable
    cell = run_one_cell_chunk5(M_test, 32.0, 17, codebook_small, N_t, device)
    assert "softmax_conf" in cell and "argmax_ret" in cell, \
        f"Missing keys in cell: {list(cell.keys())}"
    assert 0.0 <= cell["softmax_conf"] <= 1.0, \
        f"softmax_conf out of [0,1]: {cell['softmax_conf']}"

    # Test verdict HARD_PASS path
    N_tv = N_SMOKE
    M4_tv = int(4.0 * N_tv)
    M8_tv = int(8.0 * N_tv)
    cells_pass = []
    for seed in [7, 17]:
        # M/N=4, high beta -> high conf
        cells_pass.append({"M": M4_tv, "M_over_N": 4.0, "beta": 64.0,
                            "seed": seed, "softmax_conf": 0.70, "argmax_ret": 0.9})
        # M/N=8, low beta -> low conf
        cells_pass.append({"M": M8_tv, "M_over_N": 8.0, "beta": 1.0,
                            "seed": seed, "softmax_conf": 0.05, "argmax_ret": 0.5})
    v, msg = compute_verdict_chunk5({"cells": cells_pass, "N_used": N_tv})
    assert "HARD_PASS" in v, f"Self-test HARD_PASS failed: {v}: {msg}"

    # Test verdict HARD_FAIL
    cells_fail = [{"M": M4_tv, "M_over_N": 4.0, "beta": 64.0,
                   "seed": 17, "softmax_conf": 0.0001, "argmax_ret": 0.9}]
    v2, _ = compute_verdict_chunk5({"cells": cells_fail, "N_used": N_tv})
    assert "HARD_FAIL" in v2, f"Self-test HARD_FAIL failed: {v2}"

    # OOM pre-check
    oom_bytes = N_FULL * N_FULL * 4
    assert oom_bytes < 6e9, f"OOM: W at N=4096 = {oom_bytes:.2e} >= 6GB"

    print(f"[SELFTEST PASS] axis1_mb_chunk5_n4096: N_FULL={N_FULL} "
          f"conf_high_beta={conf_high:.6f} conf_low_beta={conf_low:.6f} "
          f"monotone=OK OOM={oom_bytes:.2e}",
          flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_SMOKE if smoke else N_FULL
    m_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    betas = BETA_SMOKE if smoke else BETA_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    t0 = time.time()
    out_dir = get_output_dir()
    codebook, _info = v3.make_kerdock_4coset_codebook(N, device)
    C = codebook.shape[0]
    print(f"[axis1c5] N={N} C={C} seeds={seeds} M_fracs={m_fracs} "
          f"n_betas={len(betas)} device={device} mode={'smoke' if smoke else 'full'}",
          flush=True)

    all_cells = []
    total = len(seeds) * len(m_fracs) * len(betas)
    done = 0
    for seed in seeds:
        for m_frac in m_fracs:
            M = int(m_frac * N)
            for beta in betas:
                cell = run_one_cell_chunk5(M, beta, seed, codebook, N, device)
                all_cells.append(cell)
                done += 1
                if done % max(1, total // 10) == 0 or done == total:
                    print(f"  [{done}/{total}] M/N={m_frac:.1f} beta={beta:.1f} seed={seed} "
                          f"conf={cell['softmax_conf']:.6f} argmax_ret={cell['argmax_ret']:.3f}",
                          flush=True)

    summary = {
        "cells": all_cells,
        "N_used": N,
        "N_full": N_FULL,
        "m_fracs": m_fracs,
        "betas": betas,
        "smoke": smoke,
    }
    verdict, verdict_msg = compute_verdict_chunk5(summary)
    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"smoke": smoke, "N": N, "m_fracs": m_fracs, "n_betas": len(betas)},
        "summary": summary,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[axis1c5] VERDICT: {verdict}", flush=True)
    print(f"[axis1c5] {verdict_msg}", flush=True)
    print(f"[axis1c5] elapsed={elapsed:.1f}s output={out_path}", flush=True)


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    p.add_argument("--timeout", type=int, default=3600)
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
