"""
substrate_sq3_structured_image_retrieval_v1_n2048 -- structured (image-statistics) pattern retrieval -- remote CPU.

ROUTING: SQ3 (P_drill=0.80; real-image retrieval). PROXY without CIFAR download: generate CORRELATED, low-frequency
  image-statistics patterns (smoothed random fields, like natural-image patches) vs random bipolar, and test
  substrate auto-associative retrieval. Real CIFAR (urllib loader) is the follow-up; this isolates whether the
  substrate handles NON-RANDOM correlated inputs (where Hopfield capacity typically drops). CPU numpy, $0.

CAPABILITY QUESTION: can the substrate store + retrieve (>=90% at 20% noise) CORRELATED image-like patterns, and
  how does M_crit compare to random patterns (correlated patterns interfere more -> lower capacity expected)?

MODEL: N-dim patterns reshaped to a sqrt(N) x sqrt(N) grid; low-frequency correlated field = smoothed Gaussian
  noise (local averaging) -> sign -> bipolar (natural-image-statistics proxy). Auto-assoc Hopfield; M_crit sweep.

CELLS (3 seeds): M_crit for random vs structured(image-like); structured/random capacity ratio.
PRE-REGISTERED bands: HARD-PASS structured M_crit >= 0.5 * random M_crit AND structured M_crit >= 0.05*N
  (substrate retrieves correlated inputs usefully). MIDDLE: structured >= 0.25*random. HARD-FAIL: structured < 0.25*random.

FORMULA SELF-TESTS (PROT-022): 1. random low-load recall. 2. structured patterns ARE correlated (mean|corr|>random). 3. N=2048.
ASCII-only. write_metrics. PROT-018 _n2048 -> N=2048.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_sq3_structured_image_retrieval_v1_n2048"
_N_SUFFIX = 2048
N = 2048
assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_DIM = 512; M_GRID = [10, 30, 60, 120]
else:
    SEEDS = [7, 17, 23]; N_DIM = N; M_GRID = [50, 100, 200, 300, 400]


def random_patterns(M, n, g):
    return (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)


def structured_patterns(M, n, g):
    """low-frequency correlated fields (natural-image-statistics proxy): smoothed Gaussian -> sign."""
    s = int(round(math.sqrt(n))); n2 = s * s
    out = np.zeros((M, n), dtype=np.float32)
    for i in range(M):
        f = g.standard_normal((s, s))
        # 2 box-blur passes (local averaging) -> spatial correlation
        for _ in range(2):
            f = (f + np.roll(f, 1, 0) + np.roll(f, -1, 0) + np.roll(f, 1, 1) + np.roll(f, -1, 1)) / 5.0
        flat = np.sign(f.ravel()[:n2]); flat[flat == 0] = 1.0
        v = np.ones(n, dtype=np.float32); v[:n2] = flat
        out[i] = v
    return out


def mcrit(pat_fn, n, g):
    mc = 0
    for M in M_GRID:
        X = pat_fn(M, n, g); W = (X.T @ X).astype(np.float32); np.fill_diagonal(W, 0.0)
        flip = g.random((M, n)) < 0.20; Xc = X * np.where(flip, -1.0, 1.0)
        R = np.sign(Xc @ W.T); R[R == 0] = 1.0
        if float(np.mean((R * X).sum(axis=1) / n > 0.95)) >= 0.9:
            mc = M
        else:
            break
    return mc


def _selftest():
    g = np.random.default_rng(0)
    X = random_patterns(5, 256, g); W = (X.T @ X).astype(np.float32); np.fill_diagonal(W, 0.0)
    assert float(np.mean((np.sign(X @ W.T) * X).sum(axis=1) / 256 > 0.95)) > 0.9, "random recall"
    S = structured_patterns(20, 256, g); R = random_patterns(20, 256, g)
    cs = np.abs(np.corrcoef(S)[np.triu_indices(20, 1)]).mean(); cr = np.abs(np.corrcoef(R)[np.triu_indices(20, 1)]).mean()
    assert cs > cr, "structured not more correlated than random (%.3f vs %.3f)" % (cs, cr)
    assert N == 2048
    print("[selftest] PASS: random_recall structured_corr %.3f>%.3f" % (cs, cr), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    mr = mcrit(random_patterns, N_DIM, np.random.default_rng(seed * 7 + 1))
    ms = mcrit(structured_patterns, N_DIM, np.random.default_rng(seed * 7 + 2))
    return {"seed": seed, "N": N_DIM, "M_crit_random": mr, "M_crit_structured": ms,
            "ratio": float(ms / max(mr, 1))}


def verdict(ps) -> Tuple[str, str]:
    mr = float(np.mean([p["M_crit_random"] for p in ps])); ms = float(np.mean([p["M_crit_structured"] for p in ps]))
    ratio = ms / max(mr, 1)
    summary = "M_crit random=%.0f structured=%.0f ratio=%.2f (structured>=0.05N=%.0f?)" % (mr, ms, ratio, 0.05 * N_DIM)
    if ratio >= 0.5 and ms >= 0.05 * N_DIM:
        return ("HARD_PASS", "HARD_PASS: substrate retrieves correlated image-statistics patterns usefully. " + summary)
    if ratio >= 0.25:
        return ("MIDDLE_BAND", "MIDDLE_BAND: structured capacity reduced but usable. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: structured patterns poorly retrieved. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM), flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] random=%d structured=%d ratio=%.2f" % (seed, r["M_crit_random"], r["M_crit_structured"], r["ratio"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
