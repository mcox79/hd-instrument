"""KF-1 HALLUCINATION-IMPOSSIBILITY Rescue v3: N=8192 multi-N replication.

PARENT: exp_kf1_hallu_rescue_v2_n4096.py -- v2 HARD_PASS at N=4096 5-seed x 3-M_frac.
  v2 HARD_PASS: above_thresh_frac=0 in all 5 seeds at N=4096. row lifted green->green
  with annotation "multi-N replication N=8192 still needed for tick promotion".

SCIENTIFIC QUESTION:
  Does KF-1 hallucination-detection hold at N=8192?
  Specifically: does above_thresh_frac=0 persist at N=8192 for all seeds, all M_fracs?
  This uses argmax-vs-uniform readout -- NOT Kerdock codebook. SAFE at N=8192 (log2=13 odd).
  Kerdock audit: exp_kf1_tier1_rescue_v1_n4096 and v2 both use argmax-vs-uniform.
  make_kerdock_4coset_codebook NOT reached in this script. SAFE.

PRE-REGISTERED BANDS:
  Prior anchor: v2 N=4096 HARD_PASS above_thresh_frac=0 all 5 seeds.
  HARD_PASS: (a) above_thresh_frac=0 in ALL 5 seeds at M <= N
    AND (b) mean_oos_max_conf <= 10/C in >= 4/5 seeds at M <= N
    AND max_oos_max_conf < 50/C.
    C = 4*N = 32768 at N=8192.
    Interpretation: KF-1 N-axis replication confirmed; row eligible for tick promotion.
  HARD_FAIL: any seed shows above_thresh_frac > 0 at M <= N.
    KF-1 scaling breaks at N=8192; investigation needed.
  MIDDLE_BAND: above_thresh_frac=0 but mean_max_conf > 10/C in >1 seed.

FORMULA SELF-TESTS:
  1. N == 8192 (PROT-018 binding): _n8192 suffix.
  2. C = 4*N = 32768. 1/C = 3.052e-5. 10/C = 3.052e-4. 50/C = 1.526e-3.
  3. above_thresh_frac=0 in all 5 seeds -> HARD_PASS (part a).
  4. Tighter bounds at N=8192 than N=4096 (C=32768 vs C=16384).

TIMEOUT ESTIMATE:
  v2 at N=4096 elapsed ~5-10s. N-scale: (8192/4096)^1.0 = 2x.
  Estimate: 10 * 2 = 20s. Safety 50x: 1000s. Floor _n8192 = 21600. timeout_s = 21600.

KERDOCK AUDIT: SAFE -- no make_kerdock_4coset_codebook call in v1/v2 chain.
N-suffix: _n8192 -> production N = 8192 (PROT-018 binding).
Anchor: kf1_hallu_rescue_v3_n8192
Queue: overnight_queue (GPU; N=8192 5-seed Tier-1 N-axis replication)
Pre-reg: preregs/2026-05-29_kf1_hallu_rescue_v3_n8192.md
Parent: kf1_hallu_rescue_v2_n4096 (HARD_PASS at N=4096)
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

# Load v1 for run_one_seed, compute_verdict (same evaluation logic; N is a config param)
_v1_path = REPO / "experiments" / "exp_kf1_tier1_rescue_v1_n4096.py"
_v1_spec = importlib.util.spec_from_file_location("kf1t1v1_v3n8k", _v1_path)
v1 = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(v1)

run_one_seed = v1.run_one_seed
compute_verdict = v1.compute_verdict

# PRODUCTION CONFIG -- PROT-018: _n8192 suffix binds to N = 8192
N_FULL  = 8192
N_SMOKE = 1024
assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

M_FRACTIONS_FULL  = [0.25, 0.50, 1.0]
M_FRACTIONS_SMOKE = [0.25, 1.0]

N_OOS_FULL  = 1000
N_OOS_SMOKE = 100
N_INSET_FULL  = 200
N_INSET_SMOKE = 30

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]


def get_output_dir(default_name: str = "kf1_hallu_rescue_v3_n8192") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _instrumentation_selftest() -> None:
    assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"
    # Formula: C = 4*N = 32768 at N=8192
    C = 4 * N_FULL
    assert C == 32768, f"C formula at N=8192: {C}"
    bound_10x = 10.0 / C
    assert abs(bound_10x - 3.052e-4) < 1e-5, f"bound_10x at N=8192: {bound_10x}"
    # Tighter than N=4096 (10/16384 = 6.103e-4)
    assert bound_10x < 10.0 / (4 * 4096), "N=8192 bound should be tighter than N=4096"
    # Verdict gates: build mock per_seed (using v2's compute_verdict logic)
    C_v2 = 4 * 4096  # v1's compute_verdict uses N_FULL=4096 inside; we pass override
    mock_per_seed = {}
    for seed in [7, 17, 23, 31, 41]:
        mock_per_seed[str(seed)] = {
            "per_M": {
                "0.25": {"M": 2048, "M_over_N": 0.25, "C": C,
                         "above_thresh_frac": 0.0, "near_uniform_mean": True,
                         "near_uniform_max": True, "ratio_to_uniform_mean": 2.5,
                         "oos_max_conf_mean": 2.5 / C, "oos_max_conf_max": 5.0 / C,
                         "bound_10x": bound_10x, "bound_50x": 50.0 / C,
                         "inset_acc": 0.95, "inset_max_conf_mean": 0.8},
            }
        }
    v, msg = compute_verdict({"per_seed": mock_per_seed, "N": N_FULL})
    assert "PASS" in v, f"HARD_PASS gate: {v}"
    # Smoke cell: run_one_seed at small N
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
    assert first_cell["above_thresh_frac"] >= 0.0, "above_thresh_frac < 0"
    # 4x smoke: N=4096 (N_SMOKE * 4)
    config_4x = {
        "smoke": True, "N": N_SMOKE * 4,
        "m_fracs": [0.25],
        "n_oos": 50, "n_inset": 20,
    }
    result4 = run_one_seed(17, config_4x, device)
    assert "per_M" in result4, "4x per_M missing"
    # Validity: at least 1 M-frac cell non-null
    assert len(per_M) >= 1, "validity filter: no per_M cells at smoke scale"
    print(f"[selftest] kf1_hallu_rescue_v3_n8192 PASS "
          f"above_thresh_frac={first_cell['above_thresh_frac']:.3f} "
          f"C={C} bound_10x={bound_10x:.2e}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    parser.add_argument("--N", type=int, default=N_FULL)
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    device_str = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device_str)
    smoke = args.smoke

    N_cfg = N_SMOKE if smoke else N_FULL
    # Honor --N override for PROT-018 compliance check at run time
    if not smoke and args.N != N_FULL:
        print(f"[WARN] --N={args.N} does not match PROT-018 binding N_FULL={N_FULL}; using N_FULL",
              flush=True)
    m_fracs = M_FRACTIONS_SMOKE if smoke else M_FRACTIONS_FULL
    n_oos = N_OOS_SMOKE if smoke else N_OOS_FULL
    n_inset = N_INSET_SMOKE if smoke else N_INSET_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    print(f"[run] kf1_hallu_rescue_v3_n8192 smoke={smoke} N={N_cfg} "
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
        "anchor": "kf1_hallu_rescue_v3_n8192", "N": N_cfg, "smoke": smoke,
        "m_fracs": m_fracs, "seeds": seeds,
        "per_seed": per_seed, "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    out_dir = get_output_dir()
    out_path = out_dir / "metrics.json"
    tmp_path = out_path.with_suffix(".json.tmp")
    with open(tmp_path, "w") as f:
        json.dump(summary, f, indent=2)
    os.replace(tmp_path, out_path)

    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed}s", flush=True)
    print(f"[output] {out_path}", flush=True)


if __name__ == "__main__":
    main()
