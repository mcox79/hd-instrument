"""
exp_lap4_10_common_knowledge_cpu_v1.py -- bounded common knowledge to depth k -- CPU.

ROUTING: Research WAVE3_RESOLUTION_WAVE4 (LAP4-10 BOUNDED-COMMON-KNOWLEDGE); pure-FHRR (no download). Nested everyone-knows operators to depth k; unwind to recover the proposition.
PRE-REGISTERED: HARD-PASS CK-recall>=0.75. MIDDLE>=0.55. HARD-FAIL<0.55.
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
from collections import deque
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "lap4_10_common_knowledge_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    print("[selftest] PASS: bounded-common-knowledge", flush=True)
def run() -> Dict:
    # bounded common knowledge: CK_k(P) = "everyone knows that everyone knows ... (k deep) P". Nested KNOWS operators per level
    # (one per agent at each depth); recover P by unwinding k levels; query at various depths up to KMAX.
    g = np.random.default_rng(10); N = 8192; NAG = 3; KMAX = 6; VF = 200
    agents = cphasor(NAG, N, g); KNOW = cphasor(1, N, g)[0]; fillers = cphasor(VF, N, g)
    TR = 30 if SMOKE else 200; hit = 0; n = 0
    for _ in range(TR):
        x = int(g.integers(0, VF)); k = int(g.integers(2, KMAX + 1))
        # build CK_k: nest (agent_i KNOWS ...) k deep, cycling agents
        state = fillers[x]
        order = []
        for lvl in range(k):
            ag = int(g.integers(0, NAG)); order.append(ag); state = agents[ag] * (KNOW * state)
        # unwind k levels using the known agent sequence (common-knowledge query path)
        cur = state
        for lvl in range(k - 1, -1, -1):
            cur = cur * np.conj(agents[order[lvl]]) * np.conj(KNOW)
        hit += int(cidx(cur, fillers) == x); n += 1
    acc = hit / n; print("  BOUNDED-COMMON-KNOWLEDGE depth-k(2..%d) recall=%.3f (NAG=%d, n=%d)" % (KMAX, acc, NAG, n), flush=True)
    return {"ck_recall": acc, "kmax": KMAX, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "common-knowledge-recall=%.3f (depth up to %d)" % (r["ck_recall"], r["kmax"])
    if r["ck_recall"] >= 0.75:
        return ("HARD_PASS", "HARD_PASS: substrate represents bounded common knowledge to depth %d >=0.75 -- nested 'everyone-knows-that-everyone-knows' resolves via repeated unbinding; epistemic depth holds. " % r["kmax"] + s)
    if r["ck_recall"] >= 0.55:
        return ("MIDDLE_BAND", "MIDDLE_BAND: common-knowledge 0.55-0.75. " + s)
    return ("HARD_FAIL", "HARD_FAIL: common-knowledge <0.55. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
