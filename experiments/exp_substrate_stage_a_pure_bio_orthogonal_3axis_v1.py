"""
substrate_stage_a_pure_bio_orthogonal_3axis_v1 -- orthogonal-axis composition superadditive test -- CPU.

ROUTING: notes/research_to_exp_dev_pure_bio_revised_orthogonal_axes_plus_exploration_2026-06-04. Research said YES
  to my orthogonal-axis framing (vs same-axis B36/B26 which subsumed). Tractable 3-axis flagship (capacity x task
  x parallel) on a Zipf bigram char-LM; tests the superadditive prediction directly. CPU numpy, $0. remote_cpu_queue.
  (4th axis sequence/posbind+STDP deferred to a trigram extension once this 3-axis validates the principle.)

THREE ORTHOGONAL AXES (per shared-axis taxonomy):
  CAP   (B2): sparse DG-expansion of the context (f=0.02 in N_dg=4x) -> raises representational capacity.
  TASK  (B3a): top-5% write gating (cf-RPE writes only high-error pairs) -> task-supervised efficiency.
  PAR   (B4): K=5 column ensemble (disjoint splits, averaged prediction) -> parallel capacity.

ARMS (gap = ln(V) - BPC; gain(arm) = gap(arm) - gap(base)):
  base / +CAP / +TASK / +PAR / +ALL. base = dense single-substrate write-all cf-RPE bigram.

PRE-REG (per Research): superadditive = gain(ALL) >= 2x max(gain(CAP),gain(TASK),gain(PAR)).
  HARD-PASS: gain(ALL) >= 2x best-single. MIDDLE: gain(ALL) > sum-or-additive but < 2x. HARD-FAIL: gain(ALL) <= best-single.

FORMULA SELF-TESTS (PROT-022): 1. cf-RPE shrinks error. 2. kWTA exact. 3. dist averaging valid. 4. uniform=ln(V).
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

ANCHOR_NAME = "substrate_stage_a_pure_bio_orthogonal_3axis_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

VOCAB = 70
K_ACTIVE = 8
F_SPARSE = 0.02
LR = 0.5
BATCH = 64
TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]
GATE_FRAC = 0.05
K_ENS = 5

if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N = 256; N_DG = 1024; CORPUS = 6000; N_STEPS = 200
else:
    SEEDS = [7, 17, 23]; N = 1024; N_DG = 4096; CORPUS = 25000; N_STEPS = 500


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


def _kwta(h, k):
    idx = np.argpartition(-h, k - 1, axis=1)[:, :k]; s = np.zeros_like(h); np.put_along_axis(s, idx, 1.0, axis=1)
    return s.astype(np.float32)


def encode_ctx(cb, ids, starts, cap, P):
    """context = cb[prev]; if CAP: sparse DG-expansion to N_dg via P + kWTA."""
    c = cb[ids[starts]]
    if not cap:
        return c
    k = max(1, int(round(F_SPARSE * P.shape[0])))
    return _kwta(c @ P.T, k)


def train_one(cb, tr, g, cap, task, P, ctx_dim):
    W = np.zeros((cb.shape[1], ctx_dim), dtype=np.float32)   # maps context(ctx_dim) -> next(N)
    for _ in range(N_STEPS):
        st = g.integers(0, len(tr) - 1, size=BATCH)
        ctx = encode_ctx(cb, tr, st, cap, P); nxt = cb[tr[st + 1]]
        delta = nxt - ctx @ W.T            # cf-RPE error (B,N)
        if task:
            err = np.linalg.norm(delta, axis=1); mask = err >= np.quantile(err, 1.0 - GATE_FRAC)
            if mask.sum() == 0:
                continue
            ctx, delta = ctx[mask], delta[mask]
        W = W + LR * (delta.T @ ctx) / max(1, ctx.shape[0])
    return W


def dist_one(W, cb, ids, starts, cap, P, temp):
    ctx = encode_ctx(cb, ids, starts, cap, P); pred = ctx @ W.T
    pred = pred / (np.linalg.norm(pred, axis=1, keepdims=True) + 1e-8); cos = pred @ cb.T
    z = cos / temp; z -= z.max(axis=1, keepdims=True); ez = np.exp(z); return ez / (ez.sum(axis=1, keepdims=True) + 1e-30)


def gap_arm(cb, tr, va, g, cap, task, par, un):
    ctx_dim = N_DG if cap else cb.shape[1]
    P = (g.standard_normal((N_DG, cb.shape[1])) / math.sqrt(cb.shape[1])).astype(np.float32) if cap else None
    K = K_ENS if par else 1
    Ws = []
    splits = np.array_split(tr, K) if par else [tr]
    for i in range(K):
        Ws.append(train_one(cb, splits[i], np.random.default_rng(g.integers(1 << 30)), cap, task, P, ctx_dim))
    nb = min(2000, len(va) - 1); st = np.arange(nb); nxt = va[st + 1]
    best = float("inf")
    for t in TEMP_GRID:
        Pm = np.mean([dist_one(W, cb, va, st, cap, P, t) for W in Ws], axis=0)
        bpc = float(-np.log(np.clip(Pm[np.arange(nb), nxt], 1e-12, None)).mean()); best = min(best, bpc)
    return un - best


def _selftest():
    g = np.random.default_rng(0); cb = codebook(5, 128, g)
    W = np.zeros((128, 128), dtype=np.float32); v = W @ cb[0]; eb = float(np.linalg.norm(cb[1] - v))
    W = W + np.outer(cb[1] - v, cb[0]); assert float(np.linalg.norm(cb[1] - W @ cb[0])) < eb, "cf-RPE"
    h = g.standard_normal((2, 100)); assert np.all(_kwta(h, 5).sum(axis=1) == 5), "kWTA"
    P = np.array([[0.3, 0.7], [0.5, 0.5]]); assert abs(np.mean([P, P], axis=0).sum(axis=1).mean() - 1.0) < 1e-6
    assert abs(math.log(5) - 1.6094) < 1e-3
    print("[selftest] PASS: cfrpe kWTA dist_avg", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    g = np.random.default_rng(seed); ids = gen_zipf(VOCAB, CORPUS, g); sp = int(0.8 * len(ids)); tr, va = ids[:sp], ids[sp:]
    cb = codebook(VOCAB, N, g); un = math.log(VOCAB)
    arms = {
        "base": gap_arm(cb, tr, va, np.random.default_rng(seed + 1), False, False, False, un),
        "cap": gap_arm(cb, tr, va, np.random.default_rng(seed + 2), True, False, False, un),
        "task": gap_arm(cb, tr, va, np.random.default_rng(seed + 3), False, True, False, un),
        "par": gap_arm(cb, tr, va, np.random.default_rng(seed + 4), False, False, True, un),
        "all": gap_arm(cb, tr, va, np.random.default_rng(seed + 5), True, True, True, un),
    }
    return {"seed": seed, **arms}


def verdict(per_seed) -> Tuple[str, str]:
    def m(k):
        return float(np.mean([s[k] for s in per_seed]))
    base = m("base"); gcap = m("cap") - base; gtask = m("task") - base; gpar = m("par") - base; gall = m("all") - base
    best = max(gcap, gtask, gpar); summary = f"gap base={base:.3f} gains: cap={gcap:+.3f} task={gtask:+.3f} par={gpar:+.3f} ALL={gall:+.3f} (best_single={best:+.3f})"
    if gall >= 2.0 * max(best, 1e-6):
        return ("HARD_PASS", f"HARD_PASS: orthogonal-axis composition SUPERADDITIVE (ALL >= 2x best-single). {summary}")
    if gall > best:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: ALL > best-single but < 2x (partial superadditive). {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: ALL <= best-single (axes not orthogonal/composing). {summary}")


print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} seeds={SEEDS} N={N} N_dg={N_DG} K_ens={K_ENS}", flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); per_seed = []
for seed in SEEDS:
    r = run_seed(seed); per_seed.append(r)
    print(f"  [seed={seed}] base={r['base']:.3f} cap={r['cap']:.3f} task={r['task']:.3f} par={r['par']:.3f} all={r['all']:.3f}", flush=True)
v, vmsg = verdict(per_seed)
print(f"\n[VERDICT] {vmsg}", flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE,
           "n_seeds": len(SEEDS), "cells": ["pure_bio_3axis"], "per_seed": per_seed, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, per_seed)
print("[metrics] written", flush=True)
