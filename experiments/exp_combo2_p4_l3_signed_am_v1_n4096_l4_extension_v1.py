"""
combo2_p4_l3_signed_am_v1_n4096_l4_extension_v1 -- COMBO-2 with L=4 extension at N=4096.

Extends COMBO-2 (p=4 DAM + L=3 hierarchy + signed-AM) from L=3 to L=4 hierarchical NKT.
Prior: COMBO-2 L=3 HARD_PASS at N=4096 and N=8192. This tests whether 4-layer deep
hierarchical NKT composition holds.

SCIENTIFIC QUESTION:
  At N=4096, does a 4-layer (L=4) p=4 DAM hierarchical composition with signed-AM
  still produce end-to-end fidelity >= 0.75 and B-repulsion rate >= 0.90?
  L=4 adds one more outer-context binding over L=3.

ARCHITECTURE:
  Layer 1 (innermost): M_inner=8 patterns, p=4 retrieval.
  Layer 2 (middle): M_mid=4 Hadamard-bound to inner pointers.
  Layer 3 (outer): M_outer=3 Hadamard-bound to mid pointers.
  Layer 4 (outermost): M_outermost=2 Hadamard-bound to outer pointers.
  End-to-end: noisy query at L4 -> L4 -> decode -> L3 -> decode -> L2 -> decode -> L1 compare.

PRE-REGISTERED HARD-PASS (L=4 extension):
  HP1: l4_fidelity_A >= 0.75 (relaxed from L=3 HP 0.85; L=4 adds one more retrieval step).
  HP2: b_repulsion_rate >= 0.90 (signed-AM unchanged; slight relaxation from L=3 0.95).
  HP3: parity_contamination <= 0.10 (slightly wider than L=3 0.05; L=4 cross-tree leakage larger).
  HARD-PASS: all 3 HP in >= 4/5 seeds.

PRE-REGISTERED HARD-FAIL:
  HF1: l4_fidelity_A < 0.40.
  HF2: b_repulsion_rate < 0.40.
  MIDDLE: 2/3 HP conditions met OR HP1 in [0.55, 0.75).

Calibration: prior L=3 HP confirmed; L=4 adds one binding step; expected fidelity loss ~0.05-0.10
per additional level. HP1=0.75 is conservative relative to predicted 0.80.
P_deflated = 0.60 (first L=4 test; calibration probe, wider bands).

FORMULA SELF-TESTS:
  1. p=4 update rule: h = (1/N) * Xi^T * (Xi @ x)^3.
     [INPUT: N=4, xi_0=[1,1,-1,1], Xi=[xi_0], x=xi_0]
     [EXPECTED: h = xi_0 * (xi_0.xi_0)^3 / N = xi_0 * 4^3 / 4 = 16 * xi_0]
  2. Hadamard binding decode: xi_b = (xi_a * xi_b) * xi_a.
     [INPUT: xi_a=[1,-1,1,-1], xi_b=[1,1,-1,-1]]
     [EXPECTED: decoded = xi_b]
  3. L=4 chain composition: 4 Hadamard bindings compose without overflow.
     [INPUT: N=64] [EXPECTED: final decoded cosine > 0.5]

PROT-018: anchor has _n4096; N MUST = 4096.
GPU REQUIRED: p=4 at N=4096 with 5-seed is compute-heavy for CPU (Tier A).
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

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import torch
    import torch.cuda
    import numpy as np
except ImportError:
    print("[FATAL] torch or numpy not installed.", flush=True)
    sys.exit(1)

if not torch.cuda.is_available():
    print("[FATAL] CUDA not available. This script requires a GPU.", flush=True)
    sys.exit(1)

DEVICE = torch.device('cuda')
print(f"[GPU] device={DEVICE} name={torch.cuda.get_device_name(0)} "
      f"total_mem={torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB", flush=True)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "combo2_p4_l3_signed_am_v1_n4096_l4_extension_v1"

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
    M_INNER = 4
    M_MID = 3
    M_OUTER = 2
    M_OUTERMOST = 2
    M_B = 2
    N_QUERIES = 5
    NOISE_FRAC = 0.10
    N_ACTIVE = 512
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_INNER = 8
    M_MID = 4
    M_OUTER = 3
    M_OUTERMOST = 2
    M_B = 4
    N_QUERIES = 10
    NOISE_FRAC = 0.10
    N_ACTIVE = N  # 4096

# Pre-registered thresholds
HP_L4_FIDELITY = 0.75
HP_B_REPULSION = 0.90
HP_PARITY_CONTAMINATION = 0.10
HF_L4_FIDELITY = 0.40
HF_B_REPULSION = 0.40

ALPHA_C = 0.138


def _selftest_p4_update():
    n = 4
    xi_0 = np.array([1.0, 1.0, -1.0, 1.0])
    Xi = xi_0.reshape(1, n)
    x = xi_0.copy()
    overlaps = Xi @ x
    h = (Xi.T @ (overlaps ** 3)) / n
    expected_h = xi_0 * (4.0 ** 3) / 4.0
    assert np.allclose(h, expected_h, atol=1e-8), f"p=4 update: got {h}, expected {expected_h}"


def _selftest_hadamard():
    xi_a = np.array([1.0, -1.0, 1.0, -1.0])
    xi_b = np.array([1.0, 1.0, -1.0, -1.0])
    bound = xi_a * xi_b
    decoded = bound * xi_a
    assert np.allclose(decoded, xi_b, atol=1e-8), f"Hadamard decode: {decoded} != {xi_b}"


def _selftest_l4_composition():
    """4 Hadamard bindings compose without fidelity collapse at tiny N."""
    n_t = 64
    rng = np.random.RandomState(42)
    xi_inner = rng.choice([-1.0, 1.0], size=n_t)
    ctx2 = rng.choice([-1.0, 1.0], size=n_t)
    xi_mid = xi_inner * ctx2
    ctx3 = rng.choice([-1.0, 1.0], size=n_t)
    xi_outer = xi_mid * ctx3
    ctx4 = rng.choice([-1.0, 1.0], size=n_t)
    xi_outermost = xi_outer * ctx4
    # Decode back: xi_outer_dec = xi_outermost * ctx4
    xi_outer_dec = xi_outermost * ctx4
    xi_mid_dec = xi_outer_dec * ctx3
    xi_inner_dec = xi_mid_dec * ctx2
    cos = float(np.dot(xi_inner_dec, xi_inner) / n_t)
    assert cos > 0.5, f"L=4 chain composition: cos={cos:.4f} < 0.5"


def _selftest_gpu_vram():
    n_elems = int(200 * 1e6 / 4)
    dummy = torch.zeros((n_elems,), device=DEVICE, dtype=torch.float32)
    mem_mb = torch.cuda.memory_allocated(0) / 1e6
    assert mem_mb > 100.0, f"GPU VRAM < 100 MB: {mem_mb:.1f} MB"
    del dummy
    torch.cuda.empty_cache()


def _instrumentation_selftest():
    _selftest_p4_update()
    _selftest_hadamard()
    _selftest_l4_composition()
    _selftest_gpu_vram()
    print("[selftest] PASS: p4_update, hadamard, l4_composition, gpu_vram all OK", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def p4_retrieve(Xi: np.ndarray, probe: np.ndarray, n_steps: int = 5, n: int = None) -> np.ndarray:
    """p=4 polynomial DAM retrieval: h = (1/N) * Xi^T * (Xi @ state)^3."""
    if n is None:
        n = probe.shape[0]
    state = probe.copy()
    for _ in range(n_steps):
        overlaps = Xi @ state
        h = (Xi.T @ (overlaps ** 3)) / n
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b)) / (na * nb)


def run_seed(seed: int, n_dim: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    # ---- L4 HIERARCHY (A-patterns) ----
    Xi_inner = rng.choice([-1.0, 1.0], size=(M_INNER, n_dim)).astype(np.float64)

    Xi_ctx2 = rng.choice([-1.0, 1.0], size=(M_MID, n_dim)).astype(np.float64)
    Xi_mid = Xi_ctx2 * Xi_inner[:M_MID]

    Xi_ctx3 = rng.choice([-1.0, 1.0], size=(M_OUTER, n_dim)).astype(np.float64)
    Xi_outer = Xi_ctx3 * Xi_mid[:M_OUTER]

    Xi_ctx4 = rng.choice([-1.0, 1.0], size=(M_OUTERMOST, n_dim)).astype(np.float64)
    Xi_outermost = Xi_ctx4 * Xi_outer[:M_OUTERMOST]

    # ---- SIGNED-AM (B-patterns) ----
    Xi_A_sub = rng.choice([-1.0, 1.0], size=(M_B, n_dim)).astype(np.float64)
    Xi_B = rng.choice([-1.0, 1.0], size=(M_B, n_dim)).astype(np.float64)

    def build_p4_W(Xi_pats: np.ndarray) -> np.ndarray:
        return Xi_pats.T @ Xi_pats / float(n_dim)

    W_A_sub = build_p4_W(Xi_A_sub)
    W_B_mat = build_p4_W(Xi_B)
    W_signed = W_A_sub - W_B_mat

    # ---- TEST 1: L4 END-TO-END FIDELITY ----
    l4_fidelities = []
    for q_idx in range(min(N_QUERIES, M_OUTERMOST)):
        xi_out_true = Xi_outermost[q_idx]
        probe = xi_out_true.copy()
        flip = rng.random(n_dim) < NOISE_FRAC
        probe[flip] *= -1.0

        # L4 retrieval
        xi_out_ret = p4_retrieve(Xi_outermost, probe, n=n_dim)
        # Decode to outer
        xi_outer_ptr = xi_out_ret * Xi_ctx4[q_idx]
        # L3 retrieval
        xi_outer_ret = p4_retrieve(Xi_outer, xi_outer_ptr, n=n_dim)
        # Decode to mid
        xi_mid_ptr = xi_outer_ret * Xi_ctx3[q_idx % M_OUTER]
        # L2 retrieval
        xi_mid_ret = p4_retrieve(Xi_mid, xi_mid_ptr, n=n_dim)
        # Decode to inner
        xi_inner_ptr = xi_mid_ret * Xi_ctx2[q_idx % M_MID]
        # L1 retrieval
        xi_inner_ret = p4_retrieve(Xi_inner, xi_inner_ptr, n=n_dim)
        xi_inner_true = Xi_inner[q_idx % M_INNER]
        fid = cosine_sim(xi_inner_ret, xi_inner_true)
        l4_fidelities.append(fid)

    l4_fid_mean = float(np.mean(l4_fidelities)) if l4_fidelities else 0.0

    # ---- TEST 2: B-PATTERN REPULSION ----
    repulsion_count = 0
    for b_idx in range(M_B):
        eta_b = Xi_B[b_idx]
        probe_b = eta_b.copy()
        flip_b = rng.random(n_dim) < NOISE_FRAC
        probe_b[flip_b] *= -1.0
        state = probe_b.copy()
        for _ in range(8):
            ov_A = Xi_A_sub @ state
            ov_B = Xi_B @ state
            h = (Xi_A_sub.T @ (ov_A ** 3) - Xi_B.T @ (ov_B ** 3)) / n_dim
            state = np.sign(h)
            state[state == 0] = 1.0
        # Repelled if cosine < 0
        if cosine_sim(state, eta_b) < 0.0:
            repulsion_count += 1
    b_repulsion = float(repulsion_count) / M_B if M_B > 0 else 0.0

    # ---- TEST 3: PARITY CONTAMINATION ----
    # Cross-tree: A-patterns should NOT activate in B-attractor basin
    contamination_count = 0
    for a_idx in range(min(N_QUERIES, M_B)):
        xi_a = Xi_A_sub[a_idx]
        probe_a = xi_a.copy()
        flip_a = rng.random(n_dim) < NOISE_FRAC
        probe_a[flip_a] *= -1.0
        state_a = probe_a.copy()
        for _ in range(8):
            ov_A = Xi_A_sub @ state_a
            ov_B = Xi_B @ state_a
            h = (Xi_A_sub.T @ (ov_A ** 3) - Xi_B.T @ (ov_B ** 3)) / n_dim
            state_a = np.sign(h)
            state_a[state_a == 0] = 1.0
        # Check contamination: does A-query end up in B-basin?
        cos_to_b = max(cosine_sim(state_a, Xi_B[j]) for j in range(M_B))
        if cos_to_b > 0.5:
            contamination_count += 1
    parity_contamination = float(contamination_count) / max(min(N_QUERIES, M_B), 1)

    elapsed = time.time() - t0
    print(f"  [seed={seed} N={n_dim}] l4_fid={l4_fid_mean:.4f} "
          f"b_rep={b_repulsion:.4f} parity_cont={parity_contamination:.4f} elapsed={elapsed:.2f}s",
          flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
        "l4_fidelity_A": float(l4_fid_mean),
        "b_repulsion_rate": float(b_repulsion),
        "parity_contamination": float(parity_contamination),
        "elapsed_s": float(elapsed),
        "hp1_pass": int(l4_fid_mean >= HP_L4_FIDELITY),
        "hp2_pass": int(b_repulsion >= HP_B_REPULSION),
        "hp3_pass": int(parity_contamination <= HP_PARITY_CONTAMINATION),
    }


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    def count_pass(key):
        return sum(1 for r in results if r.get(key, 0))

    n = len(results)
    hp1_c = count_pass("hp1_pass")
    hp2_c = count_pass("hp2_pass")
    hp3_c = count_pass("hp3_pass")

    def mean_key(k):
        vs = [r[k] for r in results if k in r]
        return float(sum(vs) / len(vs)) if vs else 0.0

    fid = mean_key("l4_fidelity_A")
    brep = mean_key("b_repulsion_rate")
    cont = mean_key("parity_contamination")

    summary = (f"l4_fid={fid:.4f}(HP>={HP_L4_FIDELITY} HF<{HF_L4_FIDELITY}) "
               f"b_rep={brep:.4f}(HP>={HP_B_REPULSION} HF<{HF_B_REPULSION}) "
               f"parity_cont={cont:.4f}(HP<={HP_PARITY_CONTAMINATION}) "
               f"hp1={hp1_c}/{n} hp2={hp2_c}/{n} hp3={hp3_c}/{n}")

    if fid < HF_L4_FIDELITY or brep < HF_B_REPULSION:
        return ("HARD_FAIL", f"HARD_FAIL: {summary}")

    GATE = max(4, n - 1) if n >= 4 else n
    if hp1_c >= GATE and hp2_c >= GATE and hp3_c >= GATE:
        return ("HARD_PASS", f"HARD_PASS: all 3 HP at L=4 N=4096. {summary}")
    if sum([hp1_c >= GATE, hp2_c >= GATE, hp3_c >= GATE]) >= 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: 2/3 HP. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} L=4", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
t0_total = time.time()
run_config = {"N": N, "L": 4, "M_INNER": M_INNER, "run_mode": RUN_MODE}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print(f"[run] seeds_todo={seeds_todo} out_dir={out_dir}", flush=True)

n_active = N_ACTIVE if RUN_MODE == "smoke" else N
for s in seeds_todo:
    res = run_seed(s, n_active)
    write_partial(out_dir, s, res)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

metrics = {
    "anchor": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "n_seeds": len(all_results),
    "N": N,
    "run_mode": RUN_MODE,
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
    "results": all_results,
}

metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)

print(f"\n[VERDICT] {verdict}", flush=True)
print(f"[VERDICT_MSG] {verdict_msg}", flush=True)
print(f"[METRICS_PATH] {metrics_path}", flush=True)
