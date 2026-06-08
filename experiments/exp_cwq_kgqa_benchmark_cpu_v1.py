"""
exp_cwq_kgqa_benchmark_cpu_v1 -- v1 benchmark suite: substrate K-hop on REAL ComplexWebQuestions KG-QA -- CPU.

ROUTING: v1 benchmark suite (R3 real KG-QA). RoG-ComplexWebQuestions: real questions + real Freebase subgraphs (graph = list of [h,r,t]) +
  q_entity (start) + a_entity (answer). The strongest real-KG-QA benchmark: build the substrate KG per question from its graph
  as PER-SUBJECT shards (the locked invariant), run substrate K-hop (BFS up to 3 hops via unbind+cleanup) from q_entity, and
  check whether a_entity is recovered. Reports substrate recall vs an oracle (graph-reachable within K hops) to separate
  substrate fidelity from unreachable answers. Pure numpy FHRR. CPU.
PRE-REGISTERED: HARD-PASS substrate recovers the answer in >= 0.70 of graph-reachable questions. MIDDLE >= 0.55. HARD-FAIL < 0.55.
FORMULA SELF-TESTS (PROT-022): 1. bind/unbind. 2. cleanup self. 3. json graph parse.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "cwq_kgqa_benchmark_cpu_v1"; N = 4096; MAX_HOPS = 3
DS = REPO / "data" / "datasets" / "cwq_rog.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N_Q = 60 if SMOKE else 400; MAX_GRAPH = 4000


def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)


def cidx_topk(v, book, k):
    return np.argsort((book @ np.conj(v)).real)[::-1][:k]


def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 32, g)[0]; r = cphasor(1, 32, g)[0]; o = cphasor(1, 32, g)[0]
    assert np.allclose(a * r * o * np.conj(a * r), o, atol=1e-3), "bind/unbind"
    bk = cphasor(4, 32, g); assert int(np.argmax((bk @ np.conj(bk[3])).real)) == 3, "cleanup self"
    rec = json.loads('{"graph":[["a","r","b"]],"q_entity":["a"],"a_entity":["b"]}'); assert rec["graph"][0][2] == "b", "json graph parse"
    print("[selftest] PASS: cwq-kgqa-benchmark", flush=True)


def load(n):
    out = []
    if not DS.exists():
        return out
    for l in open(DS, encoding="utf-8"):
        r = json.loads(l); g = r.get("graph"); qe = r.get("q_entity"); ae = r.get("a_entity")
        if g and qe and ae and len(g) <= MAX_GRAPH:
            out.append(r)
        if len(out) >= n:
            break
    return out


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def reachable_oracle(adj, starts, golds, hops):
    seen = set(starts); fr = set(starts)
    for _ in range(hops):
        nf = set()
        for u in fr:
            nf |= adj.get(u, set())
        nf -= seen; seen |= nf; fr = nf
    return bool(seen & golds)


def run() -> Dict:
    data = load(N_Q)
    if not data:
        print("[FATAL] no webqsp", flush=True); return {"n": 0, "sub_recall": 0.0}
    g = np.random.default_rng(7); sub_hit = 0; oracle_hit = 0; n = 0
    for rec in data:
        triples = rec["graph"]; qe = set(rec["q_entity"]); ae = set(rec["a_entity"])
        ent = {}; rel = {}; adj = {}; out_rels_id = {}
        for h, r, t in triples:
            for e in (h, t):
                if e not in ent:
                    ent[e] = len(ent)
            if r not in rel:
                rel[r] = len(rel)
            adj.setdefault(h, set()).add(t); out_rels_id.setdefault(ent[h], set()).add(rel[r])
        starts = [s for s in qe if s in ent]; golds = set(ae)
        if not starts or not (golds & set(ent.keys())):
            continue
        oracle = reachable_oracle(adj, starts, golds, MAX_HOPS); oracle_hit += int(oracle)
        if not oracle:
            n += 1; continue
        VE = len(ent); VR = len(rel); ents = cphasor(VE, N, g); rels = cphasor(VR, N, g)
        shard = {}
        for h, r, t in triples:
            shard.setdefault(ent[h], np.zeros(N, dtype=np.complex64)); shard[ent[h]] = shard[ent[h]] + rels[rel[r]] * ents[ent[t]]
        # substrate K-hop BFS from starts via unbind+cleanup
        reached = set(ent[s] for s in starts); fr = set(reached)
        gold_ids = set(ent[a] for a in golds if a in ent)
        for _ in range(MAX_HOPS):
            nf = set()
            for u in fr:
                if u not in shard:
                    continue
                for rid in out_rels_id.get(u, set()):
                    for c in cidx_topk(shard[u] * np.conj(rels[rid]), ents, 2):
                        nf.add(int(c))
            nf -= reached; reached |= nf; fr = nf
            if reached & gold_ids:
                break
        sub_hit += int(bool(reached & gold_ids)); n += 1
    orc = oracle_hit / max(1, n); sub = sub_hit / max(1, oracle_hit)
    print("  ComplexWebQuestions: graph-reachable(<=%d hops)=%.3f | substrate recovers answer (of reachable)=%.3f (n=%d)" % (MAX_HOPS, orc, sub, n), flush=True)
    return {"n": n, "oracle": orc, "sub_recall": sub}


def verdict(r) -> Tuple[str, str]:
    s = "substrate-recall(of graph-reachable)=%.3f, graph-reachable rate=%.3f (n=%d)" % (r["sub_recall"], r["oracle"], r["n"])
    if r["sub_recall"] >= 0.70:
        return ("HARD_PASS", "HARD_PASS: substrate K-hop answers real ComplexWebQuestions KG-QA in >=0.70 of graph-reachable questions -- real KG-QA validated on real questions+graphs+answers. " + s)
    if r["sub_recall"] >= 0.55:
        return ("MIDDLE_BAND", "MIDDLE_BAND: ComplexWebQuestions substrate recall 0.55-0.70. " + s)
    return ("HARD_FAIL", "HARD_FAIL: ComplexWebQuestions substrate recall <0.55. " + s)


print("[config] anchor=%s mode=%s n_q=%d hops=%d" % (ANCHOR_NAME, RUN_MODE, N_Q, MAX_HOPS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
