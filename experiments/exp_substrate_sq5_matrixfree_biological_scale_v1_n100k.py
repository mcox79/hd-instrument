"""
substrate_sq5_matrixfree_biological_scale_v1_n100k -- biological-scale sparse capacity, MATRIX-FREE -- remote CPU.

ROUTING: SQ5 (P_drill=0.78). Biological-scale N=100k: a dense W is 100k^2*4 = 40GB (INFEASIBLE). MATRIX-FREE:
  never form W; store sparse patterns as active-index lists; retrieve via an inverted index (dim -> patterns).
  Tests whether sparse coding extends capacity FAR past the dense limit (alpha_c*N=13800) at biological N.
  CPU numpy, $0. remote_cpu_queue.

CAPABILITY QUESTION: at N=100k, f=0.01 (k=1000 active), how many sparse patterns M can be stored with noisy-query
  TOP-1 retrieval >= 0.9 (matrix-free)? Dense limit = alpha_c*N = 13800; sparse should hold far more.

MODEL: M sparse patterns (k active each, random). Inverted index inv[dim] = list of patterns active there. Query
  = a stored pattern with 20% of active bits dropped. score_p = |query_active intersect p_active| via inverted
  index. top-1 = argmax_p score_p; correct iff == the query's own pattern. M_crit = max M with top-1 acc >= 0.9.

CELLS (3 seeds): top-1 retrieval at M in grid; M_crit; ratio vs dense limit (13800).
PRE-REGISTERED bands: HARD-PASS M_crit >= 5x dense_limit (>=69000; sparse extends biological-scale). MIDDLE 2-5x. HARD-FAIL <2x.

FORMULA SELF-TESTS (PROT-022): 1. inverted-index score == direct intersection. 2. clean-query self-retrieval top-1. 3. N=100000.
ASCII-only. write_metrics. PROT-018 _n100k (non-standard suffix; N=100000 declared).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_sq5_matrixfree_biological_scale_v1_n100k"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
F_SPARSE = 0.01
DROP = 0.20
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N = 10000; M_GRID = [2000, 6000, 15000]
else:
    SEEDS = [7, 17, 23]; N = 100000; M_GRID = [10000, 30000, 70000, 140000]


def make_sparse(M, n, k, g):
    pats = [np.sort(g.choice(n, size=k, replace=False)) for _ in range(M)]
    inv = defaultdict(list)
    for p, idx in enumerate(pats):
        for d in idx:
            inv[int(d)].append(p)
    return pats, inv


def top1_acc(M, n, k, g, n_test=100):
    pats, inv = make_sparse(M, n, k, g)
    test = g.choice(M, size=min(n_test, M), replace=False)
    hits = 0
    for true_p in test:
        act = pats[true_p]
        keep = act[g.random(len(act)) >= DROP]            # noisy query: drop 20% active
        score = np.zeros(M, dtype=np.int32)
        for d in keep:
            for q in inv[int(d)]:
                score[q] += 1
        hits += (int(np.argmax(score)) == true_p)
    return hits / len(test)


def mcrit(n, k, g):
    mc = 0
    for M in M_GRID:
        if top1_acc(M, n, k, np.random.default_rng(g.integers(1 << 30))) >= 0.9:
            mc = M
        else:
            break
    return mc


def _selftest():
    g = np.random.default_rng(0); n = 1000; k = 10
    pats, inv = make_sparse(5, n, k, g)
    # inverted-index score == direct intersection
    q = pats[2]; score = np.zeros(5, dtype=np.int32)
    for d in q:
        for p in inv[int(d)]:
            score[p] += 1
    direct = np.array([len(np.intersect1d(q, pats[j])) for j in range(5)])
    assert np.array_equal(score, direct), "inverted-index != direct intersection"
    assert int(np.argmax(score)) == 2, "clean self-retrieval top-1"
    assert N in (10000, 100000)
    print("[selftest] PASS: inverted_index==direct clean_top1", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    k = max(1, int(round(F_SPARSE * N))); g = np.random.default_rng(seed)
    mc = mcrit(N, k, g); dense_limit = ALPHA_C * N
    return {"seed": seed, "N": N, "k_active": k, "M_crit": mc, "dense_limit": float(dense_limit),
            "ratio_vs_dense": float(mc / max(dense_limit, 1))}


def verdict(ps) -> Tuple[str, str]:
    mc = float(np.median([p["M_crit"] for p in ps])); dl = float(ps[0]["dense_limit"]); r = mc / max(dl, 1)
    ceil_note = "" if mc < M_GRID[-1] else " (hit grid ceiling; M_crit is LOWER BOUND)"
    summary = "M_crit=%.0f dense_limit(alpha_c*N)=%.0f ratio=%.1fx%s (matrix-free, N=%d)" % (mc, dl, r, ceil_note, ps[0]["N"])
    if r >= 5.0:
        return ("HARD_PASS", "HARD_PASS: sparse coding extends capacity >=5x dense at biological N. " + summary)
    if r >= 2.0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: sparse 2-5x dense capacity. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: sparse <2x dense. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d f=%.3f" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, F_SPARSE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] M_crit=%d dense_limit=%.0f ratio=%.1fx" % (seed, r["M_crit"], r["dense_limit"], r["ratio_vs_dense"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
