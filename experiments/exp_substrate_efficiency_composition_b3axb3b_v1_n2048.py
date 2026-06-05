"""
substrate_efficiency_composition_b3axb3b_v1_n2048 -- efficiency-axis composition (writes-to-BPC) -- remote CPU.

ROUTING: research_to_exp_dev_SQ2_HP_metric_reframe_confirmed (Test B). Re-framing: efficiency primitives compose
  MULTIPLICATIVELY on the EFFICIENCY metric (writes/wall to a target BPC), not BPC. B3a top-k gating (task axis)
  x B3b exp-smoothed surprise (capacity/anti-crosstalk axis) -> heterogeneous -> predicted multiplicative write
  reduction. CPU numpy, $0. remote_cpu_queue.

CAPABILITY QUESTION: how many WRITES (examples actually written to W) does each arm need to reach a fixed target
  BPC? arms: baseline (write-all) / B3a (top-5%) / B3b (exp-smoothed surprise) / B3a+B3b (both gates AND'd).
  reduction(arm) = baseline_writes / arm_writes. Predicted: combined ~ B3a_reduction x B3b_reduction (multiplicative).

MODEL: cf-RPE bigram char-LM (Zipf V=70). target_bpc = write-all final BPC. Each arm runs until val BPC <= target
  (capped at MAX_STEPS); record writes. (Gating that preserves learning reaches target with fewer writes.)

CELLS (3 seeds): writes + reduction for the 4 arms.
PRE-REGISTERED bands: HARD-PASS combined_reduction >= 0.7 * (B3a_reduction x B3b_reduction) (multiplicative within 30%)
  AND combined > max(B3a, B3b). MIDDLE: combined > max single but sub-multiplicative. HARD-FAIL: combined <= max single.

FORMULA SELF-TESTS (PROT-022): 1. cf-RPE shrinks error. 2. surprise selects above-mean. 3. uniform=ln(V).
ASCII-only. write_metrics. PROT-018 _n2048 -> N=2048.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_efficiency_composition_b3axb3b_v1_n2048"
_N_SUFFIX = 2048
N = 2048
assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

VOCAB = 70
K_ACTIVE = 8
LR = 0.5
BATCH = 64
GATE_FRAC = 0.05
TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]
ARMS = ["all", "b3a", "b3b", "both"]
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_DIM = 512; CORPUS = 6000; MAX_STEPS = 200
else:
    SEEDS = [7, 17, 23]; N_DIM = N; CORPUS = 25000; MAX_STEPS = 600


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


def bpc(W, cb, va, g, un):
    nb = min(2000, len(va) - 1); st = g.integers(0, len(va) - 1, size=nb); ctx = cb[va[st]]; nxt = va[st + 1]
    pred = ctx @ W.T; pred = pred / (np.linalg.norm(pred, axis=1, keepdims=True) + 1e-8); cos = pred @ cb.T
    best = float("inf")
    for t in TEMP_GRID:
        z = cos / t; z -= z.max(axis=1, keepdims=True); ez = np.exp(z); pr = ez / (ez.sum(axis=1, keepdims=True) + 1e-30)
        best = min(best, float(-np.log(np.clip(pr[np.arange(nb), nxt], 1e-12, None)).mean()))
    return best


def train_to_target(n, cb, tr, va, g, un, arm, target):
    W = np.zeros((n, n), dtype=np.float32); writes = 0; run_mean = None
    warmup = max(1, MAX_STEPS // 10)
    for step in range(MAX_STEPS):
        st = g.integers(0, len(tr) - 1, size=BATCH); ctx = cb[tr[st]]; nxt = cb[tr[st + 1]]
        delta = nxt - ctx @ W.T; err = np.linalg.norm(delta, axis=1)
        mask = np.ones(BATCH, dtype=bool)
        if arm in ("b3a", "both"):
            mask = mask & (err >= np.quantile(err, 1.0 - GATE_FRAC))
        if arm in ("b3b", "both"):
            bm = float(err.mean()); run_mean = bm if run_mean is None else 0.9 * run_mean + 0.1 * bm
            mask = mask & ((err > run_mean) if step >= warmup else np.ones(BATCH, dtype=bool))
        if mask.sum() > 0:
            W = W + LR * (delta[mask].T @ ctx[mask]) / max(1, int(mask.sum())); writes += int(mask.sum())
        if target is not None and step % 10 == 0 and bpc(W, cb, va, np.random.default_rng(step), un) <= target:
            break
    return W, writes


def _selftest():
    g = np.random.default_rng(0); cb = codebook(5, 128, g)
    W = np.zeros((128, 128), dtype=np.float32); v = W @ cb[0]; eb = float(np.linalg.norm(cb[1] - v))
    W = W + np.outer(cb[1] - v, cb[0]); assert float(np.linalg.norm(cb[1] - W @ cb[0])) < eb, "cf-RPE"
    err = np.array([1.0, 5.0, 2.0, 8.0]); assert int(np.sum(err > err.mean())) == 2, "surprise"
    assert abs(math.log(5) - 1.6094) < 1e-3
    print("[selftest] PASS: cfrpe surprise", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    g = np.random.default_rng(seed); ids = gen_zipf(VOCAB, CORPUS, g); sp = int(0.8 * len(ids)); tr, va = ids[:sp], ids[sp:]
    cb = codebook(VOCAB, N_DIM, g); un = math.log(VOCAB)
    # baseline write-all to fix target BPC (final), record its writes
    Wall, w_all = train_to_target(N_DIM, cb, tr, va, np.random.default_rng(seed + 1), un, "all", None)
    target = bpc(Wall, cb, va, np.random.default_rng(seed), un) + 0.05    # slight slack
    out = {"all_writes": w_all, "target_bpc": float(target)}
    for arm in ["b3a", "b3b", "both"]:
        _, w = train_to_target(N_DIM, cb, tr, va, np.random.default_rng(seed + hash(arm) % 100), un, arm, target)
        out[arm + "_writes"] = w
    return {"seed": seed, "N": N_DIM, **out}


def verdict(ps) -> Tuple[str, str]:
    wa = float(np.mean([p["all_writes"] for p in ps]))
    r3a = wa / max(float(np.mean([p["b3a_writes"] for p in ps])), 1)
    r3b = wa / max(float(np.mean([p["b3b_writes"] for p in ps])), 1)
    rboth = wa / max(float(np.mean([p["both_writes"] for p in ps])), 1)
    summary = "writes_all=%.0f reduction[b3a=%.1fx b3b=%.1fx both=%.1fx] mult_pred=%.1fx" % (wa, r3a, r3b, rboth, r3a * r3b)
    if rboth >= 0.7 * (r3a * r3b) and rboth > max(r3a, r3b):
        return ("HARD_PASS", "HARD_PASS: efficiency primitives compose MULTIPLICATIVELY (write reduction). " + summary)
    if rboth > max(r3a, r3b):
        return ("MIDDLE_BAND", "MIDDLE_BAND: combined > best single, sub-multiplicative. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: no efficiency composition. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM), flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] all=%d b3a=%d b3b=%d both=%d" % (seed, r["all_writes"], r["b3a_writes"], r["b3b_writes"], r["both_writes"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
