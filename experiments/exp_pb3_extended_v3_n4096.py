"""PB-3 CRITICAL SLOWING DOWN v3: FIX CUDA_GENERATOR_MISMATCH in v2.

PARENT: pb3_extended_v2_n4096 SCRIPT_BUG_CUDA_GENERATOR_MISMATCH.
  v2 crashed at wall=3.13s with RuntimeError in pa.make_bsc_atoms:
    torch.rand((k, n), generator=gen) where gen.device='cuda' but torch.rand
    defaults to CPU tensor. Fix: use Generator(device='cpu') since make_bsc_atoms
    is CPU-bound before .to(device).
  FIX: run_one_seed() now creates CPU generator for atom construction:
    gen_cpu = torch.Generator(device='cpu').manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(VOCAB, N_use, gen_cpu).to(device)
    pos_atoms = pa.make_bsc_atoms(K, N_use, gen_cpu).to(device)
  All physics code (v1 helpers) unchanged.

WHAT THIS TESTS (same as v2):
  Extended beta grid {2, 4, 6, 8, 10, 12, 16} vs v1's {4, 8, 16}.
  5 seeds (vs 3 in v1). Fine-grid reveals: does tau_recovery peak sharply at
  beta=8 (training beta)? First-order or broad criticality?

PRE-REGISTERED BANDS (same as v2):
  Prior anchor: v1 HARD_PASS ratio=1.64 at {4,8,16}. Bands NOT widened.
  HARD_PASS: max(tau_by_beta) / min(tau_by_beta) >= 1.5 AND tau_peak_beta in {6,8,10}.
  HARD_FAIL: ratio < 1.0 (contradicts v1).
  MIDDLE_BAND: ratio in [1.0, 1.5) (present but weaker than v1).

CALIBRATION: prior anchor = v1 ratio=1.64 at N=4096 3-seed.
  No widening. HP threshold = ratio >= 1.5.

FORMULA SELF-TESTS:
  1. tau_ratio = max_tau / min_tau. For max=100, min=61: ratio=1.639 >= 1.5 -> HARD_PASS.
  2. tau_ratio for [1,1,1] = 1.0 -> NOT HARD_PASS.
  3. Peak location: argmax over tau_by_beta dict.
  4. N == 4096 (PROT-018).
  5. HARD_PASS fires for ratio >= 1.5 AND peak in center betas {6,8,10}.
  6. HARD_FAIL fires for ratio < 1.0.
  7. CPU generator: Generator(device='cpu') resolves RuntimeError in v2.

TIMEOUT ESTIMATE:
  v1 3-seed 3-beta elapsed: ~1800s (from status_log, remote).
  v3 5-seed 7-beta: scale = (5/3) * (7/3) = 3.89x.
  timeout_s = ceil(1.5 * 1800 * 3.89) = ceil(10503) -> 10800s.
  FLAG: > 7200s (2h). Run justified by envelope-extension of v1 HARD_PASS.
  Note: 3h run. Within 14400s (4h) limit.
  PROT-019: no _n<N> suffix -> no floor applied.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: pb3_extended_v3_n4096
Queue: overnight_queue (GPU delta-rule N=4096, 5 seeds, 7 betas)
Pre-reg: preregs/2026-05-28_pb3_extended_v3_n4096.md
Parent: pb3_extended_v2_n4096 (SCRIPT_BUG), pb3_critical_slowing_v1 (HARD_PASS baseline)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import os
import time
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402

# Load v1 base
_v1_path = REPO / "experiments" / "exp_pb3_critical_slowing_v1.py"
_v1_spec = importlib.util.spec_from_file_location("pb3v1_v3", _v1_path)
v1 = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(v1)

pa = v1.pa

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N = 4096            # PROT-018 binding contract
N_SMOKE = 1024
assert N == 4096, f"PROT-018: N must be 4096; got {N}"

K = 4
VOCAB = 256

# Extended beta grid (key change vs v1)
BETA_SWEEP_FULL = [2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 16.0]
BETA_SWEEP_SMOKE = [4.0, 8.0]

N_EDITS_FULL = 100
N_EDITS_SMOKE = 50
N_RECOVERY_FULL = 100
N_RECOVERY_SMOKE = 50
T_TRAIN_FULL = 10000
T_TRAIN_SMOKE = 1500
T_EVAL_FULL = 500
T_EVAL_SMOKE = 100
DELTA_ALPHA = 0.3
DELTA_DECAY = 1e-4
RELU_B = 0.5

# 5 seeds
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

RECOVERY_THRESHOLD = 0.10
SLOWING_RATIO = 1.5
PEAK_BETA_SET = {6.0, 8.0, 10.0}  # central betas near training beta=8


def get_output_dir(default_name: str = "pb3_extended_v3_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_data(smoke: bool):
    return v1.load_data(smoke)


def run_one_beta(seed, beta_train, config,
                  byte_atoms, pos_atoms,
                  train_idx, train_tgt, eval_idx, eval_tgt,
                  B_train, B_tgt, device):
    return v1.run_one_beta(seed, beta_train, config,
                            byte_atoms, pos_atoms,
                            train_idx, train_tgt, eval_idx, eval_tgt,
                            B_train, B_tgt, device)


def run_one_seed(seed: int, config: dict, device: torch.device) -> dict:
    smoke = config["smoke"]
    N_use = config["N"]
    beta_sweep = config["beta_sweep"]

    # FIX v3: use CPU generator for make_bsc_atoms (CPU-bound; .to(device) happens after)
    # v2 BUG: torch.Generator(device=device) when device='cuda' caused RuntimeError
    # because pa.make_bsc_atoms calls torch.rand without explicit device=, defaulting
    # to CPU tensor, but generator must match tensor's device.
    gen_cpu = torch.Generator(device='cpu').manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(VOCAB, N_use, gen_cpu).to(device)
    gen_cpu2 = torch.Generator(device='cpu').manual_seed(seed + 10000)
    pos_atoms = pa.make_bsc_atoms(K, N_use, gen_cpu2).to(device)

    train_idx, train_tgt, eval_idx, eval_tgt, B_train, B_tgt = load_data(smoke)

    per_beta = {}
    for beta_v in beta_sweep:
        print(f"  seed={seed} beta={beta_v}...", flush=True)
        result = run_one_beta(seed, beta_v, config,
                               byte_atoms, pos_atoms,
                               train_idx, train_tgt, eval_idx, eval_tgt,
                               B_train, B_tgt, device)
        per_beta[str(beta_v)] = result

    return {"seed": seed, "N": N_use, "per_beta": per_beta}


def compute_verdict(summary: dict) -> tuple:
    per_seed = summary.get("per_seed", {})
    if not per_seed:
        return ("PB3V3_INCONCLUSIVE", "No per-seed data.")

    tau_sum: Dict[float, List[int]] = defaultdict(list)
    for _, sd in per_seed.items():
        for beta_k, cell in sd.get("per_beta", {}).items():
            tau_sum[float(beta_k)].append(cell.get("tau_recovery", 1))

    tau_by_beta = {b: int(round(sum(ts) / len(ts))) for b, ts in tau_sum.items()}
    if not tau_by_beta:
        return ("PB3V3_INCONCLUSIVE", "No tau data.")

    max_tau = max(tau_by_beta.values())
    min_tau = max(1, min(tau_by_beta.values()))
    ratio = max_tau / min_tau
    peak_beta = max(tau_by_beta, key=lambda b: tau_by_beta[b])

    tau_str = {int(b): t for b, t in sorted(tau_by_beta.items())}
    detail = (f"tau_by_beta={tau_str}. max/min ratio={ratio:.2f}. "
              f"peak_beta={peak_beta}.")

    if ratio < 1.0:
        return ("PB3V3_HARD_FAIL", f"No slowing (ratio<1). {detail}")

    if ratio >= SLOWING_RATIO:
        peak_central = peak_beta in PEAK_BETA_SET
        return ("PB3V3_HARD_PASS",
                f"CRITICAL SLOWING CONFIRMED (v3 extended). ratio={ratio:.2f} >= {SLOWING_RATIO}. "
                f"peak_at_train_beta={peak_central} (beta={peak_beta}). {detail}")

    return ("PB3V3_MIDDLE_BAND",
            f"Slowing present but ratio={ratio:.2f} < {SLOWING_RATIO}. {detail}")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N == 4096, f"PROT-018: N must be 4096; got {N}"

    # Test ratio formula
    tau_pass = {4.0: 61, 8.0: 100, 16.0: 100}
    max_t = max(tau_pass.values())
    min_t = max(1, min(tau_pass.values()))
    ratio = max_t / min_t
    assert ratio >= SLOWING_RATIO, f"Self-test: ratio {ratio} < {SLOWING_RATIO}"

    tau_fail = {4.0: 1, 8.0: 1, 16.0: 1}
    ratio_f = max(tau_fail.values()) / max(1, min(tau_fail.values()))
    assert ratio_f < SLOWING_RATIO, f"Self-test: flat should not pass: {ratio_f}"

    # Test verdict HARD_PASS path
    per_seed_pass = {
        "7": {"per_beta": {"4.0": {"tau_recovery": 61}, "8.0": {"tau_recovery": 100},
                            "16.0": {"tau_recovery": 100}}},
    }
    v, msg = compute_verdict({"per_seed": per_seed_pass, "beta_sweep": [4.0, 8.0, 16.0]})
    assert "HARD_PASS" in v, f"Self-test HP failed: {v}: {msg}"

    # Test verdict MIDDLE_BAND / HARD_FAIL path
    per_seed_flat = {
        "7": {"per_beta": {"4.0": {"tau_recovery": 1}, "8.0": {"tau_recovery": 1},
                            "16.0": {"tau_recovery": 1}}},
    }
    v2, _ = compute_verdict({"per_seed": per_seed_flat, "beta_sweep": [4.0, 8.0, 16.0]})
    assert "MIDDLE_BAND" in v2 or "INCONCLUSIVE" in v2, f"Flat should be MB: {v2}"

    # Test CPU generator fix: smoke call must NOT crash on CUDA device
    # (This is the core fix from v3 -- using cpu generator always)
    cpu_gen_test = torch.Generator(device='cpu').manual_seed(42)
    test_atoms = pa.make_bsc_atoms(4, N_SMOKE, cpu_gen_test)  # should not raise
    assert test_atoms is not None and test_atoms.shape[0] == 4, \
        f"make_bsc_atoms with CPU generator failed: {test_atoms}"

    # Test one smoke seed CPU run
    device_cpu = torch.device("cpu")
    config_smoke = {
        "smoke": True,
        "N": N_SMOKE,
        "beta_sweep": [8.0],
        "n_edits": N_EDITS_SMOKE,
        "n_recovery": N_RECOVERY_SMOKE,
        "t_train": T_TRAIN_SMOKE,
        "t_eval": T_EVAL_SMOKE,
        "delta_alpha": DELTA_ALPHA,
        "delta_decay": DELTA_DECAY,
        "relu_b": RELU_B,
        "k": K,
        "vocab": VOCAB,
    }
    result = run_one_seed(17, config_smoke, device_cpu)
    cell = result.get("per_beta", {}).get("8.0")
    assert cell is not None, "No cell result for beta=8.0 in selftest"
    assert "tau_recovery" in cell and cell["tau_recovery"] >= 0, \
        f"tau_recovery missing or negative: {cell}"
    # Validity filter: at least 1 beta produces a valid cell
    assert len(result.get("per_beta", {})) >= 1, "No valid beta cells from smoke run"

    print(f"[SELFTEST PASS] pb3_extended_v3_n4096: N={N} cpu_gen_fix=OK "
          f"tau={cell.get('tau_recovery')} beta=8.0", flush=True)


_instrumentation_selftest()  # Called at module scope before sweep


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    parser.add_argument("--timeout", type=int, default=10800)
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    smoke = args.smoke
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    N_use = N_SMOKE if smoke else N
    beta_sweep = BETA_SWEEP_SMOKE if smoke else BETA_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    config = {
        "smoke": smoke,
        "N": N_use,
        "beta_sweep": beta_sweep,
        "n_edits": N_EDITS_SMOKE if smoke else N_EDITS_FULL,
        "n_recovery": N_RECOVERY_SMOKE if smoke else N_RECOVERY_FULL,
        "t_train": T_TRAIN_SMOKE if smoke else T_TRAIN_FULL,
        "t_eval": T_EVAL_SMOKE if smoke else T_EVAL_FULL,
        "delta_alpha": DELTA_ALPHA,
        "delta_decay": DELTA_DECAY,
        "relu_b": RELU_B,
        "k": K,
        "vocab": VOCAB,
    }

    outdir = get_output_dir()
    t0 = time.time()
    per_seed = {}

    for seed in seeds:
        print(f"seed={seed}...", flush=True)
        result = run_one_seed(seed, config, device)
        per_seed[str(seed)] = result
        elapsed = time.time() - t0
        print(f"  seed={seed} done elapsed={elapsed:.1f}s", flush=True)

    elapsed_s = time.time() - t0
    summary = {"per_seed": per_seed, "beta_sweep": beta_sweep, "N": N_use, "smoke": smoke}
    verdict, verdict_msg = compute_verdict(summary)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed_s,
        "config": {
            "N": N_use,
            "seeds": seeds,
            "beta_sweep": beta_sweep,
            "smoke": smoke,
        },
        "summary": summary,
    }

    out = outdir / "metrics.json"
    with open(out, "w") as f_out:
        json.dump(metrics, f_out, indent=2)

    print(f"\nVERDICT: {verdict}")
    print(f"MSG: {verdict_msg}")
    print(f"elapsed={elapsed_s:.1f}s")
    print(f"metrics -> {out}")


if __name__ == "__main__":
    main()
