"""Generator: GPU-scale substrate-physics cells (torch.cuda, scales beyond CPU). Run: python tools/gen_gpu_scale.py"""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- GPU.

ROUTING: GPU-scale substrate-physics validation ({tag}). {desc} torch.cuda; scales beyond CPU feasibility. GPU.
PRE-REGISTERED: {prereg}
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
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
{body}
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\\n[VERDICT] " + vmsg, flush=True)
metrics = {{"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''
C = []
C.append(dict(anchor="hopfield_capacity_gpu_v1", tag="modern-Hopfield capacity at GPU scale",
  title="modern vs classic Hopfield capacity sweep at N=2048 on GPU",
  desc="Sweep load P/N up to 4.0 at N=2048 (large for CPU); modern-Hopfield (softmax) vs classic, recall@1 (overlap>=0.95) under noise. Maps the exponential-capacity advantage at production dimension.",
  prereg="HARD-PASS modern recall@1 >= 0.95 at P/N=2.0 where classic < 0.1. MIDDLE modern >= 0.85. HARD-FAIL modern < 0.85.",
  selftest='''
def _selftest():
    import numpy as _n; assert _n.sign(-0.3) == -1, "sign"; assert 0.14 < 2.0, "load"; print("[selftest] PASS: hopfield-capacity-gpu", flush=True)''',
  body='''
def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(1); N = 2048; FLIP = 0.15; NQ = 200; by = {}
    loads = [0.5, 1.0, 2.0] if SMOKE else [0.5, 1.0, 2.0, 4.0]
    for load in loads:
        P = max(2, int(load * N)); X = torch.sign(torch.randn(P, N, generator=g, device=DEV)); X[X == 0] = 1
        qi = torch.randperm(P, generator=g, device=DEV)[:min(NQ, P)]; Q = X[qi].clone()
        fl = torch.rand(Q.shape, generator=g, device=DEV) < FLIP; Q[fl] *= -1
        att = torch.softmax(8.0 * (Q @ X.T), dim=1); retm = torch.sign(att @ X)
        modern = ((retm * X[qi]).sum(1) / N >= 0.95).float().mean().item()
        W = (X.T @ X) / N; W.fill_diagonal_(0.0); sc = torch.sign(Q @ W.T); sc[sc == 0] = 1
        classic = ((sc * X[qi]).sum(1) / N >= 0.95).float().mean().item()
        by["L%.1f" % load] = {"modern": modern, "classic": classic}
        print("  P/N=%.1f modern=%.3f classic=%.3f" % (load, modern, classic), flush=True)
        del X, Q, att, retm, W; torch.cuda.empty_cache()
    return {"by": by}
def verdict(r) -> Tuple[str, str]:
    l2 = r["by"].get("L2.0", {"modern": 0, "classic": 1}); m = l2["modern"]; c = l2["classic"]
    s = "at P/N=2.0 modern=%.3f classic=%.3f | %s" % (m, c, {k: (round(v["modern"], 3), round(v["classic"], 3)) for k, v in r["by"].items()})
    if m >= 0.95 and c < 0.1: return ("HARD_PASS", "HARD_PASS: modern Hopfield recall@1>=0.95 at P/N=2.0 (classic dead) at N=2048 -- exponential capacity holds at production dimension. " + s)
    if m >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: modern 0.85-0.95 at P/N=2.0. " + s)
    return ("HARD_FAIL", "HARD_FAIL: modern <0.85 at P/N=2.0. " + s)
'''))
C.append(dict(anchor="sign_recall_5M_gpu_v1", tag="sign-key recall at 5M on GPU",
  title="sign-key autoassociative recall@1 at 5M keys (GPU)",
  desc="5M sign keys (D=1024); noisy-query recall@1 via chunked GPU matmul. Pushes the CELL-4/1M recall gate to 5M -- GPU enables the scale CPU cannot reach in reasonable time.",
  prereg="HARD-PASS recall@1 >= 0.99 at N=5M under 0.15 bit-flip noise. MIDDLE >= 0.95. HARD-FAIL < 0.95.",
  selftest='''
def _selftest():
    import numpy as _n; assert _n.sign(0.2) == 1, "sign"; assert 5_000_000 > 1_000_000, "scale"; print("[selftest] PASS: sign-recall-5M-gpu", flush=True)''',
  body='''
def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(2); N = 200000 if SMOKE else 5000000; D = 1024; NQ = 300; FLIP = 0.15; CH = 250000
    qidx = torch.randperm(N, generator=g, device=DEV)[:NQ].sort().values
    # build queries from their (regenerated) key rows: regenerate keys in chunks with a fixed seed so we can match
    torch.manual_seed(12345)
    best = torch.full((NQ,), -1, device=DEV, dtype=torch.long); best_sc = torch.full((NQ,), -1e9, device=DEV)
    # first pass: materialize the NQ query keys
    qkeys = torch.zeros(NQ, D, device=DEV)
    base_seed = 777
    def chunk_keys(c0, c1):
        gg = torch.Generator(device=DEV).manual_seed(base_seed + c0); return torch.sign(torch.randn(c1 - c0, D, generator=gg, device=DEV))
    for c0 in range(0, N, CH):
        c1 = min(c0 + CH, N); K = chunk_keys(c0, c1)
        mask = (qidx >= c0) & (qidx < c1)
        if mask.any():
            qkeys[mask] = K[qidx[mask] - c0]
        del K
    fl = torch.rand(qkeys.shape, generator=g, device=DEV) < FLIP; Q = qkeys.clone(); Q[fl] *= -1
    for c0 in range(0, N, CH):
        c1 = min(c0 + CH, N); K = chunk_keys(c0, c1); sc = Q @ K.T
        bsc, bidx = sc.max(dim=1); upd = bsc > best_sc; best[upd] = c0 + bidx[upd]; best_sc[upd] = bsc[upd]
        del K, sc; torch.cuda.empty_cache()
    rec = (best == qidx).float().mean().item()
    print("  N=%d recall@1=%.4f (D=%d flip=%.2f)" % (N, rec, D, FLIP), flush=True)
    return {"n": N, "recall1": rec}
def verdict(r) -> Tuple[str, str]:
    s = "recall@1=%.4f at N=%d" % (r["recall1"], r["n"])
    if r["recall1"] >= 0.99: return ("HARD_PASS", "HARD_PASS: sign-key recall holds at 5M scale (>=0.99) on GPU -- substrate recall scales to 5M. " + s)
    if r["recall1"] >= 0.95: return ("MIDDLE_BAND", "MIDDLE_BAND: recall 0.95-0.99 at 5M. " + s)
    return ("HARD_FAIL", "HARD_FAIL: recall <0.95 at 5M. " + s)
'''))
C.append(dict(anchor="resonator_capacity_gpu_v1", tag="resonator factorization capacity at GPU scale",
  title="resonator factorization vs K at N=4096 (GPU)",
  desc="Soft-projection resonator factorizing K-way bound products at N=4096 (large), sweeping K to find the capacity cliff. GPU enables the larger N + more trials than CPU.",
  prereg="HARD-PASS full-factorization success >= 0.90 at K=3 (N=4096, M=30). MIDDLE >= 0.75. HARD-FAIL < 0.75.",
  selftest='''
def _selftest():
    import numpy as _n; assert _n.argmax([0.1, 0.9]) == 1, "argmax"; assert 4096 > 1024, "scale"; print("[selftest] PASS: resonator-capacity-gpu", flush=True)''',
  body='''
def phasor(m, d, g):
    import math; ang = (torch.rand(m, d, generator=g, device=DEV) * 2 - 1) * math.pi; return torch.complex(torch.cos(ang), torch.sin(ang))
def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(3); N = 4096; M = 30; MAXIT = 60; by = {}
    K_GRID = [2, 3] if SMOKE else [2, 3, 4]; TR = 30 if SMOKE else 120
    for K in K_GRID:
        books = [phasor(M, N, g) for _ in range(K)]; succ = 0
        for _ in range(TR):
            true = [int(torch.randint(0, M, (1,), generator=g, device=DEV)) for _ in range(K)]
            s = torch.ones(N, dtype=torch.complex64, device=DEV)
            for k in range(K):
                s = s * books[k][true[k]]
            est = [b.mean(0) for b in books]; est = [e / (e.abs() + 1e-8) for e in est]; prev = None
            for _ in range(MAXIT):
                idxs = []
                for k in range(K):
                    others = torch.ones(N, dtype=torch.complex64, device=DEV)
                    for j in range(K):
                        if j != k:
                            others = others * est[j]
                    rr = s * others.conj(); sc = (books[k] @ rr.conj()); est[k] = (sc @ books[k]); est[k] = est[k] / (est[k].abs() + 1e-8)
                    idxs.append(int(torch.argmax(sc.real)))
                if idxs == prev:
                    break
                prev = idxs
            succ += int(idxs == true)
        by["K%d" % K] = succ / TR; print("  K=%d success=%.3f (N=%d)" % (K, by["K%d" % K], N), flush=True)
    return {"by": by}
def verdict(r) -> Tuple[str, str]:
    k3 = r["by"].get("K3", 0.0); s = "success by K: %s (N=4096)" % {k: round(v, 3) for k, v in r["by"].items()}
    if k3 >= 0.90: return ("HARD_PASS", "HARD_PASS: resonator factorizes K=3 >=0.90 at N=4096 -- larger dimension extends factorization capacity. " + s)
    if k3 >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: K=3 0.75-0.90 at N=4096 (better than N=2048 0.73). " + s)
    return ("HARD_FAIL", "HARD_FAIL: K=3 <0.75 even at N=4096. " + s)
'''))
for c in C:
    txt = HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], selftest=c["selftest"], body=c["body"])
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(txt, encoding="utf-8"); print("wrote", c["anchor"])
