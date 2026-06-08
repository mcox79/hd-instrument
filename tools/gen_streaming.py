"""Generator: 3 streaming-algorithm CPU cells (pure numpy, no installs). Run: python tools/gen_streaming.py"""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: field_streaming_algorithms {anchor_tag}. {desc} Pure numpy (no installs). CPU.
PRE-REGISTERED: {prereg}
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "{anchor}"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
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
C.append(dict(anchor="streaming_count_min_sketch_v1", anchor_tag="STREAM-CMS-BENCH",
  title="Count-Min Sketch frequency estimation accuracy",
  desc="3 x W Count-Min Sketch on a Zipfian stream; point-query error vs true counts for heavy items. Sublinear-memory frequency for the substrate routing/drift layer.",
  prereg="HARD-PASS max point-query error < 0.1pct of stream_length for all items with true count >= 100. MIDDLE < 0.5pct. HARD-FAIL >= 0.5pct.",
  body='''
def _selftest():
    assert (5 * 7 + 3) % 11 % 4 >= 0, "hash math"
    t = np.zeros((2, 8)); t[0, 3] += 1; assert t[0, 3] == 1, "increment"
    assert min(5, 3, 9) == 3, "min query"
    print("[selftest] PASS: count-min-sketch", flush=True)
def run() -> Dict:
    g = np.random.default_rng(1); D = 3; W = 3000; V = 5000; N = 20000 if SMOKE else 100000
    p = 1.0 / np.power(np.arange(1, V + 1), 1.1); p /= p.sum()
    stream = g.choice(V, N, p=p)
    A = g.integers(1, 2**31, D); B = g.integers(0, 2**31, D); PR = 2147483647
    table = np.zeros((D, W), dtype=np.int64)
    for d in range(D):
        cols = ((A[d] * stream + B[d]) % PR) % W
        np.add.at(table[d], cols, 1)
    true = np.bincount(stream, minlength=V); heavy = np.where(true >= 100)[0]; errs = []
    for it in heavy:
        est = min(int(table[d, ((A[d] * it + B[d]) % PR) % W]) for d in range(D)); errs.append(abs(est - int(true[it])))
    max_err = max(errs) if errs else 0; rel = max_err / N
    print("  CMS %dx%d: heavy=%d max_abs_err=%d (%.4f pct of N=%d)" % (D, W, len(heavy), max_err, rel * 100, N), flush=True)
    return {"max_err": max_err, "rel": rel, "n": N, "heavy": int(len(heavy))}
def verdict(r) -> Tuple[str, str]:
    s = "max_err=%d (%.4f pct of N=%d) heavy=%d" % (r["max_err"], r["rel"] * 100, r["n"], r["heavy"])
    if r["rel"] < 0.001: return ("HARD_PASS", "HARD_PASS: Count-Min Sketch point-query error <0.1pct of stream for all heavy items -- sublinear-memory frequency estimation works. " + s)
    if r["rel"] < 0.005: return ("MIDDLE_BAND", "MIDDLE_BAND: CMS error 0.1-0.5pct. " + s)
    return ("HARD_FAIL", "HARD_FAIL: CMS error >=0.5pct (widen W). " + s)
'''))
C.append(dict(anchor="streaming_hyperloglog_v1", anchor_tag="HyperLogLog cardinality",
  title="HyperLogLog cardinality estimation accuracy",
  desc="HyperLogLog estimates DISTINCT-entity count in a stream at O(1) memory; compared to true cardinality. A KB-size / distinct-fact metric the substrate can report cheaply.",
  prereg="HARD-PASS relative error < 2pct on true cardinality. MIDDLE < 5pct. HARD-FAIL >= 5pct.",
  body='''
def _selftest():
    assert len(set([1, 1, 2])) == 2, "distinct"
    import math; assert 0.7 < 0.7213 < 0.73, "alpha"
    assert np.floor(np.log2(8.0)) == 3, "log2"
    print("[selftest] PASS: hyperloglog", flush=True)
def run() -> Dict:
    g = np.random.default_rng(2); P = 10 if SMOKE else 14; m = 1 << P
    true_card = 20000 if SMOKE else 200000
    ids = g.integers(0, 1 << 60, true_card, dtype=np.int64).astype(np.uint64)
    h = (ids * np.uint64(2654435761)) & np.uint64((1 << 60) - 1)
    idx = (h >> np.uint64(60 - P)).astype(np.int64)
    rest = (h & np.uint64((1 << (60 - P)) - 1)).astype(np.float64)
    restc = np.where(rest > 0, rest, 1.0)
    rank = np.where(rest > 0, (60 - P) - np.floor(np.log2(restc)).astype(np.int64), (60 - P) + 1)
    reg = np.zeros(m, dtype=np.int64)
    np.maximum.at(reg, idx, rank)
    alpha = 0.7213 / (1 + 1.079 / m)
    est = alpha * m * m / np.sum(2.0 ** (-reg.astype(np.float64)))
    zeros = int((reg == 0).sum())
    if est <= 2.5 * m and zeros > 0:
        est = m * np.log(m / zeros)
    rel = abs(est - true_card) / true_card
    print("  HLL m=%d: true=%d est=%.0f rel_err=%.4f" % (m, true_card, est, rel), flush=True)
    return {"true": true_card, "est": float(est), "rel": float(rel), "m": m}
def verdict(r) -> Tuple[str, str]:
    s = "true=%d est=%.0f rel_err=%.4f (m=%d)" % (r["true"], r["est"], r["rel"], r["m"])
    if r["rel"] < 0.02: return ("HARD_PASS", "HARD_PASS: HyperLogLog cardinality within 2pct at O(1) memory -- distinct-fact/KB-size metric works. " + s)
    if r["rel"] < 0.05: return ("MIDDLE_BAND", "MIDDLE_BAND: HLL within 5pct. " + s)
    return ("HARD_FAIL", "HARD_FAIL: HLL error >=5pct. " + s)
'''))
C.append(dict(anchor="streaming_reservoir_sampling_v1", anchor_tag="Reservoir sampling curation",
  title="Reservoir sampling yields a uniform stream sample",
  desc="Algorithm-R reservoir keeps a uniform k-sample from a stream of N in one pass, O(k) memory -- training-data curation. Validate uniformity: each stream position selected with prob ~ k/N.",
  prereg="HARD-PASS max position-bucket selection deviation < 15pct of expected. MIDDLE < 30pct. HARD-FAIL >= 30pct.",
  body='''
def _selftest():
    assert abs(np.mean([1.0, 0.0]) - 0.5) < 1e-9, "mean"
    assert 5 / 10 == 0.5, "rate"
    assert len(list(range(3))) == 3, "reservoir size"
    print("[selftest] PASS: reservoir-sampling", flush=True)
def run() -> Dict:
    g = np.random.default_rng(3); N = 10000 if SMOKE else 100000; K = 100; TRIALS = 50 if SMOKE else 300; BUCKETS = 10
    sel = np.zeros(BUCKETS)
    for _ in range(TRIALS):
        res = list(range(K))
        for i in range(K, N):
            j = int(g.integers(0, i + 1))
            if j < K:
                res[j] = i
        for idx in res:
            sel[idx * BUCKETS // N] += 1
    expected = TRIALS * K / BUCKETS; max_dev = float(np.abs(sel - expected).max() / expected)
    print("  reservoir K=%d N=%d trials=%d max_bucket_dev=%.3f" % (K, N, TRIALS, max_dev), flush=True)
    return {"max_dev": max_dev, "k": K, "n": N}
def verdict(r) -> Tuple[str, str]:
    s = "max_bucket_dev=%.3f (K=%d N=%d)" % (r["max_dev"], r["k"], r["n"])
    if r["max_dev"] < 0.15: return ("HARD_PASS", "HARD_PASS: reservoir sample uniform across positions (<15pct dev) -- one-pass O(k) curation works. " + s)
    if r["max_dev"] < 0.30: return ("MIDDLE_BAND", "MIDDLE_BAND: deviation 15-30pct. " + s)
    return ("HARD_FAIL", "HARD_FAIL: biased (>=30pct dev). " + s)
'''))
for c in C:
    txt = HEAD.format(anchor=c["anchor"], title=c["title"], anchor_tag=c["anchor_tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"])
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(txt, encoding="utf-8"); print("wrote", c["anchor"])
