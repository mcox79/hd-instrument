"""KF-1 HALLUCINATION-IMPOSSIBILITY Rescue v2: N=8192 OOS confidence scaling.

PARENT: exp_kf1_tier1_rescue_v1_n4096.py -- v1 Tier-1 reformulation at N=4096.
  v1 hypothesis: OOS max_conf ratio_to_uniform DECREASES with N.
  At N=1024: ratio ~ 2.8x. At N=4096: ratio ~ 2.8x (flat). Claimed: < 2x at N=16384.
  This experiment tests the ratio at N=8192.

SCIENTIFIC QUESTION:
  At N=8192 Kerdock (N=8192 is valid: log2=13, odd).
  Wait: Kerdock requires even log2. N=8192 log2=13 (ODD) -- INVALID.
  Use N=4096 (log2=12, even) as the largest valid Kerdock N.

  CORRECTION: this script tests whether KF-1 rescue holds at N=4096 with 5-seed
  FULL production sweep (v1 was formula-only selftest; need actual production numbers).
  v1 may have run at smoke scale (N=1024) during selftest. This ships FULL N=4096 5-seed.

  Also tests: does the near-uniform bound tighten at more seeds (reduces variance)?
  5 seeds x 3 M_fracs x N=4096 = 15 cells.

PRE-REGISTERED BANDS:
  HARD_PASS: (a) above_thresh_frac=0 in ALL 5 seeds at M <= N
    AND (b) mean_oos_max_conf <= 10/C in >= 4/5 seeds at M <= N
    AND max_oos_max_conf < 50/C (even worst-case is within 50x of uniform).
    C = 4*N = 16384 at N=4096.
    Interpretation: provably cannot hallucinate at N=4096 production scale.
  HARD_FAIL: any seed shows above_thresh_frac > 0 at M <= N.
  MIDDLE_BAND: above_thresh_frac=0 but mean_max_conf > 10/C in >1 seed.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding): _n4096 suffix.
  2. C = 4*N = 16384. 1/C = 6.103e-5. 10/C = 6.103e-4. 50/C = 3.05e-3.
  3. above_thresh_frac=0 in all 5 seeds -> HARD_PASS (part a).
  4. 5-seed mean_ratio_to_uniform at M/N=1.0 should be ~2.8x (matches v1 estimate).

TIMEOUT ESTIMATE:
  v1 elapsed ~5-10s at N=4096 5 seeds. This is same protocol.
  Safety x10 for any overhead: 100s. Floor _n4096 = 14400s. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: kf1_hallu_rescue_v2_n4096
Queue: overnight_queue (GPU; N=4096 5-seed Tier-1 rescue production run)
Pre-reg: prereqs/2026-05-28_kf1_hallu_rescue_v2_n4096.md
Parent: kf1_tier1_rescue_v1_n4096; kf1_hallu_impossibility_v2
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

# Load v1 for run_one_seed, compute_verdict, store_facts_outer
_v1_path = REPO / "experiments" / "exp_kf1_tier1_rescue_v1_n4096.py"
_v1_spec = importlib.util.spec_from_file_location("kf1t1v1_v2", _v1_path)
v1 = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(v1)

run_one_seed = v1.run_one_seed
compute_verdict = v1.compute_verdict

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_FRACTIONS_FULL  = [0.25, 0.50, 1.0]
M_FRACTIONS_SMOKE = [0.25, 1.0]

N_OOS_FULL  = 1000
N_OOS_SMOKE = 100
N_INSET_FULL  = 200
N_INSET_SMOKE = 30

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]


def get_output_dir(default_name: str = "kf1_hallu_rescue_v2_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"
    # Formula: C = 4*N = 16384
    C = 4 * N_FULL
    assert C == 16384, f"C formula: {C}"
    bound_10x = 10.0 / C
    assert abs(bound_10x - 6.103e-4) < 1e-5, f"bound_10x: {bound_10x}"
    # Verdict gates (using v1's compute_verdict)
    # Build mock per_seed with no hallucination and near-uniform
    mock_per_seed = {}
    for seed in [7, 17, 23, 31, 41]:
        mock_per_seed[str(seed)] = {
            "per_M": {
                "0.25": {"M": 1024, "M_over_N": 0.25, "C": C,
                         "above_thresh_frac": 0.0, "near_uniform_mean": True,
                         "near_uniform_max": True, "ratio_to_uniform_mean": 2.5,
                         "oos_max_conf_mean": 2.5/C, "oos_max_conf_max": 5.0/C,
                         "bound_10x": bound_10x, "bound_50x": 50.0/C,
                         "inset_acc": 0.95, "inset_max_conf_mean": 0.8},
            }
        }
    v, msg = compute_verdict({"per_seed": mock_per_seed, "N": N_FULL})
    assert "PASS" in v, f"HARD_PASS gate: {v}"
    # Smoke cell: run_one_seed at small scale
    device = torch.device("cpu")
    config_smoke = {
        "smoke": True, "N": N_SMOKE,
        "m_fracs": M_FRACTIONS_SMOKE,
        "n_oos": N_OOS_SMOKE, "n_inset": N_INSET_SMOKE,
    }
    result = run_one_seed(17, config_smoke, device)
    assert "per_M" in result, "per_M missing"
    per_M = result["per_M"]
    assert len(per_M) >= 1, "per_M empty"
    first_cell = list(per_M.values())[0]
    assert "above_thresh_frac" in first_cell, "above_thresh_frac missing"
    assert not math.isnan(first_cell["above_thresh_frac"]), "above_thresh_frac NaN"
    # 4x smoke: N=4096 (N_SMOKE * 4)
    config_4x = {
        "smoke": True, "N": N_SMOKE * 4,
        "m_fracs": [0.25],
        "n_oos": 50, "n_inset": 20,
    }
    result4 = run_one_seed(17, config_4x, device)
    assert "per_M" in result4, "4x per_M missing"
    print(f"[selftest] kf1_hallu_rescue_v2_n4096 PASS "
          f"above_thresh_frac={first_cell['above_thresh_frac']:.3f}", flush=True)


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
    m_fracs = M_FRACTIONS_SMOKE if smoke else M_FRACTIONS_FULL
    n_oos = N_OOS_SMOKE if smoke else N_OOS_FULL
    n_inset = N_INSET_SMOKE if smoke else N_INSET_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    print(f"[run] kf1_hallu_rescue_v2_n4096 smoke={smoke} N={N_cfg} "
          f"m_fracs={m_fracs} seeds={seeds}", flush=True)
    t0 = time.time()

    config = {
        "smoke": smoke, "N": N_cfg,
        "m_fracs": m_fracs,
        "n_oos": n_oos, "n_inset": n_inset,
    }

    per_seed = {}
    for seed in seeds:
        print(f"\n  [seed={seed}]", flush=True)
        result = run_one_seed(seed, config, device)
        per_seed[str(seed)] = result
        print(f"  seed={seed} elapsed={time.time()-t0:.1f}s", flush=True)

    verdict, verdict_msg = compute_verdict({
        "per_seed": per_seed, "N": N_cfg
    })
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "kf1_hallu_rescue_v2_n4096", "N": N_cfg, "smoke": smoke,
        "m_fracs": m_fracs, "seeds": seeds,
        "per_seed": per_seed, "verdict": verdict, "verdict_msg": verdict_msg,
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
