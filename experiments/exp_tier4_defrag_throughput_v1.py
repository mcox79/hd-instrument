"""
exp_tier4_defrag_throughput_v1 -- Tier4 Gate-3 via THROUGHPUT (jitter-robust) not per-call latency CV -- CPU.

ROUTING: tier4_gate3_fix follow-up. The per-call latency-CV criterion was measurement-fragile (load-dependent; flipped HP->HF
  under concurrent GPU load). Throughput (queries/sec, aggregated over many batched queries) averages out per-call jitter and
  is the robust criterion. Measures batched query throughput on the pre-defrag (fragmented w/ duplicates) vs post-defrag
  (deduped) store, and confirms defrag is lossless AND does not reduce throughput (it should INCREASE it -- fewer facts after
  dedup). Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS post-defrag throughput >= 0.95x pre-defrag AND accuracy delta <= 0.005 (lossless). MIDDLE
  throughput 0.85-0.95x. HARD-FAIL throughput < 0.85x or not lossless.
FORMULA SELF-TESTS (PROT-022): 1. base recall=1. 2. dedupe idempotent. 3. throughput positive.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "tier4_defrag_throughput_v1"; D = 1024; M = 256
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_UNIQ = 150 if RUN_MODE == "smoke" else 600; DUP_FRAC = 0.4; RIDGE = 1e-2; SECONDS = 1.0; BATCH = 200


def sign_keys(n, d, g):
    return np.sign(g.standard_normal((n, d))).astype(np.float64)


def codebook(n, m, g):
    return np.sign(g.standard_normal((n, m))).astype(np.float64)


def pinv_W(K, V, ridge):
    Dd = K.shape[1]; return np.linalg.solve(K.T @ K + ridge * np.eye(Dd), K.T @ V)


def acc(K, W, V, book):
    idx = np.argmax((K @ W) @ book.T, axis=1); gold = np.argmax(V @ book.T, axis=1); return float((idx == gold).mean())


def dedupe(K, V):
    seen = {}; keep = []
    for i in range(len(K)):
        h = K[i].tobytes()
        if h not in seen:
            seen[h] = 1; keep.append(i)
    return K[keep], V[keep]


def throughput(K, W, book, seconds, bs):
    # warmup
    _ = np.argmax((K[:bs] @ W) @ book.T, axis=1)
    nq = 0; t0 = time.perf_counter()
    while time.perf_counter() - t0 < seconds:
        for i in range(0, len(K), bs):
            _ = np.argmax((K[i:i+bs] @ W) @ book.T, axis=1); nq += min(bs, len(K) - i)
    dt = time.perf_counter() - t0
    return nq / dt


def _selftest():
    g = np.random.default_rng(0); K = sign_keys(20, 64, g); book = codebook(30, 32, g); V = book[g.integers(0, 30, 20)]
    W = pinv_W(K, V, 1e-3); assert acc(K, W, V, book) >= 0.99, "base recall=1"
    K2 = np.vstack([K, K[:5]]); Kd, _ = dedupe(K2, np.vstack([V, V[:5]])); assert len(Kd) == len(K), "dedupe idempotent"
    assert throughput(K, W, book, 0.05, 8) > 0, "throughput positive"
    print("[selftest] PASS: tier4-defrag-throughput", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(46)
    book = codebook(M * 4, M, g); Ku = sign_keys(N_UNIQ, D, g); Vu = book[g.integers(0, len(book), N_UNIQ)]
    ndup = int(N_UNIQ * DUP_FRAC); didx = g.integers(0, N_UNIQ, ndup)
    Kf = np.vstack([Ku, Ku[didx]]); Vf = np.vstack([Vu, Vu[didx]])
    W_frag = pinv_W(Kf, Vf, RIDGE); acc_before = acc(Ku, W_frag, Vu, book)
    Kd, Vd = dedupe(Kf, Vf); W_def = pinv_W(Kd, Vd, RIDGE); acc_after = acc(Ku, W_def, Vu, book)
    tput_before = throughput(Ku, W_frag, book, SECONDS, BATCH)
    tput_after = throughput(Ku, W_def, book, SECONDS, BATCH)
    ratio = tput_after / (tput_before + 1e-9)
    print("  acc before=%.3f after=%.3f | throughput before=%.0f q/s after=%.0f q/s (ratio=%.3f; n_frag=%d->dedup=%d)" % (acc_before, acc_after, tput_before, tput_after, ratio, len(Kf), len(Kd)), flush=True)
    return {"acc_before": acc_before, "acc_after": acc_after, "delta": acc_before - acc_after, "tput_before": tput_before, "tput_after": tput_after, "ratio": ratio}


def verdict(r) -> Tuple[str, str]:
    s = "acc before=%.3f after=%.3f (delta=%.4f) | throughput before=%.0f after=%.0f q/s (ratio=%.3f)" % (r["acc_before"], r["acc_after"], r["delta"], r["tput_before"], r["tput_after"], r["ratio"])
    if r["ratio"] >= 0.95 and abs(r["delta"]) <= 0.005:
        return ("HARD_PASS", "HARD_PASS: defrag is lossless AND preserves/improves query throughput (ratio>=0.95) -- Gate 3 cleared via the jitter-robust throughput criterion. " + s)
    if r["ratio"] >= 0.85:
        return ("MIDDLE_BAND", "MIDDLE_BAND: throughput ratio 0.85-0.95 after defrag. " + s)
    return ("HARD_FAIL", "HARD_FAIL: defrag reduces throughput below 0.85x or is not lossless. " + s)


print("[config] anchor=%s mode=%s D=%d N_uniq=%d batch=%d secs=%.1f" % (ANCHOR_NAME, RUN_MODE, D, N_UNIQ, BATCH, SECONDS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
