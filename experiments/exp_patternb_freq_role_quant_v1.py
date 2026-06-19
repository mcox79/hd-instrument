"""
exp_patternb_freq_role_quant_v1 -- #12: frequency-weighted role quantization -- CPU.
ROUTING: cpu_backlog_high_priority_12 #12 freq-role-quant. Quantize role-identifier vectors by frequency (common roles coarse, rare roles fine); measure reduction on role portion + retrieval F1. CPU.
PRE-REGISTERED: HARD-PASS >=1.5x reduction on role-identifier storage at retrieval F1>=0.95.
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
ANCHOR_NAME = "patternb_freq_role_quant_v1"; N = 4096
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
    g = np.random.default_rng(7); NROLE = 8; VOCAB = 300; roles = phasor(N, NROLE, g); cache = phasor(N, VOCAB, g)
    freq = np.array([2**(NROLE-i) for i in range(NROLE)], float); freq /= freq.sum()   # zipf-ish role frequency
    bits = np.where(freq > freq.mean(), 2, 6)   # common roles 2-bit, rare 6-bit
    rq = []
    for i in range(NROLE):
        rr = roles[i]; L = 2**int(bits[i])-1
        ang = np.angle(rr); aq = np.round((ang+np.pi)/(2*np.pi)*L)/L*(2*np.pi)-np.pi; rq.append(np.exp(1j*aq).astype(np.complex64))
    rq = np.array(rq); ok = 0; NB = 200
    for _ in range(NB):
        k = int(g.integers(3, NROLE)); ridx = g.choice(NROLE, k, replace=False); fid = g.choice(VOCAB, k, replace=False)
        bundle = np.sum([rq[ridx[i]]*cache[fid[i]] for i in range(k)], axis=0).astype(np.complex64)
        j = 0; got = int(np.argmax((cache.conj() @ (bundle*np.conj(rq[ridx[j]]))).real)); ok += int(got == fid[j])
    f1 = ok/NB; red = 32.0 / float(np.mean(bits)); print("  freq-weighted role quant: retrieval F1=%.3f role-storage reduction=%.2fx (avg %.1f bits)" % (f1, red, np.mean(bits)), flush=True)
    return {"f1": f1, "red": red}
def verdict(r) -> Tuple[str, str]:
    s = "F1=%.3f role-reduction=%.2fx" % (r["f1"], r["red"])
    if r["red"] >= 1.5 and r["f1"] >= 0.95: return ("HARD_PASS", "HARD_PASS: frequency-weighted role quant >=1.5x role-storage reduction at F1>=0.95. " + s)
    if r["f1"] >= 0.90: return ("MIDDLE_BAND", "MIDDLE_BAND: reduction/F1 near target. " + s)
    return ("HARD_FAIL", "HARD_FAIL: freq-role quant too lossy. " + s)

print('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
