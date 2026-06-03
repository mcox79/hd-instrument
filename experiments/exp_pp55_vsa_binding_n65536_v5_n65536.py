"""
pp55_vsa_binding_n65536_v5_n65536 -- PP-55 N-scale: VSA binding at N=65536 (5th rung).

CONTEXT:
  v1_n4096: HARD_PASS (founding; mean_cos >= 0.85 in >= 4/5 seeds).
  v2_n8192: HARD_PASS (mean_cos=0.99999; band-lift to 0.70-0.85).
  v3_n16384: HARD_PASS (mean_cos=0.9999959; 3-rung; band-lift to 0.75-0.88).
  v4_n32768: HARD_PASS (mean_cos=0.99999; 4-rung; band-lift to 0.78-0.90).
  5th rung: N=65536 to confirm algebraic N-independence at higher N.

SCIENTIFIC QUESTION:
  Does VSA bind-unbind algebra over SKAH-M-class substrate maintain fidelity at N=65536?
  Theory: larger N -> lower interference -> better retrieval. HP expected.

OOM PRE-CHECK:
  W matrix float32: 65536^2 * 4 / 1e9 = 17.18 GB. Exceeds 16 GB RAM -- NO explicit W.
  CHUNKED RETRIEVAL: W@probe computed as sum_k Xi_bound[k] * (Xi_bound[k] . probe) / N.
  Memory: Xi_bound shape (M=3276, N=65536) float32 = 0.86 GB. Fits easily.
  This is mathematically identical to (Xi_bound.T @ Xi_bound / N) @ probe.
  No W materialization needed. Retrieval O(M*N) per step vs O(N^2).

FORMULA SELF-TESTS (PROT-022):
  1. Hadamard binding self-inverse: a*b*b == a exactly for +-1 vectors.
     [INPUT: a=[1,-1,1,-1], b=[1,1,-1,-1]] [EXPECTED: (a*b)*b == a]
  2. Chunked Hopfield retrieval at N=512 alpha=0.05: cos > 0.85.
     [INPUT: N=512, M=26 (alpha~0.05)] [EXPECTED: mean_cos > 0.50]
  3. M_pairs at N=65536: int(0.05 * 65536) = 3276. [EXPECTED: M_pairs = 3276]
  4. Xi_bound memory: 3276 * 65536 * 4 / 1e9 < 1.0 GB. [EXPECTED: < 1.0 GB]

PRE-REGISTERED BANDS (PP-55 N=65536 5th-rung extension; prior N=32768 HARD_PASS):
  HARD-PASS: cos(retrieved, xi_A) >= 0.85 in >= 4/5 seeds at alpha=0.05 N=65536
             => PP-55 band-lift eligible 0.78-0.90 -> 0.80-0.92 (5-rung cross-N)
  MIDDLE: cos in [0.60, 0.85)
  HARD-FAIL: cos < 0.50 (VSA bind-unbind fails at N=65536)

PROT-018: anchor has _n65536; N MUST = 65536.
PROT-021: seed checkpoints keyed with run_mode.
QUEUE: remote_cpu_queue (pure numpy; Xi_bound (M x N) only; chunked Hopfield; ~1800s FULL wall).
TIMEOUT ESTIMATE: N=32768 elapsed=442.5s (v357, 5-seed, explicit W).
  N=65536 chunked: M=3276 vs M=1638 (2x); N=65536 vs N=32768 (2x).
  Chunked Hopfield step: O(M*N) vs O(N^2) for explicit W. Much faster.
  Estimated similar or slightly less than N=32768 due to no W build (W build was dominant).
  ceil(1.5 * 442.5 * 2.0 * 1.0) = ceil(1327) = 1800s.
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

ANCHOR_NAME = "pp55_vsa_binding_n65536_v5_n65536"

_N_SUFFIX = 65536
N = 65536
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA = 0.05
NOISE_FRAC = 0.10

# PROT-022: M_pairs check
_M_PAIRS_FULL = int(ALPHA * N)  # 3276
assert _M_PAIRS_FULL >= 1, f"M_pairs={_M_PAIRS_FULL} must be >= 1"
assert _M_PAIRS_FULL == 3276, f"M_pairs={_M_PAIRS_FULL} expected 3276"

# OOM check: Xi_bound memory at FULL N
_XI_BOUND_MEM_GB = _M_PAIRS_FULL * N * 4 / 1e9  # float32
assert _XI_BOUND_MEM_GB < 1.0, f"Xi_bound memory {_XI_BOUND_MEM_GB:.3f} GB >= 1.0 GB"

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACT = 2048
    M_ACT = int(ALPHA * N_ACT)  # 102
    N_PROBES = 10
    N_RETRIEVE_STEPS = 10
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_ACT = N
    M_ACT = _M_PAIRS_FULL  # 3276
    N_PROBES = 30
    N_RETRIEVE_STEPS = 20

# Pre-registered thresholds
HP_COS_MIN = 0.85
MID_COS_LOW = 0.60
HF_COS_MAX = 0.50
HP_MIN_SEEDS = 4


def generate_patterns(M_count: int, N_dim: int, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    return rng.choice([-1.0, 1.0], size=(M_count, N_dim)).astype(np.float32)


def hadamard_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a * b


def hadamard_unbind(bound: np.ndarray, b: np.ndarray) -> np.ndarray:
    return bound * b


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-8 or nb < 1e-8:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def chunked_hopfield_retrieve(Xi_bound: np.ndarray, probe: np.ndarray,
                               n_steps: int) -> np.ndarray:
    """W @ state computed as Xi_bound.T @ (Xi_bound @ state) / N -- no explicit W."""
    n_dim = probe.shape[0]
    state = probe.copy()
    for _ in range(n_steps):
        # activations: shape (M,)
        activations = Xi_bound @ state  # (M,) = M inner products
        # h = Xi_bound.T @ activations / n_dim: shape (N,)
        h = Xi_bound.T @ activations / n_dim
        state = np.sign(h).astype(np.float32)
        state[state == 0] = 1.0
    return state


def _selftest_hadamard_inverse():
    a = np.array([1.0, -1.0, 1.0, -1.0])
    b = np.array([1.0,  1.0, -1.0, -1.0])
    bound = hadamard_bind(a, b)
    a_rec = hadamard_unbind(bound, b)
    assert np.allclose(a_rec, a, atol=1e-6), f"Hadamard inverse failed: {a_rec} != {a}"


def _selftest_chunked_hopfield():
    """Chunked Hopfield retrieval at N=512 alpha=0.05: cos > 0.50."""
    N_t = 512
    M_t = max(1, int(ALPHA * N_t))  # 25
    rng = np.random.RandomState(42)
    Xi_A = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float32)
    Xi_B = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float32)
    Xi_bound = Xi_A * Xi_B
    cos_list = []
    for k in range(min(M_t, 5)):
        probe = Xi_bound[k].copy()
        flip = rng.random(N_t) < NOISE_FRAC
        probe[flip] *= -1.0
        retrieved_bound = chunked_hopfield_retrieve(Xi_bound, probe, n_steps=10)
        xi_A_rec = hadamard_unbind(retrieved_bound, Xi_B[k])
        cos_list.append(cosine_sim(xi_A_rec, Xi_A[k]))
    mean_cos = float(np.mean(cos_list))
    assert mean_cos > 0.50, f"chunked_hopfield selftest: mean_cos={mean_cos:.3f} < 0.50"


def _selftest_m_pairs():
    """M_pairs at N=65536: int(0.05 * 65536) = 3276."""
    assert _M_PAIRS_FULL == 3276, f"M_pairs={_M_PAIRS_FULL} expected 3276"


def _selftest_mem_check():
    """Xi_bound memory < 1.0 GB."""
    assert _XI_BOUND_MEM_GB < 1.0, f"Xi_bound mem={_XI_BOUND_MEM_GB:.3f} GB >= 1.0 GB"


def _instrumentation_selftest():
    _selftest_hadamard_inverse()
    _selftest_chunked_hopfield()
    _selftest_m_pairs()
    _selftest_mem_check()
    print(f"[selftest] PASS: hadamard_inverse, chunked_hopfield_N512, "
          f"m_pairs={_M_PAIRS_FULL}, xi_bound_mem={_XI_BOUND_MEM_GB:.3f}GB", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int, m_count: int) -> Dict:
    """Test VSA binding fidelity using chunked Hopfield (no explicit W)."""
    rng_noise = np.random.RandomState(seed + 1000)
    t_seed = time.time()

    Xi_A = generate_patterns(m_count, n_dim, seed)
    Xi_B = generate_patterns(m_count, n_dim, seed + 500)
    Xi_bound = Xi_A * Xi_B  # HRR binding (M, N)

    print(f"  [seed={seed}] Xi_bound built M={m_count} N={n_dim} "
          f"mem={Xi_bound.nbytes / 1e9:.3f}GB...", flush=True)

    cos_list = []
    k_indices = rng_noise.randint(0, m_count, size=N_PROBES)
    for k in k_indices:
        probe = Xi_bound[k].copy()
        flip = rng_noise.random(n_dim) < NOISE_FRAC
        probe[flip] *= -1.0
        retrieved_bound = chunked_hopfield_retrieve(Xi_bound, probe, n_steps=N_RETRIEVE_STEPS)
        xi_A_rec = hadamard_unbind(retrieved_bound, Xi_B[k])
        cos_list.append(float(cosine_sim(xi_A_rec, Xi_A[k])))

    mean_cos = float(np.mean(cos_list))
    elapsed = time.time() - t_seed
    print(f"  [seed={seed} N={n_dim}] mean_cos={mean_cos:.5f} over {N_PROBES} probes "
          f"elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "mean_cos": mean_cos, "cos_list": cos_list, "elapsed_s": elapsed}


def main():
    t_start = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)

    print(f"[{RUN_MODE}] N={N_ACT} M={M_ACT} alpha={ALPHA} "
          f"n_probes={N_PROBES} seeds={SEEDS} approach=chunked_hopfield_no_W", flush=True)

    done_seeds, remaining = resumable_seeds(SEEDS, out_dir)
    print(f"[ckpt] {len(done_seeds)} done; running {remaining}", flush=True)

    for seed in remaining:
        print(f"[seed {seed}]", flush=True)
        r = run_seed(seed, N_ACT, M_ACT)
        write_partial(out_dir, seed, r)

    per_seed = aggregate_partials(out_dir, SEEDS)

    cos_per_seed = [per_seed[str(s)]["mean_cos"] for s in SEEDS]
    mean_cos_all = float(np.mean(cos_per_seed))
    min_cos_all = float(np.min(cos_per_seed))

    seeds_hp = sum(1 for c in cos_per_seed if c >= HP_COS_MIN)

    if min_cos_all < HF_COS_MAX:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL: min_cos={min_cos_all:.5f} < {HF_COS_MAX}; "
                       f"VSA chunked-Hopfield bind-unbind fails at N=65536")
    elif seeds_hp >= HP_MIN_SEEDS:
        verdict = "HARD_PASS"
        verdict_msg = (f"HARD_PASS: seeds_hp={seeds_hp}/5 cos>={HP_COS_MIN}; "
                       f"mean_cos={mean_cos_all:.5f}; min_cos={min_cos_all:.5f}; "
                       f"n_seeds={len(SEEDS)}; PP-55 5th-rung cross-N band-lift gate passed. "
                       f"N={N} alpha={ALPHA} M={M_ACT} approach=chunked_hopfield_no_W")
    elif mean_cos_all >= MID_COS_LOW:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND: mean_cos={mean_cos_all:.5f} in [{MID_COS_LOW},{HP_COS_MIN}); "
                       f"seeds_hp={seeds_hp}/5 n_seeds={len(SEEDS)}")
    else:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL: mean_cos={mean_cos_all:.5f} < {MID_COS_LOW}")

    elapsed = time.time() - t_start
    metrics = {
        "anchor_name": ANCHOR_NAME,
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
        "approach": "chunked_hopfield_no_W",
    }

    out_dir.joinpath("metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    main()
else:
    main()
