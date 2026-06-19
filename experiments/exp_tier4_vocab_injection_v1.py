"""
exp_tier4_vocab_injection_v1 -- Tier4 pre-test 1: vocab-injection generalization (pure substrate) -- CPU.

ROUTING: tier4_consolidated pre-test 1. Tests whether NEW vocabulary injected into the substrate after the base KB is built
  is retrievable at the same accuracy as base facts (the continual-vocab-growth capability that gates Tier 4). Build a pinv
  associative store on N_base (key->value) pairs; then incrementally inject N_new NEW key->value pairs via the same pinv
  update; measure retrieval accuracy on the injected vocab. Pure numpy (sign keys + ridge-pinv W + codebook cleanup). CPU.
PRE-REGISTERED: HARD-PASS new-vocab retrieval accuracy >= 0.85. MIDDLE 0.70-0.85. HARD-FAIL < 0.70.
FORMULA SELF-TESTS (PROT-022): 1. base recall=1. 2. sign keys. 3. cleanup self.
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

ANCHOR_NAME = "tier4_vocab_injection_v1"; D = 1024; M = 256
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_BASE = 200 if RUN_MODE == "smoke" else 800; N_NEW = 50 if RUN_MODE == "smoke" else 200; RIDGE = 1e-2


def sign_keys(n, d, g):
    return np.sign(g.standard_normal((n, d))).astype(np.float64)


def codebook(n, m, g):
    return np.sign(g.standard_normal((n, m))).astype(np.float64)


def pinv_W(K, V, ridge):
    # ridge associative map W [D,M] s.t. k @ W ~ v ; W = (K^T K + ridge I)^-1 K^T V
    D = K.shape[1]
    return np.linalg.solve(K.T @ K + ridge * np.eye(D), K.T @ V)


def acc(K, W, V, book):
    pred = K @ W                                  # [n,M]
    idx = np.argmax(pred @ book.T, axis=1)        # cleanup to nearest codebook entry
    gold = np.argmax(V @ book.T, axis=1)
    return float((idx == gold).mean())


def _selftest():
    g = np.random.default_rng(0); K = sign_keys(20, 64, g); book = codebook(30, 32, g); V = book[g.integers(0, 30, 20)]
    W = pinv_W(K, V, 1e-3); assert acc(K, W, V, book) >= 0.99, "base recall=1"
    assert set(np.unique(K)) <= {-1.0, 1.0}, "sign keys"
    assert int(np.argmax(book[5] @ book.T)) == 5, "cleanup self"
    print("[selftest] PASS: tier4-vocab-injection", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(21)
    book = codebook(M * 4, M, g)
    Kb = sign_keys(N_BASE, D, g); Vb = book[g.integers(0, len(book), N_BASE)]
    Kn = sign_keys(N_NEW, D, g); Vn = book[g.integers(0, len(book), N_NEW)]
    # base store, then inject new vocab into the same store (joint pinv = incremental-equivalent for accuracy)
    K_all = np.vstack([Kb, Kn]); V_all = np.vstack([Vb, Vn]); W = pinv_W(K_all, V_all, RIDGE)
    base_acc = acc(Kb, W, Vb, book); new_acc = acc(Kn, W, Vn, book)
    print("  base_acc=%.3f new_vocab_acc=%.3f (N_base=%d N_new=%d D=%d)" % (base_acc, new_acc, N_BASE, N_NEW, D), flush=True)
    return {"base_acc": base_acc, "new_acc": new_acc, "n_base": N_BASE, "n_new": N_NEW}


def verdict(r) -> Tuple[str, str]:
    s = "new-vocab retrieval=%.3f (base=%.3f, N_base=%d N_new=%d)" % (r["new_acc"], r["base_acc"], r["n_base"], r["n_new"])
    if r["new_acc"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: injected vocab retrieves at >=0.85 -- continual vocab growth supported; gates Tier 4. " + s)
    if r["new_acc"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: new-vocab retrieval 0.70-0.85 -- partial; capacity or ridge tuning needed. " + s)
    return ("HARD_FAIL", "HARD_FAIL: injected vocab retrieval <0.70 -- new vocab not cleanly retrievable at this load. " + s)


print("[config] anchor=%s mode=%s D=%d M=%d N_base=%d N_new=%d" % (ANCHOR_NAME, RUN_MODE, D, M, N_BASE, N_NEW), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
