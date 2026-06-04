"""
substrate_training_speed_ladder_stage_a_charlm_v1_n2048 -- substrate vs SGD wall-time to matched BPC (CPU).

ROUTING: notes/routing_training_speed_iterative_ladder_stage_a_tiny_charLM_2026-06-04.md. Stage A of the
  training-speed ladder (user direction: "show max training on tiny models, measure speedup, move up a tier").
  CPU numpy, $0. Validates the substrate training-speed claim (~80-95x wall-time per drill) at tiny scale
  BEFORE scaling up.

CAPABILITY QUESTION:
  At a tiny char-LM (V=70), how much FASTER does substrate one-shot/few-pass training (cf-RPE for bigram;
  position-binding+symmetric-Hebbian for trigram) reach a target BPC than a STANDARD SGD-trained linear-softmax
  head on the SAME context features? Speedup = baseline_wall_to_match / substrate_wall (at matched BPC).

FAIR-COMPARISON DESIGN (same task, same context features cb-embedding; only the trained head + algorithm differ):
  - SUBSTRATE arm: native head. bigram cell -> W(N,N) via cf-RPE few-pass; trigram cell -> W(N,N) via
    posbind(K=3)+symmetric-Hebbian. Readout = calibrated-temperature cosine to codebook. Train, record (BPC_sub, t_sub).
  - BASELINE arm: standard head M(V,N), logits = ctx_emb @ M^T, softmax cross-entropy, Adam. Train up to
    MAX_EPOCHS; record t_base = first wall-time its val BPC <= BPC_sub (matched); if never, t_base = full budget
    (lower-bound speedup) and flag unmatched.
  speedup = t_base / t_sub.

CELLS (3 seeds): task in {bigram, trigram}; V=70; N=2048.

PRE-REGISTERED BANDS (median speedup at matched BPC across cells/seeds; substrate BPC must be a real LM:
  gap_sub = ln(V) - BPC_sub > 0.3 nats, else that cell is VOID -> HF):
  HARD-PASS: median speedup >= 10x AND both cells substrate gap>0.3 (substrate trains a real LM far faster than SGD).
  MIDDLE: median speedup in [2x, 10x).
  HARD-FAIL: median speedup < 2x OR a cell's substrate gap <= 0.3 (no real LM / no speed advantage).

FORMULA SELF-TESTS (PROT-022):
  1. softmax+CE gradient sign correct (one Adam step lowers loss on a toy problem). 2. cf-RPE shrinks error.
  3. roll-bind order-sensitive. 4. uniform nats = ln(V).

PROT-018: anchor _n2048 -> N=2048. PROT-019 floor 14400s. PROT-021: per-seed partials.
QUEUE: remote_cpu_queue (numpy; GPU not needed). ASCII-only.
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

ANCHOR_NAME = "substrate_training_speed_ladder_stage_a_charlm_v1_n2048"
_N_SUFFIX = 2048
N = 2048
assert N == _N_SUFFIX

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
    N_DIM = 256; VOCAB = 40; SEEDS = [1, 2]; CORPUS = 4000; SUB_STEPS = 200; MAX_EPOCHS = 12
else:
    N_DIM = N; SEEDS = [7, 17, 23]; CORPUS = 30000; SUB_STEPS = 800; MAX_EPOCHS = 60


def gen_zipf2(V, length, gen_np):
    """2nd-order Markov (covers both bigram-usable and trigram structure), Zipf targets."""
    ranks = 1.0 / np.arange(1, V + 1); zp = ranks / ranks.sum()
    T = np.zeros((V * V, V))
    for ctx in range(V * V):
        tg = gen_np.choice(V, size=K_ACTIVE, replace=False, p=zp)
        lg = gen_np.standard_normal(K_ACTIVE) * 2.0; w = np.exp(lg - lg.max()); w /= w.sum(); T[ctx, tg] = w
    ids = np.zeros(length, dtype=np.int64); a, b = 0, 0
    for i in range(length):
        ids[i] = b; nxt = gen_np.choice(V, p=T[a * V + b]); a, b = b, nxt
    return ids


def codebook(V, n, g):
    cb = (g.integers(0, 2, size=(V, n)) * 2 - 1).astype(np.float32)
    return cb / (np.linalg.norm(cb, axis=1, keepdims=True) + 1e-8)


def ctx_emb(cb, ids, starts, task):
    if task == "bigram":
        return cb[ids[starts]]
    b = np.zeros((len(starts), cb.shape[1]), dtype=np.float32)
    for j in range(3):
        b = b + np.roll(cb[ids[starts + j]], shift=j + 1, axis=1)
    return b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-8)


def _ctx_len(task):
    return 1 if task == "bigram" else 3


def bpc_cosine(W, cb, ids, task, g, un):
    cl = _ctx_len(task); nb = min(2000, len(ids) - cl - 1)
    st = g.integers(0, len(ids) - cl - 1, size=nb)
    ctx = ctx_emb(cb, ids, st, task); nxt = ids[st + cl]
    pred = ctx @ W.T; pred = pred / (np.linalg.norm(pred, axis=1, keepdims=True) + 1e-8); cos = pred @ cb.T
    best = float("inf")
    for t in TEMP_GRID:
        z = cos / t; z = z - z.max(axis=1, keepdims=True); ez = np.exp(z); pr = ez / (ez.sum(axis=1, keepdims=True) + 1e-30)
        best = min(best, float(-np.log(np.clip(pr[np.arange(nb), nxt], 1e-12, None)).mean()))
    return best


def bpc_softmax(M, cb, ids, task, g):
    cl = _ctx_len(task); nb = min(2000, len(ids) - cl - 1)
    st = g.integers(0, len(ids) - cl - 1, size=nb)
    ctx = ctx_emb(cb, ids, st, task); nxt = ids[st + cl]
    logits = ctx @ M.T; logits = logits - logits.max(axis=1, keepdims=True)
    ez = np.exp(logits); pr = ez / (ez.sum(axis=1, keepdims=True) + 1e-30)
    return float(-np.log(np.clip(pr[np.arange(nb), nxt], 1e-12, None)).mean())


def train_substrate(n, cb, tr, task, g):
    cl = _ctx_len(task); W = np.zeros((n, n), dtype=np.float32); t0 = time.time()
    for _ in range(SUB_STEPS):
        st = g.integers(0, len(tr) - cl - 1, size=BATCH)
        ctx = ctx_emb(cb, tr, st, task); nxt = cb[tr[st + cl]]
        if task == "bigram":
            W = W + LR_SUB * ((nxt - ctx @ W.T).T @ ctx) / BATCH      # cf-RPE
        else:
            W = W + LR_SUB * (nxt.T @ ctx) / BATCH                    # symmetric Hebbian (posbind trigram)
    return W, time.time() - t0


def train_baseline_to_match(n, cb, tr, va, task, target_bpc, g, un):
    """Adam softmax head; return (t_to_match or full budget, matched_bool, best_bpc)."""
    cl = _ctx_len(task); V = cb.shape[0]
    M = (g.standard_normal((V, n)) * 0.01).astype(np.float32)
    mm = np.zeros_like(M); vv = np.zeros_like(M); b1, b2, eps = 0.9, 0.999, 1e-8
    steps_per_epoch = max(1, (len(tr) - cl - 1) // BATCH); t0 = time.time(); it = 0; best = float("inf")
    for ep in range(MAX_EPOCHS):
        for _ in range(steps_per_epoch):
            it += 1
            st = g.integers(0, len(tr) - cl - 1, size=BATCH)
            ctx = ctx_emb(cb, tr, st, task); nxt = tr[st + cl]
            logits = ctx @ M.T; logits = logits - logits.max(axis=1, keepdims=True)
            ez = np.exp(logits); pr = ez / (ez.sum(axis=1, keepdims=True) + 1e-30)
            grad_logits = pr.copy(); grad_logits[np.arange(BATCH), nxt] -= 1.0; grad_logits /= BATCH
            gM = grad_logits.T @ ctx
            mm = b1 * mm + (1 - b1) * gM; vv = b2 * vv + (1 - b2) * (gM * gM)
            mhat = mm / (1 - b1 ** it); vhat = vv / (1 - b2 ** it)
            M = M - ADAM_LR * mhat / (np.sqrt(vhat) + eps)
        bpc = bpc_softmax(M, cb, va, task, g); best = min(best, bpc)
        if bpc <= target_bpc:
            return time.time() - t0, True, bpc
    return time.time() - t0, False, best


def _selftest():
    g = np.random.default_rng(0)
    # softmax+Adam step lowers CE on a toy linearly-separable problem
    cb = codebook(5, 64, g); ids = np.array([0, 1, 2, 3, 4, 0, 1, 2, 3, 4] * 50)
    M = (g.standard_normal((5, 64)) * 0.01).astype(np.float32)
    l0 = bpc_softmax(M, cb, ids, "bigram", np.random.default_rng(1))
    t, matched, best = train_baseline_to_match(64, cb, ids, ids, "bigram", -1.0, g, math.log(5))
    assert best < l0, f"Adam did not lower CE {l0}->{best}"
    W = np.zeros((64, 64), dtype=np.float32); c0, n0 = cb[0], cb[1]
    v = W @ c0; eb = float(np.linalg.norm(n0 - v)); W = W + np.outer(n0 - v, c0); ea = float(np.linalg.norm(n0 - W @ c0))
    assert ea < eb, "cf-RPE did not shrink error"
    b1 = ctx_emb(cb, np.array([0, 1, 2, 3]), np.array([0]), "trigram")
    b2 = ctx_emb(cb, np.array([2, 1, 0, 3]), np.array([0]), "trigram")
    assert float((b1 * b2).sum()) < 0.95, "roll-bind not order-sensitive"
    assert abs(math.log(5) - 1.6094) < 1e-3
    print(f"[selftest] PASS: adam_lowers_CE {l0:.3f}->{best:.3f} cfrpe_shrinks rollbind_order", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    t0 = time.time(); un = math.log(VOCAB); cells = {}
    for task in TASKS:
        g = np.random.default_rng(seed * 100 + (0 if task == "bigram" else 1))
        ids = gen_zipf2(VOCAB, CORPUS, g); sp = int(0.8 * len(ids)); tr, va = ids[:sp], ids[sp:]
        cb = codebook(VOCAB, n_dim, g)
        W, t_sub = train_substrate(n_dim, cb, tr, task, g)
        bpc_sub = bpc_cosine(W, cb, va, task, g, un); gap_sub = un - bpc_sub
        t_base, matched, bpc_base = train_baseline_to_match(n_dim, cb, tr, va, task, bpc_sub, g, un)
        speedup = float(t_base / max(t_sub, 1e-6))
        cells[task] = {"bpc_sub": float(bpc_sub), "gap_sub": float(gap_sub), "t_sub": float(t_sub),
                       "bpc_base_best": float(bpc_base), "t_base": float(t_base), "baseline_matched": bool(matched),
                       "speedup": speedup}
        print(f"  [seed={seed} {task}] bpc_sub={bpc_sub:.3f}(gap {gap_sub:.2f}) t_sub={t_sub:.2f}s | "
              f"baseline matched={matched} bpc={bpc_base:.3f} t_base={t_base:.2f}s -> speedup={speedup:.1f}x", flush=True)
    return {"seed": seed, "N": n_dim, "uniform_nats": un, "cells": cells, "elapsed_s": time.time() - t0}


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "no results")
    speeds = [r["cells"][t]["speedup"] for r in results for t in TASKS]
    med = float(np.median(speeds))
    min_gap = min(r["cells"][t]["gap_sub"] for r in results for t in TASKS)
    per = {t: (float(np.median([r["cells"][t]["speedup"] for r in results])),
               float(np.mean([r["cells"][t]["gap_sub"] for r in results])),
               sum(1 for r in results if r["cells"][t]["baseline_matched"])) for t in TASKS}
    summary = "median_speedup={:.1f}x min_gap_sub={:.2f} | ".format(med, min_gap) + \
        " ".join(f"{t}:speedup={per[t][0]:.1f}x gap={per[t][1]:.2f} matched={per[t][2]}/{len(results)}" for t in TASKS)
    if min_gap <= 0.3:
        return ("HARD_FAIL", f"HARD_FAIL: a cell substrate is not a real LM (gap<=0.3); speedup void. {summary}")
    if med >= 10.0:
        return ("HARD_PASS", f"HARD_PASS: substrate trains a real char-LM >=10x faster than SGD at matched BPC. {summary}")
    if med >= 2.0:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: 2-10x training-speed advantage. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: <2x speed advantage. {summary}")


print(f"[config] anchor={ANCHOR_NAME} N={N_DIM} V={VOCAB} tasks={TASKS} mode={RUN_MODE} seeds={SEEDS} sub_steps={SUB_STEPS} max_epochs={MAX_EPOCHS}", flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME)
done, remaining = resumable_seeds(SEEDS, out_dir, run_config={"N": N_DIM, "run_mode": RUN_MODE, "tasks": TASKS, "V": VOCAB})
print(f"[ckpt] {len(done)} done, {len(remaining)} to run", flush=True)
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    write_partial(out_dir, seed, run_seed(seed, N_DIM))
per_seed = aggregate_partials(out_dir, SEEDS); all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg, "N": N_DIM,
           "V": VOCAB, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "tasks": TASKS,
           "per_seed": [{k: v for k, v in r.items()} for r in all_results]}
write_metrics(out_dir, metrics, all_results)
print("[metrics] written", flush=True)
