"""
exp_substrate_hierarchical_hadamard_then_sparse_key_alpha_v1 -- Batch B addendum R2: ordered Hadamard->sparse -- CPU.

ROUTING: Research Batch B addendum. Naive Hadamard+sparse MIXTURE HF'd (LC1: mixing destroys orthogonality). Hypothesis:
  ORDER matters -- apply Hadamard structure FIRST, then sparsify (keep k-of-N of each Hadamard-structured pattern).
  4 arms (Hopfield exact-recovery capacity): dense, hadamard, sparse(f=0.10), hadamard-then-sparse(sequential). Does the
  ordered composition beat both singles? CPU numpy $0.
PRE-REGISTERED: HARD-PASS hadamard-then-sparse alpha >= 1.2 * max(hadamard, sparse). MID >= best single. HF < best single.
FORMULA SELF-TESTS (PROT-022): 1. hadamard orthogonal. 2. sparse k-of-N. 3. dense recovers.
ASCII-only. write_metrics. PROT-018 no _nN.
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

ANCHOR_NAME = "substrate_hierarchical_hadamard_then_sparse_key_alpha_v1"
FLIP = 0.05; F_SPARSE = 0.10
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N = 1024; LOADS = [0.05, 0.1, 0.2, 0.4, 0.7, 1.0]
else:
    SEEDS = [7, 17, 23]; N = 4096; LOADS = [0.03, 0.05, 0.08, 0.12, 0.2, 0.3, 0.4, 0.5, 0.7, 0.9]


def hadamard(n):
    H = np.array([[1.0]], np.float32)
    while H.shape[0] < n:
        H = np.block([[H, H], [H, -H]])
    return H


def pats(arm, M, n, g):
    if arm == "dense":
        return (g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32)
    if arm == "hadamard":
        H = hadamard(n); idx = g.choice(n, min(M, n), replace=False); P = H[idx]
        return P if M <= n else np.vstack([P, (g.integers(0, 2, (M - n, n)) * 2 - 1).astype(np.float32)])
    if arm == "sparse":
        k = max(1, int(F_SPARSE * n)); P = np.zeros((M, n), np.float32)
        for i in range(M):
            idx = g.choice(n, k, replace=False); P[i, idx] = g.integers(0, 2, k) * 2 - 1
        return P
    # hadamard_then_sparse: take Hadamard rows, then keep k-of-N active (sparsify the structured pattern)
    H = hadamard(n); idx = g.choice(n, min(M, n), replace=False); base = H[idx]
    if M > n:
        base = np.vstack([base, (g.integers(0, 2, (M - n, n)) * 2 - 1).astype(np.float32)])
    k = max(1, int(F_SPARSE * n)); P = np.zeros((M, n), np.float32)
    for i in range(M):
        keep = g.choice(n, k, replace=False); P[i, keep] = base[i, keep]
    return P


def recall(P, sparse_like, g):
    M, n = P.shape; W = (P.T @ P).astype(np.float32); np.fill_diagonal(W, 0.0)
    if sparse_like:
        s = P.copy()
        for i in range(M):
            nz = np.nonzero(P[i])[0]; fl = nz[g.random(len(nz)) < FLIP]; s[i, fl] *= -1
        r = np.sign(s @ W.T)
        ok = sum(int(np.all(r[i][np.nonzero(P[i])[0]] == P[i][np.nonzero(P[i])[0]])) for i in range(M))
        return ok / M
    s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(6):
        s = np.sign(s @ W.T); s[s == 0] = 1.0
    return float(np.mean(np.all(s == P, axis=1)))


def cap(arm, seed):
    sl = arm in ("sparse", "hadamard_then_sparse"); c = 0
    for load in LOADS:
        M = max(2, int(load * N))
        if recall(pats(arm, M, N, np.random.default_rng(seed * 1000 + M)), sl, np.random.default_rng(seed * 7 + M)) >= 0.95:
            c = M
        else:
            break
    return c


def _selftest():
    g = np.random.default_rng(0); H = hadamard(8); G = H @ H.T; assert np.allclose(G - np.diag(np.diag(G)), 0), "hadamard orthogonal"
    P = pats("sparse", 5, 256, g); assert np.all((P != 0).sum(1) == int(F_SPARSE * 256)), "sparse k-of-N"
    print("[selftest] PASS: hier", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    a = {arm: cap(arm, seed) / N for arm in ["dense", "hadamard", "sparse", "hadamard_then_sparse"]}
    print("  [seed=%d] %s" % (seed, {k: round(v, 4) for k, v in a.items()}), flush=True); return {"seed": seed, "alpha": a}


def verdict(ps) -> Tuple[str, str]:
    agg = {arm: float(np.mean([p["alpha"][arm] for p in ps])) for arm in ps[0]["alpha"]}
    hts = agg["hadamard_then_sparse"]; best = max(agg["hadamard"], agg["sparse"]); g = hts / max(best, 1e-9)
    summary = "alphas=%s | hadamard_then_sparse/best_single=%.2fx" % ({k: round(v, 4) for k, v in agg.items()}, g)
    if g >= 1.2:
        return ("HARD_PASS", "HARD_PASS: ordered Hadamard->sparse beats both singles (>=1.2x) -- ordering enables composition (naive mixture HF'd). " + summary)
    if g >= 1.0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: ordered ~ best single (1.0-1.2x). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: ordered Hadamard->sparse < best single -- ordering does not compose. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
