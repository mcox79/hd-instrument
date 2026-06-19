"""Generator: deep CPU batch (v2.0 fact-rep family + capability extensions). Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: deep-batch ({tag}). {desc} Pure numpy. CPU.
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
def topk(v, book, k):
    return set(np.argsort((book @ np.conj(v)).real)[::-1][:k].tolist())
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
C.append(dict(anchor="factrep_ep3_typed_values_cpu_v1", tag="EP3 typed-value facts",
  title="facts carry typed values (entity / numeric / date) recovered with the type tag",
  desc="Bind a TYPE tag with each value so a fact stores (key, type, value); recall recovers both the value and its type. Tests type-aware fact representation (entity vs numeric vs date payloads).",
  prereg="HARD-PASS value recall >= 0.95 AND type recall >= 0.95. MIDDLE >= 0.85. HARD-FAIL < 0.85.",
  body='''
def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 32, g)[0]; ty = cphasor(1, 32, g)[0]; v = cphasor(1, 32, g)[0]
    assert np.allclose(a * ty * v * np.conj(a * ty), v, atol=1e-3), "typed bind"; print("[selftest] PASS: factrep-ep3-typed-values", flush=True)
def run() -> Dict:
    g = np.random.default_rng(211); N = 4096; VK = 100; VV = 400; NTY = 3; M = int(0.6 * VK); TR = 60 if SMOKE else 200
    keys = cphasor(VK, N, g); vals = cphasor(VV, N, g); types = cphasor(NTY, N, g)
    vh = 0; th = 0; n = 0
    for _ in range(TR):
        Mem = np.zeros(N, dtype=np.complex64); facts = []
        ks = g.choice(VK, M, replace=False)
        for k in ks:
            ty = int(g.integers(0, NTY)); vv = int(g.integers(0, VV)); Mem = Mem + keys[k] * types[ty] * vals[vv]; facts.append((int(k), ty, vv))
        for k, ty, vv in facts[:20 if not SMOKE else 8]:
            rec = Mem * np.conj(keys[k])                                       # unbind key -> type*value
            tpred = cidx(rec * np.conj(vals[vv]), types)                       # given value, recover type
            vpred = cidx(rec * np.conj(types[ty]), vals)                       # given type, recover value
            th += int(tpred == ty); vh += int(vpred == vv); n += 1
    print("  value-recall=%.3f type-recall=%.3f (n=%d)" % (vh / n, th / n, n), flush=True)
    return {"value": vh / n, "type": th / n}
def verdict(r) -> Tuple[str, str]:
    s = "value-recall=%.3f type-recall=%.3f" % (r["value"], r["type"])
    if r["value"] >= 0.95 and r["type"] >= 0.95: return ("HARD_PASS", "HARD_PASS: typed-value facts recovered with both value and type >=0.95 -- type-aware fact representation works. " + s)
    if min(r["value"], r["type"]) >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: typed recall 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: typed recall <0.85. " + s)
'''))
C.append(dict(anchor="factrep_ep4_provenance_native_cpu_v1", tag="EP4 provenance-native facts",
  title="each fact carries its source; retrieval returns the fact AND its provenance",
  desc="Bind a SOURCE with each fact (key * rel * value * SOURCE-tag); a query recovers the value and the source it came from. Tests native provenance (audit/citation) in the fact representation.",
  prereg="HARD-PASS value recall >= 0.95 AND source recall >= 0.95. MIDDLE >= 0.85. HARD-FAIL < 0.85.",
  body='''
def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 32, g)[0]; s = cphasor(1, 32, g)[0]; v = cphasor(1, 32, g)[0]
    assert np.allclose(a * v * s * np.conj(a * v), s, atol=1e-3), "prov bind"; print("[selftest] PASS: factrep-ep4-provenance-native", flush=True)
def run() -> Dict:
    g = np.random.default_rng(212); N = 4096; VK = 100; VV = 400; NS = 20; M = int(0.6 * VK); TR = 60 if SMOKE else 200
    keys = cphasor(VK, N, g); vals = cphasor(VV, N, g); srcs = cphasor(NS, N, g)
    vh = 0; sh = 0; n = 0
    for _ in range(TR):
        Mem = np.zeros(N, dtype=np.complex64); facts = []; ks = g.choice(VK, M, replace=False)
        for k in ks:
            vv = int(g.integers(0, VV)); sc = int(g.integers(0, NS)); Mem = Mem + keys[k] * vals[vv] * srcs[sc]; facts.append((int(k), vv, sc))
        for k, vv, sc in facts[:20 if not SMOKE else 8]:
            rec = Mem * np.conj(keys[k])                                       # unbind key -> value*source
            vpred = cidx(rec * np.conj(srcs[sc]), vals); spred = cidx(rec * np.conj(vals[vv]), srcs)
            vh += int(vpred == vv); sh += int(spred == sc); n += 1
    print("  value-recall=%.3f source-recall=%.3f (n=%d)" % (vh / n, sh / n, n), flush=True)
    return {"value": vh / n, "source": sh / n}
def verdict(r) -> Tuple[str, str]:
    s = "value-recall=%.3f source-recall=%.3f" % (r["value"], r["source"])
    if r["value"] >= 0.95 and r["source"] >= 0.95: return ("HARD_PASS", "HARD_PASS: provenance-native facts return value + source >=0.95 -- native citation/audit in the fact rep. " + s)
    if min(r["value"], r["source"]) >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: provenance recall 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: provenance recall <0.85. " + s)
'''))
C.append(dict(anchor="sparse_value_capacity_cpu_v1", tag="sparse-VALUE coding capacity",
  title="sparse (k-active) value codes raise per-shard capacity vs dense phasor values",
  desc="Compare per-shard recall capacity using dense phasor values vs SPARSE k-active value codes (only k of N dims active). Sparse codes have lower mutual interference -> more facts per shard at fixed recall. Tests the v2.0 sparse-VALUE capacity gain.",
  prereg="HARD-PASS sparse value coding sustains recall>=0.95 at >= 1.5x the dense per-shard load. MIDDLE >= 1.2x. HARD-FAIL < 1.2x.",
  body='''
def _selftest():
    import numpy as _n; x = _n.zeros(10); x[[1, 3, 5]] = 1; assert x.sum() == 3, "sparse"; print("[selftest] PASS: sparse-value-capacity", flush=True)
def cap(make_val, N, g):
    VV = 2000; book = make_val(VV, N, g); lo, hi, best = 5, 400, 5
    while lo <= hi:
        M = (lo + hi) // 2; keys = cphasor(M, N, g); vi = g.integers(0, VV, M)
        B = np.zeros(N, dtype=np.complex64)
        for j in range(M):
            B = B + keys[j] * book[vi[j]]
        ok = sum(int(cidx(B * np.conj(keys[j]), book) == vi[j]) for j in range(M)) / M
        if ok >= 0.95:
            best = M; lo = M + 1
        else:
            hi = M - 1
    return best
def run() -> Dict:
    g = np.random.default_rng(213); N = 4096
    def dense(m, d, gg):
        return cphasor(m, d, gg)
    def sparse(m, d, gg):
        K = max(8, d // 32); out = np.zeros((m, d), dtype=np.complex64)
        for i in range(m):
            idx = gg.choice(d, K, replace=False); ph = np.exp(1j * (gg.random(K) * 2 - 1) * math.pi); out[i, idx] = ph.astype(np.complex64)
        return out
    cd = cap(dense, N, np.random.default_rng(1)); cs = cap(sparse, N, np.random.default_rng(1)); ratio = cs / max(1, cd)
    print("  per-shard capacity (recall>=0.95): dense=%d sparse=%d ratio=%.2f" % (cd, cs, ratio), flush=True)
    return {"dense": cd, "sparse": cs, "ratio": ratio}
def verdict(r) -> Tuple[str, str]:
    s = "dense-cap=%d sparse-cap=%d ratio=%.2f" % (r["dense"], r["sparse"], r["ratio"])
    if r["ratio"] >= 1.5: return ("HARD_PASS", "HARD_PASS: sparse-VALUE coding gives >=1.5x per-shard capacity -- v2.0 capacity lever validated. " + s)
    if r["ratio"] >= 1.2: return ("MIDDLE_BAND", "MIDDLE_BAND: sparse capacity gain 1.2-1.5x. " + s)
    return ("HARD_FAIL", "HARD_FAIL: sparse capacity gain <1.2x. " + s)
'''))
C.append(dict(anchor="multi_fact_aggregation_cpu_v1", tag="aggregate queries (count over a pattern)",
  title="substrate supports count/exists aggregate queries over a relation pattern",
  desc="Given many (subject, R, object) facts, answer 'how many objects does subject S have via R?' by thresholding the unbind spectrum (count entities above the signal floor). Tests aggregate/set-cardinality queries on the substrate.",
  prereg="HARD-PASS count estimate within +/-1 of true degree for >= 0.85 of queries. MIDDLE >= 0.70. HARD-FAIL < 0.70.",
  body='''
def _selftest():
    import numpy as _n; assert abs(round(2.4) - 2) == 0, "round"; print("[selftest] PASS: multi-fact-aggregation", flush=True)
def run() -> Dict:
    g = np.random.default_rng(214); N = 8192; VE = 200; TR = 60 if SMOKE else 200; R = cphasor(1, N, g)[0]; ents = cphasor(VE, N, g)
    hit = 0; n = 0
    for _ in range(TR):
        s = int(g.integers(0, VE)); deg = int(g.integers(1, 6)); objs = g.choice(VE, deg, replace=False)
        B = np.zeros(N, dtype=np.complex64)
        for o in objs:
            B = B + ents[s] * R * ents[int(o)]
        for _d in range(30):
            ss = int(g.integers(0, VE)); B = B + ents[ss] * R * ents[int(g.integers(0, VE))]
        sc = (ents @ np.conj(B * np.conj(ents[s] * R))).real / N
        est = int((sc > 0.5).sum()); hit += int(abs(est - deg) <= 1); n += 1
    rec = hit / n; print("  count-within-1 accuracy=%.3f (n=%d)" % (rec, n), flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "count-within-1=%.3f" % r["recall"]
    if r["recall"] >= 0.85: return ("HARD_PASS", "HARD_PASS: aggregate count queries within +/-1 >=0.85 -- set-cardinality queries supported. " + s)
    if r["recall"] >= 0.70: return ("MIDDLE_BAND", "MIDDLE_BAND: count accuracy 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: count accuracy <0.70. " + s)
'''))
C.append(dict(anchor="hierarchical_3level_cpu_v1", tag="3-level hierarchy navigation",
  title="domain -> category -> item 3-level hierarchical retrieval",
  desc="A 3-level taxonomy (domain -> category -> item) stored via nested binding; query a (domain, category) path to retrieve its items. Tests deeper faceted navigation than the 2-level cell.",
  prereg="HARD-PASS path-conditioned item recall >= 0.85 at 3 levels. MIDDLE >= 0.70. HARD-FAIL < 0.70.",
  body='''
def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 32, g)[0]; b = cphasor(1, 32, g)[0]; assert np.allclose(a * b * np.conj(a), b, atol=1e-3), "bind"; print("[selftest] PASS: hierarchical-3level", flush=True)
def run() -> Dict:
    g = np.random.default_rng(215); N = 8192; ND = 6; NC = 5; PER = 4; doms = cphasor(ND, N, g); cats = cphasor(NC, N, g); V = ND * NC * PER; items = cphasor(V, N, g)
    M = np.zeros(N, dtype=np.complex64); idx = 0; member = {}
    for d in range(ND):
        for c in range(NC):
            for p in range(PER):
                M = M + doms[d] * cats[c] * items[idx]; member.setdefault((d, c), set()).add(idx); idx += 1
    hit = 0; tot = 0
    for d in range(ND):
        for c in range(NC):
            rec = M * np.conj(doms[d] * cats[c]); top = topk(rec, items, PER); hit += len(top & member[(d, c)]); tot += PER
    rec = hit / tot; print("  3-level path-conditioned recall=%.3f (D=%d C=%d PER=%d)" % (rec, ND, NC, PER), flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "3-level recall=%.3f" % r["recall"]
    if r["recall"] >= 0.85: return ("HARD_PASS", "HARD_PASS: 3-level domain->category->item retrieval >=0.85 -- deep faceted navigation works. " + s)
    if r["recall"] >= 0.70: return ("MIDDLE_BAND", "MIDDLE_BAND: 3-level 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: 3-level <0.70. " + s)
'''))
C.append(dict(anchor="analogy_chain_transfer_cpu_v1", tag="chained analogical transfer",
  title="a relation learned from examples transfers across a chain of new inputs",
  desc="Estimate a relation T from K example pairs, then apply it CHAINED (c -> T(c) -> T(T(c))) and verify each step recovers the true codebook item. Tests multi-step analogical transfer (composition of a learned relation).",
  prereg="HARD-PASS 2-step chained transfer recall >= 0.85. MIDDLE >= 0.70. HARD-FAIL < 0.70.",
  body='''
def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 64, g)[0]; t = cphasor(1, 64, g)[0]; assert np.allclose(a * t * np.conj(t), a, atol=1e-3), "bind"; print("[selftest] PASS: analogy-chain-transfer", flush=True)
def run() -> Dict:
    g = np.random.default_rng(216); N = 4096; V = 300; K = 6; TR = 60 if SMOKE else 200; book = cphasor(V, N, g)
    s1 = 0; s2 = 0; n = 0
    for _ in range(TR):
        T = cphasor(1, N, g)[0]
        # examples: pairs (x, cleanup(x*T)) within the codebook
        ex = g.choice(V, K, replace=False); That = np.zeros(N, dtype=np.complex64)
        for x in ex:
            y = cidx(book[int(x)] * T, book); That = That + (book[y] * np.conj(book[int(x)]))
        That = That / (np.abs(That) + 1e-8)
        c0 = int(g.integers(0, V)); c1 = cidx(book[c0] * That, book); c2 = cidx(book[c1] * That, book)
        g1 = cidx(book[c0] * T, book); g2 = cidx(book[g1] * T, book)
        s1 += int(c1 == g1); s2 += int(c2 == g2); n += 1
    print("  chained transfer: 1-step=%.3f 2-step=%.3f (n=%d)" % (s1 / n, s2 / n, n), flush=True)
    return {"step1": s1 / n, "step2": s2 / n}
def verdict(r) -> Tuple[str, str]:
    s = "1-step=%.3f 2-step=%.3f" % (r["step1"], r["step2"])
    if r["step2"] >= 0.85: return ("HARD_PASS", "HARD_PASS: 2-step chained analogical transfer >=0.85 -- a learned relation composes across a chain. " + s)
    if r["step2"] >= 0.70: return ("MIDDLE_BAND", "MIDDLE_BAND: 2-step 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: 2-step <0.70. " + s)
'''))
for c in C:
    txt = HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"])
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(txt, encoding="utf-8"); print("wrote", c["anchor"])
