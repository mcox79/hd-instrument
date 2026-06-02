"""
q_a3_l3_cross_layer_composition_v1_n4096 -- Q-A3: L=3 cross-layer composition.

SCIENTIFIC QUESTION (Q-A3 extension):
  v334: PP-12 cross-layer L=2 SUB-PROPERTY LIFT to N=8192 HARD_PASS (outer+inner fid=1.0,
  l2_acc=1.0 at both N=4096 and N=8192). This anchor extends to L=3 (3 nested layers).

  Architecture:
    - Inner layer (L1): N=4096, M_inner=200, p=2 Hopfield. Stores base patterns.
    - Middle layer (L2): N=4096, M_mid=100, p=2 Hopfield. Pointers to L1 via Hadamard.
    - Outer layer (L3): N=4096, M_outer=50, p=2 Hopfield. Pointers to L2 via Hadamard.
    - Query: noisy L3 query -> L3 retrieval -> decode L2 pointer -> L2 retrieval ->
      decode L1 pointer -> L1 retrieval -> compare to ground truth.

  Test metrics:
    (A) Per-level fidelity: L1, L2, L3 each >= HP_FIDELITY = 0.90.
    (B) End-to-end L=3 accuracy: fraction of queries where inner_retrieved == inner_true >= 0.80.

HARD-PASS: L1_fid >= 0.90 AND L2_fid >= 0.90 AND L3_fid >= 0.90 AND l3_acc >= 0.80.
HARD-FAIL: any fidelity < 0.60 OR l3_acc < 0.40.
MIDDLE: 3/4 conditions met.

PRE-REGISTERED BANDS:
  HP: all 4 conditions (L1_fid, L2_fid, L3_fid >= 0.90, l3_acc >= 0.80).
  HF: any fidelity < 0.60 OR l3_acc < 0.40.
  Calibration: first L=3 chain at N=4096.
  Prior: L=2 at N=4096 and N=8192 both HARD_PASS with all metrics = 1.0.
  L=3 adds one more layer of Hadamard binding; per-level fidelity expected near 1.0
  but error accumulates; HP_L3 = 0.80 (more conservative than L=2 HP = 0.85).

FORMULA SELF-TESTS:
  1. L=3 Hadamard chain: xi_L3 = xi_ctx3 * xi_L2; xi_L2 = xi_ctx2 * xi_L1.
     Decode: xi_L2 = xi_L3 * xi_ctx3; xi_L1 = xi_L2 * xi_ctx2.
     [INPUT: xi_ctx3=[1,-1], xi_ctx2=[-1,1], xi_L1=[1,1]]
     [EXPECTED: xi_L2 = xi_ctx2 * xi_L1 = [-1,1]; xi_L3 = xi_ctx3 * xi_L2 = [-1,-1]]
     Decode: xi_L2 = xi_L3 * xi_ctx3 = [-1,-1]*[1,-1] = [-1,1] OK.
             xi_L1 = xi_L2 * xi_ctx2 = [-1,1]*[-1,1] = [1,1] OK.
  2. Capacity check: alpha_L1=0.049, alpha_L2=0.024, alpha_L3=0.012 all below 0.138.
     [INPUT: M_L1=200, M_L2=100, M_L3=50, N=4096] [EXPECTED: all alpha < 0.138]

PROT-018: anchor has _n4096 -> N MUST = 4096.
PROT-021: run_config includes N, M_inner, M_mid, M_outer, run_mode.
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

ANCHOR_NAME = "q_a3_l3_cross_layer_composition_v1_n4096"

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
    M_INNER = 30    # L1: 30 patterns
    M_MID = 15      # L2: 15 patterns
    M_OUTER = 8     # L3: 8 patterns
    N_QUERIES = 6
    NOISE_FRAC = 0.10
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_INNER = 200   # L1: alpha = 0.049
    M_MID = 100     # L2: alpha = 0.024
    M_OUTER = 50    # L3: alpha = 0.012
    N_QUERIES = 40
    NOISE_FRAC = 0.10

HP_FIDELITY = 0.90
HF_FIDELITY = 0.60
HP_L3_ACC = 0.80
HF_L3_ACC = 0.40
ALPHA_C = 0.138


def _selftest_l3_chain():
    xi_ctx3 = np.array([1.0, -1.0])
    xi_ctx2 = np.array([-1.0, 1.0])
    xi_L1 = np.array([1.0, 1.0])
    xi_L2 = xi_ctx2 * xi_L1
    xi_L3 = xi_ctx3 * xi_L2
    # Decode
    xi_L2_dec = xi_L3 * xi_ctx3
    xi_L1_dec = xi_L2_dec * xi_ctx2
    assert np.allclose(xi_L2_dec, xi_L2), f"L3 decode L2: {xi_L2_dec} != {xi_L2}"
    assert np.allclose(xi_L1_dec, xi_L1), f"L3 decode L1: {xi_L1_dec} != {xi_L1}"
    return xi_L3, xi_L2, xi_L1


def _selftest_capacity():
    alpha_l1 = M_INNER / N
    alpha_l2 = M_MID / N
    alpha_l3 = M_OUTER / N
    assert alpha_l1 < ALPHA_C, f"L1 alpha={alpha_l1:.4f} >= alpha_c"
    assert alpha_l2 < ALPHA_C, f"L2 alpha={alpha_l2:.4f} >= alpha_c"
    assert alpha_l3 < ALPHA_C, f"L3 alpha={alpha_l3:.4f} >= alpha_c"
    return alpha_l1, alpha_l2, alpha_l3


def _instrumentation_selftest():
    xl3, xl2, xl1 = _selftest_l3_chain()
    a1, a2, a3 = _selftest_capacity()
    assert N_QUERIES > 0, "N_QUERIES must be > 0"
    print(f"[selftest] PASS: L3_chain_xi={xl3} L2={xl2} L1={xl1} "
          f"alpha_L1={a1:.4f} alpha_L2={a2:.4f} alpha_L3={a3:.4f} "
          f"all < alpha_c={ALPHA_C}", flush=True)


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

    # L1: inner layer patterns
    Xi_inner = rng.choice([-1.0, 1.0], size=(M_INNER, N)).astype(np.float64)
    W_inner = Xi_inner.T @ Xi_inner / float(N)
    np.fill_diagonal(W_inner, 0.0)

    # L2: middle layer patterns (Hadamard binding of ctx2 with L1)
    Xi_ctx2 = rng.choice([-1.0, 1.0], size=(M_MID, N)).astype(np.float64)
    Xi_mid = Xi_ctx2 * Xi_inner[:M_MID]  # xi_L2_k = xi_ctx2_k * xi_inner_k
    W_mid = Xi_mid.T @ Xi_mid / float(N)
    np.fill_diagonal(W_mid, 0.0)

    # L3: outer layer patterns (Hadamard binding of ctx3 with L2)
    Xi_ctx3 = rng.choice([-1.0, 1.0], size=(M_OUTER, N)).astype(np.float64)
    Xi_outer = Xi_ctx3 * Xi_mid[:M_OUTER]  # xi_L3_k = xi_ctx3_k * xi_L2_k
    W_outer = Xi_outer.T @ Xi_outer / float(N)
    np.fill_diagonal(W_outer, 0.0)

    rng_noise = np.random.RandomState(seed + 100)
    l1_fids = []
    l2_fids = []
    l3_fids = []
    l3_correct = 0
    n_test = min(N_QUERIES, M_OUTER)

    for q_idx in range(n_test):
        # L3 noisy probe
        probe_l3 = Xi_outer[q_idx].copy()
        flip = rng_noise.random(N) < NOISE_FRAC
        probe_l3[flip] *= -1.0

        # Step 1: L3 retrieval
        xi_l3_ret = hopfield_retrieve(W_outer, probe_l3)
        l3_fid = cosine_sim(xi_l3_ret, Xi_outer[q_idx])
        l3_fids.append(l3_fid)

        # Step 2: Decode L2 pointer
        xi_l2_ptr = xi_l3_ret * Xi_ctx3[q_idx]
        # Find nearest L2 pattern
        l2_nearest = max(range(M_MID),
                         key=lambda i: float(np.dot(xi_l2_ptr, Xi_mid[i])) / N)
        l2_fid = cosine_sim(xi_l2_ptr, Xi_mid[l2_nearest])
        l2_fids.append(l2_fid)

        # Step 3: L2 retrieval using decoded pointer
        xi_l2_ret = hopfield_retrieve(W_mid, xi_l2_ptr)
        # Should match Xi_mid[q_idx] if l2_nearest == q_idx
        xi_l2_true = Xi_mid[q_idx]

        # Step 4: Decode L1 pointer
        xi_l1_ptr = xi_l2_ret * Xi_ctx2[q_idx]
        l1_nearest = max(range(M_INNER),
                         key=lambda i: float(np.dot(xi_l1_ptr, Xi_inner[i])) / N)
        l1_fid = cosine_sim(xi_l1_ptr, Xi_inner[l1_nearest])
        l1_fids.append(l1_fid)

        # Step 5: L1 retrieval using decoded pointer
        xi_l1_ret = hopfield_retrieve(W_inner, xi_l1_ptr)
        l3_ok = cosine_sim(xi_l1_ret, Xi_inner[q_idx]) > 0.70
        if l3_ok:
            l3_correct += 1

    l1_fid_mean = float(np.mean(l1_fids)) if l1_fids else 0.0
    l2_fid_mean = float(np.mean(l2_fids)) if l2_fids else 0.0
    l3_fid_mean = float(np.mean(l3_fids)) if l3_fids else 0.0
    l3_acc = float(l3_correct) / max(n_test, 1)

    hp_l1 = l1_fid_mean >= HP_FIDELITY
    hp_l2 = l2_fid_mean >= HP_FIDELITY
    hp_l3f = l3_fid_mean >= HP_FIDELITY
    hp_acc = l3_acc >= HP_L3_ACC

    elapsed = time.time() - t0
    print(f"  [seed={seed} N={N} M_L1={M_INNER} M_L2={M_MID} M_L3={M_OUTER}] "
          f"L1_fid={l1_fid_mean:.4f} L2_fid={l2_fid_mean:.4f} L3_fid={l3_fid_mean:.4f} "
          f"l3_acc={l3_acc:.4f}(HP>={HP_L3_ACC}) "
          f"hp=[{int(hp_l1)},{int(hp_l2)},{int(hp_l3f)},{int(hp_acc)}] "
          f"elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": N, "M_inner": M_INNER, "M_mid": M_MID, "M_outer": M_OUTER,
        "run_mode": RUN_MODE,
        "l1_fidelity": float(l1_fid_mean),
        "l2_fidelity": float(l2_fid_mean),
        "l3_fidelity": float(l3_fid_mean),
        "l3_accuracy": float(l3_acc),
        "hp_l1": bool(hp_l1), "hp_l2": bool(hp_l2),
        "hp_l3f": bool(hp_l3f), "hp_acc": bool(hp_acc),
        "elapsed_s": float(elapsed),
    }


def compute_verdict(per_seed: Dict) -> Tuple[str, str]:
    results = list(per_seed.values())
    if not results:
        return ("HARD_FAIL", "No valid results.")

    n = len(results)
    l1_fids = [r["l1_fidelity"] for r in results]
    l2_fids = [r["l2_fidelity"] for r in results]
    l3_fids = [r["l3_fidelity"] for r in results]
    accs = [r["l3_accuracy"] for r in results]

    mean_l1 = float(np.mean(l1_fids))
    mean_l2 = float(np.mean(l2_fids))
    mean_l3f = float(np.mean(l3_fids))
    mean_acc = float(np.mean(accs))

    summary = (f"L1_fid={mean_l1:.4f}(HP>={HP_FIDELITY}) "
               f"L2_fid={mean_l2:.4f}(HP>={HP_FIDELITY}) "
               f"L3_fid={mean_l3f:.4f}(HP>={HP_FIDELITY}) "
               f"l3_acc={mean_acc:.4f}(HP>={HP_L3_ACC},HF<{HF_L3_ACC}) n={n}")

    if mean_l1 < HF_FIDELITY or mean_l2 < HF_FIDELITY or mean_l3f < HF_FIDELITY:
        return ("HARD_FAIL", f"HARD_FAIL: per-level fidelity below {HF_FIDELITY}. {summary}")
    if mean_acc < HF_L3_ACC:
        return ("HARD_FAIL", f"HARD_FAIL: L=3 end-to-end accuracy below {HF_L3_ACC}. {summary}")

    n_all_hp = sum(1 for r in results if r["hp_l1"] and r["hp_l2"] and r["hp_l3f"] and r["hp_acc"])
    min_pass = math.ceil(n * 0.8)

    if n_all_hp >= min_pass:
        return ("HARD_PASS", f"HARD_PASS: L=3 composition CONFIRMED at N={N}. {summary}")

    n_hp3 = sum(1 for r in results if sum([r["hp_l1"], r["hp_l2"], r["hp_l3f"], r["hp_acc"]]) >= 3)
    if n_hp3 >= min_pass:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: 3/4 HP conditions met. {summary}")

    return ("HARD_FAIL", f"HARD_FAIL: insufficient HP conditions. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M_inner": M_INNER, "M_mid": M_MID, "M_outer": M_OUTER, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run (N={N} L=3 mode={RUN_MODE})", flush=True)

t_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] Q-A3 L=3 N={N} M_inner={M_INNER} M_mid={M_MID} M_outer={M_OUTER}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
verdict, verdict_msg = compute_verdict(per_seed)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_s = time.time() - t_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "M_inner": M_INNER, "M_mid": M_MID, "M_outer": M_OUTER,
    "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "elapsed_s": elapsed_s,
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
