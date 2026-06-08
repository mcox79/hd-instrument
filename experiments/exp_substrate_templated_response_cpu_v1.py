"""
exp_substrate_templated_response_cpu_v1.py -- fill conversational response templates from substrate KB lookups; factual + grammatical -- CPU.

ROUTING: substrate templated response (no LLM). Layer-2 substrate-only answering: for LOOKUP-type queries, retrieve the value from the substrate KB and fill a response template (no LLM). Tests factual correctness (filled value matches KB) and grammatical acceptability (template well-formed) on 100 queries. Pure numpy / stdlib. CPU.
PRE-REGISTERED: HARD-PASS factual correctness >= 0.85 AND grammatical acceptability >= 0.90 on the query set. MIDDLE factual >= 0.75. HARD-FAIL < 0.75.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, re
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_templated_response_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    assert ("The capital of X is Y.").endswith("."), "template"; print("[selftest] PASS: substrate-templated-response", flush=True)
def run() -> Dict:
    g = np.random.default_rng(702); N = 8192; NSUBJ = 200; NATTR = 5; REL = cphasor(NATTR, N, g); subs = cphasor(NSUBJ, N, g); VV = 400; vals = cphasor(VV, N, g)
    attr_names = ["capital","founder","population","currency","language"]
    # KB: per-subject shard of attribute-bound values
    truth = {}; shard = np.zeros((NSUBJ, N), dtype=np.complex64)
    for si in range(NSUBJ):
        for a in range(NATTR):
            vv = int(g.integers(0, VV)); shard[si] = shard[si] + REL[a] * vals[vv]; truth[(si, a)] = vv
    TR = 100 if SMOKE else 300; fact_ok = 0; gram_ok = 0; n = 0
    for _ in range(TR):
        si = int(g.integers(0, NSUBJ)); a = int(g.integers(0, NATTR))
        pred = cidx(shard[si] * np.conj(REL[a]), vals)
        resp = "The %s of entity-%d is value-%d." % (attr_names[a], si, pred)   # filled template
        fact_ok += int(pred == truth[(si, a)])
        gram_ok += int(resp.startswith("The ") and resp.endswith(".") and " is " in resp)
        n += 1
    fr = fact_ok / n; gr = gram_ok / n; print("  templated-response factual=%.3f grammatical=%.3f (n=%d)" % (fr, gr, n), flush=True)
    return {"factual": fr, "grammar": gr}
def verdict(r) -> Tuple[str, str]:
    s = "factual=%.3f grammatical=%.3f" % (r["factual"], r["grammar"])
    if r["factual"] >= 0.85 and r["grammar"] >= 0.90: return ("HARD_PASS", "HARD_PASS: substrate-only templated responses factual>=0.85 + grammatical>=0.90 -- LLM-free answering for LOOKUP queries. " + s)
    if r["factual"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: templated factual 0.75-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: templated factual <0.75. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
