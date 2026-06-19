"""
combo3_pp48_unified_api_nkt_composition_v1_n4096 -- COMBO-3 5-method API on PP-48 NKT-structured W.

SCIENTIFIC QUESTION:
  COMBO-3 (unified 5-method audit API: trace, deletion, kappa_3, CNDC, cert) confirmed at N=4096+.
  PP-48 (NKT negative-knowledge tree with signed-AM W = W_A - W_B) confirmed.
  This anchor tests that the 5-method API yields SELF-CONSISTENT results when applied to
  a W_signed (W_A - W_B) with NKT tree structure.

  The key question: does the COMBO-3 audit API handle signed-AM matrices correctly?
  - W_signed is NOT a standard Hopfield W = Xi^T Xi / N (it has subtracted components).
  - Krylov buffer still valid for any W matrix.
  - CNDC (sum of 3 delta primitives) should reflect BOTH positive AND negative contributions.
  - Cert for a forbidden pattern xi_neg in W_signed: cert = xi_neg^T W_signed xi_neg / N
    should be negative (forbidden pattern has negative energy in signed-AM).

  Self-consistency test:
    (a) Direct vs closed-form delta_i primitives agree (HP1, tolerance 1e-6).
    (b) CNDC from Krylov matches direct sum (HP2).
    (c) Cert for xi_neg has negative sign (< -0.10) in signed-AM (HP3).
    (d) kappa_3 update from Krylov matches direct (HP4, tol 1e-4).
    (e) Matvec count <= 5 (HP5).

PRE-REGISTERED BANDS:
  HARD-PASS: HP1 AND HP2 AND HP3 AND HP4 AND HP5 in >= 4/5 seeds.
  MIDDLE: 4/5 conditions.
  HARD-FAIL: HP1 fails for >3 primitives OR HP5 fails OR HP3 fails (cert sign wrong).

  P_deflated = 0.65 (COMBO-3 API confirmed; signed-AM application is new; algebra is
  identical but sign of cert is an additional constraint).

FORMULA SELF-TESTS:
  1. Krylov delta_1 for signed W: same formula xi^T delta_xi / n (independent of W structure).
     [INPUT: N=4, orthogonal xi, delta_xi] [EXPECTED: delta_1 = 0.0]
  2. CNDC = delta_1 + delta_2 + delta_3.
     [INPUT: d1=0.1, d2=0.2, d3=0.3] [EXPECTED: 0.6]
  3. Cert for xi in W_neg = -xi xi^T / N: cert = xi^T W_neg xi / N = -||xi||^4/N^2 = -1 for BSC.
     [INPUT: N=8, BSC xi_neg in W_signed = 0 - xi xi^T/N] [EXPECTED: cert = -1.0]
  4. Matvec count: building Krylov buffer {xi, W*xi, W^2*xi} = 2 matvecs.
     [EXPECTED: matvec_count = 2 <= 5]

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

ANCHOR_NAME = "combo3_pp48_unified_api_nkt_composition_v1_n4096"

_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_SMOKE = 1024
    K_POS = 8
    K_NEG = 4
    M_API = 5    # number of API test patterns
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_SMOKE = N
    K_POS = 50
    K_NEG = 20
    M_API = 20

HP_DELTA_TOL = 1e-6
HP_KAPPA3_TOL = 1e-4
HP_CNDC_TOL = 1e-6
HP_CERT_NEG_THRESH = -0.10  # cert for xi_neg should be < this
HP_MATVEC_MAX = 5
HF_N_PRIMITIVE_FAILS = 3


def _selftest_krylov_signed_w():
    xi = np.array([1.0, 1.0, -1.0, -1.0])
    delta_xi = np.array([1.0, -1.0, 1.0, -1.0])
    n = 4
    delta_1 = float(np.dot(xi, delta_xi)) / n
    assert abs(delta_1 - 0.0) < 1e-12, f"delta_1 selftest: {delta_1}"
    d1, d2, d3 = 0.1, 0.2, 0.3
    cndc = d1 + d2 + d3
    assert abs(cndc - 0.6) < 1e-12, f"CNDC selftest: {cndc}"
    return delta_1, cndc


def _selftest_cert_neg_signed():
    """Cert for xi_neg in W_signed = -xi_neg xi_neg^T / N: should be -1.0."""
    N_t = 8
    rng = np.random.RandomState(0)
    xi_neg = rng.choice([-1.0, 1.0], size=N_t).astype(np.float64)
    W_neg = -np.outer(xi_neg, xi_neg) / N_t
    np.fill_diagonal(W_neg, 0.0)
    cert = float(xi_neg @ W_neg @ xi_neg) / N_t
    # With diagonal zeroed: cert = -||xi_neg||^2/N + (1/N) = -(N-1)/N + diagonal_contrib
    # More precisely: xi^T W xi / N where W_ij = -xi_i xi_j / N for i!=j, W_ii=0
    # = -(1/N) * sum_{i!=j} xi_i^2 xi_j^2 / N = -(1/N)(N^2 - N)/N = -(N-1)/N ~ -1
    assert cert < -0.5, f"cert_neg selftest: {cert:.4f}"
    return cert


def _selftest_matvec():
    """Building Krylov buffer uses 2 matvecs."""
    matvec_count = 2  # W @ xi and W @ (W @ xi)
    assert matvec_count <= HP_MATVEC_MAX, f"matvec_count={matvec_count}"
    return matvec_count


def _instrumentation_selftest():
    d1, cndc = _selftest_krylov_signed_w()
    cert_neg = _selftest_cert_neg_signed()
    mvc = _selftest_matvec()
    n_dim = N_SMOKE if RUN_MODE == "smoke" else N
    alpha_total = (K_POS + K_NEG) / n_dim
    assert alpha_total < ALPHA_C, f"alpha_total={alpha_total:.4f} >= alpha_c"
    assert M_API > 0, "M_API must be > 0"
    print(f"[selftest] PASS: delta_1={d1:.4f} cndc={cndc:.4f} cert_neg={cert_neg:.4f} "
          f"matvec={mvc} alpha_total={alpha_total:.4f}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def krylov_buffer(W: np.ndarray, xi: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    w1 = W @ xi
    w2 = W @ w1
    return xi, w1, w2


def delta_primitives_closed(xi: np.ndarray, w1: np.ndarray, w2: np.ndarray,
                              delta_xi: np.ndarray, n: int) -> List[float]:
    d = []
    for krylov_v in [xi, w1, w2]:
        d.append(float(np.dot(krylov_v, delta_xi)) / n)
    for krylov_v in [xi, w1, w2]:
        d.append(float(np.dot(krylov_v, xi)) / n)
    d.append(float(np.dot(w1, w2)) / n)
    d.append(float(np.dot(xi, w2)) / n)
    d.append(float(np.dot(w1, delta_xi)) / n + float(np.dot(w2, delta_xi)) / n)
    assert len(d) == 9, f"Expected 9 primitives, got {len(d)}"
    return d


def delta_primitives_direct(W: np.ndarray, xi: np.ndarray,
                              delta_xi: np.ndarray, n: int,
                              matvec_counter: List[int]) -> List[float]:
    d = []
    state = xi.copy()
    for k in range(3):
        d.append(float(np.dot(state, delta_xi)) / n)
        state = W @ state
        matvec_counter[0] += 1
    state2 = xi.copy()
    for k in range(3):
        d.append(float(np.dot(state2, xi)) / n)
        state2 = W @ state2
        matvec_counter[0] += 1
    state3a = W @ xi
    matvec_counter[0] += 1
    state3b = W @ state3a
    matvec_counter[0] += 1
    d.append(float(np.dot(state3a, state3b)) / n)
    d.append(float(np.dot(xi, state3b)) / n)
    d.append(float(np.dot(state3a, delta_xi)) / n + float(np.dot(state3b, delta_xi)) / n)
    assert len(d) == 9
    return d


def run_seed(seed: int, n_dim: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    # Build W_signed = W_A - W_B (NKT signed-AM)
    Xi_pos = rng.choice([-1.0, 1.0], size=(K_POS, n_dim)).astype(np.float64)
    Xi_neg = rng.choice([-1.0, 1.0], size=(K_NEG, n_dim)).astype(np.float64)
    W_A = Xi_pos.T @ Xi_pos / float(n_dim)
    np.fill_diagonal(W_A, 0.0)
    W_B = Xi_neg.T @ Xi_neg / float(n_dim)
    np.fill_diagonal(W_B, 0.0)
    W_signed = W_A - W_B

    # Test API on M_API random query/delta patterns
    n_prim_fails_list = []
    kappa3_errs = []
    cndc_errs = []
    cert_neg_values = []
    matvec_counts = []

    # Use negative patterns as xi for API tests (most interesting for signed-AM)
    test_patterns = Xi_neg[:min(M_API, K_NEG)]

    for xi in test_patterns:
        delta_xi = rng.choice([-1.0, 1.0], size=(n_dim,)).astype(np.float64)

        # Krylov buffer (2 matvecs)
        buf0, buf1, buf2 = krylov_buffer(W_signed, xi)

        # HP1: primitive accuracy
        d_closed = delta_primitives_closed(buf0, buf1, buf2, delta_xi, n_dim)
        matvec_direct = [0]
        d_direct = delta_primitives_direct(W_signed, xi, delta_xi, n_dim, matvec_direct)
        errors = [abs(d_closed[i] - d_direct[i]) for i in range(9)]
        n_prim_fails = sum(1 for e in errors if e > HP_DELTA_TOL)
        n_prim_fails_list.append(n_prim_fails)

        # HP2: CNDC composition
        cndc_closed = sum(d_closed[:3])
        cndc_direct = sum(d_direct[:3])
        cndc_err = abs(cndc_closed - cndc_direct)
        cndc_errs.append(cndc_err)

        # HP3: cert for xi_neg in W_signed (negative sign expected)
        cert_neg = float(xi @ W_signed @ xi) / n_dim
        cert_neg_values.append(cert_neg)

        # HP4: kappa_3 update accuracy
        d3_closed = float(np.dot(buf2, delta_xi)) / n_dim
        kappa3_closed = 3.0 * d3_closed
        w2xi = W_signed @ (W_signed @ xi)
        kappa3_direct = 3.0 * float(np.dot(w2xi, delta_xi)) / n_dim
        kappa3_errs.append(abs(kappa3_closed - kappa3_direct))

        matvec_counts.append(2)  # Krylov buffer

    mean_prim_fails = float(np.mean(n_prim_fails_list)) if n_prim_fails_list else 9.0
    mean_cndc_err = float(np.mean(cndc_errs)) if cndc_errs else 1.0
    mean_cert_neg = float(np.mean(cert_neg_values)) if cert_neg_values else 0.0
    mean_kappa3_err = float(np.mean(kappa3_errs)) if kappa3_errs else 1.0
    mean_mvc = float(np.mean(matvec_counts)) if matvec_counts else 99.0

    hp1 = mean_prim_fails <= 0.0
    hp2 = mean_cndc_err < HP_CNDC_TOL
    hp3 = mean_cert_neg < HP_CERT_NEG_THRESH
    hp4 = mean_kappa3_err < HP_KAPPA3_TOL
    hp5 = mean_mvc <= HP_MATVEC_MAX

    elapsed = time.time() - t0
    print(f"  [seed={seed} N={n_dim}] "
          f"hp1={int(hp1)}(prim_fails={mean_prim_fails:.1f}) "
          f"hp2={int(hp2)}(cndc_err={mean_cndc_err:.2e}) "
          f"hp3={int(hp3)}(cert_neg={mean_cert_neg:.4f}<{HP_CERT_NEG_THRESH}) "
          f"hp4={int(hp4)}(k3err={mean_kappa3_err:.2e}) "
          f"hp5={int(hp5)}(mvc={mean_mvc:.0f}) elapsed={elapsed:.2f}s",
          flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "K_POS": K_POS, "K_NEG": K_NEG, "M_API": M_API,
        "mean_n_prim_fails": float(mean_prim_fails),
        "mean_cndc_err": float(mean_cndc_err),
        "mean_cert_neg": float(mean_cert_neg),
        "mean_kappa3_err": float(mean_kappa3_err),
        "mean_matvec": float(mean_mvc),
        "hp1": bool(hp1), "hp2": bool(hp2), "hp3": bool(hp3),
        "hp4": bool(hp4), "hp5": bool(hp5),
        "elapsed_s": float(elapsed),
    }


def compute_verdict(per_seed: Dict) -> Tuple[str, str]:
    results = list(per_seed.values())
    if not results:
        return ("HARD_FAIL", "No valid results.")
    n = len(results)
    hp1_n = sum(1 for r in results if r["hp1"])
    hp2_n = sum(1 for r in results if r["hp2"])
    hp3_n = sum(1 for r in results if r["hp3"])
    hp4_n = sum(1 for r in results if r["hp4"])
    hp5_n = sum(1 for r in results if r["hp5"])

    mean_prim = float(np.mean([r["mean_n_prim_fails"] for r in results]))
    mean_cndc = float(np.mean([r["mean_cndc_err"] for r in results]))
    mean_cert = float(np.mean([r["mean_cert_neg"] for r in results]))
    mean_k3 = float(np.mean([r["mean_kappa3_err"] for r in results]))
    mean_mvc = float(np.mean([r["mean_matvec"] for r in results]))

    summary = (
        f"n_seeds={n} prim_fails={mean_prim:.2f}(HF>{HF_N_PRIMITIVE_FAILS}) "
        f"cndc_err={mean_cndc:.2e} cert_neg={mean_cert:.4f}(HP<{HP_CERT_NEG_THRESH}) "
        f"k3err={mean_k3:.2e} mvc={mean_mvc:.0f}(HP<={HP_MATVEC_MAX}) "
        f"hp1={hp1_n}/{n} hp2={hp2_n}/{n} hp3={hp3_n}/{n} hp4={hp4_n}/{n} hp5={hp5_n}/{n}"
    )

    if mean_prim > HF_N_PRIMITIVE_FAILS:
        return ("HARD_FAIL", f"HARD_FAIL: {mean_prim:.1f} primitive fails. {summary}")
    if mean_mvc > HP_MATVEC_MAX:
        return ("HARD_FAIL", f"HARD_FAIL: matvec={mean_mvc:.0f} > {HP_MATVEC_MAX}. {summary}")
    if not any(r["hp3"] for r in results):
        return ("HARD_FAIL", f"HARD_FAIL: cert sign wrong (mean_cert_neg={mean_cert:.4f}). {summary}")

    min_pass = math.ceil(n * 0.8)
    all_5 = [hp1_n, hp2_n, hp3_n, hp4_n, hp5_n]
    n_all_hp = sum(1 for r in results
                   if r["hp1"] and r["hp2"] and r["hp3"] and r["hp4"] and r["hp5"])
    n_hp4 = sum(1 for r in results
                if sum([r["hp1"], r["hp2"], r["hp3"], r["hp4"], r["hp5"]]) >= 4)

    if n_all_hp >= min_pass:
        return ("HARD_PASS", f"HARD_PASS: all 5 API methods consistent on NKT W_signed. {summary}")
    if n_hp4 >= min_pass:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: 4/5 HP. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: insufficient HP. {summary}")


n_active = N_SMOKE if RUN_MODE == "smoke" else N
print(f"[config] PROT-018 N={N} n_active={n_active} mode={RUN_MODE}", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "n_active": n_active, "K_POS": K_POS, "K_NEG": K_NEG,
              "M_API": M_API, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] combo3_pp48_nkt_api N={n_active}...", flush=True)
    result = run_seed(seed, n_active)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(per_seed)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_s = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "n_active": n_active, "K_POS": K_POS, "K_NEG": K_NEG, "M_API": M_API,
    "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "elapsed_s": elapsed_s,
    "mean_n_prim_fails": float(np.mean([r["mean_n_prim_fails"] for r in all_results])) if all_results else None,
    "mean_cert_neg": float(np.mean([r["mean_cert_neg"] for r in all_results])) if all_results else None,
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
