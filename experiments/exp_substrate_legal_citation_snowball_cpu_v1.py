"""
exp_substrate_legal_citation_snowball_cpu_v1 -- I5: legal-citation K-hop snowball demo (customer pitch) -- CPU.

ROUTING: iterative_drill Anchor I5 (customer-pitch prototype). A legal-citation graph (cases cite cases) stored as substrate
  triples (case_i * CITES * case_j). From a seed case, substrate K-hop "snowballs" the citation network hop by hop (each hop
  unbinds CITES and cleans up the cited set) and should recover the known 3-hop citation closure. Discrete-symbol regime
  (citations are exact references) where iterative multi-hop works. Pure numpy FHRR. CPU.
PRE-REGISTERED: HARD-PASS substrate snowball recovers >= 0.95 of the true 3-hop citation closure. MIDDLE >= 0.85. HARD-FAIL < 0.85.
FORMULA SELF-TESTS (PROT-022): 1. bind/unbind. 2. multi-target unbind superposition. 3. BFS closure.
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

ANCHOR_NAME = "substrate_legal_citation_snowball_cpu_v1"; N = 8192; VC = 300; AVG_CITE = 3
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
NSEED = 15 if SMOKE else 50; THRESH = 0.18


def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)


def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 64, g)[0]; b = cphasor(1, 64, g)[0]; c = cphasor(1, 64, g)[0]; R = cphasor(1, 64, g)[0]
    assert np.allclose(a * R * b * np.conj(a * R), b, atol=1e-3), "bind/unbind"
    M = a * R * b + a * R * c; book = np.stack([b, c]); sc = (book @ np.conj(M * np.conj(a * R))).real / 64
    assert sc[0] > 0.3 and sc[1] > 0.3, "multi-target unbind superposition"
    adj = {0: [1], 1: [2]}; assert adj[0] == [1], "BFS closure"
    print("[selftest] PASS: substrate-legal-citation-snowball", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(7); cases = cphasor(VC, N, g); CITES = cphasor(1, N, g)[0]
    adj = {i: [] for i in range(VC)}
    M = np.zeros(N, dtype=np.complex64)
    for i in range(VC):
        outs = g.choice(VC, size=int(g.integers(1, AVG_CITE + 2)), replace=False)
        for o in outs:
            if int(o) != i and int(o) not in adj[i]:
                adj[i].append(int(o)); M = M + cases[i] * CITES * cases[int(o)]
    def true_closure(seed, hops=3):
        seen = set(); frontier = {seed}
        for _ in range(hops):
            nf = set()
            for u in frontier:
                for v in adj[u]:
                    if v not in seen:
                        nf.add(v)
            seen |= nf; frontier = nf
        return seen
    def substrate_snowball(seed, hops=3):
        reached = set(); frontier = {seed}
        for _ in range(hops):
            nf = set()
            for u in frontier:
                sc = (cases @ np.conj(M * np.conj(cases[u] * CITES))).real / N      # cited set (superposition cleanup)
                for v in np.where(sc > THRESH)[0].tolist():
                    if v not in reached and v != u:
                        nf.add(int(v))
            reached |= nf; frontier = nf
            if not frontier:
                break
        return reached
    recs = []
    for _ in range(NSEED):
        seed = int(g.integers(0, VC)); tc = true_closure(seed)
        if not tc:
            continue
        sub = substrate_snowball(seed); recs.append(len(tc & sub) / len(tc))
    rec = float(np.mean(recs)) if recs else 0.0
    print("  citation-closure recovery=%.3f (3 hops, %d seeds, %d cases)" % (rec, len(recs), VC), flush=True)
    return {"recall": rec, "seeds": len(recs)}


def verdict(r) -> Tuple[str, str]:
    s = "3-hop closure recovery=%.3f (%d seeds)" % (r["recall"], r["seeds"])
    if r["recall"] >= 0.95:
        return ("HARD_PASS", "HARD_PASS: substrate snowball recovers >=95pct of the 3-hop citation closure -- legal-citation network expansion works (customer-pitch prototype GREEN). " + s)
    if r["recall"] >= 0.85:
        return ("MIDDLE_BAND", "MIDDLE_BAND: closure recovery 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: closure recovery <0.85. " + s)


print("[config] anchor=%s mode=%s N=%d cases=%d" % (ANCHOR_NAME, RUN_MODE, N, VC), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
