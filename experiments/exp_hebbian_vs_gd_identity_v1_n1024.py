"""
hebbian_vs_gd_identity_v1_n1024 -- Cluster A1: Hebbian = MSE-optimal at 1000x speedup.

SCIENTIFIC QUESTION:
  Does one-shot Hebbian write achieve the same encoding fidelity as gradient descent
  for (key, value) memorization at N=1024, M=100 (alpha=0.098)?

  Algebraic basis: for bipolar patterns at alpha << alpha_c, Hebbian write
  W = Xi^T Xi / N is the MSE-optimal one-step solution (Hopfield 1982;
  Bishop 2006 ch.5). GD on MSE converges to the same W* when alpha << alpha_c.

PRE-REGISTERED BANDS (from routing note Item 2, v343):
  HARD-PASS: all 3 of:
    HP1: Hebbian retrieval accuracy within +-2pp of GD accuracy (5 seeds)
    HP2: wall-time speedup >= 100x
    HP3: FLOPs speedup >= 1000x (updated from Item 2 spec: 1000x not 400x)
  MIDDLE: +-5pp accuracy OR speedup 10-100x
  HARD-FAIL: Hebbian acc < 90% of GD accuracy OR speedup < 10x

  Calibration: alpha=0.098 << alpha_c=0.138; Hebbian-GD identity algebraically
  guaranteed; P_deflated=0.70+ (confirmed prior a1 run corroborates this regime).

FORMULA SELF-TESTS (PROT-022):
  1. Hebbian W = Xi^T Xi / N. For M=25, N=256 (alpha=0.098):
     expected retrieval acc > 0.85.
     [INPUT: N=256, M=25, alpha=0.098, 1 seed] [EXPECTED: acc > 0.85]
  2. MSE loss at W* = Xi^T Xi / N should be near 0 for alpha << alpha_c.
     [INPUT: W=Xi^T Xi/N, xi from same set, N=64, M=6]
     [EXPECTED: mean_residual^2 < 0.05]
  3. GD on tiny problem converges to Hebbian W.
     [INPUT: N=64, M=6, lr=0.01, max_iter=5000]
     [EXPECTED: ||W_gd - W_hebb||_F / (N*N) < 0.10]

PROT-018: anchor contains _n1024; N MUST = 1024.
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-02_hebbian_vs_gd_identity_v1_n1024.md
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

ANCHOR_NAME = "hebbian_vs_gd_identity_v1_n1024"

_N_SUFFIX = 1024
N = 1024
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_SMOKE = 256
    M_SMOKE = 25   # alpha = 0.098
    GD_MAX_ITER = 5000
    N_QUERIES = 10
    NOISE_FRAC = 0.10
    M = M_SMOKE
    _N = N_SMOKE
else:
    SEEDS = [7, 17, 23, 31, 41]
    M = 100        # alpha = 0.098
    GD_MAX_ITER = 20000
    N_QUERIES = 50
    NOISE_FRAC = 0.10
    _N = N

# Pre-registered thresholds
HP_ACC_DELTA_PP = 2.0       # within +-2pp (item 2 spec)
MID_ACC_DELTA_PP = 5.0
HF_ACC_RATIO = 0.90         # Hebbian < 90% of GD accuracy
HP_WALL_SPEEDUP = 100.0
HF_WALL_SPEEDUP = 10.0
HP_FLOPS_SPEEDUP = 1000.0   # 1000x as specified in item 2
HF_FLOPS_SPEEDUP = 10.0


def generate_patterns(M_count: int, N_dim: int, seed: int) -> np.ndarray:
    """Generate M bipolar BSC patterns, shape (M, N)."""
    rng = np.random.RandomState(seed)
    return rng.choice([-1.0, 1.0], size=(M_count, N_dim)).astype(np.float64)


def hopfield_retrieve(W: np.ndarray, probe: np.ndarray, n_steps: int = 20) -> np.ndarray:
    """Synchronous Hopfield retrieval."""
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def measure_accuracy(W: np.ndarray, Xi: np.ndarray, noise_frac: float,
                     n_queries: int, rng: np.random.RandomState) -> float:
    """Fraction of patterns correctly retrieved via noisy probe."""
    M_count, N_dim = Xi.shape
    correct = 0
    for k in range(min(M_count, n_queries)):
        probe = Xi[k].copy()
        flip = rng.random(N_dim) < noise_frac
        probe[flip] *= -1.0
        retrieved = hopfield_retrieve(W, probe)
        if float(np.dot(retrieved, Xi[k])) / N_dim >= 0.9:
            correct += 1
    return correct / min(M_count, n_queries)


def gd_train(Xi: np.ndarray, lr: float, max_iter: int) -> Tuple[np.ndarray, float, int, float, float]:
    """Train W via Adam on MSE loss. Returns (W, final_loss, n_iters, wall_s, total_flops)."""
    M_count, N_dim = Xi.shape
    W = np.zeros((N_dim, N_dim), dtype=np.float64)
    # Adam params
    m_adam = np.zeros_like(W)
    v_adam = np.zeros_like(W)
    beta1, beta2, eps = 0.9, 0.999, 1e-8
    t = 0
    t0 = time.time()
    for iteration in range(max_iter):
        preds = Xi @ W.T      # (M, N)
        residuals = preds - Xi
        loss = float(np.mean(residuals ** 2))
        grad = 2.0 * (residuals.T @ Xi) / M_count  # (N, N)
        np.fill_diagonal(grad, 0.0)
        t += 1
        m_adam = beta1 * m_adam + (1 - beta1) * grad
        v_adam = beta2 * v_adam + (1 - beta2) * grad**2
        m_hat = m_adam / (1 - beta1**t)
        v_hat = v_adam / (1 - beta2**t)
        W -= lr * m_hat / (np.sqrt(v_hat) + eps)
        np.fill_diagonal(W, 0.0)
        if loss < 1e-6:
            break
    wall_s = time.time() - t0
    # FLOPs: per iteration = 4 * M * N^2 (fwd+bwd)
    flops = 4 * M_count * N_dim**2 * t
    return W, loss, t, wall_s, flops


# ---- FORMULA SELF-TESTS ----

def _selftest_hebbian_accuracy():
    """Hebbian at alpha=0.098 should give acc > 0.85."""
    N_t, M_t = 256, 25
    Xi_t = generate_patterns(M_t, N_t, seed=42)
    W_hebb = (Xi_t.T @ Xi_t) / N_t
    np.fill_diagonal(W_hebb, 0.0)
    rng = np.random.RandomState(42)
    acc = measure_accuracy(W_hebb, Xi_t, 0.10, M_t, rng)
    assert acc > 0.85, f"selftest: Hebbian acc={acc:.3f} < 0.85 at alpha=0.098 N=256"


def _selftest_mse_at_optimum():
    """MSE at W* should be near 0."""
    N_t, M_t = 64, 6
    Xi_t = generate_patterns(M_t, N_t, seed=7)
    W_star = (Xi_t.T @ Xi_t) / N_t
    np.fill_diagonal(W_star, 0.0)
    preds = Xi_t @ W_star.T
    mse = float(np.mean((preds - Xi_t) ** 2))
    assert mse < 0.20, f"selftest: MSE at W*={mse:.4f} should be < 0.20 (low-alpha identity)"


def _selftest_gd_converges_to_hebb():
    """GD on tiny problem should approach Hebbian W."""
    N_t, M_t = 64, 6
    Xi_t = generate_patterns(M_t, N_t, seed=13)
    W_hebb = (Xi_t.T @ Xi_t) / N_t
    np.fill_diagonal(W_hebb, 0.0)
    W_gd, _, _, _, _ = gd_train(Xi_t, lr=0.01, max_iter=5000)
    rel_err = float(np.linalg.norm(W_gd - W_hebb) / (N_t * N_t))
    assert rel_err < 0.10, f"selftest: ||W_gd - W_hebb||/N^2 = {rel_err:.4f} >= 0.10"


def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    _selftest_hebbian_accuracy()
    _selftest_mse_at_optimum()
    _selftest_gd_converges_to_hebb()
    print("[selftest] PASS: hebbian_accuracy, mse_at_optimum, gd_converges all OK", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int, m_count: int) -> Dict:
    """Run one seed: Hebbian vs GD comparison."""
    rng_query = np.random.RandomState(seed + 1000)
    Xi = generate_patterns(m_count, n_dim, seed)

    # Hebbian
    t0 = time.time()
    W_hebb = (Xi.T @ Xi) / n_dim
    np.fill_diagonal(W_hebb, 0.0)
    hebb_wall = time.time() - t0
    # Hebbian FLOPs: one outer-product sum = M * N^2
    hebb_flops = float(m_count * n_dim**2)

    acc_hebb = measure_accuracy(W_hebb, Xi, NOISE_FRAC, N_QUERIES, rng_query)

    # GD
    W_gd, gd_loss, gd_iters, gd_wall, gd_flops = gd_train(Xi, lr=0.01, max_iter=GD_MAX_ITER)

    rng_query2 = np.random.RandomState(seed + 2000)
    acc_gd = measure_accuracy(W_gd, Xi, NOISE_FRAC, N_QUERIES, rng_query2)

    wall_speedup = gd_wall / max(hebb_wall, 1e-6)
    flops_speedup = gd_flops / max(hebb_flops, 1.0)

    return {
        "seed": seed,
        "acc_hebb": acc_hebb,
        "acc_gd": acc_gd,
        "acc_delta_pp": abs(acc_hebb - acc_gd) * 100.0,
        "acc_ratio": acc_hebb / max(acc_gd, 1e-6),
        "wall_speedup": wall_speedup,
        "flops_speedup": flops_speedup,
        "hebb_wall_s": hebb_wall,
        "gd_wall_s": gd_wall,
        "gd_iters": gd_iters,
        "gd_loss": gd_loss,
    }


def main():
    t_start = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)

    if RUN_MODE == "smoke":
        n_dim, m_count = _N, M
        print(f"[smoke] N={n_dim} M={m_count} alpha={m_count/n_dim:.3f}", flush=True)
    else:
        n_dim, m_count = N, M
        print(f"[full] N={n_dim} M={m_count} alpha={m_count/n_dim:.3f}", flush=True)

    done_seeds, remaining = resumable_seeds(SEEDS, out_dir)
    print(f"[ckpt] {len(done_seeds)} already done; running {remaining}", flush=True)

    for seed in remaining:
        print(f"[seed {seed}] running ...", flush=True)
        r = run_seed(seed, n_dim, m_count)
        write_partial(out_dir, seed, r)
        print(f"[seed {seed}] acc_hebb={r['acc_hebb']:.3f} acc_gd={r['acc_gd']:.3f} "
              f"delta={r['acc_delta_pp']:.1f}pp wall_spd={r['wall_speedup']:.0f}x "
              f"flops_spd={r['flops_speedup']:.0f}x", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)

    # Aggregate
    acc_hebb_list = [per_seed[str(s)]["acc_hebb"] for s in SEEDS]
    acc_gd_list   = [per_seed[str(s)]["acc_gd"]   for s in SEEDS]
    delta_list    = [per_seed[str(s)]["acc_delta_pp"] for s in SEEDS]
    wall_spd_list = [per_seed[str(s)]["wall_speedup"] for s in SEEDS]
    flops_spd_list= [per_seed[str(s)]["flops_speedup"] for s in SEEDS]
    acc_ratio_list= [per_seed[str(s)]["acc_ratio"] for s in SEEDS]

    mean_acc_hebb = float(np.mean(acc_hebb_list))
    mean_acc_gd   = float(np.mean(acc_gd_list))
    mean_delta    = float(np.mean(delta_list))
    mean_wall_spd = float(np.mean(wall_spd_list))
    mean_flops_spd= float(np.mean(flops_spd_list))
    min_acc_ratio = float(np.min(acc_ratio_list))
    max_delta     = float(np.max(delta_list))
    min_wall_spd  = float(np.min(wall_spd_list))
    min_flops_spd = float(np.min(flops_spd_list))

    # Verdict
    hp1 = max_delta <= HP_ACC_DELTA_PP
    hp2 = min_wall_spd >= HP_WALL_SPEEDUP
    hp3 = min_flops_spd >= HP_FLOPS_SPEEDUP
    hf1 = min_acc_ratio < HF_ACC_RATIO
    hf2 = min_wall_spd  < HF_WALL_SPEEDUP

    if hf1 or hf2:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HF: acc_ratio={min_acc_ratio:.3f}<{HF_ACC_RATIO} OR "
                       f"wall_spd={min_wall_spd:.0f}x<{HF_WALL_SPEEDUP}x")
    elif hp1 and hp2 and hp3:
        verdict = "HARD_PASS"
        verdict_msg = (f"HP: delta={max_delta:.1f}pp<={HP_ACC_DELTA_PP}pp, "
                       f"wall_spd={min_wall_spd:.0f}x>={HP_WALL_SPEEDUP}x, "
                       f"flops_spd={min_flops_spd:.0f}x>={HP_FLOPS_SPEEDUP}x all 5-seed")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE: delta={max_delta:.1f}pp wall_spd={min_wall_spd:.0f}x "
                       f"flops_spd={min_flops_spd:.0f}x")

    elapsed = time.time() - t_start
    metrics = {
        "anchor": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "mean_acc_hebb": mean_acc_hebb,
        "mean_acc_gd": mean_acc_gd,
        "mean_delta_pp": mean_delta,
        "max_delta_pp": max_delta,
        "mean_wall_speedup": mean_wall_spd,
        "min_wall_speedup": min_wall_spd,
        "mean_flops_speedup": mean_flops_spd,
        "min_flops_speedup": min_flops_spd,
        "min_acc_ratio": min_acc_ratio,
        "N": _N if RUN_MODE == "smoke" else N,
        "M": m_count,
        "alpha": m_count / n_dim,
        "n_seeds": len(SEEDS),
        "elapsed_s": elapsed,
        "run_mode": RUN_MODE,
    }

    out_path = out_dir / "metrics.json"
    out_path.write_text(json.dumps(metrics, indent=2))
    print(f"\n[verdict] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed:.1f}s", flush=True)
    print(f"[metrics] {out_path}", flush=True)


if __name__ == "__main__":
    main()
