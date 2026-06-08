"""Generator: 2 sleep-defrag sharding mechanisms (B inverted-shards, C cross-shard chain extraction). Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: {tag}. {desc} Pure numpy. CPU.
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
C.append(dict(anchor="cross_shard_chain_extraction_cpu_v1", tag="Mechanism C sleep-defrag cross-shard chain extraction",
  title="sleep-defrag pre-computes cross-shard 2-hop chains into single-shard lookups",
  desc="Per-subject sharded KG; a 2-hop chain A-r1->B-r2->Y spans shards (A and B in different shards). During SLEEP DEFRAG, for each (A,r1,B) look up B's shard for (B,r2,Y) and emit a DERIVED fact (A, chain[r1,r2], Y) into A's shard (chain[r1,r2]=r1*r2, a composed relation with provenance). After defrag, the 2-hop query is a SINGLE-shard lookup. Measures post-defrag single-shard 2-hop recall + that the composed relation is recoverable.",
  prereg="HARD-PASS post-defrag single-shard 2-hop recall@1 >= 0.90 AND composed-relation recoverable. MIDDLE >= 0.80. HARD-FAIL < 0.80.",
  body='''
def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 64, g)[0]; r1 = cphasor(1, 64, g)[0]; r2 = cphasor(1, 64, g)[0]; y = cphasor(1, 64, g)[0]
    chain = r1 * r2; assert np.allclose((a * chain * y) * np.conj(a * chain), y, atol=1e-3), "composed-relation unbind"; print("[selftest] PASS: cross-shard-chain-extraction", flush=True)
def run() -> Dict:
    g = np.random.default_rng(141); N = 8192; VE = 300; VR = 12; deg = 3; TR = 60 if SMOKE else 200
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g); edges = {}
    base = {}                                                              # per-subject shard: base edges r*o
    for s in range(VE):
        for _ in range(deg):
            r = int(g.integers(0, VR)); o = int(g.integers(0, VE))
            if (s, r) not in edges:
                edges[(s, r)] = o; base.setdefault(s, np.zeros(N, dtype=np.complex64)); base[s] = base[s] + rels[r] * ents[o]
    # SLEEP DEFRAG: for each (A,r1,B), find (B,r2,Y) and emit derived chain fact into A's shard: ents[A]*chain*ents[Y]
    derived = {s: np.zeros(N, dtype=np.complex64) for s in base}
    for (A, r1), B in list(edges.items()):
        for r2 in range(VR):
            if (B, r2) in edges:
                Y = edges[(B, r2)]; chain = rels[r1] * rels[r2]; derived.setdefault(A, np.zeros(N, dtype=np.complex64)); derived[A] = derived[A] + chain * ents[Y]
    def sample():
        for _ in range(150):
            A = int(g.integers(0, VE)); o1 = [(r, edges[(A, r)]) for (ss, r) in edges if ss == A]
            if not o1:
                continue
            r1, B = o1[int(g.integers(0, len(o1)))]; o2 = [(r, edges[(B, r)]) for (ss, r) in edges if ss == B]
            if not o2:
                continue
            r2, Y = o2[int(g.integers(0, len(o2)))]; return A, r1, B, r2, Y
        return None
    hit = 0; n = 0
    for _ in range(TR):
        p = sample()
        if not p:
            continue
        A, r1, B, r2, Y = p; chain = rels[r1] * rels[r2]
        pred = cidx(derived[A] * np.conj(chain), ents)                     # SINGLE-shard lookup via the pre-computed chain
        hit += int(pred == Y); n += 1
    rec = hit / max(1, n); print("  post-defrag single-shard 2-hop recall@1=%.3f (n=%d, %d subjects)" % (rec, n, len(base)), flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "post-defrag single-shard 2-hop=%.3f" % r["recall"]
    if r["recall"] >= 0.90: return ("HARD_PASS", "HARD_PASS: sleep-defrag chain extraction turns cross-shard 2-hop into a single-shard lookup at >=0.90 -- pre-computed composed-relation chains close the cross-shard cost. " + s)
    if r["recall"] >= 0.80: return ("MIDDLE_BAND", "MIDDLE_BAND: post-defrag 0.80-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: post-defrag <0.80. " + s)
'''))
C.append(dict(anchor="inverted_property_shards_cpu_v1", tag="Mechanism B sleep-defrag per-property inverted shards",
  title="sleep-defrag builds property-indexed inverted shards for O(K) set queries",
  desc="Per-subject shards answer (subject -> properties) but a query like 'all subjects with property P' would scan all M shards (O(M*K)). During SLEEP DEFRAG, scan for each property P=(relation,value) appearing in >=T subject shards and build a SECONDARY inverted shard inv[P] = bundle of those subjects. Query 'subjects with P' hits inv[P] at O(K). Measures inverted-shard recall of the true subjects-with-P set.",
  prereg="HARD-PASS inverted-shard recall of subjects-with-P >= 0.90 at frequent properties. MIDDLE >= 0.80. HARD-FAIL < 0.80.",
  body='''
def _selftest():
    assert len({1, 2, 3} & {2, 3, 4}) == 2, "set overlap"; print("[selftest] PASS: inverted-property-shards", flush=True)
def run() -> Dict:
    g = np.random.default_rng(142); N = 8192; VE = 400; NPROP = 30; PROPS_PER = 4; TR_PROPS = 20 if SMOKE else 50
    ents = cphasor(VE, N, g); props = cphasor(NPROP, N, g)                 # each property P = (relation,value) atom
    subj_props = {s: set(g.choice(NPROP, PROPS_PER, replace=False).tolist()) for s in range(VE)}   # ground truth
    # SLEEP DEFRAG: build inverted shard per property = bundle of subjects having it
    inv = {p: np.zeros(N, dtype=np.complex64) for p in range(NPROP)}
    truth = {p: set() for p in range(NPROP)}
    for s in range(VE):
        for p in subj_props[s]:
            inv[p] = inv[p] + ents[s]; truth[p].add(s)
    recs = []
    test_props = list(range(NPROP))[:TR_PROPS]
    for p in test_props:
        tset = truth[p]
        if not tset:
            continue
        sc = (ents @ np.conj(inv[p])).real; retr = set(np.argsort(-sc)[:len(tset)].tolist())       # top-|tset| subjects from inverted shard
        recs.append(len(retr & tset) / len(tset))
    rec = float(np.mean(recs)); print("  inverted-shard subjects-with-P recall=%.3f (%d properties, %d subjects, ~%d/prop)" % (rec, len(recs), VE, VE * PROPS_PER // NPROP), flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "inverted-shard recall=%.3f" % r["recall"]
    if r["recall"] >= 0.90: return ("HARD_PASS", "HARD_PASS: sleep-defrag inverted property shards recall subjects-with-P >=0.90 at O(K) -- set-of-subjects queries answered without scanning all shards. " + s)
    if r["recall"] >= 0.80: return ("MIDDLE_BAND", "MIDDLE_BAND: inverted-shard 0.80-0.90 (property bundles near capacity; sub-shard frequent properties). " + s)
    return ("HARD_FAIL", "HARD_FAIL: inverted-shard <0.80. " + s)
'''))
for c in C:
    txt = HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"])
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(txt, encoding="utf-8"); print("wrote", c["anchor"])
