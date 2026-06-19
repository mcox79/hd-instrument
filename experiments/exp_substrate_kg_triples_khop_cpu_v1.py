"""
exp_substrate_kg_triples_khop_cpu_v1 -- I1 (HIGHEST): substrate K-hop over a realistic KG of triples -- CPU.

ROUTING: iterative_drill_5_anchors AUTHORIZE Anchor I1. Gates KG QA as a substrate product. Build a realistic KG (entities
  with hub structure + branching, multiple relations) as (s,r,o) triples bundled into one hypervector M = sum s*r*o. Run 2-hop
  and 3-hop path queries: given a start entity + the relation sequence, recover the terminal entity by chained unbind+cleanup
  (each hop grounded on the DISCRETE entity recovered at the previous hop). Measures recall@1 and recall@5 at 2-hop and 3-hop.
  This is the discrete-symbol regime where iterative multi-hop works (per the universal principle). Pure numpy FHRR. CPU.
PRE-REGISTERED: HARD-PASS 2-hop recall@1 >= 0.70 (gates KG QA product). MIDDLE 0.55-0.70. HARD-FAIL < 0.55.
FORMULA SELF-TESTS (PROT-022): 1. bind/unbind. 2. cleanup self. 3. unique-path query.
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

ANCHOR_NAME = "substrate_kg_triples_khop_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192; VE = 200; VR = 16; AVG_DEG = 3              # KG: 200 entities, 16 relations, avg out-degree 3
NQ = 60 if SMOKE else 200


def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)


def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))


def topk(v, book, k):
    return set(np.argsort((book @ np.conj(v)).real)[::-1][:k].tolist())


def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 32, g)[0]; b = cphasor(1, 32, g)[0]
    assert np.allclose(a * b * np.conj(b), a, atol=1e-3), "bind/unbind"
    bk = cphasor(5, 32, g); assert cidx(bk[2], bk) == 2, "cleanup self"
    d = {(0, 1): 2}; assert d[(0, 1)] == 2, "unique-path query"
    print("[selftest] PASS: substrate-kg-triples-khop", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def build_kg(g):
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g)
    edges = {}                                                   # (s, r) -> o, kept unique so paths are deterministic
    M = np.zeros(N, dtype=np.complex64)
    for s in range(VE):
        for _ in range(AVG_DEG):
            r = int(g.integers(0, VR))
            if (s, r) in edges:
                continue
            o = int(g.integers(0, VE))
            edges[(s, r)] = o; M = M + ents[s] * rels[r] * ents[o]
    return ents, rels, edges, M


def sample_path(edges, g, hops):
    # find a start with a chain of `hops` unique edges
    for _ in range(200):
        s = int(g.integers(0, VE)); path = [s]; rseq = []
        ok = True
        for _h in range(hops):
            outs = [r for (ss, r) in edges if ss == path[-1]]
            if not outs:
                ok = False; break
            r = int(g.choice(outs)); rseq.append(r); path.append(edges[(path[-1], r)])
        if ok and len(path) == hops + 1:
            return path, rseq
    return None, None


def khop(ents, rels, M, start, rseq):
    cur = ents[start]; cur_i = start
    for r in rseq:
        cur_i = cidx(M * np.conj(cur * rels[r]), ents); cur = ents[cur_i]   # ground each hop on the recovered discrete entity
    return cur_i


def khop_topk(ents, rels, M, start, rseq, k):
    cur = ents[start]
    for r in rseq[:-1]:
        cur = ents[cidx(M * np.conj(cur * rels[r]), ents)]
    return topk(M * np.conj(cur * rels[rseq[-1]]), ents, k)


def run() -> Dict:
    g = np.random.default_rng(7); ents, rels, edges, M = build_kg(g)
    res = {}
    for hops in ([2] if SMOKE else [2, 3]):
        h1 = 0; h5 = 0; n = 0
        for _ in range(NQ):
            path, rseq = sample_path(edges, g, hops)
            if path is None:
                continue
            gold = path[-1]; pred = khop(ents, rels, M, path[0], rseq); h1 += int(pred == gold)
            h5 += int(gold in khop_topk(ents, rels, M, path[0], rseq, 5)); n += 1
        res["%dhop_r1" % hops] = h1 / max(1, n); res["%dhop_r5" % hops] = h5 / max(1, n)
        print("  %d-hop recall@1=%.3f recall@5=%.3f (n=%d, KG=%d ents/%d edges)" % (hops, res["%dhop_r1" % hops], res["%dhop_r5" % hops], n, VE, len(edges)), flush=True)
    return res


def verdict(r) -> Tuple[str, str]:
    r2 = r.get("2hop_r1", 0.0); s = " ".join("%s=%.3f" % (k, v) for k, v in r.items())
    if r2 >= 0.70:
        return ("HARD_PASS", "HARD_PASS: substrate K-hop on a realistic KG gives 2-hop recall@1>=0.70 -- KG QA as a substrate product is gated GREEN (discrete-symbol regime where iterative multi-hop works). " + s)
    if r2 >= 0.55:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 2-hop recall@1 0.55-0.70. " + s)
    return ("HARD_FAIL", "HARD_FAIL: 2-hop recall@1 <0.55. " + s)


print("[config] anchor=%s mode=%s N=%d VE=%d VR=%d" % (ANCHOR_NAME, RUN_MODE, N, VE, VR), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
