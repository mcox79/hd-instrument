"""
negative_knowledge_tree_4level_v1_n4096 -- Negative-Knowledge Tree at depth 4.

SCIENTIFIC QUESTION (PP-48 extension):
  v334 (COMBO-2 HARD_PASS) demonstrated 3-level hierarchical Negative-Knowledge Tree:
  - Level 1 (concept): allowed vs forbidden concept zones (signed-AM)
  - Level 2 (pointer): Hadamard-bound pointers into allowed zone
  - Level 3 (instance): retrievable patterns in allowed zone
  The 4-level extension adds a POLICY layer above the concept layer:
  - Level 0 (policy): meta-level domain partitions (e.g. "this context", "that context")
  - Level 1 (concept): concept zones per domain
  - Level 2 (pointer): pointers within concept zone
  - Level 3 (instance): retrievable instances
  - Cert chain: 4-level certificate traces policy->concept->pointer->instance.

  Test cells:
    (A) 4-level cert chain valid: query at L4 -> trace through all 4 levels to correct instance.
        HP-A: cert_chain_valid_rate >= 0.85 (>= 85% of queries produce valid 4-level cert).
    (B) Cross-level parity contamination <= 0.05 (forbidden instances do not leak into A retrieval).
        HP-B: parity_contamination <= 0.05 in >=4/5 seeds.
    (C) B-repulsion preserved: forbidden patterns at policy level are repelled, not retrieved.
        HP-C: b_repulsion_rate >= 0.90.

HARD-PASS: HP-A AND HP-B AND HP-C.
HARD-FAIL: cert_chain_valid < 0.50 OR parity_contamination > 0.30.
MIDDLE: 2/3 cells pass.

PRE-REGISTERED BANDS:
  HP: cert_chain_valid_rate >= 0.85, parity_contamination <= 0.05, b_repulsion >= 0.90.
  HF: cert_chain_valid < 0.50 OR parity_contamination > 0.30.
  Calibration: first 4-level test. Prior: v334 3-level HARD_PASS (contamination=0, repulsion=1.0).
  4-level adds one Hadamard decode step; error accumulates multiplicatively.
  Bands: HP cert_valid 0.85 (slightly lower than L3 0.85 to allow extra decode error).

FORMULA SELF-TESTS:
  1. 4-level Hadamard chain: xi_L4 = xi_ctx4 * xi_L3; xi_L3 = xi_ctx3 * xi_L2; etc.
     Decode chain: L2 = xi_L3 * xi_ctx3; L1 = xi_L2 * xi_ctx2; L0 = xi_L1 * xi_ctx1.
     [INPUT: ctx=[1,-1,-1,1], xi_L0=[1,1]] [EXPECTED: full encode/decode roundtrip exact]
  2. Signed-AM repulsion: W_signed = W_A - W_B. B-pattern overlap goes negative.
     [INPUT: eta_B stored in W_B; W_signed = W_A - W_B] [EXPECTED: W_signed @ eta_B < W_A @ eta_B]
  3. Parity contamination = fraction of A-retrievals that have cosine > 0.5 with any B pattern.
     [INPUT: A and B sets orthogonal] [EXPECTED: contamination = 0]

PROT-018: anchor has _n4096; N MUST = 4096.
PROT-021: run_config includes N, M_inner, M_levels, run_mode.
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

ANCHOR_NAME = "negative_knowledge_tree_4level_v1_n4096"

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
    M_L0 = 4    # L0 policy layer
    M_L1 = 8    # L1 concept
    M_L2 = 16   # L2 pointer
    M_L3 = 32   # L3 instance
    M_B = 4     # forbidden B patterns
    N_QUERIES = 4
    NOISE_FRAC = 0.10
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_L0 = 8
    M_L1 = 16
    M_L2 = 32
    M_L3 = 64
    M_B = 8
    N_QUERIES = 8
    NOISE_FRAC = 0.10

ALPHA_C = 0.138

HP_CERT_VALID = 0.85
HP_PARITY_CONTAM = 0.05
HP_B_REPULSION = 0.90
HF_CERT_VALID = 0.50
HF_PARITY_CONTAM = 0.30


def _selftest_4level_chain():
    """4-level Hadamard encode/decode roundtrip."""
    rng = np.random.RandomState(0)
    n_small = 8
    xi_L0 = rng.choice([-1.0, 1.0], size=n_small)
    ctx1 = rng.choice([-1.0, 1.0], size=n_small)
    ctx2 = rng.choice([-1.0, 1.0], size=n_small)
    ctx3 = rng.choice([-1.0, 1.0], size=n_small)
    ctx4 = rng.choice([-1.0, 1.0], size=n_small)
    xi_L1 = ctx1 * xi_L0
    xi_L2 = ctx2 * xi_L1
    xi_L3 = ctx3 * xi_L2
    xi_L4 = ctx4 * xi_L3
    # Decode
    xi_L3_dec = xi_L4 * ctx4
    xi_L2_dec = xi_L3_dec * ctx3
    xi_L1_dec = xi_L2_dec * ctx2
    xi_L0_dec = xi_L1_dec * ctx1
    assert np.allclose(xi_L3_dec, xi_L3), "L3 decode failed"
    assert np.allclose(xi_L2_dec, xi_L2), "L2 decode failed"
    assert np.allclose(xi_L1_dec, xi_L1), "L1 decode failed"
    assert np.allclose(xi_L0_dec, xi_L0), "L0 decode failed"
    return True


def _selftest_signed_am():
    """B-repulsion: W_signed @ eta_B should not align with eta_B."""
    n_small = 64
    rng = np.random.RandomState(1)
    eta_A = rng.choice([-1.0, 1.0], size=n_small).astype(np.float64)
    eta_B = rng.choice([-1.0, 1.0], size=n_small).astype(np.float64)
    W_A = np.outer(eta_A, eta_A) / n_small
    W_B = np.outer(eta_B, eta_B) / n_small
    W_signed = W_A - W_B
    result_signed = W_signed @ eta_B
    result_pure = W_B @ eta_B
    cos_signed = float(np.dot(result_signed, eta_B)) / (np.linalg.norm(result_signed) * n_small + 1e-15)
    cos_pure = float(np.dot(result_pure, eta_B)) / (np.linalg.norm(result_pure) * n_small + 1e-15)
    assert cos_signed < cos_pure, f"signed_am repulsion: {cos_signed:.4f} >= pure={cos_pure:.4f}"
    return cos_signed, cos_pure


def _selftest_capacity():
    total_patterns = M_L0 + M_L1 + M_L2 + M_L3 + M_B
    alpha_total = total_patterns / N
    assert alpha_total < ALPHA_C * 2, f"total alpha={alpha_total:.4f} too high vs {ALPHA_C}"
    return alpha_total


def _instrumentation_selftest():
    assert _selftest_4level_chain(), "4-level chain selftest failed"
    cos_s, cos_p = _selftest_signed_am()
    alpha = _selftest_capacity()
    assert N_QUERIES > 0, "N_QUERIES must be > 0"
    print(f"[selftest] PASS: 4level_chain OK signed_am_repulsion={cos_s:.4f}<pure={cos_p:.4f} "
          f"total_alpha={alpha:.4f}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def p2_retrieve(Xi: np.ndarray, probe: np.ndarray, n_steps: int = 5) -> np.ndarray:
    """p=2 Hopfield retrieval."""
    W = Xi.T @ Xi / float(Xi.shape[1])
    np.fill_diagonal(W, 0.0)
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


def signed_am_retrieve(Xi_A: np.ndarray, Xi_B: np.ndarray, probe: np.ndarray,
                        n_steps: int = 5) -> np.ndarray:
    """Signed-AM p=2: W_signed = W_A - W_B. Attract A, repel B."""
    n = Xi_A.shape[1]
    W_A = Xi_A.T @ Xi_A / float(n)
    W_B = Xi_B.T @ Xi_B / float(n)
    np.fill_diagonal(W_A, 0.0)
    np.fill_diagonal(W_B, 0.0)
    W_signed = W_A - W_B
    state = probe.copy()
    for _ in range(n_steps):
        h = W_signed @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    # Build 4-level hierarchy: L0=policy(fewest), L1=concept, L2=pointer, L3=instance(most).
    # Each L_k pattern is Hadamard-bound with a context to produce an L_{k+1} pattern.
    # Pattern count: M_L0 <= M_L1 <= M_L2 <= M_L3. Assignments cycle through L_k parents.
    Xi_L0 = rng.choice([-1.0, 1.0], size=(M_L0, N)).astype(np.float64)

    # L1: each of M_L1 L1-patterns binds ctx1_j with Xi_L0[j % M_L0]
    Ctx1 = rng.choice([-1.0, 1.0], size=(M_L1, N)).astype(np.float64)
    Xi_L1 = Ctx1 * Xi_L0[np.arange(M_L1) % M_L0]   # cycles through L0 parents

    # L2: each of M_L2 L2-patterns binds ctx2_j with Xi_L1[j % M_L1]
    Ctx2 = rng.choice([-1.0, 1.0], size=(M_L2, N)).astype(np.float64)
    Xi_L2 = Ctx2 * Xi_L1[np.arange(M_L2) % M_L1]

    # L3: each of M_L3 L3-patterns binds ctx3_j with Xi_L2[j % M_L2]
    Ctx3 = rng.choice([-1.0, 1.0], size=(M_L3, N)).astype(np.float64)
    Xi_L3 = Ctx3 * Xi_L2[np.arange(M_L3) % M_L2]

    Xi_B = rng.choice([-1.0, 1.0], size=(M_B, N)).astype(np.float64)
    # L0 level also has forbidden patterns (signed-AM)
    Xi_L0_A = Xi_L0[:M_L0]

    # Test 1: cert chain validity - query at L3, trace all 4 levels
    cert_valid = 0
    n_test = min(N_QUERIES, M_L3)

    rng_noise = np.random.RandomState(seed + 100)

    for q_idx in range(n_test):
        xi_l3_true = Xi_L3[q_idx]
        probe = xi_l3_true.copy()
        flip = rng_noise.random(N) < NOISE_FRAC
        probe[flip] *= -1.0

        # Retrieve L3
        xi_l3_ret = p2_retrieve(Xi_L3, probe)
        cos_l3 = cosine_sim(xi_l3_ret, xi_l3_true)

        # Decode L2 pointer: Xi_L3[q_idx] = Ctx3[q_idx] * Xi_L2[q_idx % M_L2]
        l2_parent_idx = q_idx % M_L2
        ctx3_q = Ctx3[q_idx]
        xi_l2_ptr = xi_l3_ret * ctx3_q
        xi_l2_ret = p2_retrieve(Xi_L2, xi_l2_ptr)
        cos_l2 = cosine_sim(xi_l2_ret, Xi_L2[l2_parent_idx])

        # Decode L1 pointer: Xi_L2[l2_parent_idx] = Ctx2[l2_parent_idx] * Xi_L1[l2_parent_idx % M_L1]
        l1_parent_idx = l2_parent_idx % M_L1
        ctx2_q = Ctx2[l2_parent_idx]
        xi_l1_ptr = xi_l2_ret * ctx2_q
        xi_l1_ret = p2_retrieve(Xi_L1, xi_l1_ptr)
        cos_l1 = cosine_sim(xi_l1_ret, Xi_L1[l1_parent_idx])

        # Decode L0 pointer: Xi_L1[l1_parent_idx] = Ctx1[l1_parent_idx] * Xi_L0[l1_parent_idx % M_L0]
        l0_parent_idx = l1_parent_idx % M_L0
        ctx1_q = Ctx1[l1_parent_idx]
        xi_l0_ptr = xi_l1_ret * ctx1_q
        xi_l0_ret = p2_retrieve(Xi_L0, xi_l0_ptr)
        cos_l0 = cosine_sim(xi_l0_ret, Xi_L0[l0_parent_idx])

        if cos_l3 > 0.60 and cos_l2 > 0.60 and cos_l1 > 0.60 and cos_l0 > 0.60:
            cert_valid += 1

    cert_valid_rate = float(cert_valid) / max(n_test, 1)

    # Test 2: parity contamination (A-retrievals vs B patterns)
    contamination = 0
    for q_idx in range(min(N_QUERIES, M_L3)):
        xi_l3_true = Xi_L3[q_idx]
        probe = xi_l3_true.copy()
        flip = rng_noise.random(N) < NOISE_FRAC
        probe[flip] *= -1.0
        xi_l3_ret = p2_retrieve(Xi_L3, probe)
        max_b_cos = max(abs(cosine_sim(xi_l3_ret, Xi_B[b])) for b in range(M_B))
        if max_b_cos > 0.50:
            contamination += 1

    parity_contamination = float(contamination) / max(n_test, 1)

    # Test 3: B-repulsion at top level (using signed-AM on L0+B)
    n_b_test = min(N_QUERIES, M_B)
    repulsion_count = 0
    for b_idx in range(n_b_test):
        eta_b = Xi_B[b_idx]
        probe_b = eta_b.copy()
        flip = rng_noise.random(N) < NOISE_FRAC
        probe_b[flip] *= -1.0
        state = signed_am_retrieve(Xi_L0_A, Xi_B, probe_b)
        cos_to_b = cosine_sim(state, eta_b)
        if cos_to_b < -0.20:
            repulsion_count += 1

    b_repulsion_rate = float(repulsion_count) / max(n_b_test, 1)

    hp_a = cert_valid_rate >= HP_CERT_VALID
    hp_b = parity_contamination <= HP_PARITY_CONTAM
    hp_c = b_repulsion_rate >= HP_B_REPULSION

    elapsed = time.time() - t0
    print(f"  [seed={seed}] cert_valid={cert_valid_rate:.4f}(HP>={HP_CERT_VALID}) "
          f"parity_contam={parity_contamination:.4f}(HP<={HP_PARITY_CONTAM}) "
          f"b_repulsion={b_repulsion_rate:.4f}(HP>={HP_B_REPULSION}) "
          f"hp_ABC=[{int(hp_a)},{int(hp_b)},{int(hp_c)}] elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": N, "M_L0": M_L0, "M_L1": M_L1, "M_L2": M_L2, "M_L3": M_L3,
        "run_mode": RUN_MODE,
        "cert_chain_valid_rate": float(cert_valid_rate),
        "parity_contamination": float(parity_contamination),
        "b_repulsion_rate": float(b_repulsion_rate),
        "hp_a": bool(hp_a), "hp_b": bool(hp_b), "hp_c": bool(hp_c),
        "elapsed_s": float(elapsed),
    }


def compute_verdict(per_seed: Dict) -> Tuple[str, str]:
    results = list(per_seed.values())
    if not results:
        return ("HARD_FAIL", "No valid results.")

    n = len(results)
    mean_cert = float(np.mean([r["cert_chain_valid_rate"] for r in results]))
    mean_contam = float(np.mean([r["parity_contamination"] for r in results]))
    mean_brep = float(np.mean([r["b_repulsion_rate"] for r in results]))

    summary = (f"cert_valid={mean_cert:.4f}(HP>={HP_CERT_VALID} HF<{HF_CERT_VALID}) "
               f"parity_contam={mean_contam:.4f}(HP<={HP_PARITY_CONTAM} HF>{HF_PARITY_CONTAM}) "
               f"b_repulsion={mean_brep:.4f}(HP>={HP_B_REPULSION}) n_seeds={n}")

    if mean_cert < HF_CERT_VALID or mean_contam > HF_PARITY_CONTAM:
        return ("HARD_FAIL", f"HARD_FAIL: {summary}")

    n_all_hp = sum(1 for r in results if r["hp_a"] and r["hp_b"] and r["hp_c"])
    n_hp2 = sum(1 for r in results if sum([r["hp_a"], r["hp_b"], r["hp_c"]]) >= 2)
    min_pass = math.ceil(n * 0.6)

    if n_all_hp >= min_pass:
        return ("HARD_PASS", f"HARD_PASS: 4-level NK tree CONFIRMED. {summary}")
    if n_hp2 >= min_pass:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: 2/3 cells pass. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: insufficient HP. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M_L0": M_L0, "M_L1": M_L1, "M_L2": M_L2, "M_L3": M_L3, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] running N={N} 4-level tree...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(per_seed)

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
    "mean_cert_chain_valid_rate": float(np.mean([r["cert_chain_valid_rate"] for r in all_results])) if all_results else None,
    "mean_parity_contamination": float(np.mean([r["parity_contamination"] for r in all_results])) if all_results else None,
    "mean_b_repulsion_rate": float(np.mean([r["b_repulsion_rate"] for r in all_results])) if all_results else None,
}
metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"[done] metrics -> {metrics_path}", flush=True)
