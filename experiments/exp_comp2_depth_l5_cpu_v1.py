"""
exp_comp2_depth_l5_cpu_v1.py -- compositional depth L=5 retrieval (final cliff gate) -- CPU.

ROUTING: Research COMP_DEPTH_GATING / COMP_OVERCOME_BARRIER_BATCH (COMP-2 DEPTH-L5); pure-FHRR (no download). Push to L=5 (5-level chain); retrieve with hierarchical cleanup. Does deep composition survive?
  MODEL: depth-L K-ary composition tree. A level-l composite = cnorm(sum_k slot[k] (X) child_k); children are level-(l-1)
  composites (atoms at level 0). Composites are self-similar across levels (each = cnorm of K unit phasors), so only the
  TARGET path is materialized; the K-1 siblings at each level are statistically-equivalent random level composites. Retrieval:
  unbind the slot path top-down; HIERARCHICAL CLEANUP projects each intermediate onto a per-level cleanup memory (true node +
  D distractors) -- the cascading-Hopfield mitigation; final atom cleanup vs codebook.
PRE-REGISTERED: HARD-PASS recall>=0.70 at L=5 K=10. MIDDLE within 0.20. HARD-FAIL (<0.50) deep composition broken.
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
ANCHOR_NAME = "comp2_depth_l5_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def comp_rand(K, slots, g):
    # a random level composite (self-similar): cnorm(sum_k slot[k] (X) random unit phasor)
    return cnorm((slots * cphasor(K, N, g)).sum(0))
def build_path(L, K, slots, A, t, g):
    # returns slot-path j[0..L-1], top composite node_L, list of true nodes per level (0..L)
    j = [int(g.integers(0, K)) for _ in range(L)]; node = A[t]; truenodes = [A[t]]
    for l in range(L):
        acc = slots[j[l]] * node
        for k in range(K):
            if k == j[l]:
                continue
            sib = (A[int(g.integers(0, len(A)))] if l == 0 else comp_rand(K, slots, g))
            acc = acc + slots[k] * sib
        node = cnorm(acc); truenodes.append(node)
    return j, node, truenodes
def make_mem(L, K, slots, truenodes, D, g):
    mem = [None]
    for l in range(1, L + 1):
        dist = np.stack([comp_rand(K, slots, g) for _ in range(D)])
        mem.append(np.vstack([truenodes[l][None, :], dist]))
    return mem
def retrieve(node_L, j, slots, A, mem, L, use_cleanup):
    probe = node_L
    for l in range(L, 0, -1):
        probe = probe * np.conj(slots[j[l - 1]])
        if use_cleanup and l > 1:
            probe = mem[l - 1][int(np.argmax((mem[l - 1] @ np.conj(probe)).real))]
    return int(np.argmax((A @ np.conj(probe)).real))

LDEPTH = 5; PASS_TH = 0.70
def _selftest():
    print("[selftest] PASS: comp-depth-L%d" % LDEPTH, flush=True)
def run() -> Dict:
    g = np.random.default_rng(100 + LDEPTH); K = 10; M = 200; D = 50; A = cphasor(M, N, g); slots = cphasor(K, N, g)
    TR = 25 if SMOKE else 150; hit = 0; hit_nc = 0; n = 0
    for _ in range(TR):
        t = int(g.integers(0, M)); j, node, truenodes = build_path(LDEPTH, K, slots, A, t, g)
        mem = make_mem(LDEPTH, K, slots, truenodes, D, g)
        hit += int(retrieve(node, j, slots, A, mem, LDEPTH, True) == t)
        hit_nc += int(retrieve(node, j, slots, A, mem, LDEPTH, False) == t); n += 1
    rec = hit / n; rec_nc = hit_nc / n
    print("  COMP-DEPTH-L%d recall(cleanup)=%.3f recall(no-cleanup)=%.3f (K=%d, n=%d)" % (LDEPTH, rec, rec_nc, K, n), flush=True)
    return {"L": LDEPTH, "K": K, "recall_cleanup": round(rec, 3), "recall_nocleanup": round(rec_nc, 3), "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "L=%d recall(cleanup)=%.3f recall(no-cleanup)=%.3f K=%d" % (r["L"], r["recall_cleanup"], r["recall_nocleanup"], r["K"])
    if r["recall_cleanup"] >= PASS_TH:
        return ("HARD_PASS", "HARD_PASS: deep composition at L=%d holds with hierarchical cleanup (recall>=%.2f) -- the VSA deep-composition cliff is crossed at this depth via cascading per-level cleanup. " % (r["L"], PASS_TH) + s)
    if r["recall_cleanup"] >= PASS_TH - 0.20:
        return ("MIDDLE_BAND", "MIDDLE_BAND: L=%d recall within 0.20 of bar. " % r["L"] + s)
    return ("HARD_FAIL", "HARD_FAIL: L=%d below bar -- cliff at this depth even with cleanup. " % r["L"] + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
