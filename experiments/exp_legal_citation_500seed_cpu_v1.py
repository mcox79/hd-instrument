"""
exp_legal_citation_500seed_cpu_v1.py -- legal-citation snowball holds at 10x scale (500 seeds, 2000 cases) -- CPU.

ROUTING: v1.5 LOCK batch (B4 legal citation 500-seed demo). Extends the legal-citation snowball demo (PP-120) from 50 to 500 seeds over a 2000-case citation graph; validates that substrate K-hop 3-hop closure recovery holds at 10x demo scale (legal-pitch dataset). Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS 3-hop closure recovery >= 0.95 across 500 seeds at 2000 cases. MIDDLE >= 0.85. HARD-FAIL < 0.85.
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
ANCHOR_NAME = "legal_citation_500seed_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 64, g)[0]; R = cphasor(1, 64, g)[0]; b = cphasor(1, 64, g)[0]
    assert np.allclose(a * R * b * np.conj(a * R), b, atol=1e-3), "bind/unbind"; print("[selftest] PASS: legal-citation-500seed", flush=True)
def run() -> Dict:
    g = np.random.default_rng(82); N = 8192; VC = 800 if SMOKE else 2000; AVG = 3; NSEED = 100 if SMOKE else 500; THRESH = 0.18
    cases = cphasor(VC, N, g); CITES = cphasor(1, N, g)[0]; adj = {i: [] for i in range(VC)}; M = np.zeros(N, dtype=np.complex64)
    for i in range(VC):
        outs = g.choice(VC, size=int(g.integers(1, AVG + 2)), replace=False)
        for o in outs:
            if int(o) != i and int(o) not in adj[i]:
                adj[i].append(int(o)); M = M + cases[i] * CITES * cases[int(o)]
    def tclose(seed, hops=3):
        seen = set(); fr = {seed}
        for _ in range(hops):
            nf = set()
            for u in fr:
                nf |= set(adj[u]) - seen
            seen |= nf; fr = nf
        return seen
    def snow(seed, hops=3):
        reached = set(); fr = {seed}
        for _ in range(hops):
            nf = set()
            for u in fr:
                sc = (cases @ np.conj(M * np.conj(cases[u] * CITES))).real / N
                for v in np.where(sc > THRESH)[0].tolist():
                    if v not in reached and v != u:
                        nf.add(int(v))
            reached |= nf; fr = nf
            if not fr:
                break
        return reached
    recs = []
    seeds = g.choice(VC, NSEED, replace=False)
    for seed in seeds:
        tc = tclose(int(seed))
        if tc:
            recs.append(len(tc & snow(int(seed))) / len(tc))
    rec = float(np.mean(recs)); print("  3-hop closure recovery=%.3f (%d seeds, %d cases)" % (rec, len(recs), VC), flush=True)
    return {"recall": rec, "cases": VC, "seeds": len(recs)}
def verdict(r) -> Tuple[str, str]:
    s = "closure-recovery=%.3f (%d seeds, %d cases)" % (r["recall"], r["seeds"], r["cases"])
    if r["recall"] >= 0.95: return ("HARD_PASS", "HARD_PASS: legal-citation snowball holds >=0.95 closure at 10x demo scale -- legal-pitch dataset validated. " + s)
    if r["recall"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: closure 0.85-0.95 at scale. " + s)
    return ("HARD_FAIL", "HARD_FAIL: closure <0.85 at scale. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
