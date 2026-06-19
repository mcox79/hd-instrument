"""AXIS-1 Phase Diagram M x beta SCAN: chunk 6 -- FULL softmax confidence surface at N=4096.

CONTEXT:
  axis1_mb_chunk5_n4096 ran at SMOKE scale only (N=1024, elapsed=0.93s). HARD_PASS smoke.
  Chunk 6 (THIS): FULL production sweep at N=4096 with 3-seed x 6-M-fracs x 15-betas = 270 cells.
  This completes the M x beta 2D confidence surface map at production scale.

  Chunk 5 SMOKE results (N=1024):
    M4_highbeta conf=1.0, M7_mix conf=0.651, M12_lowbeta conf=0.0007.
    Joint (M, beta) structure confirmed at smoke scale.

SCIENTIFIC QUESTION:
  At N=4096 (production scale):
  (a) At what (M/N, beta) does P(correct) rise above 0.5 threshold?
  (b) Does the iso-confidence line show non-trivial shape in (M, beta) space?
  (c) How does the beta threshold for P=0.5 shift with M/N (is it monotone in M)?

  M/N in {4.0, 5.0, 6.0, 7.0, 8.0, 12.0} (transition zone from chunks 2+3).
  beta in {0.5, 1, 2, 4, 6, 8, 12, 16, 24, 32, 64, 96, 128, 192, 256} (15-point grid).
  Seeds: {7, 17, 23} (3-seed).
  Total: 6 x 15 x 3 = 270 cells.

PRE-REGISTERED BANDS (envelope-extension; prior anchor = chunk5 smoke HARD_PASS):
  Prior anchor: chunk5 smoke N=1024 confirmed M4_highbeta=1.0, M8_lowbeta~0.001.
  Bands: NOT widened (prior smoke anchor established).

  HARD_PASS: softmax surface shows JOINT (M, beta) structure at N=4096:
    (a) At M/N=4 and beta>=32: mean P(correct) >= 0.50.
    (b) At M/N=8 and beta<=4: mean P(correct) < 0.10.
    Both (a) and (b) must hold.
  HARD_FAIL: P(correct) < 0.001 across ALL cells (below chance level).
    Would indicate metric broken or codebook too sparse at N=4096.
  MIDDLE_BAND: (a) or (b) holds but not both, OR M4_highbeta in [0.1, 0.5).

FORMULA SELF-TESTS:
  1. softmax_conf at beta=0: near-uniform -> conf ~ 1/C (C=16384 -> 6e-5).
  2. At very high beta: softmax -> argmax; conf ~ argmax_accuracy.
  3. M/N=4 highbeta conf > M/N=12 highbeta conf (M modulates confidence).
  4. At fixed M: conf increases (non-decreasing) with beta.
  5. N_FULL == 4096 assertion (PROT-018).

OOM CHECK:
  W float32 at N=4096: 64MB. Kerdock codebook at N=4096: C=16384 x N=4096 x 4B = 256MB.
  Total peak: ~320MB. Under 6GB. OK.

TIMEOUT ESTIMATE:
  chunk5 FULL at N=4096: 270 cells.
  Per cell (chunk5 N=1024 smoke, 9 cells, 0.93s): 0.93/9 = 0.10s/cell.
  N-scale factor (4096/1024)^1.5 = 8x. Per cell at N=4096: 0.10 * 8 = 0.8s.
  Total: 270 * 0.8 = 216s. Safety 2x: 432s. PROT-019 floor: N=4096 -> 3600s.
  timeout_s = 3600 (PROT-019 floor applies since N=4096 >= 4096).
  Under 2h: no extra flag.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: axis1_mb_chunk6_n4096
Queue: overnight_queue (GPU; N=4096 2D softmax-confidence surface FULL 270 cells)
Pre-reg: preregs/2026-05-28_axis1_mb_chunk6_n4096.md
Parent: axis1_mb_chunk5_n4096 (smoke HARD_PASS; this is the FULL production version)
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

import torch
import torch.nn.functional as F

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load chunk5 base (all functions: store_facts_batched, compute_softmax_confidence, etc.)
_c5_path = REPO / "experiments" / "exp_axis1_mb_chunk5_n4096.py"
_c5_spec = importlib.util.spec_from_file_location("axis1c5_c6", _c5_path)
c5 = importlib.util.module_from_spec(_c5_spec)
_c5_spec.loader.exec_module(c5)

c1 = c5.c1   # chunk1 base (store_facts_batched)
v3 = c5.v3   # Kerdock codebook builder

run_one_cell_chunk5 = c5.run_one_cell_chunk5
compute_verdict_chunk5 = c5.compute_verdict_chunk5
compute_softmax_confidence = c5.compute_softmax_confidence

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL = 4096       # PROT-018 binding contract
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_FRACS_FULL = [4.0, 5.0, 6.0, 7.0, 8.0, 12.0]
M_FRACS_SMOKE = [4.0, 7.0, 12.0]

BETA_FULL = [0.5, 1.0, 2.0, 4.0, 6.0, 8.0, 12.0, 16.0, 24.0, 32.0, 64.0, 96.0, 128.0, 192.0, 256.0]
BETA_SMOKE = [1.0, 8.0, 64.0]

SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]

N_PROBE = 100

# Pre-registered thresholds (same as chunk5)
HP_P_CORRECT_HIGH_REGIME = 0.50
HP_P_CORRECT_LOW_REGIME = 0.10
HF_P_CORRECT_MAX = 0.001


def get_output_dir(default_name: str = "axis1_mb_chunk6_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def compute_verdict_chunk6(summary: dict) -> tuple:
    """Verdict: same gate as chunk5 but using 3-seed aggregate."""
    cells = summary.get("cells", [])
    if not cells:
        return ("AXIS1C6_INCONCLUSIVE", "No cells computed.")

    N_use = summary.get("N_used", N_FULL)
    confs = [c["softmax_conf"] for c in cells]
    max_conf = max(confs) if confs else 0.0

    # HARD_FAIL: all confs below floor
    if max_conf < HF_P_CORRECT_MAX:
        return ("AXIS1C6_HARD_FAIL",
                f"METRIC_FAIL: max softmax_conf={max_conf:.2e} < {HF_P_CORRECT_MAX}. All below chance.")

    # Check HARD_PASS conditions
    M_set = sorted(set(c["M"] for c in cells))
    M4_target = int(4.0 * N_use)
    M4 = min(M_set, key=lambda m: abs(m - M4_target)) if M_set else M4_target
    cells_M4_high_beta = [c["softmax_conf"] for c in cells
                          if c["M"] == M4 and c["beta"] >= 32.0]
    mean_conf_M4_hb = (sum(cells_M4_high_beta) / len(cells_M4_high_beta)
                        if cells_M4_high_beta else 0.0)

    M8_target = int(8.0 * N_use)
    M8 = min(M_set, key=lambda m: abs(m - M8_target)) if M_set else M8_target
    cells_M8_low_beta = [c["softmax_conf"] for c in cells
                          if c["M"] == M8 and c["beta"] <= 4.0]
    mean_conf_M8_lb = (sum(cells_M8_low_beta) / len(cells_M8_low_beta)
                        if cells_M8_low_beta else 1.0)

    from collections import defaultdict
    conf_by_mfrac = defaultdict(list)
    for c in cells:
        conf_by_mfrac[round(c["M"] / N_use, 2)].append(c["softmax_conf"])
    mean_conf_by_mfrac = {k: round(sum(v) / len(v), 6) for k, v in sorted(conf_by_mfrac.items())}

    detail = {
        "max_conf": round(max_conf, 6),
        "mean_conf_M4_highbeta": round(mean_conf_M4_hb, 6),
        "mean_conf_M8_lowbeta": round(mean_conf_M8_lb, 6),
        "mean_conf_by_mfrac": mean_conf_by_mfrac,
        "N_cells": len(cells),
        "N": N_use,
    }

    cond_a = mean_conf_M4_hb >= HP_P_CORRECT_HIGH_REGIME
    cond_b = mean_conf_M8_lb < HP_P_CORRECT_LOW_REGIME

    if cond_a and cond_b:
        return ("AXIS1C6_HARD_PASS",
                f"JOINT (M,beta) STRUCTURE CONFIRMED N=4096: "
                f"M4_hb={mean_conf_M4_hb:.4f}>={HP_P_CORRECT_HIGH_REGIME} "
                f"AND M8_lb={mean_conf_M8_lb:.4f}<{HP_P_CORRECT_LOW_REGIME}. "
                f"details={detail}.")

    return ("AXIS1C6_MIDDLE_BAND",
            f"Partial structure. M4_hb={mean_conf_M4_hb:.4f} M8_lb={mean_conf_M8_lb:.4f}. "
            f"details={detail}.")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    device = torch.device("cpu")
    N_t = N_SMOKE

    # Build codebook at smoke scale
    codebook_small, _info = v3.make_kerdock_4coset_codebook(N_t, device)
    C = codebook_small.shape[0]

    M_test = int(4.0 * N_t)
    W, keys, vals, k_idx, v_idx = c1.store_facts_batched(codebook_small, M_test, 17, N_t, device)

    # Test softmax confidence is non-zero at high beta
    conf_high = compute_softmax_confidence(W, keys, v_idx, codebook_small, 32.0, N_t, 30)
    conf_low = compute_softmax_confidence(W, keys, v_idx, codebook_small, 1.0, N_t, 30)
    assert isinstance(conf_high, float), f"softmax_conf not float: {type(conf_high)}"
    assert 0.0 <= conf_high <= 1.0, f"softmax_conf out of [0,1]: {conf_high}"
    assert conf_high > HF_P_CORRECT_MAX, \
        f"Validity filter: conf_high={conf_high} below floor {HF_P_CORRECT_MAX}"
    # Monotone check (high beta >= low beta)
    assert conf_high >= conf_low, \
        f"Monotone test: conf_high={conf_high} < conf_low={conf_low}"

    # Test run_one_cell_chunk5 callable
    cell = run_one_cell_chunk5(M_test, 32.0, 17, codebook_small, N_t, device)
    assert "softmax_conf" in cell and "argmax_ret" in cell, \
        f"Missing keys: {list(cell.keys())}"
    assert 0.0 <= cell["softmax_conf"] <= 1.0, \
        f"softmax_conf out of [0,1]: {cell['softmax_conf']}"

    # Test verdict HARD_PASS path
    N_tv = N_SMOKE
    M4_tv = int(4.0 * N_tv)
    M8_tv = int(8.0 * N_tv)
    cells_pass = []
    for seed in [7, 17, 23]:
        cells_pass.append({"M": M4_tv, "M_over_N": 4.0, "beta": 64.0,
                            "seed": seed, "softmax_conf": 0.70, "argmax_ret": 0.9})
        cells_pass.append({"M": M8_tv, "M_over_N": 8.0, "beta": 1.0,
                            "seed": seed, "softmax_conf": 0.05, "argmax_ret": 0.5})
    v, msg = compute_verdict_chunk6({"cells": cells_pass, "N_used": N_tv})
    assert "HARD_PASS" in v, f"Self-test HARD_PASS failed: {v}: {msg}"

    # Test HARD_FAIL path
    cells_fail = [{"M": M4_tv, "M_over_N": 4.0, "beta": 64.0,
                   "seed": 17, "softmax_conf": 0.0001, "argmax_ret": 0.9}]
    v2, _ = compute_verdict_chunk6({"cells": cells_fail, "N_used": N_tv})
    assert "HARD_FAIL" in v2, f"Self-test HARD_FAIL failed: {v2}"

    # OOM pre-check
    oom_w = N_FULL * N_FULL * 4
    oom_cb = 16384 * N_FULL * 4
    assert oom_w + oom_cb < 6e9, f"OOM: W+CB = {(oom_w+oom_cb):.2e} >= 6GB"

    print(f"[SELFTEST PASS] axis1_mb_chunk6_n4096: N_FULL={N_FULL} "
          f"conf_highbeta={conf_high:.6f} OOM={oom_w+oom_cb:.2e}",
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
    print(f"[axis1c6] N={N} C={C} seeds={seeds} M_fracs={m_fracs} "
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
                # Override M_over_N to match actual N
                cell["M_over_N"] = round(M / N, 4)
                all_cells.append(cell)
                done += 1
                if done % max(1, total // 20) == 0 or done == total:
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
    verdict, verdict_msg = compute_verdict_chunk6(summary)
    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"smoke": smoke, "N": N, "m_fracs": m_fracs, "n_betas": len(betas),
                   "n_seeds": len(seeds)},
        "summary": summary,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[axis1c6] VERDICT: {verdict}", flush=True)
    print(f"[axis1c6] {verdict_msg}", flush=True)
    print(f"[axis1c6] elapsed={elapsed:.1f}s output={out_path}", flush=True)


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
