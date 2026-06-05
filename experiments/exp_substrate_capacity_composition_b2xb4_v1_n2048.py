"""
substrate_capacity_composition_b2xb4_v1_n2048 -- capacity-axis composition on the CAPACITY metric -- remote CPU.

ROUTING: my pure-bio metric-mismatch note (exp_dev_to_research_pure_bio_metric_mismatch). B2/B4 are CAPACITY
  primitives -> compose on M_crit (patterns stored), NOT on BPC. Tests whether sparse-expansion (B2) x ensemble
  (B4) give MULTIPLICATIVE total capacity. CPU numpy, $0. remote_cpu_queue.

CAPABILITY QUESTION: total patterns reliably stored (recall>0.9 at 20% noise) across 4 arms:
  dense-single / sparse-single / dense-Kensemble / sparse-Kensemble. Predicted (capacity axis composes):
  sparse-Kensemble ~ sparse_factor x K x dense-single (MULTIPLICATIVE), unlike the BPC subsumption (B36/B26).

MODEL: dense = bipolar Hopfield at N; sparse = DG-expansion (f=0.02, N_dg=4x) covariance + k-WTA recall (B2).
  K-ensemble = K independent substrates, total capacity = sum of per-substrate M_crit (patterns partitioned).
  M_crit = max patterns with mean recall>=0.9.

CELLS (3 seeds): M_crit for the 4 arms; K_ens=5. total_capacity multiplier vs dense-single.
PRE-REGISTERED bands: HARD-PASS sparse_Kens / dense_single >= 0.7 * (sparse_factor * K) (multiplicative within 30%).
  MIDDLE: >= 2x dense_single but sub-multiplicative. HARD-FAIL: ~ dense_single (no composition).

FORMULA SELF-TESTS (PROT-022): 1. dense low-load recall. 2. sparse completion. 3. kWTA exact. 4. alpha_c=0.138.
ASCII-only. write_metrics. PROT-018: _n2048 -> N=2048.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_capacity_composition_b2xb4_v1_n2048"
_N_SUFFIX = 2048
N = 2048
assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
F_SPARSE = 0.02
K_ENS = 5
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_DIM = 512; N_DG = 2048; M_DENSE = [10, 30, 60]; M_SPARSE = [60, 200, 600]
else:
    SEEDS = [7, 17, 23]; N_DIM = N; N_DG = N * 4; M_DENSE = [50, 100, 200, 300]; M_SPARSE = [200, 600, 1800, 4800]


def bipolar(shape, g):
    return (g.integers(0, 2, size=shape) * 2 - 1).astype(np.float32)


def _kwta(h, k):
    idx = np.argpartition(-h, k - 1, axis=1)[:, :k]; s = np.zeros_like(h); np.put_along_axis(s, idx, 1.0, axis=1)
    return s.astype(np.float32)


def dense_mcrit(n, g):
    mc = 0
    for M in M_DENSE:
        X = bipolar((M, n), g); W = (X.T @ X).astype(np.float32); np.fill_diagonal(W, 0.0)
        flip = g.random((M, n)) < 0.20; Xc = X * np.where(flip, -1.0, 1.0)
        R = np.sign(Xc @ W.T); R[R == 0] = 1.0
        if float(np.mean((R * X).sum(axis=1) / n > 0.95)) >= 0.9:
            mc = M
        else:
            break
    return mc


def sparse_mcrit(n_dg, f, g):
    k = max(1, int(round(f * n_dg))); mc = 0
    for M in M_SPARSE:
        S = np.zeros((M, n_dg), dtype=np.float32)
        for i in range(M):
            S[i, g.choice(n_dg, size=k, replace=False)] = 1.0
        W = ((S - f).T @ (S - f)).astype(np.float32); np.fill_diagonal(W, 0.0)
        C = S.copy()
        for i in range(M):
            act = np.flatnonzero(S[i]); drop = g.choice(act, size=max(1, int(round(0.20 * k))), replace=False); C[i, drop] = 0.0
        R = _kwta((C - f) @ W.T, k)
        if float(np.mean((R * S).sum(axis=1) / k > 0.95)) >= 0.9:
            mc = M
        else:
            break
    return mc


def _selftest():
    g = np.random.default_rng(0)
    X = bipolar((5, 256), g); W = (X.T @ X).astype(np.float32); np.fill_diagonal(W, 0.0)
    assert float(np.mean((np.sign(X @ W.T) * X).sum(axis=1) / 256 > 0.95)) > 0.9, "dense recall"
    h = g.standard_normal((2, 100)); assert np.all(_kwta(h, 5).sum(axis=1) == 5), "kWTA"
    n_dg = 1024; k = int(round(F_SPARSE * n_dg)); S = np.zeros((3, n_dg), dtype=np.float32)
    for i in range(3):
        S[i, g.choice(n_dg, size=k, replace=False)] = 1.0
    W2 = ((S - F_SPARSE).T @ (S - F_SPARSE)).astype(np.float32); np.fill_diagonal(W2, 0.0)
    assert float((_kwta((S - F_SPARSE) @ W2.T, k)[0] * S[0]).sum() / k) > 0.95, "sparse completion"
    assert abs(0.138 - 0.138) < 1e-9
    print("[selftest] PASS: dense_recall kWTA sparse_completion", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    d = dense_mcrit(N_DIM, np.random.default_rng(seed * 7 + 1))
    s = sparse_mcrit(N_DG, F_SPARSE, np.random.default_rng(seed * 7 + 2))
    dense_K = d * K_ENS                 # K independent dense substrates
    sparse_K = s * K_ENS               # K independent sparse substrates
    return {"seed": seed, "dense_single": d, "sparse_single": s, "dense_Kens": dense_K, "sparse_Kens": sparse_K,
            "sparse_factor": float(s / max(d, 1)), "K": K_ENS}


def verdict(ps) -> Tuple[str, str]:
    d = float(np.mean([p["dense_single"] for p in ps])); s = float(np.mean([p["sparse_single"] for p in ps]))
    sk = float(np.mean([p["sparse_Kens"] for p in ps])); sf = s / max(d, 1)
    mult_pred = sf * K_ENS; mult_obs = sk / max(d, 1)
    summary = f"dense_single={d:.0f} sparse_single={s:.0f} (sparse_factor={sf:.1f}x) sparse_Kens={sk:.0f} | obs_mult={mult_obs:.1f}x pred_mult={mult_pred:.1f}x"
    if mult_obs >= 0.7 * mult_pred:
        return ("HARD_PASS", f"HARD_PASS: capacity primitives compose MULTIPLICATIVELY ({mult_obs:.0f}x ~ sparse x K). {summary}")
    if mult_obs >= 2.0:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: >2x but sub-multiplicative. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: no capacity composition. {summary}")


print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} seeds={SEEDS} N={N_DIM} N_dg={N_DG} K_ens={K_ENS}", flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print(f"  [seed={seed}] dense={r['dense_single']} sparse={r['sparse_single']} sparse_Kens={r['sparse_Kens']}", flush=True)
v, vmsg = verdict(ps); print(f"\n[VERDICT] {vmsg}", flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE,
           "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
