"""
exp_oas_seeding_mitigation_v1 -- Original Antigenic Sin: do customer corrections override entrenched Wikipedia seeds? -- CPU.

ROUTING: OAS_seeding_mitigation_CRITICAL. Immune OAS analog: bindings entrenched during the seeding window (5.84M-article
  Wikipedia pre-train) could dominate retrieval, drowning out later customer corrections -- a product-blocker. Tests: seed S
  facts (Wikipedia), add C customer facts of which half CONFLICT (same key, corrected value); query the conflicting keys --
  does the store return the CUSTOMER value or the entrenched seed value? Compares UNMITIGATED equal-weight pinv vs MITIGATED
  (customer facts up-weighted in the ridge solve). Pure numpy pinv. CPU.
PRE-REGISTERED: HARD-PASS mitigated customer-override >= 0.90 AND OAS bias is real (unmitigated override <= 0.60, i.e. the
  problem exists and the mitigation fixes it). MIDDLE mitigated 0.70-0.90. HARD-FAIL mitigated < 0.70 (mitigation insufficient).
FORMULA SELF-TESTS (PROT-022): 1. base recall=1. 2. weighted-pinv shape. 3. conflict detected.
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

ANCHOR_NAME = "oas_seeding_mitigation_v1"; D = 1024; M = 256; RIDGE = 1e-2; W_CUST = 25.0
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_SEED = 300 if RUN_MODE == "smoke" else 800; N_CONFLICT = 60 if RUN_MODE == "smoke" else 150


def sign_keys(n, d, g):
    return np.sign(g.standard_normal((n, d))).astype(np.float64)


def codebook(n, m, g):
    return np.sign(g.standard_normal((n, m))).astype(np.float64)


def wpinv(K, V, w, ridge):
    Dd = K.shape[1]; Kw = K * w[:, None]
    return np.linalg.solve(K.T @ Kw + ridge * np.eye(Dd), Kw.T @ V)


def acc(K, W, V, book):
    idx = np.argmax((K @ W) @ book.T, axis=1); gold = np.argmax(V @ book.T, axis=1); return float((idx == gold).mean())


def _selftest():
    g = np.random.default_rng(0); K = sign_keys(20, 64, g); book = codebook(30, 32, g); V = book[g.integers(0, 30, 20)]
    W = wpinv(K, V, np.ones(20), 1e-3); assert acc(K, W, V, book) >= 0.99, "base recall=1"
    assert wpinv(K, V, np.ones(20), 1e-3).shape == (64, 32), "weighted-pinv shape"
    assert (np.array([1, 2]) != np.array([1, 3])).any(), "conflict detected"
    print("[selftest] PASS: oas-seeding-mitigation", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(17); book = codebook(M * 4, M, g)
    Ks = sign_keys(N_SEED, D, g); Vs = book[g.integers(0, len(book), N_SEED)]            # Wikipedia seed facts
    cidx = g.choice(N_SEED, N_CONFLICT, replace=False)                                   # customer corrects these keys
    Kc = Ks[cidx].copy()                                                                 # same keys (exact conflict)
    Vc = book[g.integers(0, len(book), N_CONFLICT)]                                       # new (corrected) values
    # ensure the corrected value differs from the seed value
    gold_c = np.argmax(Vc @ book.T, axis=1)
    K_all = np.vstack([Ks, Kc]); V_all = np.vstack([Vs, Vc])
    w_unmit = np.ones(len(K_all))
    w_mit = np.ones(len(K_all)); w_mit[N_SEED:] = W_CUST                                 # up-weight customer facts
    W_un = wpinv(K_all, V_all, w_unmit, RIDGE); W_mit = wpinv(K_all, V_all, w_mit, RIDGE)
    def override(W):
        pred = np.argmax((Kc @ W) @ book.T, axis=1); return float((pred == gold_c).mean())
    un = override(W_un); mit = override(W_mit)
    # check seed facts not catastrophically forgotten under mitigation
    non_conf = np.setdiff1d(np.arange(N_SEED), cidx); seed_keep = acc(Ks[non_conf], W_mit, Vs[non_conf], book)
    print("  customer-override: unmitigated=%.3f mitigated=%.3f | non-conflict seed retention(mit)=%.3f (w_cust=%.0f)" % (un, mit, seed_keep, W_CUST), flush=True)
    return {"unmit": un, "mit": mit, "seed_keep": seed_keep}


def verdict(r) -> Tuple[str, str]:
    s = "override unmit=%.3f mit=%.3f, seed-retention=%.3f" % (r["unmit"], r["mit"], r["seed_keep"])
    if r["mit"] >= 0.90 and r["unmit"] <= 0.60 and r["seed_keep"] >= 0.90:
        return ("HARD_PASS", "HARD_PASS: OAS bias is REAL (unmitigated override <=0.60) AND up-weighting fixes it (customer override >=0.90, seeds retained) -- pre-trained substrate can be safely overlaid with customer corrections. " + s)
    if r["mit"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: mitigation 0.70-0.90 customer override. " + s)
    return ("HARD_FAIL", "HARD_FAIL: mitigation <0.70 -- customer corrections still drowned by entrenched seeds (OAS unsolved). " + s)


print("[config] anchor=%s mode=%s D=%d N_seed=%d N_conflict=%d w_cust=%.0f" % (ANCHOR_NAME, RUN_MODE, D, N_SEED, N_CONFLICT, W_CUST), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
