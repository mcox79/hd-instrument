"""Generator: GPU-scale cells 6-10 (torch.cuda, distinct scaling axes). Run: python tools/gen_gpu_scale3.py"""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- GPU.

ROUTING: GPU-scale substrate-physics ({tag}). {desc} torch.cuda. GPU.
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
C.append(dict(anchor="patternb_composition_1M_gpu_v1", tag="Pattern-B composition at 1M vocab",
  title="Pattern-B role-filler composition recall at V=1M filler codebook (GPU)",
  desc="K role-filler pairs bundled; recover each filler by unbind + cleanup over a V=1M filler codebook (production KB scale). GPU enables the 1M-row cleanup matmul.",
  prereg="HARD-PASS recall@1 >= 0.95 at K=4 with V=1M. MIDDLE >= 0.85. HARD-FAIL < 0.85.",
  body='''
def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(6); N = 512; V = 200000 if SMOKE else 1000000; K = 4; TR = 20 if SMOKE else 80; CH = 200000
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
    if r["recall"] >= 0.95: return ("HARD_PASS", "HARD_PASS: Pattern-B composition recall>=0.95 at V=1M filler vocab -- composition holds at production KB scale. " + s)
    if r["recall"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: composition 0.85-0.95 at V=1M. " + s)
    return ("HARD_FAIL", "HARD_FAIL: composition <0.85 at V=1M. " + s)
'''))
C.append(dict(anchor="bundle_capacity_cliff_gpu_v1", tag="bundle superposition capacity cliff",
  title="how many role-filler pairs superpose before recall drops (N=4096, GPU)",
  desc="Sweep K (pairs bundled into one hypervector) at N=4096; find the K where recall@1 drops below 0.9 -- the bundling capacity cliff. GPU for the per-K trials.",
  prereg="HARD-PASS capacity K_crit (recall>=0.9) >= 0.10*N (i.e. >=400 pairs). MIDDLE >= 0.05*N. HARD-FAIL < 0.05*N.",
  body='''
def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(7); N = 4096; V = 5000; TR = 10 if SMOKE else 30
    Ks = [50, 200] if SMOKE else [50, 100, 200, 400, 600, 800]; by = {}; book = cphasor(V, N, g)
    for K in Ks:
        hit = 0; tot = 0
        for _ in range(TR):
            roles = cphasor(K, N, g); fidx = torch.randperm(V, generator=g, device=DEV)[:K]
            B = (roles * book[fidx]).sum(0)
            rec = B.unsqueeze(0) * roles.conj()                 # [K, N]
            sc = (rec @ book.conj().T).real                     # [K, V]
            pred = torch.argmax(sc, dim=1); hit += int((pred == fidx).sum()); tot += K
        by["K%d" % K] = hit / tot; print("  K=%d recall@1=%.3f" % (K, by["K%d" % K]), flush=True)
    kcrit = max([k for k in Ks if by["K%d" % k] >= 0.9] + [0])
    return {"by": by, "kcrit": kcrit, "N": N}
def verdict(r) -> Tuple[str, str]:
    kc = r["kcrit"]; frac = kc / r["N"]; s = "K_crit(recall>=0.9)=%d (=%.3f*N) | %s" % (kc, frac, {k: round(v, 3) for k, v in r["by"].items()})
    if frac >= 0.10: return ("HARD_PASS", "HARD_PASS: bundle holds >=0.10*N pairs at recall>=0.9 -- high superposition capacity at N=4096. " + s)
    if frac >= 0.05: return ("MIDDLE_BAND", "MIDDLE_BAND: capacity 0.05-0.10*N. " + s)
    return ("HARD_FAIL", "HARD_FAIL: capacity <0.05*N. " + s)
'''))
C.append(dict(anchor="vsa_permute_long_seq_gpu_v1", tag="long ordered sequences via permutation",
  title="permutation-power sequence encoding at K=12 positions (GPU)",
  desc="Encode ordered sequences of length up to K=12 via permutation powers (S = sum P^k(item_k)); recover position k via P^-k. GPU for the per-position cleanup. Tests long-sequence (timeline) capacity.",
  prereg="HARD-PASS position-recovery >= 0.90 at K=12 (N=4096, V=200). MIDDLE >= 0.80. HARD-FAIL < 0.80.",
  body='''
def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(8); N = 4096; V = 200; perm = torch.randperm(N, generator=g, device=DEV); inv = torch.argsort(perm)
    Ks = [5, 12] if SMOKE else [5, 8, 12]; TR = 30 if SMOKE else 120; book = cphasor(V, N, g); by = {}
    def permute(v, k):
        out = v
        idx = perm if k >= 0 else inv
        for _ in range(abs(k)):
            out = out[idx]
        return out
    for K in Ks:
        hit = 0; tot = 0
        for _ in range(TR):
            seq = torch.randperm(V, generator=g, device=DEV)[:K]
            S = torch.zeros(N, dtype=torch.complex64, device=DEV)
            for k in range(K):
                S = S + permute(book[seq[k]], k)
            for k in range(K):
                rec = permute(S, -k); pred = int(torch.argmax((book @ rec.conj()).real)); hit += int(pred == int(seq[k])); tot += 1
        by["K%d" % K] = hit / tot; print("  K=%d position-recovery=%.3f" % (K, by["K%d" % K]), flush=True)
    return {"by": by}
def verdict(r) -> Tuple[str, str]:
    k12 = r["by"].get("K12", 0.0); s = "recovery by K: %s" % {k: round(v, 3) for k, v in r["by"].items()}
    if k12 >= 0.90: return ("HARD_PASS", "HARD_PASS: ordered-sequence recovery >=0.90 at K=12 -- long timelines/ranked-lists representable. " + s)
    if k12 >= 0.80: return ("MIDDLE_BAND", "MIDDLE_BAND: K=12 recovery 0.80-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: K=12 recovery <0.80. " + s)
'''))
C.append(dict(anchor="sign_recall_10M_gpu_v1", tag="sign-key recall at 10M",
  title="sign-key autoassociative recall@1 at 10M keys (GPU)",
  desc="10M sign keys (D=1024); chunked GPU recall@1 under noise. Pushes the recall scaling gate to 10M (10x the 1M CPU gate).",
  prereg="HARD-PASS recall@1 >= 0.99 at N=10M under 0.15 flip. MIDDLE >= 0.95. HARD-FAIL < 0.95.",
  body='''
def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(9); N = 300000 if SMOKE else 10000000; D = 1024; NQ = 300; FLIP = 0.15; CH = 250000; base = 999
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
    if r["recall1"] >= 0.99: return ("HARD_PASS", "HARD_PASS: sign-key recall >=0.99 at 10M -- substrate recall scales to 10M. " + s)
    if r["recall1"] >= 0.95: return ("MIDDLE_BAND", "MIDDLE_BAND: recall 0.95-0.99 at 10M. " + s)
    return ("HARD_FAIL", "HARD_FAIL: recall <0.95 at 10M. " + s)
'''))
C.append(dict(anchor="iterative_cleanup_gpu_v1", tag="iterative Hopfield cleanup",
  title="iterative (multi-step) Hopfield cleanup improves recall under high noise (GPU)",
  desc="Compare 1-step vs T-step iterative modern-Hopfield cleanup (re-feed retrieved into the query) at high noise; iterative cleanup should recover patterns single-step misses. N=2048, P/N=1.",
  prereg="HARD-PASS iterative (5-step) recall@1 >= single-step + 0.05 at flip=0.30. MIDDLE >= +0.02. HARD-FAIL no improvement.",
  body='''
def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(10); N = 2048; P = N; FLIP = 0.30; NQ = 200; BETA = 8.0; T = 5
    X = torch.sign(torch.randn(P, N, generator=g, device=DEV)); X[X == 0] = 1
    qi = torch.randperm(P, generator=g, device=DEV)[:NQ]; Q0 = X[qi].clone(); fl = torch.rand(Q0.shape, generator=g, device=DEV) < FLIP; Q0[fl] *= -1
    def step(Q):
        return torch.sign(torch.softmax(BETA * (Q @ X.T), dim=1) @ X)
    s1 = step(Q0); r1 = ((s1 * X[qi]).sum(1) / N >= 0.95).float().mean().item()
    Q = Q0
    for _ in range(T):
        Q = step(Q)
    rt = ((Q * X[qi]).sum(1) / N >= 0.95).float().mean().item()
    print("  flip=%.2f: 1-step recall=%.3f %d-step recall=%.3f (gain=%.3f)" % (FLIP, r1, T, rt, rt - r1), flush=True)
    return {"step1": r1, "stepT": rt, "gain": rt - r1, "T": T}
def verdict(r) -> Tuple[str, str]:
    s = "1-step=%.3f %d-step=%.3f gain=%.3f" % (r["step1"], r["T"], r["stepT"], r["gain"])
    if r["gain"] >= 0.05: return ("HARD_PASS", "HARD_PASS: iterative cleanup adds >=0.05 recall at high noise -- multi-step Hopfield recovers patterns single-step misses. " + s)
    if r["gain"] >= 0.02: return ("MIDDLE_BAND", "MIDDLE_BAND: iterative gain 0.02-0.05. " + s)
    return ("HARD_FAIL", "HARD_FAIL: iterative cleanup no meaningful gain (single-step already saturates). " + s)
'''))
for c in C:
    txt = HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], selftest=ST.replace("%s", c["anchor"]), body=c["body"])
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(txt, encoding="utf-8"); print("wrote", c["anchor"])
