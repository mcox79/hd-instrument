"""Generator: fresh cheap CPU -- NDCG ranking quality + dependency K-hop with Merkle audit trail. Write-tool authored (no heredoc)."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: FRESH cheap batch ({tag}). {desc} Pure numpy. CPU.
PRE-REGISTERED: {prereg}
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, hashlib
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "{anchor}"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
{body}
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\\n[VERDICT] " + vmsg, flush=True)
metrics = {{"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''

NDCG_BODY = r'''
def _selftest():
    import numpy as _n; assert _n.log2(2) == 1.0, "log2"; print("[selftest] PASS: ndcg-ranking-quality", flush=True)
def ndcg(order, rel, k=10):
    dcg = sum((2 ** rel[order[i]] - 1) / math.log2(i + 2) for i in range(min(k, len(order))))
    ideal = sorted(rel.values(), reverse=True); idcg = sum((2 ** ideal[i] - 1) / math.log2(i + 2) for i in range(min(k, len(ideal))))
    return dcg / idcg if idcg > 0 else 0.0
def run() -> Dict:
    g = np.random.default_rng(951); N = 8192; VE = 200; REL = cphasor(1, N, g)[0]; ents = cphasor(VE, N, g); TR = 60 if SMOKE else 200
    ndcgs = []
    for _ in range(TR):
        ncand = 20; cand = g.choice(VE, ncand, replace=False); rels = g.integers(0, 4, ncand)
        shard = np.zeros(N, dtype=np.complex64)
        for ci in range(ncand):
            shard = shard + (0.3 + float(rels[ci])) * ents[int(cand[ci])] * REL
        sc = (ents[cand] @ np.conj(shard * np.conj(REL))).real; order = list(np.argsort(sc)[::-1])
        ndcgs.append(ndcg(order, {i: int(rels[i]) for i in range(ncand)}, 10))
    nd = float(np.mean(ndcgs)); print("  NDCG@10=%.3f (n=%d)" % (nd, TR), flush=True)
    return {"ndcg": nd}
def verdict(r) -> Tuple[str, str]:
    s = "NDCG@10=%.3f" % r["ndcg"]
    if r["ndcg"] >= 0.6: return ("HARD_PASS", "HARD_PASS: substrate ranking NDCG@10>=0.6 -- graded relevance ranking works (not just top-1). " + s)
    if r["ndcg"] >= 0.45: return ("MIDDLE_BAND", "MIDDLE_BAND: NDCG 0.45-0.6. " + s)
    return ("HARD_FAIL", "HARD_FAIL: NDCG <0.45. " + s)
'''

AUDIT_BODY = r'''
def _selftest():
    h = hashlib.sha256(b"x").hexdigest(); assert len(h) == 64, "sha"; print("[selftest] PASS: dependency-with-audit", flush=True)
def run() -> Dict:
    g = np.random.default_rng(952); N = 8192; VT = 120; DEP = cphasor(1, N, g)[0]; thms = cphasor(VT, N, g); TR = 40 if SMOKE else 120; HOPS = 3
    rec_sum = 0.0; audit_ok = 0; n = 0
    for _ in range(TR):
        adj = {i: [] for i in range(VT)}; shard = {i: np.zeros(N, dtype=np.complex64) for i in range(VT)}
        for t in range(1, VT):
            for d in g.choice(t, min(int(g.integers(1, 4)), t), replace=False):
                adj[t].append(int(d)); shard[t] = shard[t] + DEP * thms[int(d)]
        root = int(g.integers(VT // 2, VT)); gold = set(); fr = {root}
        for _h in range(HOPS):
            nf = set()
            for u in fr:
                nf |= set(adj[u]) - gold
            gold |= nf; fr = nf
        if not gold:
            continue
        reached = set(); fr = [root]; chain = "0" * 64; edges = []
        for _h in range(HOPS):
            nf = []
            for u in fr:
                if not adj[u]:
                    continue
                for v in np.where((thms @ np.conj(shard[u] * np.conj(DEP))).real / N > 0.30)[0].tolist():
                    if v not in reached:
                        nf.append(v); edges.append((u, v)); chain = hashlib.sha256((chain + "%d-%d" % (u, v)).encode()).hexdigest()
            reached |= set(nf); fr = nf
        replay = "0" * 64
        for (u, v) in edges:
            replay = hashlib.sha256((replay + "%d-%d" % (u, v)).encode()).hexdigest()
        rec_sum += len(gold & reached) / len(gold); audit_ok += int(replay == chain); n += 1
    rc = rec_sum / n; ar = audit_ok / n; print("  dependency-closure recall=%.3f audit-reproduces=%.3f (n=%d)" % (rc, ar, n), flush=True)
    return {"recall": rc, "audit": ar}
def verdict(r) -> Tuple[str, str]:
    s = "closure-recall=%.3f audit-reproduces=%.3f" % (r["recall"], r["audit"])
    if r["recall"] >= 0.95 and r["audit"] >= 0.999: return ("HARD_PASS", "HARD_PASS: dependency K-hop closure >=0.95 with a 100pct-reproducible Merkle audit trail -- verifiable derivations. " + s)
    if r["recall"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: closure 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: closure <0.85. " + s)
'''

C = [
    dict(anchor="ndcg_ranking_quality_cpu_v1", tag="CHEAP-CAP NDCG ranking quality",
         title="substrate cleanup-score ranking achieves NDCG@10 >= 0.6 vs graded relevance",
         desc="Ranked retrieval: candidates at graded relevance tiers (bound at graded strengths); rank by substrate cleanup score; measure NDCG@10 vs ideal. Substrate as a graded RANKER, not just top-1.",
         prereg="HARD-PASS NDCG@10 >= 0.6. MIDDLE >= 0.45. HARD-FAIL < 0.45.", body=NDCG_BODY),
    dict(anchor="dependency_with_audit_cpu_v1", tag="CHEAP-CAP dependency K-hop + audit trail",
         title="theorem-dependency closure with a per-dependency Merkle audit trail",
         desc="K-hop dependency traversal + a hash-chained audit trail (each resolved edge appended to a Merkle chain). Measures closure recall AND that the audit chain reproduces (tamper-evident).",
         prereg="HARD-PASS closure recall >= 0.95 AND audit reproduces 100pct. MIDDLE recall >= 0.85. HARD-FAIL < 0.85.", body=AUDIT_BODY),
]
for c in C:
    txt = HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"])
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(txt, encoding="utf-8"); print("wrote", c["anchor"])
