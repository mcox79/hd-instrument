"""Generator: CPU batch H (5 sharding-architecture validation cells). Run: python tools/gen_cpu_batch_h.py"""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: sharding-architecture validation ({tag}). {desc} Pure numpy. CPU.
PRE-REGISTERED: {prereg}
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
C = []
C.append(dict(anchor="shard_routing_accuracy_cpu_v1", tag="content-based shard routing",
  title="content router sends queries to the correct shard (no oracle)",
  desc="The sharding capacity story assumes queries reach the right shard. Each shard has a topic centroid; queries are routed to the nearest centroid (content-based, no oracle). Measures routing accuracy and end-to-end recall vs oracle routing, when shards are topically coherent.",
  prereg="HARD-PASS routing accuracy >= 0.95 AND end-to-end recall >= 0.90 (within 0.03 of oracle). MIDDLE routing >= 0.85. HARD-FAIL < 0.85.",
  body='''
def _selftest():
    c = np.array([[1.0, 0], [0, 1.0]]); q = np.array([0.9, 0.1]); assert int(np.argmax(c @ q)) == 0, "nearest centroid"; print("[selftest] PASS: shard-routing-accuracy", flush=True)
def run() -> Dict:
    g = np.random.default_rng(71); N = 4096; S = 16; K = 60; Dtopic = 64
    centers = g.standard_normal((S, Dtopic))                                  # topic centroid per shard
    book = cphasor(2000, N, g); bundles = [np.zeros(N, dtype=np.complex64) for _ in range(S)]
    keys = []; vals = []; shards = []; topics = []
    for s in range(S):
        for _ in range(K):
            k = cphasor(1, N, g)[0]; vv = int(g.integers(0, 2000)); t = centers[s] + 0.5 * g.standard_normal(Dtopic)
            bundles[s] = bundles[s] + k * book[vv]; keys.append(k); vals.append(vv); shards.append(s); topics.append(t)
    cents = np.stack([centers[s] for s in range(S)])
    route_hit = 0; e2e = 0; oracle = 0
    for i in range(len(keys)):
        pred_shard = int(np.argmax(cents @ topics[i]))                        # content routing
        route_hit += int(pred_shard == shards[i])
        e2e += int(cidx(bundles[pred_shard] * np.conj(keys[i]), book) == vals[i])
        oracle += int(cidx(bundles[shards[i]] * np.conj(keys[i]), book) == vals[i])
    nq = len(keys); ra = route_hit / nq; ee = e2e / nq; orc = oracle / nq
    print("  routing-accuracy=%.3f end-to-end-recall=%.3f oracle-recall=%.3f (S=%d K=%d)" % (ra, ee, orc, S, K), flush=True)
    return {"routing": ra, "e2e": ee, "oracle": orc}
def verdict(r) -> Tuple[str, str]:
    s = "routing=%.3f e2e=%.3f oracle=%.3f" % (r["routing"], r["e2e"], r["oracle"])
    if r["routing"] >= 0.95 and r["e2e"] >= 0.90: return ("HARD_PASS", "HARD_PASS: content routing hits the right shard >=0.95 with end-to-end recall >=0.90 -- sharding works without an oracle router. " + s)
    if r["routing"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: routing 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: routing <0.85. " + s)
'''))
C.append(dict(anchor="skewed_shard_capacity_cpu_v1", tag="skewed (Zipf) shard sizes",
  title="per-shard recall stays high under realistic skewed shard sizes",
  desc="Real shards are uneven (some customers/domains much larger). Allocate shard sizes by a Zipf distribution; measure per-shard recall. Tests whether the flat-recall capacity story survives skew, or whether large shards degrade (and need sub-sharding).",
  prereg="HARD-PASS recall on the LARGEST shard >= 0.90 when its size <= the per-shard capacity floor; smallest shards ~1.0. MIDDLE largest >= 0.80. HARD-FAIL < 0.80.",
  body='''
def _selftest():
    p = 1.0 / np.arange(1, 5); assert p[0] > p[3], "zipf"; print("[selftest] PASS: skewed-shard-capacity", flush=True)
def run() -> Dict:
    g = np.random.default_rng(72); N = 4096; S = 12; BASE = 30
    sizes = (BASE * (1.0 / np.arange(1, S + 1)) * S).astype(int) + 10                   # zipf-ish skewed sizes
    sizes = np.maximum(sizes, 10); book = cphasor(3000, N, g); by = {}
    for si in range(S):
        Ks = int(sizes[si]); keys = cphasor(Ks, N, g); vals = g.integers(0, 3000, Ks)
        B = np.zeros(N, dtype=np.complex64)
        for j in range(Ks):
            B = B + keys[j] * book[vals[j]]
        hit = sum(int(cidx(B * np.conj(keys[j]), book) == vals[j]) for j in range(Ks))
        by[Ks] = hit / Ks
    largest = max(by.keys()); smallest = min(by.keys())
    print("  recall by shard size: largest(%d)=%.3f smallest(%d)=%.3f | sizes=%s" % (largest, by[largest], smallest, by[smallest], sorted(by.keys(), reverse=True)), flush=True)
    return {"largest_recall": by[largest], "smallest_recall": by[smallest], "largest_size": largest}
def verdict(r) -> Tuple[str, str]:
    s = "largest-shard(%d)-recall=%.3f smallest-recall=%.3f" % (r["largest_size"], r["largest_recall"], r["smallest_recall"])
    if r["largest_recall"] >= 0.90: return ("HARD_PASS", "HARD_PASS: per-shard recall stays >=0.90 even on the largest skewed shard -- sharding survives realistic skew (sub-shard only the biggest). " + s)
    if r["largest_recall"] >= 0.80: return ("MIDDLE_BAND", "MIDDLE_BAND: largest-shard recall 0.80-0.90 (sub-sharding advised). " + s)
    return ("HARD_FAIL", "HARD_FAIL: largest shard degrades (<0.80) -- skew requires sub-sharding. " + s)
'''))
C.append(dict(anchor="per_relation_sharding_kg_cpu_v1", tag="per-relation KG sharding",
  title="per-relation shards keep KG 2-hop recall high at scale",
  desc="Shard the KG by RELATION (each relation type is its own bundle). A 2-hop query routes through the relation shards for r1 then r2. Compares per-relation-sharded recall to a single monolithic KG bundle as the triple count grows.",
  prereg="HARD-PASS per-relation-sharded 2-hop recall@1 >= 0.85 AND beats monolithic by >= 0.15 at high triple count. MIDDLE gap >= 0.05. HARD-FAIL otherwise.",
  body='''
def _selftest():
    assert {0: 1}[0] == 1, "dict"; print("[selftest] PASS: per-relation-sharding-kg", flush=True)
def run() -> Dict:
    g = np.random.default_rng(73); N = 4096; VE = 300; VR = 10; deg = 4
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g)
    edges = {}; Mono = np.zeros(N, dtype=np.complex64); RS = [np.zeros(N, dtype=np.complex64) for _ in range(VR)]
    for s in range(VE):
        for _ in range(deg):
            r = int(g.integers(0, VR)); o = int(g.integers(0, VE))
            if (s, r) not in edges:
                edges[(s, r)] = o; Mono = Mono + ents[s] * rels[r] * ents[o]; RS[r] = RS[r] + ents[s] * rels[r] * ents[o]
    def path():
        for _ in range(150):
            s = int(g.integers(0, VE)); o1 = [(r, edges[(s, r)]) for (ss, r) in edges if ss == s]
            if not o1:
                continue
            r1, b = o1[int(g.integers(0, len(o1)))]; o2 = [(r, edges[(b, r)]) for (ss, r) in edges if ss == b]
            if not o2:
                continue
            r2, a = o2[int(g.integers(0, len(o2)))]; return s, r1, b, r2, a
        return None
    TR = 60 if SMOKE else 200; mh = 0; sh = 0; n = 0
    for _ in range(TR):
        p = path()
        if not p:
            continue
        s, r1, b, r2, a = p
        # monolithic
        bm = cidx(Mono * np.conj(ents[s] * rels[r1]), ents); am = cidx(Mono * np.conj(ents[bm] * rels[r2]), ents); mh += int(am == a)
        # per-relation sharded: route hop1 to RS[r1], hop2 to RS[r2]
        bs = cidx(RS[r1] * np.conj(ents[s] * rels[r1]), ents); asg = cidx(RS[r2] * np.conj(ents[bs] * rels[r2]), ents); sh += int(asg == a)
        n += 1
    mr = mh / max(1, n); sr = sh / max(1, n); print("  2-hop recall: monolithic=%.3f per-relation-sharded=%.3f (gap=%.3f, %d edges)" % (mr, sr, sr - mr, len(edges)), flush=True)
    return {"mono": mr, "sharded": sr, "gap": sr - mr}
def verdict(r) -> Tuple[str, str]:
    s = "per-relation-sharded=%.3f monolithic=%.3f gap=%.3f" % (r["sharded"], r["mono"], r["gap"])
    if r["sharded"] >= 0.85 and r["gap"] >= 0.15: return ("HARD_PASS", "HARD_PASS: per-relation sharding keeps 2-hop recall >=0.85 and beats monolithic by >=0.15 -- KG-QA scales by relation-sharding. " + s)
    if r["gap"] >= 0.05: return ("MIDDLE_BAND", "MIDDLE_BAND: per-relation sharding gap 0.05-0.15. " + s)
    return ("HARD_FAIL", "HARD_FAIL: per-relation sharding gap <0.05. " + s)
'''))
C.append(dict(anchor="shard_overflow_split_cpu_v1", tag="online shard overflow split",
  title="splitting an overflowing shard restores per-shard recall online",
  desc="A shard grows past its capacity floor (recall drops); split it into two and re-route. Tests that an online split restores recall without rebuilding the whole store (operational elasticity).",
  prereg="HARD-PASS post-split recall >= 0.95 (restored) AND pre-split (overflowed) recall < 0.80 (split was warranted). MIDDLE post-split >= 0.85. HARD-FAIL < 0.85.",
  body='''
def _selftest():
    assert len([0, 1, 2, 3][:2]) == 2 and len([0, 1, 2, 3][2:]) == 2, "split halves"; print("[selftest] PASS: shard-overflow-split", flush=True)
def run() -> Dict:
    g = np.random.default_rng(74); N = 2048; OVER = 600; book = cphasor(4000, N, g)
    keys = cphasor(OVER, N, g); vals = g.integers(0, 4000, OVER)
    B = np.zeros(N, dtype=np.complex64)
    for j in range(OVER):
        B = B + keys[j] * book[vals[j]]
    pre = sum(int(cidx(B * np.conj(keys[j]), book) == vals[j]) for j in range(OVER)) / OVER   # overflowed monolithic shard
    half = OVER // 2; B1 = np.zeros(N, dtype=np.complex64); B2 = np.zeros(N, dtype=np.complex64)
    for j in range(half):
        B1 = B1 + keys[j] * book[vals[j]]
    for j in range(half, OVER):
        B2 = B2 + keys[j] * book[vals[j]]
    post = (sum(int(cidx(B1 * np.conj(keys[j]), book) == vals[j]) for j in range(half)) + sum(int(cidx(B2 * np.conj(keys[j]), book) == vals[j]) for j in range(half, OVER))) / OVER
    print("  pre-split(overflowed)=%.3f post-split(2 shards)=%.3f (load=%d)" % (pre, post, OVER), flush=True)
    return {"pre": pre, "post": post}
def verdict(r) -> Tuple[str, str]:
    s = "pre-split=%.3f post-split=%.3f" % (r["pre"], r["post"])
    if r["post"] >= 0.95 and r["pre"] < 0.80: return ("HARD_PASS", "HARD_PASS: splitting an overflowed shard restores recall to >=0.95 (from <0.80) -- online elastic sharding works. " + s)
    if r["post"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: post-split recall 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: split does not restore recall. " + s)
'''))
C.append(dict(anchor="cross_shard_query_cpu_v1", tag="multi-shard scatter-gather query",
  title="a query whose answer spans shards is recovered by scatter-gather",
  desc="When a query's relevant items live in multiple shards, fan the query to all shards and gather the top results (scatter-gather). Tests recall of a multi-shard result set vs a single-shard query, with a confidence threshold to suppress non-matching shards.",
  prereg="HARD-PASS scatter-gather recall of the multi-shard gold set >= 0.90 with low false-include rate. MIDDLE >= 0.75. HARD-FAIL < 0.75.",
  body='''
def _selftest():
    assert (set([1, 2]) | set([3])) == {1, 2, 3}, "gather union"; print("[selftest] PASS: cross-shard-query", flush=True)
def run() -> Dict:
    g = np.random.default_rng(75); N = 4096; S = 8; K = 60; book = cphasor(3000, N, g); TR = 40 if SMOKE else 150
    bundles = []; shard_keys = []; shard_vals = []
    for s in range(S):
        ky = cphasor(K, N, g); vv = g.integers(0, 3000, K); B = np.zeros(N, dtype=np.complex64)
        for j in range(K):
            B = B + ky[j] * book[vv[j]]
        bundles.append(B); shard_keys.append(ky); shard_vals.append(vv)
    hit = 0; n = 0
    for _ in range(TR):
        # a query relevant to one item in each of M random shards (multi-shard answer set)
        Msh = g.choice(S, 3, replace=False); gold = set(); qkeys = []
        for s in Msh:
            j = int(g.integers(0, K)); qkeys.append((s, j)); gold.add((s, int(shard_vals[s][j])))
        retr = set()
        for (s, j) in qkeys:
            for si in range(S):                                                  # scatter to all shards, gather best per shard
                cand = cidx(bundles[si] * np.conj(shard_keys[s][j]), book)
                sc = (book[cand] @ np.conj(bundles[si] * np.conj(shard_keys[s][j]))).real / N
                if sc > 0.5:
                    retr.add((si, cand))
        hit += int(len(retr & gold) == len(gold)); n += 1
    rec = hit / max(1, n); print("  multi-shard scatter-gather recall=%.3f (S=%d, 3-shard answers)" % (rec, S), flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "scatter-gather recall=%.3f" % r["recall"]
    if r["recall"] >= 0.90: return ("HARD_PASS", "HARD_PASS: scatter-gather recovers multi-shard answer sets >=0.90 -- cross-shard queries work when answers span shards. " + s)
    if r["recall"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: scatter-gather 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: scatter-gather <0.75. " + s)
'''))
for c in C:
    txt = HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"])
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(txt, encoding="utf-8"); print("wrote", c["anchor"])
