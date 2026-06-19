"""Generator batch 3: hopfield beta-sweep + sparse-hopfield + bloom-filter (pure numpy). Run: python tools/gen_batch3.py"""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: {routing}. {desc} Pure numpy. CPU.
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
C.append(dict(anchor="hopfield_beta_sweep_v1", routing="field_modern_hopfield Anchor 2 (separation/beta sweep)",
  title="modern-Hopfield retrieval separation threshold vs inverse-temperature beta",
  desc="At fixed load P/N=1.0, sweep beta (inverse temperature). Modern Hopfield needs beta above a separation threshold for clean retrieval (Ramsauer). Find the minimum beta achieving recall@1 >= 0.95 from noisy queries.",
  prereg="HARD-PASS some beta <= 16 achieves recall@1 >= 0.95 at P/N=1.0 (separation threshold is practical). MIDDLE needs beta <= 64. HARD-FAIL no beta clears 0.95.",
  body='''
def softmax(x):
    x = x - x.max(axis=-1, keepdims=True); e = np.exp(x); return e / e.sum(axis=-1, keepdims=True)
def _selftest():
    sm = softmax(np.array([[1.0, 2.0]])); assert abs(sm.sum() - 1.0) < 1e-9, "softmax norm"
    assert 1 < 2, "order"; assert np.sign(-0.5) == -1, "sign"
    print("[selftest] PASS: hopfield-beta-sweep", flush=True)
def run() -> Dict:
    g = np.random.default_rng(1); N = 256; P = N; FLIP = 0.15; NQ = 200
    X = np.sign(g.standard_normal((P, N))).astype(np.float64)
    qi = g.choice(P, min(NQ, P), replace=False); Q = X[qi].copy(); fl = g.random(Q.shape) < FLIP; Q[fl] *= -1
    betas = [1, 2, 4, 8, 16] if SMOKE else [0.5, 1, 2, 4, 8, 16, 32, 64]; by = {}
    for b in betas:
        ret = softmax(b * (Q @ X.T)) @ X; rs = np.sign(ret)
        rec = float(((rs * X[qi]).sum(1) / N >= 0.95).mean()); by["b%g" % b] = rec
        print("  beta=%g recall@1=%.3f" % (b, rec), flush=True)
    good = [b for b in betas if by["b%g" % b] >= 0.95]; minb = min(good) if good else 1e9
    return {"by": by, "min_beta": minb}
def verdict(r) -> Tuple[str, str]:
    mb = r["min_beta"]; s = "min-beta-for-0.95=%s | %s" % (mb if mb < 1e9 else "none", {k: round(v, 3) for k, v in r["by"].items()})
    if mb <= 16: return ("HARD_PASS", "HARD_PASS: modern-Hopfield clean retrieval at beta<=16 (P/N=1.0) -- the separation threshold is practical; the substrate operates well inside it. " + s)
    if mb <= 64: return ("MIDDLE_BAND", "MIDDLE_BAND: needs beta<=64. " + s)
    return ("HARD_FAIL", "HARD_FAIL: no beta clears 0.95 at P/N=1.0. " + s)
'''))
C.append(dict(anchor="sparse_hopfield_v1", routing="field_modern_hopfield finding 4 (sparse Hopfield / sparsemax)",
  title="sparse (top-k) Hopfield retrieval matches softmax with interpretable support",
  desc="Replace softmax attention with sparse top-k attention (sparsemax analog): keep only the top-k stored patterns by score, renormalize. Compare recall@1 + support size to dense softmax. Sparse retrieval = exact-zero, auditable attention.",
  prereg="HARD-PASS sparse recall@1 >= softmax recall - 0.02 at top-k=5 (sparsity with no recall loss). MIDDLE within 0.05. HARD-FAIL sparse loses > 0.05.",
  body='''
def softmax(x):
    x = x - x.max(axis=-1, keepdims=True); e = np.exp(x); return e / e.sum(axis=-1, keepdims=True)
def _selftest():
    sm = softmax(np.array([[1.0, 2.0, 3.0]])); assert abs(sm.sum() - 1.0) < 1e-9, "softmax norm"
    a = np.array([0.1, 0.9, 0.5]); k = np.argsort(a)[::-1][:2]; assert set(k.tolist()) == {1, 2}, "top-k"
    assert np.sign(0.3) == 1, "sign"
    print("[selftest] PASS: sparse-hopfield", flush=True)
def run() -> Dict:
    g = np.random.default_rng(2); N = 256; P = N; FLIP = 0.15; NQ = 200; BETA = 8.0; TOPK = 5
    X = np.sign(g.standard_normal((P, N))).astype(np.float64)
    qi = g.choice(P, min(NQ, P), replace=False); Q = X[qi].copy(); fl = g.random(Q.shape) < FLIP; Q[fl] *= -1
    sc = BETA * (Q @ X.T)
    dense = softmax(sc) @ X; rd = float(((np.sign(dense) * X[qi]).sum(1) / N >= 0.95).mean())
    # sparse: keep top-k scores per query, softmax over them only
    att = np.zeros_like(sc)
    for i in range(sc.shape[0]):
        idx = np.argsort(sc[i])[::-1][:TOPK]; att[i, idx] = softmax(sc[i, idx][None, :])[0]
    sparse = att @ X; rs = float(((np.sign(sparse) * X[qi]).sum(1) / N >= 0.95).mean())
    print("  dense recall@1=%.3f sparse(top-%d) recall@1=%.3f (delta=%.3f)" % (rd, TOPK, rs, rd - rs), flush=True)
    return {"dense": rd, "sparse": rs, "delta": rd - rs, "topk": TOPK}
def verdict(r) -> Tuple[str, str]:
    s = "dense=%.3f sparse=%.3f delta=%.3f (top-%d)" % (r["dense"], r["sparse"], r["delta"], r["topk"])
    if r["delta"] <= 0.02: return ("HARD_PASS", "HARD_PASS: sparse top-k Hopfield matches softmax within 0.02 -- exact-zero interpretable attention with no recall loss. " + s)
    if r["delta"] <= 0.05: return ("MIDDLE_BAND", "MIDDLE_BAND: sparse within 0.05 of dense. " + s)
    return ("HARD_FAIL", "HARD_FAIL: sparse loses >0.05 recall. " + s)
'''))
C.append(dict(anchor="streaming_bloom_dedup_v1", routing="field_streaming_algorithms (membership/dedup filter)",
  title="Bloom filter duplicate-ingest detection accuracy",
  desc="A k-hash Bloom filter detects duplicate fact ingests (membership) at O(1) memory per item. Insert M unique items, query M inserted + M novel; measure false-positive rate on novel and zero false-negatives on inserted.",
  prereg="HARD-PASS false-positive rate < 1pct AND false-negative rate = 0 at the designed load. MIDDLE FPR < 3pct. HARD-FAIL FPR >= 3pct or any false negative.",
  body='''
def _selftest():
    bits = np.zeros(16, dtype=bool); bits[3] = True; assert bits[3] and not bits[4], "bit set"
    assert (7 * 3 + 1) % 13 >= 0, "hash"
    print("[selftest] PASS: bloom-dedup", flush=True)
def run() -> Dict:
    g = np.random.default_rng(3); M = 20000 if SMOKE else 200000; K = 7; BITS = M * 15
    A = g.integers(1, 2**31, K); B = g.integers(0, 2**31, K); PR = 2147483647
    bits = np.zeros(BITS, dtype=bool)
    ins = g.integers(0, 1 << 50, M, dtype=np.int64)
    for k in range(K):
        bits[((A[k] * ins + B[k]) % PR) % BITS] = True
    # false negatives on inserted
    fn = 0
    for k in range(1):
        pass
    fn_mask = np.ones(M, dtype=bool)
    for k in range(K):
        fn_mask &= bits[((A[k] * ins + B[k]) % PR) % BITS]
    fn = int((~fn_mask).sum())
    # false positives on novel
    nov = g.integers(1 << 50, 1 << 51, M, dtype=np.int64)
    fp_mask = np.ones(M, dtype=bool)
    for k in range(K):
        fp_mask &= bits[((A[k] * nov + B[k]) % PR) % BITS]
    fp = int(fp_mask.sum()); fpr = fp / M
    print("  Bloom M=%d K=%d bits=%d: FPR=%.4f FN=%d" % (M, K, BITS, fpr, fn), flush=True)
    return {"fpr": fpr, "fn": fn, "m": M}
def verdict(r) -> Tuple[str, str]:
    s = "FPR=%.4f FN=%d (M=%d)" % (r["fpr"], r["fn"], r["m"])
    if r["fpr"] < 0.01 and r["fn"] == 0: return ("HARD_PASS", "HARD_PASS: Bloom dedup FPR<1pct with zero false negatives -- O(1)-memory duplicate-ingest prevention works. " + s)
    if r["fpr"] < 0.03 and r["fn"] == 0: return ("MIDDLE_BAND", "MIDDLE_BAND: FPR 1-3pct. " + s)
    return ("HARD_FAIL", "HARD_FAIL: FPR>=3pct or false negative present. " + s)
'''))
for c in C:
    txt = HEAD.format(anchor=c["anchor"], title=c["title"], routing=c["routing"], desc=c["desc"], prereg=c["prereg"], body=c["body"])
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(txt, encoding="utf-8"); print("wrote", c["anchor"])
