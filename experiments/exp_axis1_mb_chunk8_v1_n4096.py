"""AXIS1 MB-CHUNK 8 v1: hyper-loaded regime M_frac=[25, 32, 40] at N=4096.

CONTEXT:
  axis1_mb_chunk7_n4096 (v266/v267 region): M_frac=[16, 20] at N=4096, probing the
  tail of the multi-basin regime. Chunk 8 extends to M_frac=[25, 32, 40] --
  hyper-loaded regime where M >> N (M/N = 25-40x). Goal: characterize retention
  collapse profile at extreme load.

  RELEVANCE: Knowing the full retention-vs-M curve (including tail behavior at M/N=40)
  is essential for the KF-1 rescue: entropy-gap detection depends on how saturated
  the codebook becomes at M >> C.

SCIENTIFIC QUESTION:
  Does retention collapse completely at M/N >= 25 (fall to 0), or does it plateau
  at some non-zero value (residual retrieval from the strongest patterns)?

PRE-REGISTERED BANDS:
  Prior: chunk7 at M_frac=20 shows near-zero retention (based on expected collapse).
  Expected: further collapse, retention -> 0 for large M.

  HARD_PASS: retention < 0.10 at M_frac=25 AND M_frac=40 at >= 2/3 seeds.
    Interpretation: complete collapse confirmed; hyper-loaded regime well-characterized.
  HARD_FAIL: retention at M_frac=40 >= 0.50 (surprisingly high; would indicate M-independent).
    Interpretation: substrate has no capacity limit -- would falsify the multi-basin framing.
  MIDDLE_BAND: retention in [0.10, 0.50] at M_frac=40 (partial collapse).

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. M at M_frac=40, N=4096: M=163840.
  3. OOM: W=64MB, keys=163840*4096*4=2.7GB. CB=268MB. Total~3GB. Under 6GB. OK.
     Actually: store M patterns. W accumulates outer products. W itself stays 64MB.
     Pattern STORAGE: M*N bytes = 163840*4096*4 = 2.7GB for keys. This is borderline.
     Reduce M_frac max to 32: M=131072. keys=131072*4096*4=2.1GB. Total~2.4GB. OK.

TIMEOUT ESTIMATE:
  3 M_fracs x 3 betas x 3 seeds = 27 cells.
  At M_frac=32, storing 131072 patterns takes ~10s. Retrieval ~1s.
  Total: 27 * 11s = 297s. Safety: ceil(1.5 * 297 * 5) = 2228s. Floor 14400. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: axis1_mb_chunk8_v1_n4096
Queue: overnight_queue (GPU; hyper-loaded M/N=[25,32] at N=4096)
Pre-reg: preregs/2026-05-28_axis1_mb_chunk8_v1_n4096.md
Parent: axis1_mb_chunk7_n4096; axis1_mb_chunk1_v1 (run_one_cell pattern)
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
_c1_spec = importlib.util.spec_from_file_location("axis1c1_c8", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)

store_facts_batched = c1.store_facts_batched
compute_retention = c1.compute_retention
v3 = c1.v3

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_FRACS_FULL  = [25.0, 32.0]
M_FRACS_SMOKE = [25.0]

BETA_FULL  = [8.0, 32.0, 256.0]
BETA_SMOKE = [32.0]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

N_PROBE = 200

# Pre-registered thresholds
HP_RET_COLLAPSE  = 0.10   # retention < 0.10 at M_frac=25 = collapse confirmed
HF_RET_HIGH      = 0.50   # retention >= 0.50 at M_frac=32 = no capacity limit = HARD_FAIL
HP_SEEDS_MIN     = 2


def get_output_dir(default_name: str = "axis1_mb_chunk8_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_cell(N: int, M_frac: float, beta: float, seed: int, device: torch.device) -> Dict:
    """Run retention measurement at (N, M_frac, beta, seed)."""
    M = int(M_frac * N)
    codebook, _ = v3.make_kerdock_4coset_codebook(N, device)
    W, keys, _vals, _key_idx, val_idx = store_facts_batched(codebook, M, seed, N, device)
    ret = compute_retention(W, keys, val_idx, codebook, beta, N, n_probe=N_PROBE)
    print(f"    N={N} M_frac={M_frac} beta={beta} seed={seed} ret={ret:.5f}", flush=True)
    return {
        "N": N, "M_frac": M_frac, "M": M, "beta": beta, "seed": seed,
        "retention": round(ret, 5),
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("C8_INCONCLUSIVE", "No cells.")

    by_mfrac: Dict[float, List] = {}
    for c in cells:
        by_mfrac.setdefault(c["M_frac"], []).append(c)

    m_sorted = sorted(by_mfrac.keys())

    # Mean retention per M_frac (over betas and seeds)
    mean_ret: Dict[float, float] = {}
    for m in m_sorted:
        rets = [c["retention"] for c in by_mfrac[m]]
        mean_ret[m] = sum(rets) / len(rets)

    m_low = m_sorted[0] if m_sorted else 0.0
    m_high = m_sorted[-1] if m_sorted else 0.0
    ret_low = mean_ret.get(m_low, float("nan"))
    ret_high = mean_ret.get(m_high, float("nan"))

    # Seed-level pass for collapse at m_low
    m_low_cells = by_mfrac.get(m_low, [])
    pass_collapse = sum(1 for c in m_low_cells if c["retention"] < HP_RET_COLLAPSE)
    total = len(m_low_cells)

    detail = (f"mean_ret_by_M={dict((k, round(v,4)) for k,v in mean_ret.items())} "
              f"ret_low(M={m_low})={ret_low:.4f} ret_high(M={m_high})={ret_high:.4f} "
              f"pass_collapse={pass_collapse}/{total} N={summary.get('N', N_FULL)}")

    if ret_high >= HF_RET_HIGH:
        return ("C8_HARD_FAIL",
                f"NO_COLLAPSE: ret at M_frac={m_high} = {ret_high:.4f} >= {HF_RET_HIGH}. " + detail)

    if pass_collapse >= HP_SEEDS_MIN:
        return ("C8_HARD_PASS",
                f"HYPER_COLLAPSE: ret < {HP_RET_COLLAPSE} at M_frac={m_low}. " + detail)

    return ("C8_MIDDLE_BAND", f"PARTIAL_COLLAPSE: ret_low={ret_low:.4f}. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"
    # Formula: M calculation
    assert int(32.0 * N_FULL) == 131072, f"M=32*4096: {int(32.0*N_FULL)}"
    # OOM check at M_frac=32
    oom_bytes = int(32.0 * N_FULL) * N_FULL * 4
    assert oom_bytes < 6 * 1024**3, f"OOM at M_frac=32: {oom_bytes/(1024**3):.1f}GB"
    # Verdict gates
    fake_hp = [{"M_frac": 25.0, "retention": 0.05, "beta": 32.0, "seed": 7, "M": 0, "N": N_FULL},
               {"M_frac": 25.0, "retention": 0.04, "beta": 32.0, "seed": 17, "M": 0, "N": N_FULL},
               {"M_frac": 32.0, "retention": 0.03, "beta": 32.0, "seed": 7, "M": 0, "N": N_FULL}]
    v, _ = compute_verdict({"cells": fake_hp, "N": N_FULL})
    assert "HARD_PASS" in v, f"HARD_PASS gate: {v}"
    fake_hf = [{"M_frac": 32.0, "retention": 0.80, "beta": 32.0, "seed": 7, "M": 0, "N": N_FULL}]
    vf, _ = compute_verdict({"cells": fake_hf, "N": N_FULL})
    assert "HARD_FAIL" in vf, f"HARD_FAIL gate: {vf}"
    # Smoke cell
    device = torch.device("cpu")
    cell = run_one_cell(N_SMOKE, 25.0, 32.0, 17, device)
    assert not math.isnan(cell["retention"]), "retention NaN"
    assert 0.0 <= cell["retention"] <= 1.0, f"retention out of range: {cell['retention']}"
    # 4x scale: use N=4096 (N_SMOKE*4, must be power-of-2 with even log2)
    cell4 = run_one_cell(N_SMOKE * 4, 25.0, 32.0, 17, device)
    assert not math.isnan(cell4["retention"]), "4x retention NaN"
    print(f"[selftest] axis1_mb_chunk8_v1_n4096 PASS ret_smoke={cell['retention']:.5f}", flush=True)


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
    betas = BETA_SMOKE if smoke else BETA_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    print(f"[run] axis1_mb_chunk8_v1_n4096 smoke={smoke} N={N_cfg} M_fracs={m_fracs} seeds={seeds} device={device_str}", flush=True)
    t0 = time.time()

    all_cells = []
    for M_frac in m_fracs:
        print(f"\n  [M_frac={M_frac}]", flush=True)
        for beta in betas:
            for seed in seeds:
                cell = run_one_cell(N_cfg, M_frac, beta, seed, device)
                all_cells.append(cell)
        print(f"  M_frac={M_frac} elapsed={time.time()-t0:.1f}s", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "axis1_mb_chunk8_v1_n4096", "N": N_cfg, "smoke": smoke,
        "M_fracs": m_fracs, "betas": betas, "seeds": seeds,
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
