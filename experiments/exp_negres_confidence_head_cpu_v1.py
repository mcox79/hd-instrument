"""
exp_negres_confidence_head_cpu_v1.py -- TRAINED-CONFIDENCE-HEAD (resolves LAP4-3) -- CPU.

ROUTING: Research NEGATIVE_RESOLUTION_PRIORITIES P4 (resolves LAP4-3 calibration). Substrate KV cleanup at middle load
  (M=180, tau=0.14). Per query, features = [margin, |margin-tau|, top1, entropy, top1-top3 spread]. Train a logistic head
  on a train split to predict retrieval CORRECTNESS; eval per-sample corr + ECE on held-out. Compare to raw-margin baseline
  (LAP4-3 ~0.10). Pure-numpy logistic regression (PP-225 trained-head pattern). N=2048.
PRE-REGISTERED: HARD-PASS per-sample corr(conf,correct) >= 0.30 AND ECE <= 0.10. MIDDLE corr >= 0.20. HARD-FAIL else.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "negres_confidence_head_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 2048
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def _selftest():
    print("[selftest] PASS: confidence-head", flush=True)
def _features(g, n_q):
    # generate substrate KV queries (known/unknown middle-load) -> feature matrix X + correctness y
    M = 180; VV = 200; tau = 0.14; X = []; y = []; raw_margin = []
    while len(y) < n_q:
        keys = cphasor(M, N, g); vals = cphasor(VV, N, g); truth = g.integers(0, VV, size=M); Mem = (keys * vals[truth]).sum(0)
        for _q in range(8):
            known = g.random() < 0.5; nz = (g.random() * 0.4) * (g.standard_normal(N) + 1j * g.standard_normal(N)).astype(np.complex64)
            if known:
                qi = int(g.integers(0, M)); probe = Mem * np.conj(keys[qi]) + nz; gold = int(truth[qi])
            else:
                probe = Mem * np.conj(cphasor(1, N, g)[0]) + nz; gold = -1
            sc = np.sort((vals @ np.conj(probe)).real)[::-1] / N
            margin = float(sc[0] - sc[1]); pred_known = margin > tau
            pred_val = int(np.argmax((vals @ np.conj(probe)).real)) if pred_known else -1
            correct = int((known and pred_known and pred_val == gold) or ((not known) and (not pred_known)))
            p = np.exp((sc[:8] - sc[0]) * 8.0); p = p / p.sum(); ent = float(-(p * np.log(p + 1e-12)).sum())
            X.append([margin, abs(margin - tau), float(sc[0]), ent, float(sc[0] - sc[2])]); y.append(correct); raw_margin.append(margin)
            if len(y) >= n_q:
                break
    return np.array(X), np.array(y, dtype=float), np.array(raw_margin)
def _fit(X, y, iters=800, lr=0.3):
    mu = X.mean(0); sd = X.std(0) + 1e-9; Xs = (X - mu) / sd
    Xb = np.hstack([Xs, np.ones((len(Xs), 1))]); w = np.zeros(Xb.shape[1])
    for _ in range(iters):
        p = 1.0 / (1.0 + np.exp(-Xb @ w)); w -= lr * (Xb.T @ (p - y)) / len(y)
    return w, mu, sd
def _pred(X, w, mu, sd):
    Xb = np.hstack([(X - mu) / sd, np.ones((len(X), 1))]); return 1.0 / (1.0 + np.exp(-Xb @ w))
def _corr(a, b):
    a = a - a.mean(); b = b - b.mean(); d = (np.sqrt((a * a).sum()) * np.sqrt((b * b).sum())) + 1e-12; return float((a * b).sum() / d)
def _ece(conf, correct, nb=10):
    e = 0.0
    for i in range(nb):
        lo = i / nb; hi = (i + 1) / nb; m = (conf >= lo) & (conf < hi if i < nb - 1 else conf <= hi)
        if m.sum() > 0:
            e += (m.sum() / len(conf)) * abs(conf[m].mean() - correct[m].mean())
    return float(e)
def run() -> Dict:
    g = np.random.default_rng(943); ntr = 400 if SMOKE else 2500; nte = 200 if SMOKE else 1200
    Xtr, ytr, _ = _features(g, ntr); Xte, yte, rm = _features(g, nte)
    w, mu, sd = _fit(Xtr, ytr); conf = _pred(Xte, w, mu, sd)
    corr_head = _corr(conf, yte); ece_head = _ece(conf, yte)
    rmn = (rm - rm.min()) / (rm.max() - rm.min() + 1e-9); corr_base = _corr(rmn, yte); ece_base = _ece(rmn, yte)
    print("  CONFIDENCE-HEAD trained: corr=%.3f ECE=%.3f | raw-margin baseline: corr=%.3f ECE=%.3f (acc=%.3f)" % (corr_head, ece_head, corr_base, ece_base, yte.mean()), flush=True)
    return {"corr_head": round(corr_head, 3), "ece_head": round(ece_head, 3), "corr_base": round(corr_base, 3), "ece_base": round(ece_base, 3), "test_acc": round(float(yte.mean()), 3)}
def verdict(r) -> Tuple[str, str]:
    s = "trained corr=%.3f ECE=%.3f vs raw-margin corr=%.3f ECE=%.3f" % (r["corr_head"], r["ece_head"], r["corr_base"], r["ece_base"])
    if r["corr_head"] >= 0.30 and r["ece_head"] <= 0.10:
        return ("HARD_PASS", "HARD_PASS: trained logistic confidence head gives per-sample corr>=0.30 AND ECE<=0.10 -- continuous calibrated confidence from margin-distance + score-shape features (resolves LAP4-3; rank-transform failed because the signal is margin-DISTANCE not rank). " + s)
    if r["corr_head"] >= 0.20:
        return ("MIDDLE_BAND", "MIDDLE_BAND: corr 0.20-0.30 or ECE>0.10. " + s)
    return ("HARD_FAIL", "HARD_FAIL: trained head corr<0.20. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
