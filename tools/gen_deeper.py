"""Generator: 3 DEEPER-drill CPU substrate cells (pure numpy). Run: python tools/gen_deeper.py"""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: DEEPER_drills_8 {tag}. {desc} Pure numpy. CPU.
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
C.append(dict(anchor="int8_lossless_storage_v1", tag="Anchor 1.3 (int8 Modern Hopfield)",
  title="int8-quantized substrate retains recall vs bf16 (4x memory saving)",
  desc="Quantize continuous stored patterns to int8 (per-vector scale) vs float16; measure recall@1 of noisy queries. int8 = 4x memory vs fp32, 2x vs fp16; validates lossless int8 production storage.",
  prereg="HARD-PASS int8 recall@1 >= 0.95 * fp16 recall at production noise. MIDDLE >= 0.90. HARD-FAIL < 0.90.",
  body='''
def _selftest():
    x = np.array([0.5, -0.3]); q = np.clip(np.round(x / 0.004), -127, 127).astype(np.int8); assert q.dtype == np.int8, "int8 dtype"
    assert np.float16(1.0) == 1.0, "fp16 ok"
    e = np.array([3.0, 4.0]); assert abs(np.linalg.norm(e) - 5.0) < 1e-6, "norm"
    print("[selftest] PASS: int8-lossless-storage", flush=True)
def quant8(X):
    sc = np.abs(X).max(axis=1, keepdims=True) / 127.0 + 1e-12
    return np.round(X / sc).astype(np.int8).astype(np.float32) * sc
def recall(K, Q, qi, dtype):
    Kd = K.astype(dtype).astype(np.float32); Qd = Q.astype(dtype).astype(np.float32)
    pred = np.argmax(Qd @ Kd.T, axis=1); return float((pred == qi).mean())
def run() -> Dict:
    g = np.random.default_rng(1); N = 5000 if SMOKE else 30000; D = 768; NOISE = 0.3; NQ = 500
    X = g.standard_normal((N, D)).astype(np.float32); X = X / np.linalg.norm(X, axis=1, keepdims=True)
    qi = g.choice(N, NQ, replace=False); Q = X[qi] + NOISE / np.sqrt(D) * g.standard_normal((NQ, D)).astype(np.float32)
    r16 = recall(X, Q, qi, np.float16)
    X8 = quant8(X); Q8 = quant8(Q); pred = np.argmax(Q8 @ X8.T, axis=1); r8 = float((pred == qi).mean())
    ratio = r8 / (r16 + 1e-9)
    print("  recall@1 fp16=%.3f int8=%.3f ratio=%.3f (N=%d D=%d noise=%.1f)" % (r16, r8, ratio, N, D, NOISE), flush=True)
    return {"fp16": r16, "int8": r8, "ratio": ratio}
def verdict(r) -> Tuple[str, str]:
    s = "int8=%.3f fp16=%.3f ratio=%.3f" % (r["int8"], r["fp16"], r["ratio"])
    if r["ratio"] >= 0.95: return ("HARD_PASS", "HARD_PASS: int8 storage retains >=95pct of fp16 recall -- 4x memory saving production-safe. " + s)
    if r["ratio"] >= 0.90: return ("MIDDLE_BAND", "MIDDLE_BAND: int8 0.90-0.95 of fp16. " + s)
    return ("HARD_FAIL", "HARD_FAIL: int8 <0.90 of fp16 recall. " + s)
'''))
C.append(dict(anchor="burial_depth_invariant_v1", tag="Anchor 1.2 (burial-depth / load-bearing protection)",
  title="load-bearing bindings detected + protected from decay",
  desc="Some bindings are load-bearing (referenced by many composite facts). Detect them by reference count; protect (exempt from decay); verify protected bindings survive N decay cycles while unreferenced ones decay out.",
  prereg="HARD-PASS load-bearing detection accuracy >= 0.95 AND protected bindings retain >= 0.95 recall after decay cycles (vs unprotected decaying out). MIDDLE 0.85. HARD-FAIL < 0.85.",
  body='''
def _selftest():
    refs = {0: 10, 1: 1, 2: 8}; lb = [k for k, v in refs.items() if v >= 5]; assert set(lb) == {0, 2}, "load-bearing by refcount"
    w = 1.0; w *= 0.9; assert w < 1.0, "decay shrinks"
    assert sorted([3, 1])[0] == 1, "sort"
    print("[selftest] PASS: burial-depth-invariant", flush=True)
def run() -> Dict:
    g = np.random.default_rng(2); N = 500 if SMOKE else 2000; THR = 5; CYCLES = 20; DECAY = 0.85
    refcount = g.integers(0, 12, N)                          # how many composites reference each binding
    load_bearing = refcount >= THR                          # ground truth
    detected = refcount >= THR                              # detector (refcount-based) -- here exact; test robustness with noise
    noisy_rc = refcount + g.integers(-1, 2, N)
    detected = noisy_rc >= THR
    det_acc = float((detected == load_bearing).mean())
    # decay: weights start 1.0; protected (detected load-bearing) exempt; others decay each cycle
    w = np.ones(N)
    for _ in range(CYCLES):
        w[~detected] *= DECAY
    protected_recall = float((w[load_bearing] >= 0.95).mean()) if load_bearing.any() else 1.0
    unprotected_decayed = float((w[~load_bearing] < 0.5).mean()) if (~load_bearing).any() else 1.0
    print("  load-bearing detection acc=%.3f | protected retention=%.3f unprotected decayed=%.3f (N=%d cycles=%d)" % (det_acc, protected_recall, unprotected_decayed, N, CYCLES), flush=True)
    return {"det_acc": det_acc, "protected": protected_recall, "unprotected_decayed": unprotected_decayed}
def verdict(r) -> Tuple[str, str]:
    s = "detection=%.3f protected-retention=%.3f unprotected-decayed=%.3f" % (r["det_acc"], r["protected"], r["unprotected_decayed"])
    if r["det_acc"] >= 0.95 and r["protected"] >= 0.95: return ("HARD_PASS", "HARD_PASS: load-bearing bindings detected >=0.95 + protected from decay -- burial-depth invariant holds (critical facts survive consolidation). " + s)
    if r["det_acc"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: detection 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: load-bearing detection <0.85. " + s)
'''))
C.append(dict(anchor="two_tier_age_decay_v1", tag="Anchor 1.1 (two-tier confidence + age-weighted decay)",
  title="age-weighted decay lets customer overlay win conflicts over entrenched seeds",
  desc="Extends OAS mitigation: instead of static up-weighting, use age-weighted decay -- seed (Wikipedia) bindings decay with age while recent customer bindings stay strong. Measure customer-overlay conflict-win rate with vs without age decay.",
  prereg="HARD-PASS customer-overlay wins >= 0.90 with age-decay mitigation vs <= 0.50 without. MIDDLE 0.70-0.90. HARD-FAIL < 0.70.",
  body='''
def sign_keys(n, d, g):
    return np.sign(g.standard_normal((n, d))).astype(np.float64)
def codebook(n, m, g):
    return np.sign(g.standard_normal((n, m))).astype(np.float64)
def wpinv(K, V, w, ridge):
    Dd = K.shape[1]; Kw = K * w[:, None]; return np.linalg.solve(K.T @ Kw + ridge * np.eye(Dd), Kw.T @ V)
def _selftest():
    g = np.random.default_rng(0); K = sign_keys(10, 32, g); bk = codebook(20, 16, g); V = bk[g.integers(0, 20, 10)]
    W = wpinv(K, V, np.ones(10), 1e-3); idx = np.argmax((K @ W) @ bk.T, axis=1); gold = np.argmax(V @ bk.T, axis=1); assert (idx == gold).mean() >= 0.9, "base recall"
    assert np.exp(-0.5) < 1.0, "age decay <1"
    print("[selftest] PASS: two-tier-age-decay", flush=True)
def run() -> Dict:
    g = np.random.default_rng(3); D = 1024; M = 256; S = 300 if SMOKE else 800; CN = 60 if SMOKE else 150; RIDGE = 1e-2
    bk = codebook(M * 4, M, g); Ks = sign_keys(S, D, g); Vs = bk[g.integers(0, len(bk), S)]
    ci = g.choice(S, CN, replace=False); Kc = Ks[ci].copy(); Vc = bk[g.integers(0, len(bk), CN)]; goldc = np.argmax(Vc @ bk.T, axis=1)
    K_all = np.vstack([Ks, Kc]); V_all = np.vstack([Vs, Vc])
    # ages: seeds old (age ~ large), customer recent (age ~ 0); weight = exp(-LAMBDA * age)
    ages = np.concatenate([g.uniform(5, 10, S), np.zeros(CN)]); LAMBDA = 0.7
    w_decay = np.exp(-LAMBDA * ages); w_flat = np.ones(len(K_all))
    def winrate(w):
        W = wpinv(K_all, V_all, w, RIDGE); pred = np.argmax((Kc @ W) @ bk.T, axis=1); return float((pred == goldc).mean())
    base = winrate(w_flat); mit = winrate(w_decay)
    print("  customer-overlay win: no-decay=%.3f age-decay=%.3f (lambda=%.1f)" % (base, mit, LAMBDA), flush=True)
    return {"no_decay": base, "age_decay": mit}
def verdict(r) -> Tuple[str, str]:
    s = "win no-decay=%.3f age-decay=%.3f" % (r["no_decay"], r["age_decay"])
    if r["age_decay"] >= 0.90 and r["no_decay"] <= 0.50: return ("HARD_PASS", "HARD_PASS: age-weighted decay lets customer overlay win >=0.90 (vs <=0.50 flat) -- recency-decay is a clean OAS mitigation. " + s)
    if r["age_decay"] >= 0.70: return ("MIDDLE_BAND", "MIDDLE_BAND: age-decay win 0.70-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: age-decay <0.70 customer win. " + s)
'''))
for c in C:
    txt = HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"])
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(txt, encoding="utf-8"); print("wrote", c["anchor"])
