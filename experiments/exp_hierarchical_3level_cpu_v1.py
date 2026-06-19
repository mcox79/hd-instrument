"""
exp_hierarchical_3level_cpu_v1.py -- domain -> category -> item 3-level hierarchical retrieval -- CPU.

ROUTING: deep-batch (3-level hierarchy navigation). A 3-level taxonomy (domain -> category -> item) stored via nested binding; query a (domain, category) path to retrieve its items. Tests deeper faceted navigation than the 2-level cell. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS path-conditioned item recall >= 0.85 at 3 levels. MIDDLE >= 0.70. HARD-FAIL < 0.70.
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
ANCHOR_NAME = "hierarchical_3level_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def topk(v, book, k):
    return set(np.argsort((book @ np.conj(v)).real)[::-1][:k].tolist())

def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 32, g)[0]; b = cphasor(1, 32, g)[0]; assert np.allclose(a * b * np.conj(a), b, atol=1e-3), "bind"; print("[selftest] PASS: hierarchical-3level", flush=True)
def run() -> Dict:
    g = np.random.default_rng(215); N = 8192; ND = 6; NC = 5; PER = 4; doms = cphasor(ND, N, g); cats = cphasor(NC, N, g); V = ND * NC * PER; items = cphasor(V, N, g)
    M = np.zeros(N, dtype=np.complex64); idx = 0; member = {}
    for d in range(ND):
        for c in range(NC):
            for p in range(PER):
                M = M + doms[d] * cats[c] * items[idx]; member.setdefault((d, c), set()).add(idx); idx += 1
    hit = 0; tot = 0
    for d in range(ND):
        for c in range(NC):
            rec = M * np.conj(doms[d] * cats[c]); top = topk(rec, items, PER); hit += len(top & member[(d, c)]); tot += PER
    rec = hit / tot; print("  3-level path-conditioned recall=%.3f (D=%d C=%d PER=%d)" % (rec, ND, NC, PER), flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "3-level recall=%.3f" % r["recall"]
    if r["recall"] >= 0.85: return ("HARD_PASS", "HARD_PASS: 3-level domain->category->item retrieval >=0.85 -- deep faceted navigation works. " + s)
    if r["recall"] >= 0.70: return ("MIDDLE_BAND", "MIDDLE_BAND: 3-level 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: 3-level <0.70. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
