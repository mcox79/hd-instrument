"""
vsa_binding_n8192_v2_n8192 -- PP-55 N-scale: VSA binding at N=8192.

CONTEXT (cycle22 strategy #4):
  v1_n4096: HARD_PASS (mean_cos >= 0.85 in >= 4/5 seeds at N=4096 alpha=0.05).
  PP-55 founded at 0.65-0.80 EXPLORATORY (single N=4096 anchor).
  Next gate for band-lift 0.70-0.85: cross-N at N=8192 (and N=16384 later).
  This anchor tests N=8192, alpha=0.05.

SCIENTIFIC QUESTION:
  Does VSA bind/unbind algebra over SKAH-M-class static attractor network maintain
  fidelity at N=8192? Theory predicts improved performance at larger N (more capacity,
  better Hopfield retrieval). HP at N=8192 would support PP-55 band-lift.

TEST DESIGN:
  N=8192, alpha=0.05, M_pairs = int(alpha * N) = 409 bound pairs stored.
  For each pair k: store bound_k = xi_A_k * xi_B_k (Hadamard / HRR binding).
  W = sum_k bound_k bound_k^T / N. Retrieval: noisy_query -> Hopfield -> unbind.
  Measure cos(xi_A_recovered, xi_A_k).

FORMULA SELF-TESTS (PROT-022):
  1. Hadamard binding is self-inverse over +-1 vectors.
     [INPUT: a=[1,-1,1,-1], b=[1,1,-1,-1]] [EXPECTED: (a*b)*b == a exactly]
  2. Orthogonality at N=8192: E[cos(xi_A, xi_B)] < 0.05 (tighter at larger N).
     [INPUT: N=8192, 100 random pairs] [EXPECTED: mean |cos| < 0.08]
  3. Hopfield at alpha=0.05 N=8192 should retrieve patterns with cos > 0.80.
     [INPUT: N=256, M=13 (alpha=0.051)] [EXPECTED: fidelity > 0.50]
  4. M_pairs at N=8192: int(0.05 * 8192) = 409. Must be >= 1.
     [EXPECTED: M_pairs = 409]

PRE-REGISTERED BANDS (PP-55 N-scale; prior v1_n4096 HARD_PASS cos ~0.90):
  HARD-PASS: cos(retrieved, xi_A) >= 0.85 in >= 4/5 seeds at alpha=0.05 N=8192
             => PP-55 band-lift 0.65-0.80 -> 0.70-0.85 eligible (2-rung cross-N)
  MIDDLE: cos in [0.60, 0.85)
  HARD-FAIL: cos < 0.5 -- VSA bind-unbind fails at N=8192

PROT-018: anchor has _n8192; N MUST = 8192.
QUEUE: remote_cpu_queue (pure numpy; N=8192 W matrix = 2.15 GB float64; ~10 min wall).
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

import numpy as np

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "vsa_binding_n8192_v2_n8192"

_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA = 0.05

# PROT-022: M_pairs check
_M_PAIRS_FULL = int(ALPHA * N)  # 409
assert _M_PAIRS_FULL >= 1, f"M_pairs={_M_PAIRS_FULL} must be >= 1"

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACT = 1024
    M_ACT = int(ALPHA * N_ACT)  # 51
    N_PROBES = 10
    NOISE_FRAC = 0.10
    N_RETRIEVE_STEPS = 10
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_ACT = N
    M_ACT = _M_PAIRS_FULL  # 409
    N_PROBES = 30
    NOISE_FRAC = 0.10
    N_RETRIEVE_STEPS = 20

# Pre-registered thresholds
HP_COS_MIN   = 0.85
MID_COS_LOW  = 0.60
HF_COS_MAX   = 0.50
HP_MIN_SEEDS = 4


def generate_patterns(M_count: int, N_dim: int, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    return rng.choice([-1.0, 1.0], size=(M_count, N_dim)).astype(np.float32)


def hadamard_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a * b


def hadamard_unbind(bound: np.ndarray, b: np.ndarray) -> np.ndarray:
    return bound * b


def hopfield_retrieve(W: np.ndarray, probe: np.ndarray, n_steps: int) -> np.ndarray:
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h).astype(np.float32)
        state[state == 0] = 1.0
    return state


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-8 or nb < 1e-8:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def _selftest_hadamard_inverse():
    a = np.array([1.0, -1.0, 1.0, -1.0])
    b = np.array([1.0,  1.0, -1.0, -1.0])
    bound = hadamard_bind(a, b)
    a_rec = hadamard_unbind(bound, b)
    assert np.allclose(a_rec, a, atol=1e-6), f"Hadamard inverse failed: {a_rec} != {a}"


def _selftest_orthogonality():
    """Random bipolar vectors should be near-orthogonal at N=8192 (tighter than N=4096)."""
    rng = np.random.RandomState(0)
    Xi = rng.choice([-1.0, 1.0], size=(100, 8192)).astype(np.float32)
    sims = []
    for i in range(100):
        c = float(np.dot(Xi[i], Xi[(i+1) % 100]) / 8192.0)
        sims.append(abs(c))
    mean_sim = float(np.mean(sims))
    assert mean_sim < 0.08, f"Orthogonality at N=8192: mean |cos|={mean_sim:.4f} >= 0.08"


def _selftest_hopfield_retrieval():
    """Hopfield at alpha=0.05 N=256 should retrieve with cos > 0.50."""
    N_t, M_t = 256, 13
    rng = np.random.RandomState(42)
    Xi = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float32)
    ctx = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float32)
    bounds = Xi * ctx
    W = (bounds.T @ bounds) / N_t
    np.fill_diagonal(W, 0.0)
    cos_list = []
    for k in range(M_t):
        probe = bounds[k].copy()
        flip = rng.random(N_t) < 0.10
        probe[flip] *= -1.0
        retrieved = hopfield_retrieve(W.astype(np.float32), probe, n_steps=10)
        xi_A_rec = hadamard_unbind(retrieved, ctx[k])
        cos_list.append(cosine_sim(xi_A_rec, Xi[k]))
    mean_cos = float(np.mean(cos_list))
    assert mean_cos > 0.50, f"selftest Hopfield retrieval mean_cos={mean_cos:.3f} < 0.50"


def _selftest_m_pairs():
    """M_pairs at N=8192 must be 409."""
    assert _M_PAIRS_FULL == 409, f"M_pairs={_M_PAIRS_FULL} expected 409"


def _instrumentation_selftest():
    _selftest_hadamard_inverse()
    _selftest_orthogonality()
    _selftest_hopfield_retrieval()
    _selftest_m_pairs()
    print("[selftest] PASS: hadamard_inverse, orthogonality_N8192, hopfield_retrieval, m_pairs",
          flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int, m_count: int) -> Dict:
    rng_noise = np.random.RandomState(seed + 1000)
    Xi_A = generate_patterns(m_count, n_dim, seed)
    Xi_B = generate_patterns(m_count, n_dim, seed + 500)

    Xi_bound = Xi_A * Xi_B  # HRR binding

    W = (Xi_bound.T @ Xi_bound) / n_dim
    np.fill_diagonal(W, 0.0)

    cos_list = []
    k_indices = rng_noise.randint(0, m_count, size=N_PROBES)
    for k in k_indices:
        probe = Xi_bound[k].copy()
        flip = rng_noise.random(n_dim) < NOISE_FRAC
        probe[flip] *= -1.0
        retrieved_bound = hopfield_retrieve(W, probe, n_steps=N_RETRIEVE_STEPS)
        xi_A_rec = hadamard_unbind(retrieved_bound, Xi_B[k])
        cos_list.append(float(cosine_sim(xi_A_rec, Xi_A[k])))

    mean_cos = float(np.mean(cos_list))
    print(f"  [seed={seed} N={n_dim}] mean_cos={mean_cos:.4f} over {N_PROBES} probes", flush=True)
    return {"seed": seed, "mean_cos": mean_cos, "cos_list": cos_list}


def main():
    t_start = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)

    print(f"[{RUN_MODE}] N={N_ACT} M={M_ACT} alpha={ALPHA} "
          f"n_probes={N_PROBES} seeds={SEEDS}", flush=True)

    done_seeds, remaining = resumable_seeds(SEEDS, out_dir)
    print(f"[ckpt] {len(done_seeds)} done; running {remaining}", flush=True)

    for seed in remaining:
        print(f"[seed {seed}]", flush=True)
        r = run_seed(seed, N_ACT, M_ACT)
        write_partial(out_dir, seed, r)

    per_seed = aggregate_partials(out_dir, SEEDS)

    cos_per_seed = [per_seed[str(s)]["mean_cos"] for s in SEEDS]
    mean_cos_all = float(np.mean(cos_per_seed))
    min_cos_all  = float(np.min(cos_per_seed))

    seeds_hp = sum(1 for c in cos_per_seed if c >= HP_COS_MIN)

    if min_cos_all < HF_COS_MAX:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HF: min_cos={min_cos_all:.4f} < {HF_COS_MAX}; "
                       f"VSA bind-unbind fails at N=8192")
    elif seeds_hp >= HP_MIN_SEEDS:
        verdict = "HARD_PASS"
        verdict_msg = (f"HP: {seeds_hp}/5 seeds cos >= {HP_COS_MIN}; "
                       f"mean_cos={mean_cos_all:.4f}; "
                       f"VSA bind-unbind preserved at N=8192 (PP-55 band-lift gate passed)")
    elif mean_cos_all >= MID_COS_LOW:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE: mean_cos={mean_cos_all:.4f} in [{MID_COS_LOW},{HP_COS_MIN}); "
                       f"seeds_hp={seeds_hp}/5")
    else:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HF: mean_cos={mean_cos_all:.4f} < {MID_COS_LOW}")

    elapsed = time.time() - t_start
    metrics = {
        "anchor": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "mean_cos_all_seeds": mean_cos_all,
        "min_cos_all_seeds": min_cos_all,
        "cos_per_seed": {str(s): c for s, c in zip(SEEDS, cos_per_seed)},
        "seeds_hp": seeds_hp,
        "N": N_ACT,
        "M": M_ACT,
        "alpha": ALPHA,
        "n_seeds": len(SEEDS),
        "n_probes": N_PROBES,
        "elapsed_s": elapsed,
        "run_mode": RUN_MODE,
    }

    out_dir.joinpath("metrics.json").write_text(json.dumps(metrics, indent=2))
    print(f"\n[verdict] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    main()
else:
    main()
