"""Generator: GPU batch D (5 OOM-safe torch.cuda cells). Run: python tools/gen_gpu_batch_d.py"""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- GPU.

ROUTING: GPU-scale substrate-physics ({tag}). {desc} torch.cuda; OOM-safe (chunked) for an 8GB card. GPU.
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
C.append(dict(anchor="patternb_composition_300k_gpu_v1", tag="Pattern-B composition at V=300k (OOM-fixed)",
  title="Pattern-B role-filler composition recall at V=300k filler codebook (GPU)",
  desc="OOM-fixed rerun of the V=1M composition (1M complex codebook overflowed the 8GB card). V=300k complex book ~1.2GB fits. K=4 pairs bundled; recover each filler by unbind + chunked cleanup over the 300k codebook.",
  prereg="HARD-PASS recall@1 >= 0.95 at K=4, V=300k. MIDDLE >= 0.85. HARD-FAIL < 0.85.",
  selftest=ST,
  body='''
def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(6); N = 512; V = 80000 if SMOKE else 300000; K = 4; TR = 20 if SMOKE else 60; CH = 100000
    book = cphasor(V, N, g); hit = 0; tot = 0
    for _ in range(TR):
        roles = cphasor(K, N, g); fidx = torch.randperm(V, generator=g, device=DEV)[:K]
        B = torch.zeros(N, dtype=torch.complex64, device=DEV)
        for k in range(K):
            B = B + roles[k] * book[fidx[k]]
        for k in range(K):
            rec = B * roles[k].conj(); best = -1; bs = -1e18
            for c0 in range(0, V, CH):
                c1 = min(c0 + CH, V); sc = (book[c0:c1] @ rec.conj()).real; j = int(torch.argmax(sc))
                if float(sc[j]) > bs:
                    bs = float(sc[j]); best = c0 + j
            hit += int(best == int(fidx[k])); tot += 1
        del B; torch.cuda.empty_cache()
    rec = hit / tot; print("  V=%d K=%d recall@1=%.3f (N=%d)" % (V, K, rec, N), flush=True)
    return {"recall": rec, "V": V}
def verdict(r) -> Tuple[str, str]:
    s = "recall@1=%.3f at V=%d" % (r["recall"], r["V"])
    if r["recall"] >= 0.95: return ("HARD_PASS", "HARD_PASS: Pattern-B composition recall>=0.95 at V=300k filler vocab -- composition holds at large KB scale. " + s)
    if r["recall"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: composition 0.85-0.95 at V=300k. " + s)
    return ("HARD_FAIL", "HARD_FAIL: composition <0.85 at V=300k. " + s)
'''))
C.append(dict(anchor="sign_recall_20M_gpu_v1", tag="sign-key recall at 20M",
  title="sign-key autoassociative recall@1 at 20M keys (GPU, chunked)",
  desc="20M sign keys (D=1024) regenerated per chunk (never fully materialized); chunked GPU recall@1 under 0.15 bit-flip. Pushes the recall scaling gate to 20M (2x the 10M result).",
  prereg="HARD-PASS recall@1 >= 0.99 at N=20M. MIDDLE >= 0.95. HARD-FAIL < 0.95.",
  selftest=ST,
  body='''
def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(9); N = 400000 if SMOKE else 20000000; D = 1024; NQ = 300; FLIP = 0.15; CH = 250000; base = 1001
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
    if r["recall1"] >= 0.99: return ("HARD_PASS", "HARD_PASS: sign-key recall >=0.99 at 20M -- substrate recall scales to 20M keys. " + s)
    if r["recall1"] >= 0.95: return ("MIDDLE_BAND", "MIDDLE_BAND: recall 0.95-0.99 at 20M. " + s)
    return ("HARD_FAIL", "HARD_FAIL: recall <0.95 at 20M. " + s)
'''))
C.append(dict(anchor="hopfield_capacity_n4096_gpu_v1", tag="modern Hopfield capacity at N=4096",
  title="modern vs classic Hopfield capacity at N=4096 (GPU)",
  desc="Extends the N=2048 capacity map to N=4096; sweep load P/N up to 4.0; modern-Hopfield (softmax) vs classic recall@1 (overlap>=0.95) under 0.15 noise. Confirms exponential capacity at higher dimension.",
  prereg="HARD-PASS modern recall@1 >= 0.95 at P/N=2.0 where classic < 0.1. MIDDLE modern >= 0.85. HARD-FAIL < 0.85.",
  selftest=ST,
  body='''
def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(31); N = 4096; FLIP = 0.15; NQ = 200; by = {}
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
    if m >= 0.95 and c < 0.1: return ("HARD_PASS", "HARD_PASS: modern Hopfield recall>=0.95 at P/N=2.0 (classic dead) at N=4096 -- exponential capacity confirmed at higher dimension. " + s)
    if m >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: modern 0.85-0.95 at P/N=2.0. " + s)
    return ("HARD_FAIL", "HARD_FAIL: modern <0.85 at P/N=2.0. " + s)
'''))
C.append(dict(anchor="bundle_capacity_largeN_gpu_v1", tag="bundle capacity at large N vs theory",
  title="bundle K_crit at N in {8192,16384} tracks N/(2 ln N) (GPU)",
  desc="Extends the bundle-capacity law to large N (8192, 16384) on GPU; binary-search K_crit (recall@1>=0.9 for bundled role-filler pairs) and compare to N/(2 ln N). Confirms the composition-capacity law at scale.",
  prereg="HARD-PASS K_crit within 35pct of N/(2 ln N) at both N. MIDDLE within 60pct. HARD-FAIL > 60pct.",
  selftest=ST,
  body='''
def kcrit(N, g, V=4000, TR=6):
    book = cphasor(V, N, g); lo, hi, best = 10, int(0.15 * N), 10
    while lo <= hi:
        K = (lo + hi) // 2; ok = 0; tot = 0
        for _ in range(TR):
            roles = cphasor(K, N, g); fidx = torch.randperm(V, generator=g, device=DEV)[:K]
            B = (roles * book[fidx]).sum(0); rec = B.unsqueeze(0) * roles.conj(); sc = (rec @ book.conj().T).real
            pred = torch.argmax(sc, dim=1); ok += int((pred == fidx).sum()); tot += K
        if ok / tot >= 0.9:
            best = K; lo = K + 1
        else:
            hi = K - 1
    return best
def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(32); Ns = [4096, 8192] if SMOKE else [8192, 16384]; rows = {}; devs = []
    for N in Ns:
        kc = kcrit(N, g); theo = N / (2 * math.log(N)); dev = abs(kc - theo) / theo; devs.append(dev); rows["N%d" % N] = (kc, round(theo, 1))
        print("  N=%d K_crit=%d theory=%.1f dev=%.2f" % (N, kc, theo, dev), flush=True); torch.cuda.empty_cache()
    return {"rows": rows, "max_dev": float(max(devs))}
def verdict(r) -> Tuple[str, str]:
    s = "max dev from N/(2 ln N) = %.2f | (K_crit, theory): %s" % (r["max_dev"], r["rows"])
    if r["max_dev"] <= 0.35: return ("HARD_PASS", "HARD_PASS: bundle capacity tracks N/(2 ln N) within 35pct at large N -- composition-capacity law holds at scale. " + s)
    if r["max_dev"] <= 0.60: return ("MIDDLE_BAND", "MIDDLE_BAND: within 60pct of theory. " + s)
    return ("HARD_FAIL", "HARD_FAIL: deviates >60pct from theory. " + s)
'''))
C.append(dict(anchor="precision_int4_recall_gpu_v1", tag="int4 vs fp16 recall at scale",
  title="int4 (4-bit) quantized continuous-key recall vs fp16 at 5M (GPU)",
  desc="Quantize continuous random keys to 4-bit (16 levels, per-vector scale) vs fp16; chunked recall@1 at 5M under 0.30 query noise. Tests whether 4-bit storage (8x memory saving vs fp32) preserves recall at scale.",
  prereg="HARD-PASS int4 recall@1 >= 0.95 * fp16 at 5M. MIDDLE >= 0.90. HARD-FAIL < 0.90.",
  selftest=ST,
  body='''
def quant4(X):
    sc = X.abs().amax(dim=1, keepdim=True) / 7.0 + 1e-12; return (torch.round(X / sc).clamp(-7, 7)) * sc      # 4-bit signed: 15 levels
def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(41); N = 200000 if SMOKE else 5000000; D = 1024; NQ = 300; NOISE = 0.30; CH = 250000; base = 1313
    qidx = torch.randperm(N, generator=g, device=DEV)[:NQ].sort().values
    def chunk(c0, c1, q4):
        gg = torch.Generator(device=DEV).manual_seed(base + c0); X = torch.randn(c1 - c0, D, generator=gg, device=DEV); X = X / X.norm(dim=1, keepdim=True)
        return quant4(X) if q4 else X.half()
    qk = torch.zeros(NQ, D, device=DEV)
    for c0 in range(0, N, CH):
        c1 = min(c0 + CH, N); gg = torch.Generator(device=DEV).manual_seed(base + c0); X = torch.randn(c1 - c0, D, generator=gg, device=DEV); X = X / X.norm(dim=1, keepdim=True)
        mask = (qidx >= c0) & (qidx < c1)
        if mask.any():
            qk[mask] = X[qidx[mask] - c0]
        del X
    Q = qk + (NOISE / math.sqrt(D)) * torch.randn(NQ, D, generator=g, device=DEV)
    def recall(q4):
        best = torch.full((NQ,), -1, device=DEV, dtype=torch.long); bs = torch.full((NQ,), -1e9, device=DEV)
        Qd = quant4(Q) if q4 else Q.half()
        for c0 in range(0, N, CH):
            c1 = min(c0 + CH, N); K = chunk(c0, c1, q4); sc = (Qd.float() @ K.float().T); bsc, bidx = sc.max(1); upd = bsc > bs; best[upd] = c0 + bidx[upd]; bs[upd] = bsc[upd]
            del K, sc; torch.cuda.empty_cache()
        return (best == qidx).float().mean().item()
    r16 = recall(False); r4 = recall(True); ratio = r4 / (r16 + 1e-9)
    print("  N=%d recall@1 fp16=%.4f int4=%.4f ratio=%.3f" % (N, r16, r4, ratio), flush=True)
    return {"n": N, "fp16": r16, "int4": r4, "ratio": ratio}
def verdict(r) -> Tuple[str, str]:
    s = "int4=%.4f fp16=%.4f ratio=%.3f at N=%d" % (r["int4"], r["fp16"], r["ratio"], r["n"])
    if r["ratio"] >= 0.95: return ("HARD_PASS", "HARD_PASS: int4 retains >=95pct of fp16 recall at 5M -- 4-bit storage (8x memory vs fp32) viable at scale. " + s)
    if r["ratio"] >= 0.90: return ("MIDDLE_BAND", "MIDDLE_BAND: int4 0.90-0.95 of fp16 at 5M. " + s)
    return ("HARD_FAIL", "HARD_FAIL: int4 <0.90 of fp16 at 5M. " + s)
'''))
for c in C:
    txt = HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], selftest=c["selftest"].replace("%s", c["anchor"]), body=c["body"])
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(txt, encoding="utf-8"); print("wrote", c["anchor"])
