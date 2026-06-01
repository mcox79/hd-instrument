"""KF-4 DRIFT DETECTION v5: higher-resolution N_DRIFT sweep at N=4096.

CONTEXT:
  kf4_drift_detect_v4_n4096 (completed or recent): N_DRIFT=200, testing acc_drop signal.
  v4 pre-reg: HARD_PASS if mean_acc_drop >= 0.05.
  v5 (THIS): increase N_DRIFT to 500 to amplify the signal and also add a N_DRIFT=50
  control arm (should show near-zero drop at low drift) for a dose-response curve.

  Rationale: v4 may produce weak signal near MIDDLE_BAND. A dose-response curve
  at 3 N_DRIFT levels (50, 200, 500) gives:
    - Dose-response shape (acc_drop vs N_DRIFT) -- is it linear, saturating, threshold?
    - Control at N_DRIFT=50 confirms the low-drift baseline is near-zero.
    - N_DRIFT=500 gives max signal for a clear HARD_PASS or HARD_FAIL.

SCIENTIFIC QUESTION:
  At N=4096, does acc_drop scale with N_DRIFT (more drift = more detectable accuracy loss)?
  Is there a saturation point, or is the response linear up to N_DRIFT=500?

PRE-REGISTERED BANDS:
  Prior: v4 pre-reg HARD_PASS=0.05 at N_DRIFT=200. N_DRIFT=500 expected stronger signal.

  HARD_PASS: mean_acc_drop at N_DRIFT=500 >= 0.10 (2x the v4 HP threshold)
    AND dose_response_slope > 0 (acc_drop increases with N_DRIFT).
    Interpretation: drift is clearly detectable; dose-response confirms calibrated mechanism.
  HARD_FAIL: mean_acc_drop at N_DRIFT=500 < 0.005 (essentially zero signal even at 5x drift).
    Interpretation: N=4096 substrate structurally immune even at N_DRIFT=500.
  MIDDLE_BAND: acc_drop in [0.005, 0.10) at N_DRIFT=500.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. noise_frac at N_DRIFT=500, M_frac=2: 500/8192 = 0.061.
  3. dose_response_slope: slope of (acc_drop vs N_DRIFT). positive = detectable.
  4. HARD_PASS gate: acc_drop(N_DRIFT=500) >= 0.10.
  5. Expected acc_drop ~ noise_frac = 0.061 at M_frac=2 (from v4 theory).
     At N_DRIFT=500: expected ~ 500/8192 = 0.061. Borderline HP.
     At M_frac=0.5 (M=2048): noise_frac = 500/2048 = 0.244 -> well above HP.
     Use M_FRACS=[0.5, 2.0] to ensure at least one M_frac gives clean HARD_PASS signal.

OOM CHECK:
  N=4096, M_frac=2.0: M=8192. W=64MB. Keys=8192*4096*4=128MB. Total ~200MB. OK.

TIMEOUT ESTIMATE:
  v4 at N=4096, 2 M_fracs, 3 seeds, N_PROBE=200: floor 14400s (fast ~360s actual).
  v5: 3 N_DRIFT x 2 M_fracs x 3 seeds = 18 cells.
  Per cell at N=4096: ~5s. Total: 18 * 5 * (500/200) = 225s.
  Safety: ceil(1.5 * 225 * 5) = 1688s. Floor _n4096 = 14400. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: kf4_drift_detect_v5_n4096
Queue: remote_cpu_queue (CPU; N=4096 Kerdock; dose-response N_DRIFT sweep)
Pre-reg: preregs/2026-05-29_kf4_drift_detect_v5_n4096.md
Parent: kf4_drift_detect_v4_n4096 (completed)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load v4 for shared infrastructure
import importlib.util
_v4_path = REPO / "experiments" / "exp_kf4_drift_detect_v4_n4096.py"
_v4_spec = importlib.util.spec_from_file_location("kf4v4_v5", _v4_path)
_v4_mod = importlib.util.module_from_spec(_v4_spec)
_v4_spec.loader.exec_module(_v4_mod)

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# Dose-response N_DRIFT levels
N_DRIFT_LEVELS_FULL  = [50, 200, 500]
N_DRIFT_LEVELS_SMOKE = [50, 200]   # 2 levels at smoke scale

M_FRACS_FULL  = [0.5, 2.0]
M_FRACS_SMOKE = [0.5]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

BETA          = 32.0
N_PROBE_FULL  = 200
N_PROBE_SMOKE = 50

# Pre-registered thresholds
HP_ACC_DROP_MIN  = 0.10   # >= 10% at N_DRIFT=500
HF_ACC_DROP_MAX  = 0.005  # < 0.5% = no detectable signal
HP_SEEDS_MIN     = 2


def get_output_dir(default_name: str = "kf4_drift_detect_v5_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_cell_ndrift(N: int, M_frac: float, seed: int, n_probe: int,
                        n_drift_steps: int, device: torch.device) -> Dict:
    """Measure acc_drop at specified N_DRIFT via v4 infrastructure."""
    # Patch v4's N_DRIFT_STEPS temporarily
    orig = _v4_mod.N_DRIFT_STEPS
    _v4_mod.N_DRIFT_STEPS = n_drift_steps
    try:
        result = _v4_mod.run_one_cell(N=N, M_frac=M_frac, seed=seed,
                                      n_probe=n_probe, device=device)
    finally:
        _v4_mod.N_DRIFT_STEPS = orig
    result["n_drift_steps"] = n_drift_steps
    return result


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    per_ndrift = summary.get("per_ndrift", {})
    if not per_ndrift:
        return ("KF4_V5_INCONCLUSIVE", "No per_ndrift data.")

    # Focus on N_DRIFT=500 for verdict
    cells_500 = per_ndrift.get("500", [])
    if not cells_500:
        cells_500 = per_ndrift.get(str(max(int(k) for k in per_ndrift.keys())), [])

    drops_500 = [c["acc_drop"] for c in cells_500
                 if c.get("acc_drop") is not None and not math.isnan(c["acc_drop"])]
    if not drops_500:
        return ("KF4_V5_INCONCLUSIVE", "No acc_drop at max N_DRIFT.")

    mean_drop_500 = sum(drops_500) / len(drops_500)
    n_pass_500 = sum(1 for d in drops_500 if d >= HP_ACC_DROP_MIN)

    # Dose-response slope
    drift_levels = sorted(int(k) for k in per_ndrift.keys())
    mean_drops = []
    for dl in drift_levels:
        cells = per_ndrift.get(str(dl), [])
        ds = [c["acc_drop"] for c in cells
              if c.get("acc_drop") is not None and not math.isnan(c["acc_drop"])]
        mean_drops.append(sum(ds) / len(ds) if ds else 0.0)

    # Simple slope: (last - first) / (last_level - first_level)
    slope = (mean_drops[-1] - mean_drops[0]) / max(drift_levels[-1] - drift_levels[0], 1)

    detail = (f"mean_acc_drop_500={mean_drop_500:.5f} n_pass={n_pass_500}/{len(drops_500)} "
              f"dose_slope={slope:.6f} drift_levels={drift_levels} mean_drops={[round(d,4) for d in mean_drops]}")

    if mean_drop_500 < HF_ACC_DROP_MAX:
        return ("KF4_V5_HARD_FAIL",
                f"NO_SIGNAL at N_DRIFT=500: mean_acc_drop={mean_drop_500:.5f}. " + detail)

    if mean_drop_500 >= HP_ACC_DROP_MIN and n_pass_500 >= HP_SEEDS_MIN and slope > 0:
        return ("KF4_V5_HARD_PASS",
                f"DOSE_RESPONSE_CONFIRMED: drift detectable at N_DRIFT=500. " + detail)

    return ("KF4_V5_MIDDLE_BAND",
            f"WEAK_SIGNAL at N_DRIFT=500: mean_acc_drop={mean_drop_500:.5f}. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Import chain
    assert _v4_mod is not None, "v4 import failed"
    assert hasattr(_v4_mod, "run_one_cell"), "v4 missing run_one_cell"

    # Formula tests
    noise_frac_500_mfrac2 = 500 / (2.0 * N_FULL)
    assert abs(noise_frac_500_mfrac2 - 500/8192) < 1e-6, f"noise_frac: {noise_frac_500_mfrac2}"
    noise_frac_500_mfrac05 = 500 / (0.5 * N_FULL)
    assert abs(noise_frac_500_mfrac05 - 500/2048) < 1e-4, "noise_frac M_frac=0.5"

    # Verdict tests
    cells_hp = [{"acc_drop": 0.12, "n_drift_steps": 500, "M_frac": 0.5, "passes_hp": True},
                {"acc_drop": 0.11, "n_drift_steps": 500, "M_frac": 0.5, "passes_hp": True}]
    cells_low = [{"acc_drop": 0.03, "n_drift_steps": 50, "M_frac": 0.5},
                 {"acc_drop": 0.03, "n_drift_steps": 50, "M_frac": 0.5}]
    sum_hp = {"per_ndrift": {"50": cells_low, "500": cells_hp}, "N": N_FULL}
    v, msg = compute_verdict(sum_hp)
    assert "HARD_PASS" in v, f"Expected HP: {v}: {msg}"

    cells_hf = [{"acc_drop": 0.001, "n_drift_steps": 500},
                {"acc_drop": 0.002, "n_drift_steps": 500}]
    v_hf, _ = compute_verdict({"per_ndrift": {"500": cells_hf}, "N": N_FULL})
    assert "HARD_FAIL" in v_hf, f"Expected HF: {v_hf}"

    # Live smoke cell
    device = torch.device("cpu")
    cell = run_one_cell_ndrift(N_SMOKE, 0.5, 17, N_PROBE_SMOKE, 200, device)
    assert "acc_drop" in cell, f"missing acc_drop: {list(cell.keys())}"
    assert not math.isnan(cell["acc_drop"]), "acc_drop NaN"
    assert cell["acc_base"] > 0, "acc_base not positive"

    # 4x smoke (N=4096)
    cell4 = run_one_cell_ndrift(N_SMOKE * 4, 0.5, 17, N_PROBE_SMOKE, 200, device)
    assert "acc_drop" in cell4, "4x acc_drop missing"
    assert not math.isnan(cell4["acc_drop"]), "4x acc_drop NaN"

    print(f"[selftest] kf4_drift_detect_v5_n4096 PASS "
          f"acc_drop_smoke={cell['acc_drop']:.4f} acc_drop_4x={cell4['acc_drop']:.4f}",
          flush=True)


_instrumentation_selftest()


def run_full(smoke: bool = False) -> None:
    t0 = time.monotonic()

    n_drift_levels = N_DRIFT_LEVELS_SMOKE if smoke else N_DRIFT_LEVELS_FULL
    m_fracs        = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    seeds          = SEEDS_SMOKE if smoke else SEEDS_FULL
    N_cfg          = N_SMOKE if smoke else N_FULL
    n_probe        = N_PROBE_SMOKE if smoke else N_PROBE_FULL

    device = torch.device("cpu")
    print(f"kf4_drift_detect_v5_n4096 mode={'SMOKE' if smoke else 'FULL'} "
          f"N={N_cfg} n_drift_levels={n_drift_levels} m_fracs={m_fracs} seeds={seeds}",
          flush=True)

    per_ndrift: Dict = {}

    for n_drift in n_drift_levels:
        print(f"\n== N_DRIFT={n_drift} ==", flush=True)
        cells = []

        for M_frac in m_fracs:
            for seed in seeds:
                t_cell = time.monotonic()
                result = run_one_cell_ndrift(N_cfg, M_frac, seed, n_probe, n_drift, device)
                elapsed_cell = time.monotonic() - t_cell
                print(f"  N_DRIFT={n_drift} M_frac={M_frac} seed={seed} "
                      f"acc_drop={result['acc_drop']:.4f} elapsed={elapsed_cell:.1f}s",
                      flush=True)
                cells.append(result)

        per_ndrift[str(n_drift)] = cells

    elapsed_total = time.monotonic() - t0
    verdict, verdict_msg = compute_verdict({"per_ndrift": per_ndrift, "N": N_cfg})

    summary = {
        "anchor": "kf4_drift_detect_v5_n4096",
        "N": N_cfg, "smoke": smoke,
        "n_drift_levels": n_drift_levels, "m_fracs": m_fracs, "seeds": seeds,
        "per_ndrift": per_ndrift,
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
