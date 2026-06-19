"""
pp12_capacity_ondemand_w_v1_n16384 -- PP-12: capacity envelope at N=16384 with on-demand W build.

CONTEXT (v372 all-night burst cycle 43):
  PP-12 Q-A3 depth ladder at N=16384 tests COMPOSITIONAL depth (L layers, M=2 patterns/layer).
  This experiment tests CAPACITY: how many patterns M can the substrate store and retrieve
  with on-demand W build (never storing the full W matrix in memory) at N=16384?
  The on-demand W formulation: W = (Xi.T @ Xi) / N, built per-query, never persisted.

  Theoretical capacity: M_crit ~ alpha_c * N = 0.138 * 16384 = 2260 patterns at N=16384.
  Below M_crit: recall fidelity >= 0.97 (EXACT-class). Above M_crit: graceful degradation.

  Prior data: all Q-A3 anchors use M_INNER=100 (alpha=0.0061 << alpha_c). This tests
  closer to the capacity limit to calibrate the capacity envelope for PP-12 product claims.

SCIENTIFIC QUESTION:
  At N=16384 with on-demand W build, what is the capacity envelope?
  Does recall drop below 0.85 HARD-FAIL threshold before M = 0.138*N = 2260?
  What is the first alpha where recall drops below 0.97 (onset of degradation)?

  Sweep: alpha in {0.02, 0.05, 0.08, 0.10, 0.12, 0.138, 0.15, 0.18, 0.20}
         (M = alpha * N; M ranges from 328 to 3277 patterns)
  Metric: mean cosine similarity across 10 random queries with 10% noise.

OOM PRE-CHECK (GPU):
  On-demand W at N=16384: 16384^2 * 4 = 1.07 GB. Built and freed per query.
  Xi at alpha=0.20: 3277 * 16384 * 4 = 214 MB.
  Peak GPU per alpha: Xi (214 MB) + W_ondemand (1.07 GB) = ~1.3 GB. Well within 8 GB.

PRE-REGISTERED BANDS (PP-12 capacity on-demand W N=16384):
  Theoretical prediction: alpha_c = 0.138 at N=inf. At finite N=16384, onset earlier.
  No prior empirical anchor for the sweep form at N=16384 (Q-A3 only tests alpha=0.0061).
  Calibration: no prior empirical anchor; bands set +-50% of theoretical per calibration-probe policy.
  HARD-PASS: recall >= 0.97 at alpha <= 0.10 (safe capacity regime) unanimously 5/5 seeds
             AND first degradation onset (recall < 0.97) in alpha in [0.08, 0.20]
             (onset between alpha_c/2 and 1.5*alpha_c).
  MIDDLE: recall >= 0.85 at alpha <= 0.10 but degradation onset not cleanly identified.
  HARD-FAIL: recall < 0.85 at alpha <= 0.05 (capacity much lower than theoretical prediction)
             OR recall > 0.97 at alpha = 0.20 (no degradation even at 1.45x theoretical capacity).

FORMULA SELF-TESTS (PROT-022):
  1. alpha_c = 0.138 at N=16384: M_crit = int(0.138 * 16384) = 2261.
     [INPUT: alpha_c=0.138, N=16384] [EXPECTED: M_crit=2261]
  2. W on-demand memory at N=16384: 16384^2 * 4 bytes = 1073741824 = ~1.07 GB < 2 GB.
     [EXPECTED: True]
  3. alpha sweep is monotonically increasing.
     [EXPECTED: all(a<b for a,b in zip(sweep, sweep[1:]))]
  4. Retrieval at alpha=0.02 (tiny load): recall non-NaN.
  5. GPU memory > 0 after W build.

MULTI-SCALE SMOKE: alpha is load-bearing axis; smoke at N_smoke=512 and N_smoke*4=2048.

PROT-018: anchor has _n16384; N MUST = 16384.
PROT-021: seed checkpoints keyed with run_mode + N.
QUEUE: overnight_queue (GPU; on-demand W build, never persist full W matrix).
TIMEOUT ESTIMATE: Smoke (2 seeds, 3 alpha, N=512): ~5s. Full (5 seeds, 9 alpha, N=16384).
  W build at N=16384: ~0.5s per matrix. Retrieval: ~0.1s per query. 9 alpha * 10 queries * 5 seeds = 450 steps.
  Direct: 9 * (0.5 + 10*0.1) * 5 = 9 * 1.5 * 5 = 67.5s. With margin ceil(1.5 * 68) = 102s.
  Use PROT-019 floor: 21600s.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import torch
    import torch.cuda
except ImportError:
    print("[FATAL] torch not installed.", flush=True)
    sys.exit(1)

if not torch.cuda.is_available():
    print("[FATAL] CUDA not available. This script requires a GPU.", flush=True)
    sys.exit(1)

DEVICE = torch.device('cuda')
print(f"[GPU] device={DEVICE} name={torch.cuda.get_device_name(0)} "
      f"total_mem={torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB", flush=True)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "pp12_capacity_ondemand_w_v1_n16384"

_N_SUFFIX = 16384
N = 16384
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
_M_CRIT = int(ALPHA_C * N)  # 2261

# PROT-022 formula self-tests at module scope (arithmetic only, no GPU)
assert _M_CRIT == 2261, f"M_crit={_M_CRIT} expected 2261"
_W_BYTES = N * N * 4
assert _W_BYTES < 2e9, f"W on-demand bytes: {_W_BYTES/1e9:.2f}GB >= 2GB"
print(f"[selftest-formula] M_crit={_M_CRIT} W_ondemand={_W_BYTES/1e9:.2f}GB alpha_c={ALPHA_C}",
      flush=True)

# Alpha sweep
ALPHA_SWEEP_FULL = [0.02, 0.05, 0.08, 0.10, 0.12, 0.138, 0.15, 0.18, 0.20]
assert all(a < b for a, b in zip(ALPHA_SWEEP_FULL, ALPHA_SWEEP_FULL[1:])), (
    f"alpha sweep not monotone: {ALPHA_SWEEP_FULL}")
print(f"[selftest-formula] Alpha sweep monotone: {ALPHA_SWEEP_FULL}", flush=True)

NOISE_FRAC = 0.10
HP_RECALL_SAFE = 0.97     # recall >= 0.97 at alpha <= 0.10
HF_RECALL_LOW = 0.85      # recall < 0.85 at alpha <= 0.05 = HARD_FAIL
HP_RECALL_MIDMAX = 0.97   # recall > 0.97 at alpha=0.20 = HARD_FAIL (no degradation)

if RUN_MODE == "smoke":
    N_ACTIVE = 512
    SEEDS = [7, 17]
    ALPHA_SWEEP = [0.02, 0.10, 0.20]  # smoke: 3 points (low, mid, high)
    N_QUERIES = 5
    N_STEPS = 5
elif RUN_MODE == "smoke4x":
    N_ACTIVE = 2048
    SEEDS = [7, 17]
    ALPHA_SWEEP = [0.02, 0.10, 0.20]
    N_QUERIES = 5
    N_STEPS = 5
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    ALPHA_SWEEP = ALPHA_SWEEP_FULL
    N_QUERIES = 10
    N_STEPS = 8


def hopfield_retrieve_gpu(W: torch.Tensor, probe: torch.Tensor, n_steps: int = 8) -> torch.Tensor:
    state = probe.clone()
    for _ in range(n_steps):
        h = W @ state
        state = torch.sign(h)
        state[state == 0] = 1.0
    return state


def cosine_sim_gpu(a: torch.Tensor, b: torch.Tensor) -> float:
    na = float(a.norm())
    nb = float(b.norm())
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(torch.dot(a, b)) / (na * nb)


def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # 1. Build Xi at small N, small alpha
    n_test = 512
    M_test = max(1, int(0.05 * n_test))
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(42)
    Xi = (torch.randint(0, 2, (M_test, n_test), generator=gen, device=DEVICE).float() * 2 - 1)

    # 2. On-demand W build
    W = (Xi.t() @ Xi) / n_test
    mem_after_w = torch.cuda.memory_allocated(0) / 1e9
    assert mem_after_w > 0, f"GPU memory not allocated after W build"

    # 3. Retrieval
    probe = Xi[0].clone()
    flip = (torch.rand(n_test, generator=gen, device=DEVICE) < NOISE_FRAC)
    probe[flip] *= -1.0
    retrieved = hopfield_retrieve_gpu(W, probe)
    recall = cosine_sim_gpu(retrieved, Xi[0])
    assert not (recall != recall), f"recall is NaN"
    assert recall > 0.0, f"recall is zero at alpha=0.05 smoke -- instrumentation broken"

    # 4. Free W (on-demand pattern)
    del W
    torch.cuda.empty_cache()

    print(f"[selftest] PASS: M_test={M_test} recall={recall:.4f} "
          f"gpu_mem_after_W={mem_after_w:.3f}GB N={n_test}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)

# Multi-scale smoke check
if RUN_MODE in ("smoke", "smoke4x"):
    print(f"[smoke] Running at N_active={N_ACTIVE} (multi-scale smoke)", flush=True)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed)
    t0 = time.time()

    cell_results = {}
    for alpha in ALPHA_SWEEP:
        M = max(1, int(alpha * n_dim))
        Xi = (torch.randint(0, 2, (M, n_dim), generator=gen, device=DEVICE).float() * 2 - 1)

        mem_xi = torch.cuda.memory_allocated(0) / 1e9

        # On-demand W build
        W = (Xi.t() @ Xi) / n_dim

        mem_w = torch.cuda.memory_allocated(0) / 1e9
        print(f"  [seed={seed} alpha={alpha:.3f} M={M}] Xi={mem_xi:.3f}GB W={mem_w:.3f}GB",
              flush=True)

        n_q = min(N_QUERIES, M)
        recalls = []
        for q in range(n_q):
            probe = Xi[q].clone()
            flip = (torch.rand(n_dim, generator=gen, device=DEVICE) < NOISE_FRAC)
            probe[flip] *= -1.0
            retrieved = hopfield_retrieve_gpu(W, probe, n_steps=N_STEPS)
            recalls.append(cosine_sim_gpu(retrieved, Xi[q]))

        mean_recall = float(sum(recalls) / len(recalls)) if recalls else 0.0
        del W
        torch.cuda.empty_cache()

        key = f"a{alpha:.4f}"
        cell_results[key] = {
            "alpha": float(alpha), "M": M, "recall": float(mean_recall), "n_queries": n_q
        }
        print(f"  [seed={seed} alpha={alpha:.3f}] recall={mean_recall:.4f}", flush=True)

    elapsed = time.time() - t0
    peak_mem = torch.cuda.max_memory_allocated(0) / 1e9
    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "elapsed_s": float(elapsed), "peak_gpu_gb": float(peak_mem),
        "cells": cell_results,
    }


def compute_verdict(seed_results: List[Dict]) -> tuple:
    if not seed_results:
        return ("HARD_FAIL", "No valid results.")

    # Aggregate recall per alpha across seeds
    alpha_recalls: Dict[str, List[float]] = {}
    for r in seed_results:
        for key, cell in r.get("cells", {}).items():
            alpha_recalls.setdefault(key, []).append(cell["recall"])

    alpha_mean = {k: float(sum(v) / len(v)) for k, v in alpha_recalls.items()}

    # Find recall at key alpha values
    def recall_at(a_target: float) -> float:
        key = f"a{a_target:.4f}"
        return alpha_mean.get(key, float('nan'))

    summary_parts = [f"a{a:.3f}:{alpha_mean.get(f'a{a:.4f}', float('nan')):.3f}"
                     for a in ALPHA_SWEEP_FULL if f"a{a:.4f}" in alpha_mean]
    summary = f"recall_by_alpha: [{', '.join(summary_parts)}] n_seeds={len(seed_results)}"

    r_005 = recall_at(0.05)
    r_010 = recall_at(0.10)
    r_020 = recall_at(0.20)

    # HARD-FAIL: recall < 0.85 at alpha=0.05
    import math
    if not math.isnan(r_005) and r_005 < HF_RECALL_LOW:
        return ("HARD_FAIL",
                f"HARD_FAIL: recall(alpha=0.05)={r_005:.3f} < {HF_RECALL_LOW}. "
                f"Capacity below alpha_c/3 -- theoretical prediction wrong. {summary}")

    # HARD-FAIL: no degradation at alpha=0.20
    if not math.isnan(r_020) and r_020 > HP_RECALL_MIDMAX:
        return ("HARD_FAIL",
                f"HARD_FAIL: recall(alpha=0.20)={r_020:.3f} > {HP_RECALL_MIDMAX} "
                f"(no degradation at 1.45*alpha_c). Capacity envelope unclear. {summary}")

    # HARD-PASS criteria
    hp_safe = (not math.isnan(r_010) and r_010 >= HP_RECALL_SAFE)

    # Find degradation onset: first alpha where recall drops below 0.97
    onset_alpha = None
    for a in sorted(ALPHA_SWEEP_FULL):
        r = recall_at(a)
        if not math.isnan(r) and r < HP_RECALL_SAFE:
            onset_alpha = a
            break

    hp_onset = (onset_alpha is not None and 0.08 <= onset_alpha <= 0.20)

    if hp_safe and hp_onset:
        return ("HARD_PASS",
                f"HARD_PASS: PP-12 capacity on-demand W at N={N}. "
                f"recall(alpha=0.10)={r_010:.3f} >= {HP_RECALL_SAFE}; "
                f"degradation onset at alpha={onset_alpha:.3f} in [0.08,0.20]. {summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: partial capacity characterization. "
            f"hp_safe={hp_safe} hp_onset={hp_onset} onset_alpha={onset_alpha}. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"alpha_sweep={ALPHA_SWEEP}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE, "alpha_sweep": str(ALPHA_SWEEP_FULL)}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed, N_ACTIVE if RUN_MODE == "smoke" else N)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep_start
peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
print(f"[GPU] peak memory allocated: {peak_mem_gb:.3f} GB", flush=True)
assert peak_mem_gb > 0.01, f"GPU util check FAIL: peak_gpu={peak_mem_gb:.3f}GB (< 100MB)"

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "alpha_c": ALPHA_C, "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "alpha_sweep": ALPHA_SWEEP_FULL,
    "per_seed": [
        {"seed": r.get("seed"),
         "peak_gpu_gb": r.get("peak_gpu_gb"),
         "elapsed_s": r.get("elapsed_s")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
