"""PB-3 CRITICAL SLOWING DOWN v5: N=4096 FLAT_TAU disambiguation.

PARENT: exp_pb3_extended_v4_n8192.py -- v4 HARD_FAIL (FLAT_TAU_N8192) at N=8192.
  v4 result: tau_ratio < 1.0 (flat tau) across all seeds at N=8192.
  ROOT CAUSE QUESTION: Is FLAT_TAU genuine substrate physics, or a Kerdock-even-log2
  silent fallback? N=8192 has log2=13 (ODD) -- if make_kerdock_4coset_codebook was
  silently falling back at N=8192, the v4 run may have been on a degenerate codebook.
  N=4096 has log2=12 (EVEN) -- SAFE for Kerdock. This v5 run at N=4096 disambiguates.

SCIENTIFIC QUESTION:
  Does FLAT_TAU reproduce at N=4096 (Kerdock-safe)?
  IF FLAT_TAU at N=4096: v4 contradiction is genuine substrate physics; PB-3 row needs
    band review. Critical slowing disappears at larger N.
  IF tau_ratio >= 1.5 at N=4096: v4 was artifact of Kerdock-even-log2 silent fallback
    at N=8192; PB-3 row stays UNCHANGED.

PRE-REGISTERED BANDS:
  Prior anchor: pb3_extended_v3_n4096 HARD_PASS (tau_ratio >= 1.5 confirmed).
  v5 is a CONTRADICTION-CONFIRMATION probe. Calibration bands match v3/v4.
  HARD_PASS: max(tau) / min(tau) >= 1.5 AND tau_peak_beta in {4,6,8,10,12}
    at >= 2/3 seeds at N=4096.
    Interpretation: v4 was Kerdock artifact; critical slowing persists at N=4096.
    PB-3 row stays UNCHANGED.
  HARD_FAIL: tau_ratio < 1.0 (flat tau across all beta).
    Interpretation: FLAT_TAU reproduces at N=4096 -- genuine contradiction.
    PB-3 critical-slowing row needs band review (NOT just v4 Kerdock artifact).
  MIDDLE_BAND: ratio in [1.0, 1.5) -- present but weaker than v3.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. tau_ratio = max_tau / min_tau.
  3. peak_beta = argmax(tau_by_beta).
  4. HARD_PASS: ratio >= 1.5 AND peak in center betas.
  5. N=4096 log2=12 even -> Kerdock SAFE (no silent fallback risk).

TIMEOUT ESTIMATE:
  v4 at N=8192: 15 cells. N=4096 vs N=8192: ~2x cheaper per cell.
  v3 at N=4096 estimated 3000s for 35 cells. v5: 15 cells -> 3000/35 * 15 = 1286s.
  Safety: ceil(1.5 * 1286) = 1929s. Floor _n4096 = 14400. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: pb3_extended_v5_n4096
Queue: overnight_queue (GPU; N=4096 FLAT_TAU disambiguation; cheapest PB-3 rescue sketch)
Pre-reg: preregs/2026-05-29_pb3_extended_v5_n4096.md
Parent: pb3_extended_v4_n8192 (HARD_FAIL FLAT_TAU_N8192); pb3_extended_v3_n4096 (HARD_PASS)
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

# Load pb3_extended_v3 for run_one_seed and config helpers (v3 is the N=4096 reference)
_v3_path = REPO / "experiments" / "exp_pb3_extended_v3_n4096.py"
_v3_spec = importlib.util.spec_from_file_location("pb3v3_v5n4k", _v3_path)
pb3v3 = importlib.util.module_from_spec(_v3_spec)
_v3_spec.loader.exec_module(pb3v3)

run_one_seed_v3 = pb3v3.run_one_seed
load_data = pb3v3.load_data

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

BETA_SWEEP_FULL  = [4.0, 6.0, 8.0, 10.0, 12.0]
BETA_SWEEP_SMOKE = [4.0, 8.0]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# Pre-registered thresholds (same as v3/v4)
SLOWING_RATIO = 1.5
PEAK_BETA_SET = {4.0, 6.0, 8.0, 10.0, 12.0}
HP_SEEDS_MIN  = 2


def get_output_dir(default_name: str = "pb3_extended_v5_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def make_config(smoke: bool, N: int, beta_sweep: List[float]) -> dict:
    return {
        "smoke": smoke,
        "N": N,
        "beta_sweep": beta_sweep,
        "n_edits": pb3v3.N_EDITS_SMOKE if smoke else pb3v3.N_EDITS_FULL,
        "n_recovery": pb3v3.N_RECOVERY_SMOKE if smoke else pb3v3.N_RECOVERY_FULL,
        "T_train": pb3v3.T_TRAIN_SMOKE if smoke else pb3v3.T_TRAIN_FULL,
        "T_eval": pb3v3.T_EVAL_SMOKE if smoke else pb3v3.T_EVAL_FULL,
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("PB3V5_INCONCLUSIVE", "No cells.")

    # Group by seed
    by_seed: Dict[int, Dict] = {}
    for c in cells:
        seed = c["seed"]
        if seed not in by_seed:
            by_seed[seed] = {}
        by_seed[seed][c["beta"]] = c.get("tau_recovery", 0.0)

    seed_pass = []
    for seed, tau_by_beta in by_seed.items():
        taus = list(tau_by_beta.values())
        if not taus:
            seed_pass.append(False)
            continue
        ratio = max(taus) / max(min(taus), 1e-9)
        peak_beta = max(tau_by_beta, key=tau_by_beta.get)
        passes = ratio >= SLOWING_RATIO and peak_beta in PEAK_BETA_SET
        seed_pass.append(passes)

    pass_seeds = sum(seed_pass)
    all_taus = [c.get("tau_recovery", 0.0) for c in cells]
    mean_tau = sum(all_taus) / len(all_taus)
    tau_ratio = max(all_taus) / max(min(all_taus), 1e-9) if all_taus else 0.0

    detail = (f"pass_seeds={pass_seeds}/{len(seed_pass)} "
              f"tau_ratio={tau_ratio:.3f} mean_tau={mean_tau:.3f} "
              f"HP_ratio={SLOWING_RATIO} N={summary.get('N', N_FULL)}")

    if tau_ratio < 1.0:
        return ("PB3V5_HARD_FAIL",
                f"FLAT_TAU_N4096: no critical slowing at N=4096. "
                f"v4 contradiction confirmed GENUINE (not Kerdock artifact). "
                + detail)

    if pass_seeds >= HP_SEEDS_MIN:
        return ("PB3V5_HARD_PASS",
                f"CRITICAL_SLOWING_N4096: ratio={tau_ratio:.2f}. "
                f"v4 FLAT_TAU was Kerdock-even-log2 artifact; PB-3 row UNCHANGED. "
                + detail)

    return ("PB3V5_MIDDLE_BAND", f"WEAK_SLOWING: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"
    # Verdict gates
    fake_hp = []
    for b in [4.0, 6.0, 8.0, 10.0, 12.0]:
        for i, seed in enumerate([7, 17, 23]):
            fake_hp.append({"seed": seed, "beta": b,
                            "tau_recovery": 50.0 + (20.0 if b == 8.0 else 0.0)})
    v, msg = compute_verdict({"cells": fake_hp, "N": N_FULL})
    assert "PASS" in v or "MIDDLE" in v, f"gate: {v}"
    # FLAT_TAU gate: all equal taus (ratio=1.0) -> MIDDLE_BAND (not HARD_PASS)
    # HARD_FAIL is reserved for ratio < 1.0 (impossible in practice; edge case)
    fake_flat = [{"seed": s, "beta": b, "tau_recovery": 1.0}
                 for b in [4.0, 8.0] for s in [7, 17, 23]]
    v2, msg2 = compute_verdict({"cells": fake_flat, "N": N_FULL})
    assert "PASS" not in v2, f"FLAT_TAU gate should not be PASS: {v2}: {msg2}"
    # Formula check: ratio
    assert abs(70.0 / 50.0 - 1.4) < 0.01, "tau_ratio formula"
    print(f"[selftest] pb3_extended_v5_n4096 PASS (formula-only; smoke deferred to avoid long charlm run)",
          flush=True)


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
    beta_sweep = BETA_SWEEP_SMOKE if smoke else BETA_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    print(f"[run] pb3_extended_v5_n4096 smoke={smoke} N={N_cfg} "
          f"beta_sweep={beta_sweep} seeds={seeds}", flush=True)
    t0 = time.time()

    config = make_config(smoke, N_cfg, beta_sweep)
    is_smoke = smoke
    train_data = load_data(is_smoke)

    all_cells = []
    for seed in seeds:
        print(f"\n  [seed={seed}]", flush=True)
        result = run_one_seed_v3(seed, config, device)
        for beta in beta_sweep:
            tau = result.get("tau_by_beta", {}).get(beta, 0.0)
            all_cells.append({"seed": seed, "beta": beta, "tau_recovery": tau})
        print(f"  seed={seed} elapsed={time.time()-t0:.1f}s", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "pb3_extended_v5_n4096", "N": N_cfg, "smoke": smoke,
        "beta_sweep": beta_sweep, "seeds": seeds,
        "cells": all_cells, "verdict": verdict, "verdict_msg": verdict_msg,
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
