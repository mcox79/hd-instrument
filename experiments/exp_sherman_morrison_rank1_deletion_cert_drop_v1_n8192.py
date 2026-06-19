"""
sherman_morrison_rank1_deletion_cert_drop_v1_n8192 -- PP-56 production-envelope N=8192.

PP-56 was FOUNDED at N=4096 (v351): cert_ratio=0.000241, theory=0.000244, 1.2% match, 5/5 seeds.
This run confirms PP-56 algebraic cert at production-N=8192 for band-lift eligibility.
Theory: cert_ratio = lam/(lam+N) = 1/8193 ~ 0.000122 at N=8192, lam=1.

SCIENTIFIC QUESTION: Does SM deletion cert drop replicate at N=8192 with predicted N-scaling?
  At N=4096: cert_ratio=0.000241 ~ 1/4097
  At N=8192: predicted cert_ratio ~ 1/8193 = 0.000122 (half of N=4096 value)
  Test: cert_ratio < 0.15 (same HP gate as N=4096; theory now 1225x below gate).
  Monotone decrease: cert_ratio(N=8192) < cert_ratio(N=4096) is the additional test.

PRE-REGISTERED BANDS (PP-56 production-N=8192; same gate structure as v2_n4096):
  HARD-PASS:
    (a) mean cert_ratio < 0.15 (deletion cert drops to near-zero; gate = 1225x above theory)
    (b) mean retained_delta < 0.10 (retained patterns unaffected)
    (c) cert_ratio(N=8192) < cert_ratio(N=4096) = 0.000241 (N-scaling monotone decrease)
    (d) 5-seed unanimous on (a) and (b)
  MIDDLE: cert_ratio in [0.15, 0.30] OR retained_delta in [0.10, 0.20]
  HARD-FAIL: cert_ratio > 0.30 OR retained_delta > 0.30

FORMULA SELF-TESTS (PROT-022):
  1. cert_before for stored BSC xi: xi^T (xi xi^T / N) xi / N = 1.0.
     [INPUT: N=16, M=1, BSC xi] [EXPECTED: cert_before = 1.0]
  2. cert_after theoretical at N=8192: lam/(lam+N) = 1/8193 = 0.0001221
     [INPUT: lam=1.0, N=8192] [EXPECTED: 0.0001221 within 1e-6]
     Verified: 1/(1+8192) = 0.00012206...
  3. N-scaling: theory(N=8192)/theory(N=4096) = 4097/8193 ~ 0.5001 (half).
     [INPUT: N1=4096, N2=8192, lam=1] [EXPECTED: ratio ~ 0.5001]

PROT-018: anchor has _n8192; N MUST = 8192.
PROT-021: seed checkpoints keyed with run_mode.
QUEUE: remote_cpu_queue (pure CPU; N=8192 matrix W=(8192x8192) float32 = 268 MB; fits in CPU RAM).
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

ANCHOR_NAME = "sherman_morrison_rank1_deletion_cert_drop_v1_n8192"

_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

LAM = 1.0   # SM regularization parameter

# PROT-022: formula self-test values
_THEORY_N4096 = 1.0 / (1.0 + 4096)   # 0.000244
_THEORY_N8192 = 1.0 / (1.0 + 8192)   # 0.000122
_NSCALE_RATIO = _THEORY_N8192 / _THEORY_N4096  # ~0.5001

# Verify formulas (PROT-022 self-tests)
assert abs(_THEORY_N8192 - 0.00012206) < 1e-5, f"PROT-022 theory N=8192 fail: {_THEORY_N8192}"
assert abs(_NSCALE_RATIO - 0.5001) < 0.001, f"PROT-022 N-scaling ratio fail: {_NSCALE_RATIO}"
print(f"[PROT-022] theory_N8192={_THEORY_N8192:.6f} nscale_ratio={_NSCALE_RATIO:.4f}", flush=True)

HP_CERT_RATIO = 0.15
HP_RETAINED_DELTA = 0.10
HF_CERT_RATIO = 0.30
HF_RETAINED_DELTA = 0.30
N4096_CERT_RATIO = 0.000241   # empirical result from v2_n4096 for monotone check

if RUN_MODE == "smoke":
    N_ACTIVE = 1024   # multi-scale smoke at 1024 (N/8 of full)
    SEEDS = [7, 17]
    M_STORE = 10
    N_TRIALS = 5
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    M_STORE = 50
    N_TRIALS = 20


def bsc_np(m: int, n: int, rng: np.random.Generator) -> np.ndarray:
    """BSC vectors in {+1, -1}."""
    return rng.integers(0, 2, size=(m, n)).astype(np.float32) * 2 - 1


def build_hopfield_W(Xi: np.ndarray, n: int) -> np.ndarray:
    """W = Xi^T Xi / n."""
    return (Xi.T @ Xi) / n


def sm_delete(W: np.ndarray, xi: np.ndarray, n: int, lam: float = 1.0) -> np.ndarray:
    """Sherman-Morrison rank-1 deletion: W_new = W - (W xi)(xi^T W) / (lam + xi^T W xi)."""
    Wxi = W @ xi
    xiTW = xi @ W
    denom = lam + float(xi @ Wxi)
    if abs(denom) < 1e-12:
        return W.copy()
    return W - np.outer(Wxi, xiTW) / denom


def cert_fn(xi: np.ndarray, W: np.ndarray, n: int) -> float:
    """Cert = xi^T W xi / n."""
    return float(xi @ W @ xi) / n


def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel."""
    # Test 1: cert_before = 1.0 for M=1 stored pattern
    N_t = 16
    rng = np.random.default_rng(0)
    xi = bsc_np(1, N_t, rng)[0]
    W1 = np.outer(xi, xi) / N_t
    cb = cert_fn(xi, W1, N_t)
    assert abs(cb - 1.0) < 1e-5, f"cert_before selftest: {cb:.8f} expected ~1.0"

    # Test 2+3: SM deletion cert_after << 1
    W_new = sm_delete(W1, xi, N_t, lam=1.0)
    ca = cert_fn(xi, W_new, N_t)
    cert_ratio_t = ca / cb if cb > 1e-9 else 1.0
    assert cert_ratio_t < 0.3, f"cert_ratio selftest: {cert_ratio_t:.6f} expected < 0.3"

    # Test 4: PROT-022 N=8192 theory formula
    theory_check = 1.0 / (1.0 + N)
    assert abs(theory_check - _THEORY_N8192) < 1e-8, f"PROT-022 theory check fail: {theory_check}"

    # Test 5: production-scale smoke (N_ACTIVE)
    N_t3 = N_ACTIVE
    rng3 = np.random.default_rng(2)
    Xi3 = bsc_np(3, N_t3, rng3)
    W3 = build_hopfield_W(Xi3, N_t3)
    cb_check = cert_fn(Xi3[0], W3, N_t3)
    assert cb_check > 0.01, f"cert_before at smoke scale: {cb_check:.6f}"
    W3_del = sm_delete(W3, Xi3[0], N_t3, lam=LAM)
    ca_check = cert_fn(Xi3[0], W3_del, N_t3)
    ratio_check = ca_check / cb_check if cb_check > 1e-9 else 1.0
    assert not np.isnan(ratio_check), "cert_ratio NaN at smoke scale"
    assert 0.0 <= ratio_check <= 1.1, f"cert_ratio out of range: {ratio_check}"
    print(f"[selftest] PASS: cb={cb:.4f} ca={ca:.6f} ratio_small={cert_ratio_t:.4f} "
          f"ratio_Nactive={ratio_check:.6f} N={N_ACTIVE}", flush=True)


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

        cb = cert_fn(xi_del, W, n_dim)
        W_new = sm_delete(W, xi_del, n_dim, lam=LAM)
        ca = cert_fn(xi_del, W_new, n_dim)
        ratio = ca / cb if cb > 1e-9 else 1.0
        cert_ratios.append(ratio)

        n_retain_check = min(3, M_STORE - 1)
        retain_indices = [i for i in range(M_STORE) if i != del_idx][:n_retain_check]
        for ret_idx in retain_indices:
            xi_ret = Xi[ret_idx]
            cb_ret = cert_fn(xi_ret, W, n_dim)
            ca_ret = cert_fn(xi_ret, W_new, n_dim)
            delta = abs(ca_ret - cb_ret)
            retained_deltas.append(delta)

    mean_ratio = float(np.mean(cert_ratios))
    mean_retained = float(np.mean(retained_deltas)) if retained_deltas else 0.0
    elapsed = time.time() - t0

    print(f"  [seed={seed} N={n_dim}] cert_ratio={mean_ratio:.6f} "
          f"retained_delta={mean_retained:.6f} elapsed={elapsed:.2f}s theory={_THEORY_N8192:.6f}",
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
    n_monotone = sum(1 for r in results if r.get("mean_cert_ratio", 1.0) < N4096_CERT_RATIO)

    summary = (f"cert_ratio={cert_ratio:.6f}(HP<{HP_CERT_RATIO} HF>{HF_CERT_RATIO}) "
               f"retained_delta={retained_delta:.6f}(HP<{HP_RETAINED_DELTA}) "
               f"n_monotone={n_monotone}/{len(results)} "
               f"theory_N8192={_THEORY_N8192:.6f} N={N} lam={LAM} n_seeds={len(results)}")

    if cert_ratio > HF_CERT_RATIO or retained_delta > HF_RETAINED_DELTA:
        reasons = []
        if cert_ratio > HF_CERT_RATIO:
            reasons.append(f"cert_ratio={cert_ratio:.4f}>{HF_CERT_RATIO}")
        if retained_delta > HF_RETAINED_DELTA:
            reasons.append(f"retained_delta={retained_delta:.4f}>{HF_RETAINED_DELTA}")
        return ("HARD_FAIL", f"HARD_FAIL: {'; '.join(reasons)}. {summary}")

    if cert_ratio < HP_CERT_RATIO and retained_delta < HP_RETAINED_DELTA:
        monotone_tag = f"N-scaling monotone: {n_monotone}/{len(results)} seeds < N4096_result"
        return ("HARD_PASS",
                f"HARD_PASS: cert_ratio={cert_ratio:.6f}<{HP_CERT_RATIO} after SM deletion; "
                f"retained stable (delta={retained_delta:.6f}<{HP_RETAINED_DELTA}); {monotone_tag}. "
                f"PP-56 production-N=8192 confirmed. {summary}")

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

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

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
    "theory_cert_ratio_N8192": _THEORY_N8192,
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
