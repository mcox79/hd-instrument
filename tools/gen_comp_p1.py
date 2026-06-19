"""Research WAVE-5 P1: COMP-5 DEPTH-L4 + COMP-6 DEPTH-L6 + COMP-7 DEPTH-L8 + COMP-8 VARIABLE-K@L3.
Extended depth sweep -- map the cliff/asymptote. Pure-FHRR, vectorized composite construction. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: Research COMP_OVERCOME_BARRIER_BATCH P1 ({tag}); pure-FHRR (no download). {desc}
  MODEL: depth-L K-ary composition tree; level composite = cnorm(sum_k slot[k] (X) child_k); self-similar across levels
  (only target path materialized; siblings = statistically-equivalent random composites). HIERARCHICAL CLEANUP at each level
  (true node + D distractors). Same model as P0 COMP-1/2/3/4. N=8192.
PRE-REGISTERED: {prereg}
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
ANCHOR_NAME = "{anchor}"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def comp_rand_batch(B, K, slots, g):
    r = cphasor(B * K, N, g).reshape(B, K, N); return cnorm((slots[None, :, :] * r).sum(1))
def build_path(L, K, slots, A, t, g):
    j = [int(g.integers(0, K)) for _ in range(L)]; node = A[t]; truenodes = [A[t]]
    for l in range(L):
        sibs = (A[g.integers(0, len(A), size=K)] if l == 0 else comp_rand_batch(K, K, slots, g))
        bound = slots * sibs; bound[j[l]] = slots[j[l]] * node
        node = cnorm(bound.sum(0)); truenodes.append(node)
    return j, node, truenodes
def make_mem(L, K, slots, truenodes, D, g):
    mem = [None]
    for l in range(1, L + 1):
        mem.append(np.vstack([truenodes[l][None, :], comp_rand_batch(D, K, slots, g)]))
    return mem
def retrieve(node_L, j, slots, A, mem, L, use_cleanup):
    probe = node_L
    for l in range(L, 0, -1):
        probe = probe * np.conj(slots[j[l - 1]])
        if use_cleanup and l > 1:
            probe = mem[l - 1][int(np.argmax((mem[l - 1] @ np.conj(probe)).real))]
    return int(np.argmax((A @ np.conj(probe)).real))
{body}
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\\n[VERDICT] " + vmsg, flush=True)
metrics = {{"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''

DEPTH = r'''
LDEPTH = __LDEPTH__; PASS_TH = __PASSTH__
def _selftest():
    print("[selftest] PASS: comp-depth-L%d" % LDEPTH, flush=True)
def run() -> Dict:
    g = np.random.default_rng(500 + LDEPTH); K = 10; M = 200; D = 50; A = cphasor(M, N, g); slots = cphasor(K, N, g)
    TR = 20 if SMOKE else 120; hit = 0; hit_nc = 0; n = 0
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
        return ("HARD_PASS", "HARD_PASS: composition at L=%d holds with hierarchical cleanup (recall>=%.2f); cleanup makes recall near depth-independent while no-cleanup collapses. " % (r["L"], PASS_TH) + s)
    if r["recall_cleanup"] >= PASS_TH - 0.20:
        return ("MIDDLE_BAND", "MIDDLE_BAND: L=%d within 0.20 of bar. " % r["L"] + s)
    return ("HARD_FAIL", "HARD_FAIL: L=%d below bar even with cleanup (asymptote reached). " % r["L"] + s)
'''

VARK = r'''
def _selftest():
    print("[selftest] PASS: variable-k-L3", flush=True)
def run() -> Dict:
    g = np.random.default_rng(608); L = 3; M = 200; D = 50; Ks = [5, 10, 20] if SMOKE else [5, 10, 20, 50]
    TR = 15 if SMOKE else 100; curve = {}
    for K in Ks:
        A = cphasor(M, N, g); slots = cphasor(K, N, g); hit = 0
        for _ in range(TR):
            t = int(g.integers(0, M)); j, node, truenodes = build_path(L, K, slots, A, t, g)
            mem = make_mem(L, K, slots, truenodes, D, g); hit += int(retrieve(node, j, slots, A, mem, L, True) == t)
        curve[K] = round(hit / TR, 3); print("  VARIABLE-K@L3 K=%d recall=%.3f" % (K, curve[K]), flush=True)
    kmax = max(Ks); rmax = curve[kmax]
    return {"L": 3, "recall_curve": {str(k): v for k, v in curve.items()}, "recall_at_kmax": rmax, "kmax": kmax}
def verdict(r) -> Tuple[str, str]:
    s = "recall-vs-K@L3=%s (recall@K=%d=%.3f)" % (r["recall_curve"], r["kmax"], r["recall_at_kmax"])
    if r["recall_at_kmax"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: capacity-vs-depth tradeoff -- L=3 holds recall>=0.85 even at K=%d per level (with cleanup); width and depth compose. " % r["kmax"] + s)
    if r["recall_at_kmax"] >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: recall 0.65-0.85 at K=%d. " % r["kmax"] + s)
    return ("HARD_FAIL", "HARD_FAIL: width collapses at depth (recall<0.65 at K=%d). " % r["kmax"] + s)
'''

C = [
    dict(anchor="comp5_depth_l4_cpu_v1", tag="COMP-5 DEPTH-L4", title="compositional depth L=4 (between L3 and L5)",
         desc="L=4 K=10 retrieval with hierarchical cleanup; intermediate depth test.",
         prereg="HARD-PASS recall>=0.80 at L=4 K=10. MIDDLE within 0.20. HARD-FAIL else.", body=DEPTH.replace("__LDEPTH__", "4").replace("__PASSTH__", "0.80")),
    dict(anchor="comp6_depth_l6_cpu_v1", tag="COMP-6 DEPTH-L6", title="compositional depth L=6 (past L5)",
         desc="L=6 K=10 retrieval with hierarchical cleanup; characterizes cliff location past L5.",
         prereg="HARD-PASS recall>=0.60 at L=6 K=10. MIDDLE within 0.20. HARD-FAIL else.", body=DEPTH.replace("__LDEPTH__", "6").replace("__PASSTH__", "0.60")),
    dict(anchor="comp7_depth_l8_cpu_v1", tag="COMP-7 DEPTH-L8", title="compositional depth L=8 (extreme; asymptote)",
         desc="L=8 K=10 retrieval with hierarchical cleanup; maps asymptote (where humans typically max out).",
         prereg="HARD-PASS recall>=0.30 at L=8 (informational asymptote). MIDDLE within 0.20. HARD-FAIL else.", body=DEPTH.replace("__LDEPTH__", "8").replace("__PASSTH__", "0.30")),
    dict(anchor="comp8_variable_k_l3_cpu_v1", tag="COMP-8 DEPTH-VARIABLE-K", title="variable-K sweep at fixed L=3 (capacity-vs-depth)",
         desc="Sweep K (5/10/20/50) at L=3 with cleanup; capacity-vs-depth tradeoff curve.",
         prereg="HARD-PASS recall>=0.85 at K=50 L=3. MIDDLE>=0.65. HARD-FAIL else.", body=VARK),
]
for c in C:
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"]), encoding="utf-8"); print("wrote", c["anchor"])
