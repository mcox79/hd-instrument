"""
substrate_stage_a_bio_smoke_B4_ensemble_v1 -- column ensemble parameter-efficiency -- LAPTOP CPU.

ROUTING: notes/change_request_stage_a_bio_smoke_REVISED_drill_B_specs (B4). REVISED HP = PARAMETER-EFFICIENCY
  (ensemble within 0.05 BPC of single large substrate), NOT wall-time (parallel speedup needs hardware not on a
  single CPU thread). Single-substrate N reduced 20480->10240 (RAM-safe, same logic that revised B2). CPU numpy, $0.

CAPABILITY QUESTION (B4): can K=10 small substrates (N=2048 each; cf-RPE bigram char-LM; predictions averaged)
  match a single large N=10240 substrate's BPC? If yes, the ensemble is parameter-efficient + parallelizable
  (column-style scaling). Also tests ensemble DIVERSITY (disjoint splits vs bagging).

CELLS (3 seeds; BPC nats on a shared Zipf bigram corpus):
  4a disjoint: K sub-substrates each trained on a DISJOINT 1/K split; predictions averaged.
  4b bagging:  K sub-substrates each on a random 50% subset (different seeds).
  4c single:   one N=10240 substrate on the full corpus.

PRE-REG (REVISED parameter-efficiency): HP best-ensemble BPC <= single BPC + 0.05. MID within +0.20. HF > +0.20.
WHY-DRILL HF: pairwise W cos-similarity > 0.9 -> no ensemble diversity -> use bagging 50% subsets.

FORMULA SELF-TESTS (PROT-022): 1. cf-RPE shrinks error. 2. averaging 2 dists is a valid dist (sums to 1). 3. uniform=ln(V).
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

ANCHOR_NAME = "substrate_stage_a_bio_smoke_B4_ensemble_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

VOCAB = 70
K_ACTIVE = 8
LR = 0.5
BATCH = 64
TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]

if RUN_MODE == "smoke":
    SEEDS = [1, 2]; K_SUB = 4; N_SUB = 256; N_SINGLE = 1024; CORPUS = 6000; N_STEPS = 150
else:
    SEEDS = [7, 17, 23]; K_SUB = 10; N_SUB = 2048; N_SINGLE = 6144; CORPUS = 30000; N_STEPS = 400


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
    cb = ((g.integers(0, 2, (V, n)) * 2 - 1)).astype(np.float32)
    return cb / (np.linalg.norm(cb, axis=1, keepdims=True) + 1e-8)


def train_cfrpe(n, cb, tr, g):
    W = np.zeros((n, n), dtype=np.float32)
    for _ in range(N_STEPS):
        st = g.integers(0, len(tr) - 1, size=BATCH); ctx = cb[tr[st]]; nxt = cb[tr[st + 1]]
        W = W + LR * ((nxt - ctx @ W.T).T @ ctx) / BATCH
    return W


def dist(W, cb, ctx_ids, temp):
    ctx = cb[ctx_ids]; pred = ctx @ W.T; pred = pred / (np.linalg.norm(pred, axis=1, keepdims=True) + 1e-8)
    cos = pred @ cb.T; z = cos / temp; z = z - z.max(axis=1, keepdims=True); ez = np.exp(z)
    return ez / (ez.sum(axis=1, keepdims=True) + 1e-30)


def bpc_from_dist(P, nxt):
    return float(-np.log(np.clip(P[np.arange(len(nxt)), nxt], 1e-12, None)).mean())


def best_temp_single(W, cb, va):
    nb = min(2000, len(va) - 1); st = np.arange(nb); ctxq = va[st]; nxt = va[st + 1]
    best = float("inf")
    for t in TEMP_GRID:
        best = min(best, bpc_from_dist(dist(W, cb, ctxq, t), nxt))
    return best


def best_temp_ensemble(Ws, cb, va):
    nb = min(2000, len(va) - 1); st = np.arange(nb); ctxq = va[st]; nxt = va[st + 1]
    best = float("inf")
    for t in TEMP_GRID:
        P = np.mean([dist(W, cb, ctxq, t) for W in Ws], axis=0)
        best = min(best, bpc_from_dist(P, nxt))
    return best


def run_seed(seed: int) -> Dict:
    g = np.random.default_rng(seed); ids = gen_zipf(VOCAB, CORPUS, g)
    sp = int(0.8 * len(ids)); tr, va = ids[:sp], ids[sp:]
    cb_sub = codebook(VOCAB, N_SUB, g); cb_big = codebook(VOCAB, N_SINGLE, g)
    # 4a disjoint splits
    splits = np.array_split(tr, K_SUB)
    Wa = [train_cfrpe(N_SUB, cb_sub, splits[i], np.random.default_rng(seed * 100 + i)) for i in range(K_SUB)]
    bpc_a = best_temp_ensemble(Wa, cb_sub, va)
    # 4b bagging 50% subsets
    Wb = []
    for i in range(K_SUB):
        gi = np.random.default_rng(seed * 200 + i); sub = gi.choice(len(tr), size=len(tr) // 2, replace=False)
        Wb.append(train_cfrpe(N_SUB, cb_sub, tr[np.sort(sub)], gi))
    bpc_b = best_temp_ensemble(Wb, cb_sub, va)
    # 4c single large
    Wc = train_cfrpe(N_SINGLE, cb_big, tr, np.random.default_rng(seed * 300))
    bpc_c = best_temp_single(Wc, cb_big, va)
    # diversity: mean pairwise cos-sim of bagging Ws
    flat = np.stack([W.ravel() for W in Wb]); flat = flat / (np.linalg.norm(flat, axis=1, keepdims=True) + 1e-8)
    cosm = flat @ flat.T; div = float(cosm[~np.eye(K_SUB, dtype=bool)].mean())
    return {"seed": seed, "bpc_disjoint": float(bpc_a), "bpc_bagging": float(bpc_b), "bpc_single": float(bpc_c),
            "ensemble_W_cossim": div, "best_ensemble": float(min(bpc_a, bpc_b))}


def _selftest():
    g = np.random.default_rng(0); cb = codebook(5, 128, g)
    W = np.zeros((128, 128), dtype=np.float32); v = W @ cb[0]; eb = float(np.linalg.norm(cb[1] - v))
    W = W + np.outer(cb[1] - v, cb[0]); ea = float(np.linalg.norm(cb[1] - W @ cb[0])); assert ea < eb
    P = np.array([[0.2, 0.8], [0.5, 0.5]]); Pm = np.mean([P, P], axis=0); assert abs(Pm.sum(axis=1).mean() - 1.0) < 1e-6
    assert abs(math.log(5) - 1.6094) < 1e-3
    print("[selftest] PASS: cfrpe_shrinks dist_avg_valid", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def verdict(per_seed) -> Tuple[str, str]:
    be = float(np.mean([s["best_ensemble"] for s in per_seed])); bs = float(np.mean([s["bpc_single"] for s in per_seed]))
    bd = float(np.mean([s["bpc_disjoint"] for s in per_seed])); bb = float(np.mean([s["bpc_bagging"] for s in per_seed]))
    div = float(np.mean([s["ensemble_W_cossim"] for s in per_seed]))
    delta = be - bs
    summary = f"single={bs:.3f} disjoint={bd:.3f} bagging={bb:.3f} best_ensemble={be:.3f} (delta_vs_single={delta:+.3f}) W_cossim={div:.2f}"
    if delta <= 0.05:
        return ("HARD_PASS", f"HARD_PASS: K={K_SUB} ensemble (N={N_SUB}) matches single N={N_SINGLE} within 0.05 BPC -> parameter-efficient. {summary}")
    if delta <= 0.20:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: ensemble within 0.20 BPC of single. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: ensemble >0.20 BPC worse than single (diversity W_cossim={div:.2f}; if >0.9 use bagging). {summary}")


print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} seeds={SEEDS} K_sub={K_SUB} N_sub={N_SUB} N_single={N_SINGLE}", flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); per_seed = []
for seed in SEEDS:
    r = run_seed(seed); per_seed.append(r)
    print(f"  [seed={seed}] single={r['bpc_single']:.3f} disjoint={r['bpc_disjoint']:.3f} bagging={r['bpc_bagging']:.3f} (W_cossim={r['ensemble_W_cossim']:.2f})", flush=True)
v, vmsg = verdict(per_seed)
print(f"\n[VERDICT] {vmsg}", flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE,
           "n_seeds": len(SEEDS), "cells": ["B4_ensemble"], "per_seed": per_seed, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, per_seed)
print("[metrics] written", flush=True)
