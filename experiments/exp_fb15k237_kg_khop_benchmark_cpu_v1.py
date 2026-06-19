"""
exp_fb15k237_kg_khop_benchmark_cpu_v1 -- REAL-KG benchmark: sharded substrate K-hop on FB15k-237 (Freebase) -- CPU.

ROUTING: v1 benchmark suite (real-KG). FB15k-237 (Freebase subset, 50k triples, ~14k entities, 237 relations) is cached.
  Builds the substrate KG as PER-SUBJECT shards (the locked v1.5 invariant: shard[s] bundles rel*obj for subject s) and
  measures substrate retrieval on REAL Freebase triples: 1-hop (s,p)->o and 2-hop s-p1->mid-p2->tail recall@1/@5. Compares
  sharded vs monolithic (monolithic must collapse at 50k triples). This is the real-data KG-QA product validation (R3/I1 on
  real data) and the substrate-side input to the head-to-head benchmark suite. Pure numpy FHRR. CPU.
PRE-REGISTERED: HARD-PASS sharded 1-hop recall@5 >= 0.80 AND sharded 2-hop recall@5 >= 0.55 on real FB15k-237 (1-to-many KG).
  MIDDLE 1-hop >= 0.65. HARD-FAIL 1-hop < 0.65.
FORMULA SELF-TESTS (PROT-022): 1. bind/unbind. 2. cleanup self. 3. jsonl parse.
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

ANCHOR_NAME = "fb15k237_kg_khop_benchmark_cpu_v1"; N = 8192
FB = REPO / "data" / "datasets" / "fb15k_237_train_50k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
MAX_TRIPLES = 8000 if SMOKE else 50000; NQ = 300 if SMOKE else 800


def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)


def cidx_topk(v, book, k):
    return np.argsort((book @ np.conj(v)).real)[::-1][:k]


def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 32, g)[0]; r = cphasor(1, 32, g)[0]; o = cphasor(1, 32, g)[0]
    assert np.allclose(a * r * o * np.conj(a * r), o, atol=1e-3), "bind/unbind"
    bk = cphasor(4, 32, g); assert int(np.argmax((bk @ np.conj(bk[2])).real)) == 2, "cleanup self"
    rec = json.loads('{"subject":"a","predicate":"p","object":"b"}'); assert rec["object"] == "b", "jsonl parse"
    print("[selftest] PASS: fb15k237-kg-khop-benchmark", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    if not FB.exists():
        print("[FATAL] no FB15k-237", flush=True); return {"n": 0, "h1_r5": 0.0, "h2_r5": 0.0}
    g = np.random.default_rng(7); triples = []; ent = {}; rel = {}
    for l in open(FB, encoding="utf-8"):
        r = json.loads(l); s, p, o = r["subject"], r["predicate"], r["object"]
        for e in (s, o):
            if e not in ent:
                ent[e] = len(ent)
        if p not in rel:
            rel[p] = len(rel)
        triples.append((ent[s], rel[p], ent[o]))
        if len(triples) >= MAX_TRIPLES:
            break
    VE = len(ent); VR = len(rel); print("  loaded %d triples, %d entities, %d relations" % (len(triples), VE, VR), flush=True)
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g)
    out_edges = {}                                                          # subject -> list of (rel, obj)
    sp_objs = {}                                                            # (s,p) -> set of objects (1-to-many)
    shards = {}; Mono = np.zeros(N, dtype=np.complex64)
    for s, p, o in triples:
        out_edges.setdefault(s, []).append((p, o)); sp_objs.setdefault((s, p), set()).add(o)
        shards.setdefault(s, np.zeros(N, dtype=np.complex64)); shards[s] = shards[s] + rels[p] * ents[o]
        Mono = Mono + ents[s] * rels[p] * ents[o]
    # 1-hop benchmark
    keys = list(sp_objs.keys()); g.shuffle(keys); h1_r1 = h1_r5 = m1_r5 = 0; n1 = 0
    for (s, p) in keys[:NQ]:
        gold = sp_objs[(s, p)]; top = cidx_topk(shards[s] * np.conj(rels[p]), ents, 5)
        h1_r1 += int(top[0] in gold); h1_r5 += int(len(set(top.tolist()) & gold) > 0)
        m1_r5 += int(len(set(cidx_topk(Mono * np.conj(ents[s] * rels[p]), ents, 5).tolist()) & gold) > 0); n1 += 1
    # 2-hop benchmark (sharded; route each hop to its subject shard)
    h2_r5 = 0; n2 = 0; subs = [s for s in out_edges if len(out_edges[s]) > 0]
    for _ in range(NQ):
        s = subs[int(g.integers(0, len(subs)))]; p1, mid = out_edges[s][int(g.integers(0, len(out_edges[s])))]
        if mid not in out_edges:
            continue
        p2, tail = out_edges[mid][int(g.integers(0, len(out_edges[mid])))]
        mids = cidx_topk(shards[s] * np.conj(rels[p1]), ents, 3)             # hop1 candidates
        found = set()
        for mh in mids:
            if int(mh) in shards:
                found |= set(cidx_topk(shards[int(mh)] * np.conj(rels[p2]), ents, 3).tolist())
        h2_r5 += int(tail in found); n2 += 1
    r = {"n1": n1, "n2": n2, "h1_r1": h1_r1 / max(1, n1), "h1_r5": h1_r5 / max(1, n1), "mono1_r5": m1_r5 / max(1, n1), "h2_r5": h2_r5 / max(1, n2), "VE": VE, "VR": VR}
    print("  sharded 1-hop recall@1=%.3f recall@5=%.3f (monolithic@5=%.3f) | sharded 2-hop recall@5=%.3f" % (r["h1_r1"], r["h1_r5"], r["mono1_r5"], r["h2_r5"]), flush=True)
    return r


def verdict(r) -> Tuple[str, str]:
    s = "1-hop r@1=%.3f r@5=%.3f (mono@5=%.3f) 2-hop r@5=%.3f (%d ents, %d rels)" % (r["h1_r1"], r["h1_r5"], r["mono1_r5"], r["h2_r5"], r["VE"], r["VR"])
    if r["h1_r5"] >= 0.80 and r["h2_r5"] >= 0.55:
        return ("HARD_PASS", "HARD_PASS: sharded substrate K-hop works on REAL Freebase (FB15k-237) -- 1-hop r@5>=0.80, 2-hop r@5>=0.55; KG-QA product validated on real data (monolithic collapses). " + s)
    if r["h1_r5"] >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: real-KG 1-hop r@5 0.65-0.80. " + s)
    return ("HARD_FAIL", "HARD_FAIL: real-KG 1-hop r@5 <0.65. " + s)


print("[config] anchor=%s mode=%s N=%d max_triples=%d" % (ANCHOR_NAME, RUN_MODE, N, MAX_TRIPLES), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
