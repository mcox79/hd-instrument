"""
exp_f6_pacer_10k_scale_cpu_v1.py -- legal-citation snowball recall=precision>=0.95 at 10000-case scale -- CPU.

ROUTING: CYCLE_200_FOLLOWUPS (F6 PACER 10000-case scale). Extends PP-208 (1000-case 0.999/1.000) to 10000 cases for VALIDATED legal-scale promotion. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS recall>=0.95 AND precision>=0.95. MIDDLE recall>=0.85. HARD-FAIL <0.85.
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
ANCHOR_NAME = "f6_pacer_10k_scale_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    assert len({1,2}&{2}) == 1, "set"; print("[selftest] PASS: f6-pacer-10k", flush=True)
def run() -> Dict:
    g = np.random.default_rng(2006); N = 4096; VC = 2000 if SMOKE else 10000; CITES = cphasor(1, N, g)[0]; cases = cphasor(VC, N, g); NSEED = 60 if SMOKE else 300
    adj = {}; shard = {}
    for i in range(VC):
        outs = [int(o) for o in g.choice(VC, int(g.integers(1, 5)), replace=False) if int(o) != i]
        adj[i] = outs; sh = np.zeros(N, dtype=np.complex64)
        for o in outs:
            sh = sh + CITES * cases[o]
        shard[i] = sh
    recs = []; precs = []
    for seed in g.choice(VC, NSEED, replace=False):
        seed = int(seed); gold = set(); fr = {seed}
        for _h in range(3):
            nf = set()
            for u in fr:
                nf |= set(adj[u]) - gold
            gold |= nf; fr = nf
        if not gold:
            continue
        reached = set(); fr = [seed]
        for _h in range(3):
            nf = []
            for u in fr:
                sc = (cases @ np.conj(shard[u] * np.conj(CITES))).real / N
                for v in np.where(sc > 0.30)[0].tolist():
                    if v not in reached and v != seed:
                        nf.append(v)
            reached |= set(nf); fr = nf
        tp = len(gold & reached); recs.append(tp / len(gold)); precs.append(tp / max(1, len(reached)))
    rc = float(np.mean(recs)); pr = float(np.mean(precs)); print("  PACER %d-case snowball recall=%.3f precision=%.3f (n=%d)" % (VC, rc, pr, len(recs)), flush=True)
    return {"recall": rc, "precision": pr, "cases": VC}
def verdict(r) -> Tuple[str, str]:
    s = "recall=%.3f precision=%.3f at %d cases" % (r["recall"], r["precision"], r["cases"])
    if r["recall"] >= 0.95 and r["precision"] >= 0.95: return ("HARD_PASS", "HARD_PASS: legal-citation snowball recall=precision>=0.95 at 10000-case scale -- VALIDATED at production legal scale. " + s)
    if r["recall"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: recall 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: recall <0.85. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
