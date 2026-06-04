"""
substrate_stage_a_bio_smoke_B2_sparse_fix_v2 -- DG sparse-expansion capacity, CORRECTED recall -- LAPTOP CPU.

ROUTING: notes/change_request_stage_a_bio_smoke_REVISED_drill_B_specs (B2). Batch-2 B2 returned M_crit_sparse=0
  because I re-expanded a NOISY input through k-WTA (unstable -> different sparse code, not a noisy cue). FIX:
  test sparse associative-memory capacity DIRECTLY -- generate sparse codes, cue by DROPPING active bits, recall
  via covariance W + k-WTA completion. CPU numpy, $0. LAPTOP.

CAPABILITY QUESTION (B2): does a high-dim SPARSE code (f=0.02 at N_dg=4096) hold more patterns (M_crit) than a
  dense bipolar code at matched-ish dimension (N=2048, f=0.5)? Willshaw/Tsodyks: sparse codes have far higher
  associative capacity. HP: M_crit(sparse) >= 10x M_crit(dense).

MODEL:
  dense (2a): N bipolar +-1; W=sum xx^T diag0; cue=20% bit-flip; recall=sign(W@cue); recovered iff overlap>0.95.
  sparse (2b): k=f*N_dg active binary; W=sum(s-f)(s-f)^T diag0; cue=drop 20% of active bits; recall h=(cue-f)@W,
              k-WTA top-k -> recovered binary; recovered iff active-overlap (|recovered & stored|/k) > 0.95.
  M_crit = largest M (swept) with mean recovery >= 0.90.

PRE-REG: HP M_crit_sparse >= 10x M_crit_dense; MID >= 2x; HF < 2x.
WHY-DRILL HF: code Gram off-diagonal mean > 0.1*k -> sparse codes not separable -> raise N_dg / lower f.

FORMULA SELF-TESTS (PROT-022): 1. sparse covariance recall completes a dropped-bit cue at low load. 2. dense recalls
  at low load. 3. k-WTA exact. 4. f=0.02.
ASCII-only. PROT-021: local CPU.
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

ANCHOR_NAME = "substrate_stage_a_bio_smoke_B2_sparse_fix_v2"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

F_SPARSE = 0.02
DROP = 0.20          # fraction of active bits dropped in the cue
RECALL = 0.90

if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_DENSE = 512; N_DG = 2048
    M_DENSE = [10, 30, 60]; M_SPARSE = [50, 150, 400, 800]
else:
    SEEDS = [7, 17, 23]; N_DENSE = 2048; N_DG = 4096
    M_DENSE = [50, 100, 200, 300, 400]; M_SPARSE = [100, 300, 600, 1200, 2400, 4800]


def _kwta_rows(h, k):
    idx = np.argpartition(-h, k - 1, axis=1)[:, :k]
    s = np.zeros_like(h); np.put_along_axis(s, idx, 1.0, axis=1)
    return s.astype(np.float32)


def dense_mcrit(n, g):
    mcrit = 0
    for M in M_DENSE:
        X = ((g.integers(0, 2, (M, n)) * 2 - 1)).astype(np.float32)
        W = (X.T @ X).astype(np.float32); np.fill_diagonal(W, 0.0)
        flip = g.random((M, n)) < 0.20; Xc = X * np.where(flip, -1.0, 1.0)
        R = np.sign(Xc @ W.T); R[R == 0] = 1.0
        rec = float(np.mean((R * X).sum(axis=1) / n > 0.95))
        if rec >= RECALL:
            mcrit = M
        else:
            break
    return mcrit


def sparse_mcrit(n_dg, f, g):
    k = max(1, int(round(f * n_dg))); mcrit = 0
    for M in M_SPARSE:
        # generate M sparse binary codes (k active each)
        S = np.zeros((M, n_dg), dtype=np.float32)
        for i in range(M):
            S[i, g.choice(n_dg, size=k, replace=False)] = 1.0
        W = ((S - f).T @ (S - f)).astype(np.float32); np.fill_diagonal(W, 0.0)
        # cue: drop 20% of active bits
        C = S.copy()
        for i in range(M):
            act = np.flatnonzero(S[i]); drop = g.choice(act, size=max(1, int(round(DROP * k))), replace=False)
            C[i, drop] = 0.0
        H = (C - f) @ W.T
        R = _kwta_rows(H, k)
        rec = float(np.mean((R * S).sum(axis=1) / k > 0.95))
        if rec >= RECALL:
            mcrit = M
        else:
            break
    return mcrit, k


def _selftest():
    g = np.random.default_rng(0)
    # sparse low-load completion
    n_dg = 1024; f = 0.02; k = int(round(f * n_dg))
    S = np.zeros((5, n_dg), dtype=np.float32)
    for i in range(5):
        S[i, g.choice(n_dg, size=k, replace=False)] = 1.0
    W = ((S - f).T @ (S - f)).astype(np.float32); np.fill_diagonal(W, 0.0)
    C = S.copy(); act = np.flatnonzero(S[0]); C[0, act[:max(1, k // 5)]] = 0.0
    R = _kwta_rows((C - f) @ W.T, k)
    assert float((R[0] * S[0]).sum() / k) > 0.95, "sparse completion failed"
    h = g.standard_normal((2, 50)); s = _kwta_rows(h, 5); assert np.all(s.sum(axis=1) == 5)
    X = ((g.integers(0, 2, (5, 256)) * 2 - 1)).astype(np.float32); Wd = (X.T @ X).astype(np.float32); np.fill_diagonal(Wd, 0)
    assert float(np.mean((np.sign(X @ Wd.T) * X).sum(axis=1) / 256 > 0.95)) > 0.9
    assert abs(F_SPARSE - 0.02) < 1e-9
    print("[selftest] PASS: sparse_completion kwta_exact dense_recall", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_all() -> Dict:
    t0 = time.time(); per_seed = []
    for seed in SEEDS:
        g = np.random.default_rng(seed * 17 + 2)
        md = dense_mcrit(N_DENSE, g)
        ms, k = sparse_mcrit(N_DG, F_SPARSE, g)
        ratio = float(ms / max(md, 1))
        per_seed.append({"seed": seed, "M_crit_dense": md, "M_crit_sparse": ms, "k_active": k,
                         "N_dense": N_DENSE, "N_dg": N_DG, "ratio": ratio})
        print(f"  [seed={seed}] dense(N={N_DENSE}) M_crit={md} | sparse(N_dg={N_DG} k={k}) M_crit={ms} -> ratio={ratio:.1f}x", flush=True)
    return {"per_seed": per_seed, "elapsed_s": time.time() - t0}


def verdict(per_seed) -> Tuple[str, str]:
    ratio = float(np.median([s["ratio"] for s in per_seed]))
    md = float(np.median([s["M_crit_dense"] for s in per_seed])); ms = float(np.median([s["M_crit_sparse"] for s in per_seed]))
    note = "" if ms < M_SPARSE[-1] else " (sparse M_crit hit grid ceiling -- true ratio is HIGHER)"
    summary = f"M_crit dense={md:.0f} sparse={ms:.0f} ratio={ratio:.1f}x{note}"
    if ratio >= 10.0:
        return ("HARD_PASS", f"HARD_PASS: DG sparse expansion gives >=10x capacity. {summary}")
    if ratio >= 2.0:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: sparse 2-10x capacity. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: sparse <2x dense capacity. {summary}")


print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} seeds={SEEDS} N_dense={N_DENSE} N_dg={N_DG} f={F_SPARSE}", flush=True)
out_dir = get_output_dir(ANCHOR_NAME)
r = run_all()
v, vmsg = verdict(r["per_seed"])
print(f"\n[VERDICT] {vmsg}", flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE,
           "n_seeds": len(SEEDS), "cells": ["B2_sparse_fix"], "per_seed": r["per_seed"], "elapsed_s": r["elapsed_s"]}
write_metrics(out_dir, metrics, r["per_seed"])
print("[metrics] written", flush=True)
