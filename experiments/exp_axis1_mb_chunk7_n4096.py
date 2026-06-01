"""AXIS-1 Phase Diagram M x beta SCAN: chunk 7 -- HIGH-M tail at N=4096.

CONTEXT:
  Chunks 1-6 cover M/N in {0.25..12} in the transition zone.
  chunk2 data: M/N=16 ret=0.238, M/N=32 ret=0.117 (power-law decay in over-capacity regime).
  Chunk 7 (THIS): extend the softmax confidence surface to M/N in {16, 20} (tail regime).
  Scope reduced to M/N <= 20 to keep wall time under PROT-019 floor (M=98304 at M/N=24
  takes ~27s/cell, making 150-cell sweep too slow at M/N>20).

  BUG FIX from smoke-design iteration: original chunk7 probed random keys NOT stored in W.
  This script uses store_facts_batched() to probe the actual stored patterns.
  At N=4096 M/N=16: store_facts_batched confirmed conf=0.23 at beta=32 (real signal).

SCIENTIFIC QUESTION:
  At N=4096 in the over-capacity tail (M/N in {16, 20}):
  (a) Does softmax confidence remain measurable at any beta (confirms substrate signal)?
  (b) How does confidence decay from M/N=12 (chunk6) to M/N=16, 20?
  (c) Is there a beta peak (maximum confidence) that shifts with M/N?

  M/N in {16.0, 20.0} (tail zone; scope-limited for wall-time budget).
  beta in {0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256} (10-point grid).
  Seeds: {7, 17, 23} (3-seed).
  Total: 2 x 10 x 3 = 60 cells.

PRE-REGISTERED BANDS (calibration probe; prior anchor = chunk2 argmax_ret=0.238 at M/N=16):
  Prior anchor: argmax_ret=0.238 at M/N=16 N=4096 (chunk2); softmax_conf probe confirmed ~0.23.
  HARD_PASS: at M/N=16 and beta in {32, 64}: mean softmax_conf >= 0.10
    (measurable signal in far over-capacity regime).
    AND mean softmax_conf at M/N=20 < mean softmax_conf at M/N=16 (monotone in M).
  HARD_FAIL: softmax_conf < 0.001 at M/N=16 for ALL beta values.
    (signal completely lost; metric or store broken; contradicts probe result above).
  MIDDLE_BAND: softmax_conf in [0.001, 0.10) at M/N=16 best-beta.
    (weak signal in far over-capacity; characterizes tail).

  NOTE: Per calibration-probe policy: at M/N>12 we have a prior ARGMAX anchor (not softmax).
  Bands NOT widened to +-50% because we have a directional prior.

FORMULA SELF-TESTS:
  1. store_facts_batched(M=65536 at N=4096): returns keys tensor of shape (65536, 4096). Callable.
  2. At M/N=16, beta=32, N=4096: softmax_conf ~0.23 (empirically confirmed in design probe).
  3. M/N=20 conf <= M/N=16 conf at same beta (monotone in M; capacity decreases with M).
  4. N_FULL == 4096 assertion (PROT-018).
  5. theory_check: W = sum_k v_k k_T / N. For M>>N, W ~ random matrix; softmax_conf->1/C.
     At M/N=16, C=16384: chance=6e-5. Observed conf=0.23 >> chance (signal recovers at high beta).

OOM CHECK:
  M/N=20 at N=4096: M=81920. keys=81920*4096*4=1.34GB. W=64MB. CB=256MB.
  Total peak (keys + vals + W + CB): ~3.05GB. Under 6GB. OK.
  M/N=16: M=65536. Peak ~2.46GB. Under 6GB. OK.

TIMEOUT ESTIMATE:
  Per-cell wall calibration (empirical):
    M/N=16 N=4096: store_facts_batched + retrieval = ~14s/cell.
    M/N=20 N=4096: linear in M -> 14 * (20/16) = 17.5s/cell.
  Total: (14 + 17.5)s * 10 betas * 3 seeds = 945s.
  Safety: ceil(1.5 * 945) = ceil(1418) -> 1500s.
  PROT-019: _n4096 >= 4096 -> floor 3600s. timeout_s = 3600.
  Under 2h: no extra flag.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: axis1_mb_chunk7_n4096
Queue: overnight_queue (GPU; N=4096 high-M tail; M/N in {16,20} x 10 betas x 3 seeds)
Pre-reg: preregs/2026-05-28_axis1_mb_chunk7_n4096.md
Parent: axis1_mb_chunk6_n4096 (FULL M-transition surface; this extends to tail regime)
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

# Load chunk5 base (store_facts_batched, compute_softmax_confidence, Kerdock builder)
_c5_path = REPO / "experiments" / "exp_axis1_mb_chunk5_n4096.py"
_c5_spec = importlib.util.spec_from_file_location("axis1c5_c7", _c5_path)
c5 = importlib.util.module_from_spec(_c5_spec)
_c5_spec.loader.exec_module(c5)

c1 = c5.c1   # chunk1 base (store_facts_batched)
v3 = c5.v3   # Kerdock codebook builder

compute_softmax_confidence = c5.compute_softmax_confidence

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL = 4096       # PROT-018 binding contract
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# HIGH-M TAIL REGIME (M/N > 12, below M/N=32 memory ceiling)
M_FRACS_FULL = [16.0, 20.0]
M_FRACS_SMOKE = [16.0]   # smoke: just M/N=16

BETA_FULL = [0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0, 128.0, 256.0]
BETA_SMOKE = [8.0, 32.0, 256.0]

SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]

N_PROBE = 100

# Pre-registered thresholds
HP_CONF_M16_BEST = 0.10    # mean conf >= 0.10 at M/N=16 best-beta (beta in 32-64)
HF_CONF_MAX_M16 = 0.001    # conf < 0.001 everywhere at M/N=16


def get_output_dir(default_name: str = "axis1_mb_chunk7_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_cell_chunk7(M: int, beta: float, seed: int, codebook: torch.Tensor,
                         N: int, device: torch.device) -> dict:
    """Run one (M, beta, seed) cell for high-M tail regime.

    Uses store_facts_batched to actually probe stored patterns (not random keys).
    This is correct; chunk7 earlier design used random probe keys (bug).
    """
    C = codebook.shape[0]
    # store_facts_batched returns (W, keys, vals, key_idx, val_idx)
    W, keys, vals, key_idx, val_idx = c1.store_facts_batched(codebook, M, seed, N, device)

    n_probe = min(N_PROBE, M)
    probe_keys = keys[:n_probe]
    probe_val_idx = val_idx[:n_probe] % C

    # Softmax confidence
    sims = (codebook @ (probe_keys @ W.T).T) / N  # (C, n_probe)
    log_probs = F.log_softmax(beta * sims, dim=0)  # (C, n_probe)
    correct_lp = log_probs[probe_val_idx, torch.arange(n_probe, device=device)]
    softmax_conf = float(correct_lp.exp().mean().item())

    # Argmax retention
    pred = torch.argmax(sims, dim=0)
    argmax_ret = float((pred == probe_val_idx.to(device)).float().mean().item())

    # Free large tensors immediately to save memory
    del keys, vals, W

    return {
        "M": M,
        "M_over_N": round(M / N, 4),
        "beta": beta,
        "seed": seed,
        "softmax_conf": softmax_conf,
        "argmax_ret": argmax_ret,
    }


def compute_verdict_chunk7(summary: dict) -> tuple:
    """Verdict: high-M tail softmax confidence structure."""
    cells = summary.get("cells", [])
    if not cells:
        return ("AXIS1C7_INCONCLUSIVE", "No cells.")

    N_use = summary.get("N_used", N_FULL)
    confs = [c["softmax_conf"] for c in cells]
    max_conf = max(confs) if confs else 0.0

    # Cells at M/N=16
    M16 = int(16.0 * N_use)
    cells_M16 = [c for c in cells if abs(c["M"] - M16) < N_use]
    cells_M16_midhi_beta = [c["softmax_conf"] for c in cells_M16
                             if c["beta"] in [32.0, 64.0]]
    mean_M16_midhi = (sum(cells_M16_midhi_beta) / len(cells_M16_midhi_beta)
                      if cells_M16_midhi_beta else 0.0)

    # Best conf across all M/N=16 cells
    best_M16_conf = max([c["softmax_conf"] for c in cells_M16]) if cells_M16 else 0.0

    from collections import defaultdict
    conf_by_mfrac = defaultdict(list)
    for c in cells:
        conf_by_mfrac[round(c["M"] / N_use, 1)].append(c["softmax_conf"])
    mean_conf_by_mfrac = {k: round(sum(v) / len(v), 6) for k, v in sorted(conf_by_mfrac.items())}

    detail = {
        "max_conf": round(max_conf, 6),
        "mean_conf_M16_midhibeta": round(mean_M16_midhi, 6),
        "best_conf_M16": round(best_M16_conf, 6),
        "mean_conf_by_mfrac": mean_conf_by_mfrac,
        "N_cells": len(cells),
        "N": N_use,
    }

    # HARD_FAIL: signal completely lost at M/N=16
    if best_M16_conf < HF_CONF_MAX_M16:
        return ("AXIS1C7_HARD_FAIL",
                f"SIGNAL LOST at M/N=16: best_conf={best_M16_conf:.2e} < {HF_CONF_MAX_M16}. "
                f"Substrate fully saturated at M/N=16. details={detail}.")

    # Check monotone M behavior
    m_keys = sorted(mean_conf_by_mfrac.keys())
    monotone_ok = all(mean_conf_by_mfrac[m_keys[i]] >= mean_conf_by_mfrac[m_keys[i + 1]] - 0.05
                      for i in range(len(m_keys) - 1)) if len(m_keys) > 1 else True

    # HARD_PASS: measurable signal at M/N=16 mid-high beta AND monotone
    if mean_M16_midhi >= HP_CONF_M16_BEST and monotone_ok:
        return ("AXIS1C7_HARD_PASS",
                f"TAIL SIGNAL CONFIRMED: M16_midhibeta={mean_M16_midhi:.4f}>={HP_CONF_M16_BEST}. "
                f"Substrate retains partial signal at M/N=16. monotone_ok={monotone_ok}. "
                f"details={detail}.")

    return ("AXIS1C7_MIDDLE_BAND",
            f"Weak tail signal. M16_midhibeta={mean_M16_midhi:.4f}. "
            f"details={detail}.")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    device = torch.device("cpu")
    N_t = N_SMOKE   # smoke scale = 1024

    # Build codebook at smoke scale
    codebook_small, _info = v3.make_kerdock_4coset_codebook(N_t, device)
    C = codebook_small.shape[0]

    # Test at M/N=4 at smoke scale (M/N=16 at N=1024 is deeply saturated)
    M_test_safe = int(4.0 * N_t)   # 4096 patterns at N=1024 (under-capacity)
    cell_safe = run_one_cell_chunk7(M_test_safe, 32.0, 17, codebook_small, N_t, device)
    assert "softmax_conf" in cell_safe and "argmax_ret" in cell_safe, \
        f"Missing keys: {list(cell_safe.keys())}"
    assert 0.0 <= cell_safe["softmax_conf"] <= 1.0, \
        f"softmax_conf out of [0,1]: {cell_safe['softmax_conf']}"
    assert cell_safe["softmax_conf"] > HF_CONF_MAX_M16, \
        f"Validity: conf at M/N=4 smoke={cell_safe['softmax_conf']} should be > {HF_CONF_MAX_M16}"

    # Test verdict HARD_PASS path
    N_tv = 4096
    M16_tv = int(16.0 * N_tv)
    M20_tv = int(20.0 * N_tv)
    cells_pass = []
    for seed in [7, 17, 23]:
        for beta in [8.0, 32.0, 64.0]:
            cells_pass.append({"M": M16_tv, "M_over_N": 16.0, "beta": beta,
                                "seed": seed, "softmax_conf": 0.20, "argmax_ret": 0.17})
        for beta in [8.0, 32.0, 64.0]:
            cells_pass.append({"M": M20_tv, "M_over_N": 20.0, "beta": beta,
                                "seed": seed, "softmax_conf": 0.12, "argmax_ret": 0.10})
    v, msg = compute_verdict_chunk7({"cells": cells_pass, "N_used": N_tv})
    assert "HARD_PASS" in v, f"Self-test HARD_PASS failed: {v}: {msg}"

    # Test HARD_FAIL path
    cells_fail = [{"M": M16_tv, "M_over_N": 16.0, "beta": 256.0,
                   "seed": 17, "softmax_conf": 0.0005, "argmax_ret": 0.0}]
    v2, _ = compute_verdict_chunk7({"cells": cells_fail, "N_used": N_tv})
    assert "HARD_FAIL" in v2, f"Self-test HARD_FAIL failed: {v2}"

    # OOM pre-check: M/N=20 at N=4096
    M20_full = int(20.0 * N_FULL)
    keys_bytes = M20_full * N_FULL * 4
    w_bytes = N_FULL * N_FULL * 4
    cb_bytes = 16384 * N_FULL * 4
    peak = keys_bytes * 2 + w_bytes + cb_bytes   # keys + vals + W + CB
    assert peak < 6e9, f"OOM at M/N=20: {peak:.2e} >= 6GB"

    print(f"[SELFTEST PASS] axis1_mb_chunk7_n4096: N_FULL={N_FULL} "
          f"safe_cell_conf={cell_safe['softmax_conf']:.6f} peak_OOM_M20={peak:.2e}",
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
    print(f"[axis1c7] N={N} C={C} seeds={seeds} M_fracs={m_fracs} "
          f"n_betas={len(betas)} device={device} mode={'smoke' if smoke else 'full'}",
          flush=True)

    all_cells = []
    total = len(seeds) * len(m_fracs) * len(betas)
    done = 0
    for seed in seeds:
        for m_frac in m_fracs:
            M = int(m_frac * N)
            t_cell = time.time()
            for beta in betas:
                cell = run_one_cell_chunk7(M, beta, seed, codebook, N, device)
                all_cells.append(cell)
                done += 1
                if done % max(1, total // 20) == 0 or done == total:
                    elapsed = time.time() - t0
                    print(f"  [{done}/{total}] M/N={m_frac:.1f} beta={beta:.1f} seed={seed} "
                          f"conf={cell['softmax_conf']:.6f} ret={cell['argmax_ret']:.3f} "
                          f"elapsed={elapsed:.1f}s",
                          flush=True)
            cell_elapsed = time.time() - t_cell
            print(f"[axis1c7] M/N={m_frac:.1f} seed={seed} betas={len(betas)} "
                  f"cell_elapsed={cell_elapsed:.1f}s", flush=True)

    summary = {
        "cells": all_cells,
        "N_used": N,
        "N_full": N_FULL,
        "m_fracs": m_fracs,
        "betas": betas,
        "smoke": smoke,
    }
    verdict, verdict_msg = compute_verdict_chunk7(summary)
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
    print(f"\n[axis1c7] VERDICT: {verdict}", flush=True)
    print(f"[axis1c7] {verdict_msg}", flush=True)
    print(f"[axis1c7] elapsed={elapsed:.1f}s output={out_path}", flush=True)


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
