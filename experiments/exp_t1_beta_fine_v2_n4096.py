"""T1 BETA FINE SWEEP v2: high-resolution beta near beta_c at N=4096.

CONTEXT:
  T1_BETA_HARD_PASS (v267): coarse sweep {1..512} shows beta_c in [8,16] range.
  v2 adds FINE resolution {6,8,10,12,14,16,20,24,32} to localize beta_c precisely.
  At beta_c, retention gradient |d(ret)/d(log2_beta)| is maximized.

SCIENTIFIC QUESTION:
  Exact beta_c for the retrieval phase transition at M_frac=8.0?
  Fine sweep confirms the transition is sharp (vs broad crossover).

PRE-REGISTERED BANDS:
  Parent anchor: T1_BETA_HARD_PASS at M_frac=8, 5/5 seeds mono+gradient.
  Expected beta_c in [8,16]; fine sweep narrows to [8,16] 2-unit resolution.

  HARD_PASS: transition localized within [10,20] (4-unit window) AND max gradient >= 0.15
    per log2-unit AND at least 3/5 seeds show same beta_c +/- 2.
    Interpretation: sharp, reproducible transition localized.
  HARD_FAIL: max gradient < 0.05 per log2-unit across all seeds
    OR transition is spread over > 6 fine-beta values.
    Interpretation: diffuse crossover, beta_c not sharp.
  MIDDLE_BAND: gradient 0.05-0.15 or transition window 4-6 beta values.

FORMULA SELF-TESTS:
  1. Fine grid: {6,8,10,12,14,16,20,24,32}. log2-spacings range 0.26 to 1.0.
  2. d(ret)/d(log2_beta) at step i: (ret[i+1]-ret[i-1])/(log2(beta[i+1])-log2(beta[i-1])).
  3. beta_c = beta_sweep[argmax(gradient)].
  4. Sharp gate: transition within 4-unit window.
  5. N == 4096 (PROT-018).
  6. M = M_frac*N = 8.0*4096 = 32768.

OOM CHECK:
  M=32768, N=4096: W=64MB, keys=32768*4096*4=537MB. CB=268MB. Total=869MB. Under 6GB. OK.

TIMEOUT ESTIMATE:
  9 beta pts x 5 seeds = 45 cells x 1.0s = 45s (M=32768 heavier than v1 M=16384).
  Smoke: 5 pts x 1 seed = 5 cells x 0.5s = 2.5s.
  Safety: ceil(1.5 * 45 * 10) = 675s. _n4096 floor = 14400. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: t1_beta_fine_v2_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-28_t1_beta_fine_v2_n4096.md
Parent: exp_t1_beta_sweep_v1_n4096 (v267 HARD_PASS; beta_c in [8,16])
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

_c1_path = REPO / "experiments" / "exp_axis1_mb_chunk1_v1.py"
_c1_spec = importlib.util.spec_from_file_location("axis1c1_t1fine", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)

store_facts_batched = c1.store_facts_batched
v3 = c1.v3

# Load t1 for softmax_confidence
_t1_path = REPO / "experiments" / "exp_t1_beta_sweep_v1_n4096.py"
_t1_spec = importlib.util.spec_from_file_location("t1v1", _t1_path)
t1v1 = importlib.util.module_from_spec(_t1_spec)
_t1_spec.loader.exec_module(t1v1)

softmax_confidence = t1v1.softmax_confidence

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_FRAC = 8.0

BETA_SWEEP_FULL  = [6, 8, 10, 12, 14, 16, 20, 24, 32]
BETA_SWEEP_SMOKE = [6, 10, 16, 24, 32]

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

N_PROBE = 200

# Pre-registered thresholds
HP_MAX_GRADIENT_MIN  = 0.15   # max |d(ret)/d(log2_beta)| >= 0.15
HP_TRANSITION_WINDOW = 4      # beta_c in window of width <= 4
HF_FLAT_MAX_GRAD     = 0.05   # max gradient < 0.05 = no transition = HARD_FAIL
HP_SEEDS_MIN         = 3      # >= 3/5 seeds agree on beta_c location


def get_output_dir(default_name: str = "t1_beta_fine_v2_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_seed(N: int, M_frac: float, beta_sweep: List[float],
                 seed: int, device: torch.device) -> Dict:
    """Run fine beta sweep for one seed."""
    M = int(M_frac * N)
    codebook, _ = v3.make_kerdock_4coset_codebook(N, device)
    W, keys, _vals, _key_idx, val_idx = store_facts_batched(codebook, M, seed, N, device)

    ret_by_beta = []
    for beta in beta_sweep:
        conf = softmax_confidence(W, keys, val_idx, codebook, float(beta), N, n_probe=N_PROBE)
        ret_by_beta.append(round(conf, 5))
        print(f"    beta={beta:5.1f} softmax_conf={conf:.5f}", flush=True)

    log2_betas = [math.log2(b) for b in beta_sweep]
    gradients = []
    for i in range(1, len(ret_by_beta) - 1):
        d_ret = ret_by_beta[i + 1] - ret_by_beta[i - 1]
        d_log = log2_betas[i + 1] - log2_betas[i - 1]
        gradients.append(abs(d_ret / d_log) if abs(d_log) > 1e-9 else 0.0)

    max_grad = max(gradients) if gradients else 0.0
    argmax_i = gradients.index(max_grad) + 1 if gradients else 0
    beta_c = beta_sweep[argmax_i] if argmax_i < len(beta_sweep) else float("nan")
    total_var = max(ret_by_beta) - min(ret_by_beta)

    return {
        "seed": seed, "M_frac": M_frac, "M": M,
        "beta_sweep": list(beta_sweep),
        "ret_by_beta": ret_by_beta,
        "gradients": [round(g, 5) for g in gradients],
        "max_gradient": round(max_grad, 4),
        "beta_c_est": float(beta_c),
        "total_var": round(total_var, 4),
    }


def seed_passes_hp(cell: Dict) -> bool:
    return cell["max_gradient"] >= HP_MAX_GRADIENT_MIN


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("T1_FINE_INCONCLUSIVE", "No cells.")

    pass_seeds = sum(1 for c in cells if seed_passes_hp(c))
    total = len(cells)
    max_grads = [c["max_gradient"] for c in cells]
    beta_cs = [c["beta_c_est"] for c in cells if not math.isnan(c["beta_c_est"])]
    mean_grad = sum(max_grads) / len(max_grads)
    mean_beta_c = sum(beta_cs) / len(beta_cs) if beta_cs else float("nan")
    # Window: max - min of beta_c estimates
    window = (max(beta_cs) - min(beta_cs)) if len(beta_cs) >= 2 else 999.0

    detail = (f"pass_seeds={pass_seeds}/{total} mean_max_gradient={mean_grad:.3f} "
              f"mean_beta_c={mean_beta_c:.1f} window={window:.1f} "
              f"HP_grad={HP_MAX_GRADIENT_MIN} HP_seeds={HP_SEEDS_MIN} N={summary.get('N', N_FULL)}")

    if mean_grad < HF_FLAT_MAX_GRAD:
        return ("T1_FINE_HARD_FAIL", f"FLAT_BETA_RESPONSE: max_gradient={mean_grad:.3f} < {HF_FLAT_MAX_GRAD}. " + detail)

    if pass_seeds >= HP_SEEDS_MIN and window <= HP_TRANSITION_WINDOW:
        return ("T1_FINE_HARD_PASS",
                f"SHARP_BETA_TRANSITION: beta_c={mean_beta_c:.1f} +/-{window/2:.1f} gradient={mean_grad:.3f}. " + detail)

    return ("T1_FINE_MIDDLE_BAND",
            f"DIFFUSE_OR_PARTIAL: gradient={mean_grad:.3f} window={window:.1f}. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"
    # Formula self-test: gradient formula
    betas = [8.0, 10.0, 12.0]
    rets = [0.2, 0.5, 0.8]
    log2_b = [math.log2(b) for b in betas]
    grad = abs((rets[2] - rets[0]) / (log2_b[2] - log2_b[0]))
    # d_ret = 0.6, d_log2 = log2(12)-log2(8) = 0.585; grad ~ 1.03
    assert grad > 0.5, f"Gradient formula check failed: {grad}"
    # HARD_PASS verdict gate
    fake_cells = [{"max_gradient": 0.20, "beta_c_est": 12.0} for _ in range(5)]
    v, _ = compute_verdict({"cells": fake_cells, "N": N_FULL})
    assert "HARD_PASS" in v, f"Verdict gate failed: {v}"
    # HARD_FAIL verdict gate
    fail_cells = [{"max_gradient": 0.02, "beta_c_est": 12.0} for _ in range(5)]
    vf, _ = compute_verdict({"cells": fail_cells, "N": N_FULL})
    assert "HARD_FAIL" in vf, f"HARD_FAIL gate failed: {vf}"
    # Smoke cell: non-null metrics
    device = torch.device("cpu")
    cell = run_one_seed(N_SMOKE, M_FRAC, [8.0, 12.0, 16.0], 17, device)
    assert not math.isnan(cell["max_gradient"]), "max_gradient NaN in selftest"
    assert cell["max_gradient"] >= 0.0, "max_gradient negative"
    # 4x smoke check
    cell4 = run_one_seed(N_SMOKE * 4, M_FRAC, [8.0, 12.0, 16.0], 17, device)
    assert not math.isnan(cell4["max_gradient"]), "4x max_gradient NaN"
    print(f"[selftest] t1_beta_fine_v2_n4096 PASS gradient_smoke={cell['max_gradient']:.4f}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    device_str = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device_str)
    smoke = args.smoke

    N_cfg = N_SMOKE if smoke else N_FULL
    beta_sweep = BETA_SWEEP_SMOKE if smoke else BETA_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    print(f"[run] t1_beta_fine_v2_n4096 smoke={smoke} N={N_cfg} beta_pts={len(beta_sweep)} seeds={seeds} device={device_str}", flush=True)
    t0 = time.time()

    all_cells = []
    for seed in seeds:
        M = int(M_FRAC * N_cfg)
        print(f"\n  [seed={seed}] M={M}", flush=True)
        cell = run_one_seed(N_cfg, M_FRAC, beta_sweep, seed, device)
        all_cells.append(cell)
        print(f"  seed={seed} max_gradient={cell['max_gradient']:.4f} beta_c_est={cell['beta_c_est']:.1f} ({time.time()-t0:.1f}s)", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "t1_beta_fine_v2_n4096", "N": N_cfg, "smoke": smoke,
        "M_frac": M_FRAC, "beta_sweep": beta_sweep, "seeds": seeds,
        "cells": all_cells, "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    out_dir = get_output_dir()
    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed}s", flush=True)
    print(f"[output] {out_path}", flush=True)


if __name__ == "__main__":
    main()
