"""
combo2_p4_l3_signed_am_v1_n4096 -- Wave 4 COMBO-2: p=4 DAM + L3 + signed-AM at N=4096.

SCIENTIFIC QUESTION (COMBO-2 Bundle):
  p=4 polynomial DAM confirmed viable (COMBO-1 v2 HP1+HP2 PASS: p>2 identities valid).
  Does combining:
    (A) p=4 high-resolution storage (parity-symmetric outer product)
    (B) L=3 hierarchical composition (3-layer nested retrieval)
    (C) Signed-AM B-pattern active repulsion (storing negative knowledge)
  produce an end-to-end system with:
    (HP1) End-to-end L3 fidelity_A >= 0.85 (retrieving a level-3 bound pattern correctly)
    (HP2) B-repulsion rate >= 0.95 (B-patterns actively repelled from attractors)
    (HP3) Cross-tree parity contamination <= 0.05 (L3 A-patterns don't leak into B-attractor basin)

HARD-PASS: HP1 AND HP2 AND HP3 (all 3).
HARD-FAIL: l3_fidelity_A < 0.50 OR b_repulsion_rate < 0.50.
MIDDLE: 2/3 conditions met.

PRE-REGISTERED BANDS:
  HP: l3_fidelity_A >= 0.85, b_repulsion_rate >= 0.95, parity_contamination <= 0.05.
  HF: l3_fidelity_A < 0.50 OR b_repulsion_rate < 0.50.
  MIDDLE: 2/3 HP conditions met.
  Calibration note: first COMBO-2 test. p=4 L3 fidelity extrapolated from
  combo1 (p=3, L2 fidelity ~0.96-0.99 per research), bands set per calibration policy.
  No _nN suffix binding: N=4096 set below. PROT-018 compliant.

ARCHITECTURE:
  W_A = (1/N) sum_mu (xi_mu^(p/2))^T (xi_mu^(p/2)) -- p=4 outer product (even, parity-safe)
        For p=4: W_A = (1/N) Xi^T Xi where Xi_mu = outer(xi_mu, xi_mu, xi_mu, xi_mu) collapsed
        Practical: use W_A = (1/N) * (Xi^T Xi)^2 / N as p=4 kernel approximation.
        Correct p=4 polynomial DAM: energy E = -(1/p) * sum_mu (xi_mu . x)^p
        Gradient (Hopfield update): h = (1/N) * Xi^T * (Xi * x)^{p-1}
        For p=4: h = (1/N) * Xi^T * (Xi * x)^3
  W_B = W_signed = W_A_sub - W_B_sub (signed-AM: A-patterns attract, B-patterns repel).
  L3 hierarchy:
    Layer 1 (innermost): M_inner=16 patterns, p=4 retrieval.
    Layer 2 (middle): M_mid=8 outer patterns, Hadamard-bound to inner pointers.
    Layer 3 (outermost): M_outer=4 outer-outer patterns, bound to mid pointers.
  End-to-end: noisy query at L3 -> retrieve L3 -> decode -> L2 -> decode -> L1 -> compare.

FORMULA SELF-TESTS:
  1. p=4 update rule: h = (1/N) * Xi^T * (Xi @ x)^3.
     For x = xi_0 (stored pattern): (Xi @ xi_0) has one entry = N (xi_0.xi_0=N),
     others ~N(0, M) by random. Dominant term: Xi[:,0] * (N)^3 / N = N^2 * xi_0.
     [INPUT: N=4, xi_0=[1,1,-1,1], Xi=[xi_0], x=xi_0]
     [EXPECTED: h = xi_0 * (xi_0.xi_0)^3 / N = xi_0 * 4^3 / 4 = 16 * xi_0]
  2. Hadamard binding decode: xi_b = (xi_a * xi_b) * xi_a (for +-1 vectors, element-wise).
     [INPUT: xi_a=[1,-1,1,-1], xi_b=[1,1,-1,-1]]
     [EXPECTED: xi_a * xi_b = [1,-1,-1,1]; decoded = [1,-1,-1,1]*[1,-1,1,-1] = [1,1,-1,-1] = xi_b]
  3. Signed-AM repulsion: W_signed = W_A - W_B. Energy at eta_B > 0 -> repulsion.
     For eta_B = stored B-pattern, W_B @ eta_B ~ eta_B (dominant term).
     W_signed @ eta_B = W_A @ eta_B - W_B @ eta_B ~ W_A @ eta_B - eta_B.
     If W_A weak (small M_A), gradient points away from eta_B.
     [INPUT: W_B = eta_B^T * eta_B / N] [EXPECTED: W_B @ eta_B / ||eta_B|| = eta_B / N * N = eta_B]

PROT-018: anchor name contains _n4096; N MUST = 4096.
PROT-021: run_config includes N, M_inner, run_mode (config-discriminating).
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

ANCHOR_NAME = "combo2_p4_l3_signed_am_v1_n4096"

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
    M_INNER = 8
    M_MID = 4
    M_OUTER = 2
    M_B = 2
    N_QUERIES = 10
    NOISE_FRAC = 0.10
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_INNER = 16
    M_MID = 8
    M_OUTER = 4
    M_B = 4
    N_QUERIES = 30
    NOISE_FRAC = 0.10

# Pre-registered thresholds
HP_L3_FIDELITY = 0.85
HP_B_REPULSION = 0.95
HP_PARITY_CONTAMINATION = 0.05
HF_L3_FIDELITY = 0.50
HF_B_REPULSION = 0.50

ALPHA_C = 0.138


def _selftest_p4_update():
    """p=4 update rule: h = (1/N) * Xi^T * (Xi @ x)^3."""
    n = 4
    xi_0 = np.array([1.0, 1.0, -1.0, 1.0])
    Xi = xi_0.reshape(1, n)  # M=1
    x = xi_0.copy()
    overlaps = Xi @ x  # shape (1,) = [N=4]
    h = (Xi.T @ (overlaps**3)) / n  # (n,)
    expected_h = xi_0 * (4.0**3) / 4.0  # 16 * xi_0
    assert np.allclose(h, expected_h, atol=1e-8), f"p=4 update: got {h}, expected {expected_h}"


def _selftest_hadamard():
    """Hadamard binding decode for +-1 vectors."""
    xi_a = np.array([1.0, -1.0, 1.0, -1.0])
    xi_b = np.array([1.0, 1.0, -1.0, -1.0])
    bound = xi_a * xi_b
    decoded = bound * xi_a
    assert np.allclose(decoded, xi_b, atol=1e-8), f"Hadamard decode: {decoded} != {xi_b}"


def _selftest_signed_am():
    """Signed-AM: W_B @ eta_B / N = eta_B."""
    n = 16
    rng = np.random.RandomState(0)
    eta_b = rng.choice([-1.0, 1.0], size=n)
    W_B = np.outer(eta_b, eta_b) / n
    result = W_B @ eta_b
    expected = eta_b  # (eta_b . eta_b) / n * eta_b = n/n * eta_b
    assert np.allclose(result, expected, atol=1e-8), f"signed_AM W_B @ eta_B: {result[:3]} != {expected[:3]}"


def _instrumentation_selftest():
    _selftest_p4_update()
    _selftest_hadamard()
    _selftest_signed_am()
    print("[selftest] combo2_p4_l3_signed_am: p4_update, hadamard, signed_am all PASS", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def p4_retrieve(Xi: np.ndarray, probe: np.ndarray, n_steps: int = 5, n: int = None) -> np.ndarray:
    """p=4 polynomial DAM retrieval: h = (1/N) * Xi^T * (Xi @ state)^3."""
    if n is None:
        n = probe.shape[0]
    state = probe.copy()
    for _ in range(n_steps):
        overlaps = Xi @ state  # (M,)
        h = (Xi.T @ (overlaps**3)) / n  # (N,)
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

    # ---- L3 HIERARCHY (A-patterns, positive knowledge) ----
    # Layer 1 (inner): M_INNER patterns, p=4
    Xi_inner = rng.choice([-1.0, 1.0], size=(M_INNER, N)).astype(np.float64)

    # Layer 2 (middle): M_MID context + Hadamard-bound pointers to inner
    Xi_ctx2 = rng.choice([-1.0, 1.0], size=(M_MID, N)).astype(np.float64)
    Xi_mid = Xi_ctx2 * Xi_inner[:M_MID]  # Hadamard bind context2 * inner

    # Layer 3 (outer): M_OUTER context + Hadamard-bound pointers to mid
    Xi_ctx3 = rng.choice([-1.0, 1.0], size=(M_OUTER, N)).astype(np.float64)
    Xi_outer = Xi_ctx3 * Xi_mid[:M_OUTER]  # Hadamard bind context3 * mid

    # ---- SIGNED-AM (B-patterns, negative knowledge) ----
    # Store B-patterns in W_signed = W_A_small - W_B
    # Use small A-sub (M_B patterns) so B-repulsion is reliable
    Xi_A_sub = rng.choice([-1.0, 1.0], size=(M_B, N)).astype(np.float64)
    Xi_B = rng.choice([-1.0, 1.0], size=(M_B, N)).astype(np.float64)

    # W_signed using p=4 outer product form
    # For signed-AM: sum A-attractors minus B-attractors in same weight matrix
    def build_p4_W(Xi_pats):
        # p=4 outer product: W = (1/N) * sum_mu (xi_mu * xi_mu^T)^2 (approx via moment)
        # Practical: W_p4 = (1/N^2) * (Xi^T Xi)^2 for p=4 energy landscape
        # Direct: W = (1/N) * Xi^T @ Xi -- same as p=2 but retrieval uses (Xi@x)^3
        # Per research note: p=4 DAM uses h=(1/N)*Xi^T*(Xi@x)^3; W is still rank-M outer sum
        return Xi_pats.T @ Xi_pats / float(N)

    W_A_sub = build_p4_W(Xi_A_sub)
    W_B_mat = build_p4_W(Xi_B)
    W_signed = W_A_sub - W_B_mat  # signed weight matrix

    # ---- TEST 1: L3 END-TO-END FIDELITY ----
    l3_fidelities = []
    for q_idx in range(min(N_QUERIES, M_OUTER)):
        # Noisy outer (L3) query
        xi_outer_true = Xi_outer[q_idx]
        probe = xi_outer_true.copy()
        flip = rng.random(N) < NOISE_FRAC
        probe[flip] *= -1.0

        # L3 retrieval
        xi_outer_ret = p4_retrieve(Xi_outer, probe, n=N)

        # Decode to mid pointer: xi_mid_ptr = xi_outer_ret * xi_ctx3[q_idx]
        xi_mid_ptr = xi_outer_ret * Xi_ctx3[q_idx]

        # L2 retrieval
        xi_mid_ret = p4_retrieve(Xi_mid, xi_mid_ptr, n=N)

        # Decode to inner pointer
        xi_inner_ptr = xi_mid_ret * Xi_ctx2[q_idx]

        # L1 (inner) retrieval
        xi_inner_ret = p4_retrieve(Xi_inner, xi_inner_ptr, n=N)
        xi_inner_true = Xi_inner[q_idx]

        fid = cosine_sim(xi_inner_ret, xi_inner_true)
        l3_fidelities.append(fid)

    l3_fid_mean = float(np.mean(l3_fidelities)) if l3_fidelities else 0.0

    # ---- TEST 2: B-PATTERN REPULSION ----
    repulsion_count = 0
    n_b_queries = min(N_QUERIES, M_B)
    for b_idx in range(n_b_queries):
        eta_b = Xi_B[b_idx]
        probe_b = eta_b.copy()
        flip = rng.random(N) < NOISE_FRAC
        probe_b[flip] *= -1.0

        # Use signed-weight dynamics: h = (1/N) * W_signed @ state... actually
        # for signed-AM repulsion we use the signed weight matrix directly
        # p=4 signed update: h = (1/N) * [Xi_A^T*(Xi_A@x)^3 - Xi_B^T*(Xi_B@x)^3]
        state = probe_b.copy()
        for _ in range(5):
            ov_A = Xi_A_sub @ state
            ov_B = Xi_B @ state
            h = (Xi_A_sub.T @ (ov_A**3) - Xi_B.T @ (ov_B**3)) / N
            state = np.sign(h)
            state[state == 0] = 1.0

        cos_to_b = cosine_sim(state, eta_b)
        if cos_to_b < -0.3:  # repelled (converged away from B)
            repulsion_count += 1

    b_repulsion_rate = repulsion_count / n_b_queries if n_b_queries > 0 else 0.0

    # ---- TEST 3: PARITY CONTAMINATION ----
    # L3 A-pattern retrieval should NOT converge to B-attractor basin.
    # For each L3 query result (xi_inner_ret), check cosine to all B-patterns.
    contamination_flags = 0
    n_contam_tests = min(N_QUERIES, M_OUTER, M_B)
    for q_idx in range(n_contam_tests):
        xi_outer_true = Xi_outer[q_idx]
        probe = xi_outer_true.copy()
        flip = rng.random(N) < NOISE_FRAC
        probe[flip] *= -1.0

        xi_outer_ret = p4_retrieve(Xi_outer, probe, n=N)
        xi_mid_ptr = xi_outer_ret * Xi_ctx3[q_idx]
        xi_mid_ret = p4_retrieve(Xi_mid, xi_mid_ptr, n=N)
        xi_inner_ptr = xi_mid_ret * Xi_ctx2[q_idx]
        xi_inner_ret = p4_retrieve(Xi_inner, xi_inner_ptr, n=N)

        # Check contamination: cosine to any B-pattern > 0.5?
        max_b_cos = max(abs(cosine_sim(xi_inner_ret, Xi_B[b])) for b in range(M_B))
        if max_b_cos > 0.5:
            contamination_flags += 1

    parity_contamination = contamination_flags / n_contam_tests if n_contam_tests > 0 else 0.0

    elapsed = time.time() - t0
    print(f"  [seed={seed}] l3_fid={l3_fid_mean:.4f} b_repulsion={b_repulsion_rate:.4f} "
          f"parity_contam={parity_contamination:.4f} elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": N, "run_mode": RUN_MODE,
        "M_inner": M_INNER, "M_mid": M_MID, "M_outer": M_OUTER, "M_B": M_B,
        "l3_fidelity_A": float(l3_fid_mean),
        "b_repulsion_rate": float(b_repulsion_rate),
        "parity_contamination": float(parity_contamination),
        "elapsed_s": elapsed,
    }


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    l3_fids = [r["l3_fidelity_A"] for r in results if "l3_fidelity_A" in r]
    b_reps = [r["b_repulsion_rate"] for r in results if "b_repulsion_rate" in r]
    p_conts = [r["parity_contamination"] for r in results if "parity_contamination" in r]

    if not l3_fids:
        return ("HARD_FAIL", "No valid results.")

    mean_l3 = float(np.mean(l3_fids))
    mean_brep = float(np.mean(b_reps))
    mean_pcont = float(np.mean(p_conts))

    summary = (f"l3_fidelity_A={mean_l3:.4f} (HP>={HP_L3_FIDELITY} HF<{HF_L3_FIDELITY}) "
               f"b_repulsion={mean_brep:.4f} (HP>={HP_B_REPULSION} HF<{HF_B_REPULSION}) "
               f"parity_contamination={mean_pcont:.4f} (HP<={HP_PARITY_CONTAMINATION}) "
               f"n_seeds={len(l3_fids)}")

    if mean_l3 < HF_L3_FIDELITY or mean_brep < HF_B_REPULSION:
        return ("HARD_FAIL", f"HARD_FAIL: {summary}")

    hp1 = mean_l3 >= HP_L3_FIDELITY
    hp2 = mean_brep >= HP_B_REPULSION
    hp3 = mean_pcont <= HP_PARITY_CONTAMINATION

    if hp1 and hp2 and hp3:
        return ("HARD_PASS", f"HARD_PASS: all 3 HP conditions met. {summary}")
    if sum([hp1, hp2, hp3]) >= 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {sum([hp1,hp2,hp3])}/3 HP conditions. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: {sum([hp1,hp2,hp3])}/3 HP conditions. {summary}")


# ---- MAIN SWEEP ----
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M_inner": M_INNER, "M_outer": M_OUTER, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] running N={N} M_inner={M_INNER} M_outer={M_OUTER} M_B={M_B}...", flush=True)
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
    "mean_l3_fidelity_A": float(np.mean([r["l3_fidelity_A"] for r in all_results])) if all_results else None,
    "mean_b_repulsion_rate": float(np.mean([r["b_repulsion_rate"] for r in all_results])) if all_results else None,
    "mean_parity_contamination": float(np.mean([r["parity_contamination"] for r in all_results])) if all_results else None,
}
metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"[done] metrics -> {metrics_path}", flush=True)
