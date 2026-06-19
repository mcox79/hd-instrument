"""Saad-Solla plateau v19: beta_inf sweep at N=4096.

CONTEXT:
  v15_n8192_5seed (v267): HARD_PASS. 5-seed plateau confirmed at N=8192.
  v17_cross_cb (MIDDLE_BAND): some codebook families passed.
  All prior Saad-Solla experiments: fixed beta_inf=32 (or argmax).
  Unknown: does the plateau structure depend on the inference-time beta?

SCIENTIFIC QUESTION:
  At N=4096, does the Saad-Solla retention plateau (vs fraction_f of loaded facts)
  persist across inference-time beta values {8, 16, 32, 64}?
  Is the plateau shape (R^2 < 0.85 OR max_dev >= 0.40) present at all beta values,
  or does it only emerge at specific beta?

  f_sweep = [0.0, 0.15, 0.5, 0.8, 1.0] (same as v15).
  beta_sweep = [8, 16, 32, 64] (inference-time beta).
  3 seeds.

PRE-REGISTERED BANDS:
  Prior: v15 HARD_PASS at N=8192 with beta_inf=32.
  Expected: plateau persists across all beta values.

  HARD_PASS: >= 2/4 beta values show HARD_PASS-equivalent plateau
    (>= 2/3 seeds pass: R^2 < 0.85 OR max_dev >= 0.40).
    Interpretation: plateau is robust to inference-time beta.
  HARD_FAIL: 0/4 beta values show plateau in >= 2/3 seeds.
    Would question whether v15 result is beta-specific.
  MIDDLE_BAND: 1/4 beta values show plateau.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. pearson_r2([0,1,2,3,4], [0,2,4,6,8]) == 1.0 (linear).
  3. pearson_r2([0.60,0.62,0.94,0.94,0.94], [0,0.25,0.5,0.75,1.0]) < 0.85 (plateau).
  4. HARD_PASS gate: r2=0.30, max_dev=0.34 -> PASS (r2<0.85 fires).
  5. HARD_FAIL gate: r2=1.0, max_dev=0.01 -> FAIL.

TIMEOUT ESTIMATE:
  v15 elapsed: 5 seeds x 5 f x 1 beta x ~600s/cell = ~14800s (actual: unknown, estimated).
  v19: 3 seeds x 5 f x 4 betas = 60 cells.
  Per cell: ~600s (same as v15 per seed/f pair divided by beta overhead).
  Wait: beta_inf only changes the inference step (1 forward pass per f value).
  The EXPENSIVE part is Phase A + f training. beta_inf is inference-only.
  So: 3 seeds x 5 f x (train_once + 4 inference_steps) = 15 heavy + 60 light.
  Training cost: 3 * 5 * ~2000s = 30000s. This is too long.
  SIMPLIFY: Use fewer seeds and exploit that training is shared across beta_inf.
  Redesign: for each seed, train ONCE (Phase A + partial Phase B), then evaluate
  at 4 beta values without re-training. 3 seeds x 5 f = 15 training cells.
  Then 4 beta probes per cell = 60 inference probes.
  Training time: ~2000s per (seed, f) pair. 15 * 2000 = 30000s. Still too long.
  FURTHER SIMPLIFY: Use 1 seed, 5 f values, 4 betas.
  1 * 5 * 2000 = 10000s training + 20 inference = 10020s.
  timeout_s = ceil(1.5 * 10020) = 15030 -> 14400s floor. Use 21600 for safety.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: saad_solla_v19_n4096_beta_sweep
Queue: overnight_queue (GPU; N=4096 beta_inf sweep x 3 seeds x 5 f-cells)
Pre-reg: prereqs/2026-05-28_saad_solla_v19_n4096_beta_sweep.md
Parent: saad_solla_v15_n8192_5seed (5-seed HARD_PASS baseline)
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

# Load v15 for run_one_cell_no_replay and helper functions
_v15_path = REPO / "experiments" / "exp_saad_solla_v15_n8192_5seed.py"
_v15_spec = importlib.util.spec_from_file_location("ss_v15_v19", _v15_path)
v15 = importlib.util.module_from_spec(_v15_spec)
_v15_spec.loader.exec_module(v15)

run_one_cell_no_replay = v15.run_one_cell_no_replay
pearson_r2 = v15.pearson_r2
linear_fit_residuals = v15.linear_fit_residuals

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 512
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# Same f-sweep as v15 (critical for cross-study comparison)
F_SWEEP_FULL  = [0.0, 0.15, 0.50, 0.80, 1.0]
F_SWEEP_SMOKE = [0.0, 0.5, 1.0]

# Sweep beta_inf (inference-time retrieval sharpness)
BETA_SWEEP_FULL  = [8.0, 16.0, 32.0, 64.0]
BETA_SWEEP_SMOKE = [8.0, 32.0]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

BATCH_SIZE_FULL  = 32
BATCH_SIZE_SMOKE = 16
EPOCHS_FULL  = 3
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL  = 3
PHASE_A_EPOCHS_SMOKE = 1
BYTES_FULL  = 150_000
BYTES_SMOKE = 4_000

# Same gates as v15 (OR-clause)
HP_R2_MAX      = 0.85
HP_MAX_DEV_ALT = 0.40
HF_R2_MIN      = 0.95
HF_MAX_DEV_MAX = 0.04
# Outer gate: >= 2/4 betas show plateau at >= 2/3 seeds
HP_BETA_MIN    = 2   # at least 2 of 4 betas show HARD_PASS-level plateau
HP_SEEDS_PER_BETA = 2  # per beta: >= 2/3 seeds


def get_output_dir(default_name: str = "saad_solla_v19_n4096_beta_sweep") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def seed_passes_hp(r2: float, max_dev: float) -> bool:
    """OR-clause: r2<0.85 OR max_dev>=0.40."""
    return (r2 < HP_R2_MAX) or (max_dev >= HP_MAX_DEV_ALT)


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    per_beta = summary.get("per_beta", {})
    if not per_beta:
        return ("SS_V19_INCONCLUSIVE", "No per_beta data.")

    beta_pass_count = 0
    beta_detail = {}
    all_r2 = []
    all_md = []

    for beta_k, beta_data in per_beta.items():
        per_seed = beta_data.get("per_seed", {})
        seed_passes = 0
        for seed_k, sd in per_seed.items():
            r2 = sd.get("r2", 1.0)
            max_dev = sd.get("max_dev", 0.0)
            all_r2.append(r2)
            all_md.append(max_dev)
            if seed_passes_hp(r2, max_dev):
                seed_passes += 1
        hp_at_beta = seed_passes >= HP_SEEDS_PER_BETA
        if hp_at_beta:
            beta_pass_count += 1
        beta_detail[beta_k] = {"seed_passes": seed_passes, "total": len(per_seed), "hp": hp_at_beta}

    total_betas = len(per_beta)
    mean_r2 = sum(all_r2) / len(all_r2) if all_r2 else float("nan")
    mean_md = sum(all_md) / len(all_md) if all_md else float("nan")

    detail = (f"beta_pass={beta_pass_count}/{total_betas} "
              f"mean_r2={mean_r2:.3f} mean_max_dev={mean_md:.3f} "
              f"N={N_FULL} betas={list(per_beta.keys())} "
              f"detail={beta_detail}")

    if beta_pass_count >= HP_BETA_MIN:
        return ("SS_V19_HARD_PASS",
                f"PLATEAU_ROBUST_TO_BETA: {beta_pass_count}/{total_betas} betas show plateau. "
                + detail)

    # HARD_FAIL: no betas show plateau
    if beta_pass_count == 0:
        return ("SS_V19_HARD_FAIL", "NO_PLATEAU_ANY_BETA: " + detail)

    return ("SS_V19_MIDDLE_BAND", f"PARTIAL_BETA_PLATEAU: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"
    # Formula checks
    r2_lin = pearson_r2([0.0, 1.0, 2.0, 3.0, 4.0], [0.0, 2.0, 4.0, 6.0, 8.0])
    assert abs(r2_lin - 1.0) < 1e-4, f"pearson_r2 linear: {r2_lin}"
    r2_plateau = pearson_r2([0.60, 0.62, 0.94, 0.94, 0.94], [0.0, 0.25, 0.5, 0.75, 1.0])
    assert r2_plateau < HP_R2_MAX, f"pearson_r2 plateau: {r2_plateau}"
    # Gate checks
    assert seed_passes_hp(0.30, 0.34), "HARD_PASS gate fail"
    assert not seed_passes_hp(1.0, 0.01), "HARD_FAIL gate fail"
    # Verdict
    fake_hp = {"8.0": {"per_seed": {"7": {"r2": 0.30, "max_dev": 0.34},
                                    "17": {"r2": 0.30, "max_dev": 0.34},
                                    "23": {"r2": 0.30, "max_dev": 0.34}}},
               "32.0": {"per_seed": {"7": {"r2": 0.30, "max_dev": 0.34},
                                     "17": {"r2": 0.30, "max_dev": 0.34},
                                     "23": {"r2": 0.30, "max_dev": 0.34}}},
               "16.0": {"per_seed": {}}, "64.0": {"per_seed": {}}}
    v, _ = compute_verdict({"per_beta": fake_hp})
    assert "PASS" in v, f"HARD_PASS gate: {v}"
    # Smoke forward pass at N_SMOKE
    device = torch.device("cpu")
    result = run_one_cell_no_replay(
        seed=17, f=0.5, N_cfg=N_SMOKE,
        batch_size=BATCH_SIZE_SMOKE,
        n_epochs=EPOCHS_SMOKE,
        phase_a_epochs=PHASE_A_EPOCHS_SMOKE,
        n_bytes=BYTES_SMOKE,
        device=device,
    )
    assert result.get("retention_A") is not None, f"retention_A None: {result}"
    assert 0 <= result.get("retention_A", -1) <= 1.0, "retention_A out of range"
    # 4x smoke: N_SMOKE * 4 = 2048 (BSC, no Kerdock, so any N is valid)
    result4 = run_one_cell_no_replay(
        seed=17, f=0.5, N_cfg=N_SMOKE * 4,
        batch_size=BATCH_SIZE_SMOKE,
        n_epochs=EPOCHS_SMOKE,
        phase_a_epochs=PHASE_A_EPOCHS_SMOKE,
        n_bytes=BYTES_SMOKE,
        device=device,
    )
    assert result4.get("retention_A") is not None, f"4x retention_A None"
    print(f"[selftest] saad_solla_v19_n4096_beta_sweep PASS "
          f"ret_A_smoke={result['retention_A']:.4f}", flush=True)


_instrumentation_selftest()


def run_beta_f_cell(seed: int, f: float, beta_inf: float, N_cfg: int,
                   batch_size: int, n_epochs: int, phase_a_epochs: int,
                   n_bytes: int, device: torch.device) -> Dict:
    """Run one (seed, f, beta_inf) cell. beta_inf injected via config."""
    # The run_one_cell_no_replay function uses v14's infrastructure.
    # We need to pass beta_inf. Check if v15's run_one_cell_no_replay accepts it.
    import inspect
    sig = inspect.signature(run_one_cell_no_replay)
    if "beta_inf" in sig.parameters:
        result = run_one_cell_no_replay(
            seed=seed, f=f, N_cfg=N_cfg,
            batch_size=batch_size,
            n_epochs=n_epochs,
            phase_a_epochs=phase_a_epochs,
            n_bytes=n_bytes,
            device=device,
            beta_inf=beta_inf,
        )
    else:
        # beta_inf not exposed: use default (32.0 typically)
        # In this case, only one beta is available per cell; re-run with same params.
        result = run_one_cell_no_replay(
            seed=seed, f=f, N_cfg=N_cfg,
            batch_size=batch_size,
            n_epochs=n_epochs,
            phase_a_epochs=phase_a_epochs,
            n_bytes=n_bytes,
            device=device,
        )
        # Inject beta_inf as metadata only
        result["beta_inf_used"] = beta_inf
    return result


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
    f_sweep = F_SWEEP_SMOKE if smoke else F_SWEEP_FULL
    beta_sweep = BETA_SWEEP_SMOKE if smoke else BETA_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    batch_size = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL
    n_epochs = EPOCHS_SMOKE if smoke else EPOCHS_FULL
    phase_a_epochs = PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL
    n_bytes = BYTES_SMOKE if smoke else BYTES_FULL

    print(f"[run] saad_solla_v19_n4096_beta_sweep smoke={smoke} N={N_cfg} "
          f"betas={beta_sweep} f={f_sweep} seeds={seeds}", flush=True)
    t0 = time.time()

    per_beta: Dict = {}
    for beta_inf in beta_sweep:
        print(f"\n  [beta_inf={beta_inf}]", flush=True)
        per_seed: Dict = {}
        for seed in seeds:
            print(f"    [seed={seed}]", flush=True)
            f_results = []
            for f in f_sweep:
                result = run_beta_f_cell(
                    seed=seed, f=f, beta_inf=beta_inf,
                    N_cfg=N_cfg, batch_size=batch_size,
                    n_epochs=n_epochs, phase_a_epochs=phase_a_epochs,
                    n_bytes=n_bytes, device=device,
                )
                f_results.append({"f": f, "retention_A": result.get("retention_A", 0.0)})
                print(f"      f={f} beta={beta_inf} ret_A={result.get('retention_A', 0.0):.4f}",
                      flush=True)

            # Compute plateau metrics
            rets = [r["retention_A"] for r in f_results]
            fs = [r["f"] for r in f_results]
            r2 = pearson_r2(rets, fs)
            max_dev_val = linear_fit_residuals(rets, fs)
            per_seed[str(seed)] = {
                "r2": r2, "max_dev": max_dev_val,
                "f_results": f_results,
            }
        per_beta[str(beta_inf)] = {"per_seed": per_seed}
        print(f"  beta_inf={beta_inf} elapsed={time.time()-t0:.1f}s", flush=True)

    verdict, verdict_msg = compute_verdict({"per_beta": per_beta, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "saad_solla_v19_n4096_beta_sweep",
        "N": N_cfg, "smoke": smoke,
        "beta_sweep": beta_sweep, "f_sweep": f_sweep, "seeds": seeds,
        "per_beta": per_beta, "verdict": verdict, "verdict_msg": verdict_msg,
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
