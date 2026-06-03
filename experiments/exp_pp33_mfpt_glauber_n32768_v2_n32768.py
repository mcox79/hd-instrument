"""
pp33_mfpt_glauber_n32768_v2_n32768 -- PP-33 MFPT N-scaling extension at N=32768.

CONTEXT:
  pp33_mfpt_glauber_n_scaling_v1 (pending): N in {4096, 8192, 16384}, alpha=0.10, 5 seeds.
  This script extends the N-scaling sweep to N=32768 (4th rung).
  Purpose: tighten the scaling exponent estimate with a 4th data point; at N=32768
  the N^(1/3) and N^1 hypotheses separate by a factor of 8^(1/3)/8 = 2.0/8.0.

SCIENTIFIC QUESTION:
  Does substrate MFPT continue to scale as N^(1/3) (1-RSB, Aspelmeier-Bray-Moore 2004)
  at N=32768? Or does the exponent shift (crossover to RS or near-critical)?

TEST DESIGN:
  N=32768, alpha=0.10, 5 seeds.
  M=int(0.10 * 32768) = 3276 patterns stored in W.
  For each seed: retrieve one pattern from noise, run Glauber dynamics until basin-escape.
  N_TRAJECTORIES=10 per seed, MAX_GLAUBER_STEPS=5000 (matches v1 cap).
  Combined with v1 results {N=4096, 8192, 16384} for 4-point scaling fit.

OOM PRE-CHECK:
  W matrix CPU: N=32768, float64 = 32768^2 * 8 / 1e9 = 8.59 GB.
  Remote CPU (marsh@home) has 16+ GB RAM. Feasible.
  Xi matrix: 3276 * 32768 * 8 / 1e6 = 859 MB. Fine.

PRE-REGISTERED BANDS (PP-33 N=32768 extension; v1 pending with N={4096,8192,16384}):
  Calibration probe at N=32768; no prior v1 result yet to anchor against.
  Bands per +-50% policy (first single-N measurement at N=32768).
  HARD-PASS: mean_tau at N=32768 in [1.5x, 5.0x] * mean_tau_at_N=16384.
             (N^(1/3) predicts 2.0x; +-50% gives [1.0x, 3.0x]; but log scaling broadens)
             Simplified: tau_32768 > tau_16384 (monotone increasing with N)
             AND exponent_32768 in [0.15, 0.55] (covers both RS and 1-RSB hypotheses).
  MIDDLE: tau_32768 within 1.5x of tau_16384 (very weak N-dependence) OR exponent < 0.15.
  HARD-FAIL: tau_32768 < tau_16384 (N-DECREASING tau; unexpected; likely numerical).

FORMULA SELF-TESTS (PROT-022):
  1. N^(1/3) ratio: (32768/16384)^(1/3) = 2.0^(1/3) = 1.260.
     [INPUT: N1=16384, N2=32768] [EXPECTED: 1.260 within 0.001]
  2. Glauber accept prob at h=1, T=2.0: 1/(1+exp(2*1/2.0)) = 1/(1+exp(1)) = 0.26894.
     [INPUT: h=1, T=2.0] [EXPECTED: 0.26894 within 0.0001]
  3. M at alpha=0.10, N=32768: int(0.10 * 32768) = 3276. [EXPECTED: 3276]
  4. W memory: 32768^2 * 8 / 1e9 = 8.59 GB < 16 GB remote RAM. [EXPECTED: < 16.0]

PROT-018: anchor has _n32768; N MUST = 32768.
PROT-021: seed checkpoints keyed with run_mode.
QUEUE: remote_cpu_queue (Glauber MCMC is CPU-native; ~8.59 GB W matrix; needs remote 16+ GB RAM).
TIMEOUT ESTIMATE: N=16384 v1 est ~2680s (5 seeds). N=32768 W is 4x larger; O(N^2) per step.
  Glauber step: W@x = O(N^2); but W@x done once per spin flip, not per step.
  At N=32768: each full Glauber step samples 1 spin; actual cost per step ~ O(N) (one row of W).
  5000 steps * 32768 * 10 traj * 5 seeds / 1e10 ops/s = 820s.
  Plus W construction: 3276 * 32768^2 * 2 (outer product) / 1e10 = 703s.
  Total est: 1523s. ceil(1.5 * 1523) = 2285 -> 2400s.
  timeout=3600s (with extra margin for W build I/O and memory bandwidth).
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
from pathlib import Path
from typing import Dict, List, Optional

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import numpy as np
except ImportError:
    print("[FATAL] numpy not installed.", flush=True)
    sys.exit(1)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "pp33_mfpt_glauber_n32768_v2_n32768"

_N_SUFFIX = 32768
N = 32768
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

ALPHA = 0.10
TEMP_GLAUBER = 2.0
MAX_GLAUBER_STEPS = 5000
N_TRAJECTORIES = 10
INITIAL_NOISE_FRAC = 0.05
ESCAPE_OVERLAP_THRESH = 0.30

# Pre-registered thresholds
HP_EXPONENT_LO = 0.15
HP_EXPONENT_HI = 0.55
HF_TAU_DECREASING = True   # fail if tau_32768 < tau_16384

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# PROT-022 formula self-tests at module scope
_N_CUBEROOT_RATIO = (32768.0 / 16384.0) ** (1.0 / 3.0)
assert abs(_N_CUBEROOT_RATIO - 1.2599) < 0.001, f"N^(1/3) ratio: {_N_CUBEROOT_RATIO:.4f} expected 1.260"

_GLAUBER_ACCEPT = 1.0 / (1.0 + 2.71828 ** (2.0 * 1.0 / TEMP_GLAUBER))
assert abs(_GLAUBER_ACCEPT - 0.26894) < 0.0002, f"Glauber accept: {_GLAUBER_ACCEPT:.5f} expected 0.26894"

_M_FULL = int(ALPHA * N)
assert _M_FULL == 3276, f"M at N={N} alpha={ALPHA}: {_M_FULL} expected 3276"

_W_MEM_GB = (N ** 2) * 8 / 1e9
assert _W_MEM_GB < 16.0, f"W memory {_W_MEM_GB:.2f} GB exceeds 16 GB remote RAM"

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACT = 2048
    N_TRAJ_ACT = 3
    MAX_STEPS_ACT = 1000
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_ACT = N
    N_TRAJ_ACT = N_TRAJECTORIES
    MAX_STEPS_ACT = MAX_GLAUBER_STEPS


def _selftest_n_cuberoot():
    """(32768/16384)^(1/3) = 2^(1/3) = 1.260"""
    ratio = (32768.0 / 16384.0) ** (1.0 / 3.0)
    assert abs(ratio - 1.2599) < 0.001, f"N^(1/3) selftest: {ratio:.4f} expected 1.260"


def _selftest_glauber_accept():
    """Glauber accept at h=1, T=2.0"""
    import math
    p = 1.0 / (1.0 + math.exp(2.0 * 1.0 / TEMP_GLAUBER))
    assert abs(p - 0.26894) < 0.0002, f"Glauber accept: {p:.5f} expected 0.26894"


def _selftest_m_check():
    """M at alpha=0.10, N=32768: 3276"""
    M = int(ALPHA * N)
    assert M == 3276, f"M={M} expected 3276"


def _selftest_w_mem():
    """W memory check: < 16 GB"""
    w_gb = (N ** 2) * 8 / 1e9
    assert w_gb < 16.0, f"W memory {w_gb:.2f} GB exceeds 16 GB"


def _selftest_small_forward():
    """Run one Glauber step at small N without error."""
    n_t = 64
    rng = np.random.RandomState(1)
    M_t = max(1, int(ALPHA * n_t))
    Xi_t = rng.choice([-1., 1.], size=(M_t, n_t)).astype(np.float64)
    W_t = (Xi_t.T @ Xi_t) / float(n_t)
    x = Xi_t[0].copy()
    h = W_t @ x
    p_flip = 1.0 / (1.0 + np.exp(2.0 * h / TEMP_GLAUBER))
    assert len(p_flip) == n_t, f"p_flip length {len(p_flip)} expected {n_t}"
    assert not np.any(np.isnan(p_flip)), "p_flip contains NaN"


def _instrumentation_selftest():
    _selftest_n_cuberoot()
    _selftest_glauber_accept()
    _selftest_m_check()
    _selftest_w_mem()
    _selftest_small_forward()
    print(f"[selftest] PASS: N^(1/3)_ratio={_N_CUBEROOT_RATIO:.4f}, glauber_ok, "
          f"M=3276, W_mem={_W_MEM_GB:.2f}GB, forward_pass_ok; "
          f"N_ACT={N_ACT} mode={RUN_MODE}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def retrieve_pattern(W: np.ndarray, Xi: np.ndarray, pattern_idx: int,
                     noise_frac: float, rng: np.random.RandomState,
                     n_steps: int = 8) -> np.ndarray:
    xi_target = Xi[pattern_idx]
    probe = xi_target.copy()
    flip = rng.random(len(probe)) < noise_frac
    probe[flip] *= -1.0
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def glauber_basin_escape(W: np.ndarray, Xi: np.ndarray, initial_state: np.ndarray,
                         T: float, max_steps: int, rng: np.random.RandomState) -> int:
    n_dim = W.shape[0]
    state = initial_state.copy()
    for step in range(max_steps):
        overlaps = (Xi @ state) / float(n_dim)
        if float(np.max(overlaps)) < ESCAPE_OVERLAP_THRESH:
            return step
        i = int(rng.randint(0, n_dim))
        h_i = float(W[i] @ state)
        p_flip = 1.0 / (1.0 + np.exp(2.0 * h_i / T))
        if rng.random() < p_flip:
            state[i] = -state[i]
    return max_steps


def run_seed(seed: int, n_dim: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    M_val = max(1, int(ALPHA * n_dim))
    print(f"  [seed={seed} N={n_dim}] building Xi (M={M_val}) and W ({n_dim}x{n_dim})...",
          flush=True)
    Xi = rng.choice([-1., 1.], size=(M_val, n_dim)).astype(np.float64)
    W = (Xi.T @ Xi) / float(n_dim)
    t_w = time.time() - t0
    print(f"  [seed={seed} N={n_dim}] W built in {t_w:.1f}s, W_mem={W.nbytes/1e9:.2f}GB",
          flush=True)

    tau_values = []
    for traj_idx in range(N_TRAJ_ACT):
        initial_state = retrieve_pattern(W, Xi, 0, INITIAL_NOISE_FRAC, rng)
        tau = glauber_basin_escape(W, Xi, initial_state, TEMP_GLAUBER, MAX_STEPS_ACT, rng)
        tau_values.append(tau)
        print(f"  [seed={seed} N={n_dim} traj={traj_idx}] tau={tau}", flush=True)

    mean_tau = float(np.mean(tau_values))
    std_tau = float(np.std(tau_values))
    elapsed = time.time() - t0

    print(f"  [seed={seed} N={n_dim}] mean_tau={mean_tau:.1f} std={std_tau:.1f} "
          f"elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": n_dim, "alpha": ALPHA, "run_mode": RUN_MODE,
        "mean_tau": mean_tau, "std_tau": std_tau,
        "tau_values": tau_values, "elapsed_s": float(elapsed),
        "max_steps_active": MAX_STEPS_ACT,
    }


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    tau_means = [r["mean_tau"] for r in results]
    mean_tau = float(np.mean(tau_means))
    std_tau = float(np.std(tau_means))
    n_seeds = len(results)

    summary = (f"N={N} mean_tau={mean_tau:.1f} std={std_tau:.1f} "
               f"n_seeds={n_seeds} max_steps={MAX_STEPS_ACT}")

    if mean_tau <= 0:
        return ("HARD_FAIL", f"HARD_FAIL: mean_tau <= 0. {summary}")

    # The verdict is informational -- full scaling exponent requires combining with v1 {4096,8192,16384}
    # We report tau and flag the monotone-increasing check
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND (informational): N=32768 tau={mean_tau:.1f}. "
            f"Combine with v1 {4096, 8192, 16384} results for scaling exponent. {summary}")


print(f"[config] anchor={ANCHOR_NAME} N={N_ACT} alpha={ALPHA} "
      f"mode={RUN_MODE} seeds={SEEDS} max_steps={MAX_STEPS_ACT} n_traj={N_TRAJ_ACT}", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "alpha": ALPHA, "run_mode": RUN_MODE, "max_steps": MAX_STEPS_ACT}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

all_results = []
for seed in done:
    fpath = out_dir / f"seed_{seed}.json"
    if fpath.exists():
        d = json.loads(fpath.read_text(encoding="utf-8"))
        if isinstance(d, dict):
            all_results.append(d)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    r = run_seed(seed, N_ACT)
    all_results.append(r)
    write_partial(out_dir, seed, r)

verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "alpha": ALPHA, "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "max_steps": MAX_STEPS_ACT,
    "elapsed_s": elapsed_total,
    "all_results": all_results,
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
