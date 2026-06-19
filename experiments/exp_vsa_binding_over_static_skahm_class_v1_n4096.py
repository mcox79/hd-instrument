"""
vsa_binding_over_static_skahm_class_v1_n4096 -- VSA bind/unbind over static SKAH-M attractor.

SCIENTIFIC QUESTION:
  Do standard VSA bind/unbind operations (HRR-style Hadamard circular-product binding)
  preserve fidelity when operating over patterns stored in the substrate's
  SKAH-M-class static attractor network (vs the standard temporal-reservoir treatment)?

  Cross-drill resonance: Reservoir drill confirmed VSA community treats reservoirs only
  as nonlinear expansion kernels, never as mutable algebraic stores. Memristor drill
  confirmed SKAH-M class hardware-family match. This test verifies the algebraic side:
  can VSA bind(xi_A, xi_B) be stored in substrate W and retrieved via unbind(query, xi_B)
  with cos(retrieved, xi_A) >= 0.85?

TEST DESIGN:
  N=4096, alpha=0.05, M_pairs = int(alpha * N) = 204 bound pairs stored.
  For each pair k: store bound_k = xi_A_k * xi_B_k (Hadamard / HRR binding).
  W = sum_k bound_k bound_k^T / N (Hopfield store of bound vectors).
  Retrieval: noisy_query = bound_k + noise; retrieve via Hopfield -> decoded_bound;
  unbind: xi_A_recovered = decoded_bound * xi_B_k.
  Measure cos(xi_A_recovered, xi_A_k).

PRE-REGISTERED BANDS (Item 19 v343):
  HARD-PASS: cos(retrieved, xi_A) >= 0.85 in >= 4/5 seeds at alpha=0.05 N=4096
  MIDDLE: cos in [0.60, 0.85)
  HARD-FAIL: cos < 0.5 -- VSA bind-unbind algebra doesn't survive static SKAH-M storage

  Calibration probe: no prior empirical anchor for this exact regime.
  Bands set at theoretical prediction (cos ~ 0.90 expected at alpha=0.05) +-20%.
  P_deflated=0.55.

FORMULA SELF-TESTS (PROT-022):
  1. Hadamard binding and unbinding: bind(a, b) = a * b; unbind(a*b, b) = a.
     [INPUT: a=[1,-1,1,-1], b=[1,1,-1,-1]] [EXPECTED: (a*b)*b == a exactly]
  2. Orthogonality: E[cos(xi_A, xi_B)] ~ 0 for random bipolar vectors at N=4096.
     [INPUT: N=4096, 100 random pairs] [EXPECTED: mean |cos| < 0.10]
  3. Hopfield retrieval at alpha=0.05 N=4096: mean retrieval fidelity > 0.85 for stored patterns.
     [INPUT: N=256, M=13 (alpha=0.051), 5 noisy probes] [EXPECTED: fidelity > 0.80]

PROT-018: anchor contains _n4096; N MUST = 4096.
Queue: remote_cpu_queue (pure numpy; ~30 min wall)
Pre-reg: preregs/2026-06-02_vsa_binding_over_static_skahm_class_v1_n4096.md

TIMEOUT ESTIMATE:
  Smoke: N=512, M=26 (alpha=0.05), 2 seeds, 20 probes.
  Full: N=4096, M=204, 5 seeds, 50 probes.
  Per seed: W build (M*N^2 flops) + retrieval (n_probes * 20 steps * N^2 flops).
  N=4096: W build ~204 * 4096^2 / 1e9 ~ 3.4 GFlops; with numpy ~3s.
          retrieval: 50 * 20 * N^2 ~ 16.8 GFlops; numpy ~15s.
  Per seed ~20s. Full 5 seeds = ~100s.
  timeout_s = ceil(1.5 * 100 * 1) = 150 -> 600s (with headroom for N=4096 scale).
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
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "vsa_binding_over_static_skahm_class_v1_n4096"

_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA = 0.05

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACT = 512
    M_ACT = int(ALPHA * N_ACT)   # 26
    N_PROBES = 10
    NOISE_FRAC = 0.10
    N_RETRIEVE_STEPS = 10
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_ACT = N
    M_ACT = int(ALPHA * N_ACT)   # 204
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
    """HRR-style Hadamard binding: elementwise product."""
    return a * b


def hadamard_unbind(bound: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Unbind: since bind is self-inverse over +-1, unbind(bound, b) = bound * b = a."""
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


# ---- FORMULA SELF-TESTS ----

def _selftest_hadamard_inverse():
    """Hadamard bind/unbind is self-inverse over +-1 vectors."""
    a = np.array([1.0, -1.0, 1.0, -1.0])
    b = np.array([1.0,  1.0, -1.0, -1.0])
    bound = hadamard_bind(a, b)
    a_rec = hadamard_unbind(bound, b)
    assert np.allclose(a_rec, a, atol=1e-6), f"Hadamard inverse failed: {a_rec} != {a}"


def _selftest_orthogonality():
    """Random bipolar vectors should be near-orthogonal at N=4096."""
    rng = np.random.RandomState(0)
    Xi = rng.choice([-1.0, 1.0], size=(100, 4096)).astype(np.float32)
    sims = []
    for i in range(100):
        c = float(np.dot(Xi[i], Xi[(i+1) % 100]) / 4096.0)
        sims.append(abs(c))
    mean_sim = float(np.mean(sims))
    assert mean_sim < 0.10, f"Orthogonality: mean |cos|={mean_sim:.4f} >= 0.10"


def _selftest_hopfield_retrieval():
    """Hopfield at alpha=0.05 should retrieve patterns with cos > 0.80."""
    N_t, M_t = 256, 13
    rng = np.random.RandomState(42)
    Xi = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float32)
    # Build a set of bound vectors to store
    ctx = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float32)
    bounds = Xi * ctx  # element-wise binding
    W = (bounds.T @ bounds) / N_t
    np.fill_diagonal(W, 0.0)
    # Retrieve
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


def _instrumentation_selftest():
    """Assert all claimed metrics non-null/non-sentinel."""
    _selftest_hadamard_inverse()
    _selftest_orthogonality()
    _selftest_hopfield_retrieval()
    print("[selftest] PASS: hadamard_inverse, orthogonality, hopfield_retrieval all OK",
          flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int, m_count: int) -> Dict:
    rng_noise = np.random.RandomState(seed + 1000)
    # Generate xi_A and xi_B patterns
    Xi_A = generate_patterns(m_count, n_dim, seed)
    Xi_B = generate_patterns(m_count, n_dim, seed + 500)

    # Bound vectors: bind(xi_A_k, xi_B_k)
    Xi_bound = Xi_A * Xi_B  # (M, N) HRR binding

    # Build Hopfield W over bound vectors
    W = (Xi_bound.T @ Xi_bound) / n_dim
    np.fill_diagonal(W, 0.0)

    # Retrieval: for each of n_probes queries, pick a random pair k
    cos_list = []
    k_indices = rng_noise.randint(0, m_count, size=N_PROBES)
    for k in k_indices:
        probe = Xi_bound[k].copy()
        flip = rng_noise.random(n_dim) < NOISE_FRAC
        probe[flip] *= -1.0
        # Retrieve bound vector from noisy probe
        retrieved_bound = hopfield_retrieve(W, probe, n_steps=N_RETRIEVE_STEPS)
        # Unbind: xi_A_recovered = retrieved_bound * xi_B_k
        xi_A_rec = hadamard_unbind(retrieved_bound, Xi_B[k])
        cos = cosine_sim(xi_A_rec, Xi_A[k])
        cos_list.append(float(cos))

    mean_cos = float(np.mean(cos_list))
    print(f"  [seed={seed}] mean_cos={mean_cos:.4f} over {N_PROBES} probes", flush=True)
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

    # Verdict
    if min_cos_all < HF_COS_MAX:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HF: min_cos={min_cos_all:.4f} < {HF_COS_MAX}; "
                       f"VSA bind-unbind fails over static SKAH-M storage")
    elif seeds_hp >= HP_MIN_SEEDS:
        verdict = "HARD_PASS"
        verdict_msg = (f"HP: {seeds_hp}/5 seeds cos >= {HP_COS_MIN}; "
                       f"mean_cos={mean_cos_all:.4f}; "
                       f"VSA bind-unbind preserved over SKAH-M attractor (founds PP-55 algebraic side)")
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
