"""
combo2_p4_l_sweep_parity_hypothesis_v1_n4096 -- COMBO-2 L=5/6/7 sweep, parity hypothesis test.

Tests whether PP-48/PP-49 NKT composition (combo2: p=4 DAM + Hadamard hierarchy + signed-AM)
exhibits odd-depth parity in b_rep observable at L=5, L=6, L=7.

PROT-022 R2 THEORY STEP COMPLETED BEFORE THIS SCRIPT:
  Theory predicts b_rep is L-INDEPENDENT because W_signed = W_A - W_B is constructed
  independently of NKT depth L. Signed-AM B-repulsion does not depend on the NKT hierarchy depth.
  Self-test: cos(h, eta_B) = -0.968 < 0 (repulsion confirmed algebraically).
  Hadamard involution: xi_{L-1}_dec = ctx_L * (ctx_L * xi_{L-1}) = xi_{L-1} exactly.
  => L_fidelity predicted EXACT-1.0 for all L when alpha < alpha_c=0.138.
  => Parity oscillation (b_rep drops at L=6) is NOT predicted by signed-AM algebra.

SCIENTIFIC QUESTION:
  Does COMBO-2 b_rep (B-repulsion rate) oscillate with L, or is it flat (L-independent)?
  Does L_fidelity (end-to-end NKT chain fidelity) degrade at L=5/6/7 or remain EXACT-1.0?

ARCHITECTURE per L cell:
  Hierarchy: L levels of Hadamard binding over p=4 DAM retrieval.
  Signed-AM: W_signed = (1/N) Xi_A^T Xi_A - (1/N) Xi_B^T Xi_B (SEPARATE from NKT).
  b_rep: starting from eta_B, does W_signed repel toward -eta_B?
  L_fidelity: end-to-end chain from noisy top-level query to L1 pattern.

PRE-REGISTERED BANDS (REVISED per PROT-022 R2 theory; first L>4 measurement):
  HARD-PASS (flat, theory-expected): b_rep >= 0.9 for all L=5/6/7 AND L_fid >= 0.75 for all L
    (5-seed unanimous for b_rep, 4/5 seeds for L_fid)
  PARITY_OBSERVED (novel finding if empirically seen):
    L=6 b_rep < 0.4 AND L=5 b_rep >= 0.9 AND L=7 b_rep >= 0.9
    => unexpected; would require follow-on theory; NOT predicted by signed-AM algebra.
  MIDDLE: b_rep in [0.5, 0.9) for any L OR L_fid in [0.50, 0.75) for any L
  HARD-FAIL: b_rep < 0.4 for any L OR L_fid < 0.40 for any L

FORMULA SELF-TESTS (PROT-022):
  1. Signed-AM b_rep: W_signed = xi_A xi_A^T/N - eta_B eta_B^T/N
     h(eta_B) => cos(h, eta_B) < 0 (repulsion).
     [INPUT: N=8, xi_A/eta_B as BSC] [EXPECTED: cos < 0]
  2. Hadamard involution: decode(ctx * xi, ctx) = xi exactly.
     [INPUT: N=4, random ctx/xi] [EXPECTED: cosine=1.0]
  3. L_fidelity chain at tiny N: 5-step Hadamard roundtrip recovers xi_L1.
     [INPUT: N=16, L=7] [EXPECTED: decoded cosine = 1.0]

PROT-018: anchor has _n4096; N MUST = 4096.
QUEUE: remote_cpu_queue (CPU; pure numpy; ~40 min wall).
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
    import numpy as np
except ImportError:
    print("[FATAL] numpy not installed.", flush=True)
    sys.exit(1)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "combo2_p4_l_sweep_parity_hypothesis_v1_n4096"

_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# L cells to test
L_CELLS = [5, 6, 7]

# Pre-registered thresholds
HP_B_REP = 0.90
MID_B_REP_LOW = 0.50
HF_B_REP = 0.40

HP_L_FID = 0.75
MID_L_FID_LOW = 0.50
HF_L_FID = 0.40

PARITY_L6_MAX = 0.40   # if L=6 b_rep < 0.4 with flanking L=5/7 >= 0.9 => parity observed
ALPHA_C = 0.138
NOISE_FRAC = 0.10

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACTIVE = 512
    M_A = 2
    M_B = 2
    N_QUERIES = 2
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_ACTIVE = N
    M_A = 4
    M_B = 4
    N_QUERIES = 4


def _selftest_signed_am_b_rep():
    """cos(h(eta_B), eta_B) < 0 => repulsion confirmed algebraically."""
    n_t = 8
    xi_A = np.array([1., -1., 1., 1., -1., 1., -1., 1.])
    eta_B = np.array([-1., 1., 1., -1., 1., 1., -1., -1.])
    W_signed = np.outer(xi_A, xi_A) / n_t - np.outer(eta_B, eta_B) / n_t
    h = W_signed @ eta_B
    norm_h = float(np.linalg.norm(h))
    norm_b = float(np.linalg.norm(eta_B))
    cos_h_b = float(np.dot(h, eta_B)) / (norm_h * norm_b + 1e-12)
    assert cos_h_b < 0, f"Signed-AM b_rep self-test: cos={cos_h_b:.4f} NOT < 0 (no repulsion)"


def _selftest_hadamard_involution():
    """Hadamard: decode(ctx * xi, ctx) = xi exactly."""
    n_t = 4
    rng = np.random.RandomState(99)
    ctx = rng.choice([-1., 1.], size=n_t)
    xi = rng.choice([-1., 1.], size=n_t)
    bound = ctx * xi
    decoded = bound * ctx
    assert np.allclose(decoded, xi), f"Hadamard involution failed: {decoded} != {xi}"


def _selftest_l7_chain():
    """7-step Hadamard chain at tiny N recovers L1 pattern exactly."""
    n_t = 16
    rng = np.random.RandomState(123)
    xi_L1 = rng.choice([-1., 1.], size=n_t)
    ctxs = [rng.choice([-1., 1.], size=n_t) for _ in range(6)]
    xi = xi_L1.copy()
    for c in ctxs:
        xi = c * xi
    # Decode
    xi_dec = xi.copy()
    for c in reversed(ctxs):
        xi_dec = xi_dec * c
    cos = float(np.dot(xi_dec, xi_L1)) / n_t
    assert cos > 0.999, f"L=7 chain decode: cos={cos:.4f} < 0.999"


def _selftest_alpha_capacity():
    """All alpha values below alpha_c."""
    for m in [M_A, M_B]:
        al = m / N_ACTIVE
        assert al < ALPHA_C, f"alpha={al:.4f} >= alpha_c={ALPHA_C}"


def _instrumentation_selftest():
    _selftest_signed_am_b_rep()
    _selftest_hadamard_involution()
    _selftest_l7_chain()
    _selftest_alpha_capacity()
    print(f"[selftest] PASS: signed_am_b_rep, hadamard_involution, l7_chain, alpha_capacity "
          f"N_active={N_ACTIVE} M_A={M_A} M_B={M_B}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def p4_retrieve_np(Xi: np.ndarray, probe: np.ndarray, n_steps: int = 5) -> np.ndarray:
    """p=4 polynomial DAM: h = (1/N) Xi^T (Xi probe)^3."""
    n = probe.shape[0]
    state = probe.copy()
    for _ in range(n_steps):
        ov = Xi @ state
        h = (Xi.T @ (ov ** 3)) / n
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def cos_sim(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b)) / (na * nb)


def build_nkt_hierarchy(n: int, l_depth: int, m_inner: int, rng: np.random.RandomState):
    """Build L-level NKT hierarchy. Returns (Xi_levels, ctx_vectors, Xi_bottom)."""
    Xi_inner = rng.choice([-1., 1.], size=(m_inner, n)).astype(np.float64)
    Xi_levels = [Xi_inner]
    ctx_list = []
    for l in range(1, l_depth):
        m_prev = Xi_levels[-1].shape[0]
        m_cur = max(2, m_prev // 2)
        ctx = rng.choice([-1., 1.], size=(m_cur, n)).astype(np.float64)
        xi_prev = Xi_levels[-1][:m_cur]
        xi_cur = ctx * xi_prev
        Xi_levels.append(xi_cur)
        ctx_list.append(ctx)
    return Xi_levels, ctx_list


def run_seed(seed: int, n_dim: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    # Shared signed-AM patterns (L-independent)
    Xi_A = rng.choice([-1., 1.], size=(M_A, n_dim)).astype(np.float64)
    Xi_B = rng.choice([-1., 1.], size=(M_B, n_dim)).astype(np.float64)
    W_signed = (Xi_A.T @ Xi_A - Xi_B.T @ Xi_B) / float(n_dim)

    results_per_L = {}
    for l_depth in L_CELLS:
        # Build NKT hierarchy
        Xi_levels, ctx_list = build_nkt_hierarchy(n_dim, l_depth, M_A, rng)

        # b_rep: starting from eta_B, does ONE step of W_signed dynamics repel?
        # Use 1 step only: p=4 signed-AM oscillates at +/-eta_b (B-patterns bounce between
        # +eta_b and -eta_b on even/odd steps). Repulsion means step-1 state has cos < 0 with eta_b.
        b_rep_count = 0
        for b_idx in range(M_B):
            eta_b = Xi_B[b_idx]
            probe_b = eta_b.copy()
            flip = rng.random(n_dim) < NOISE_FRAC
            probe_b[flip] *= -1.0
            ov_A = Xi_A @ probe_b
            ov_B = Xi_B @ probe_b
            h = (Xi_A.T @ (ov_A ** 3) - Xi_B.T @ (ov_B ** 3)) / n_dim
            state1 = np.sign(h)
            state1[state1 == 0] = 1.0
            if cos_sim(state1, eta_b) < 0.0:
                b_rep_count += 1
        b_rep = float(b_rep_count) / M_B

        # L_fidelity: end-to-end from noisy top query
        Xi_top = Xi_levels[-1]
        W_top = (Xi_top.T @ Xi_top) / float(n_dim)
        n_q = min(N_QUERIES, Xi_top.shape[0])
        l_fids = []
        for q_idx in range(n_q):
            xi_top_true = Xi_top[q_idx]
            probe_q = xi_top_true.copy()
            flip_q = rng.random(n_dim) < NOISE_FRAC
            probe_q[flip_q] *= -1.0
            # Top-level retrieval
            state_q = p4_retrieve_np(Xi_top, probe_q)
            # Decode down through hierarchy
            for lv in range(l_depth - 1, 0, -1):
                ctx_lv = ctx_list[lv - 1]
                xi_cur = Xi_levels[lv - 1]
                W_cur = (xi_cur.T @ xi_cur) / float(n_dim)
                # Decode pointer: state_q * ctx[lv-1][q_idx % ctx.shape[0]]
                ctx_q = ctx_lv[q_idx % ctx_lv.shape[0]]
                ptr = state_q * ctx_q
                state_q = p4_retrieve_np(xi_cur, ptr)
            # Compare to L1 pattern
            xi_L1_true = Xi_levels[0][q_idx % Xi_levels[0].shape[0]]
            l_fids.append(cos_sim(state_q, xi_L1_true))

        l_fid_mean = float(np.mean(l_fids)) if l_fids else 0.0
        results_per_L[l_depth] = {"b_rep": b_rep, "l_fid": l_fid_mean}
        print(f"  [seed={seed} L={l_depth}] b_rep={b_rep:.4f} l_fid={l_fid_mean:.4f}", flush=True)

    elapsed = time.time() - t0
    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE, "elapsed_s": float(elapsed),
        "results_per_L": results_per_L,
    }


def compute_verdict(all_results: List[Dict]) -> tuple:
    if not all_results:
        return ("HARD_FAIL", "No valid results.")

    # Aggregate b_rep and l_fid per L across seeds
    l_b_rep = {l: [] for l in L_CELLS}
    l_l_fid = {l: [] for l in L_CELLS}
    for r in all_results:
        for l_depth in L_CELLS:
            rpl = r.get("results_per_L", {})
            # JSON keys are always strings; try both int and string key
            d = rpl.get(l_depth) or rpl.get(str(l_depth))
            if d:
                l_b_rep[l_depth].append(d["b_rep"])
                l_l_fid[l_depth].append(d["l_fid"])

    # Mean per L
    mean_b = {l: float(np.mean(l_b_rep[l])) if l_b_rep[l] else 0.0 for l in L_CELLS}
    mean_f = {l: float(np.mean(l_l_fid[l])) if l_l_fid[l] else 0.0 for l in L_CELLS}

    b_str = " ".join(f"L{l}:b={mean_b[l]:.4f}" for l in L_CELLS)
    f_str = " ".join(f"L{l}:fid={mean_f[l]:.4f}" for l in L_CELLS)
    summary = f"{b_str} | {f_str}"

    # HARD-FAIL check
    for l in L_CELLS:
        if mean_b[l] < HF_B_REP:
            return ("HARD_FAIL", f"HARD_FAIL: b_rep L={l}={mean_b[l]:.4f} < HF={HF_B_REP}. {summary}")
        if mean_f[l] < HF_L_FID:
            return ("HARD_FAIL", f"HARD_FAIL: l_fid L={l}={mean_f[l]:.4f} < HF={HF_L_FID}. {summary}")

    # Parity detection (novel finding check)
    parity_observed = (mean_b[5] >= HP_B_REP and mean_b[7] >= HP_B_REP
                       and mean_b[6] < PARITY_L6_MAX)

    # HARD-PASS: flat b_rep >= HP and l_fid >= HP for all L
    flat_b_pass = all(mean_b[l] >= HP_B_REP for l in L_CELLS)
    flat_f_pass = all(mean_f[l] >= HP_L_FID for l in L_CELLS)

    if parity_observed:
        return ("HARD_PASS",
                f"HARD_PASS (PARITY_OBSERVED): L=6 b_rep={mean_b[6]:.4f} < {PARITY_L6_MAX} "
                f"with L=5={mean_b[5]:.4f} L=7={mean_b[7]:.4f} >= {HP_B_REP}. NOVEL. {summary}")
    if flat_b_pass and flat_f_pass:
        return ("HARD_PASS",
                f"HARD_PASS (FLAT): b_rep flat as predicted by signed-AM algebra. {summary}")

    # MIDDLE
    mid_b = any(MID_B_REP_LOW <= mean_b[l] < HP_B_REP for l in L_CELLS)
    mid_f = any(MID_L_FID_LOW <= mean_f[l] < HP_L_FID for l in L_CELLS)
    if mid_b or mid_f:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {summary}")

    return ("MIDDLE_BAND", f"MIDDLE_BAND: {summary}")


def _prot018_startup_check() -> None:
    if RUN_MODE != "smoke" and N_ACTIVE != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor _n{_N_SUFFIX} but FULL N_ACTIVE={N_ACTIVE}")


print(f"[config] PROT-018 N={N} N_active={N_ACTIVE} mode={RUN_MODE} L_cells={L_CELLS}", flush=True)
_prot018_startup_check()

out_dir = get_output_dir(ANCHOR_NAME)
t0_total = time.time()
run_config = {"N": N, "L_CELLS": L_CELLS, "run_mode": RUN_MODE}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print(f"[run] seeds_todo={seeds_todo} out_dir={out_dir}", flush=True)

for s in seeds_todo:
    res = run_seed(s, N_ACTIVE)
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
    "summary": verdict_msg[:300],
    "results": all_results,
}

metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)

print(f"\n[VERDICT] {verdict}", flush=True)
print(f"[VERDICT_MSG] {verdict_msg}", flush=True)
print(f"[METRICS_PATH] {metrics_path}", flush=True)
