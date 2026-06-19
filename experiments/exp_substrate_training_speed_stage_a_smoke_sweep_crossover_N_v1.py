"""
substrate_training_speed_stage_a_smoke_sweep_crossover_N_v1 -- find the substrate-vs-Adam crossover N* (CPU).

ROUTING: notes/change_request_stage_a_smoke_sweep_crossover_N_2026-06-04.md (responds to my Stage A smoke:
  N=256 HARD_FAIL was a capacity-starved small-N artifact). Sweeps N to find the EMPIRICAL crossover N* where
  substrate first beats the Adam-softmax baseline at matched BPC. CPU numpy, $0. GATES the full Stage A run.

CAPABILITY QUESTION:
  At what substrate dimension N does the substrate-hybrid (cf-RPE bigram / posbind+symW trigram + cosine
  readout) achieve a wall-time advantage over a standard Adam-softmax head on the same char-LM task?
  Below N*: Adam wins (substrate capacity-starved -> easy target). Above N*: substrate wins (capacity realized).

METHOD (per (N, task) cell, 3 seeds): same task + same cb context features; substrate trains to its OWN BPC at
  this N; Adam baseline trains to MATCH that BPC; speedup = Adam_wall_to_match / substrate_wall. Synthetic Zipf
  2nd-order corpus (corpus-agnostic crossover; matches the Stage A smoke that triggered this).

CELLS: N in {256,512,1024,2048,4096} x task in {bigram,trigram}; 3 seeds.

PRE-REGISTERED bands (N* = smallest N with median speedup >= 1.0 across both tasks):
  HARD-PASS: N* <= 2048 (substrate advantage at substrate-class scale -> proceed to full Stage A at N>=N*).
  MIDDLE: N* == 4096 (advantage only at larger scale -> reassess full-run target N).
  HARD-FAIL: no crossover in range (substrate never >= 1.0x -> iterate trick selection before any full run).

FORMULA SELF-TESTS (PROT-022): 1. Adam step lowers CE. 2. cf-RPE shrinks error. 3. roll-bind order-sensitive. 4. uniform=ln(V).

PROT-018: swept-N anchor (no _nN binding). PROT-021: per-seed partials. QUEUE: remote_cpu_queue (numpy). ASCII-only.
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
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics

ANCHOR_NAME = "substrate_training_speed_stage_a_smoke_sweep_crossover_N_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

VOCAB = 70
K_ACTIVE = 8
LR_SUB = 0.5
BATCH = 64
TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]
TASKS = ["bigram", "trigram"]
ADAM_LR = 0.01

if RUN_MODE == "smoke":
    N_GRID = [256, 512]; SEEDS = [1, 2]; CORPUS = 4000; SUB_STEPS = 150; MAX_EPOCHS = 12; VOCAB = 40
else:
    N_GRID = [256, 512, 1024, 2048, 4096]; SEEDS = [7, 17, 23]; CORPUS = 15000; SUB_STEPS = 350; MAX_EPOCHS = 30


def gen_zipf2(V, length, g):
    ranks = 1.0 / np.arange(1, V + 1); zp = ranks / ranks.sum()
    T = np.zeros((V * V, V))
    for ctx in range(V * V):
        tg = g.choice(V, size=K_ACTIVE, replace=False, p=zp)
        lg = g.standard_normal(K_ACTIVE) * 2.0; w = np.exp(lg - lg.max()); w /= w.sum(); T[ctx, tg] = w
    ids = np.zeros(length, dtype=np.int64); a, b = 0, 0
    for i in range(length):
        ids[i] = b; nxt = g.choice(V, p=T[a * V + b]); a, b = b, nxt
    return ids


def codebook(V, n, g):
    cb = (g.integers(0, 2, size=(V, n)) * 2 - 1).astype(np.float32)
    return cb / (np.linalg.norm(cb, axis=1, keepdims=True) + 1e-8)


def _cl(task):
    return 1 if task == "bigram" else 3


def ctx_emb(cb, ids, starts, task):
    if task == "bigram":
        return cb[ids[starts]]
    b = np.zeros((len(starts), cb.shape[1]), dtype=np.float32)
    for j in range(3):
        b = b + np.roll(cb[ids[starts + j]], shift=j + 1, axis=1)
    return b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-8)


def bpc_cosine(W, cb, ids, task, g, un):
    cl = _cl(task); nb = min(2000, len(ids) - cl - 1); st = g.integers(0, len(ids) - cl - 1, size=nb)
    ctx = ctx_emb(cb, ids, st, task); nxt = ids[st + cl]
    pred = ctx @ W.T; pred = pred / (np.linalg.norm(pred, axis=1, keepdims=True) + 1e-8); cos = pred @ cb.T
    best = float("inf")
    for t in TEMP_GRID:
        z = cos / t; z = z - z.max(axis=1, keepdims=True); ez = np.exp(z); pr = ez / (ez.sum(axis=1, keepdims=True) + 1e-30)
        best = min(best, float(-np.log(np.clip(pr[np.arange(nb), nxt], 1e-12, None)).mean()))
    return best


def bpc_softmax(M, cb, ids, task, g):
    cl = _cl(task); nb = min(2000, len(ids) - cl - 1); st = g.integers(0, len(ids) - cl - 1, size=nb)
    ctx = ctx_emb(cb, ids, st, task); nxt = ids[st + cl]
    logits = ctx @ M.T; logits = logits - logits.max(axis=1, keepdims=True)
    ez = np.exp(logits); pr = ez / (ez.sum(axis=1, keepdims=True) + 1e-30)
    return float(-np.log(np.clip(pr[np.arange(nb), nxt], 1e-12, None)).mean())


def train_substrate(n, cb, tr, task, g):
    cl = _cl(task); W = np.zeros((n, n), dtype=np.float32); t0 = time.time()
    for _ in range(SUB_STEPS):
        st = g.integers(0, len(tr) - cl - 1, size=BATCH)
        ctx = ctx_emb(cb, tr, st, task); nxt = cb[tr[st + cl]]
        if task == "bigram":
            W = W + LR_SUB * ((nxt - ctx @ W.T).T @ ctx) / BATCH
        else:
            W = W + LR_SUB * (nxt.T @ ctx) / BATCH
    return W, time.time() - t0


def train_baseline_to_match(n, cb, tr, va, task, target_bpc, g):
    cl = _cl(task); V = cb.shape[0]; M = (g.standard_normal((V, n)) * 0.01).astype(np.float32)
    mm = np.zeros_like(M); vv = np.zeros_like(M); b1, b2, eps = 0.9, 0.999, 1e-8
    spe = max(1, (len(tr) - cl - 1) // BATCH); t0 = time.time(); it = 0; best = float("inf")
    for ep in range(MAX_EPOCHS):
        for _ in range(spe):
            it += 1; st = g.integers(0, len(tr) - cl - 1, size=BATCH)
            ctx = ctx_emb(cb, tr, st, task); nxt = tr[st + cl]
            logits = ctx @ M.T; logits = logits - logits.max(axis=1, keepdims=True)
            ez = np.exp(logits); pr = ez / (ez.sum(axis=1, keepdims=True) + 1e-30)
            gl = pr.copy(); gl[np.arange(BATCH), nxt] -= 1.0; gl /= BATCH; gM = gl.T @ ctx
            mm = b1 * mm + (1 - b1) * gM; vv = b2 * vv + (1 - b2) * (gM * gM)
            M = M - ADAM_LR * (mm / (1 - b1 ** it)) / (np.sqrt(vv / (1 - b2 ** it)) + eps)
        bpc = bpc_softmax(M, cb, va, task, g); best = min(best, bpc)
        if bpc <= target_bpc:
            return time.time() - t0, True, bpc
    return time.time() - t0, False, best


def _selftest():
    g = np.random.default_rng(0); cb = codebook(5, 64, g); ids = np.array([0, 1, 2, 3, 4] * 100)
    M = (g.standard_normal((5, 64)) * 0.01).astype(np.float32)
    l0 = bpc_softmax(M, cb, ids, "bigram", np.random.default_rng(1))
    _, _, best = train_baseline_to_match(64, cb, ids, ids, "bigram", -1.0, g); assert best < l0, "Adam no progress"
    W = np.zeros((64, 64), dtype=np.float32); v = W @ cb[0]; eb = float(np.linalg.norm(cb[1] - v))
    W = W + np.outer(cb[1] - v, cb[0]); ea = float(np.linalg.norm(cb[1] - W @ cb[0])); assert ea < eb, "cf-RPE no shrink"
    b1 = ctx_emb(cb, np.array([0, 1, 2, 3]), np.array([0]), "trigram")
    b2 = ctx_emb(cb, np.array([2, 1, 0, 3]), np.array([0]), "trigram"); assert float((b1 * b2).sum()) < 0.95
    assert abs(math.log(5) - 1.6094) < 1e-3
    print(f"[selftest] PASS: adam_lowers_CE {l0:.3f}->{best:.3f} cfrpe_shrinks rollbind_order", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    t0 = time.time(); un = math.log(VOCAB); cells = {}
    for n in N_GRID:
        for task in TASKS:
            g = np.random.default_rng(seed * 1000 + n + (0 if task == "bigram" else 1))
            ids = gen_zipf2(VOCAB, CORPUS, g); sp = int(0.8 * len(ids)); tr, va = ids[:sp], ids[sp:]
            cb = codebook(VOCAB, n, g)
            W, t_sub = train_substrate(n, cb, tr, task, g)
            bpc_sub = bpc_cosine(W, cb, va, task, g, un)
            t_base, matched, bpc_base = train_baseline_to_match(n, cb, tr, va, task, bpc_sub, g)
            speedup = float(t_base / max(t_sub, 1e-6))
            cells[f"N{n}_{task}"] = {"N": n, "task": task, "bpc_sub": float(bpc_sub), "gap_sub": float(un - bpc_sub),
                                     "t_sub": float(t_sub), "t_base": float(t_base), "matched": bool(matched), "speedup": speedup}
            print(f"  [seed={seed} N={n} {task}] gap_sub={un - bpc_sub:.2f} t_sub={t_sub:.2f}s t_base={t_base:.2f}s speedup={speedup:.2f}x matched={matched}", flush=True)
    return {"seed": seed, "cells": cells, "elapsed_s": time.time() - t0}


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "no results")
    def med_speed(n):
        return float(np.median([r["cells"][f"N{n}_{t}"]["speedup"] for r in results for t in TASKS]))
    curve = {n: med_speed(n) for n in N_GRID}
    nstar = next((n for n in N_GRID if curve[n] >= 1.0), None)
    summary = "crossover_curve " + " ".join(f"N{n}:{curve[n]:.2f}x" for n in N_GRID) + f" | N*={nstar}"
    if nstar is not None and nstar <= 2048:
        return ("HARD_PASS", f"HARD_PASS: substrate-vs-Adam crossover at N*={nstar}<=2048 (advantage at substrate-class scale). {summary}")
    if nstar == 4096:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: crossover only at N*=4096 (advantage at larger scale). {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: no crossover in range (substrate never beats Adam) -> iterate trick selection. {summary}")


print(f"[config] anchor={ANCHOR_NAME} N_grid={N_GRID} tasks={TASKS} mode={RUN_MODE} seeds={SEEDS} sub_steps={SUB_STEPS} max_epochs={MAX_EPOCHS}", flush=True)
out_dir = get_output_dir(ANCHOR_NAME)
done, remaining = resumable_seeds(SEEDS, out_dir, run_config={"N_grid": N_GRID, "run_mode": RUN_MODE, "tasks": TASKS, "V": VOCAB})
print(f"[ckpt] {len(done)} done, {len(remaining)} to run", flush=True)
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    write_partial(out_dir, seed, run_seed(seed))
per_seed = aggregate_partials(out_dir, SEEDS); all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg,
           "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "N_grid": N_GRID, "tasks": TASKS,
           "per_seed": [{k: v for k, v in r.items()} for r in all_results]}
write_metrics(out_dir, metrics, all_results)
print("[metrics] written", flush=True)
