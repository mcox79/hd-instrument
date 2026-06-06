"""
exp_substrate_sparse_vs_dense_write_regime_alpha_n4096_n16384_v1 -- Slot 3: sparse vs dense write capacity alpha -- CPU.

ROUTING: PRIORITY_QUEUE_LIVE Slot 3 (Research-confirmed metric). The capacity-scaling MIDDLE showed two-regime alpha
  (0.060 small N -> 0.040 large N). This tests whether a NOVELTY-GATED SPARSE write rule recovers alpha > 0.040 at large
  N (capacity rescue). DENSE: W += outer(p,p). SPARSE (f=0.10): per pattern, residual r = p - W@p; write only top-f |r|
  components -> W += outer(sparsify(r,f), p) (sparse delta-rule; fewer interfering writes -> linear-noise regime).
  Metric = Research-confirmed auto-assoc Hopfield (zero-diag W, flip-cue 0.05, exact recovery, sweep M -> alpha=M*/N).
  CPU numpy $0.

PRE-REGISTERED bands: HARD-PASS sparse alpha >= 0.055 at N=16384 (recovers above dense ~0.040 -> major rescue path).
  MIDDLE: sparse in (dense, 0.055). HARD-FAIL: sparse <= dense (no rescue).
FORMULA SELF-TESTS (PROT-022): 1. sparsify top-f. 2. dense recovers low-load. 3. dense overloads high-load.
ASCII-only. write_metrics. PROT-018: _v1 (N in name is grid, not single).
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
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_sparse_vs_dense_write_regime_alpha_n4096_n16384_v1"
FLIP = 0.05; STEPS = 6; F_SPARSE = 0.10; LR = 1.0
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_GRID = [1024]; LOADS = [0.05, 0.1, 0.14, 0.2, 0.3]
else:
    SEEDS = [7, 17, 23]; N_GRID = [4096, 16384]; LOADS = [0.03, 0.04, 0.05, 0.06, 0.08, 0.10, 0.13, 0.16, 0.20]


def rand_pm1(M, n, g):
    return (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)


def sparsify_rows(R, f):
    out = np.zeros_like(R); k = max(1, int(f * R.shape[1]))
    for i in range(R.shape[0]):
        idx = np.argpartition(np.abs(R[i]), -k)[-k:]; out[i, idx] = R[i, idx]
    return out


def build_W_dense(P):
    W = (P.T @ P).astype(np.float32); np.fill_diagonal(W, 0.0); return W


def build_W_sparse(P, f):
    M, n = P.shape; W = np.zeros((n, n), dtype=np.float32)
    for i in range(M):
        r = P[i] - W @ P[i]                                   # novelty residual
        rs = np.zeros(n, dtype=np.float32); k = max(1, int(f * n))
        idx = np.argpartition(np.abs(r), -k)[-k:]; rs[idx] = r[idx]
        W += LR * np.outer(rs, P[i])
    np.fill_diagonal(W, 0.0); return W


def recall(P, W, g):
    M, n = P.shape
    s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(STEPS):
        s = np.sign(s @ W.T); s[s == 0] = 1.0
    return float(np.mean(np.all(s == P, axis=1)))


def _selftest():
    r = np.array([[0.1, 0.9, 0.2, 0.05]], np.float32); s = sparsify_rows(r, 0.25)
    assert np.count_nonzero(s) == 1 and s[0, 1] == 0.9, "sparsify top-f"
    g = np.random.default_rng(0); n = 256; P = rand_pm1(20, n, g)
    assert recall(P, build_W_dense(P), g) >= 0.95, "dense recovers low-load"
    assert recall(rand_pm1(200, n, g), build_W_dense(rand_pm1(200, n, g)), g) < 0.95, "dense overloads high-load"
    print("[selftest] PASS: sparsify dense", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def capacity(n, builder, seed):
    cap = 0
    for load in LOADS:
        M = max(2, int(load * n)); g = np.random.default_rng(seed * 1000 + M)
        P = rand_pm1(M, n, g); W = builder(P)
        if recall(P, W, np.random.default_rng(seed * 7 + M)) >= 0.95:
            cap = M
        else:
            break
    return cap


def run_seed(seed) -> Dict:
    res = {"seed": seed, "by_N": {}}
    for n in N_GRID:
        cd = capacity(n, build_W_dense, seed); cs = capacity(n, lambda P: build_W_sparse(P, F_SPARSE), seed)
        res["by_N"]["N%d" % n] = {"dense_alpha": cd / n, "sparse_alpha": cs / n, "dense_cap": cd, "sparse_cap": cs}
    return res


def verdict(ps) -> Tuple[str, str]:
    nmax = "N%d" % N_GRID[-1]
    da = float(np.mean([p["by_N"][nmax]["dense_alpha"] for p in ps])); sa = float(np.mean([p["by_N"][nmax]["sparse_alpha"] for p in ps]))
    parts = " ".join("%s: dense_a=%.3f sparse_a=%.3f" % (k, np.mean([p["by_N"][k]["dense_alpha"] for p in ps]), np.mean([p["by_N"][k]["sparse_alpha"] for p in ps])) for k in ps[0]["by_N"])
    summary = "at %s: dense_alpha=%.3f sparse_alpha=%.3f | %s" % (nmax, da, sa, parts)
    if sa >= 0.055:
        return ("HARD_PASS", "HARD_PASS: sparse write recovers alpha>=0.055 at %s (above dense ~0.040) -- capacity rescue path. " % nmax + summary)
    if sa > da:
        return ("MIDDLE_BAND", "MIDDLE_BAND: sparse alpha > dense but < 0.055. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: sparse write does not exceed dense alpha (no rescue). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_grid=%s f_sparse=%.2f flip=%.2f" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_GRID, F_SPARSE, FLIP), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] %s" % (seed, {k: {kk: round(vv, 3) for kk, vv in v.items() if 'alpha' in kk} for k, v in r["by_N"].items()}), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
