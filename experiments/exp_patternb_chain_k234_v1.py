"""
exp_patternb_chain_k234_v1 -- #5: Pattern B multi-step causal chains k=2/3/4 -- CPU.
ROUTING: cpu_backlog_high_priority_12 #5 chain-k234. Chained unbinding through k hops (each fact links to next via a bridge role) at production N; measure end-to-end chain retrieval at k=2/3/4. CPU.
PRE-REGISTERED: HARD-PASS chain retrieval >=80pct at k=3 and >=65pct at k=4.
FORMULA SELF-TESTS (PROT-022): 1. pinv recovers. 2. quant ok. 3. sign keys.
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
ANCHOR_NAME = "patternb_chain_k234_v1"; N = 4096
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
def phasor(n, k, g): return np.exp(1j * g.uniform(-np.pi, np.pi, (k, n))).astype(np.complex64)
def sign_keys(M, n, g): return np.sign(g.standard_normal((M, n))).astype(np.float32)
def pinv_W(K, ridge=1e-3):
    W = (K.T @ np.linalg.solve(K @ K.T + ridge * np.eye(len(K)), K)).astype(np.float32); np.fill_diagonal(W, 0.0); return W
def recall(W, K, g, flip=0.05, it=8):
    s = K * np.where(g.random(K.shape) < flip, -1.0, 1.0)
    for _ in range(it):
        rec = np.sign(s @ W.T); rec[rec == 0] = 1.0; s = rec
    return float(np.mean(np.all(rec == K, axis=1)))
def quant(W, bits):
    L = 2 ** bits - 1; lo, hi = np.quantile(W, 0.001), np.quantile(W, 0.999); Wc = np.clip(W, lo, hi)
    return (np.round((Wc - lo) / (hi - lo + 1e-12) * L) / L * (hi - lo) + lo).astype(np.float32)
def _selftest():
    g = np.random.default_rng(0); K = sign_keys(3, 64, g); W = pinv_W(K); assert recall(W, K, np.random.default_rng(1), flip=0.0) >= 0.9, "pinv recovers"
    assert quant(W, 4).shape == W.shape, "quant ok"
    assert set(np.unique(K)) <= {-1.0, 1.0}, "sign keys"
    print("[selftest] PASS: %s" % ANCHOR_NAME, flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(7); VOCAB = 500; cache = phasor(N, VOCAB, g); link = phasor(N, 1, g)[0]; by = {}
    T = 100 if RUN_MODE=="smoke" else 300
    for k in [2, 3, 4]:
        ok = 0
        for _ in range(T):
            chain = g.choice(VOCAB, k+1, replace=False)
            facts = [(link * cache[chain[i]] + cache[chain[i+1]]).astype(np.complex64) for i in range(k)]   # fact_i: link->next bound + payload
            cur = chain[0]; good = True
            for i in range(k):
                nxt = int(np.argmax((cache.conj() @ (facts[i] * np.conj(link))).real))
                if nxt != chain[i+1]: good = False; break
                cur = nxt
            ok += int(good)
        by["k%d" % k] = ok / T; print("  k=%d chain-retrieval=%.3f" % (k, by["k%d" % k]), flush=True)
    return {"by": by}
def verdict(r) -> Tuple[str, str]:
    s = "chain retrieval by k: %s" % {k: round(v,3) for k,v in r["by"].items()}
    if r["by"].get("k3",0) >= 0.80 and r["by"].get("k4",0) >= 0.65: return ("HARD_PASS", "HARD_PASS: multi-step chain retrieval >=80pct@k3, >=65pct@k4 -- substrate-native deep causal chaining works. " + s)
    if r["by"].get("k3",0) >= 0.65: return ("MIDDLE_BAND", "MIDDLE_BAND: chains degrade by k=4. " + s)
    return ("HARD_FAIL", "HARD_FAIL: chains fail by k=3. " + s)

print('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
