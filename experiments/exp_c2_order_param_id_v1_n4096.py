"""C2 ORDER PARAMETER IDENTIFICATION v1: basin enumeration across phase boundary at N=4096.

CONTEXT:
  v267 confirmed two-orthogonal-boundary lattice: beta-axis AND codebook-axis.
  C2 is the first direct basin-enumeration probe: how many distinct attractors does
  the substrate visit as beta crosses beta_c (8->16)?

  MECHANISM:
    Store M facts. Run random initializations from codebook. Cluster final states.
    Count distinct attractors = number of clusters (with hamming distance > sqrt(N) apart).
    Track how n_basins changes as beta crosses beta_c.

SCIENTIFIC QUESTION:
  Does basin count increase sharply at beta_c (multi-basin transition)?
  Before beta_c: single attractor (or few). After beta_c: many distinct basins.

PRE-REGISTERED BANDS (calibration probe):
  No prior direct basin-count measurement at this scale.

  HARD_PASS: n_basins at beta=16 >= 2x n_basins at beta=8 at >= 2/3 seeds.
    Interpretation: crossing beta_c increases accessible basins -- confirms first-order
    multi-basin character of the transition.
  HARD_FAIL: n_basins flat (<= 1.1x ratio) across beta sweep.
    Interpretation: no basin proliferation; transition is NOT first-order multi-basin.
  MIDDLE_BAND: ratio 1.1-2.0x (some proliferation, not sharp).

FORMULA SELF-TESTS:
  1. Hamming distance threshold: sqrt(N) for N=4096 -> 64.
  2. Distinct basins: greedy cluster where each new sample with min_dist > threshold
     to all existing centroids starts a new basin.
  3. Basin ratio: n_basins_hi / n_basins_lo where lo=beta=8, hi=beta=16.
  4. M = M_frac * N = 4.0 * 4096 = 16384 (multi-basin regime).
  5. N_INIT = 200 random initializations per (beta, seed).

OOM CHECK:
  M=16384, N=4096: W=64MB. CB=268MB. 200 query vecs=200*4096*4=3.3MB. Total~336MB. OK.

TIMEOUT ESTIMATE:
  Per cell: 200 random init queries per beta, greedy cluster. ~1s per beta.
  5 beta vals x 3 seeds = 15 cells x 1s = 15s.
  Smoke: 3 beta x 1 seed = 3 cells x 0.5s = 1.5s.
  Safety: ceil(1.5*15*10) = 225s. Floor 14400. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: c2_order_param_id_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-28_c2_order_param_id_v1_n4096.md
Parent: t1_beta_sweep_v1_n4096 (v267 HARD_PASS; beta_c confirmed); pred4_hysteresis (first-order multi-basin)
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
_c1_spec = importlib.util.spec_from_file_location("axis1c1_c2", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)

store_facts_batched = c1.store_facts_batched
v3 = c1.v3

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_FRAC = 4.0   # multi-basin regime (well below collapse)

BETA_SWEEP_FULL  = [4.0, 8.0, 12.0, 16.0, 32.0]
BETA_SWEEP_SMOKE = [4.0, 8.0, 16.0]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

N_INIT = 200   # random initialization queries per cell

# Pre-registered thresholds
HP_BASIN_RATIO_MIN  = 2.0    # n_basins(beta=16) / n_basins(beta=8) >= 2x
HF_BASIN_RATIO_MAX  = 1.1    # ratio < 1.1 = flat = HARD_FAIL
HP_SEEDS_MIN        = 2


def get_output_dir(default_name: str = "c2_order_param_id_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def count_basins(W: torch.Tensor, codebook: torch.Tensor,
                 beta: float, N: int, n_init: int, seed: int,
                 device: torch.device) -> int:
    """Count distinct attractors via random codebook queries.

    Each query: pick random codebook row, apply W retrieval, find argmax.
    Cluster final states: greedy clustering with Hamming threshold sqrt(N).
    """
    C = codebook.shape[0]
    gen = torch.Generator(device=device).manual_seed(seed + 9999)
    query_idx = torch.randint(0, C, (n_init,), generator=gen, device=device)
    queries = codebook[query_idx]  # (n_init, N)

    # One-step retrieval: final state index via argmax over codebook
    logits = (codebook @ (queries @ W.T).T) / N * beta  # (C, n_init)
    final_idx = torch.argmax(logits, dim=0)  # (n_init,)

    # Convert to final states
    final_states = codebook[final_idx]  # (n_init, N)

    # Greedy clustering: BSC Hamming distance (but float -- use L2 proxy)
    # Hamming threshold: sqrt(N) * scale ~ 0.5*N for random vectors
    # Use cosine similarity: two attractor states are distinct if cos < 0.9
    threshold_cos = 0.9
    centroids: List[torch.Tensor] = []

    for i in range(n_init):
        state = final_states[i]  # (N,)
        norm_s = state.norm() + 1e-8
        is_new = True
        for c in centroids:
            cos_sim = (state @ c) / (norm_s * (c.norm() + 1e-8))
            if cos_sim.item() > threshold_cos:
                is_new = False
                break
        if is_new:
            centroids.append(state)

    return len(centroids)


def run_one_seed(N: int, M_frac: float, beta_sweep: List[float],
                 seed: int, device: torch.device) -> Dict:
    """Count basins across beta sweep for one seed."""
    M = int(M_frac * N)
    codebook, _ = v3.make_kerdock_4coset_codebook(N, device)
    W, keys, _vals, _key_idx, val_idx = store_facts_batched(codebook, M, seed, N, device)

    n_basins_by_beta = []
    for beta in beta_sweep:
        nb = count_basins(W, codebook, beta, N, N_INIT, seed, device)
        n_basins_by_beta.append(nb)
        print(f"    beta={beta:5.1f} n_basins={nb}", flush=True)

    # Basin ratio: beta=16 / beta=8 (or closest available)
    beta_lo = 8.0
    beta_hi = 16.0
    def get_nb(b):
        # find closest beta in sweep
        idx = min(range(len(beta_sweep)), key=lambda i: abs(beta_sweep[i] - b))
        return n_basins_by_beta[idx]

    nb_lo = get_nb(beta_lo)
    nb_hi = get_nb(beta_hi)
    ratio = nb_hi / max(1, nb_lo)

    return {
        "seed": seed, "M_frac": M_frac, "M": M,
        "beta_sweep": list(beta_sweep),
        "n_basins_by_beta": n_basins_by_beta,
        "nb_lo": nb_lo, "nb_hi": nb_hi,
        "basin_ratio": round(ratio, 3),
    }


def seed_passes_hp(cell: Dict) -> bool:
    return cell["basin_ratio"] >= HP_BASIN_RATIO_MIN


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("C2_INCONCLUSIVE", "No cells.")

    pass_seeds = sum(1 for c in cells if seed_passes_hp(c))
    total = len(cells)
    ratios = [c["basin_ratio"] for c in cells]
    mean_ratio = sum(ratios) / len(ratios)
    mean_nb_hi = sum(c["nb_hi"] for c in cells) / len(cells)
    mean_nb_lo = sum(c["nb_lo"] for c in cells) / len(cells)

    detail = (f"pass_seeds={pass_seeds}/{total} mean_ratio={mean_ratio:.2f} "
              f"mean_nb_lo(b=8)={mean_nb_lo:.1f} mean_nb_hi(b=16)={mean_nb_hi:.1f} "
              f"HP_ratio={HP_BASIN_RATIO_MIN} N={summary.get('N', N_FULL)}")

    if mean_ratio < HF_BASIN_RATIO_MAX:
        return ("C2_HARD_FAIL", f"FLAT_BASIN_COUNT: ratio={mean_ratio:.2f} < {HF_BASIN_RATIO_MAX}. " + detail)

    if pass_seeds >= HP_SEEDS_MIN:
        return ("C2_HARD_PASS",
                f"BASIN_PROLIFERATION: ratio={mean_ratio:.2f}x at beta_c. " + detail)

    return ("C2_MIDDLE_BAND", f"PARTIAL_PROLIFERATION: ratio={mean_ratio:.2f}x. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"
    # Formula self-test: cosine threshold clustering
    # Two identical vectors should cluster together
    device = torch.device("cpu")
    v1 = torch.randn(N_FULL)
    v2 = v1.clone()
    cos = (v1 @ v2) / (v1.norm() * v2.norm())
    assert cos.item() > 0.9, f"Identical vectors cosine < 0.9: {cos}"
    # Two random vectors should NOT cluster
    v3r = torch.randn(N_FULL)
    cos_rnd = (v1 @ v3r) / (v1.norm() * v3r.norm())
    # Random expected ~0.0; should be < 0.9
    assert cos_rnd.item() < 0.9, f"Random vectors cosine too high: {cos_rnd}"
    # Verdict gates
    fake_hp = [{"basin_ratio": 2.5, "nb_lo": 2, "nb_hi": 5} for _ in range(3)]
    v, _ = compute_verdict({"cells": fake_hp, "N": N_FULL})
    assert "HARD_PASS" in v, f"HARD_PASS gate: {v}"
    fake_hf = [{"basin_ratio": 1.0, "nb_lo": 3, "nb_hi": 3} for _ in range(3)]
    vf, _ = compute_verdict({"cells": fake_hf, "N": N_FULL})
    assert "HARD_FAIL" in vf, f"HARD_FAIL gate: {vf}"
    # Smoke cell
    cell = run_one_seed(N_SMOKE, M_FRAC, [4.0, 8.0, 16.0], 17, device)
    assert not math.isnan(cell["basin_ratio"]), "basin_ratio NaN in selftest"
    assert cell["n_basins_by_beta"][0] >= 1, f"0 basins at smoke scale: {cell}"
    # 4x scale
    cell4 = run_one_seed(N_SMOKE * 4, M_FRAC, [4.0, 8.0, 16.0], 17, device)
    assert cell4["n_basins_by_beta"][0] >= 1, f"0 basins at 4x smoke"
    print(f"[selftest] c2_order_param_id_v1_n4096 PASS basin_ratio_smoke={cell['basin_ratio']:.3f}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    import sys as _sys
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        _sys.exit(0)

    device_str = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device_str)
    smoke = args.smoke

    N_cfg = N_SMOKE if smoke else N_FULL
    beta_sweep = BETA_SWEEP_SMOKE if smoke else BETA_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    print(f"[run] c2_order_param_id_v1_n4096 smoke={smoke} N={N_cfg} beta_pts={len(beta_sweep)} seeds={seeds} device={device_str}", flush=True)
    t0 = time.time()

    all_cells = []
    for seed in seeds:
        M = int(M_FRAC * N_cfg)
        print(f"\n  [seed={seed}] M={M}", flush=True)
        cell = run_one_seed(N_cfg, M_FRAC, beta_sweep, seed, device)
        all_cells.append(cell)
        print(f"  seed={seed} basin_ratio={cell['basin_ratio']:.3f} nb_lo={cell['nb_lo']} nb_hi={cell['nb_hi']} ({time.time()-t0:.1f}s)", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "c2_order_param_id_v1_n4096", "N": N_cfg, "smoke": smoke,
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
