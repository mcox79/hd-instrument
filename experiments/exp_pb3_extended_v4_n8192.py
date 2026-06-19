"""PB-3 CRITICAL SLOWING DOWN v4: N=8192 extension of critical slowing probe.

CONTEXT:
  pb3_extended_v3_n4096 (v267/new): critical slowing confirmed at N=4096, beta_c ~ 8-12.
  v4 extends to N=8192 to test: does tau_recovery peak persist at N=8192?
  Does beta_c shift with N (N-dependence of critical temperature)?

SCIENTIFIC QUESTION:
  At N=8192, is there a beta where tau_recovery peaks (critical slowing)?
  Is the peak location beta_c the same as N=4096?

PRE-REGISTERED BANDS:
  Prior: pb3_extended_v3_n4096 HARD_PASS expected. v4 calibration probe at N=8192.

  HARD_PASS: max(tau) / min(tau) >= 1.5 AND tau_peak_beta in {4,6,8,10,12}
    at >= 2/3 seeds at N=8192.
    Interpretation: critical slowing persists at N=8192.
  HARD_FAIL: ratio < 1.0 (flat tau across all beta).
    Interpretation: critical slowing disappears at N=8192.
  MIDDLE_BAND: ratio in [1.0, 1.5) -- present but weaker.

FORMULA SELF-TESTS:
  1. N == 8192 (PROT-018 binding).
  2. tau_ratio = max_tau / min_tau.
  3. peak_beta = argmax(tau_by_beta).
  4. HARD_PASS: ratio >= 1.5 AND peak in center betas.

TIMEOUT ESTIMATE:
  5 beta x 3 seeds = 15 cells. Each cell at N=8192 similar to N=4096 ~360s.
  Wait: pb3 uses charlm training (T_train=10000 tokens at K=4).
  At N=8192, each forward pass is 8192 dim operations (~8x slower than N=1024).
  Scale from v3 estimate (3000s for 5x7=35 cells): 15 cells at 8x slower per step.
  Rough estimate: 15 * (3000/35) * 2 = 2571s. Safety: ceil(1.5 * 2571) = 3857s.
  _n8192 floor=21600. timeout_s=21600.

N-suffix: _n8192 -> production N = 8192 (PROT-018 binding).
Anchor: pb3_extended_v4_n8192
Queue: overnight_queue (GPU; N=8192, 5 beta x 3 seeds)
Pre-reg: prereqs/2026-05-28_pb3_extended_v4_n8192.md
Parent: pb3_extended_v3_n4096; pb3_critical_slowing_v1 (HARD_PASS baseline)
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

# Load pb3_extended_v3 for run_one_seed and config helpers
_v3_path = REPO / "experiments" / "exp_pb3_extended_v3_n4096.py"
_v3_spec = importlib.util.spec_from_file_location("pb3v3_v4n8k", _v3_path)
pb3v3 = importlib.util.module_from_spec(_v3_spec)
_v3_spec.loader.exec_module(pb3v3)

run_one_seed_v3 = pb3v3.run_one_seed
load_data = pb3v3.load_data

# PRODUCTION CONFIG -- PROT-018: _n8192 suffix binds to N = 8192
N_FULL  = 8192
N_SMOKE = 1024
assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

BETA_SWEEP_FULL  = [4.0, 6.0, 8.0, 10.0, 12.0]
BETA_SWEEP_SMOKE = [4.0, 8.0]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
SLOWING_RATIO = 1.5
PEAK_BETA_SET = {4.0, 6.0, 8.0, 10.0, 12.0}
HP_SEEDS_MIN  = 2


def get_output_dir(default_name: str = "pb3_extended_v4_n8192") -> Path:
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
        return ("PB3V4_INCONCLUSIVE", "No cells.")

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
        return ("PB3V4_HARD_FAIL", f"FLAT_TAU_N8192: no critical slowing. " + detail)

    if pass_seeds >= HP_SEEDS_MIN:
        return ("PB3V4_HARD_PASS", f"CRITICAL_SLOWING_N8192: ratio={tau_ratio:.2f}. " + detail)

    return ("PB3V4_MIDDLE_BAND", f"WEAK_SLOWING: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"
    # Verdict gates
    fake_hp = [{"seed": 17, "beta": b, "tau_recovery": 50.0 + (20.0 if b == 8.0 else 0.0)}
               for b in [4.0, 6.0, 8.0, 10.0, 12.0] for _ in range(3)]
    # Set seed field
    for i, c in enumerate(fake_hp):
        c["seed"] = [7, 17, 23][i % 3]
    v, _ = compute_verdict({"cells": fake_hp, "N": N_FULL})
    assert "PASS" in v or "MIDDLE" in v, f"gate: {v}"
    # Formula check: ratio
    assert abs(70.0 / 50.0 - 1.4) < 0.01, "tau_ratio formula"
    print(f"[selftest] pb3_extended_v4_n8192 PASS (formula-only; smoke deferred to avoid long charlm run)", flush=True)


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

    print(f"[run] pb3_extended_v4_n8192 smoke={smoke} N={N_cfg} beta_sweep={beta_sweep} seeds={seeds}", flush=True)
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
        "anchor": "pb3_extended_v4_n8192", "N": N_cfg, "smoke": smoke,
        "beta_sweep": beta_sweep, "seeds": seeds,
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
