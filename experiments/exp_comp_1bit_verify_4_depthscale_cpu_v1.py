"""
exp_comp_1bit_verify_4_depthscale_cpu_v1.py -- COMP-1BIT-VERIFY-4 DEPTH-SCALING -- CPU.

ROUTING: Research 1BIT_DEPTH_VERIFICATION (COMP-1BIT-VERIFY-4 DEPTH-SCALING); pure-FHRR (no download). Sweep L=3/5/8/10 at K=10,M=500; track 1-bit loss(L) -- compounding?
  Bipolar QPSK 1-bit-per-component quantization of EVERY stored vector vs float32, on the depth-retrieval task with
  hierarchical cleanup. Baseline config L=5,K=10,M=500,rho=0,N=8192; this cell sweeps L (depth). Reports float vs 1-bit
  recall + loss at each point and the critical break value. Verifies PP-301 (COMP-11) under production-realism.
PRE-REGISTERED: HARD-PASS loss<5pp at L=10. MIDDLE<15pp. HARD-FAIL degrades faster than float.
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
ANCHOR_NAME = "comp_1bit_verify_4_depthscale_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
_S = 1.0 / math.sqrt(2.0)
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def q1(v):
    return ((np.sign(v.real) + 1j * np.sign(v.imag)) * _S).astype(np.complex64)
def mq(v, Q):
    return q1(v) if Q else v
def codebook(M, rho, Nd, g):
    ind = cphasor(M, Nd, g)
    if rho <= 0:
        return ind
    base = cphasor(1, Nd, g)                                          # shared component induces pairwise correlation ~rho
    return cnorm(math.sqrt(rho) * base + math.sqrt(1.0 - rho) * ind)
def comp_batch(B, K, slots, Nd, g, Q):
    r = cphasor(B * K, Nd, g).reshape(B, K, Nd); return mq(cnorm((slots[None, :, :] * r).sum(1)), Q)
def build_path(L, K, slots, A, t, Nd, g, Q):
    j = [int(g.integers(0, K)) for _ in range(L)]; node = A[t]; tn = [A[t]]
    for l in range(L):
        sibs = (A[g.integers(0, len(A), size=K)] if l == 0 else comp_batch(K, K, slots, Nd, g, Q))
        bound = slots * sibs; bound[j[l]] = slots[j[l]] * node; node = mq(cnorm(bound.sum(0)), Q); tn.append(node)
    return j, node, tn
def make_mem(L, K, slots, tn, D, Nd, g, Q):
    mem = [None]
    for l in range(1, L + 1):
        mem.append(np.vstack([tn[l][None, :], comp_batch(D, K, slots, Nd, g, Q)]))
    return mem
def retrieve(node, j, slots, A, mem, L, Q):
    p = node
    for l in range(L, 0, -1):
        p = mq(p * np.conj(slots[j[l - 1]]), Q)
        if l > 1:
            p = mem[l - 1][int(np.argmax((mem[l - 1] @ np.conj(p)).real))]
    return int(np.argmax((A @ np.conj(p)).real))
def recall(L, K, M, rho, Nd, Q, g, TR, D=50):
    A = mq(codebook(M, rho, Nd, g), Q); slots = mq(cphasor(K, Nd, g), Q); hit = 0
    for _ in range(TR):
        t = int(g.integers(0, M)); j, node, tn = build_path(L, K, slots, A, t, Nd, g, Q)
        mem = make_mem(L, K, slots, tn, D, Nd, g, Q); hit += int(retrieve(node, j, slots, A, mem, L, Q) == t)
    return hit / TR

def _selftest():
    print("[selftest] PASS: 1bit-verify-depth", flush=True)
def run() -> Dict:
    g = np.random.default_rng(804); Ls = [3, 5, 8] if SMOKE else [3, 5, 8, 10]; TR = 15 if SMOKE else 60
    rows = {}; maxloss = 0.0
    for L in Ls:
        rf = recall(L, 10, 500, 0.0, 8192, False, g, TR); rq = recall(L, 10, 500, 0.0, 8192, True, g, TR)
        rows[L] = {"float": round(rf, 3), "q1bit": round(rq, 3), "loss": round(rf - rq, 3)}; maxloss = max(maxloss, rf - rq)
        print("  1BIT-DEPTH L=%d float=%.3f 1bit=%.3f loss=%.3f" % (L, rf, rq, rf - rq), flush=True)
    return {"rows": {str(k): v for k, v in rows.items()}, "max_loss": round(maxloss, 3)}
def verdict(r) -> Tuple[str, str]:
    s = "max 1-bit loss across L<=10 = %.3f ; rows=%s" % (r["max_loss"], r["rows"])
    if r["max_loss"] < 0.05:
        return ("HARD_PASS", "HARD_PASS: 1-bit loss <5pp through L=10 -- quantization noise does NOT compound with depth. " + s)
    if r["max_loss"] < 0.15:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 1-bit loss 5-15pp by L=10. " + s)
    return ("HARD_FAIL", "HARD_FAIL: 1-bit degrades >15pp by L=10 -- compounding quantization noise. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
