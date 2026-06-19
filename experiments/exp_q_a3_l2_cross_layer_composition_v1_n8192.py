"""
q_a3_l2_cross_layer_composition_v1_n8192 -- Q-A3 L=2 cross-layer at N=8192.

SAME DESIGN AS n4096 VERSION (q_a3_l2_cross_layer_composition_v1_n4096 PASS v333).
Production envelope: N=8192.

HARD-PASS: outer_fidelity >= 0.93 AND inner_fidelity >= 0.93 AND l2_accuracy >= 0.85.
HARD-FAIL: any fidelity < 0.60 OR l2_accuracy < 0.50.
MIDDLE: 2/3 conditions met.

PRE-REGISTERED BANDS (same as n4096 version, extended to N=8192):
  HP: outer_fidelity >= 0.93, inner_fidelity >= 0.93, l2_accuracy >= 0.85.
  HF: any fidelity < 0.60 OR l2_accuracy < 0.50.
  Calibration: n4096 HARD_PASS confirms L=2 at N=4096. N=8192 is production envelope.
  Expected: fidelity should be >= n4096 result (larger N means less interference).

FORMULA SELF-TESTS:
  1. Hadamard binding: xi_outer = xi_a XOR xi_inner_id (element-wise product for +-1).
     [INPUT: xi_a=[1,-1,1], xi_b=[-1,1,1]] [EXPECTED: xi_a*xi_b=[-1,-1,1]]
     [EXPECTED: (xi_a*xi_b)*xi_a=xi_b]
  2. Capacity: alpha = M_inner/N = 200/8192 = 0.024 << alpha_c = 0.138.
     [EXPECTED: 200/8192 < 0.138]
  3. Outer capacity: alpha_outer = M_outer/N = 100/8192 = 0.012 << alpha_c.
     [EXPECTED: 100/8192 < 0.138]

PROT-018: anchor name has _n8192; N MUST = 8192.
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

ANCHOR_NAME = "q_a3_l2_cross_layer_composition_v1_n8192"

# PROT-018: anchor has _n8192 -> N must = 8192
_N_SUFFIX = 8192
N = 8192
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
    M_INNER = 200
    M_OUTER = 100
    N_QUERIES = 50
    NOISE_FRAC = 0.10

HP_INNER_FIDELITY = 0.93
HP_OUTER_FIDELITY = 0.93
HP_L2_ACCURACY = 0.85
HF_FIDELITY = 0.60
HF_L2_ACCURACY = 0.50
ALPHA_C = 0.138

assert M_INNER / N < ALPHA_C, f"inner overloaded: alpha={M_INNER/N:.4f} >= alpha_c={ALPHA_C}"
assert M_OUTER / N < ALPHA_C, f"outer overloaded: alpha={M_OUTER/N:.4f} >= alpha_c={ALPHA_C}"


def _selftest_hadamard_binding():
    xi_a = np.array([1.0, -1.0, 1.0, -1.0], dtype=np.float64)
    xi_b = np.array([-1.0, 1.0, 1.0, -1.0], dtype=np.float64)
    xi_bound = xi_a * xi_b
    xi_decoded = xi_bound * xi_a
    assert np.allclose(xi_decoded, xi_b), f"Hadamard decode failed: {xi_decoded} != {xi_b}"
    return xi_bound, xi_decoded


def _selftest_capacity():
    alpha_inner = M_INNER / N
    alpha_outer = M_OUTER / N
    assert alpha_inner < ALPHA_C
    assert alpha_outer < ALPHA_C
    return alpha_inner, alpha_outer


def _instrumentation_selftest():
    t1, t2 = _selftest_hadamard_binding()
    a_in, a_out = _selftest_capacity()
    print(f"[selftest] hadamard OK; alpha_inner={a_in:.4f} alpha_outer={a_out:.4f} < alpha_c={ALPHA_C}",
          flush=True)


_instrumentation_selftest()
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

    Xi_inner = rng.choice([-1.0, 1.0], size=(M_INNER, N)).astype(np.float64)
    W_inner = Xi_inner.T @ Xi_inner / float(N)
    np.fill_diagonal(W_inner, 0.0)

    Xi_context = rng.choice([-1.0, 1.0], size=(M_OUTER, N)).astype(np.float64)
    Xi_outer = Xi_context * Xi_inner[:M_OUTER]
    W_outer = Xi_outer.T @ Xi_outer / float(N)
    np.fill_diagonal(W_outer, 0.0)

    inner_fidelities = []
    outer_fidelities = []
    l2_correct = 0

    for q_idx in range(min(N_QUERIES, M_OUTER)):
        xi_outer_true = Xi_outer[q_idx]
        probe_outer = xi_outer_true.copy()
        flip_outer = rng.random(N) < NOISE_FRAC
        probe_outer[flip_outer] *= -1.0

        xi_outer_retrieved = hopfield_retrieve(W_outer, probe_outer)
        outer_fid = cosine_sim(xi_outer_retrieved, xi_outer_true)
        outer_fidelities.append(outer_fid)

        xi_context_q = Xi_context[q_idx]
        xi_inner_pointer = xi_outer_retrieved * xi_context_q

        xi_inner_retrieved = hopfield_retrieve(W_inner, xi_inner_pointer)
        xi_inner_true = Xi_inner[q_idx]
        inner_fid = cosine_sim(xi_inner_retrieved, xi_inner_true)
        inner_fidelities.append(inner_fid)

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


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M_inner": M_INNER, "M_outer": M_OUTER, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] running N={N} M_inner={M_INNER} M_outer={M_OUTER}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "N": N,
    "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS),
    "elapsed_s": elapsed_total,
    "mean_outer_fidelity": float(np.mean([r["outer_fidelity"] for r in all_results])) if all_results else None,
    "mean_inner_fidelity": float(np.mean([r["inner_fidelity"] for r in all_results])) if all_results else None,
    "mean_l2_accuracy": float(np.mean([r["l2_accuracy"] for r in all_results])) if all_results else None,
}
metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"[done] metrics -> {metrics_path}", flush=True)
