"""
exp_tier4_orthogonal_stability_v1 -- Tier4 pre-test 2: orthogonal-update stability (pure substrate) -- CPU.

ROUTING: tier4_consolidated pre-test 2 (substrate analog of LoRA-orthogonal stability). Tests whether adding NEW facts whose
  keys lie in a near-orthogonal subspace leaves held-out accuracy on the ORIGINAL facts within 3% -- i.e. updates do not
  catastrophically interfere (the stability that gates continual fine-tuning). Build pinv W on base facts; measure held-out
  recall (base keys + noise); add N_new orthogonal-subspace facts; re-measure base held-out recall. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS base held-out accuracy after update within 3% (abs) of before. MIDDLE within 8%. HARD-FAIL >8% drop.
FORMULA SELF-TESTS (PROT-022): 1. base recall=1. 2. orthogonal subspace. 3. cleanup self.
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

ANCHOR_NAME = "tier4_orthogonal_stability_v1"; D = 1024; M = 256
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_BASE = 150 if RUN_MODE == "smoke" else 600; N_NEW = 100 if RUN_MODE == "smoke" else 400; RIDGE = 1e-2; QNOISE = 0.3


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


def _selftest():
    g = np.random.default_rng(0); K = sign_keys(20, 64, g); book = codebook(30, 32, g); V = book[g.integers(0, 30, 20)]
    W = pinv_W(K, V, 1e-3); assert acc(K, W, V, book) >= 0.99, "base recall=1"
    a = np.zeros(8); a[:4] = 1; b = np.zeros(8); b[4:] = 1; assert abs(a @ b) < 1e-9, "orthogonal subspace"
    assert int(np.argmax(book[7] @ book.T)) == 7, "cleanup self"
    print("[selftest] PASS: tier4-orthogonal-stability", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(31)
    book = codebook(M * 4, M, g)
    half = D // 2
    # base facts live in the first-half subspace; new facts in the orthogonal second-half subspace
    Kb = sign_keys(N_BASE, D, g).copy(); Kb[:, half:] = 0.0
    Vb = book[g.integers(0, len(book), N_BASE)]
    Kn = sign_keys(N_NEW, D, g).copy(); Kn[:, :half] = 0.0
    Vn = book[g.integers(0, len(book), N_NEW)]
    held_q = np.sign(Kb + QNOISE * g.standard_normal(Kb.shape))   # held-out queries = noisy base keys
    W_before = pinv_W(Kb, Vb, RIDGE); acc_before = acc(held_q, W_before, Vb, book)
    K_all = np.vstack([Kb, Kn]); V_all = np.vstack([Vb, Vn]); W_after = pinv_W(K_all, V_all, RIDGE)
    acc_after = acc(held_q, W_after, Vb, book)
    drop = acc_before - acc_after
    print("  base held-out acc: before=%.3f after_orthogonal_update=%.3f (drop=%.3f; N_base=%d N_new=%d)" % (acc_before, acc_after, drop, N_BASE, N_NEW), flush=True)
    return {"acc_before": acc_before, "acc_after": acc_after, "drop": drop, "n_base": N_BASE, "n_new": N_NEW}


def verdict(r) -> Tuple[str, str]:
    drop = r["drop"]; s = "before=%.3f after=%.3f drop=%.3f (N_base=%d N_new=%d)" % (r["acc_before"], r["acc_after"], drop, r["n_base"], r["n_new"])
    if drop <= 0.03:
        return ("HARD_PASS", "HARD_PASS: orthogonal-subspace updates leave base accuracy within 3pct -- stable continual updates; gates Tier 4 fine-tuning path. " + s)
    if drop <= 0.08:
        return ("MIDDLE_BAND", "MIDDLE_BAND: base accuracy drop 3-8pct under orthogonal updates -- some interference. " + s)
    return ("HARD_FAIL", "HARD_FAIL: base accuracy drops >8pct -- orthogonal updates interfere; capacity-limited. " + s)


print("[config] anchor=%s mode=%s D=%d N_base=%d N_new=%d" % (ANCHOR_NAME, RUN_MODE, D, N_BASE, N_NEW), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
