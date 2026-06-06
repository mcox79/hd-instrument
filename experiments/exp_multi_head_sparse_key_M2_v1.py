"""
exp_multi_head_sparse_key_M2_v1 -- Batch C1 #1 (FIRST priority): MMV multi-head sparse-KEY capacity -- CPU.

ROUTING: Research Batch C (composition drill). MMV theory (Davies-Eldar 2012): storing each item with M independent
  measurement heads sharing SUPPORT but with independent signs gives ~sqrt(M) support-recovery gain. Tests whether
  multi-head COMPOSES with sparse-KEY (Batch B said "sparse alone"; drill says multi-head was unfairly foreclosed).
  Each item i has shared support S_i (k positions); head h pattern = independent +-1 on S_i. Per-head sparse Hopfield bank
  W_h. Recall combines heads' fields (sum |f_h|) to recover the support. capacity M_c = max M with support-recovery>=0.95.
  H=1 baseline vs H=2 at MATCHED alpha (same per-head load M/N). CPU numpy $0.
PRE-REGISTERED: HARD-PASS H=2 capacity >= 1.3x H=1. MID 1.1-1.3x. HARD-FAIL <1.1x (multi-head doesn't compose).
FORMULA SELF-TESTS (PROT-022): 1. single item exact support. 2. shared support across heads. 3. low-load recovers.
ASCII-only. write_metrics. PROT-018 _v1 (M2 fixed head count, NOT an N-anchor).
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

ANCHOR_NAME = "multi_head_sparse_key_M2_v1"
HEADS = [1, 2]; F_SPARSE = 0.05; FLIP = 0.05
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N = 1024; LOADS = [0.02, 0.05, 0.1, 0.2, 0.4]
else:
    SEEDS = [7, 17, 23]; N = 4096; LOADS = [0.02, 0.04, 0.06, 0.1, 0.15, 0.2, 0.3, 0.4, 0.55, 0.7]


def gen(M, n, H, seed):
    g = np.random.default_rng(seed); k = max(1, int(F_SPARSE * n)); supp = []; heads = []
    for i in range(M):
        S = g.choice(n, k, replace=False); supp_h = []
        for h in range(H):
            p = np.zeros(n, np.float32); p[S] = g.integers(0, 2, k) * 2 - 1; supp_h.append(p)
        supp.append(S) if False else None; supp_h_arr = np.stack(supp_h); heads.append(supp_h_arr); supp.append(S)
    return heads, supp, k


def cap(H, seed):
    c = 0
    for load in LOADS:
        M = max(2, int(load * N)); heads, supp, k = gen(M, N, H, seed + M)
        banks = []
        for h in range(H):
            Ph = np.stack([heads[i][h] for i in range(M)]); W = (Ph.T @ Ph).astype(np.float32); np.fill_diagonal(W, 0.0); banks.append(W)
        g = np.random.default_rng(seed * 3 + M); ok = 0
        for i in range(M):
            score = np.zeros(N, np.float32)
            for h in range(H):
                cue = heads[i][h].copy(); nz = np.nonzero(cue)[0]; fl = nz[g.random(len(nz)) < FLIP]; cue[fl] *= -1
                score += np.abs(cue @ banks[h])
            rec = set(np.argsort(score)[-k:]); ok += int(rec == set(supp[i].tolist()))
        if ok / M >= 0.95:
            c = M
        else:
            break
    return c / N


def _selftest():
    heads, supp, k = gen(1, 256, 2, 0)
    assert np.array_equal(np.nonzero(heads[0][0])[0], np.sort(supp[0])), "single item support"
    assert np.array_equal(np.nonzero(heads[0][0])[0], np.nonzero(heads[0][1])[0]), "shared support across heads"
    assert cap(1, 0) > 0, "low-load recovers"
    print("[selftest] PASS: multihead", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    a = {("H%d" % H): cap(H, seed) for H in HEADS}; print("  [seed=%d] alpha %s" % (seed, {k: round(v, 4) for k, v in a.items()}), flush=True); return {"seed": seed, "alpha": a}


def verdict(ps) -> Tuple[str, str]:
    agg = {h: float(np.mean([p["alpha"][h] for p in ps])) for h in ps[0]["alpha"]}; g = agg["H2"] / max(agg["H1"], 1e-9)
    summary = "alpha H1=%.4f H2=%.4f | H2/H1=%.2fx (sqrt(2)=1.41 predicted)" % (agg["H1"], agg["H2"], g)
    if g >= 1.3:
        return ("HARD_PASS", "HARD_PASS: multi-head (M=2) composes with sparse-KEY (>=1.3x, MMV sqrt(M) gain) -- Batch B 'sparse alone' was premature. " + summary)
    if g >= 1.1:
        return ("MIDDLE_BAND", "MIDDLE_BAND: partial multi-head gain (1.1-1.3x). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: multi-head does not compose (<1.1x). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d heads=%s f=%.2f" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, HEADS, F_SPARSE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
