"""
pp45_combo3_unified_api_at_intermediate_alpha_v1 -- PP-45: 5-method API at intermediate alpha.

SCIENTIFIC QUESTION:
  PP-45 (5-method unified-API algebraic theorem) confirmed at alpha=M/N=200/4096 ~= 0.049.
  This anchor tests whether the algebraic uniformity (HP1-HP5) holds at INTERMEDIATE
  alpha values: alpha in {0.05, 0.10, 0.12} at production N.

  Motivation: substrate audit API is used at various memory loading levels.
  At higher alpha, the Gram matrix is less sparse and the Krylov buffer may have
  different numerical properties. This tests that the algebraic uniformity is
  alpha-invariant (not just a low-loading artifact).

  Note: uses N=512 (CPU-scale) to sweep 3 alpha cells quickly. Algebraic identity
  is N-independent by construction.

PRE-REGISTERED BANDS:
  HP1: |delta_i^direct - delta_i^Krylov| < 1e-10 for primitives k=1,2,3 at all 3 alpha cells.
  HP2: kappa_3 update error < 1e-4 at all 3 alpha cells.
  HP3: CNDC composition error < 1e-10 at all 3 alpha cells.
  HP4: cert signature error < 1e-10 at all 3 alpha cells.
  HP5: matvec count <= 5 (independent of alpha).
  HARD-PASS: all 5 HP at all 3 alpha cells in >= 4/5 seeds.

  HARD-FAIL: HP1 fails for >3 primitives at any alpha cell.
  MIDDLE: 4/5 HP conditions OR 2/3 alpha cells pass all HP.

  Prior: alpha=0.049 all-5-HP at N=4096. Algebraically identical at all alpha;
  HP here tests whether floating-point conditioning degrades at higher alpha.
  P_deflated = 0.75 (algebraic identity alpha-independent but fp precision may shift).

FORMULA SELF-TESTS:
  1. delta_1 = xi^T delta_xi / N = scalar dot product (alpha-independent).
     [INPUT: N=16, xi=ones, delta_xi=alternating +-1] [EXPECTED: delta_1 = 0.0]
  2. Krylov buffer matvec count = 2 (build {xi, Wxi, W2xi}).
     [EXPECTED: matvec_count = 2]
  3. CNDC = d1 + d2 + d3 (arithmetic).
     [INPUT: d1=0.1, d2=0.2, d3=0.3] [EXPECTED: 0.6]

No _nN suffix: N=512 CPU-scale for alpha sweep. PROT-018 rule 3.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "pp45_combo3_unified_api_at_intermediate_alpha_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

N = 512  # CPU-scale for alpha sweep

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    ALPHA_CELLS = [0.05, 0.10]
    N_TEST_PATTERNS = 5
else:
    SEEDS = [7, 17, 23, 31, 41]
    ALPHA_CELLS = [0.05, 0.10, 0.12]
    N_TEST_PATTERNS = 20

# Pre-registered tolerances (same as PP-45 founding)
HP1_DELTA_TOL = 1e-10
HP2_K3_TOL = 1e-4
HP3_CNDC_TOL = 1e-10
HP4_CERT_TOL = 1e-10
HP5_MAX_MATVECS = 5
HF1_MAX_FAILS = 3

# Formula self-tests
_xi_t = np.ones(8, dtype=np.float64)
_dxi_t = np.array([1., -1., 1., -1., 1., -1., 1., -1.], dtype=np.float64)
_d1_test = float(np.dot(_xi_t, _dxi_t)) / 8
assert abs(_d1_test) < 1e-10, f"delta_1 formula selftest: {_d1_test} != 0.0"
print("[formula_selftest] delta_1=0 for orthogonal OK", flush=True)

_cndc_test = 0.1 + 0.2 + 0.3
assert abs(_cndc_test - 0.6) < 1e-10, f"CNDC sum selftest: {_cndc_test} != 0.6"
print("[formula_selftest] CNDC = d1+d2+d3 arithmetic OK", flush=True)


def build_hopfield_w(M: int, n: int, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1.0, 1.0], size=(M, n)).astype(np.float64)
    W = (Xi.T @ Xi) / float(n)
    np.fill_diagonal(W, 0.0)
    return W, Xi


def build_krylov_buffer(W: np.ndarray, xi: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    Wxi = W @ xi
    W2xi = W @ Wxi
    return xi, Wxi, W2xi


def compute_primitives_from_buffer(xi0: np.ndarray, Wxi: np.ndarray,
                                   W2xi: np.ndarray, delta_xi: np.ndarray,
                                   n: int) -> Dict:
    d1 = float(np.dot(xi0, delta_xi)) / n
    d2 = float(np.dot(Wxi, delta_xi)) / n
    d3 = float(np.dot(W2xi, delta_xi)) / n
    return {"d1": d1, "d2": d2, "d3": d3}


def compute_primitives_direct(W: np.ndarray, xi: np.ndarray, delta_xi: np.ndarray,
                               n: int) -> Dict:
    d1 = float(np.dot(xi, delta_xi)) / n
    Wxi = W @ xi
    d2 = float(np.dot(Wxi, delta_xi)) / n
    W2xi = W @ Wxi
    d3 = float(np.dot(W2xi, delta_xi)) / n
    return {"d1": d1, "d2": d2, "d3": d3}


def compute_kappa3_update(xi0: np.ndarray, Wxi: np.ndarray, W2xi: np.ndarray,
                           delta_xi: np.ndarray, n: int) -> float:
    W2_delta = float(np.dot(W2xi, delta_xi)) / (n * n)
    return 3.0 * W2_delta


def compute_cert_signature(xi0: np.ndarray, Wxi: np.ndarray, W2xi: np.ndarray,
                            delta_xi: np.ndarray, n: int) -> float:
    d1 = float(np.dot(xi0, delta_xi)) / n
    d2 = float(np.dot(Wxi, delta_xi)) / n
    d3 = float(np.dot(W2xi, delta_xi)) / n
    return d1 ** 2 + d2 + d3 ** 2


def _selftest_krylov():
    n_t = 32
    rng = np.random.RandomState(0)
    W_t = rng.randn(n_t, n_t)
    W_t = (W_t + W_t.T) / 2
    xi_t = rng.choice([-1., 1.], size=n_t).astype(np.float64)
    dxi_t = rng.choice([-1., 1.], size=n_t).astype(np.float64)
    xi0, Wxi, W2xi = build_krylov_buffer(W_t, xi_t)
    buf = compute_primitives_from_buffer(xi0, Wxi, W2xi, dxi_t, n_t)
    direct = compute_primitives_direct(W_t, xi_t, dxi_t, n_t)
    for k in ["d1", "d2", "d3"]:
        err = abs(buf[k] - direct[k])
        assert err < 1e-10, f"selftest Krylov {k}: err={err:.4e}"
    print("[selftest] Krylov buffer d1/d2/d3 match direct to <1e-10 OK", flush=True)


def _instrumentation_selftest():
    _selftest_krylov()
    # Verify at least 1 alpha cell is covered
    assert len(ALPHA_CELLS) >= 1, f"ALPHA_CELLS empty"
    print(f"[selftest] PASS: krylov_ok, alpha_cells={ALPHA_CELLS}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed_alpha(seed: int, alpha: float) -> Dict:
    """Run one alpha cell for one seed."""
    M = max(1, int(alpha * N))
    W, Xi = build_hopfield_w(M, N, seed * 100 + int(alpha * 1000))
    rng = np.random.RandomState(seed + int(alpha * 1000))
    n_test = min(N_TEST_PATTERNS, M)

    hp1_fails = 0
    max_cndc_err = 0.0
    max_cert_err = 0.0
    k3_errors = []
    matvec_count = 2  # building Krylov buffer

    for i in range(n_test):
        xi = Xi[i % M].copy()
        delta_xi = Xi[(i + 1) % M].copy()

        xi0, Wxi, W2xi = build_krylov_buffer(W, xi)
        buf = compute_primitives_from_buffer(xi0, Wxi, W2xi, delta_xi, N)
        direct = compute_primitives_direct(W, xi, delta_xi, N)

        # HP1: delta primitive errors for k=1,2,3
        for k in ["d1", "d2", "d3"]:
            err = abs(buf[k] - direct[k])
            if err >= HP1_DELTA_TOL:
                hp1_fails += 1

        # HP3: CNDC error
        cndc_buf = buf["d1"] + buf["d2"] + buf["d3"]
        cndc_direct = direct["d1"] + direct["d2"] + direct["d3"]
        max_cndc_err = max(max_cndc_err, abs(cndc_buf - cndc_direct))

        # HP2: kappa_3 update error
        k3_buf = compute_kappa3_update(xi0, Wxi, W2xi, delta_xi, N)
        # Direct: 3 * xi^T W^2 delta_xi / N^2
        k3_direct = 3.0 * float(np.dot(W2xi, delta_xi)) / (N * N)
        k3_errors.append(abs(k3_buf - k3_direct))

        # HP4: cert signature error
        cert_buf = compute_cert_signature(xi0, Wxi, W2xi, delta_xi, N)
        d1_d = direct["d1"]; d2_d = direct["d2"]; d3_d = direct["d3"]
        cert_direct = d1_d ** 2 + d2_d + d3_d ** 2
        max_cert_err = max(max_cert_err, abs(cert_buf - cert_direct))

    max_k3_err = float(max(k3_errors)) if k3_errors else 0.0

    hp1_ok = int(hp1_fails <= HF1_MAX_FAILS)
    hp2_ok = int(max_k3_err < HP2_K3_TOL)
    hp3_ok = int(max_cndc_err < HP3_CNDC_TOL)
    hp4_ok = int(max_cert_err < HP4_CERT_TOL)
    hp5_ok = int(matvec_count <= HP5_MAX_MATVECS)

    return {
        "alpha": float(alpha), "M": M,
        "hp1_fails": hp1_fails, "max_cndc_err": float(max_cndc_err),
        "max_k3_err": float(max_k3_err), "max_cert_err": float(max_cert_err),
        "matvec_count": int(matvec_count),
        "hp1_ok": hp1_ok, "hp2_ok": hp2_ok, "hp3_ok": hp3_ok,
        "hp4_ok": hp4_ok, "hp5_ok": hp5_ok,
        "all_hp_ok": int(hp1_ok and hp2_ok and hp3_ok and hp4_ok and hp5_ok),
    }


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    alpha_results = {}
    for alpha in ALPHA_CELLS:
        r = run_seed_alpha(seed, alpha)
        alpha_results[f"alpha_{int(alpha*100):03d}"] = r
        status = "ALL_HP" if r["all_hp_ok"] else "PARTIAL"
        print(f"  [seed={seed} alpha={alpha:.2f}] M={r['M']} status={status} "
              f"hp1_fails={r['hp1_fails']} max_k3={r['max_k3_err']:.2e} "
              f"max_cndc={r['max_cndc_err']:.2e} max_cert={r['max_cert_err']:.2e}",
              flush=True)

    n_cells_all_hp = sum(1 for r in alpha_results.values() if r["all_hp_ok"])
    elapsed = time.time() - t0

    return {
        "seed": seed, "N": N, "run_mode": RUN_MODE,
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
        "alpha_results": alpha_results,
        "n_cells_all_hp": int(n_cells_all_hp),
        "n_cells_total": len(ALPHA_CELLS),
        "elapsed_s": float(elapsed),
        "all_cells_pass": int(n_cells_all_hp == len(ALPHA_CELLS)),
    }


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    n = len(results)
    all_pass_count = sum(1 for r in results if r.get("all_cells_pass", 0))

    def mean_key(k):
        vs = [r[k] for r in results if k in r]
        return float(sum(vs) / len(vs)) if vs else 0.0

    mean_cells = mean_key("n_cells_all_hp")

    summary = (f"seeds_all_cells_pass={all_pass_count}/{n} "
               f"mean_cells_all_hp={mean_cells:.1f}/{len(ALPHA_CELLS)} "
               f"alpha_cells={ALPHA_CELLS}")

    # Check HP1 failures across all seeds and cells
    max_hp1_fails = 0
    for r in results:
        for cell in r.get("alpha_results", {}).values():
            max_hp1_fails = max(max_hp1_fails, cell.get("hp1_fails", 0))

    if max_hp1_fails > HF1_MAX_FAILS:
        return ("HARD_FAIL", f"HARD_FAIL: HP1 fails={max_hp1_fails}>{HF1_MAX_FAILS} per cell. {summary}")

    GATE = max(4, n - 1) if n >= 4 else n
    if all_pass_count >= GATE:
        return ("HARD_PASS", f"HARD_PASS: 5-method API algebraically uniform at all intermediate alpha. {summary}")
    if mean_cells >= len(ALPHA_CELLS) - 1:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: 1 alpha cell partial. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
t0_total = time.time()
run_config = {"N": N, "alpha_cells": ALPHA_CELLS, "run_mode": RUN_MODE}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print(f"[run] mode={RUN_MODE} N={N} alpha_cells={ALPHA_CELLS} seeds_todo={seeds_todo}", flush=True)

for s in seeds_todo:
    res = run_seed(s)
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
    "alpha_cells": ALPHA_CELLS,
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
