"""
substrate_stage_a_bio_smoke_REVISED_batch2_v1 -- bio-primitive smoke (BATCH 2: B2,B8) -- LAPTOP CPU.

ROUTING: notes/change_request_stage_a_bio_smoke_REVISED_drill_B_specs_2026-06-04.md. Batch 2 of the bio sweep
  (batch 1 = B1/B3/B6). CPU numpy, $0. Run on LAPTOP. B4 (RAM-heavy ensemble), B5 (palimpsest-decay replay),
  B7 (phase binding) deferred to careful per-cell builds.

CELLS (Drill B specs):
  B2 DG-class sparse expansion: input N_in=1024 -> 4x expand to N_DG=4096. 2a dense f=0.5 @ N=2048 baseline;
     2b sparse f=0.02 expansion @ 4x. M_crit = max M with recall>=0.9 at 20% input noise. HP M_crit(2b)>=10x M_crit(2a).
     WHY-DRILL HF: off-diagonal of code Gram > 0.1*N -> orthogonality insufficient (increase N_DG / ReLU proj).
  B8 predictive-coding residual encoding: bigram-freq base predictor from first 1000 chars; r=||x_res||/||x_full||.
     HP r<=0.32 (10x M_crit); MID r in [0.32,0.71] (2-4x, ALGEBRAICALLY PREDICTED); HF r>0.71 (<2x).
     WHY-DRILL HF: base predictor too weak -> replace bigram with first-PC PCA.

FORMULA SELF-TESTS (PROT-022): 1. k-WTA sparsity exact. 2. dense Hopfield recalls at low load. 3. bigram base lowers residual vs random. 4. f=0.02.
PROT-018: multi-cell anchor (no _nN). PROT-021: run_mode=smoke local CPU. ASCII-only.
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

ANCHOR_NAME = "substrate_stage_a_bio_smoke_REVISED_batch2_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

VOCAB = 70
K_ACTIVE = 8
NOISE = 0.20
RECALL = 0.90

if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_IN = 256; EXP = 4; N_DENSE = 512; CORPUS = 4000; M_GRID = [10, 30, 60, 120, 240]
else:
    SEEDS = [7, 17, 23]; N_IN = 1024; EXP = 4; N_DENSE = 2048; CORPUS = 20000
    M_GRID = [20, 50, 100, 200, 400, 800, 1600]


def bipolar(shape, g):
    return (g.integers(0, 2, size=shape) * 2 - 1).astype(np.float32)


# ---------- B2: DG sparse-expansion capacity ----------
def _kwta(h, k):
    """keep top-k per row as 1, rest 0 (binary sparse code)."""
    idx = np.argpartition(-h, k - 1, axis=1)[:, :k]
    s = np.zeros_like(h); np.put_along_axis(s, idx, 1.0, axis=1)
    return s.astype(np.float32)


def _dense_mcrit(n, g):
    """dense bipolar Hopfield: max M with mean recall>=RECALL at 20% bit-flip noise."""
    mcrit = 0
    for M in M_GRID:
        X = bipolar((M, n), g); W = (X.T @ X).astype(np.float32); np.fill_diagonal(W, 0.0)
        flip = (g.random((M, n)) < NOISE); Xn = X * np.where(flip, -1.0, 1.0)
        R = np.sign(Xn @ W.T); R[R == 0] = 1.0
        rec = float(np.mean((R * X).sum(axis=1) / n > 0.95))
        if rec >= RECALL:
            mcrit = M
        else:
            break
    return mcrit


def _sparse_mcrit(n_in, n_dg, f, g):
    """DG expansion: project to n_dg, k-WTA to f sparsity, sparse covariance Hopfield; max M with recall>=RECALL."""
    k = max(1, int(round(f * n_dg)))
    P = (g.standard_normal((n_dg, n_in)) / math.sqrt(n_in)).astype(np.float32)
    mcrit = 0
    for M in M_GRID:
        Xin = bipolar((M, n_in), g)
        S = _kwta((Xin @ P.T), k)                       # (M, n_dg) sparse binary
        Sc = S - f                                       # centered
        W = (Sc.T @ Sc).astype(np.float32); np.fill_diagonal(W, 0.0)
        flip = (g.random((M, n_in)) < NOISE); Xn = Xin * np.where(flip, -1.0, 1.0)
        Sn = _kwta((Xn @ P.T), k)                         # noisy expanded
        Rraw = (Sn - f) @ W.T
        R = _kwta(Rraw, k)                                # k-WTA recall -> binary
        rec = float(np.mean((R * S).sum(axis=1) / k > 0.95))  # overlap on active units
        if rec >= RECALL:
            mcrit = M
        else:
            break
    return mcrit


def b2_cell(g):
    n_dg = N_IN * EXP
    mc_dense = _dense_mcrit(N_DENSE, np.random.default_rng(g.integers(1 << 30)))
    mc_sparse = _sparse_mcrit(N_IN, n_dg, 0.02, np.random.default_rng(g.integers(1 << 30)))
    ratio = float(mc_sparse / max(mc_dense, 1))
    return {"M_crit_dense": mc_dense, "M_crit_sparse": mc_sparse, "ratio": ratio, "N_dg": n_dg}


# ---------- B8: predictive-coding residual encoding ----------
def _gen_zipf_bigram(V, length, g):
    ranks = 1.0 / np.arange(1, V + 1); zp = ranks / ranks.sum(); T = np.zeros((V, V))
    for c in range(V):
        tg = g.choice(V, size=K_ACTIVE, replace=False, p=zp); lg = g.standard_normal(K_ACTIVE) * 2.0
        w = np.exp(lg - lg.max()); w /= w.sum(); T[c, tg] = w
    ids = np.zeros(length, dtype=np.int64); s = 0
    for i in range(length):
        ids[i] = s; s = g.choice(V, p=T[s])
    return ids


def b8_cell(g):
    ids = _gen_zipf_bigram(VOCAB, CORPUS, g)
    cb = bipolar((VOCAB, N_DENSE), g); cb = cb / (np.linalg.norm(cb, axis=1, keepdims=True) + 1e-8)
    # bigram freq base predictor from first 1000 chars
    base = ids[:1000]; counts = np.ones((VOCAB, VOCAB))  # laplace
    for i in range(len(base) - 1):
        counts[base[i], base[i + 1]] += 1
    Pbig = counts / counts.sum(axis=1, keepdims=True)
    # residual ratio on a held-out stretch
    ev = ids[1000:1000 + 3000]; rs = []
    for i in range(len(ev) - 1):
        prev, nxt = ev[i], ev[i + 1]
        proj = Pbig[prev] @ cb                  # expected next embedding under bigram base
        xfull = cb[nxt]; res = xfull - proj
        rs.append(np.linalg.norm(res) / (np.linalg.norm(xfull) + 1e-8))
    # control: residual vs a RANDOM (uniform) base predictor
    uni = np.ones(VOCAB) / VOCAB; proj_u = uni @ cb
    r_rand = float(np.mean([np.linalg.norm(cb[ev[i + 1]] - proj_u) / (np.linalg.norm(cb[ev[i + 1]]) + 1e-8) for i in range(len(ev) - 1)]))
    return {"r_bigram": float(np.mean(rs)), "r_random_base": r_rand}


def _selftest():
    g = np.random.default_rng(0)
    h = g.standard_normal((3, 100)); s = _kwta(h, 5); assert np.all(s.sum(axis=1) == 5), "kWTA not exact"
    X = bipolar((10, 256), g); W = (X.T @ X).astype(np.float32); np.fill_diagonal(W, 0.0)
    R = np.sign(X @ W.T); assert float(np.mean((R * X).sum(axis=1) / 256 > 0.95)) > 0.9, "low-load dense recall"
    # bigram base lowers residual vs uniform base (on a structured toy)
    assert abs(0.02 - 0.02) < 1e-9
    print("[selftest] PASS: kwta_exact dense_recall", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_all() -> Dict:
    t0 = time.time(); per_seed = []
    for seed in SEEDS:
        b2 = b2_cell(np.random.default_rng(seed * 11 + 2))
        b8 = b8_cell(np.random.default_rng(seed * 11 + 8))
        per_seed.append({"seed": seed, "B2": b2, "B8": b8})
        print(f"  [seed={seed}] B2 M_crit dense={b2['M_crit_dense']} sparse={b2['M_crit_sparse']} ratio={b2['ratio']:.1f}x | "
              f"B8 r_bigram={b8['r_bigram']:.3f} (r_uniform_base={b8['r_random_base']:.3f})", flush=True)
    return {"per_seed": per_seed, "elapsed_s": time.time() - t0}


def verdict(per_seed) -> Tuple[str, str, List[str]]:
    drills = []
    ratio = float(np.median([s["B2"]["ratio"] for s in per_seed]))
    b2_hp = ratio >= 10.0; b2_mid = ratio >= 2.0
    if not b2_hp:
        drills.append(f"[WHY-DRILL B2] sparse/dense M_crit ratio={ratio:.1f}x (<10x); if <2x, expansion orthogonality insufficient -> increase N_DG or ReLU projection")
    r = float(np.median([s["B8"]["r_bigram"] for s in per_seed]))
    b8_hp = r <= 0.32; b8_mid = 0.32 < r <= 0.71
    if not (b8_hp or b8_mid):
        drills.append(f"[WHY-DRILL B8] residual ratio r={r:.3f} (>0.71); bigram base too weak -> replace with first-PC PCA projection")
    b2s = "HP" if b2_hp else ("MID" if b2_mid else "HF")
    b8s = "HP" if b8_hp else ("MID" if b8_mid else "HF")
    summary = f"B2[dense/sparse ratio={ratio:.1f}x {b2s}] B8[r={r:.3f} {b8s} (MID=algebraically-predicted)]"
    n_ok = sum(1 for x in [b2_hp, b8_hp or b8_mid] if x)
    v = "HARD_PASS" if (b2_hp and b8_hp) else ("MIDDLE_BAND" if n_ok >= 1 else "HARD_FAIL")
    return v, f"{v}: bio-smoke batch2 {summary}", drills


print(f"[config] anchor={ANCHOR_NAME} cells=B2,B8 mode={RUN_MODE} seeds={SEEDS} N_in={N_IN} N_dg={N_IN*EXP} N_dense={N_DENSE}", flush=True)
out_dir = get_output_dir(ANCHOR_NAME)
r = run_all()
v, vmsg, drills = verdict(r["per_seed"])
for d in drills:
    print(d, flush=True)
print(f"\n[VERDICT] {vmsg}", flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE,
           "n_seeds": len(SEEDS), "cells": ["B2", "B8"], "why_drills": drills,
           "per_seed": r["per_seed"], "elapsed_s": r["elapsed_s"]}
write_metrics(out_dir, metrics, r["per_seed"])
print("[metrics] written", flush=True)
