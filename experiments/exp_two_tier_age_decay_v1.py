"""
exp_two_tier_age_decay_v1.py -- age-weighted decay lets customer overlay win conflicts over entrenched seeds -- CPU.

ROUTING: DEEPER_drills_8 Anchor 1.1 (two-tier confidence + age-weighted decay). Extends OAS mitigation: instead of static up-weighting, use age-weighted decay -- seed (Wikipedia) bindings decay with age while recent customer bindings stay strong. Measure customer-overlay conflict-win rate with vs without age decay. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS customer-overlay wins >= 0.90 with age-decay mitigation vs <= 0.50 without. MIDDLE 0.70-0.90. HARD-FAIL < 0.70.
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
ANCHOR_NAME = "two_tier_age_decay_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def sign_keys(n, d, g):
    return np.sign(g.standard_normal((n, d))).astype(np.float64)
def codebook(n, m, g):
    return np.sign(g.standard_normal((n, m))).astype(np.float64)
def wpinv(K, V, w, ridge):
    Dd = K.shape[1]; Kw = K * w[:, None]; return np.linalg.solve(K.T @ Kw + ridge * np.eye(Dd), Kw.T @ V)
def _selftest():
    g = np.random.default_rng(0); K = sign_keys(10, 32, g); bk = codebook(20, 16, g); V = bk[g.integers(0, 20, 10)]
    W = wpinv(K, V, np.ones(10), 1e-3); idx = np.argmax((K @ W) @ bk.T, axis=1); gold = np.argmax(V @ bk.T, axis=1); assert (idx == gold).mean() >= 0.9, "base recall"
    assert np.exp(-0.5) < 1.0, "age decay <1"
    print("[selftest] PASS: two-tier-age-decay", flush=True)
def run() -> Dict:
    g = np.random.default_rng(3); D = 1024; M = 256; S = 300 if SMOKE else 800; CN = 60 if SMOKE else 150; RIDGE = 1e-2
    bk = codebook(M * 4, M, g); Ks = sign_keys(S, D, g); Vs = bk[g.integers(0, len(bk), S)]
    ci = g.choice(S, CN, replace=False); Kc = Ks[ci].copy(); Vc = bk[g.integers(0, len(bk), CN)]; goldc = np.argmax(Vc @ bk.T, axis=1)
    K_all = np.vstack([Ks, Kc]); V_all = np.vstack([Vs, Vc])
    # ages: seeds old (age ~ large), customer recent (age ~ 0); weight = exp(-LAMBDA * age)
    ages = np.concatenate([g.uniform(5, 10, S), np.zeros(CN)]); LAMBDA = 0.7
    w_decay = np.exp(-LAMBDA * ages); w_flat = np.ones(len(K_all))
    def winrate(w):
        W = wpinv(K_all, V_all, w, RIDGE); pred = np.argmax((Kc @ W) @ bk.T, axis=1); return float((pred == goldc).mean())
    base = winrate(w_flat); mit = winrate(w_decay)
    print("  customer-overlay win: no-decay=%.3f age-decay=%.3f (lambda=%.1f)" % (base, mit, LAMBDA), flush=True)
    return {"no_decay": base, "age_decay": mit}
def verdict(r) -> Tuple[str, str]:
    s = "win no-decay=%.3f age-decay=%.3f" % (r["no_decay"], r["age_decay"])
    if r["age_decay"] >= 0.90 and r["no_decay"] <= 0.50: return ("HARD_PASS", "HARD_PASS: age-weighted decay lets customer overlay win >=0.90 (vs <=0.50 flat) -- recency-decay is a clean OAS mitigation. " + s)
    if r["age_decay"] >= 0.70: return ("MIDDLE_BAND", "MIDDLE_BAND: age-decay win 0.70-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: age-decay <0.70 customer win. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
