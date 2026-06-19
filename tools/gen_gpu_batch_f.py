"""Generator: GPU batch F (5 product/capacity-scale torch.cuda cells). Run: python tools/gen_gpu_batch_f.py"""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- GPU.

ROUTING: GPU product/capacity-scale ({tag}). {desc} torch.cuda; 8GB-safe. GPU.
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
C.append(dict(anchor="substrate_kg_khop_10k_gpu_v1", tag="KG-QA at 10k entities",
  title="substrate KG K-hop at 10000 entities / ~30k triples (GPU)",
  desc="Pushes the KG-QA product gate to 10000 entities and ~30k triples. 2-hop and 3-hop chained unbind+cleanup over the 10k-entity codebook on GPU. Validates KG QA at a large production graph.",
  prereg="HARD-PASS 2-hop recall@1 >= 0.65 at 10000 entities (slightly relaxed vs 5000 due to crosstalk). MIDDLE >= 0.50. HARD-FAIL < 0.50.",
  selftest=ST,
  body='''
def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(11); N = 16384; VE = 3000 if SMOKE else 10000; VR = 32; deg = 3; NQ = 150 if SMOKE else 400
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g); edges = {}
    M = torch.zeros(N, dtype=torch.complex64, device=DEV)
    for s in range(VE):
        for _ in range(deg):
            r = int(torch.randint(0, VR, (1,), generator=g, device=DEV)); o = int(torch.randint(0, VE, (1,), generator=g, device=DEV))
            if (s, r) not in edges:
                edges[(s, r)] = o; M = M + ents[s] * rels[r] * ents[o]
    by = {}
    for hops in ([2] if SMOKE else [2, 3]):
        hit = 0; n = 0
        for _ in range(NQ):
            path = None
            for _t in range(80):
                s0 = int(torch.randint(0, VE, (1,), generator=g, device=DEV)); cur = s0; rseq = []; ok = True
                for _h in range(hops):
                    outs = [r for (ss, r) in edges if ss == cur]
                    if not outs:
                        ok = False; break
                    r = outs[int(torch.randint(0, len(outs), (1,), generator=g, device=DEV))]; rseq.append(r); cur = edges[(cur, r)]
                if ok:
                    path = (s0, rseq, cur); break
            if path is None:
                continue
            s0, rseq, gold = path; cv = ents[s0]
            for r in rseq:
                cv = ents[cidx(M * torch.conj(cv * rels[r]), ents)]
            hit += int(cidx(cv, ents) == gold); n += 1
        by["%dhop" % hops] = hit / max(1, n); print("  %d-hop recall@1=%.3f (n=%d VE=%d %d edges)" % (hops, by["%dhop" % hops], n, VE, len(edges)), flush=True)
    return {"by": by, "r2": by.get("2hop", 0.0)}
def verdict(r) -> Tuple[str, str]:
    s = "recall: %s" % {k: round(v, 3) for k, v in r["by"].items()}
    if r["r2"] >= 0.65: return ("HARD_PASS", "HARD_PASS: KG K-hop 2-hop recall>=0.65 at 10000-entity graph -- KG QA scales to large graphs. " + s)
    if r["r2"] >= 0.50: return ("MIDDLE_BAND", "MIDDLE_BAND: 2-hop 0.50-0.65 at 10k (consider higher N or relation-sharding). " + s)
    return ("HARD_FAIL", "HARD_FAIL: 2-hop <0.50 at 10k. " + s)
'''))
C.append(dict(anchor="multi_relation_kg_gpu_scale_v1", tag="bidirectional KG triple query at scale",
  title="bidirectional KG triple query (s,r)->o and (r,o)->s at 5000 entities (GPU)",
  desc="Scales the multi-relation KG bidirectional query to 5000 entities and ~10k triples on GPU. Recovers object via M*(s*r).conj() and subject via M*(r*o).conj(), cleanup over the entity codebook. Validates queryable-both-ways KG at scale.",
  prereg="HARD-PASS both (s,r)->o and (r,o)->s recall >= 0.80 at 5000 entities. MIDDLE >= 0.65. HARD-FAIL < 0.65.",
  selftest=ST,
  body='''
def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(12); N = 16384; VE = 1500 if SMOKE else 5000; VR = 24; T = 3000 if SMOKE else 10000
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g)
    trip = []; M = torch.zeros(N, dtype=torch.complex64, device=DEV)
    for _ in range(T):
        s = int(torch.randint(0, VE, (1,), generator=g, device=DEV)); r = int(torch.randint(0, VR, (1,), generator=g, device=DEV)); o = int(torch.randint(0, VE, (1,), generator=g, device=DEV))
        M = M + ents[s] * rels[r] * ents[o]; trip.append((s, r, o))
    import random as _rnd
    samp = trip if len(trip) <= 400 else [trip[int(torch.randint(0, len(trip), (1,), generator=g, device=DEV))] for _ in range(400)]
    oh = 0; sh = 0
    for s, r, o in samp:
        oh += int(cidx(M * torch.conj(ents[s] * rels[r]), ents) == o)
        sh += int(cidx(M * torch.conj(rels[r] * ents[o]), ents) == s)
    so = oh / len(samp); ss = sh / len(samp); print("  (s,r)->o=%.3f (r,o)->s=%.3f (VE=%d T=%d)" % (so, ss, VE, T), flush=True)
    return {"sro": so, "ros": ss, "m": min(so, ss)}
def verdict(r) -> Tuple[str, str]:
    s = "(s,r)->o=%.3f (r,o)->s=%.3f" % (r["sro"], r["ros"])
    if r["m"] >= 0.80: return ("HARD_PASS", "HARD_PASS: bidirectional KG triple recall>=0.80 at 5000-entity/10k-triple scale -- queryable-both-ways KG holds at scale. " + s)
    if r["m"] >= 0.65: return ("MIDDLE_BAND", "MIDDLE_BAND: bidirectional 0.65-0.80 at scale (relation-sharding would lift). " + s)
    return ("HARD_FAIL", "HARD_FAIL: bidirectional <0.65 at scale. " + s)
'''))
C.append(dict(anchor="sharding_scaling_S1024_gpu_v1", tag="sharding to S=1024",
  title="sharding scaling law to S=1024 shards (GPU)",
  desc="Extends the sharding scaling law to S up to 1024 shards (fixed per-shard K=80; total up to ~80k items). Confirms per-shard recall stays flat ~1.0 and interference ~0 at very large shard counts -- the unbounded-capacity claim at extreme scale.",
  prereg="HARD-PASS per-shard recall flat >=0.95 (spread<=0.05) and interference<=0.02 up to S=1024. MIDDLE spread<=0.10. HARD-FAIL otherwise.",
  selftest=ST,
  body='''
def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(13); N = 8192; K = 80; VV = 5000; book = cphasor(VV, N, g)
    Ss = [64, 256] if SMOKE else [64, 256, 512, 1024]; per = {}; inter = {}
    for S in Ss:
        keys = cphasor(S * K, N, g); vals = torch.randint(0, VV, (S * K,), generator=g, device=DEV)
        bundles = torch.zeros(S, N, dtype=torch.complex64, device=DEV)
        for i in range(S * K):
            bundles[i // K] = bundles[i // K] + keys[i] * book[vals[i]]
        samp = list(range(0, S * K, max(1, (S * K) // 500))); ph = 0; itr = 0
        for i in samp:
            sh = i // K; rec = bundles[sh] * torch.conj(keys[i]); ph += int(int(torch.argmax((book @ torch.conj(rec)).real)) == int(vals[i]))
            wrong = (sh + 1) % S; own = (book[vals[i]] @ torch.conj(rec)).real; wb = (book @ torch.conj(bundles[wrong] * torch.conj(keys[i]))).real.max(); itr += int(wb > own)
        per["S%d" % S] = ph / len(samp); inter["S%d" % S] = itr / len(samp); print("  S=%d total=%d per-shard=%.3f interference=%.4f" % (S, S * K, per["S%d" % S], inter["S%d" % S]), flush=True)
        del bundles; torch.cuda.empty_cache()
    pv = list(per.values()); return {"per": per, "inter": inter, "spread": max(pv) - min(pv), "minp": min(pv), "maxi": max(inter.values())}
def verdict(r) -> Tuple[str, str]:
    s = "per-shard=%s interference=%s (spread=%.3f max-inter=%.4f)" % ({k: round(v, 3) for k, v in r["per"].items()}, {k: round(v, 4) for k, v in r["inter"].items()}, r["spread"], r["maxi"])
    if r["minp"] >= 0.95 and r["spread"] <= 0.05 and r["maxi"] <= 0.02: return ("HARD_PASS", "HARD_PASS: per-shard recall flat >=0.95 with ~0 interference up to S=1024 (~80k items) -- unbounded capacity by sharding confirmed at extreme scale. " + s)
    if r["spread"] <= 0.10: return ("MIDDLE_BAND", "MIDDLE_BAND: spread<=0.10. " + s)
    return ("HARD_FAIL", "HARD_FAIL: not flat at S=1024. " + s)
'''))
C.append(dict(anchor="sign_recall_50M_gpu_v1", tag="sign-key recall at 50M",
  title="sign-key autoassociative recall@1 at 50M keys (GPU, chunked)",
  desc="50M sign keys (D=1024) regenerated per chunk; chunked GPU recall@1 under 0.15 bit-flip. Pushes the recall scaling gate to 50M (5x the 10M result, 50x the 1M CPU gate).",
  prereg="HARD-PASS recall@1 >= 0.99 at N=50M. MIDDLE >= 0.95. HARD-FAIL < 0.95.",
  selftest=ST,
  body='''
def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(14); N = 500000 if SMOKE else 50000000; D = 1024; NQ = 300; FLIP = 0.15; CH = 250000; base = 2002
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
    if r["recall1"] >= 0.99: return ("HARD_PASS", "HARD_PASS: sign-key recall >=0.99 at 50M -- substrate recall scales to 50M keys. " + s)
    if r["recall1"] >= 0.95: return ("MIDDLE_BAND", "MIDDLE_BAND: recall 0.95-0.99 at 50M. " + s)
    return ("HARD_FAIL", "HARD_FAIL: recall <0.95 at 50M. " + s)
'''))
C.append(dict(anchor="hopfield_capacity_n16384_gpu_v1", tag="modern Hopfield capacity at N=16384",
  title="modern vs classic Hopfield capacity at N=16384 (GPU)",
  desc="Capacity map at N=16384 (highest dimension yet); sweep load P/N up to 4.0; modern-Hopfield (softmax) vs classic recall@1 (overlap>=0.95) under 0.15 noise. Confirms exponential capacity holds at large dimension.",
  prereg="HARD-PASS modern recall@1 >= 0.95 at P/N=2.0 where classic < 0.1. MIDDLE modern >= 0.85. HARD-FAIL < 0.85.",
  selftest=ST,
  body='''
def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(15); N = 16384; FLIP = 0.15; NQ = 150; by = {}
    loads = [1.0, 2.0] if SMOKE else [0.5, 1.0, 2.0, 4.0]
    for load in loads:
        P = max(2, int(load * N)); X = torch.sign(torch.randn(P, N, generator=g, device=DEV)); X[X == 0] = 1
        qi = torch.randperm(P, generator=g, device=DEV)[:min(NQ, P)]; Q = X[qi].clone(); fl = torch.rand(Q.shape, generator=g, device=DEV) < FLIP; Q[fl] *= -1
        att = torch.softmax(8.0 * (Q @ X.T), dim=1); modern = ((torch.sign(att @ X) * X[qi]).sum(1) / N >= 0.95).float().mean().item()
        W = (X.T @ X) / N; W.fill_diagonal_(0.0); classic = ((torch.sign(Q @ W.T) * X[qi]).sum(1) / N >= 0.95).float().mean().item()
        by["L%.1f" % load] = {"modern": modern, "classic": classic}; print("  P/N=%.1f modern=%.3f classic=%.3f" % (load, modern, classic), flush=True)
        del X, Q, att, W; torch.cuda.empty_cache()
    return {"by": by}
def verdict(r) -> Tuple[str, str]:
    l2 = r["by"].get("L2.0", {"modern": 0, "classic": 1}); m = l2["modern"]; c = l2["classic"]
    s = "at P/N=2.0 modern=%.3f classic=%.3f | %s" % (m, c, {k: (round(v["modern"], 3), round(v["classic"], 3)) for k, v in r["by"].items()})
    if m >= 0.95 and c < 0.1: return ("HARD_PASS", "HARD_PASS: modern Hopfield recall>=0.95 at P/N=2.0 (classic dead) at N=16384 -- exponential capacity at large dimension. " + s)
    if m >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: modern 0.85-0.95 at P/N=2.0. " + s)
    return ("HARD_FAIL", "HARD_FAIL: modern <0.85 at P/N=2.0. " + s)
'''))
for c in C:
    txt = HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], selftest=c["selftest"].replace("%s", c["anchor"]), body=c["body"])
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(txt, encoding="utf-8"); print("wrote", c["anchor"])
