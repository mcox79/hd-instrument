"""
substrate_stage_a_bio_b26_composition_v1 -- B2 sparse-expansion x B6 D-ECR eviction (additive control).

ROUTING: notes/research_to_exp_dev_B36_refutation_acknowledged_refined_taxonomy_2026-06-04 (Priority 1, B26).
  Per refined taxonomy: B2 = capacity-CEILING expansion (raises alpha_c); B6 = capacity-LIMIT correction
  (evict when over). Different scales of the capacity axis -> predicted ADDITIVE composition (control vs B36).
  CPU numpy, $0. QUEUE: remote_cpu_queue (numpy; reloads the drained CPU queue with meaningful Priority-1 work).

CAPABILITY QUESTION (B26): in a STREAMING-NOVEL pattern task (T >> capacity), does combining sparse-expansion
  (B2) + D-ECR eviction (B6) sustain higher recall than each alone? Predicted ADDITIVE (sparse raises the
  per-pattern ceiling; eviction maintains a fresh bank past streaming) -- NOT superadditive (same axis).

MODEL: stream T novel bipolar patterns (N_in). ENCODE: dense (identity at N=2048) or sparse (DG expand to
  N_dg=4096, k-WTA f=0.02). Auto-assoc W (covariance for sparse, outer for dense) + bank cap m_cap. EVICT
  arm: D-ECR (drop lowest self-overlap) when bank>m_cap; NOEVICT arm: keep all (overflow). recall = frac of
  the FINAL bank recalled (dense overlap>0.95; sparse active-overlap>0.95). m_cap = alpha_c * N_dense.

CELLS (3 seeds): {dense,sparse} x {noevict,evict}; T = 3 * m_cap (streaming past capacity).
PRE-REG (gain vs dense-noevict baseline): HARD-PASS sparse+evict gain ~ sparse_gain + evict_gain (ADDITIVE,
  within 0.10) AND > max(sparse_gain, evict_gain) (both contribute). MIDDLE: subsumed (sparse+evict ~ max single).
  HARD-FAIL: sparse+evict < max single (collapse). [Predicted: MIDDLE/additive per refined taxonomy.]

FORMULA SELF-TESTS (PROT-022): 1. k-WTA exact. 2. dense low-load recall. 3. sparse completion. 4. alpha_c=0.138.
PROT-018: multi-cell anchor (no _nN). ASCII-only. write_metrics.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, json, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_stage_a_bio_b26_composition_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
F_SPARSE = 0.02
RECALL = 0.95

if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_DENSE = 512; N_DG = 2048
else:
    SEEDS = [7, 17, 23]; N_DENSE = 2048; N_DG = 4096


def bipolar(shape, g):
    return (g.integers(0, 2, size=shape) * 2 - 1).astype(np.float32)


def _kwta(h, k):
    idx = np.argpartition(-h, k - 1, axis=1)[:, :k]
    s = np.zeros_like(h); np.put_along_axis(s, idx, 1.0, axis=1)
    return s.astype(np.float32)


def stream_recall(encoding, evict, T, m_cap, g):
    """stream T novel patterns; bank cap m_cap (if evict); return recall of final bank."""
    if encoding == "dense":
        n = N_DENSE; W = np.zeros((n, n), dtype=np.float32); bank = []
        for t in range(T):
            x = bipolar((n,), g); bank.append(x); W += np.outer(x, x); np.fill_diagonal(W, 0.0)
            if evict and len(bank) > m_cap:
                X = np.stack(bank); R = np.sign(X @ W.T); R[R == 0] = 1.0; ov = (X * R).sum(axis=1) / n
                ev = int(np.argmin(ov)); xe = bank.pop(ev); W -= np.outer(xe, xe); np.fill_diagonal(W, 0.0)
        X = np.stack(bank); R = np.sign(X @ W.T); R[R == 0] = 1.0
        return float(np.mean((X * R).sum(axis=1) / n > RECALL))
    else:  # sparse DG expansion
        n_in = N_DENSE; n_dg = N_DG; k = max(1, int(round(F_SPARSE * n_dg)))
        P = (g.standard_normal((n_dg, n_in)) / math.sqrt(n_in)).astype(np.float32)
        W = np.zeros((n_dg, n_dg), dtype=np.float32); bank = []   # store sparse codes
        for t in range(T):
            xin = bipolar((1, n_in), g); s = _kwta(xin @ P.T, k)[0]; bank.append(s)
            W += np.outer(s - F_SPARSE, s - F_SPARSE); np.fill_diagonal(W, 0.0)
            if evict and len(bank) > m_cap:
                S = np.stack(bank); Rr = _kwta((S - F_SPARSE) @ W.T, k); ov = (Rr * S).sum(axis=1) / k
                ev = int(np.argmin(ov)); se = bank.pop(ev); W -= np.outer(se - F_SPARSE, se - F_SPARSE); np.fill_diagonal(W, 0.0)
        S = np.stack(bank); Rr = _kwta((S - F_SPARSE) @ W.T, k)
        return float(np.mean((Rr * S).sum(axis=1) / k > RECALL))


def _selftest():
    g = np.random.default_rng(0)
    h = g.standard_normal((2, 100)); assert np.all(_kwta(h, 5).sum(axis=1) == 5), "kWTA"
    X = bipolar((5, 256), g); W = (X.T @ X).astype(np.float32); np.fill_diagonal(W, 0.0)
    assert float(np.mean((np.sign(X @ W.T) * X).sum(axis=1) / 256 > 0.95)) > 0.9, "dense recall"
    n_dg = 1024; k = int(round(F_SPARSE * n_dg)); S = np.zeros((4, n_dg), dtype=np.float32)
    for i in range(4):
        S[i, g.choice(n_dg, size=k, replace=False)] = 1.0
    W2 = ((S - F_SPARSE).T @ (S - F_SPARSE)).astype(np.float32); np.fill_diagonal(W2, 0.0)
    R = _kwta((S - F_SPARSE) @ W2.T, k); assert float((R[0] * S[0]).sum() / k) > 0.95, "sparse completion"
    assert abs(ALPHA_C - 0.138) < 1e-6
    print("[selftest] PASS: kwta dense_recall sparse_completion", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    m_cap = max(4, int(round(ALPHA_C * N_DENSE))); T = 3 * m_cap; out = {}
    for enc in ["dense", "sparse"]:
        for ev in [False, True]:
            g = np.random.default_rng(seed * 100 + (0 if enc == "dense" else 10) + (1 if ev else 0))
            out[f"{enc}_{'evict' if ev else 'noevict'}"] = stream_recall(enc, ev, T, m_cap, g)
    return {"seed": seed, "m_cap": m_cap, "T": T, **out}


def verdict(per_seed) -> Tuple[str, str]:
    def mean(k):
        return float(np.mean([s[k] for s in per_seed]))
    base = mean("dense_noevict")
    g_sparse = mean("sparse_noevict") - base; g_evict = mean("dense_evict") - base; g_both = mean("sparse_evict") - base
    summary = (f"dense_noevict={base:.2f} | gains: sparse={g_sparse:+.2f} evict={g_evict:+.2f} both={g_both:+.2f} "
               f"(sum_singles={g_sparse + g_evict:+.2f})")
    if g_both > max(g_sparse, g_evict) + 0.02 and abs(g_both - (g_sparse + g_evict)) <= 0.10:
        return ("HARD_PASS", f"HARD_PASS: B2+B6 ADDITIVE (both contribute, ~sum). {summary}")
    if g_both >= max(g_sparse, g_evict) - 0.02:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: B2+B6 subsumed (~max single, not clearly additive). {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: B2+B6 composition collapse (both < max single). {summary}")


print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} seeds={SEEDS} N_dense={N_DENSE} N_dg={N_DG}", flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); per_seed = []
for seed in SEEDS:
    r = run_seed(seed); per_seed.append(r)
    print(f"  [seed={seed}] dense_noevict={r['dense_noevict']:.2f} dense_evict={r['dense_evict']:.2f} sparse_noevict={r['sparse_noevict']:.2f} sparse_evict={r['sparse_evict']:.2f}", flush=True)
v, vmsg = verdict(per_seed)
print(f"\n[VERDICT] {vmsg}", flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE,
           "n_seeds": len(SEEDS), "cells": ["B26_composition"], "per_seed": per_seed, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, per_seed)
print("[metrics] written", flush=True)
