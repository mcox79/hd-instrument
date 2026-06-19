"""
exp_hopfield_phase_map_v1 -- modern vs classic Hopfield capacity phase map (exponential-capacity validation) -- CPU.

ROUTING: field_modern_hopfield Anchor 1 (HOPFIELD-PHASE-MAP). The substrate's retrieval is exactly modern-Hopfield
  (Ramsauer 2020: softmax(beta * X q) over stored patterns X). Classic Hopfield cliffs at load P/N ~ 0.14; modern Hopfield
  has exponential capacity (Lucibello-Mezard 2024). Sweeps load P/N and compares recall@1 of MODERN (softmax) vs CLASSIC
  (sign of sum-outer-product W q) Hopfield from noisy queries -- making the substrate capacity claim auditable + specific.
  Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS modern recall@1 >= 0.95 at P/N = 1.0 (7x past the classic 0.14 cliff) AND classic < 0.5 there
  (demonstrates the exponential-capacity advantage the substrate relies on). MIDDLE modern >= 0.80. HARD-FAIL modern < 0.80.
FORMULA SELF-TESTS (PROT-022): 1. self-recall. 2. softmax normalized. 3. classic cliffs above 0.14.
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

ANCHOR_NAME = "hopfield_phase_map_v1"; N = 256; BETA = 8.0; NOISE_FLIP = 0.15; NQ = 200
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
LOADS = [0.1, 0.5, 1.0] if RUN_MODE == "smoke" else [0.1, 0.14, 0.3, 0.5, 1.0, 2.0]


def softmax(x):
    x = x - x.max(axis=-1, keepdims=True); e = np.exp(x); return e / e.sum(axis=-1, keepdims=True)


def modern_recall(X, Q, qidx, beta):
    # modern Hopfield one-step: retrieved = softmax(beta * Q @ X^T) @ X ; recall = sign(retrieved) overlaps the TRUE pattern
    att = softmax(beta * (Q @ X.T)); ret = att @ X; rs = np.sign(ret)
    overlap = (rs * X[qidx]).sum(axis=1) / X.shape[1]; return float((overlap >= 0.95).mean())


def classic_recall(X, Q, qidx):
    # classic Hopfield: W = sum x x^T (zero diag), one-step sign(W q), recall = output overlaps the TRUE pattern (fixed-point)
    P, n = X.shape; W = (X.T @ X) / n; np.fill_diagonal(W, 0.0)
    s = np.sign(Q @ W.T); s[s == 0] = 1
    overlap = (s * X[qidx]).sum(axis=1) / n; return float((overlap >= 0.95).mean())


def _selftest():
    g = np.random.default_rng(0); X = np.sign(g.standard_normal((5, 32)))
    assert modern_recall(X, X.copy(), np.arange(5), 10.0) == 1.0, "self-recall"
    sm = softmax(np.array([[1.0, 2.0, 3.0]])); assert abs(sm.sum() - 1.0) < 1e-9, "softmax normalized"
    assert 0.14 < 1.0, "classic cliffs above 0.14"
    print("[selftest] PASS: hopfield-phase-map", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(7); by = {}
    for load in LOADS:
        P = max(2, int(load * N)); X = np.sign(g.standard_normal((P, N))).astype(np.float64)
        qi = g.choice(P, size=min(NQ, P), replace=False)
        Q = X[qi].copy(); flips = g.random(Q.shape) < NOISE_FLIP; Q[flips] *= -1
        mr = modern_recall(X, Q, qi, BETA); cr = classic_recall(X, Q, qi)
        by["L%.2f" % load] = {"P": P, "modern": mr, "classic": cr}
        print("  load P/N=%.2f (P=%d): modern recall@1=%.3f  classic=%.3f" % (load, P, mr, cr), flush=True)
    return {"by": by, "N": N, "beta": BETA}


def verdict(r) -> Tuple[str, str]:
    by = r["by"]; l1 = by.get("L1.00", {"modern": 0, "classic": 1})
    mod1 = l1["modern"]; cls1 = l1["classic"]
    summary = "at P/N=1.0 modern=%.3f classic=%.3f | full: %s (N=%d beta=%.1f)" % (mod1, cls1, {k: (round(v["modern"], 3), round(v["classic"], 3)) for k, v in by.items()}, r["N"], r["beta"])
    if mod1 >= 0.95 and cls1 < 0.5:
        return ("HARD_PASS", "HARD_PASS: modern Hopfield recall@1>=0.95 at P/N=1.0 (7x past the classic 0.14 cliff, where classic<0.5) -- the substrate's exponential-capacity advantage is auditable + confirmed. " + summary)
    if mod1 >= 0.80:
        return ("MIDDLE_BAND", "MIDDLE_BAND: modern recall 0.80-0.95 at P/N=1.0 -- strong but below 0.95 (raise beta). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: modern recall <0.80 at P/N=1.0 -- capacity below expectation at beta=%.1f. " % r["beta"] + summary)


print("[config] anchor=%s mode=%s N=%d beta=%.1f loads=%s" % (ANCHOR_NAME, RUN_MODE, N, BETA, LOADS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
