"""
exp_tier4_defrag_consistency_v1 -- Tier4 pre-test 3: defrag consistency (pure substrate) -- CPU.

ROUTING: tier4_consolidated pre-test 3. The substrate periodically "defrags" (consolidates the KB: drops exact-duplicate
  facts, re-solves the associative map). This must be LOSSLESS for queries and not blow up latency. Build a KB with injected
  duplicates; measure unique-query accuracy + per-query latency; run defrag (dedupe + re-solve); re-measure. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS query accuracy unchanged (delta <= 0.005) AND post-defrag per-query latency variance < 20pct.
  MIDDLE accuracy unchanged but latency variance 20-40pct. HARD-FAIL accuracy drops > 0.005.
FORMULA SELF-TESTS (PROT-022): 1. base recall=1. 2. dedupe idempotent. 3. cleanup self.
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

ANCHOR_NAME = "tier4_defrag_consistency_v1"; D = 1024; M = 256
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_UNIQ = 150 if RUN_MODE == "smoke" else 600; DUP_FRAC = 0.4; RIDGE = 1e-2; LAT_REPS = 50


def sign_keys(n, d, g):
    return np.sign(g.standard_normal((n, d))).astype(np.float64)


def codebook(n, m, g):
    return np.sign(g.standard_normal((n, m))).astype(np.float64)


def pinv_W(K, V, ridge):
    Dd = K.shape[1]
    return np.linalg.solve(K.T @ K + ridge * np.eye(Dd), K.T @ V)


def acc(K, W, V, book):
    pred = K @ W; idx = np.argmax(pred @ book.T, axis=1); gold = np.argmax(V @ book.T, axis=1)
    return float((idx == gold).mean())


def dedupe(K, V):
    seen = {}; keep = []
    for i in range(len(K)):
        h = K[i].tobytes()
        if h not in seen:
            seen[h] = 1; keep.append(i)
    return K[keep], V[keep]


def _selftest():
    g = np.random.default_rng(0); K = sign_keys(20, 64, g); book = codebook(30, 32, g); V = book[g.integers(0, 30, 20)]
    W = pinv_W(K, V, 1e-3); assert acc(K, W, V, book) >= 0.99, "base recall=1"
    K2 = np.vstack([K, K[:5]]); V2 = np.vstack([V, V[:5]]); Kd, Vd = dedupe(K2, V2)
    assert len(Kd) == len(K), "dedupe idempotent"
    assert int(np.argmax(book[3] @ book.T)) == 3, "cleanup self"
    print("[selftest] PASS: tier4-defrag-consistency", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def query_latency(K, W, book, reps):
    lat = []
    for _ in range(reps):
        t = time.perf_counter(); pred = K @ W; _ = np.argmax(pred @ book.T, axis=1); lat.append(time.perf_counter() - t)
    return np.array(lat)


def run() -> Dict:
    g = np.random.default_rng(41)
    book = codebook(M * 4, M, g)
    Ku = sign_keys(N_UNIQ, D, g); Vu = book[g.integers(0, len(book), N_UNIQ)]
    ndup = int(N_UNIQ * DUP_FRAC); didx = g.integers(0, N_UNIQ, ndup)
    K_frag = np.vstack([Ku, Ku[didx]]); V_frag = np.vstack([Vu, Vu[didx]])
    W_frag = pinv_W(K_frag, V_frag, RIDGE); acc_before = acc(Ku, W_frag, Vu, book)
    Kd, Vd = dedupe(K_frag, V_frag); W_def = pinv_W(Kd, Vd, RIDGE); acc_after = acc(Ku, W_def, Vu, book)
    lat = query_latency(Ku, W_def, book, LAT_REPS)
    lat_var = float(lat.std() / (lat.mean() + 1e-12))
    print("  acc before_defrag=%.3f after_defrag=%.3f | n_frag=%d -> n_dedup=%d | latency cv=%.3f" % (acc_before, acc_after, len(K_frag), len(Kd), lat_var), flush=True)
    return {"acc_before": acc_before, "acc_after": acc_after, "delta": acc_before - acc_after, "lat_cv": lat_var, "n_frag": len(K_frag), "n_dedup": len(Kd)}


def verdict(r) -> Tuple[str, str]:
    s = "acc before=%.3f after=%.3f (delta=%.4f) latency_cv=%.3f n_frag=%d->dedup=%d" % (r["acc_before"], r["acc_after"], r["delta"], r["lat_cv"], r["n_frag"], r["n_dedup"])
    if abs(r["delta"]) <= 0.005 and r["lat_cv"] < 0.20:
        return ("HARD_PASS", "HARD_PASS: defrag is lossless (accuracy unchanged) AND latency stable (cv<20pct) -- safe periodic consolidation; gates Tier 4. " + s)
    if abs(r["delta"]) <= 0.005:
        return ("MIDDLE_BAND", "MIDDLE_BAND: defrag lossless but latency variance 20-40pct. " + s)
    return ("HARD_FAIL", "HARD_FAIL: defrag changes query accuracy by >0.005 -- not lossless. " + s)


print("[config] anchor=%s mode=%s D=%d N_uniq=%d dup_frac=%.2f" % (ANCHOR_NAME, RUN_MODE, D, N_UNIQ, DUP_FRAC), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
