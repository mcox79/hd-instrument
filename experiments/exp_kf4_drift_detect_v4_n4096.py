"""KF-4 DRIFT DETECTION v4: accuracy-drop with calibrated drift magnitude at N=4096.

CONTEXT:
  kf4_drift_detect_v3_n4096 (HARD_FAIL): margin-based drift gap=0.0 at 0/3 seeds.
  Root cause analysis: noise_scale=0.01 x 100 steps = total noise of 1.0/N per W entry.
    Signal = M stored patterns / N = 2.0 at M_frac=2. Noise/signal ratio = 0.0005.
    The drift was 2000x below the signal -> undetectable.

  This v4 rescue: CALIBRATED drift magnitude. Use noise_scale such that
  total_perturbation = noise_scale * N_DRIFT_STEPS / N is comparable to 1.0 (unity).
  Specifically: noise_scale=1.0, N_DRIFT_STEPS=200 -> total = 200/N_FULL.
  At N=4096: total = 200/4096 = 0.049. At M_frac=2 signal~2.0, noise/signal=0.024.
  This should be detectable as accuracy drop (signal partially corrupted by noise).

RESCUE MECHANISM (calibrated-noise accuracy drop):
  Base state: substrate W_0 stores M facts.
  Drifted state: W_d = W_0 + sum_{i=1}^{N_DRIFT} outer(v_rnd, k_rnd) / N
    where v_rnd, k_rnd are random codebook atoms (no scale factor; each outer product = 1.0/N).
  N_DRIFT = 200 gives total perturbation 200/N to each W entry.
  Detection metric: acc_base - acc_drifted (accuracy drop from drift).
  HARD_PASS: mean_acc_drop >= 0.05 (5% accuracy loss detectable).
  HARD_FAIL: mean_acc_drop < 0.005 (< 0.5% loss = noise is below detection threshold).

  Why this works at N=4096: 200 outer products of scale 1/N create structured interference.
  At M_frac=2 (M=8192 patterns stored), capacity is at 2x nominal. 200 spurious patterns
  represent ~2.4% of M. Each spurious outer product interferes with 1/C of stored keys.
  Expected acc drop ~ 200/M ~ 0.024 (2.4%). Close to HARD_PASS threshold.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. M at M_frac=2.0, N=4096: M=8192.
  3. total_perturbation = N_DRIFT_STEPS / N = 200 / 4096 = 0.04883.
  4. noise_fraction = N_DRIFT_STEPS / M = 200 / 8192 = 0.02441 at M_frac=2.0.
  5. Expected acc_drop ~ noise_fraction ~ 0.024. HP=0.05 is 2x this -> achievable at M_frac=8.
  6. At M_frac=8 (M=32768): noise_fraction = 200/32768 = 0.0061. HP boundary.
     MIDDLE_BAND likely at M_frac=8; HARD_PASS at M_frac=2 only -- acceptable for rescue.

PRE-REGISTERED BANDS (empirical anchor from v3 = 0.0 gap):
  Prior anchor: v3 gap = 0.0 at noise_scale=0.01 x 100 steps.
  This probe uses N_DRIFT_STEPS=200 (20x more drift) to find the signal threshold.
  HARD_PASS: mean_acc_drop >= 0.05 at any M_frac, >= 2/3 seeds.
    Interpretation: drift detectable at practical noise levels.
  HARD_FAIL: mean_acc_drop < 0.005 across ALL M_fracs ALL seeds.
    Interpretation: N=4096 substrate is structurally immune to 200-pattern perturbation.
  MIDDLE_BAND: mean_acc_drop in [0.005, 0.05) -- partial signal, needs higher drift.

OOM CHECK:
  N=4096, C=16384: W=64MB. At M_frac=8: keys=32768*4096*4=537MB. Total ~600MB.
  Remote CPU has 16GB+ RAM. OK for CPU.

TIMEOUT ESTIMATE:
  Smoke at N=1024, M_frac=2, 1 seed, n_probe=50, N_DRIFT=200: estimate ~5s.
  FULL: N=4096, 2 M_fracs, 3 seeds, n_probe=200, N_DRIFT=200.
  N-scale: (4096/1024)^1.5 = 8x. seeds: 3. M_fracs: 2.
  Estimate: 1.5 * 5 * 8 * 3 * 2 = 360s. Safety x4 = 1440s.
  Floor: _n4096 floor = 14400s. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: kf4_drift_detect_v4_n4096
Queue: remote_cpu_queue (CPU; N=4096 Kerdock; calibrated-drift accuracy-drop rescue)
Pre-reg: preregs/2026-05-29_kf4_drift_detect_v4_n4096.md
Parent: kf4_drift_detect_v3_n4096 (HARD_FAIL gap=0); strategy_request_v269_kf4
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

# Load chunk1 for store_facts_batched, compute_retention, v3
_c1_path = REPO / "experiments" / "exp_axis1_mb_chunk1_v1.py"
_c1_spec = importlib.util.spec_from_file_location("axis1c1_kf4v4", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)

store_facts_batched = c1.store_facts_batched
compute_retention   = c1.compute_retention
v3 = c1.v3

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_FRACS_FULL  = [2.0, 8.0]
M_FRACS_SMOKE = [2.0]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

BETA      = 32.0
N_PROBE_FULL  = 200
N_PROBE_SMOKE = 50
N_DRIFT_STEPS = 200   # number of spurious outer products (no scale factor)

# Pre-registered thresholds
HP_ACC_DROP_MIN  = 0.05   # >= 5% accuracy loss from drift
HF_ACC_DROP_MAX  = 0.005  # < 0.5% = no detectable signal
HP_SEEDS_MIN     = 2


def get_output_dir(default_name: str = "kf4_drift_detect_v4_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_cell(N: int, M_frac: float, seed: int, n_probe: int,
                 device: torch.device) -> Dict:
    """Measure accuracy-drop drift signal at (N, M_frac, seed)."""
    M = int(M_frac * N)
    codebook, _ = v3.make_kerdock_4coset_codebook(N, device)
    W, keys, _vals, _key_idx, val_idx = store_facts_batched(codebook, M, seed, N, device)

    C = codebook.shape[0]

    # Baseline retention (before drift)
    acc_base = compute_retention(W, keys, val_idx, codebook, BETA, N, n_probe)

    # Apply calibrated drift: N_DRIFT_STEPS spurious outer products (scale = 1/N)
    gen = torch.Generator(device=device).manual_seed(seed + 8888)
    W_drifted = W.clone()
    for _ in range(N_DRIFT_STEPS):
        k_rnd = torch.randint(0, C, (1,), generator=gen, device=device)
        v_rnd = torch.randint(0, C, (1,), generator=gen, device=device)
        noise_k = codebook[k_rnd[0]]
        noise_v = codebook[v_rnd[0]]
        # No scale factor -- each outer product is 1.0/N (same as stored patterns)
        W_drifted = W_drifted + torch.outer(noise_v, noise_k) / N

    # Retention after drift
    acc_drifted = compute_retention(W_drifted, keys, val_idx, codebook, BETA, N, n_probe)

    acc_drop = acc_base - acc_drifted
    noise_fraction = N_DRIFT_STEPS / max(M, 1)

    print(f"    N={N} M_frac={M_frac} M={M} seed={seed} "
          f"acc_base={acc_base:.4f} acc_drifted={acc_drifted:.4f} "
          f"acc_drop={acc_drop:.4f} noise_frac={noise_fraction:.4f}", flush=True)
    return {
        "N": N, "M_frac": M_frac, "M": M, "seed": seed,
        "acc_base": round(acc_base, 5),
        "acc_drifted": round(acc_drifted, 5),
        "acc_drop": round(acc_drop, 5),
        "noise_fraction": round(noise_fraction, 5),
        "passes_hp": acc_drop >= HP_ACC_DROP_MIN,
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("KF4_V4_INCONCLUSIVE", "No cells.")

    valid_cells = [c for c in cells if c.get("acc_drop") is not None
                   and not math.isnan(c.get("acc_drop", float("nan")))]
    if not valid_cells:
        return ("KF4_V4_INCONCLUSIVE", "No valid acc_drop values.")

    all_drops = [c["acc_drop"] for c in valid_cells]
    mean_drop = sum(all_drops) / len(all_drops)
    max_drop  = max(all_drops)
    n_pass    = sum(1 for c in valid_cells if c.get("passes_hp", False))

    N = summary.get("N", N_FULL)
    detail = (f"mean_acc_drop={mean_drop:.5f} max_acc_drop={max_drop:.5f} "
              f"n_pass={n_pass}/{len(valid_cells)} "
              f"HP_min={HP_ACC_DROP_MIN} HF_max={HF_ACC_DROP_MAX} N={N}")

    # Smoke/single-M_frac case
    m_fracs_tested = list({c["M_frac"] for c in valid_cells})
    if len(m_fracs_tested) <= 1:
        smoke_label = "KF4_V4_SMOKE_PASS" if mean_drop >= HP_ACC_DROP_MIN else (
            "KF4_V4_SMOKE_MIDDLE" if mean_drop >= HF_ACC_DROP_MAX else "KF4_V4_SMOKE_FAIL"
        )
        return (smoke_label, f"SMOKE_ONLY: mean_acc_drop={mean_drop:.5f}. " + detail)

    if mean_drop < HF_ACC_DROP_MAX:
        return ("KF4_V4_HARD_FAIL",
                f"NO_ACCURACY_DROP: mean_acc_drop={mean_drop:.5f} < {HF_ACC_DROP_MAX}. "
                + detail)

    if mean_drop >= HP_ACC_DROP_MIN and n_pass >= HP_SEEDS_MIN:
        return ("KF4_V4_HARD_PASS",
                f"DRIFT_DETECTABLE: mean_acc_drop={mean_drop:.5f}. " + detail)

    return ("KF4_V4_MIDDLE_BAND",
            f"WEAK_SIGNAL: mean_acc_drop={mean_drop:.5f}. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Formula self-tests
    M_at_2 = int(2.0 * N_FULL)
    assert M_at_2 == 8192, f"M at M_frac=2: {M_at_2}"
    M_at_8 = int(8.0 * N_FULL)
    assert M_at_8 == 32768, f"M at M_frac=8: {M_at_8}"
    total_perturb = N_DRIFT_STEPS / N_FULL
    assert abs(total_perturb - 200/4096) < 1e-6, f"total_perturb: {total_perturb}"
    noise_frac_at_2 = N_DRIFT_STEPS / M_at_2
    assert abs(noise_frac_at_2 - 200/8192) < 1e-6, f"noise_frac_at_2: {noise_frac_at_2}"

    # Verdict gates
    fake_hp = [
        {"acc_drop": 0.08, "passes_hp": True, "M_frac": 2.0,
         "acc_base": 0.95, "acc_drifted": 0.87},
        {"acc_drop": 0.07, "passes_hp": True, "M_frac": 2.0,
         "acc_base": 0.93, "acc_drifted": 0.86},
        {"acc_drop": 0.09, "passes_hp": True, "M_frac": 8.0,
         "acc_base": 0.90, "acc_drifted": 0.81},
    ]
    v, msg = compute_verdict({"cells": fake_hp, "N": N_FULL})
    assert "HARD_PASS" in v, f"HP verdict gate: {v}: {msg}"

    fake_hf = [
        {"acc_drop": 0.001, "passes_hp": False, "M_frac": 2.0,
         "acc_base": 0.95, "acc_drifted": 0.949},
        {"acc_drop": 0.002, "passes_hp": False, "M_frac": 8.0,
         "acc_base": 0.90, "acc_drifted": 0.898},
    ]
    vf, _ = compute_verdict({"cells": fake_hf, "N": N_FULL})
    assert "HARD_FAIL" in vf, f"HARD_FAIL gate: {vf}"

    # Smoke forward pass (N_SMOKE=1024)
    device = torch.device("cpu")
    cell = run_one_cell(N_SMOKE, 2.0, 17, N_PROBE_SMOKE, device)
    assert "acc_drop" in cell, "acc_drop missing"
    assert not math.isnan(cell["acc_drop"]), "acc_drop NaN"
    # acc_base must be positive (substrate must store at least something)
    assert cell["acc_base"] > 0, f"acc_base not positive: {cell['acc_base']}"
    # acc_drop >= -0.05 (small negative allowed from seed variability in retention sampling)
    assert cell["acc_drop"] >= -0.05, f"acc_drop large negative: {cell['acc_drop']}"

    # 4x smoke (N_SMOKE * 4 = N_FULL = 4096 -- valid Kerdock N)
    cell4 = run_one_cell(N_SMOKE * 4, 2.0, 17, N_PROBE_SMOKE, device)
    assert "acc_drop" in cell4, "4x acc_drop missing"
    assert not math.isnan(cell4["acc_drop"]), "4x acc_drop NaN"
    assert cell4["acc_base"] > 0, f"4x acc_base not positive: {cell4['acc_base']}"

    print(f"[selftest] kf4_drift_detect_v4_n4096 PASS "
          f"acc_drop_smoke={cell['acc_drop']:.4f} acc_drop_4x={cell4['acc_drop']:.4f}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    device = torch.device("cpu")
    smoke = args.smoke

    N_cfg = N_SMOKE if smoke else N_FULL
    m_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    n_probe = N_PROBE_SMOKE if smoke else N_PROBE_FULL

    print(f"[run] kf4_drift_detect_v4_n4096 smoke={smoke} N={N_cfg} "
          f"M_fracs={m_fracs} seeds={seeds} n_probe={n_probe}", flush=True)
    t0 = time.time()

    all_cells = []
    for M_frac in m_fracs:
        print(f"\n  [M_frac={M_frac}]", flush=True)
        for seed in seeds:
            cell = run_one_cell(N_cfg, M_frac, seed, n_probe, device)
            all_cells.append(cell)
        print(f"  M_frac={M_frac} elapsed={time.time()-t0:.1f}s", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "kf4_drift_detect_v4_n4096", "N": N_cfg, "smoke": smoke,
        "M_fracs": m_fracs, "seeds": seeds, "n_probe": n_probe,
        "N_drift_steps": N_DRIFT_STEPS,
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
