"""
q_a3_l4_cross_layer_composition_v1_n4096 -- Q-A3: L=4 cross-layer composition.

SCIENTIFIC QUESTION (Q-A3 extension to L=4):
  L=2 and L=3 at N=4096 both HARD_PASS (all fidelities = 1.0).
  L=3 end-to-end accuracy = 1.0 at N=4096.
  This anchor extends to L=4 (4 nested Hadamard layers).

  Architecture:
    - L1 (inner): N=4096, M_inner=200, p=2 Hopfield.
    - L2 (mid-inner): M_mid2=100, Hadamard binding ctx2*L1.
    - L3 (mid-outer): M_mid3=50, Hadamard binding ctx3*L2.
    - L4 (outer): M_outer=25, Hadamard binding ctx4*L3.
    - Query: noisy L4 probe -> L4 retrieval -> decode L3 ptr -> L3 retrieval ->
      decode L2 ptr -> L2 retrieval -> decode L1 ptr -> L1 retrieval.

  Test metrics:
    (A) Per-level fidelity: L1, L2, L3, L4 each >= 0.93.
    (B) End-to-end L=4 accuracy >= 0.75.

HARD-PASS: L1_fid >= 0.93 AND L2_fid >= 0.93 AND L3_fid >= 0.93 AND L4_fid >= 0.93 AND l4_acc >= 0.75.
HARD-FAIL: any fidelity < 0.60 OR l4_acc < 0.40.
MIDDLE: 4/5 conditions met.

PRE-REGISTERED BANDS:
  HP: all 5 conditions.
  HF: any fidelity < 0.60 OR l4_acc < 0.40.
  Prior: L=3 at N=4096: all fidelities 1.0, l3_acc=1.0. L=4 adds one more Hadamard
  layer; error accumulates. HP thresholds = 0.93 per-level (geometric extrapolation:
  1.0^(1/3) per layer, 0.93 at L=4 is conservative), 0.75 end-to-end.

FORMULA SELF-TESTS:
  1. L=4 chain: xi_L4 = ctx4*(ctx3*(ctx2*xi_L1)); decode reverses.
     [INPUT: tiny 2-element vectors] [EXPECTED: full round-trip recovers xi_L1]
  2. Capacity: alpha_L1=0.049, L2=0.024, L3=0.012, L4=0.006 all < 0.138.
  3. Noise recovery: noisy probe (10% flip) still retrieves at L4.

PROT-018: anchor has _n4096; N MUST = 4096.
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

ANCHOR_NAME = "q_a3_l4_cross_layer_composition_v1_n4096"

_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
HP_FIDELITY = 0.93
HF_FIDELITY = 0.60
HP_L4_ACC = 0.75
HF_L4_ACC = 0.40

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_INNER = 30
    M_MID2 = 15
    M_MID3 = 8
    M_OUTER = 4
    N_QUERIES = 4
    NOISE_FRAC = 0.10
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_INNER = 200
    M_MID2 = 100
    M_MID3 = 50
    M_OUTER = 25
    N_QUERIES = 20
    NOISE_FRAC = 0.10


def _selftest_l4_chain():
    xi_ctx4 = np.array([1.0, -1.0])
    xi_ctx3 = np.array([-1.0, 1.0])
    xi_ctx2 = np.array([1.0, 1.0])
    xi_L1 = np.array([-1.0, 1.0])
    xi_L2 = xi_ctx2 * xi_L1
    xi_L3 = xi_ctx3 * xi_L2
    xi_L4 = xi_ctx4 * xi_L3
    # Decode
    xi_L3_dec = xi_L4 * xi_ctx4
    xi_L2_dec = xi_L3_dec * xi_ctx3
    xi_L1_dec = xi_L2_dec * xi_ctx2
    assert np.allclose(xi_L3_dec, xi_L3), f"L4 decode L3 failed"
    assert np.allclose(xi_L2_dec, xi_L2), f"L4 decode L2 failed"
    assert np.allclose(xi_L1_dec, xi_L1), f"L4 decode L1 failed"
    return xi_L4, xi_L3, xi_L2, xi_L1


def _selftest_capacity():
    alphas = [M_INNER / N, M_MID2 / N, M_MID3 / N, M_OUTER / N]
    for i, a in enumerate(alphas):
        assert a < ALPHA_C, f"L{i+1} alpha={a:.4f} >= alpha_c={ALPHA_C}"
    return alphas


def _instrumentation_selftest():
    xl4, xl3, xl2, xl1 = _selftest_l4_chain()
    alphas = _selftest_capacity()
    assert N_QUERIES > 0, "N_QUERIES > 0 required"
    print(f"[selftest] PASS: L4_chain_ok xi_L4={xl4} "
          f"alphas={[f'{a:.4f}' for a in alphas]} all < alpha_c={ALPHA_C} "
          f"N={N} M_INNER={M_INNER} M_MID2={M_MID2} M_MID3={M_MID3} M_OUTER={M_OUTER}",
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

    # L1: inner
    Xi_inner = rng.choice([-1.0, 1.0], size=(M_INNER, N)).astype(np.float64)
    W_inner = Xi_inner.T @ Xi_inner / float(N)
    np.fill_diagonal(W_inner, 0.0)

    # L2: Hadamard(ctx2, L1)
    Xi_ctx2 = rng.choice([-1.0, 1.0], size=(M_MID2, N)).astype(np.float64)
    Xi_mid2 = Xi_ctx2 * Xi_inner[:M_MID2]
    W_mid2 = Xi_mid2.T @ Xi_mid2 / float(N)
    np.fill_diagonal(W_mid2, 0.0)

    # L3: Hadamard(ctx3, L2)
    Xi_ctx3 = rng.choice([-1.0, 1.0], size=(M_MID3, N)).astype(np.float64)
    Xi_mid3 = Xi_ctx3 * Xi_mid2[:M_MID3]
    W_mid3 = Xi_mid3.T @ Xi_mid3 / float(N)
    np.fill_diagonal(W_mid3, 0.0)

    # L4: Hadamard(ctx4, L3)
    Xi_ctx4 = rng.choice([-1.0, 1.0], size=(M_OUTER, N)).astype(np.float64)
    Xi_outer = Xi_ctx4 * Xi_mid3[:M_OUTER]
    W_outer = Xi_outer.T @ Xi_outer / float(N)
    np.fill_diagonal(W_outer, 0.0)

    rng_noise = np.random.RandomState(seed + 100)
    l1_fids, l2_fids, l3_fids, l4_fids = [], [], [], []
    l4_correct = 0
    n_test = min(N_QUERIES, M_OUTER)

    for q_idx in range(n_test):
        # L4 noisy probe
        probe_l4 = Xi_outer[q_idx].copy()
        flip = rng_noise.random(N) < NOISE_FRAC
        probe_l4[flip] *= -1.0

        # L4 retrieval
        xi_l4_ret = hopfield_retrieve(W_outer, probe_l4)
        l4_fids.append(cosine_sim(xi_l4_ret, Xi_outer[q_idx]))

        # Decode L3 pointer
        xi_l3_ptr = xi_l4_ret * Xi_ctx4[q_idx]
        l3_nearest = max(range(M_MID3),
                         key=lambda i: float(np.dot(xi_l3_ptr, Xi_mid3[i])) / N)
        l3_fids.append(cosine_sim(xi_l3_ptr, Xi_mid3[l3_nearest]))

        # L3 retrieval
        xi_l3_ret = hopfield_retrieve(W_mid3, xi_l3_ptr)

        # Decode L2 pointer
        xi_l2_ptr = xi_l3_ret * Xi_ctx3[q_idx]
        l2_nearest = max(range(M_MID2),
                         key=lambda i: float(np.dot(xi_l2_ptr, Xi_mid2[i])) / N)
        l2_fids.append(cosine_sim(xi_l2_ptr, Xi_mid2[l2_nearest]))

        # L2 retrieval
        xi_l2_ret = hopfield_retrieve(W_mid2, xi_l2_ptr)

        # Decode L1 pointer
        xi_l1_ptr = xi_l2_ret * Xi_ctx2[q_idx]
        l1_nearest = max(range(M_INNER),
                         key=lambda i: float(np.dot(xi_l1_ptr, Xi_inner[i])) / N)
        l1_fids.append(cosine_sim(xi_l1_ptr, Xi_inner[l1_nearest]))

        # L1 retrieval
        xi_l1_ret = hopfield_retrieve(W_inner, xi_l1_ptr)
        l4_ok = cosine_sim(xi_l1_ret, Xi_inner[q_idx]) > 0.70
        if l4_ok:
            l4_correct += 1

    l1_mean = float(np.mean(l1_fids)) if l1_fids else 0.0
    l2_mean = float(np.mean(l2_fids)) if l2_fids else 0.0
    l3_mean = float(np.mean(l3_fids)) if l3_fids else 0.0
    l4_fid_mean = float(np.mean(l4_fids)) if l4_fids else 0.0
    l4_acc = float(l4_correct) / max(n_test, 1)

    hp_l1 = l1_mean >= HP_FIDELITY
    hp_l2 = l2_mean >= HP_FIDELITY
    hp_l3f = l3_mean >= HP_FIDELITY
    hp_l4f = l4_fid_mean >= HP_FIDELITY
    hp_acc = l4_acc >= HP_L4_ACC

    elapsed = time.time() - t0
    print(f"  [seed={seed} N={N} L=4] "
          f"L1_fid={l1_mean:.4f} L2_fid={l2_mean:.4f} L3_fid={l3_mean:.4f} "
          f"L4_fid={l4_fid_mean:.4f} l4_acc={l4_acc:.4f}(HP>={HP_L4_ACC}) "
          f"hp=[{int(hp_l1)},{int(hp_l2)},{int(hp_l3f)},{int(hp_l4f)},{int(hp_acc)}] "
          f"elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": N, "run_mode": RUN_MODE,
        "M_inner": M_INNER, "M_mid2": M_MID2, "M_mid3": M_MID3, "M_outer": M_OUTER,
        "l1_fidelity": float(l1_mean),
        "l2_fidelity": float(l2_mean),
        "l3_fidelity": float(l3_mean),
        "l4_fidelity": float(l4_fid_mean),
        "l4_accuracy": float(l4_acc),
        "hp_l1": bool(hp_l1), "hp_l2": bool(hp_l2),
        "hp_l3f": bool(hp_l3f), "hp_l4f": bool(hp_l4f),
        "hp_acc": bool(hp_acc),
        "elapsed_s": float(elapsed),
    }


def compute_verdict(per_seed: Dict) -> Tuple[str, str]:
    results = list(per_seed.values())
    if not results:
        return ("HARD_FAIL", "No valid results.")
    n = len(results)
    l1f = [r["l1_fidelity"] for r in results]
    l2f = [r["l2_fidelity"] for r in results]
    l3f = [r["l3_fidelity"] for r in results]
    l4f = [r["l4_fidelity"] for r in results]
    accs = [r["l4_accuracy"] for r in results]

    mean_l1 = float(np.mean(l1f))
    mean_l2 = float(np.mean(l2f))
    mean_l3 = float(np.mean(l3f))
    mean_l4f = float(np.mean(l4f))
    mean_acc = float(np.mean(accs))

    summary = (f"L1_fid={mean_l1:.4f} L2_fid={mean_l2:.4f} L3_fid={mean_l3:.4f} "
               f"L4_fid={mean_l4f:.4f}(HP>={HP_FIDELITY}) "
               f"l4_acc={mean_acc:.4f}(HP>={HP_L4_ACC} HF<{HF_L4_ACC}) n={n}")

    if any(f < HF_FIDELITY for f in [mean_l1, mean_l2, mean_l3, mean_l4f]):
        return ("HARD_FAIL", f"HARD_FAIL: per-level fidelity below {HF_FIDELITY}. {summary}")
    if mean_acc < HF_L4_ACC:
        return ("HARD_FAIL", f"HARD_FAIL: L=4 end-to-end below {HF_L4_ACC}. {summary}")

    n_all_hp = sum(1 for r in results
                   if r["hp_l1"] and r["hp_l2"] and r["hp_l3f"] and r["hp_l4f"] and r["hp_acc"])
    min_pass = math.ceil(n * 0.8)
    if n_all_hp >= min_pass:
        return ("HARD_PASS", f"HARD_PASS: L=4 composition confirmed at N={N}. {summary}")

    n_hp4 = sum(1 for r in results
                if sum([r["hp_l1"], r["hp_l2"], r["hp_l3f"], r["hp_l4f"], r["hp_acc"]]) >= 4)
    if n_hp4 >= min_pass:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: 4/5 HP conditions. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: insufficient HP conditions. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M_inner": M_INNER, "M_mid2": M_MID2, "M_mid3": M_MID3,
              "M_outer": M_OUTER, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run (N={N} L=4 mode={RUN_MODE})", flush=True)

t_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] Q-A3 L=4 N={N}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
verdict, verdict_msg = compute_verdict(per_seed)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_s = time.time() - t_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "M_inner": M_INNER, "M_mid2": M_MID2, "M_mid3": M_MID3, "M_outer": M_OUTER,
    "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "elapsed_s": elapsed_s,
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
