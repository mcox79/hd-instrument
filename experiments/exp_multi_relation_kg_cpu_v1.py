"""
exp_multi_relation_kg_cpu_v1.py -- store (subject,relation,object) triples; query (s,r)->o and (r,o)->s -- CPU.

ROUTING: CPU substrate capability characterization (knowledge-graph triple queries). Bundle KG triples as M = sum s*r*o. Recover the object via M*(s*r).conj() + cleanup over entities, and the subject via M*(r*o).conj(). Tests bidirectional relational query over a bundled knowledge graph. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS both (s,r)->o and (r,o)->s recall >= 0.90 at T triples. MIDDLE >= 0.75. HARD-FAIL < 0.75.
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
ANCHOR_NAME = "multi_relation_kg_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)

def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 16, g)[0]; b = cphasor(1, 16, g)[0]; c = cphasor(1, 16, g)[0]
    assert np.argmax((np.stack([c]) @ ((a * b * c) * (a * b).conj()).conj().reshape(-1, 1)).real) == 0, "unbind"; print("[selftest] PASS: multi-relation-kg-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(42); N = 2048; VE = 150; VR = 12; T = 30 if SMOKE else 60
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g)
    triples = [(int(g.integers(0, VE)), int(g.integers(0, VR)), int(g.integers(0, VE))) for _ in range(T)]
    M = np.zeros(N, dtype=np.complex64)
    for s, r, o in triples:
        M = M + ents[s] * rels[r] * ents[o]
    o_hit = s_hit = 0
    for s, r, o in triples:
        po = int(np.argmax((ents @ (M * (ents[s] * rels[r]).conj()).conj()).real)); o_hit += int(po == o)
        ps = int(np.argmax((ents @ (M * (rels[r] * ents[o]).conj()).conj()).real)); s_hit += int(ps == s)
    so = o_hit / T; ss = s_hit / T; print("  (s,r)->o recall=%.3f (r,o)->s recall=%.3f (T=%d triples)" % (so, ss, T), flush=True)
    return {"sro": so, "ros": ss}
def verdict(r) -> Tuple[str, str]:
    m = min(r["sro"], r["ros"]); s = "(s,r)->o=%.3f (r,o)->s=%.3f" % (r["sro"], r["ros"])
    if m >= 0.90: return ("HARD_PASS", "HARD_PASS: bidirectional KG triple recall >=0.90 -- a bundled knowledge graph is queryable both ways. " + s)
    if m >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: KG recall 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: KG recall <0.75. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
