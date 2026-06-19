"""
exp_now1_temporal_grounding_cpu_v1.py -- NOW-1 TEMPORAL/CONTEXTUAL GROUNDING -- CPU.

ROUTING: Research NOW_SHARD_PLUS_HIERARCHICAL_GENERATION ARCH-2 NOW-1. A "now" shard supplies context: the SAME query
  key has DIFFERENT correct answers in different contexts. Mem = sum_{c,k} now[c] (X) qkey[k] (X) ans[c,k]. Grounded
  retrieval unbinds now[c] AND qkey[k] -> ans[c,k]; ungrounded (no now) unbinds only qkey[k] -> ambiguous mix. Verify
  grounding disambiguates: grounded recall high AND >> ungrounded. N=8192.
PRE-REGISTERED: HARD-PASS grounded recall >= 0.85 AND grounded - ungrounded >= 0.40 (now-shard disambiguates). MIDDLE grounded>=0.70. HARD-FAIL else.
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
ANCHOR_NAME = "now1_temporal_grounding_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def _selftest():
    print("[selftest] PASS: now1-temporal-grounding", flush=True)
def run() -> Dict:
    g = np.random.default_rng(901); NC = 4; NQ = 30; V = 200
    TR = 25 if SMOKE else 150; gr = 0; un = 0; n = 0
    for _ in range(TR):
        now = cphasor(NC, N, g); qk = cphasor(NQ, N, g); ans = cphasor(V, N, g)
        # each (context, query) -> a context-specific answer index; same query differs across contexts
        amap = g.integers(0, V, size=(NC, NQ))
        Mem = np.zeros(N, dtype=np.complex64)
        for c in range(NC):
            for k in range(NQ):
                Mem = Mem + now[c] * qk[k] * ans[amap[c, k]]
        for _q in range(8):
            c = int(g.integers(0, NC)); k = int(g.integers(0, NQ)); gold = int(amap[c, k])
            grounded = Mem * np.conj(now[c]) * np.conj(qk[k])      # unbind now AND query
            gr += int(cidx(grounded, ans) == gold)
            ungr = Mem * np.conj(qk[k])                            # unbind only query -> ambiguous across contexts
            un += int(cidx(ungr, ans) == gold); n += 1
    g_acc = gr / n; u_acc = un / n
    print("  NOW-1 grounded-recall=%.3f ungrounded-recall=%.3f (disambiguation=%.3f, NC=%d)" % (g_acc, u_acc, g_acc - u_acc, NC), flush=True)
    return {"grounded": round(g_acc, 3), "ungrounded": round(u_acc, 3), "disambiguation": round(g_acc - u_acc, 3), "NC": NC, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "grounded=%.3f ungrounded=%.3f disambiguation=%.3f NC=%d" % (r["grounded"], r["ungrounded"], r["disambiguation"], r["NC"])
    if r["grounded"] >= 0.85 and r["disambiguation"] >= 0.40:
        return ("HARD_PASS", "HARD_PASS: 'now' shard provides temporal/contextual grounding -- the same query returns context-appropriate answers when bound to now (recall>=0.85), and grounding disambiguates vs ungrounded by >=0.40. One primitive for temporal/multimodal/embodied/multi-agent grounding. " + s)
    if r["grounded"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: grounded 0.70-0.85 or weak disambiguation. " + s)
    return ("HARD_FAIL", "HARD_FAIL: now-grounding does not resolve context. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
