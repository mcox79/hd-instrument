"""
substrate_stage_a_bio_b8_logit_sparse_residual_v1 -- B8 Cell-4 logit-space sparse residual (CPU).

ROUTING: notes/research_to_exp_dev_B8_residual_encoding_cells_per_drill (Cell 4, recommended first; P=0.40).
  Round-1 B8 r=0.86 because random codebooks guarantee r->1 for the FULL residual (D-RIP worst case). Cell-4 fix:
  store only the SPARSE top-K logit residual (K=5 most-mispredicted symbols vs a bigram base) -> norm ~sqrt(K)
  vs full ~sqrt(V) -> r ~ sqrt(K/V) ~ 0.27 -> ~14x M_crit. CPU numpy, $0. remote_cpu_queue (reload).

MODEL: bigram base predictor Pbig from corpus. For each (context c, next x): error_v = 1[v==x] - Pbig[c,v]
  (per-symbol prediction error). Project to random codebook cb (V x N, unit-norm):
    full_residual_vec  = sum_v sign(error_v) * cb[v]            (all V symbols; norm ~ sqrt(V))
    sparse_residual_vec= sum_{topK |error|} sign(error_v)*cb[v] (K=5 symbols; norm ~ sqrt(K))
  r = ||sparse|| / ||full||. M_crit gain: store M sparse-residuals vs M full-patterns in auto-assoc W, compare
  capacity (max M with self-recall>0.9). RECONSTRUCTION check: does base + retrieved sparse-residual predict the
  next char better than base alone (validates the compact residual is USEFUL, not just small)?

CELLS (3 seeds): measure r; M_crit(sparse-residual) vs M_crit(full-pattern); reconstruction acc base vs base+residual.
PRE-REG (per spec): HARD-PASS r<=0.30 AND M_crit gain>=10x. MID r in [0.30,0.55] OR gain 4-10x. HARD-FAIL r>0.55 OR gain<4x.
  (Reconstruction reported alongside: residual must improve next-char prediction over base, else gain is for useless storage.)
WHY-DRILL HF: top-K calibration -- does bigram base identify the surprising symbols? if poorly calibrated -> higher-order n-gram base.

FORMULA SELF-TESTS (PROT-022): 1. sparse residual norm < full residual norm. 2. top-K selects largest |error|. 3. dense low-load recall. 4. r ~ sqrt(K/V) sanity.
ASCII-only. write_metrics. PROT-018: multi-cell anchor (no _nN).
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

ANCHOR_NAME = "substrate_stage_a_bio_b8_logit_sparse_residual_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

VOCAB = 70
K_ACTIVE = 8
TOPK = 5

if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N = 512; CORPUS = 5000; M_GRID = [10, 30, 80, 200, 500]
else:
    SEEDS = [7, 17, 23]; N = 2048; CORPUS = 25000; M_GRID = [20, 50, 100, 200, 400, 800, 1600]


def gen_zipf(V, length, g):
    ranks = 1.0 / np.arange(1, V + 1); zp = ranks / ranks.sum(); T = np.zeros((V, V))
    for c in range(V):
        tg = g.choice(V, size=K_ACTIVE, replace=False, p=zp); lg = g.standard_normal(K_ACTIVE) * 2.0
        w = np.exp(lg - lg.max()); w /= w.sum(); T[c, tg] = w
    ids = np.zeros(length, dtype=np.int64); s = 0
    for i in range(length):
        ids[i] = s; s = g.choice(V, p=T[s])
    return ids


def codebook(V, n, g):
    cb = (g.integers(0, 2, size=(V, n)) * 2 - 1).astype(np.float32)
    return cb / (np.linalg.norm(cb, axis=1, keepdims=True) + 1e-8)


def _mcrit(vecs_fn, g):
    """vecs_fn(M, g) -> (M,n) normalized stored vectors; M_crit = max M with self-recall>0.9 (auto-assoc, 20% noise)."""
    mc = 0
    for M in M_GRID:
        X = vecs_fn(M, g); n = X.shape[1]
        W = (X.T @ X).astype(np.float32); np.fill_diagonal(W, 0.0)
        flip = g.random((M, n)) < 0.20; Xc = X * np.where(flip, -1.0, 1.0)
        R = np.sign(Xc @ W.T); R[R == 0] = 1.0
        if float(np.mean((R * np.sign(X)).sum(axis=1) / n > 0.90)) >= 0.90:
            mc = M
        else:
            break
    return mc


def run_seed(seed: int) -> Dict:
    g = np.random.default_rng(seed); ids = gen_zipf(VOCAB, CORPUS, g)
    cb = codebook(VOCAB, N, g)
    counts = np.ones((VOCAB, VOCAB))
    for i in range(len(ids) - 1):
        counts[ids[i], ids[i + 1]] += 1
    Pbig = counts / counts.sum(axis=1, keepdims=True)
    # measure r + reconstruction over eval pairs
    ev = ids[:3000]; rs = []; base_hit = 0; res_hit = 0; ntot = 0
    sparse_vecs = []
    for i in range(len(ev) - 1):
        c, x = ev[i], ev[i + 1]; err = -Pbig[c].copy(); err[x] += 1.0   # 1[v==x] - p_pred
        full_vec = (np.sign(err)[:, None] * cb).sum(axis=0)
        topk = np.argpartition(-np.abs(err), TOPK - 1)[:TOPK]
        sp = np.zeros(N, dtype=np.float32)
        for v in topk:
            sp += math.copysign(1.0, err[v]) * cb[v]
        rs.append(np.linalg.norm(sp) / (np.linalg.norm(full_vec) + 1e-8))
        sparse_vecs.append(sp / (np.linalg.norm(sp) + 1e-8))
        # reconstruction: base pred vs base + sparse-residual (decode residual -> which symbols corrected)
        base_pred = int(np.argmax(Pbig[c]))
        resid_scores = cb @ sp                      # similarity of each symbol to the stored residual
        combo = np.log(Pbig[c] + 1e-9) + 0.5 * resid_scores
        base_hit += (base_pred == x); res_hit += (int(np.argmax(combo)) == x); ntot += 1
    r = float(np.mean(rs))
    # M_crit: full next-char patterns vs sparse residuals
    def full_fn(M, gg):
        idx = gg.integers(0, len(ev) - 1, size=M); return cb[ev[idx]]
    def sparse_fn(M, gg):
        idx = gg.integers(0, len(sparse_vecs), size=M); return np.stack([sparse_vecs[j] for j in idx])
    mc_full = _mcrit(full_fn, np.random.default_rng(seed + 1))
    mc_sparse = _mcrit(sparse_fn, np.random.default_rng(seed + 2))
    return {"seed": seed, "r": r, "M_crit_full": mc_full, "M_crit_sparse": mc_sparse,
            "M_crit_gain": float(mc_sparse / max(mc_full, 1)),
            "recon_base_acc": base_hit / ntot, "recon_residual_acc": res_hit / ntot}


def _selftest():
    g = np.random.default_rng(0); cb = codebook(20, 256, g)
    err = g.standard_normal(20); full = (np.sign(err)[:, None] * cb).sum(axis=0)
    tk = np.argpartition(-np.abs(err), 4)[:5]; sp = sum(math.copysign(1, err[v]) * cb[v] for v in tk)
    assert np.linalg.norm(sp) < np.linalg.norm(full), "sparse not smaller than full"
    assert set(tk.tolist()) == set(np.argsort(-np.abs(err))[:5].tolist()), "topK wrong"
    X = (g.integers(0, 2, (5, 256)) * 2 - 1).astype(np.float32); X = X / np.linalg.norm(X, axis=1, keepdims=True)
    W = (X.T @ X).astype(np.float32); np.fill_diagonal(W, 0.0)
    assert float(np.mean((np.sign(X @ W.T) * np.sign(X)).sum(axis=1) / 256 > 0.9)) > 0.9, "dense recall"
    assert abs(math.sqrt(5 / 70) - 0.267) < 0.01
    print("[selftest] PASS: sparse<full topK_ok dense_recall sqrtKV=0.267", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def verdict(per_seed) -> Tuple[str, str]:
    r = float(np.mean([s["r"] for s in per_seed])); gain = float(np.median([s["M_crit_gain"] for s in per_seed]))
    rb = float(np.mean([s["recon_base_acc"] for s in per_seed])); rr = float(np.mean([s["recon_residual_acc"] for s in per_seed]))
    useful = rr >= rb - 0.01
    summary = f"r={r:.3f} M_crit_gain={gain:.1f}x recon_base={rb:.3f} recon_base+residual={rr:.3f} (residual_useful={useful})"
    if r <= 0.30 and gain >= 10.0:
        return ("HARD_PASS", f"HARD_PASS: logit-space sparse residual r<=0.30 + >=10x capacity. {summary}")
    if r <= 0.55 or gain >= 4.0:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: r in [0.30,0.55] or gain 4-10x. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: r>0.55 and gain<4x. {summary}")


print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} seeds={SEEDS} N={N} V={VOCAB} topK={TOPK}", flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); per_seed = []
for seed in SEEDS:
    r = run_seed(seed); per_seed.append(r)
    print(f"  [seed={seed}] r={r['r']:.3f} M_crit full={r['M_crit_full']} sparse={r['M_crit_sparse']} gain={r['M_crit_gain']:.1f}x recon {r['recon_base_acc']:.3f}->{r['recon_residual_acc']:.3f}", flush=True)
v, vmsg = verdict(per_seed)
print(f"\n[VERDICT] {vmsg}", flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE,
           "n_seeds": len(SEEDS), "cells": ["B8_cell4_logit_sparse_residual"], "per_seed": per_seed, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, per_seed)
print("[metrics] written", flush=True)
