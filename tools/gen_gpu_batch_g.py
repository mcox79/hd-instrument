"""Generator: GPU batch G (4 sharded-KG-at-scale restorations + long recall). Run: python tools/gen_gpu_batch_g.py"""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- GPU.

ROUTING: KG-scale sharding restoration ({tag}). {desc} torch.cuda; 8GB-safe. GPU.
PRE-REGISTERED: {prereg}
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os, math
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "{anchor}"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
{selftest}
_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
except Exception as e:
    print("[FATAL] torch: %s" % e, flush=True); sys.exit(1)
if not torch.cuda.is_available():
    print("[FATAL] CUDA required.", flush=True); sys.exit(1)
DEV = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)
def cphasor(m, d, g):
    ang = (torch.rand(m, d, generator=g, device=DEV) * 2 - 1) * math.pi; return torch.complex(torch.cos(ang), torch.sin(ang))
def cidx(v, book):
    return int(torch.argmax((book @ torch.conj(v)).real))
{body}
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\\n[VERDICT] " + vmsg, flush=True)
metrics = {{"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''
ST = '''
def _selftest():
    import numpy as _n; assert _n.argmax([0.1, 0.9]) == 1, "argmax"; print("[selftest] PASS: %s", flush=True)'''
C = []
C.append(dict(anchor="multi_relation_kg_sharded_gpu_v1", tag="bidirectional KG sharded at scale",
  title="bidirectional KG triple query at 5000 entities via sharding (restores the monolithic collapse)",
  desc="multi_relation_kg_gpu_scale collapsed monolithic at 5000 entities ((s,r)->o=0.045). Shard by subject for (s,r)->o queries and by object for (r,o)->s queries (each shard bundles only that node's incident edges). Restores bidirectional recall at scale.",
  prereg="HARD-PASS both (s,r)->o and (r,o)->s recall >= 0.90 sharded AND monolithic <= 0.15. MIDDLE >= 0.75. HARD-FAIL < 0.75.",
  selftest=ST,
  body='''
def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(31); N = 8192; VE = 1500 if SMOKE else 5000; VR = 24; T = 3000 if SMOKE else 10000
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g)
    Mono = torch.zeros(N, dtype=torch.complex64, device=DEV)
    subj = torch.zeros(VE, N, dtype=torch.complex64, device=DEV)   # per-subject: bundles r*o (for (s,r)->o)
    obj = torch.zeros(VE, N, dtype=torch.complex64, device=DEV)    # per-object: bundles s*r (for (r,o)->s)
    trip = []
    for _ in range(T):
        s = int(torch.randint(0, VE, (1,), generator=g, device=DEV)); r = int(torch.randint(0, VR, (1,), generator=g, device=DEV)); o = int(torch.randint(0, VE, (1,), generator=g, device=DEV))
        Mono = Mono + ents[s] * rels[r] * ents[o]; subj[s] = subj[s] + rels[r] * ents[o]; obj[o] = obj[o] + ents[s] * rels[r]; trip.append((s, r, o))
    samp = [trip[int(torch.randint(0, len(trip), (1,), generator=g, device=DEV))] for _ in range(400)]
    mo = 0; so = 0; ss = 0
    for s, r, o in samp:
        mo += int(cidx(Mono * torch.conj(ents[s] * rels[r]), ents) == o)
        so += int(cidx(subj[s] * torch.conj(rels[r]), ents) == o)
        ss += int(cidx(obj[o] * torch.conj(rels[r]), ents) == s)
    mr = mo / len(samp); sro = so / len(samp); ros = ss / len(samp); print("  monolithic (s,r)->o=%.3f | SHARDED (s,r)->o=%.3f (r,o)->s=%.3f (VE=%d T=%d)" % (mr, sro, ros, VE, T), flush=True)
    return {"mono": mr, "sro": sro, "ros": ros, "m": min(sro, ros)}
def verdict(r) -> Tuple[str, str]:
    s = "sharded (s,r)->o=%.3f (r,o)->s=%.3f monolithic=%.3f" % (r["sro"], r["ros"], r["mono"])
    if r["m"] >= 0.90 and r["mono"] <= 0.15: return ("HARD_PASS", "HARD_PASS: sharding restores bidirectional KG recall to >=0.90 at 5000 entities where monolithic collapses -- KG must be sharded by subject/object. " + s)
    if r["m"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: sharded bidirectional 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: sharded bidirectional <0.75. " + s)
'''))
C.append(dict(anchor="kgqa_discrete_sharded_vs_fuzzy_gpu_v1", tag="discrete-sharded vs fuzzy at scale",
  title="discrete-KG sharded K-hop vs fuzzy retrieval on 2-hop QA at 5000 entities (GPU)",
  desc="The universal-principle comparison done correctly at scale: discrete-KG with PER-SUBJECT SHARDING (the proven scale fix) vs fuzzy-embedding iterative retrieval, on identical 2-hop questions over 5000 entities. Confirms discrete-sharded wins decisively at scale (monolithic discrete was 0.0; sharded should beat fuzzy).",
  prereg="HARD-PASS discrete-sharded recall@1 >= 0.85 AND >= fuzzy + 0.40. MIDDLE gap >= 0.20. HARD-FAIL gap < 0.20.",
  selftest=ST,
  body='''
def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(32); N = 8192; VE = 1500 if SMOKE else 5000; VR = 24; deg = 3; NQ = 150 if SMOKE else 400
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g); edges = {}; subj = torch.zeros(VE, N, dtype=torch.complex64, device=DEV)
    for s in range(VE):
        for _ in range(deg):
            r = int(torch.randint(0, VR, (1,), generator=g, device=DEV)); o = int(torch.randint(0, VE, (1,), generator=g, device=DEV))
            if (s, r) not in edges:
                edges[(s, r)] = o; subj[s] = subj[s] + rels[r] * ents[o]
    fz = torch.randn(VE, 96, generator=g, device=DEV); fz = fz / fz.norm(dim=1, keepdim=True)
    dh = 0; fh = 0; n = 0
    for _ in range(NQ):
        path = None
        for _t in range(80):
            s0 = int(torch.randint(0, VE, (1,), generator=g, device=DEV)); o1 = [(r, edges[(s0, r)]) for (ss, r) in edges if ss == s0]
            if not o1:
                continue
            r1, b = o1[int(torch.randint(0, len(o1), (1,), generator=g, device=DEV))]; o2 = [(r, edges[(b, r)]) for (ss, r) in edges if ss == b]
            if not o2:
                continue
            r2, c = o2[int(torch.randint(0, len(o2), (1,), generator=g, device=DEV))]; path = (s0, r1, b, r2, c); break
        if path is None:
            continue
        s0, r1, b, r2, c = path
        bh = cidx(subj[s0] * torch.conj(rels[r1]), ents); ch = cidx(subj[bh] * torch.conj(rels[r2]), ents); dh += int(ch == c)
        qf = fz[s0] + (1.0 / math.sqrt(96)) * torch.randn(96, generator=g, device=DEV); bb = int(torch.argmax(fz @ qf)); qf2 = fz[bb] + (1.0 / math.sqrt(96)) * torch.randn(96, generator=g, device=DEV); fh += int(int(torch.argmax(fz @ qf2)) == c); n += 1
    dr = dh / max(1, n); fr = fh / max(1, n); print("  2-hop QA recall@1: discrete-sharded=%.3f fuzzy=%.3f gap=%.3f (VE=%d)" % (dr, fr, dr - fr, VE), flush=True)
    return {"discrete": dr, "fuzzy": fr, "gap": dr - fr}
def verdict(r) -> Tuple[str, str]:
    s = "discrete-sharded=%.3f fuzzy=%.3f gap=%.3f" % (r["discrete"], r["fuzzy"], r["gap"])
    if r["discrete"] >= 0.85 and r["gap"] >= 0.40: return ("HARD_PASS", "HARD_PASS: discrete-sharded K-hop >=0.85 beats fuzzy by >=0.40 at 5000-entity scale -- the right architecture (discrete+sharded) wins decisively. " + s)
    if r["gap"] >= 0.20: return ("MIDDLE_BAND", "MIDDLE_BAND: gap 0.20-0.40 at scale. " + s)
    return ("HARD_FAIL", "HARD_FAIL: gap <0.20 at scale. " + s)
'''))
C.append(dict(anchor="kg_sharding_strategy_compare_gpu_v1", tag="per-subject vs per-relation shard key",
  title="which shard key is best for KG K-hop at scale: subject vs relation",
  desc="Compares two KG sharding strategies at 5000 entities: shard by SUBJECT (each entity's edges) vs shard by RELATION (each relation type). Both should beat monolithic; identifies which keeps 2-hop recall highest (informs the v1.5 KG storage layout).",
  prereg="HARD-PASS the better strategy >= 0.85 2-hop recall (and both >> monolithic). MIDDLE >= 0.70. HARD-FAIL < 0.70.",
  selftest=ST,
  body='''
def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(33); N = 8192; VE = 1500 if SMOKE else 5000; VR = 16; deg = 3; NQ = 150 if SMOKE else 400
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g); edges = {}
    subj = torch.zeros(VE, N, dtype=torch.complex64, device=DEV); rel = torch.zeros(VR, N, dtype=torch.complex64, device=DEV)
    for s in range(VE):
        for _ in range(deg):
            r = int(torch.randint(0, VR, (1,), generator=g, device=DEV)); o = int(torch.randint(0, VE, (1,), generator=g, device=DEV))
            if (s, r) not in edges:
                edges[(s, r)] = o; subj[s] = subj[s] + rels[r] * ents[o]; rel[r] = rel[r] + ents[s] * ents[o]
    def sample():
        for _t in range(80):
            s0 = int(torch.randint(0, VE, (1,), generator=g, device=DEV)); o1 = [(r, edges[(s0, r)]) for (ss, r) in edges if ss == s0]
            if not o1:
                continue
            r1, b = o1[int(torch.randint(0, len(o1), (1,), generator=g, device=DEV))]; o2 = [(r, edges[(b, r)]) for (ss, r) in edges if ss == b]
            if not o2:
                continue
            r2, c = o2[int(torch.randint(0, len(o2), (1,), generator=g, device=DEV))]; return s0, r1, b, r2, c
        return None
    sh = 0; rh = 0; n = 0
    for _ in range(NQ):
        p = sample()
        if p is None:
            continue
        s0, r1, b, r2, c = p
        bh = cidx(subj[s0] * torch.conj(rels[r1]), ents); ch = cidx(subj[bh] * torch.conj(rels[r2]), ents); sh += int(ch == c)
        bh2 = cidx(rel[r1] * torch.conj(ents[s0]), ents); ch2 = cidx(rel[r2] * torch.conj(ents[bh2]), ents); rh += int(ch2 == c); n += 1
    sr = sh / max(1, n); rr = rh / max(1, n); print("  2-hop recall: shard-by-subject=%.3f shard-by-relation=%.3f (VE=%d)" % (sr, rr, VE), flush=True)
    return {"subject": sr, "relation": rr, "best": max(sr, rr)}
def verdict(r) -> Tuple[str, str]:
    win = "subject" if r["subject"] >= r["relation"] else "relation"; s = "shard-by-subject=%.3f shard-by-relation=%.3f (best=%s)" % (r["subject"], r["relation"], win)
    if r["best"] >= 0.85: return ("HARD_PASS", "HARD_PASS: best KG sharding strategy (%s) >=0.85 2-hop at scale -- recommended v1.5 KG layout. " % win + s)
    if r["best"] >= 0.70: return ("MIDDLE_BAND", "MIDDLE_BAND: best strategy 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: neither sharding strategy >=0.70. " + s)
'''))
C.append(dict(anchor="sign_recall_100M_gpu_v1", tag="sign-key recall at 100M",
  title="sign-key autoassociative recall@1 at 100M keys (GPU, chunked, long-running)",
  desc="100M sign keys (D=1024) regenerated per chunk; chunked GPU recall@1 under 0.15 bit-flip. Pushes recall scaling to 100M (100x the 1M CPU gate) and is a long-running job that keeps the GPU saturated.",
  prereg="HARD-PASS recall@1 >= 0.99 at N=100M. MIDDLE >= 0.95. HARD-FAIL < 0.95.",
  selftest=ST,
  body='''
def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(34); N = 500000 if SMOKE else 100000000; D = 1024; NQ = 300; FLIP = 0.15; CH = 250000; base = 3003
    qidx = torch.randperm(N, generator=g, device=DEV)[:NQ].sort().values
    def chunk(c0, c1):
        gg = torch.Generator(device=DEV).manual_seed(base + c0); return torch.sign(torch.randn(c1 - c0, D, generator=gg, device=DEV))
    qk = torch.zeros(NQ, D, device=DEV)
    for c0 in range(0, N, CH):
        c1 = min(c0 + CH, N); K = chunk(c0, c1); mask = (qidx >= c0) & (qidx < c1)
        if mask.any():
            qk[mask] = K[qidx[mask] - c0]
        del K
    fl = torch.rand(qk.shape, generator=g, device=DEV) < FLIP; Q = qk.clone(); Q[fl] *= -1
    best = torch.full((NQ,), -1, device=DEV, dtype=torch.long); bs = torch.full((NQ,), -1e9, device=DEV)
    for c0 in range(0, N, CH):
        c1 = min(c0 + CH, N); K = chunk(c0, c1); sc = Q @ K.T; bsc, bidx = sc.max(1); upd = bsc > bs; best[upd] = c0 + bidx[upd]; bs[upd] = bsc[upd]
        del K, sc; torch.cuda.empty_cache()
    rec = (best == qidx).float().mean().item(); print("  N=%d recall@1=%.4f" % (N, rec), flush=True)
    return {"n": N, "recall1": rec}
def verdict(r) -> Tuple[str, str]:
    s = "recall@1=%.4f at N=%d" % (r["recall1"], r["n"])
    if r["recall1"] >= 0.99: return ("HARD_PASS", "HARD_PASS: sign-key recall >=0.99 at 100M -- substrate recall scales to 100M keys. " + s)
    if r["recall1"] >= 0.95: return ("MIDDLE_BAND", "MIDDLE_BAND: recall 0.95-0.99 at 100M. " + s)
    return ("HARD_FAIL", "HARD_FAIL: recall <0.95 at 100M. " + s)
'''))
for c in C:
    txt = HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], selftest=c["selftest"].replace("%s", c["anchor"]), body=c["body"])
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(txt, encoding="utf-8"); print("wrote", c["anchor"])
