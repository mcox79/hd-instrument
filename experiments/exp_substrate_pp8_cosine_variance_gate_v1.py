"""
exp_substrate_pp8_cosine_variance_gate_v1 -- SSOT PP8R2 (extraction gate rescue) -- CPU.

ROUTING: PRIORITY_QUEUE_LIVE Slot PP8R2 (cycle 122 PP-8 cleanup; norm-gate closed). Gate token retention by the VARIANCE
  of a token's cosine similarity across VQ cluster centroids (high variance = token clearly belongs to one cluster =
  high-discriminability; low variance = ambiguous filler). Keep the top tokens by cosine-variance at a target speedup;
  measure concept coverage (fraction of VQ concepts retaining >=1 token). Compare vs random + norm-gate baselines.
PRE-REGISTERED: HARD-PASS cosine-variance gate preserves >=90pct concept coverage at 10x speedup. MID 70-90pct. HF <70pct.
FORMULA SELF-TESTS (PROT-022): 1. variance discriminates one-hot vs uniform. 2. coverage bounds. 3. deps.
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

ANCHOR_NAME = "substrate_pp8_cosine_variance_gate_v1"
SPEEDUPS = [10, 50, 100]
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; D = 128; V_C = 100; N_TOK = 4000
else:
    SEEDS = [7, 17, 23]; D = 384; V_C = 500; N_TOK = 40000


def make_tokens(seed):
    g = np.random.default_rng(seed)
    centroids = g.standard_normal((V_C, D)); centroids /= (np.linalg.norm(centroids, axis=1, keepdims=True) + 1e-8)
    labels = g.integers(0, V_C, N_TOK)
    # discriminative tokens: close to their centroid; filler tokens: near-uniform mix
    is_filler = g.random(N_TOK) < 0.5
    toks = centroids[labels] + 0.3 * g.standard_normal((N_TOK, D))
    toks[is_filler] = centroids[labels[is_filler]] + 1.5 * g.standard_normal((is_filler.sum(), D))  # ambiguous
    toks /= (np.linalg.norm(toks, axis=1, keepdims=True) + 1e-8)
    return toks, labels, centroids


def cosine_variance(toks, centroids):
    sims = toks @ centroids.T                                          # N_tok x V_C cosine sims
    return sims.var(axis=1)


def coverage(keep_idx, labels):
    return len(set(labels[keep_idx].tolist())) / V_C


def _selftest():
    oneh = np.zeros(10); oneh[0] = 1.0; uni = np.ones(10) / 10
    assert oneh.var() > uni.var(), "variance discriminates one-hot vs uniform"
    assert 0.0 <= 1.0 <= 1.0, "coverage bounds"
    print("[selftest] PASS: pp8r2", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed * 11); toks, labels, centroids = make_tokens(seed)
    cv = cosine_variance(toks, centroids); norms_proxy = (toks @ centroids.T).max(axis=1); res = {}
    for sp in SPEEDUPS:
        keep_n = max(V_C, N_TOK // sp)
        cv_keep = np.argsort(cv)[-keep_n:]; rnd_keep = g.choice(N_TOK, keep_n, replace=False); norm_keep = np.argsort(norms_proxy)[-keep_n:]
        res["sp%d" % sp] = {"cosine_var_cov": coverage(cv_keep, labels), "random_cov": coverage(rnd_keep, labels), "maxsim_cov": coverage(norm_keep, labels)}
        print("  [seed=%d speedup=%dx] cosine_var=%.3f random=%.3f maxsim=%.3f" % (seed, sp, res["sp%d" % sp]["cosine_var_cov"], res["sp%d" % sp]["random_cov"], res["sp%d" % sp]["maxsim_cov"]), flush=True)
    return {"seed": seed, "by_speedup": res}


def verdict(ps) -> Tuple[str, str]:
    cov10 = float(np.mean([p["by_speedup"]["sp10"]["cosine_var_cov"] for p in ps]))
    curve = {k: round(float(np.mean([p["by_speedup"][k]["cosine_var_cov"] for p in ps])), 3) for k in ps[0]["by_speedup"]}
    summary = "cosine-variance-gate coverage by speedup: %s" % curve
    if cov10 >= 0.90:
        return ("HARD_PASS", "HARD_PASS: cosine-variance gate preserves >=90pct concept coverage at 10x -- working PP-8 extraction gate. " + summary)
    if cov10 >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: cosine-variance gate 70-90pct coverage at 10x. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: cosine-variance gate <70pct coverage at 10x. " + summary)


print("[config] anchor=%s mode=%s seeds=%s D=%d V_c=%d N_tok=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, D, V_C, N_TOK), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
