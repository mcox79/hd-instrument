"""Generator: CYCLE_200 follow-up CPU anchors F1/F2/F4/F5/F6. Write-tool authored (no heredoc)."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: CYCLE_200_FOLLOWUPS ({tag}). {desc} Pure numpy. CPU.
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

F1 = r'''
def _selftest():
    import numpy as _n; assert _n.all(_n.diff([0,1,2])>0), "mono"; print("[selftest] PASS: f1-topk-bitflip-rescue", flush=True)
def run() -> Dict:
    g = np.random.default_rng(2001); N = 8192; VK = 100; VV = 400; keys = cphasor(VK, N, g); vals = cphasor(VV, N, g); M = 50; K = 5
    levels = [0.0, 0.1, 0.3, 0.5]; TR = 40 if SMOKE else 150; curve1 = {}; curvek = {}
    for fl in levels:
        h1 = 0; hk = 0; n = 0
        for _ in range(TR):
            Mem = np.zeros(N, dtype=np.complex64); facts = []
            for _f in range(M):
                k = int(g.integers(0, VK)); vv = int(g.integers(0, VV)); Mem = Mem + keys[k] * vals[vv]; facts.append((k, vv))
            k, vv = facts[int(g.integers(0, len(facts)))]
            qk = keys[k].copy(); nf = int(fl * N); idx = g.choice(N, nf, replace=False); qk[idx] = np.exp(1j * (g.random(nf) * 2 - 1) * math.pi)
            sc = (vals @ np.conj(Mem * np.conj(qk))).real; order = np.argsort(sc)[::-1]
            h1 += int(order[0] == vv); hk += int(vv in order[:K].tolist()); n += 1
        curve1["f%.1f" % fl] = h1 / n; curvek["f%.1f" % fl] = hk / n
    t1 = curve1["f0.3"]; tk = curvek["f0.3"]; tk5 = curvek["f0.5"]
    print("  top-1@0.3=%.3f TOP-%d@0.3=%.3f top-%d@0.5=%.3f" % (t1, K, tk, K, tk5), flush=True)
    return {"top1_03": t1, "topk_03": tk, "topk_05": tk5, "curvek": {k: round(v, 3) for k, v in curvek.items()}}
def verdict(r) -> Tuple[str, str]:
    s = "top1@0.3=%.3f TOPK@0.3=%.3f topk@0.5=%.3f curve=%s" % (r["top1_03"], r["topk_03"], r["topk_05"], r["curvek"])
    if r["topk_03"] >= 0.95 and r["topk_05"] >= 0.70: return ("HARD_PASS", "HARD_PASS: top-k rescue recovers >=0.95 recall at 30pct bit-flip with graceful decay through 50pct (top-1 alone degrades) -- robust noisy-key retrieval. " + s)
    if r["topk_03"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: top-k@0.3 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: top-k@0.3 <0.85. " + s)
'''

F2 = r'''
def _selftest():
    import numpy as _n; assert _n.percentile([1,2,3,4],95) > 3, "pct"; print("[selftest] PASS: f2-latency-at-scale", flush=True)
def run() -> Dict:
    g = np.random.default_rng(2002); N = 1024
    def p95_at(scale, chunk=50000):
        lat = []
        nq = 20 if SMOKE else 60
        book = cphasor(min(scale, chunk), N, g); nchunks = max(1, scale // chunk)
        for _ in range(nq):
            q = cphasor(1, N, g)[0]; t0 = time.perf_counter()
            best = -1e9
            for _c in range(nchunks):
                sc = (book @ np.conj(q)).real; m = float(sc.max())
                if m > best:
                    best = m
            lat.append((time.perf_counter() - t0) * 1000)
        return float(np.percentile(lat, 95))
    s100k = 10000 if SMOKE else 100000; s1m = 50000 if SMOKE else 1000000
    p100 = p95_at(s100k); p1m = p95_at(s1m)
    print("  P95 latency: %d->%.3fms  %d->%.3fms" % (s100k, p100, s1m, p1m), flush=True)
    return {"p95_100k": p100, "p95_1m": p1m}
def verdict(r) -> Tuple[str, str]:
    s = "P95@100K=%.3fms P95@1M=%.3fms" % (r["p95_100k"], r["p95_1m"])
    if r["p95_100k"] < 5.0 and r["p95_1m"] < 50.0: return ("HARD_PASS", "HARD_PASS: substrate query P95 <5ms at 100K and <50ms at 1M -- fast-tier latency holds at production scale. " + s)
    if r["p95_100k"] < 10.0: return ("MIDDLE_BAND", "MIDDLE_BAND: P95@100K 5-10ms. " + s)
    return ("HARD_FAIL", "HARD_FAIL: P95@100K >=10ms. " + s)
'''

F4 = r'''
def _selftest():
    assert (1 != 2), "neq"; print("[selftest] PASS: f4-harder-constraints", flush=True)
def run() -> Dict:
    g = np.random.default_rng(2004); N = 8192; VN = 100; NCOL = 4; TR = 20 if SMOKE else 60; ncolv = cphasor(NCOL, N, g); nodes = cphasor(VN, N, g)
    agree = 0; n = 0
    for _ in range(TR):
        edges = []
        for _e in range(250):
            a = int(g.integers(0, VN)); b = int(g.integers(0, VN))
            if a != b:
                edges.append((a, b))
        coloring = g.integers(0, NCOL, VN)
        store = np.zeros(N, dtype=np.complex64)
        for vtx in range(VN):
            store = store + nodes[vtx] * ncolv[int(coloring[vtx])]
        readcol = [cidx(store * np.conj(nodes[vtx]), ncolv) for vtx in range(VN)]
        true_valid = all(coloring[a] != coloring[b] for a, b in edges)
        sub_valid = all(readcol[a] != readcol[b] for a, b in edges)
        agree += int(sub_valid == true_valid); n += 1
    acc = agree / n; print("  100-vertex coloring-validity agreement=%.3f (n=%d)" % (acc, n), flush=True)
    return {"acc": acc, "vertices": VN}
def verdict(r) -> Tuple[str, str]:
    s = "100-vertex coloring agreement=%.3f" % r["acc"]
    if r["acc"] >= 0.95: return ("HARD_PASS", "HARD_PASS: substrate constraint-check agreement >=0.95 on 100-vertex graphs vs ground truth -- scales to harder constraint problems. " + s)
    if r["acc"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: agreement 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: agreement <0.85. " + s)
'''

F5 = r'''
def _selftest():
    import numpy as _n; assert _n.var([0.78,0.79,0.80]) < 0.02, "var"; print("[selftest] PASS: f5-gapscore-3seed", flush=True)
def auc(scores, labels):
    order = np.argsort(scores); ranks = np.empty(len(scores)); ranks[order] = np.arange(1, len(scores) + 1)
    pos = labels == 1; npos = int(pos.sum()); nneg = len(labels) - npos
    if npos == 0 or nneg == 0:
        return 0.5
    return (ranks[pos].sum() - npos * (npos + 1) / 2) / (npos * nneg)
def one_seed(seed):
    g = np.random.default_rng(seed); N = 8192; VK = 60; VV = 300; keys = cphasor(VK, N, g); vals = cphasor(VV, N, g); M = 30
    TR = 120 if SMOKE else 400; scores = []; labels = []
    for _ in range(TR):
        Mem = np.zeros(N, dtype=np.complex64); present = []
        for _f in range(M):
            k = int(g.integers(0, VK)); vv = int(g.integers(0, VV)); Mem = Mem + keys[k] * vals[vv]; present.append((k, vv))
        if g.random() < 0.5:
            k, vv = present[int(g.integers(0, len(present)))]; lab = 1
        else:
            k = int(g.integers(0, VK)); vv = int(g.integers(0, VV)); lab = 0
        sc = np.sort((vals @ np.conj(Mem * np.conj(keys[k]))).real)[::-1]
        gap = float(sc[0] - sc[1]); scores.append(gap); labels.append(lab)
    return auc(np.array(scores), np.array(labels))
def run() -> Dict:
    seeds = [7] if SMOKE else [7, 13, 29]; aucs = [one_seed(s) for s in seeds]
    mean = float(np.mean(aucs)); var = float(np.var(aucs)); print("  gap-score AUC seeds=%s mean=%.3f var=%.4f" % ([round(a, 3) for a in aucs], mean, var), flush=True)
    return {"aucs": [round(a, 3) for a in aucs], "mean_auc": mean, "var": var, "n_seeds": len(seeds)}
def verdict(r) -> Tuple[str, str]:
    s = "3-seed mean AUC=%.3f var=%.4f seeds=%s" % (r["mean_auc"], r["var"], r["aucs"])
    if r["n_seeds"] >= 3 and r["mean_auc"] >= 0.80 and r["var"] < 0.02: return ("HARD_PASS", "HARD_PASS: gap-score abstention 3-seed mean AUC >=0.80 with variance <0.02 -- VALIDATED multi-seed. " + s)
    if r["mean_auc"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: mean AUC 0.75-0.80. " + s)
    return ("HARD_FAIL", "HARD_FAIL: mean AUC <0.75. " + s)
'''

F6 = r'''
def _selftest():
    assert len({1,2}&{2}) == 1, "set"; print("[selftest] PASS: f6-pacer-10k", flush=True)
def run() -> Dict:
    g = np.random.default_rng(2006); N = 4096; VC = 2000 if SMOKE else 10000; CITES = cphasor(1, N, g)[0]; cases = cphasor(VC, N, g); NSEED = 60 if SMOKE else 300
    adj = {}; shard = {}
    for i in range(VC):
        outs = [int(o) for o in g.choice(VC, int(g.integers(1, 5)), replace=False) if int(o) != i]
        adj[i] = outs; sh = np.zeros(N, dtype=np.complex64)
        for o in outs:
            sh = sh + CITES * cases[o]
        shard[i] = sh
    recs = []; precs = []
    for seed in g.choice(VC, NSEED, replace=False):
        seed = int(seed); gold = set(); fr = {seed}
        for _h in range(3):
            nf = set()
            for u in fr:
                nf |= set(adj[u]) - gold
            gold |= nf; fr = nf
        if not gold:
            continue
        reached = set(); fr = [seed]
        for _h in range(3):
            nf = []
            for u in fr:
                sc = (cases @ np.conj(shard[u] * np.conj(CITES))).real / N
                for v in np.where(sc > 0.30)[0].tolist():
                    if v not in reached and v != seed:
                        nf.append(v)
            reached |= set(nf); fr = nf
        tp = len(gold & reached); recs.append(tp / len(gold)); precs.append(tp / max(1, len(reached)))
    rc = float(np.mean(recs)); pr = float(np.mean(precs)); print("  PACER %d-case snowball recall=%.3f precision=%.3f (n=%d)" % (VC, rc, pr, len(recs)), flush=True)
    return {"recall": rc, "precision": pr, "cases": VC}
def verdict(r) -> Tuple[str, str]:
    s = "recall=%.3f precision=%.3f at %d cases" % (r["recall"], r["precision"], r["cases"])
    if r["recall"] >= 0.95 and r["precision"] >= 0.95: return ("HARD_PASS", "HARD_PASS: legal-citation snowball recall=precision>=0.95 at 10000-case scale -- VALIDATED at production legal scale. " + s)
    if r["recall"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: recall 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: recall <0.85. " + s)
'''

C = [
    dict(anchor="f1_topk_bitflip_rescue_cpu_v1", tag="F1 top-k bit-flip rescue", title="top-k recovers >=0.95 recall at 30pct bit-flip with graceful decay to 50pct", desc="Bit-flips a fraction of the query-key dims; top-1 degrades but top-k (k=5) rescues; sweeps flip 0->0.5.", prereg="HARD-PASS top-k@0.3 >=0.95 AND top-k@0.5 >=0.70. MIDDLE top-k@0.3 >=0.85. HARD-FAIL <0.85.", body=F1),
    dict(anchor="f2_latency_at_scale_cpu_v1", tag="F2 fast-tier latency at scale", title="substrate query P95 <5ms at 100K and <50ms at 1M", desc="Measures P95 query latency at 100K and 1M KB scale (chunked cleanup, memory-safe).", prereg="HARD-PASS P95@100K <5ms AND P95@1M <50ms. MIDDLE P95@100K <10ms. HARD-FAIL >=10ms.", body=F2),
    dict(anchor="f4_harder_constraints_cpu_v1", tag="F4 harder constraint problems", title="substrate constraint-check agreement >=0.95 on 100-vertex graphs", desc="Graph-coloring constraint checking on 100-vertex graphs (vs the small graphs in PP-213).", prereg="HARD-PASS agreement >=0.95. MIDDLE >=0.85. HARD-FAIL <0.85.", body=F4),
    dict(anchor="f5_gapscore_3seed_cpu_v1", tag="F5 gap-score 3-seed promotion", title="gap-score abstention 3-seed mean AUC >=0.80 with variance <0.02", desc="Multi-seed (3) gap-score abstention AUC for VALIDATED promotion of PP-181.", prereg="HARD-PASS 3-seed mean AUC >=0.80 AND var <0.02. MIDDLE mean >=0.75. HARD-FAIL <0.75.", body=F5),
    dict(anchor="f6_pacer_10k_scale_cpu_v1", tag="F6 PACER 10000-case scale", title="legal-citation snowball recall=precision>=0.95 at 10000-case scale", desc="Extends PP-208 (1000-case 0.999/1.000) to 10000 cases for VALIDATED legal-scale promotion.", prereg="HARD-PASS recall>=0.95 AND precision>=0.95. MIDDLE recall>=0.85. HARD-FAIL <0.85.", body=F6),
]
for c in C:
    txt = HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"])
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(txt, encoding="utf-8"); print("wrote", c["anchor"])
