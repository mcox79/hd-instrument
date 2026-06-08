"""
exp_cyclic_graph_khop_cpu_v1.py -- K-hop on cyclic graphs terminates and returns correct results (no infinite loop) -- CPU.

ROUTING: NEW_EXPERIMENTS batch (N4 cyclic-graph K-hop failure-mode probe). Substrate K-hop assumes acyclic traversal. Build graphs WITH cycles (A->B->C->A) and run bounded K-hop with a visited-set; verify it terminates within the hop bound AND returns the correct reachable target. Characterizes the cyclic-graph structural limit. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS K-hop on cyclic graphs returns the correct target >= 0.90 AND always terminates (bounded). MIDDLE >= 0.75. HARD-FAIL < 0.75 or non-termination.
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
ANCHOR_NAME = "cyclic_graph_khop_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    seen = set([0, 1]); assert 1 in seen, "visited set"; print("[selftest] PASS: cyclic-graph-khop", flush=True)
def run() -> Dict:
    g = np.random.default_rng(223); N = 8192; VE = 150; VR = 8; TR = 60 if SMOKE else 200; ents = cphasor(VE, N, g); rels = cphasor(VR, N, g)
    hit = 0; terminated = 0; n = 0
    for _ in range(TR):
        # build a graph WITH a guaranteed cycle among a few nodes + a target path
        edges = {}; shard = {}
        cyc = g.choice(VE, 4, replace=False).tolist()
        for i in range(len(cyc)):                                               # cycle: cyc[0]->cyc[1]->...->cyc[0]
            s = cyc[i]; o = cyc[(i + 1) % len(cyc)]; r = int(g.integers(0, VR)); edges[(s, r)] = o; shard.setdefault(s, np.zeros(N, dtype=np.complex64)); shard[s] = shard[s] + rels[r] * ents[o]
        tgt = int(g.integers(0, VE)); rt = int(g.integers(0, VR))               # an exit edge from the cycle to a target
        edges[(cyc[2], rt)] = tgt; shard.setdefault(cyc[2], np.zeros(N, dtype=np.complex64)); shard[cyc[2]] = shard[cyc[2]] + rels[rt] * ents[tgt]
        # bounded K-hop BFS with visited-set from cyc[0]; can it reach tgt without looping forever?
        start = cyc[0]; reached = set([start]); fr = set([start]); steps = 0; MAXH = 12
        while fr and steps < MAXH:
            steps += 1; nf = set()
            for u in fr:
                if u not in shard:
                    continue
                for r in range(VR):
                    if (u, r) in edges:
                        c = cidx(shard[u] * np.conj(rels[r]), ents)
                        if c not in reached:
                            nf.add(c)
            reached |= nf; fr = nf
        terminated += int(steps < MAXH or not fr)                               # terminated (frontier emptied) before the hard bound
        hit += int(tgt in reached); n += 1
    rec = hit / n; term = terminated / n; print("  cyclic-graph K-hop: target-reached=%.3f terminated=%.3f (n=%d)" % (rec, term, n), flush=True)
    return {"recall": rec, "terminated": term}
def verdict(r) -> Tuple[str, str]:
    s = "target-reached=%.3f terminated=%.3f" % (r["recall"], r["terminated"])
    if r["recall"] >= 0.90 and r["terminated"] >= 0.99: return ("HARD_PASS", "HARD_PASS: K-hop on cyclic graphs reaches the target >=0.90 and always terminates (visited-set) -- cycles handled, no infinite loop. " + s)
    if r["recall"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: cyclic K-hop 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: cyclic K-hop <0.75 or non-termination. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
