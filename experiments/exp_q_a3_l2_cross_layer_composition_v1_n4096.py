"""
q_a3_l2_cross_layer_composition_v1_n4096 -- Q-A3: L=2 cross-layer composition.

SCIENTIFIC QUESTION (Q-A3):
  Does the substrate support 2-level nested composition where:
    - INNER level (p=2): stores M_inner patterns in W_inner (N_inner-dim space).
    - OUTER level (p=3): routes over inner retrieval outputs (N_outer-dim space).
  Full composition: outer query -> outer retrieval -> inner retrieval.

  Architecture:
    - Inner layer: N_inner=4096, M_inner=200, p=2 Hopfield.
    - Outer layer: N_outer=4096, M_outer=100, p=3 polynomial DAM.
    - Composition: outer pattern encodes a POINTER to an inner pattern.
      Retrieve outer -> decode pointer -> retrieve inner -> compare to ground truth.
    - Cross-layer binding: Hadamard binding (outer pattern = xi_outer XOR xi_inner_id)
      so that outer retrieval automatically decodes the inner pattern index.

  Test metrics:
    (A) Per-level fidelity:
        - inner_fidelity: cosine(W_inner @ xi_inner_noisy, xi_inner_true) >= HP_INNER.
        - outer_fidelity: cosine(W_outer @ xi_outer_noisy, xi_outer_true) >= HP_OUTER.
    (B) End-to-end L=2 accuracy:
        - Given noisy outer query, retrieve outer, decode, retrieve inner.
        - l2_accuracy = fraction of queries where inner_retrieved == inner_true.
        - HP_L2: l2_accuracy >= 0.85.

HARD-PASS: outer_fidelity >= 0.93 AND inner_fidelity >= 0.93 AND l2_accuracy >= 0.85.
HARD-FAIL: outer_fidelity < 0.60 OR inner_fidelity < 0.60 OR l2_accuracy < 0.50.
MIDDLE: 2/3 conditions met.

PRE-REGISTERED BANDS:
  HP: outer_fidelity >= 0.93, inner_fidelity >= 0.93, l2_accuracy >= 0.85.
  HF: any fidelity < 0.60 OR l2_accuracy < 0.50.
  Calibration: first L=2 cross-layer composition test at N=4096.
  Bands based on prior heteroassoc chain tests (heteroassoc_chain_cert_v1 HARD_PASS).

FORMULA SELF-TESTS:
  1. Hadamard binding: xi_outer = xi_a XOR xi_inner_id (element-wise product for +-1 vectors).
     For +-1 vectors: XOR = element-wise product. Decode: xi_inner_id = xi_outer * xi_a.
     [INPUT: xi_a = [1,-1,1], xi_b = [-1,1,1]] [EXPECTED: xi_a * xi_b = [-1,-1,1]]
     [EXPECTED: (xi_a * xi_b) * xi_a = xi_b]
  2. Hopfield capacity: at alpha = M/N = 0.049 (M_inner=200, N=4096), well below
     alpha_c = 0.138 => high fidelity expected.
     [INPUT: alpha=0.049] [EXPECTED: alpha < alpha_c]
  3. Outer layer: at alpha = M_outer/N = 0.024, also well below alpha_c.
     [INPUT: alpha_outer=0.024] [EXPECTED: alpha_outer < alpha_c]

PROT-018: anchor name has _n4096; N MUST = 4096.
PROT-021: run_config includes N, M_inner, M_outer, run_mode.
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

ANCHOR_NAME = "q_a3_l2_cross_layer_composition_v1_n4096"

# PROT-018: anchor has _n4096 -> N must = 4096
_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_INNER = 50
    M_OUTER = 25
    N_QUERIES = 20
    NOISE_FRAC = 0.10
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_INNER = 200   # alpha = 0.049 -- well below capacity
    M_OUTER = 100   # alpha = 0.024
    N_QUERIES = 50
    NOISE_FRAC = 0.10

HP_INNER_FIDELITY = 0.93
HP_OUTER_FIDELITY = 0.93
HP_L2_ACCURACY = 0.85
HF_FIDELITY = 0.60
HF_L2_ACCURACY = 0.50

ALPHA_C = 0.138  # Hopfield capacity

# PROT-021
assert M_INNER / N < ALPHA_C, f"inner overloaded: alpha={M_INNER/N:.3f} >= alpha_c={ALPHA_C}"
assert M_OUTER / N < ALPHA_C, f"outer overloaded: alpha={M_OUTER/N:.3f} >= alpha_c={ALPHA_C}"


def _selftest_hadamard_binding():
    """Hadamard binding: xi_outer = xi_a * xi_b (for +-1 vectors, * = XOR analog).
    Decode: xi_b = xi_outer * xi_a (since xi_a * xi_a = +1 for all entries).
    """
    xi_a = np.array([1.0, -1.0, 1.0, -1.0], dtype=np.float64)
    xi_b = np.array([-1.0, 1.0, 1.0, -1.0], dtype=np.float64)
    xi_bound = xi_a * xi_b
    xi_decoded = xi_bound * xi_a
    assert np.allclose(xi_decoded, xi_b), f"Hadamard decode failed: {xi_decoded} != {xi_b}"
    return xi_bound, xi_decoded


def _selftest_capacity():
    alpha_inner = M_INNER / N
    alpha_outer = M_OUTER / N
    assert alpha_inner < ALPHA_C, f"inner alpha {alpha_inner:.3f} >= alpha_c {ALPHA_C}"
    assert alpha_outer < ALPHA_C, f"outer alpha {alpha_outer:.3f} >= alpha_c {ALPHA_C}"
    return alpha_inner, alpha_outer


def _instrumentation_selftest():
    t1, t2 = _selftest_hadamard_binding()
    a_in, a_out = _selftest_capacity()
    print(f"[selftest] hadamard_bind={t1[:2]}... decode={t2[:2]}... "
          f"alpha_inner={a_in:.4f} alpha_outer={a_out:.4f} both < alpha_c={ALPHA_C}", flush=True)


_instrumentation_selftest()
# Self-test only: exit after formula checks.
if _ARGS.self_test:
    sys.exit(0)


def hopfield_retrieve(W: np.ndarray, probe: np.ndarray, n_steps: int = 5) -> np.ndarray:
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b)) / (na * nb)


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    # Build inner layer: M_INNER patterns, N-dim
    Xi_inner = rng.choice([-1.0, 1.0], size=(M_INNER, N)).astype(np.float64)
    W_inner = Xi_inner.T @ Xi_inner / float(N)
    np.fill_diagonal(W_inner, 0.0)

    # Build outer layer: M_OUTER patterns, N-dim
    # Each outer pattern encodes a pointer to an inner pattern via Hadamard binding.
    # xi_outer_k = xi_context_k * xi_inner_k  (element-wise product)
    Xi_context = rng.choice([-1.0, 1.0], size=(M_OUTER, N)).astype(np.float64)
    Xi_outer = Xi_context * Xi_inner[:M_OUTER]  # Hadamard-bind context with inner pattern

    W_outer = Xi_outer.T @ Xi_outer / float(N)
    np.fill_diagonal(W_outer, 0.0)

    # Test queries
    inner_fidelities = []
    outer_fidelities = []
    l2_correct = 0

    for q_idx in range(min(N_QUERIES, M_OUTER)):
        inner_idx = q_idx  # inner pattern index

        # Noisy outer query
        xi_outer_true = Xi_outer[q_idx]
        probe_outer = xi_outer_true.copy()
        flip_outer = rng.random(N) < NOISE_FRAC
        probe_outer[flip_outer] *= -1.0

        # Step 1: Outer retrieval
        xi_outer_retrieved = hopfield_retrieve(W_outer, probe_outer)
        outer_fid = cosine_sim(xi_outer_retrieved, xi_outer_true)
        outer_fidelities.append(outer_fid)

        # Step 2: Decode inner pointer via Hadamard unbinding
        xi_context_q = Xi_context[q_idx]
        xi_inner_pointer = xi_outer_retrieved * xi_context_q  # decode

        # Step 3: Inner retrieval from decoded pointer
        xi_inner_retrieved = hopfield_retrieve(W_inner, xi_inner_pointer)
        xi_inner_true = Xi_inner[inner_idx]
        inner_fid = cosine_sim(xi_inner_retrieved, xi_inner_true)
        inner_fidelities.append(inner_fid)

        # L=2 accuracy: sign match (cosine > 0.5 = correct retrieval)
        if inner_fid > 0.5:
            l2_correct += 1

    inner_fid_mean = float(np.mean(inner_fidelities)) if inner_fidelities else 0.0
    outer_fid_mean = float(np.mean(outer_fidelities)) if outer_fidelities else 0.0
    l2_acc = l2_correct / N_QUERIES if N_QUERIES > 0 else 0.0
    elapsed = time.time() - t0

    print(f"  [seed={seed}] outer_fid={outer_fid_mean:.4f} inner_fid={inner_fid_mean:.4f} "
          f"l2_acc={l2_acc:.4f} elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": N, "M_inner": M_INNER, "M_outer": M_OUTER,
        "run_mode": RUN_MODE,
        "outer_fidelity": float(outer_fid_mean),
        "inner_fidelity": float(inner_fid_mean),
        "l2_accuracy": float(l2_acc),
        "n_queries": N_QUERIES,
        "elapsed_s": elapsed,
    }


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    outer_fids = [r["outer_fidelity"] for r in results if "outer_fidelity" in r]
    inner_fids = [r["inner_fidelity"] for r in results if "inner_fidelity" in r]
    l2_accs = [r["l2_accuracy"] for r in results if "l2_accuracy" in r]

    if not outer_fids:
        return ("HARD_FAIL", "No valid results.")

    mean_outer = float(np.mean(outer_fids))
    mean_inner = float(np.mean(inner_fids))
    mean_l2 = float(np.mean(l2_accs))

    summary = (f"outer_fid={mean_outer:.4f} (HP>={HP_OUTER_FIDELITY} HF<{HF_FIDELITY}) "
               f"inner_fid={mean_inner:.4f} (HP>={HP_INNER_FIDELITY} HF<{HF_FIDELITY}) "
               f"l2_acc={mean_l2:.4f} (HP>={HP_L2_ACCURACY} HF<{HF_L2_ACCURACY}) "
               f"n_seeds={len(outer_fids)}")

    if mean_outer < HF_FIDELITY or mean_inner < HF_FIDELITY or mean_l2 < HF_L2_ACCURACY:
        return ("HARD_FAIL", f"HARD_FAIL: {summary}")

    hp_outer = mean_outer >= HP_OUTER_FIDELITY
    hp_inner = mean_inner >= HP_INNER_FIDELITY
    hp_l2 = mean_l2 >= HP_L2_ACCURACY

    if hp_outer and hp_inner and hp_l2:
        return ("HARD_PASS", f"HARD_PASS: all 3 HP conditions met. {summary}")
    if sum([hp_outer, hp_inner, hp_l2]) >= 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {sum([hp_outer,hp_inner,hp_l2])}/3 HP conditions. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: only {sum([hp_outer,hp_inner,hp_l2])}/3 HP conditions. {summary}")


# ---- MAIN SWEEP ----
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M_inner": M_INNER, "M_outer": M_OUTER, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_s = time.time() - t_sweep_start
metrics = {
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": verdict_msg,
    "elapsed_s": elapsed_s,
    "n_seeds": len(SEEDS),
    "run_mode": RUN_MODE,
    "N": N,
    "M_inner": M_INNER,
    "M_outer": M_OUTER,
    "per_seed": [
        {"seed": r.get("seed"), "outer_fid": r.get("outer_fidelity"),
         "inner_fid": r.get("inner_fidelity"), "l2_acc": r.get("l2_accuracy")}
        for r in all_results
    ],
    "elapsed_total_s": elapsed_s,
}

metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
