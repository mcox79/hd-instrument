"""
exp_pb_srht_vs_hadamard_codebook_v1 -- propose-back (DAMB3 SRHT, Research-requested, never built) -- CPU.

ROUTING: closes the open DAMB3 question. SRHT (Subsampled Randomized Hadamard Transform = random-sign diagonal D then
  Hadamard) randomizes Hadamard's systematic interference. Compares exact-recovery capacity of three synthetic codebooks
  at matched N: random / fixed-Hadamard / SRHT (D*Hadamard rows). Does SRHT match or beat Hadamard while avoiding its
  systematic-collision structure? CPU $0.
PRE-REGISTERED: HARD-PASS SRHT alpha_c >= 0.9 * Hadamard AND >= 2x random (keeps Hadamard's gain, randomized). MID 0.5-0.9
  of Hadamard. HARD-FAIL SRHT ~ random (loses the structure benefit).
FORMULA SELF-TESTS (PROT-022): 1. hadamard orthogonal. 2. SRHT orthogonal (D preserves it). 3. hopfield low load.
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

ANCHOR_NAME = "pb_srht_vs_hadamard_codebook_v1"
FLIP = 0.05; STEPS = 6; ARMS = ["random", "hadamard", "srht"]
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_GRID = [512, 1024]; LOADS = [0.05, 0.1, 0.2, 0.4, 0.7, 1.0]
else:
    SEEDS = [7, 17, 23]; N_GRID = [1024, 2048]; LOADS = [0.05, 0.1, 0.2, 0.35, 0.5, 0.7, 0.85, 1.0]


def hadamard(n):
    H = np.array([[1.0]], np.float32)
    while H.shape[0] < n:
        H = np.block([[H, H], [H, -H]])
    return H


def make(arm, M, n, g):
    if arm == "random":
        return (g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32)
    H = hadamard(n)
    if arm == "srht":
        D = (g.integers(0, 2, n) * 2 - 1).astype(np.float32); H = H * D[None, :]   # random sign-flip columns (orthogonality preserved)
    idx = g.choice(n, min(M, n), replace=False); P = H[idx]
    return P if M <= n else np.vstack([P, (g.integers(0, 2, (M - n, n)) * 2 - 1).astype(np.float32)])


def recall(P, seed):
    g = np.random.default_rng(seed); M, n = P.shape; s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(STEPS):
        s = np.sign((s @ P.T) @ P - M * s); s[s == 0] = 1.0
    return float(np.mean(np.all(s == P, axis=1)))


def cap(arm, n, seed):
    g = np.random.default_rng(seed); c = 0.0
    for load in LOADS:
        M = max(2, int(load * n))
        if recall(make(arm, M, n, g), seed * 7 + M) >= 0.95:
            c = load
        else:
            break
    return c


def _selftest():
    H = hadamard(8); G = H @ H.T; assert np.allclose(G - np.diag(np.diag(G)), 0), "hadamard orthogonal"
    g = np.random.default_rng(0); D = (g.integers(0, 2, 8) * 2 - 1).astype(np.float32); Hs = H * D[None, :]; Gs = Hs @ Hs.T
    assert np.allclose(Gs - np.diag(np.diag(Gs)), 0), "SRHT orthogonal"
    P = make("random", 4, 256, g); assert recall(P, 0) >= 0.95, "hopfield low load"
    print("[selftest] PASS: srht", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    nmax = N_GRID[-1]; a = {arm: cap(arm, nmax, seed) for arm in ARMS}
    print("  [seed=%d N=%d] %s" % (seed, nmax, {k: round(v, 3) for k, v in a.items()}), flush=True); return {"seed": seed, "alpha": a}


def verdict(ps) -> Tuple[str, str]:
    agg = {arm: float(np.mean([p["alpha"][arm] for p in ps])) for arm in ARMS}
    srht_vs_had = agg["srht"] / max(agg["hadamard"], 1e-9); srht_vs_rand = agg["srht"] / max(agg["random"], 1e-9)
    summary = "alpha_c: %s | srht/hadamard=%.2f srht/random=%.2f" % ({k: round(v, 3) for k, v in agg.items()}, srht_vs_had, srht_vs_rand)
    if srht_vs_had >= 0.9 and srht_vs_rand >= 2.0:
        return ("HARD_PASS", "HARD_PASS: SRHT keeps Hadamard's capacity gain (>=0.9x) while randomizing structure (>=2x random) -- ships as drop-in codebook. " + summary)
    if srht_vs_had >= 0.5:
        return ("MIDDLE_BAND", "MIDDLE_BAND: SRHT 0.5-0.9 of Hadamard. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: SRHT ~ random (loses structure benefit). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_grid=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_GRID), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
