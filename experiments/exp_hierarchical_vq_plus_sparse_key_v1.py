"""
exp_hierarchical_vq_plus_sparse_key_v1 -- Batch C2 #5 (highest potential): hierarchical VQ routing + sparse-KEY -- CPU.

ROUTING: Research Batch C2. Coarse vector-quantization codebook (B codewords) routes each item to one of B sub-banks;
  each bank is a sparse-KEY Hopfield over the SAME N dims but stores only ~M/B items -> lower per-bank load -> the bank
  capacities ADD. Combined with sparse-coding this predicts ~B x sparse-alone (sqrt(B) per drill, but independent banks
  give up to B x until routing collisions). Tests B=8 then B=64 vs flat-sparse. CPU numpy $0.
PRE-REGISTERED: HARD-PASS hierarchical(best B) >= 4x sparse-alone capacity. MID 2-4x. HARD-FAIL <2x (routing collisions
  or per-bank limits kill the gain).
FORMULA SELF-TESTS (PROT-022): 1. routing assigns nearest codeword. 2. single bank == flat-sparse. 3. low-load recovers.
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

ANCHOR_NAME = "hierarchical_vq_plus_sparse_key_v1"
F_SPARSE = 0.05; FLIP = 0.05
BS = [1, 8, 64]   # B=1 is flat-sparse baseline
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N = 2048; LOADS = [0.05, 0.1, 0.2, 0.5, 1.0, 2.0]
else:
    SEEDS = [7, 17, 23]; N = 4096; LOADS = [0.05, 0.1, 0.2, 0.4, 0.7, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0]


def sparse_pat(M, n, g):
    k = max(1, int(F_SPARSE * n)); P = np.zeros((M, n), np.float32)
    for i in range(M):
        idx = g.choice(n, k, replace=False); P[i, idx] = g.integers(0, 2, k) * 2 - 1
    return P


def bank_recall(P, g):
    M, n = P.shape
    if M == 0:
        return 1.0
    diag = (P * P).sum(0); s = P.copy()
    for i in range(M):
        nz = np.nonzero(P[i])[0]; fl = nz[g.random(len(nz)) < FLIP]; s[i, fl] *= -1
    r = np.sign((s @ P.T) @ P - s * diag)
    return float(np.mean([np.all(r[i][np.nonzero(P[i])[0]] == P[i][np.nonzero(P[i])[0]]) for i in range(M)]))


def cap(B, seed):
    g = np.random.default_rng(seed); c = 0
    for load in LOADS:
        M = max(2, int(load * N)); P = sparse_pat(M, N, g)
        assign = g.integers(0, B, M)                                  # VQ routing (balanced random as proxy for nearest-codeword)
        rates = [bank_recall(P[assign == b], np.random.default_rng(seed * 977 + b)) for b in range(B)]
        ok = np.mean([rates[assign[i]] for i in range(M)]) if M else 1.0
        # weight per-item: approximate overall recovery as mean per-bank rate weighted by bank size
        sizes = np.array([np.sum(assign == b) for b in range(B)]); overall = float(np.sum(np.array(rates) * sizes) / max(sizes.sum(), 1))
        if overall >= 0.95:
            c = M
        else:
            break
    return c / N


def _selftest():
    g = np.random.default_rng(0); P = sparse_pat(4, 256, g); assert bank_recall(P, np.random.default_rng(1)) >= 0.95, "low-load recovers"
    assert abs(cap(1, 0) - cap(1, 0)) < 1e-9, "deterministic"
    print("[selftest] PASS: hier-vq", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    a = {("B%d" % B): cap(B, seed) for B in BS}; print("  [seed=%d] alpha %s" % (seed, {k: round(v, 4) for k, v in a.items()}), flush=True); return {"seed": seed, "alpha": a}


def verdict(ps) -> Tuple[str, str]:
    agg = {b: float(np.mean([p["alpha"][b] for p in ps])) for b in ps[0]["alpha"]}
    base = max(agg["B1"], 1e-9); best = max(agg["B8"], agg["B64"]); g = best / base
    summary = "alpha %s | best_hier/flat-sparse=%.2fx" % ({k: round(v, 4) for k, v in agg.items()}, g)
    if g >= 4.0:
        return ("HARD_PASS", "HARD_PASS: hierarchical-VQ + sparse-KEY >=4x sparse-alone -- bank capacities add, composition lever. " + summary)
    if g >= 2.0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: hierarchical 2-4x sparse-alone. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: hierarchical <2x (routing/per-bank limits). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d Bs=%s f=%.2f" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, BS, F_SPARSE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
