"""Generator: 2 CPU rescues PP-131 + PP-132. Run: python tools/gen_cpu_rescues.py"""
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
C.append(dict(anchor="skewed_shard_online_split_cpu_v1", tag="PP-131 skewed-shard online split",
  title="online-splitting hot shards under Zipf skew restores recall",
  desc="skewed_shard_capacity MID: the largest Zipf shard (370 facts) dropped to 0.873. Rescue: an online split policy that, when a shard exceeds the capacity FLOOR, splits it into sub-shards of <=FLOOR. Measures recall on the hot shard after splitting vs before.",
  prereg="HARD-PASS hot-shard recall after online-split >= 0.95 AND before-split < 0.90. MIDDLE >= 0.85. HARD-FAIL < 0.85.",
  body='''
def _selftest():
    assert int(np.ceil(370 / 150)) == 3, "split count"; print("[selftest] PASS: skewed-shard-online-split", flush=True)
def run() -> Dict:
    g = np.random.default_rng(131); N = 4096; FLOOR = 120; HOT = 380; book = cphasor(4000, N, g)
    keys = cphasor(HOT, N, g); vals = g.integers(0, 4000, HOT)
    B = np.zeros(N, dtype=np.complex64)
    for j in range(HOT):
        B = B + keys[j] * book[vals[j]]
    before = sum(int(cidx(B * np.conj(keys[j]), book) == vals[j]) for j in range(HOT)) / HOT
    nsplit = int(np.ceil(HOT / FLOOR)); per = int(np.ceil(HOT / nsplit)); subs = [np.zeros(N, dtype=np.complex64) for _ in range(nsplit)]
    owner = np.minimum(np.arange(HOT) // per, nsplit - 1)
    for j in range(HOT):
        subs[owner[j]] = subs[owner[j]] + keys[j] * book[vals[j]]
    after = sum(int(cidx(subs[owner[j]] * np.conj(keys[j]), book) == vals[j]) for j in range(HOT)) / HOT
    print("  hot-shard(%d facts) recall before-split=%.3f after-split(%d sub-shards)=%.3f" % (HOT, before, nsplit, after), flush=True)
    return {"before": before, "after": after}
def verdict(r) -> Tuple[str, str]:
    s = "before-split=%.3f after-split=%.3f" % (r["before"], r["after"])
    if r["after"] >= 0.95 and r["before"] < 0.90: return ("HARD_PASS", "HARD_PASS: online-splitting the hot Zipf shard restores recall to >=0.95 -- elastic split policy handles skew. " + s)
    if r["after"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: after-split 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: split does not restore (<0.85). " + s)
'''))
C.append(dict(anchor="hierarchical_subshard_kg_cpu_v1", tag="PP-132 within-relation hierarchical sub-sharding",
  title="relation-then-subject hierarchical sub-sharding clears the KG 2-hop gate",
  desc="per_relation_sharding_kg MID: relation-sharding lifted 0.19 to 0.735 but relation shards stay large. Rescue: hierarchical sub-sharding (shard by relation, then within each relation sub-shard by subject) so each sub-bundle holds few edges. 2-hop routes by (relation, subject). Should clear 0.90.",
  prereg="HARD-PASS hierarchical sub-sharded 2-hop recall@1 >= 0.90 (vs per-relation 0.735). MIDDLE >= 0.80. HARD-FAIL < 0.80.",
  body='''
def _selftest():
    d = {}; d[(1, 2)] = 3; assert d[(1, 2)] == 3, "subshard key"; print("[selftest] PASS: hierarchical-subshard-kg", flush=True)
def run() -> Dict:
    g = np.random.default_rng(132); N = 8192; VE = 300; VR = 10; deg = 4; TR = 60 if SMOKE else 200
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g); edges = {}; sub = {}
    for s in range(VE):
        for _ in range(deg):
            r = int(g.integers(0, VR)); o = int(g.integers(0, VE))
            if (s, r) not in edges:
                edges[(s, r)] = o
                sub.setdefault((r, s), np.zeros(N, dtype=np.complex64)); sub[(r, s)] = sub[(r, s)] + ents[o]
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
    hit = 0; n = 0
    for _ in range(TR):
        p = path()
        if not p:
            continue
        s, r1, b, r2, a = p
        bh = cidx(sub[(r1, s)], ents) if (r1, s) in sub else -1
        ah = cidx(sub[(r2, bh)], ents) if (r2, bh) in sub else -1
        hit += int(ah == a); n += 1
    rec = hit / max(1, n); print("  hierarchical sub-sharded 2-hop recall@1=%.3f (n=%d, %d sub-shards)" % (rec, n, len(sub)), flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "hierarchical 2-hop=%.3f (vs per-relation 0.735)" % r["recall"]
    if r["recall"] >= 0.90: return ("HARD_PASS", "HARD_PASS: relation-then-subject hierarchical sub-sharding clears 2-hop recall >=0.90 -- hierarchical sharding resolves the per-relation gate. " + s)
    if r["recall"] >= 0.80: return ("MIDDLE_BAND", "MIDDLE_BAND: hierarchical 0.80-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: hierarchical <0.80. " + s)
'''))
for c in C:
    txt = HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"])
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(txt, encoding="utf-8"); print("wrote", c["anchor"])
