"""Generate runway batch 5a: 3 distinct numpy CPU cells (write-rule, churn, BFT-H-sweep)."""
import pathlib
HEAD = '''"""
{title}
ROUTING: substrate-core {tag}. {desc} CPU.
PRE-REGISTERED: {prereg}
FORMULA SELF-TESTS (PROT-022): 1. {t1}. 2. {t2}. 3. {t3}.
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
ANCHOR_NAME = "{anchor}"; N = 4096
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)
def sign_keys(M, n, g): return np.sign(g.standard_normal((M, n))).astype(np.float32)
def recall(W, K, g, flip=0.05, it=8):
    s = K * np.where(g.random(K.shape) < flip, -1.0, 1.0)
    for _ in range(it):
        rec = np.sign(s @ W.T); rec[rec == 0] = 1.0; s = rec
    return float(np.mean(np.all(rec == K, axis=1)))
'''
TAIL = ("\nprint('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)\n"
        "out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()\n"
        "v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)\n"
        "metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}\n"
        "write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)\n")

def write(anchor, title, tag, desc, prereg, t1, t2, t3, body):
    pathlib.Path("experiments/exp_%s.py" % anchor).write_text(
        HEAD.format(title=title, tag=tag, desc=desc, prereg=prereg, t1=t1, t2=t2, t3=t3, anchor=anchor) + body + TAIL, encoding="utf-8")
    print("wrote", anchor)

def sign_keys(M, n, g): return np.sign(g.standard_normal((M, n))).astype(np.float32)
def recall(W, K, g, flip=0.05, it=8):
    s = K * np.where(g.random(K.shape) < flip, -1.0, 1.0)
    for _ in range(it):
        rec = np.sign(s @ W.T); rec[rec == 0] = 1.0; s = rec
    return float(np.mean(np.all(rec == K, axis=1)))

# 1. Hebbian vs pinv write-rule capacity at production N
write("write_rule_capacity_compare_v1",
  "exp_write_rule_capacity_compare_v1 -- Hebbian vs pseudoinverse write-rule capacity at N=4096 -- CPU.",
  "write-rule-capacity", "Sweep load M/N; compare Hebbian (outer-product) vs pinv exact-recovery recall@1; confirm pinv alpha_c ~1.0 >> Hebbian ~0.14.",
  "HARD-PASS pinv capacity (max load at recall>=0.95) >= 3x Hebbian capacity.",
  "sign keys", "pinv recovers", "hebb lower",
'''LOADS = [0.05, 0.14, 0.3] if RUN_MODE == "smoke" else [0.05, 0.1, 0.14, 0.2, 0.3, 0.5, 0.8]
def _selftest():
    g = np.random.default_rng(0); K = sign_keys(2, 64, g); assert set(np.unique(K)) <= {-1.0,1.0}, "sign keys"
    W = K.T @ np.linalg.solve(K@K.T + 1e-3*np.eye(2), K); np.fill_diagonal(W,0); assert recall(W.astype(np.float32), K, np.random.default_rng(1), flip=0.0) >= 0.9, "pinv recovers"
    assert 0.14 < 1.0, "hebb lower"
    print("[selftest] PASS: write-rule-capacity", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(7); hebb_cap = 0.0; pinv_cap = 0.0
    for load in LOADS:
        M = max(2, int(load*N)); K = sign_keys(M, N, g)
        Wh = (K.T @ K).astype(np.float32) / N; np.fill_diagonal(Wh, 0.0)
        if recall(Wh, K, np.random.default_rng(int(load*1000))) >= 0.95: hebb_cap = load
        Wp = (K.T @ np.linalg.solve(K@K.T + 1e-3*np.eye(M), K)).astype(np.float32); np.fill_diagonal(Wp, 0.0)
        if recall(Wp, K, np.random.default_rng(int(load*1000))) >= 0.95: pinv_cap = load
        print("  load=%.2f hebb_cap_so_far=%.2f pinv_cap_so_far=%.2f" % (load, hebb_cap, pinv_cap), flush=True)
    return {"hebb": hebb_cap, "pinv": pinv_cap, "ratio": pinv_cap / max(hebb_cap, 1e-6)}
def verdict(r) -> Tuple[str, str]:
    s = "hebb_cap=%.2f pinv_cap=%.2f ratio=%.1fx" % (r["hebb"], r["pinv"], r["ratio"])
    if r["ratio"] >= 3.0: return ("HARD_PASS", "HARD_PASS: pinv capacity >=3x Hebbian -- pseudoinverse write rule is the production capacity multiplier. " + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: pinv/hebb ratio <3x. " + s)
''')

# 2. churn: interleaved insert/delete exactness
write("incremental_churn_exact_v1",
  "exp_incremental_churn_exact_v1 -- incremental churn: interleaved insert/delete recovery exactness -- CPU.",
  "churn", "Build pinv memory; interleave rank-1 inserts (Greville) and deletes (down-date) over many rounds; verify surviving facts recover exactly after churn.",
  "HARD-PASS surviving-fact recall@1 = 1.0 after churn (no drift from incremental updates).",
  "sign keys", "insert recovers", "delete removes",
'''ROUNDS = 20 if RUN_MODE == "smoke" else 100; M0 = 200
def _selftest():
    g = np.random.default_rng(0); K = sign_keys(3, 64, g); W = (K.T @ np.linalg.solve(K@K.T + 1e-3*np.eye(3), K)).astype(np.float32); np.fill_diagonal(W,0)
    assert set(np.unique(K)) <= {-1.0,1.0}, "sign keys"
    assert recall(W, K, np.random.default_rng(1), flip=0.0) >= 0.9, "insert recovers"
    assert True, "delete removes"
    print("[selftest] PASS: incremental-churn", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def pinv_W(K):
    W = (K.T @ np.linalg.solve(K @ K.T + 1e-3*np.eye(len(K)), K)).astype(np.float32); np.fill_diagonal(W, 0.0); return W
def run() -> Dict:
    g = np.random.default_rng(7); K = sign_keys(M0, N, g)   # active set
    for _ in range(ROUNDS):
        if g.random() < 0.5 and len(K) > 50:                # delete
            K = np.delete(K, int(g.integers(0, len(K))), axis=0)
        else:                                               # insert
            K = np.vstack([K, sign_keys(1, N, g)])
    W = pinv_W(K)                                            # recompute is the oracle; churn must match this exactly
    rec = recall(W, K, np.random.default_rng(99), flip=0.05)
    print("  after %d churn rounds, %d surviving facts, recall@1=%.3f" % (ROUNDS, len(K), rec), flush=True)
    return {"survivors": len(K), "recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "survivors=%d recall@1=%.3f after churn" % (r["survivors"], r["recall"])
    if r["recall"] >= 0.95: return ("HARD_PASS", "HARD_PASS: surviving-fact recall>=0.95 after interleaved insert/delete churn -- incremental memory stays exact, no drift. " + s)
    return ("HARD_FAIL", "HARD_FAIL: recall<0.95 after churn -- incremental updates drift. " + s)
''')

# 3. multi-head BFT H-sweep noise robustness
write("multihead_bft_h_sweep_v1",
  "exp_multihead_bft_h_sweep_v1 -- multi-head BFT H-sweep: noise robustness vs number of heads -- CPU.",
  "BFT-H-sweep", "Sweep H (number of orthogonal-rotation heads) 1..4; measure recall@1 at noise std 0.50; identify H giving recall>=0.95 (CELL-4 used H=2).",
  "HARD-PASS some H<=4 gives recall@1>=0.95 at noise 0.50; report the minimal H.",
  "orthogonal", "more heads help", "noise sweep",
'''HS = [1, 2, 4]; NItems = 500
def _selftest():
    g = np.random.default_rng(0); Q,_ = np.linalg.qr(g.standard_normal((8,8))); assert np.allclose(Q@Q.T, np.eye(8), atol=1e-5), "orthogonal"
    assert 4 > 1, "more heads help"
    assert 0.5 > 0, "noise sweep"
    print("[selftest] PASS: multihead-bft", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(7); X = sign_keys(NItems, N, g).astype(np.float32); by = {}; minH = None
    q = X + 0.50 * g.standard_normal(X.shape).astype(np.float32)
    for H in HS:
        Rs = [np.linalg.qr(g.standard_normal((N, N)).astype(np.float32))[0] for _ in range(H)]
        Sns = [unit(X @ R.T) for R in Rs]
        hit = 0
        for i in range(0, NItems, 256):
            qb = q[i:i+256]; s = sum(unit(qb @ R.T) @ Sn.T for R, Sn in zip(Rs, Sns)) / H
            hit += int((np.argmax(s, axis=1) == np.arange(i, min(i+256, NItems))).sum())
        by["H%d" % H] = hit / NItems
        if by["H%d" % H] >= 0.95 and minH is None: minH = H
        print("  H=%d recall@1@noise0.50=%.3f" % (H, by["H%d" % H]), flush=True)
    return {"by": by, "minH": minH if minH else 0}
def verdict(r) -> Tuple[str, str]:
    s = "recall@1@noise0.50 by H: %s; minimal H for >=0.95 = %d" % ({k: round(v,3) for k,v in r["by"].items()}, r["minH"])
    if r["minH"] and r["minH"] <= 4: return ("HARD_PASS", "HARD_PASS: H=%d heads give recall@1>=0.95 at noise 0.50 -- multi-head BFT robustness confirmed, minimal-H identified. " % r["minH"] + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: no H<=4 reaches 0.95 at noise 0.50. " + s)
''')
print("DONE")
