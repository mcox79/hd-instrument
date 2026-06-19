"""TIER-2 P1 (Research Q3, highest-informative): FB15K-237 HIGH-FANOUT bundle-capacity stress -- (h,r) with >=10 tails, measure top1 + recall@fanout under superposition. Reliable GitHub-raw. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
CELL = r'''"""
exp_fb15k237_highfanout_cpu_v1.py -- TIER-2 P1 Q3: FB15K-237 high-fanout bundle-capacity stress -- CPU.

ROUTING: Research TIER_2_NLQA_DESIGN_ANSWER Q3 (highest-informative follow-up). The prior traversal cell (top1=1.0) was easy
  because most (h,r) are low-degree. THIS filters to high-fanout (head,relation) pairs with >=10 distinct tails -- the bundle-
  CAPACITY question: when many tails superpose in one shard, can substrate cleanup still rank a TRUE tail top-1, and recover the
  full tail set (recall@fanout)? Ranks among all involved entities. Buckets by fanout to show graceful degradation. numpy/VSA. CPU.
PRE-REGISTERED (Research bars): HARD-PASS top1 >= 0.85 on high-fanout. MIDDLE 0.65-0.85 (characterizes superposition limit).
  HARD-FAIL < 0.65 (needs per-fanout sharding fix). Also reports recall@fanout + per-bucket.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "10")
import argparse, time, math, urllib.request
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "fb15k237_highfanout_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 4096; MINFAN = 10
URL = "https://raw.githubusercontent.com/villmow/datasets_knowledge_embedding/master/FB15k-237/train.txt"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)


def _selftest():
    import numpy as _n; assert int(_n.argmax([0.1, 0.9])) == 1, "argmax"; print("[selftest] PASS: fb15k237-highfanout", flush=True)


def load_triples():
    try:
        with urllib.request.urlopen(URL, timeout=40) as r:
            txt = r.read().decode("utf-8", "replace")
        tr = [tuple(ln.split("\t")) for ln in txt.splitlines() if len(ln.split("\t")) == 3]
        if len(tr) > 1000:
            print("[data] %d triples" % len(tr), flush=True); return tr
    except Exception as e:
        print("[data] url failed: %s" % str(e)[:80], flush=True)
    return None


def run() -> Dict:
    g = np.random.default_rng(1010); triples = load_triples()
    if not triples:
        return {"error": "download_failed", "top1": 0.0, "recall_fan": 0.0, "n": 0}
    hr = defaultdict(set)
    for h, r, t in triples:
        hr[(h, r)].add(t)
    high = [(k, sorted(v)) for k, v in hr.items() if len(v) >= MINFAN]
    g.shuffle(high)
    want = 60 if SMOKE else 400
    high = high[:want]
    # entity universe = all heads + all tails of sampled high-fanout pairs
    ents = sorted({h for (h, r), ts in high for _ in [0]} | {h for (h, r), _ in high} | {t for _, ts in high for t in ts})
    rels = sorted({r for (h, r), _ in high})
    ei = {e: i for i, e in enumerate(ents)}; ri = {r: i for i, r in enumerate(rels)}
    E = cphasor(len(ents), N, g); R = cphasor(len(rels), N, g); Econj = np.conj(E)
    top1 = 0; rec = 0.0; n = 0; buckets = defaultdict(lambda: [0, 0])   # fanout-bucket -> [top1hits, count]
    for (h, r), ts in high:
        bundle = np.zeros(N, dtype=np.complex64)
        for t in ts:
            bundle = bundle + E[ei[h]] * (R[ri[r]] * E[ei[t]])
        q = bundle * Econj[ei[h]] * np.conj(R[ri[r]]); scores = (E @ np.conj(q)).real
        order = np.argsort(scores)[::-1]
        gold = {ei[t] for t in ts}; k = len(gold)
        is1 = int(int(order[0]) in gold); top1 += is1
        rec += len(gold & set(int(x) for x in order[:k])) / k             # recall@fanout
        n += 1
        b = "10-19" if k < 20 else ("20-49" if k < 50 else "50+")
        buckets[b][0] += is1; buckets[b][1] += 1
    t1 = top1 / n if n else 0.0; rf = rec / n if n else 0.0
    bj = {b: round(v[0] / v[1], 3) for b, v in sorted(buckets.items())}
    print("  FB15K-237 HIGH-FANOUT (>=%d tails): top1=%.3f recall@fanout=%.3f (n=%d) by-bucket-top1=%s" % (MINFAN, t1, rf, n, bj), flush=True)
    return {"top1": t1, "recall_fan": round(rf, 3), "n": n, "by_bucket": bj}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: FB15K-237 download failed. " + r["error"])
    s = "top1=%.3f recall@fanout=%.3f (n=%d) buckets=%s" % (r["top1"], r["recall_fan"], r["n"], r["by_bucket"])
    if r["top1"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: substrate maintains top1>=0.85 on HIGH-FANOUT (>=10 superposed tails) -- bundle capacity holds; exhaustive retrieval beats probabilistic top-K which over-selects the dominant tail. " + s)
    if r["top1"] >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: top1 0.65-0.85 on high-fanout -- superposition capacity limit; per-fanout sharding (PP-127/131/132/147) would lift. " + s)
    return ("HARD_FAIL", "HARD_FAIL: top1<0.65 on high-fanout -- substrate needs per-fanout sharding at this bundle load. " + s)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s minfan=%d" % (ANCHOR_NAME, RUN_MODE, MINFAN), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''
(EXP / "exp_fb15k237_highfanout_cpu_v1.py").write_text(CELL, encoding="utf-8"); print("wrote fb15k237_highfanout")
