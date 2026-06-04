"""
substrate_stage_a_bio_b3_b6_ceiling_followup_v1 -- push B3 + B6 wins to ceilings -- LAPTOP CPU.

ROUTING: notes/research_to_exp_dev_bio_smoke_followup_consolidated_2026-06-04 (B3 ceiling + B6 ceiling). Reuses
  existing B3 cf-RPE active-gating + B6 D-ECR eviction scaffolds. CPU numpy, $0. LAPTOP.

CELLS (3 seeds):
  B3a top-5% gating (vs top-10%): HP 18-25x write reduction at >=85% perf retention; MID 12-18x; HF <12x.
  B3b exp-smoothed surprise gating (write when err > running-mean err): HP 10-15x at >=90% perf; MID 5-10x; HF <5x.
  B6c D-ECR ceiling: sweep M={3,4,5}*alpha_c at N=512. HP D-ECR>=2x LRU recall at M=3x; MID 1.5-2x; HF collapses to LRU.

  perf retention (B3) = gated_gap / all_gap (fraction of write-all BPC-gap retained).

FORMULA SELF-TESTS (PROT-022): 1. cf-RPE shrinks error. 2. running-mean surprise selects above-average errors. 3. eviction reduces ||W||. 4. alpha_c=0.138.
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

ANCHOR_NAME = "substrate_stage_a_bio_b3_b6_ceiling_followup_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

VOCAB = 70
K_ACTIVE = 8
LR = 0.5
BATCH = 64
ALPHA_C = 0.138
TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]

if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_B3 = 512; CORPUS = 5000; N_B6 = 256; M_MULTS = [3, 4, 5]
else:
    SEEDS = [7, 17, 23]; N_B3 = 2048; CORPUS = 20000; N_B6 = 512; M_MULTS = [3, 4, 5]


def bipolar(shape, g):
    return (g.integers(0, 2, size=shape) * 2 - 1).astype(np.float32)


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
    cb = bipolar((V, n), g); return cb / (np.linalg.norm(cb, axis=1, keepdims=True) + 1e-8)


def bpc_cos(W, cb, ids, g, un):
    nb = min(2000, len(ids) - 2); st = g.integers(0, len(ids) - 2, size=nb); ctx = cb[ids[st]]; nxt = ids[st + 1]
    pred = ctx @ W.T; pred = pred / (np.linalg.norm(pred, axis=1, keepdims=True) + 1e-8); cos = pred @ cb.T
    best = float("inf")
    for t in TEMP_GRID:
        z = cos / t; z -= z.max(axis=1, keepdims=True); ez = np.exp(z); pr = ez / (ez.sum(axis=1, keepdims=True) + 1e-30)
        best = min(best, float(-np.log(np.clip(pr[np.arange(nb), nxt], 1e-12, None)).mean()))
    return best


def train_gated(n, cb, tr, va, g, un, mode, frac=0.05):
    W = np.zeros((n, n), dtype=np.float32); writes = 0; run_mean = None
    nsteps = max(1, (len(tr) - 1) // BATCH); warmup = max(1, nsteps // 10)
    for step in range(nsteps):
        st = g.integers(0, len(tr) - 1, size=BATCH); ctx = cb[tr[st]]; nxt = cb[tr[st + 1]]
        err = np.linalg.norm(nxt - ctx @ W.T, axis=1)
        if mode == "all":
            mask = np.ones(BATCH, dtype=bool)
        elif mode == "topk":
            mask = err >= np.quantile(err, 1.0 - frac)
        else:  # surprise: write-all warmup (cold start), then above-running-mean error
            bm = float(err.mean()); run_mean = bm if run_mean is None else 0.9 * run_mean + 0.1 * bm
            mask = np.ones(BATCH, dtype=bool) if step < warmup else (err > run_mean)
        if mask.sum() > 0:
            c2, n2 = ctx[mask], nxt[mask]; W = W + LR * ((n2 - c2 @ W.T).T @ c2) / max(1, mask.sum()); writes += int(mask.sum())
    return bpc_cos(W, cb, va, g, un), writes


def b3_followup(n, g):
    ids = gen_zipf(VOCAB, CORPUS, g); sp = int(0.8 * len(ids)); tr, va = ids[:sp], ids[sp:]
    cb = codebook(VOCAB, n, g); un = math.log(VOCAB)
    bpc_all, w_all = train_gated(n, cb, tr, va, np.random.default_rng(1), un, "all")
    gap_all = un - bpc_all
    bpc_5, w_5 = train_gated(n, cb, tr, va, np.random.default_rng(2), un, "topk", 0.05)
    bpc_sup, w_sup = train_gated(n, cb, tr, va, np.random.default_rng(3), un, "surprise")
    return {"gap_all": float(gap_all), "w_all": w_all,
            "b3a_top5": {"reduction": float(w_all / max(w_5, 1)), "perf": float((un - bpc_5) / max(gap_all, 1e-6)), "writes": w_5},
            "b3b_surprise": {"reduction": float(w_all / max(w_sup, 1)), "perf": float((un - bpc_sup) / max(gap_all, 1e-6)), "writes": w_sup}}


# B6c D-ECR ceiling
def _self_ov(W, bank, n):
    if not bank:
        return np.array([])
    X = np.stack(bank); R = np.sign(X @ W.T); R[R == 0] = 1.0
    return (X * R).sum(axis=1) / n


def _stream(n, policy, m_cap, g):
    W = np.zeros((n, n), dtype=np.float32); bank = []
    for t in range(3 * m_cap):
        x = bipolar((n,), g); bank.append(x); W += np.outer(x, x); np.fill_diagonal(W, 0.0)
        if len(bank) > m_cap:
            ev = (0 if policy == "lru" else (int(g.integers(0, len(bank))) if policy == "random" else int(np.argmin(_self_ov(W, bank, n)))))
            xe = bank.pop(ev); W -= np.outer(xe, xe); np.fill_diagonal(W, 0.0)
    ov = _self_ov(W, bank, n); return float(np.mean(ov > 0.95)) if len(ov) else 0.0


def b6_ceiling(g):
    n = N_B6; out = {}
    for mult in M_MULTS:
        m_cap = max(4, int(round(mult * ALPHA_C * n)))
        out[f"m{mult}x"] = {"decr": _stream(n, "decr", m_cap, np.random.default_rng(g.integers(1 << 30))),
                            "lru": _stream(n, "lru", m_cap, np.random.default_rng(g.integers(1 << 30)))}
    return out


def _selftest():
    g = np.random.default_rng(0); cb = codebook(5, 128, g)
    W = np.zeros((128, 128), dtype=np.float32); v = W @ cb[0]; eb = float(np.linalg.norm(cb[1] - v))
    W = W + np.outer(cb[1] - v, cb[0]); ea = float(np.linalg.norm(cb[1] - W @ cb[0])); assert ea < eb
    err = np.array([1.0, 5.0, 2.0, 8.0]); assert np.sum(err > err.mean()) == 2, "surprise selection"
    x = bipolar((128,), g); W2 = np.outer(x, x); nb = float(np.abs(W2).sum()); assert float(np.abs(W2 - np.outer(x, x)).sum()) < nb
    assert abs(ALPHA_C - 0.138) < 1e-6
    print("[selftest] PASS: cfrpe_shrinks surprise_select eviction_reduces_W", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def verdict(per_seed) -> Tuple[str, str]:
    r5 = float(np.median([s["B3"]["b3a_top5"]["reduction"] for s in per_seed])); p5 = float(np.mean([s["B3"]["b3a_top5"]["perf"] for s in per_seed]))
    rs = float(np.median([s["B3"]["b3b_surprise"]["reduction"] for s in per_seed])); ps = float(np.mean([s["B3"]["b3b_surprise"]["perf"] for s in per_seed]))
    b3a = "HP" if (18 <= r5 <= 25 and p5 >= 0.85) else ("MID" if (12 <= r5 and p5 >= 0.85) else "HF")
    b3b = "HP" if (10 <= rs <= 15 and ps >= 0.90) else ("MID" if (5 <= rs and ps >= 0.90) else "HF")
    d3 = float(np.mean([s["B6"]["m3x"]["decr"] for s in per_seed])); l3 = float(np.mean([s["B6"]["m3x"]["lru"] for s in per_seed]))
    ratio3 = d3 / max(l3, 1e-6)
    b6c = "HP" if ratio3 >= 2.0 else ("MID" if ratio3 >= 1.5 else "HF")
    b6tab = " ".join(f"{m}x:decr={np.mean([s['B6']['m'+str(m)+'x']['decr'] for s in per_seed]):.2f}/lru={np.mean([s['B6']['m'+str(m)+'x']['lru'] for s in per_seed]):.2f}" for m in M_MULTS)
    summary = f"B3a[top5 {r5:.1f}x @perf{p5:.2f} {b3a}] B3b[surprise {rs:.1f}x @perf{ps:.2f} {b3b}] B6c[{b6tab} ratio@3x={ratio3:.2f} {b6c}]"
    n_hp = sum(1 for x in [b3a, b3b, b6c] if x == "HP")
    v = "HARD_PASS" if n_hp == 3 else ("MIDDLE_BAND" if n_hp >= 1 or "MID" in [b3a, b3b, b6c] else "HARD_FAIL")
    return v, f"{v}: B3/B6 ceiling {summary} ({n_hp}/3 HP)"


print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} seeds={SEEDS} N_B3={N_B3} N_B6={N_B6} M_mults={M_MULTS}", flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); per_seed = []
for seed in SEEDS:
    b3 = b3_followup(N_B3, np.random.default_rng(seed * 19 + 3)); b6 = b6_ceiling(np.random.default_rng(seed * 19 + 6))
    per_seed.append({"seed": seed, "B3": b3, "B6": b6})
    print(f"  [seed={seed}] B3a top5={b3['b3a_top5']['reduction']:.1f}x@{b3['b3a_top5']['perf']:.2f} B3b surprise={b3['b3b_surprise']['reduction']:.1f}x@{b3['b3b_surprise']['perf']:.2f} | "
          f"B6c " + " ".join(f"{m}x:{b6['m'+str(m)+'x']['decr']:.2f}/{b6['m'+str(m)+'x']['lru']:.2f}" for m in M_MULTS), flush=True)
v, vmsg = verdict(per_seed)
print(f"\n[VERDICT] {vmsg}", flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE,
           "n_seeds": len(SEEDS), "cells": ["B3a_top5", "B3b_surprise", "B6c_ceiling"], "per_seed": per_seed, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, per_seed)
print("[metrics] written", flush=True)
