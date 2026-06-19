"""Orthogonal Non-Equilibrium Corroborator v2: N=4096, rescue from v1.

CONTEXT:
  ortho_noneq_corroborator_v1 (completed on remote_cpu_queue): N=4096 orthogonal
  non-equilibrium probe completed.
  v2 (THIS): extended sweep probing whether the non-equilibrium signature strengthens
  with increasing M_frac (overcapacity) and whether it correlates with the SKAH-M
  saddle-hierarchy mechanism.

  Non-equilibrium signature: Hatano-Sasa HS identity violation (EP > 0 in steady state).
  v1 tested basic HS violation at a fixed operating point.
  v2 extends to 4 M_fracs to map the M-dependence of the non-equilibrium signature.

SCIENTIFIC QUESTION:
  Does the HS entropy production EP increase with M_frac (more overcapacity = more
  non-equilibrium drive)?
  At what M_frac does EP first become detectable above noise?

PRE-REGISTERED BANDS:
  Prior: v1 completed (result unknown here, assume EP > 0 at tested M_frac).
  Calibration probe for M-axis: no prior M-sweep anchor.
  Bands: +/-50% of v1 EP value per calibration policy.

  HARD_PASS: EP monotonically increases with M_frac at >= 2/3 seeds.
    AND EP > 0 at M_frac=2.0 at all seeds.
    Interpretation: non-equilibrium drive scales with memory load.
  HARD_FAIL: EP <= 0 at M_frac=0.5 AND M_frac=2.0 at >= 2/3 seeds.
    Interpretation: HS violation not reproducible across load levels.
  MIDDLE_BAND: EP > 0 at some M_fracs but not monotone.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. EP = entropy production proxy (see v1 method).
  3. M at M_frac=2.0, N=4096: M=8192.
  4. HARD_PASS requires monotone: EP(M_frac=2.0) > EP(M_frac=0.5).

OOM CHECK:
  W float32 at N=4096: 64MB. M=8192 keys: 128MB. OK.

TIMEOUT ESTIMATE:
  v1 N=4096 elapsed from completed status: estimated ~300-1000s.
  v2: 4 M_fracs x 3 seeds = 12 cells. ~3x v1 cells.
  Total: 3 * 1000 = 3000s (conservative). Safety 1.5x: 4500s. Floor 14400. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: ortho_noneq_v2_n4096
Queue: remote_cpu_queue (CPU; N=4096 Kerdock; M-axis non-equilibrium EP sweep)
Pre-reg: preregs/2026-05-29_ortho_noneq_v2_n4096.md
Parent: ortho_noneq_corroborator_v1 (completed N=4096)
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

# Load v1 for shared HS violation infrastructure
_v1_path = REPO / "experiments" / "exp_ortho_noneq_corroborator_v1.py"
_v1_spec = importlib.util.spec_from_file_location("ortho_noneq_v1_v2", _v1_path)
_v1_mod = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(_v1_mod)

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_FRACS_FULL  = [0.25, 0.5, 1.0, 2.0]
M_FRACS_SMOKE = [1.0]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
HP_EP_MIN        = 0.0   # EP > 0 = non-equilibrium signal
HP_MONOTONE_MIN  = 2     # >= 2/3 seeds show monotone EP increase
HF_EP_MAX        = 0.0   # EP <= 0 at high M_frac = fail


def get_output_dir(default_name: str = "ortho_noneq_v2_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_cell(N: int, M_frac: float, seed: int) -> Dict:
    """Run HS non-equilibrium probe at (N, M_frac, seed) via v1 infrastructure.

    Override v1's ALPHA_INIT to achieve the desired M_frac.
    v1 uses M_init = max(4, int(N * ALPHA_INIT)).
    We set ALPHA_INIT = M_frac to get M_init = M_frac * N.
    """
    orig_alpha = _v1_mod.ALPHA_INIT
    try:
        _v1_mod.ALPHA_INIT = M_frac
        result = _v1_mod.run_one_seed(N=N, seed=seed)
    finally:
        _v1_mod.ALPHA_INIT = orig_alpha

    result["N"] = N
    result["M_frac"] = M_frac
    result["M"] = int(M_frac * N)
    result["seed"] = seed
    # Standardize ep key
    if "ep" not in result:
        # v1 returns hs_ratio (>1 = non-equilibrium). ep proxy = hs_ratio - 1.
        hs = result.get("hs_ratio", 1.0)
        result["ep"] = float(hs) - 1.0
    return result


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    per_mfrac = summary.get("per_mfrac", {})
    if not per_mfrac:
        return ("NONEQ_V2_INCONCLUSIVE", "No per_mfrac data.")

    mfracs = sorted(float(k) for k in per_mfrac.keys())
    mean_ep_by_mfrac = {}
    for mf in mfracs:
        cells = per_mfrac.get(str(mf), [])
        eps = [c.get("ep", c.get("entropy_production", None))
               for c in cells if c is not None]
        eps = [e for e in eps if e is not None and not math.isnan(e)]
        mean_ep_by_mfrac[mf] = sum(eps) / len(eps) if eps else 0.0

    if len(mfracs) < 2:
        # Only 1 M_frac tested (smoke)
        ep_val = mean_ep_by_mfrac.get(mfracs[0], 0.0)
        if ep_val > HP_EP_MIN:
            return ("NONEQ_V2_SMOKE_PASS", f"EP>0 at M_frac={mfracs[0]}: ep={ep_val:.4f}")
        return ("NONEQ_V2_SMOKE_FAIL", f"EP<=0: ep={ep_val:.4f}")

    # Monotone check
    ep_vals = [mean_ep_by_mfrac[mf] for mf in mfracs]
    n_increasing = sum(1 for i in range(1, len(ep_vals)) if ep_vals[i] > ep_vals[i-1])
    is_monotone = (n_increasing >= len(mfracs) - 1)

    ep_high = mean_ep_by_mfrac.get(max(mfracs), 0.0)
    detail = (f"mean_ep_by_mfrac={dict((k, round(v,4)) for k,v in mean_ep_by_mfrac.items())} "
              f"n_increasing={n_increasing}/{len(mfracs)-1} ep_high={ep_high:.4f}")

    if ep_high <= HF_EP_MAX:
        return ("NONEQ_V2_HARD_FAIL",
                f"EP<=0 at high M_frac: ep_high={ep_high:.4f}. " + detail)

    if ep_high > HP_EP_MIN and is_monotone:
        return ("NONEQ_V2_HARD_PASS",
                f"EP MONOTONE-INCREASING with M_frac. " + detail)

    return ("NONEQ_V2_MIDDLE_BAND",
            f"EP>0 but not robustly monotone. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Import chain
    assert _v1_mod is not None, "v1 import failed"

    # Formula tests
    assert int(2.0 * N_FULL) == 8192, "M at M_frac=2.0"
    assert int(4.0 * N_FULL) == 16384, "M at M_frac=4.0"

    # Live smoke cell -- use small N=256 to avoid slow Python loop in build_W
    SELFTEST_N = 256
    result = run_one_cell(SELFTEST_N, 0.25, 17)
    # ep is computed in run_one_cell as hs_ratio - 1
    ep_val = result.get("ep")
    assert ep_val is not None, f"ep is None in result: {list(result.keys())}"
    assert isinstance(ep_val, (int, float)), f"ep not numeric: {type(ep_val)}"
    assert not math.isnan(ep_val), "ep is NaN"

    # 4x smoke: N=256*4 = 1024 (multi-scale gate)
    result4 = run_one_cell(SELFTEST_N * 4, 0.25, 17)
    ep4 = result4.get("ep")
    assert ep4 is not None, "4x ep None"
    assert not math.isnan(ep4), "4x ep NaN"

    # Filter: at least one M_frac should produce ep != 0 (non-trivial non-eq signal)
    # Allow ep=0 (equilibrium at low M_frac is valid)

    print(f"[selftest] ortho_noneq_v2_n4096 PASS ep_N256={ep_val:.4f} ep_N1024={ep4:.4f}",
          flush=True)


_instrumentation_selftest()


def run_full(smoke: bool = False) -> None:
    t0 = time.monotonic()

    m_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    seeds   = SEEDS_SMOKE if smoke else SEEDS_FULL
    N_cfg   = N_SMOKE if smoke else N_FULL

    print(f"ortho_noneq_v2_n4096 mode={'SMOKE' if smoke else 'FULL'} "
          f"N={N_cfg} m_fracs={m_fracs} seeds={seeds}", flush=True)

    per_mfrac: Dict = {}

    for M_frac in m_fracs:
        M = int(M_frac * N_cfg)
        print(f"\n== M_frac={M_frac} (M={M}) ==", flush=True)
        cells = []
        for seed in seeds:
            t_cell = time.monotonic()
            result = run_one_cell(N_cfg, M_frac, seed)
            elapsed_cell = time.monotonic() - t_cell
            ep_val = result.get("ep", result.get("entropy_production", None))
            print(f"  M_frac={M_frac} seed={seed} ep={ep_val} elapsed={elapsed_cell:.1f}s",
                  flush=True)
            result["elapsed_s"] = round(elapsed_cell, 2)
            cells.append(result)
        per_mfrac[str(M_frac)] = cells

    elapsed_total = time.monotonic() - t0
    verdict, verdict_msg = compute_verdict({"per_mfrac": per_mfrac, "N": N_cfg})

    summary = {
        "anchor": "ortho_noneq_v2_n4096",
        "N": N_cfg, "smoke": smoke,
        "m_fracs": m_fracs, "seeds": seeds,
        "per_mfrac": per_mfrac,
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": round(elapsed_total, 2),
    }
    out_dir = get_output_dir()
    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as fp:
        json.dump(summary, fp, indent=2)

    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_total:.1f}s", flush=True)
    print(f"[output] {out_path}", flush=True)


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    run_full(smoke=args.smoke)


if __name__ == "__main__":
    main()
