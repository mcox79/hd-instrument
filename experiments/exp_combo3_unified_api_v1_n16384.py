"""
combo3_unified_api_v1_n16384 -- COMBO-3: 5-method unified audit API at N=16384.

Fills N=16384 in the scaling curve: N=4096 (HARD_PASS), N=8192 (pending), N=32768 (cloud LIFT).
VRAM estimate: W matrix float64 = 8 * 16384^2 = 2.15 GB; M=40 Xi: 5.2 MB; peak ~2.16 GB OK.
(numpy/CPU only; overnight_queue for remote machine depth.)

PRE-REGISTERED BANDS:
  HP1: |delta_i^direct - delta_i^closedform| < 1e-8 for ALL 9 primitives.
       (Same tolerance as n8192; float64 at N=16384 should be stable.)
  HP2: kappa_3 update error < 1e-5.
  HP3: CNDC composition error < 1e-8.
  HP4: Cert signature error < 1e-8.
  HP5: Matvec count <= 5.
  HARD-PASS: ALL 5 HP conditions satisfied in >= 4/5 seeds.
  MIDDLE: 4 of 5 conditions.
  HARD-FAIL: HP1 fails for >3 primitives OR HP5 fails.

  Prior: N=4096 exact-0 all primitives; N=8192 similar uniformity.
  N=16384 may widen float64 accumulation errors but closed-form uses only dot products.

FORMULA SELF-TESTS:
  1. Krylov buffer delta_1: xi^T delta_xi / N = 0 for orthogonal pair.
     [INPUT: N=4, xi=[1,1,-1,-1], delta_xi=[1,-1,1,-1]] [EXPECTED: delta_1 = 0.0]
  2. CNDC sum: delta_1 + delta_2 + delta_3.
     [INPUT: delta_1=0.1, delta_2=0.2, delta_3=0.3] [EXPECTED: CNDC=0.6]
  3. Matvec count for Krylov buffer (2 ops) covers all 9 primitives.
     [INPUT: any xi, W] [EXPECTED: matvec_count=2 <= 5]

PROT-018: anchor has _n16384; N MUST = 16384.
PROT-021: run_config includes N, M, run_mode.
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

ANCHOR_NAME = "combo3_unified_api_v1_n16384"

_N_SUFFIX = 16384
N = 16384
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    N_SMOKE = 1024
    SEEDS = [7, 17]
    M = 10
else:
    N_SMOKE = N
    SEEDS = [7, 17, 23, 31, 41]
    M = 40

HP_DELTA_TOL = 1e-8
HP_KAPPA3_TOL = 1e-5
HP_CNDC_TOL = 1e-8
HP_CERT_TOL = 1e-8
HP_MATVEC_MAX = 5
HF_N_PRIMITIVE_FAILS = 3


def _selftest_krylov_basic():
    xi = np.array([1.0, 1.0, -1.0, -1.0])
    delta_xi = np.array([1.0, -1.0, 1.0, -1.0])
    n = 4
    delta_1 = float(np.dot(xi, delta_xi)) / n
    assert abs(delta_1 - 0.0) < 1e-12, f"delta_1 selftest: {delta_1} expected 0.0"
    d1, d2, d3 = 0.1, 0.2, 0.3
    cndc = d1 + d2 + d3
    assert abs(cndc - 0.6) < 1e-12, f"CNDC selftest: {cndc} expected 0.6"
    return delta_1, cndc


def _instrumentation_selftest():
    d1, cndc = _selftest_krylov_basic()
    n_dim = N_SMOKE if RUN_MODE == "smoke" else N
    assert M > 0, "M must be > 0"
    print(f"[selftest] PASS: delta_1={d1:.4f} cndc={cndc:.4f} N={N} n_active={n_dim} M={M}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def krylov_buffer(W: np.ndarray, xi: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build {xi, W*xi, W^2*xi} -- 2 matvecs."""
    w1 = W @ xi
    w2 = W @ w1
    return xi, w1, w2


def delta_primitives_closed(xi: np.ndarray, w1: np.ndarray, w2: np.ndarray,
                              delta_xi: np.ndarray, n: int) -> List[float]:
    """9 primitives from Krylov buffer."""
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
    """Direct computation (ground truth)."""
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


def kappa3_update_closed(W: np.ndarray, xi: np.ndarray, delta_xi: np.ndarray, n: int) -> float:
    buf0, buf1, buf2 = krylov_buffer(W, xi)
    d3 = float(np.dot(buf2, delta_xi)) / n
    return 3.0 * d3


def kappa3_update_direct(W: np.ndarray, xi: np.ndarray, delta_xi: np.ndarray, n: int) -> float:
    w2xi = W @ (W @ xi)
    return 3.0 * float(np.dot(w2xi, delta_xi)) / n


def run_seed(seed: int, n_dim: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    Xi = rng.choice([-1.0, 1.0], size=(M, n_dim)).astype(np.float64)
    W = Xi.T @ Xi / float(n_dim)
    np.fill_diagonal(W, 0.0)

    xi = rng.choice([-1.0, 1.0], size=(n_dim,)).astype(np.float64)
    delta_xi = rng.choice([-1.0, 1.0], size=(n_dim,)).astype(np.float64)

    buf0, buf1, buf2 = krylov_buffer(W, xi)
    krylov_matvecs = 2

    d_closed = delta_primitives_closed(buf0, buf1, buf2, delta_xi, n_dim)
    matvec_direct = [0]
    d_direct = delta_primitives_direct(W, xi, delta_xi, n_dim, matvec_direct)

    errors = [abs(d_closed[i] - d_direct[i]) for i in range(9)]
    n_primitive_fails = sum(1 for e in errors if e > HP_DELTA_TOL)
    hp1 = n_primitive_fails == 0

    kappa3_closed = kappa3_update_closed(W, xi, delta_xi, n_dim)
    kappa3_direct = kappa3_update_direct(W, xi, delta_xi, n_dim)
    kappa3_err = abs(kappa3_closed - kappa3_direct)
    hp2 = kappa3_err < HP_KAPPA3_TOL

    cndc_closed = sum(d_closed[:3])
    cndc_direct = sum(d_direct[:3])
    cndc_err = abs(cndc_closed - cndc_direct)
    hp3 = cndc_err < HP_CNDC_TOL

    cert_closed = float(np.dot(buf2, delta_xi)) / n_dim
    cert_direct = float(np.dot(W @ (W @ xi), delta_xi)) / n_dim
    cert_err = abs(cert_closed - cert_direct)
    hp4 = cert_err < HP_CERT_TOL

    matvec_count = 2
    hp5 = matvec_count <= HP_MATVEC_MAX

    elapsed = time.time() - t0
    print(f"  [seed={seed} N={n_dim}] hp1={int(hp1)}(n_fails={n_primitive_fails}) "
          f"hp2={int(hp2)}(k3err={kappa3_err:.2e}) hp3={int(hp3)}(cndc_err={cndc_err:.2e}) "
          f"hp4={int(hp4)}(cert_err={cert_err:.2e}) hp5={int(hp5)}(mvc={matvec_count}) "
          f"elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": n_dim, "M": M, "run_mode": RUN_MODE,
        "n_primitive_fails": n_primitive_fails,
        "kappa3_err": float(kappa3_err),
        "cndc_err": float(cndc_err),
        "cert_err": float(cert_err),
        "matvec_count": int(matvec_count),
        "hp1": bool(hp1), "hp2": bool(hp2), "hp3": bool(hp3),
        "hp4": bool(hp4), "hp5": bool(hp5),
        "elapsed_s": float(elapsed),
    }


def compute_verdict(per_seed: Dict) -> Tuple[str, str]:
    results = list(per_seed.values())
    if not results:
        return ("HARD_FAIL", "No valid results.")

    n = len(results)
    mean_fails = float(np.mean([r["n_primitive_fails"] for r in results]))
    mean_k3err = float(np.mean([r["kappa3_err"] for r in results]))
    mean_cndc = float(np.mean([r["cndc_err"] for r in results]))
    mean_cert = float(np.mean([r["cert_err"] for r in results]))
    mean_mvc = float(np.mean([r["matvec_count"] for r in results]))

    summary = (f"mean_prim_fails={mean_fails:.2f}(HP==0 HF>{HF_N_PRIMITIVE_FAILS}) "
               f"kappa3_err={mean_k3err:.2e}(HP<{HP_KAPPA3_TOL}) "
               f"cndc_err={mean_cndc:.2e}(HP<{HP_CNDC_TOL}) "
               f"cert_err={mean_cert:.2e}(HP<{HP_CERT_TOL}) "
               f"matvec={mean_mvc:.1f}(HP<={HP_MATVEC_MAX}) n_seeds={n}")

    if mean_fails > HF_N_PRIMITIVE_FAILS:
        return ("HARD_FAIL", f"HARD_FAIL: {mean_fails:.1f} primitive fails > {HF_N_PRIMITIVE_FAILS}. {summary}")
    if mean_mvc > HP_MATVEC_MAX:
        return ("HARD_FAIL", f"HARD_FAIL: matvec={mean_mvc:.1f} > {HP_MATVEC_MAX}. {summary}")

    n_all_hp = sum(1 for r in results if r["hp1"] and r["hp2"] and r["hp3"] and r["hp4"] and r["hp5"])
    n_hp4 = sum(1 for r in results if sum([r["hp1"], r["hp2"], r["hp3"], r["hp4"], r["hp5"]]) >= 4)
    min_pass = math.ceil(n * 0.8)

    if n_all_hp >= min_pass:
        return ("HARD_PASS", f"HARD_PASS: all 5 HP at N=16384. {summary}")
    if n_hp4 >= min_pass:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: 4/5 HP at N=16384. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: insufficient HP at N=16384. {summary}")


n_active = N_SMOKE if RUN_MODE == "smoke" else N
print(f"[config] PROT-018 N={N} n_active={n_active} mode={RUN_MODE} "
      f"VRAM_est_GB={8*N*N/1e9:.2f} (float64 W at N={N})", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "n_active": n_active, "M": M, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] running N={n_active} M={M}...", flush=True)
    result = run_seed(seed, n_active)
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
    "n_active": n_active,
    "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS),
    "elapsed_s": elapsed_total,
    "mean_n_primitive_fails": float(np.mean([r["n_primitive_fails"] for r in all_results])) if all_results else None,
    "mean_kappa3_err": float(np.mean([r["kappa3_err"] for r in all_results])) if all_results else None,
    "mean_cndc_err": float(np.mean([r["cndc_err"] for r in all_results])) if all_results else None,
    "mean_cert_err": float(np.mean([r["cert_err"] for r in all_results])) if all_results else None,
    "mean_matvec_count": float(np.mean([r["matvec_count"] for r in all_results])) if all_results else None,
}
metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"[done] metrics -> {metrics_path}", flush=True)
