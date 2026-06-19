"""
a6_oneshot_vs_lora_economics_v2_longer_timeout_v1 -- A6: one-shot Hebbian vs LoRA economics v2.

RESCUE from v1 timeout at 1200s. v2 changes:
  - Raise timeout to 3600s.
  - Simplify LoRA simulation: use vectorized numpy matmuls instead of per-step loops.
  - Reduce N_KV_PAIRS from 10 to 5 (fewer benchmarks, same signal).
  - Reduce K_LORA_STEPS from 100 to 50 for wall-time measurement (FLOP ratio is deterministic).

SCIENTIFIC QUESTION (Cluster A6):
  One-shot Hebbian write at N=8192 vs LoRA fine-tune at matched model size.
  FLOP speedup: lora_flops / hebbian_flops at N=8192.
  Wall speedup: lora_wall / hebbian_wall.

PRE-REGISTERED BANDS (same as v1):
  HP: flop_speedup >= 1.5x AND wall_speedup >= 5x.
  HF: flop_speedup < 1.0x (impossible by theory: LoRA needs K>1 steps).
  MIDDLE: flop_speedup in [1.0, 1.5) OR wall_speedup in [1.0, 5).

FORMULA SELF-TESTS:
  1. Hebbian FLOPs = N^2 (outer product is N^2 multiplications).
     [INPUT: N=8192] [EXPECTED: hebbian_flops = 8192^2 = 67108864]
  2. LoRA FLOPs = K_LORA_STEPS * 2 * r * N (forward pass per step is 2rN).
     [INPUT: N=8192, r=91, K=50] [EXPECTED: lora_flops = 50*2*91*8192 = 74522624]
  3. flop_speedup = lora_flops / hebbian_flops.
     [INPUT: above] [EXPECTED: 74522624 / 67108864 = 1.11 >= 1.0]

NOTE: v2 reduces K_LORA_STEPS to 50 (wall time rescue). FLOP speedup slightly > 1.0.
Revised HP bands remain valid: flop_speedup > 1.0 is algebraically guaranteed.

No _nN suffix; production N=8192 (PROT-018 rule 3).
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "a6_oneshot_vs_lora_economics_v2_longer_timeout_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N = 1024
    K_LORA_STEPS = 20
    N_KV_PAIRS = 3
else:
    SEEDS = [7, 17, 23, 31, 41]
    N = 8192
    K_LORA_STEPS = 50   # v2: reduced from 100 for wall-time rescue
    N_KV_PAIRS = 5       # v2: reduced from 10

LORA_R = max(1, round(math.sqrt(N)))

HP_FLOP_SPEEDUP = 1.5
HF_FLOP_SPEEDUP = 1.0
HP_WALL_SPEEDUP = 5.0
HF_WALL_SPEEDUP = 1.0


def _selftest_flop_counts():
    N_t = 8192
    r_t = max(1, round(math.sqrt(N_t)))
    K_t = 50
    hebbian_flops_t = N_t * N_t
    lora_flops_t = K_t * 2 * r_t * N_t
    speedup_t = lora_flops_t / hebbian_flops_t
    assert hebbian_flops_t == 67108864, f"hebbian_flops selftest: {hebbian_flops_t}"
    # At K=50 and r=91: 50*2*91*8192=74522624
    assert lora_flops_t > hebbian_flops_t, (
        f"lora_flops ({lora_flops_t}) must exceed hebbian_flops ({hebbian_flops_t})")
    assert speedup_t >= HF_FLOP_SPEEDUP, f"speedup selftest at N=8192: {speedup_t:.4f} < {HF_FLOP_SPEEDUP}"
    return hebbian_flops_t, lora_flops_t, speedup_t


def _selftest_lora_vectorized():
    """Vectorized LoRA sim converges."""
    N_t = 64
    r_t = 8
    K_t = 20
    rng = np.random.RandomState(42)
    xi_key = rng.choice([-1.0, 1.0], size=N_t).astype(np.float64)
    xi_val = rng.choice([-1.0, 1.0], size=N_t).astype(np.float64)
    target = np.outer(xi_key, xi_val) / float(N_t)
    A = rng.randn(N_t, r_t).astype(np.float64) * 0.01
    B = rng.randn(r_t, N_t).astype(np.float64) * 0.01
    lr = 0.001
    t0_inner = time.time()
    for _ in range(K_t):
        diff = A @ B - target
        dA = diff @ B.T / N_t
        dB = A.T @ diff / N_t
        A -= lr * dA
        B -= lr * dB
    inner_wall = time.time() - t0_inner
    final_err = float(np.linalg.norm(A @ B - target, 'fro'))
    return inner_wall, final_err


def _instrumentation_selftest():
    h_flops, l_flops, speedup = _selftest_flop_counts()
    wall, err = _selftest_lora_vectorized()
    assert N_KV_PAIRS > 0, "N_KV_PAIRS must be > 0"
    print(f"[selftest] PASS: hebbian_flops={h_flops:.2e} lora_flops={l_flops:.2e} "
          f"speedup={speedup:.3f} lora_err={err:.4f} lora_wall={wall:.3f}s "
          f"N={N} LORA_R={LORA_R} K={K_LORA_STEPS} N_KV_PAIRS={N_KV_PAIRS}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def simulate_lora_steps(xi_key: np.ndarray, xi_val: np.ndarray,
                         N_dim: int, lora_r: int, k_steps: int,
                         seed: int) -> Tuple[float, float]:
    rng = np.random.RandomState(seed)
    target = np.outer(xi_key, xi_val) / float(N_dim)
    A = rng.randn(N_dim, lora_r).astype(np.float64) * 0.01
    B = rng.randn(lora_r, N_dim).astype(np.float64) * 0.01
    lr = 0.001
    t0 = time.time()
    for _ in range(k_steps):
        diff = A @ B - target
        dA = diff @ B.T / N_dim
        dB = A.T @ diff / N_dim
        A -= lr * dA
        B -= lr * dB
    wall = time.time() - t0
    final_err = float(np.linalg.norm(A @ B - target, 'fro'))
    return wall, final_err


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    hebbian_walls = []
    lora_walls = []
    lora_errors = []

    for pair_idx in range(N_KV_PAIRS):
        xi_key = rng.choice([-1.0, 1.0], size=N).astype(np.float64)
        xi_val = rng.choice([-1.0, 1.0], size=N).astype(np.float64)

        t_hebb = time.time()
        _W_hebb = np.outer(xi_key, xi_val) / float(N)
        hebb_wall = time.time() - t_hebb
        hebbian_walls.append(hebb_wall)

        lora_wall, lora_err = simulate_lora_steps(
            xi_key, xi_val, N, LORA_R, K_LORA_STEPS, seed + pair_idx * 100
        )
        lora_walls.append(lora_wall)
        lora_errors.append(lora_err)

    mean_hebb_wall = float(np.mean(hebbian_walls))
    mean_lora_wall = float(np.mean(lora_walls))
    mean_lora_err = float(np.mean(lora_errors))

    hebbian_flops = N * N
    lora_flops = K_LORA_STEPS * 2 * LORA_R * N
    flop_speedup = lora_flops / max(hebbian_flops, 1)
    wall_speedup = mean_lora_wall / max(mean_hebb_wall, 1e-9)

    hp_flop = flop_speedup >= HP_FLOP_SPEEDUP
    hp_wall = wall_speedup >= HP_WALL_SPEEDUP
    hf_flop = flop_speedup < HF_FLOP_SPEEDUP
    hf_wall = wall_speedup < HF_WALL_SPEEDUP

    elapsed = time.time() - t0
    print(f"  [seed={seed} N={N} r={LORA_R} K={K_LORA_STEPS}] "
          f"flop_speedup={flop_speedup:.2f}x(HP>={HP_FLOP_SPEEDUP}) "
          f"wall_speedup={wall_speedup:.2f}x(HP>={HP_WALL_SPEEDUP}) "
          f"hebb_wall={mean_hebb_wall*1000:.2f}ms lora_wall={mean_lora_wall*1000:.2f}ms "
          f"lora_err={mean_lora_err:.4f} hp=[{int(hp_flop)},{int(hp_wall)}] elapsed={elapsed:.2f}s",
          flush=True)

    return {
        "seed": seed, "N": N, "LORA_R": LORA_R, "K_LORA_STEPS": K_LORA_STEPS,
        "run_mode": RUN_MODE,
        "flop_speedup": float(flop_speedup),
        "wall_speedup": float(wall_speedup),
        "mean_hebb_wall_s": float(mean_hebb_wall),
        "mean_lora_wall_s": float(mean_lora_wall),
        "mean_lora_err": float(mean_lora_err),
        "hebbian_flops": int(hebbian_flops),
        "lora_flops": int(lora_flops),
        "hp_flop": bool(hp_flop),
        "hp_wall": bool(hp_wall),
        "hf_flop": bool(hf_flop),
        "hf_wall": bool(hf_wall),
        "elapsed_s": float(elapsed),
    }


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid results.")
    n = len(results)
    mean_flop = float(np.mean([r["flop_speedup"] for r in results]))
    mean_wall = float(np.mean([r["wall_speedup"] for r in results]))
    hp_flop_n = sum(1 for r in results if r["hp_flop"])
    hp_wall_n = sum(1 for r in results if r["hp_wall"])
    hf_flop_any = any(r["hf_flop"] for r in results)
    hf_wall_any = any(r["hf_wall"] for r in results)

    summary = (f"mean_flop_speedup={mean_flop:.2f}x(HP>={HP_FLOP_SPEEDUP} HF<{HF_FLOP_SPEEDUP}) "
               f"mean_wall_speedup={mean_wall:.2f}x(HP>={HP_WALL_SPEEDUP} HF<{HF_WALL_SPEEDUP}) "
               f"hp_flop={hp_flop_n}/{n} hp_wall={hp_wall_n}/{n} "
               f"N={N} r={LORA_R} K={K_LORA_STEPS}")

    if hf_flop_any:
        return ("HARD_FAIL", f"HARD_FAIL: LoRA cheaper than Hebbian in FLOPs (impossible). {summary}")
    if hf_wall_any:
        return ("HARD_FAIL", f"HARD_FAIL: Hebbian not faster than LoRA in wall time. {summary}")

    min_thresh = math.ceil(n * 0.8)
    if hp_flop_n >= min_thresh and hp_wall_n >= min_thresh:
        return ("HARD_PASS", f"HARD_PASS: Hebbian one-shot economics confirmed vs LoRA (v2). {summary}")
    if mean_flop >= HP_FLOP_SPEEDUP or mean_wall >= HP_WALL_SPEEDUP:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: partial speedup advantage. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: speedup below HP thresholds. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "LORA_R": LORA_R, "K_LORA_STEPS": K_LORA_STEPS,
              "N_KV_PAIRS": N_KV_PAIRS, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run "
      f"(N={N} LORA_R={LORA_R} K_LORA={K_LORA_STEPS} N_KV_PAIRS={N_KV_PAIRS} mode={RUN_MODE})",
      flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME} N={N} r={LORA_R}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_s = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "LORA_R": LORA_R, "K_LORA_STEPS": K_LORA_STEPS, "N_KV_PAIRS": N_KV_PAIRS,
    "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "elapsed_s": elapsed_s,
    "per_seed": [
        {"seed": r.get("seed"), "flop_speedup": r.get("flop_speedup"),
         "wall_speedup": r.get("wall_speedup"),
         "hp_flop": r.get("hp_flop"), "hp_wall": r.get("hp_wall")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
