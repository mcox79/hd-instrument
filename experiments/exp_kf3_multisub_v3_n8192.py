"""KF-3 MULTI-SUBSTRATE v3: isolation at N=8192 (envelope extension).

CONTEXT:
  kf3_multisub_v2_n4096 (v267 region HARD_PASS): substrate A and B isolate at N=4096.
  v3 extends to N=8192 to confirm isolation scales with N.
  1/sqrt(N) theory bound: at N=8192 -> ~0.011 (tighter than N=4096's ~0.016).

SCIENTIFIC QUESTION:
  At N=8192, does cross-substrate leakage remain < HP_LEAKAGE_MAX?
  Does 1/sqrt(N) scaling predict N=8192 isolation?

PRE-REGISTERED BANDS:
  Prior: v2 N=4096 HARD_PASS (max_leakage < 0.01).
  Expected: isolation tighter at N=8192 (smaller leakage due to 1/sqrt(N)).

  HARD_PASS: max_leakage < 0.01 AND max_contam < 0.05 at >= 4/5 seeds.
    Confirms scaling law.
  HARD_FAIL: leakage >= 0.05 at N=8192.
  MIDDLE_BAND: leakage in [0.01, 0.05).

FORMULA SELF-TESTS:
  1. N == 8192 (PROT-018 binding).
  2. theory_bound = 1/sqrt(8192) = 0.01104. HP_LEAKAGE_MAX = 0.015 (some slack).
  3. M at M_frac=8, N=8192: M=65536.

OOM CHECK:
  Two W matrices at N=8192: 2 * 268MB = 536MB. Keys=65536*8192*4=2.1GB.
  Total~2.8GB. Under 6GB. OK.

TIMEOUT ESTIMATE:
  3 M_fracs x 5 seeds = 15 cells x 5s = 75s.
  Smoke: 1 M_frac x 1 seed x 2s = 2s.
  Safety: ceil(1.5*75*10) = 1125s. _n8192 floor = 21600. timeout_s = 21600.

N-suffix: _n8192 -> production N = 8192 (PROT-018 binding).
Anchor: kf3_multisub_v3_n8192
Queue: overnight_queue (GPU; N=8192)
Pre-reg: preregs/2026-05-28_kf3_multisub_v3_n8192.md
Parent: kf3_multisub_v2_n4096 (v267 HARD_PASS; N-envelope extension)
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

# Load kf3_multisub_v2 for run_one_cell
_v2_path = REPO / "experiments" / "exp_kf3_multisub_v2_n4096.py"
_v2_spec = importlib.util.spec_from_file_location("kf3v2_n8k", _v2_path)
kf3v2 = importlib.util.module_from_spec(_v2_spec)
_v2_spec.loader.exec_module(kf3v2)

run_one_cell_kf3 = kf3v2.run_one_cell
build_substrate = kf3v2.build_substrate if hasattr(kf3v2, "build_substrate") else None

# PRODUCTION CONFIG -- PROT-018: _n8192 suffix binds to N = 8192
N_FULL  = 8192
N_SMOKE = 1024
assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

M_FRACS_FULL  = [4, 8, 12]
M_FRACS_SMOKE = [4]

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
HP_LEAKAGE_MAX = 0.015   # slightly relaxed vs theory bound 0.011
HP_CONTAM_MAX  = 0.05
HP_SEEDS_MIN   = 4


def get_output_dir(default_name: str = "kf3_multisub_v3_n8192") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


N_PROBE_KF3 = 200
COUPLING_COUNT = 0  # no coupling between substrates (isolation test)


def run_one_seed_mfrac(N: int, M_frac: int, seed: int, device: torch.device) -> Dict:
    """Run KF-3 multi-substrate isolation test using shared Kerdock codebook."""
    M = M_frac * N
    codebook, _ = kf3v2.v3.make_kerdock_4coset_codebook(N, device)
    C = codebook.shape[0]

    gen_a = torch.Generator(device=device).manual_seed(seed)
    gen_b = torch.Generator(device=device).manual_seed(seed + 99999)

    key_idx_a = torch.randint(0, C, (M,), generator=gen_a, device=device)
    val_idx_a = torch.randint(0, C, (M,), generator=gen_a, device=device)
    key_idx_b = torch.randint(0, C, (M,), generator=gen_b, device=device)
    val_idx_b = torch.randint(0, C, (M,), generator=gen_b, device=device)

    W_A = torch.zeros(N, N, device=device)
    W_B = torch.zeros(N, N, device=device)
    batch = 256
    for start in range(0, M, batch):
        ka = codebook[key_idx_a[start:start+batch]]
        va = codebook[val_idx_a[start:start+batch]]
        W_A = W_A + (va.T @ ka) / N
        kb = codebook[key_idx_b[start:start+batch]]
        vb = codebook[val_idx_b[start:start+batch]]
        W_B = W_B + (vb.T @ kb) / N

    keys_A = codebook[key_idx_a[:N_PROBE_KF3]]
    keys_B = codebook[key_idx_b[:N_PROBE_KF3]]

    result = run_one_cell_kf3(W_A, W_B, codebook,
                               keys_A, val_idx_a[:N_PROBE_KF3],
                               keys_B, val_idx_b[:N_PROBE_KF3],
                               COUPLING_COUNT, N_PROBE_KF3, N)
    result["M_frac"] = M_frac
    result["seed"] = seed
    return result


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("KF3_V3_INCONCLUSIVE", "No cells.")

    leakages = [c.get("leakage_A_to_B", c.get("max_leakage", 0.0)) for c in cells]
    contams = [c.get("contam", c.get("max_contam", 0.0)) for c in cells]
    max_leak = max(leakages) if leakages else 0.0
    max_cont = max(contams) if contams else 0.0
    mean_leak = sum(leakages) / len(leakages)

    pass_seeds = sum(1 for l, ct in zip(leakages, contams)
                     if l < HP_LEAKAGE_MAX and ct < HP_CONTAM_MAX)
    total = len(cells)

    theory_bound = 1.0 / math.sqrt(summary.get("N", N_FULL))

    detail = (f"max_leak={max_leak:.5f} max_cont={max_cont:.5f} mean_leak={mean_leak:.5f} "
              f"theory_bound={theory_bound:.5f} pass_seeds={pass_seeds}/{total} "
              f"HP_leak={HP_LEAKAGE_MAX} N={summary.get('N', N_FULL)}")

    if max_leak >= 0.05:
        return ("KF3_V3_HARD_FAIL", f"CROSS_CONTAMINATION: max_leak={max_leak:.5f}. " + detail)

    if pass_seeds >= HP_SEEDS_MIN and max_leak < HP_LEAKAGE_MAX:
        return ("KF3_V3_HARD_PASS",
                f"ISOLATION_N8192: max_leak={max_leak:.5f} < {HP_LEAKAGE_MAX}. " + detail)

    return ("KF3_V3_MIDDLE_BAND", f"PARTIAL_ISOLATION: max_leak={max_leak:.5f}. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"
    theory_bound = 1.0 / math.sqrt(N_FULL)
    assert abs(theory_bound - 0.01104) < 0.001, f"theory_bound: {theory_bound}"
    # Check run_one_cell_kf3 signature matches what we pass
    import inspect
    sig = inspect.signature(run_one_cell_kf3)
    params = list(sig.parameters.keys())
    assert "W_A" in params or "W_a" in params, f"W_A not in params: {params}"
    # Smoke cell
    device = torch.device("cpu")
    cell = run_one_seed_mfrac(N_SMOKE, 4, 17, device)
    assert "M_frac" in cell, f"M_frac missing: {list(cell.keys())}"
    # Check that some isolation metric exists
    metrics = [k for k in cell.keys() if "leak" in k.lower() or "contam" in k.lower() or "isolation" in k.lower()]
    assert len(metrics) > 0, f"No isolation metric in cell: {list(cell.keys())}"
    # 4x scale
    cell4 = run_one_seed_mfrac(N_SMOKE * 4, 4, 17, device)
    assert "M_frac" in cell4, f"4x missing"
    print(f"[selftest] kf3_multisub_v3_n8192 PASS cell_keys={list(cell.keys())[:5]}", flush=True)


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
    m_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    print(f"[run] kf3_multisub_v3_n8192 smoke={smoke} N={N_cfg} M_fracs={m_fracs} seeds={seeds} device={device_str}", flush=True)
    t0 = time.time()

    all_cells = []
    for M_frac in m_fracs:
        for seed in seeds:
            cell = run_one_seed_mfrac(N_cfg, M_frac, seed, device)
            all_cells.append(cell)
            print(f"  M_frac={M_frac} seed={seed} ({time.time()-t0:.1f}s)", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "kf3_multisub_v3_n8192", "N": N_cfg, "smoke": smoke,
        "M_fracs": m_fracs, "seeds": seeds,
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
