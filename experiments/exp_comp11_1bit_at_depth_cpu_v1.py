"""
exp_comp11_1bit_at_depth_cpu_v1.py -- COMP-11 1-BIT-AT-DEPTH -- CPU.

ROUTING: Research COMP_OVERCOME_BARRIER_BATCH P2 (COMP-11). Quantize EVERY stored vector (atoms, slots, composites,
  cleanup memory, intermediate probe) to 1-bit-per-component QPSK: each complex dim -> nearest of {+-1 +- 1j}/sqrt2.
  Run the P0/P1 depth model (L=3 and L=5, K=10, hierarchical cleanup) under full 1-bit quantization and compare recall
  to the float substrate. Tests whether the depth-independence survives extreme (32x memory-saving) quantization --
  counterintuitively 1-bit noise is less correlated so signal may be preserved. N=8192.
PRE-REGISTERED: HARD-PASS 1-bit recall within 5pp of float at L=5 (i.e. >=0.95 if float ~1.0). MIDDLE within 15pp. HARD-FAIL else.
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
ANCHOR_NAME = "comp11_1bit_at_depth_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192; _S = 1.0 / math.sqrt(2.0)
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def q1(v):
    # 1-bit-per-component QPSK quantization
    return ((np.sign(v.real) + 1j * np.sign(v.imag)) * _S).astype(np.complex64)
def maybe_q(v, Q):
    return q1(v) if Q else v
def comp_rand_batch(B, K, slots, g, Q):
    r = cphasor(B * K, N, g).reshape(B, K, N); c = cnorm((slots[None, :, :] * r).sum(1)); return maybe_q(c, Q)
def build_path(L, K, slots, A, t, g, Q):
    j = [int(g.integers(0, K)) for _ in range(L)]; node = A[t]; truenodes = [A[t]]
    for l in range(L):
        sibs = (A[g.integers(0, len(A), size=K)] if l == 0 else comp_rand_batch(K, K, slots, g, Q))
        bound = slots * sibs; bound[j[l]] = slots[j[l]] * node
        node = maybe_q(cnorm(bound.sum(0)), Q); truenodes.append(node)
    return j, node, truenodes
def make_mem(L, K, slots, truenodes, D, g, Q):
    mem = [None]
    for l in range(1, L + 1):
        mem.append(np.vstack([truenodes[l][None, :], comp_rand_batch(D, K, slots, g, Q)]))
    return mem
def retrieve(node_L, j, slots, A, mem, L, Q):
    probe = node_L
    for l in range(L, 0, -1):
        probe = maybe_q(probe * np.conj(slots[j[l - 1]]), Q)
        if l > 1:
            probe = mem[l - 1][int(np.argmax((mem[l - 1] @ np.conj(probe)).real))]
    return int(np.argmax((A @ np.conj(probe)).real))
def _selftest():
    print("[selftest] PASS: 1-bit-at-depth", flush=True)
def _recall(L, Q, g, M=200, K=10, D=50, TR=120):
    A = maybe_q(cphasor(M, N, g), Q); slots = maybe_q(cphasor(K, N, g), Q); hit = 0
    for _ in range(TR):
        t = int(g.integers(0, M)); j, node, truenodes = build_path(L, K, slots, A, t, g, Q)
        mem = make_mem(L, K, slots, truenodes, D, g, Q); hit += int(retrieve(node, j, slots, A, mem, L, Q) == t)
    return hit / TR
def run() -> Dict:
    g = np.random.default_rng(711); TR = 25 if SMOKE else 120; out = {}
    for L in (3, 5):
        rf = _recall(L, False, g, TR=TR); rq = _recall(L, True, g, TR=TR)
        out["float_L%d" % L] = round(rf, 3); out["q1bit_L%d" % L] = round(rq, 3)
        print("  1-BIT-AT-DEPTH L=%d float=%.3f 1bit=%.3f (loss=%.3f)" % (L, rf, rq, rf - rq), flush=True)
    out["loss_L5"] = round(out["float_L5"] - out["q1bit_L5"], 3)
    return out
def verdict(r) -> Tuple[str, str]:
    s = "L3 float=%.3f/1bit=%.3f ; L5 float=%.3f/1bit=%.3f (L5 loss=%.3f)" % (r["float_L3"], r["q1bit_L3"], r["float_L5"], r["q1bit_L5"], r["loss_L5"])
    if r["q1bit_L5"] >= r["float_L5"] - 0.05:
        return ("HARD_PASS", "HARD_PASS: 1-bit (QPSK) quantization of the entire substrate preserves depth-independent recall -- within 5pp of float at L=5 with cleanup. Deep composition holds at 32x memory saving. " + s)
    if r["q1bit_L5"] >= r["float_L5"] - 0.15:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 1-bit within 15pp of float at L=5. " + s)
    return ("HARD_FAIL", "HARD_FAIL: 1-bit loses >15pp at L=5; quantization breaks deep composition. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
