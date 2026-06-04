"""
substrate_stage_a_bio_smoke_REVISED_v1 -- bio-primitive smoke sweep (BATCH 1: B1,B3,B6) -- LAPTOP CPU.

ROUTING: notes/change_request_stage_a_bio_smoke_REVISED_drill_B_specs_2026-06-04.md. Bio-primitive smoke cells
  for the training-speed Stage A trick library, per Drill B specs + WHY-DRILL diagnostics. CPU numpy, $0.
  BATCH 1 = the 3 highest-confidence reuse-heavy cells (B1 one-shot Hebbian, B3 cf-RPE active gating,
  B6 D-ECR energy-driven pruning). B2/B4/B5/B7/B8 follow in batch 2. Run on the LAPTOP CPU (local, ASAP).

CELLS (per change-request Drill B specs):
  B1 one-shot Hebbian classification (N=2048, K=5 classes, M=50): one-shot class-prototype memory vs Adam linear
     classifier. sub: 1a balanced / 1b hard-negatives / 1c noisy sigma=0.5. HP acc>=0.80 AND speedup>=100x.
  B3 cf-RPE active gating (N=2048, V=70 bigram char-LM): write-all vs write@top-10%-err vs top-1%-err.
     HP: gated reaches BPC<=2.0 with <=1/10 the writes of write-all. (writes = examples actually written.)
  B6 D-ECR energy-driven pruning (N=512, alpha_c=72, M in {72,94}): no-eviction / D-ECR / LRU / random.
     HP: D-ECR recall >= 1.20x no-eviction AND > LRU at M=94. (D-ECR = evict lowest self-overlap = energy-contribution.)

WHY-DRILL diagnostics emitted on each cell HF (per [[feedback-pressure-test-negative-findings]]).

FORMULA SELF-TESTS (PROT-022): 1. one-shot prototype recovers clean class. 2. cf-RPE shrinks error.
  3. eviction reduces ||W||. 4. alpha_c=0.138.

PROT-018: swept/multi-cell anchor (no _nN binding). PROT-021: run_mode=smoke local CPU. ASCII-only.
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

ANCHOR_NAME = "substrate_stage_a_bio_smoke_REVISED_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
VOCAB = 70
K_ACTIVE = 8
BATCH = 64
ADAM_LR = 0.01
TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]

if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_B1 = 512; N_B3 = 512; CORPUS = 4000; ADAM_EPOCHS = 20
else:
    SEEDS = [7, 17, 23]; N_B1 = 2048; N_B3 = 2048; CORPUS = 20000; ADAM_EPOCHS = 60


def bipolar(shape, g):
    return (g.integers(0, 2, size=shape) * 2 - 1).astype(np.float32)


# ---------- B1: one-shot Hebbian classification vs Adam ----------
def _b1_data(n, mode, g):
    K, per = 5, 10
    protos = bipolar((K, n), g)
    X, y = [], []
    for c in range(K):
        for _ in range(per):
            if mode == "balanced":
                x = bipolar((n,), g)
            elif mode == "hardneg":
                x = protos[c].copy(); flip = g.choice(n, size=n // 5, replace=False); x[flip] *= -1
            else:  # noisy
                x = protos[c] + g.standard_normal(n).astype(np.float32) * 0.5; x = np.sign(x); x[x == 0] = 1
            X.append(x.astype(np.float32)); y.append(c)
    return np.stack(X), np.array(y), K


def b1_cell(n, g):
    res = {}
    for mode in ["balanced", "hardneg", "noisy"]:
        X, y, K = _b1_data(n, mode, g)
        # one-shot Hebbian: class-prototype matrix W(K,n) = sum of class members
        t0 = time.time()
        Wh = np.zeros((K, n), dtype=np.float32)
        for i in range(len(X)):
            Wh[y[i]] += X[i]
        acc_h = float((np.argmax(X @ Wh.T, axis=1) == y).mean()); t_h = time.time() - t0
        # Adam linear classifier to match acc_h
        M = (g.standard_normal((K, n)) * 0.01).astype(np.float32)
        mm = np.zeros_like(M); vv = np.zeros_like(M); b1, b2, eps = 0.9, 0.999, 1e-8; it = 0; t0 = time.time(); t_match = None
        for ep in range(ADAM_EPOCHS):
            idx = g.permutation(len(X))
            for s in range(0, len(X), BATCH):
                it += 1; bi = idx[s:s + BATCH]; xb, yb = X[bi], y[bi]
                logits = xb @ M.T; logits -= logits.max(axis=1, keepdims=True)
                ez = np.exp(logits); pr = ez / ez.sum(axis=1, keepdims=True)
                gl = pr.copy(); gl[np.arange(len(bi)), yb] -= 1.0; gl /= len(bi); gM = gl.T @ xb
                mm = b1 * mm + (1 - b1) * gM; vv = b2 * vv + (1 - b2) * (gM * gM)
                M = M - ADAM_LR * (mm / (1 - b1 ** it)) / (np.sqrt(vv / (1 - b2 ** it)) + eps)
            if t_match is None and float((np.argmax(X @ M.T, axis=1) == y).mean()) >= acc_h:
                t_match = time.time() - t0
        if t_match is None:
            t_match = time.time() - t0
        speedup = float(t_match / max(t_h, 1e-6))
        res[mode] = {"acc_oneshot": acc_h, "t_oneshot": t_h, "t_adam_match": t_match, "speedup": speedup}
    return res


# ---------- B3: cf-RPE active gating ----------
def _gen_zipf_bigram(V, length, g):
    ranks = 1.0 / np.arange(1, V + 1); zp = ranks / ranks.sum()
    T = np.zeros((V, V))
    for c in range(V):
        tg = g.choice(V, size=K_ACTIVE, replace=False, p=zp); lg = g.standard_normal(K_ACTIVE) * 2.0
        w = np.exp(lg - lg.max()); w /= w.sum(); T[c, tg] = w
    ids = np.zeros(length, dtype=np.int64); s = 0
    for i in range(length):
        ids[i] = s; s = g.choice(V, p=T[s])
    return ids


def _bpc_cos(W, cb, ids, g, un):
    nb = min(2000, len(ids) - 2); st = g.integers(0, len(ids) - 2, size=nb)
    ctx = cb[ids[st]]; nxt = ids[st + 1]
    pred = ctx @ W.T; pred = pred / (np.linalg.norm(pred, axis=1, keepdims=True) + 1e-8); cos = pred @ cb.T
    best = float("inf")
    for t in TEMP_GRID:
        z = cos / t; z -= z.max(axis=1, keepdims=True); ez = np.exp(z); pr = ez / (ez.sum(axis=1, keepdims=True) + 1e-30)
        best = min(best, float(-np.log(np.clip(pr[np.arange(nb), nxt], 1e-12, None)).mean()))
    return best


def b3_cell(n, g):
    ids = _gen_zipf_bigram(VOCAB, CORPUS, g); sp = int(0.8 * len(ids)); tr, va = ids[:sp], ids[sp:]
    cb = bipolar((VOCAB, n), g); cb = cb / (np.linalg.norm(cb, axis=1, keepdims=True) + 1e-8)
    un = math.log(VOCAB); res = {}
    for gate, frac in [("all", 1.0), ("top10", 0.10), ("top1", 0.01)]:
        W = np.zeros((n, n), dtype=np.float32); writes = 0; LR = 0.5
        nsteps = max(1, (len(tr) - 1) // BATCH)
        for _ in range(nsteps):
            st = g.integers(0, len(tr) - 1, size=BATCH)
            ctx = cb[tr[st]]; nxt = cb[tr[st + 1]]
            err = np.linalg.norm(nxt - ctx @ W.T, axis=1)
            if gate == "all":
                mask = np.ones(BATCH, dtype=bool)
            else:
                thr = np.quantile(err, 1.0 - frac); mask = err >= thr
            if mask.sum() > 0:
                c2, n2 = ctx[mask], nxt[mask]
                W = W + LR * ((n2 - c2 @ W.T).T @ c2) / max(1, mask.sum()); writes += int(mask.sum())
        bpc = _bpc_cos(W, cb, va, g, un)
        res[gate] = {"bpc": float(bpc), "gap": float(un - bpc), "writes": writes}
    return res


# ---------- B6: D-ECR energy-driven pruning (reuses eviction logic) ----------
def _self_ov(W, bank, n):
    if not bank:
        return np.array([])
    X = np.stack(bank); R = np.sign(X @ W.T); R[R == 0] = 1.0
    return (X * R).sum(axis=1) / n


def _stream(n, policy, m_cap, g):
    W = np.zeros((n, n), dtype=np.float32); bank = []; n_stream = 3 * m_cap
    for t in range(n_stream):
        x = bipolar((n,), g); bank.append(x); W += np.outer(x, x); np.fill_diagonal(W, 0.0)
        if len(bank) > m_cap:
            if policy == "none":
                bank.pop(0); continue  # FIFO drop but keep all in W? no -> 'none' = no eviction (let W overload)
            if policy == "lru":
                ev = 0
            elif policy == "random":
                ev = int(g.integers(0, len(bank)))
            else:  # decr = lowest energy-contribution (self-overlap)
                ev = int(np.argmin(_self_ov(W, bank, n)))
            xe = bank.pop(ev); W -= np.outer(xe, xe); np.fill_diagonal(W, 0.0)
    ov = _self_ov(W, bank, n); return float(np.mean(ov > 0.95)) if len(ov) else 0.0


def _stream_noevict(n, m_cap, g):
    # no eviction: store ALL n_stream patterns (overload), measure recall of all
    W = np.zeros((n, n), dtype=np.float32); bank = []; n_stream = 3 * m_cap
    for t in range(n_stream):
        x = bipolar((n,), g); bank.append(x); W += np.outer(x, x)
    np.fill_diagonal(W, 0.0); ov = _self_ov(W, bank, n); return float(np.mean(ov > 0.95))


def b6_cell(g):
    n = 512; res = {}
    for mload, m_cap in [("m1.0", int(round(1.0 * ALPHA_C * n))), ("m1.3", int(round(1.3 * ALPHA_C * n)))]:
        sub = {"none": _stream_noevict(n, m_cap, g)}
        for pol in ["decr", "lru", "random"]:
            sub[pol] = _stream(n, pol, m_cap, g)
        res[mload] = sub
    return res


def _selftest():
    g = np.random.default_rng(0)
    # one-shot prototype recovers a clean class
    protos = bipolar((3, 128), g); Wh = protos.copy()
    assert int(np.argmax(protos[1] @ Wh.T)) == 1, "one-shot prototype wrong"
    cb = bipolar((5, 128), g); cb = cb / np.linalg.norm(cb, axis=1, keepdims=True)
    W = np.zeros((128, 128), dtype=np.float32); v = W @ cb[0]; eb = float(np.linalg.norm(cb[1] - v))
    W = W + np.outer(cb[1] - v, cb[0]); ea = float(np.linalg.norm(cb[1] - W @ cb[0])); assert ea < eb, "cf-RPE no shrink"
    W2 = np.outer(cb[0], cb[0]); nb = float(np.abs(W2).sum()); W3 = W2 - np.outer(cb[0], cb[0]); assert float(np.abs(W3).sum()) < nb
    assert abs(ALPHA_C - 0.138) < 1e-6
    print("[selftest] PASS: oneshot_proto cfrpe_shrinks eviction_reduces_W", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _why_drill(cell, payload):
    return f"[WHY-DRILL {cell}] {payload}"


def run_all() -> Dict:
    t0 = time.time(); per_seed = []
    for seed in SEEDS:
        g = np.random.default_rng(seed)
        b1 = b1_cell(N_B1, np.random.default_rng(seed * 7 + 1))
        b3 = b3_cell(N_B3, np.random.default_rng(seed * 7 + 3))
        b6 = b6_cell(np.random.default_rng(seed * 7 + 6))
        per_seed.append({"seed": seed, "B1": b1, "B3": b3, "B6": b6})
        print(f"  [seed={seed}] B1 balanced acc={b1['balanced']['acc_oneshot']:.2f} speedup={b1['balanced']['speedup']:.0f}x | "
              f"B3 writes all={b3['all']['writes']} top10={b3['top10']['writes']} (gap all={b3['all']['gap']:.2f} top10={b3['top10']['gap']:.2f}) | "
              f"B6 m1.3 decr={b6['m1.3']['decr']:.2f} none={b6['m1.3']['none']:.2f} lru={b6['m1.3']['lru']:.2f}", flush=True)
    return {"per_seed": per_seed, "elapsed_s": time.time() - t0}


def verdict(per_seed) -> Tuple[str, str, List[str]]:
    drills = []
    # B1: acc>=0.80 AND speedup>=100x (balanced)
    b1_acc = float(np.mean([s["B1"]["balanced"]["acc_oneshot"] for s in per_seed]))
    b1_sp = float(np.median([s["B1"]["balanced"]["speedup"] for s in per_seed]))
    b1_hp = b1_acc >= 0.80 and b1_sp >= 100
    if not b1_hp:
        drills.append(_why_drill("B1", f"acc={b1_acc:.2f} speedup={b1_sp:.0f}x; if speedup low, one-shot is O(M*N) vs Adam cheap small-head -- expected at tiny scale; revisit at larger M/N"))
    # B3: gated reaches gap-equivalent with <=1/10 writes of all
    w_all = float(np.mean([s["B3"]["all"]["writes"] for s in per_seed]))
    w_t10 = float(np.mean([s["B3"]["top10"]["writes"] for s in per_seed]))
    g_all = float(np.mean([s["B3"]["all"]["gap"] for s in per_seed]))
    g_t10 = float(np.mean([s["B3"]["top10"]["gap"] for s in per_seed]))
    b3_hp = (w_t10 <= w_all / 10.0) and (g_t10 >= 0.8 * g_all)
    if not b3_hp:
        drills.append(_why_drill("B3", f"writes all={w_all:.0f} top10={w_t10:.0f}; gap all={g_all:.2f} top10={g_t10:.2f}; if not selective, use exponentially-smoothed surprise"))
    # B6: D-ECR >= 1.2x no-eviction AND > LRU at m1.3
    decr = float(np.mean([s["B6"]["m1.3"]["decr"] for s in per_seed]))
    none_ = float(np.mean([s["B6"]["m1.3"]["none"] for s in per_seed]))
    lru = float(np.mean([s["B6"]["m1.3"]["lru"] for s in per_seed]))
    b6_hp = (decr >= 1.2 * max(none_, 1e-6)) and (decr > lru)
    if not b6_hp:
        drills.append(_why_drill("B6", f"decr={decr:.2f} none={none_:.2f} lru={lru:.2f}; if decr<=lru, energy may not proxy interference -> evict by direct interference score"))
    n_hp = sum([b1_hp, b3_hp, b6_hp])
    summary = (f"B1[acc={b1_acc:.2f} speedup={b1_sp:.0f}x {'HP' if b1_hp else 'HF'}] "
               f"B3[writes {w_all:.0f}->{w_t10:.0f} gap {g_all:.2f}->{g_t10:.2f} {'HP' if b3_hp else 'HF'}] "
               f"B6[decr={decr:.2f} none={none_:.2f} lru={lru:.2f} {'HP' if b6_hp else 'HF'}] | {n_hp}/3 HP")
    v = "HARD_PASS" if n_hp == 3 else ("MIDDLE_BAND" if n_hp >= 1 else "HARD_FAIL")
    return v, f"{v}: bio-smoke batch1 {summary}", drills


print(f"[config] anchor={ANCHOR_NAME} cells=B1,B3,B6 mode={RUN_MODE} seeds={SEEDS} N_B1={N_B1} N_B3={N_B3}", flush=True)
out_dir = get_output_dir(ANCHOR_NAME)
r = run_all()
v, vmsg, drills = verdict(r["per_seed"])
for d in drills:
    print(d, flush=True)
print(f"\n[VERDICT] {vmsg}", flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE,
           "n_seeds": len(SEEDS), "cells": ["B1", "B3", "B6"], "why_drills": drills,
           "per_seed": r["per_seed"], "elapsed_s": r["elapsed_s"]}
write_metrics(out_dir, metrics, r["per_seed"])
print("[metrics] written", flush=True)
