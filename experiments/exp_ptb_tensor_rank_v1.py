"""
exp_ptb_tensor_rank_v1 -- #3 PTB-TTRP-3: low-rank tensor profiling of Pattern B bundles -- CPU.
ROUTING: top20/pattern-b-ext #3 PTB-TTRP. Reshape bundle reps as (roles x filler-dim) matrices; low-rank (SVD) truncate at varying rank; retrieval F1 vs rank; find rank giving F1>=0.95 at <200 bytes/fact. CPU.
PRE-REGISTERED: HARD-PASS rank with F1>=0.95 gives storage <200 bytes/fact.
FORMULA SELF-TESTS (PROT-022): 1. svd reconstructs. 2. unit phasor. 3. rank sweep.
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
ANCHOR_NAME = "ptb_tensor_rank_v1"; N = 4096
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
def phasor(n, k, g): return np.exp(1j * g.uniform(-np.pi, np.pi, (k, n))).astype(np.complex64)
def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)
RANKS = [2, 4, 8] if RUN_MODE == "smoke" else [2, 4, 8, 16, 32]; NB = 200; NROLE = 8
def _selftest():
    g = np.random.default_rng(0); M = g.standard_normal((8, 8)); U,S,Vt = np.linalg.svd(M); assert np.allclose(U@np.diag(S)@Vt, M, atol=1e-4), "svd reconstructs"
    assert np.allclose(np.abs(phasor(64,1,g)[0]),1.0,atol=1e-5), "unit phasor"
    assert len(RANKS) >= 2, "rank sweep"
    print("[selftest] PASS: ptb-tensor-rank", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(7); roles = phasor(N, NROLE, g); VOCAB = 300; cache = phasor(N, VOCAB, g); by = {}; best = None
    bundles = []; gts = []
    for _ in range(NB):
        k = NROLE; fid = g.choice(VOCAB, k, replace=False); bundles.append(np.sum([roles[i]*cache[fid[i]] for i in range(k)], axis=0)); gts.append(fid)
    B = np.array(bundles)   # [NB, N] complex
    Br = np.concatenate([B.real, B.imag], 1).astype(np.float32)   # [NB, 2N]
    for rk in RANKS:
        U, S, Vt = np.linalg.svd(Br - Br.mean(0), full_matrices=False); approx = (U[:, :rk]*S[:rk]) @ Vt[:rk] + Br.mean(0)
        Bc = approx[:, :N] + 1j*approx[:, N:]
        ok = 0
        for i in range(NB):
            got = int(np.argmax((cache @ np.conj(Bc[i] * np.conj(roles[0]))).real)); ok += int(got == gts[i][0])
        f1 = ok / NB; per_fact = rk * 4 + (2*N*rk*4)/NB   # rk coeffs/fact + amortized basis
        by["rk%d" % rk] = {"f1": f1, "bytes": per_fact}
        if f1 >= 0.95 and (best is None or per_fact < best[1]): best = (rk, per_fact)
        print("  rank=%d F1=%.3f per-fact=%.0f bytes" % (rk, f1, per_fact), flush=True)
    return {"by": by, "best_bytes": best[1] if best else 1e9, "best_rk": best[0] if best else -1}
def verdict(r) -> Tuple[str, str]:
    s = "by rank: %s; best rank with F1>=0.95 = %d (%.0f bytes/fact)" % ({k: {'f1': round(v['f1'],3), 'B': round(v['bytes'])} for k,v in r["by"].items()}, r["best_rk"], r["best_bytes"])
    if r["best_bytes"] < 200: return ("HARD_PASS", "HARD_PASS: low-rank tensor profiling reaches F1>=0.95 at <200 bytes/fact -- another viable Pattern B compression axis. " + s)
    return ("HARD_FAIL", "HARD_FAIL: no rank gives F1>=0.95 under 200 bytes/fact. " + s)

print('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
