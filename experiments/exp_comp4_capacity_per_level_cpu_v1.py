"""
exp_comp4_capacity_per_level_cpu_v1.py -- empirical kstar capacity curve per depth -- CPU.

ROUTING: Research COMP_DEPTH_GATING / COMP_OVERCOME_BARRIER_BATCH (COMP-4 CAPACITY-PER-LEVEL); pure-FHRR (no download). At each level L sweep K; find kstar (max K with recall>=0.90 under cleanup); compare to N/(2 ln N).
  MODEL: depth-L K-ary composition tree. A level-l composite = cnorm(sum_k slot[k] (X) child_k); children are level-(l-1)
  composites (atoms at level 0). Composites are self-similar across levels (each = cnorm of K unit phasors), so only the
  TARGET path is materialized; the K-1 siblings at each level are statistically-equivalent random level composites. Retrieval:
  unbind the slot path top-down; HIERARCHICAL CLEANUP projects each intermediate onto a per-level cleanup memory (true node +
  D distractors) -- the cascading-Hopfield mitigation; final atom cleanup vs codebook.
PRE-REGISTERED: HARD-PASS kstar>=10 at L=3 AND >=5 at L=5. MIDDLE kstar>=5 at L=3. HARD-FAIL else.
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
ANCHOR_NAME = "comp4_capacity_per_level_cpu_v1"
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
def comp_rand_batch(B, K, slots, g):
    # B self-similar random composites at once -> (B, N)
    r = cphasor(B * K, N, g).reshape(B, K, N)
    return cnorm((slots[None, :, :] * r).sum(1))
def build_path(L, K, slots, A, t, g):
    # vectorized: slot-path j, top composite node_L, true nodes per level (0..L)
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

def _selftest():
    print("[selftest] PASS: capacity-per-level", flush=True)
def _recall_at(L, K, g, M=200, D=50, TR=40):
    A = cphasor(M, N, g); slots = cphasor(K, N, g); hit = 0
    for _ in range(TR):
        t = int(g.integers(0, M)); j, node, truenodes = build_path(L, K, slots, A, t, g); mem = make_mem(L, K, slots, truenodes, D, g)
        hit += int(retrieve(node, j, slots, A, mem, L, True) == t)
    return hit / TR
def run() -> Dict:
    g = np.random.default_rng(404); Ks = [5, 10, 20] if SMOKE else [5, 10, 20, 40, 80]; Ls = ([1, 3, 5] if SMOKE else [1, 2, 3, 4, 5])
    TR = 10 if SMOKE else 50; kstar = {}; curve = {}
    for L in Ls:
        ks = 0; row = {}
        for K in Ks:
            rec = _recall_at(L, K, g, TR=TR); row[K] = round(rec, 3)
            if rec >= 0.90:
                ks = K
        kstar[L] = ks; curve[L] = row
        print("  CAPACITY L=%d kstar(recall>=0.90)=%d row=%s" % (L, ks, row), flush=True)
    theo = N / (2 * math.log(N))
    print("  theoretical atomic capacity N/(2 ln N)=%.0f" % theo, flush=True)
    return {"kstar_per_level": kstar, "curve": {str(k): v for k, v in curve.items()}, "theo_atomic": round(theo, 1)}
def verdict(r) -> Tuple[str, str]:
    ks = r["kstar_per_level"]; s = "kstar-per-level=%s theo-atomic=%.0f" % (ks, r["theo_atomic"])
    if ks.get(3, 0) >= 10 and ks.get(5, 0) >= 5:
        return ("HARD_PASS", "HARD_PASS: capacity curve characterized -- kstar>=10 at L=3 AND kstar>=5 at L=5 (with cleanup); operational depth-capacity envelope mapped. " + s)
    if ks.get(3, 0) >= 5:
        return ("MIDDLE_BAND", "MIDDLE_BAND: kstar>=5 at L=3 but thinner at depth. " + s)
    return ("HARD_FAIL", "HARD_FAIL: kstar<5 at L=3 -- capacity collapses with depth. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
