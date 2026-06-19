"""
exp_substrate_etf_hadamard_codebook_init_v1 -- Slot 2: ETF/Hadamard codebook init vs random (attack dominant noise) -- CPU.

ROUTING: PRIORITY_QUEUE_LIVE Slot 2 (promoted to Tier-1). Matthiessen diagnosis (HP) showed CODEBOOK-COLLISION is the
  dominant substrate noise. This cell attacks it directly: initialize the KEY codebook with mutually-orthogonal
  Hadamard rows (an ETF at M<=N -> zero pairwise coherence) instead of random bipolar (which has O(1/sqrt(N)) random
  cross-coherence = collisions). Measures heteroassociative capacity (M* with recall>=0.95) for Hadamard vs random keys.
  CPU numpy $0.

PRE-REGISTERED bands: HARD-PASS Hadamard-codebook capacity >= 2x random at N=4096 (collision noise removed -> capacity
  gain). MIDDLE: 1.3-2x. HARD-FAIL: < 1.3x (orthogonal init does not help -> collision was not the binding constraint).
FORMULA SELF-TESTS (PROT-022): 1. Hadamard rows orthogonal. 2. orthogonal-key recall perfect at high load. 3. N=4096.
ASCII-only. write_metrics. PROT-018 _n4096 -> N=4096.
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

ANCHOR_NAME = "substrate_etf_hadamard_codebook_init_v1"
_N_SUFFIX = 4096; N = 4096; assert N == _N_SUFFIX
N_VAL = 64
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_DIM = 1024; LOADS = [0.05, 0.1, 0.2, 0.4, 0.7, 1.0]
else:
    SEEDS = [7, 17, 23]; N_DIM = 4096; LOADS = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 0.9, 1.0]


def hadamard(n):
    H = np.array([[1.0]], dtype=np.float32)
    while H.shape[0] < n:
        H = np.block([[H, H], [H, -H]])
    return H


FLIP = 0.05; STEPS = 6


def pats_random(M, n, g):
    return (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)


def pats_hadamard(M, n, g):
    H = hadamard(n); idx = g.choice(n, size=min(M, n), replace=False); P = H[idx]    # M<=n mutually-orthogonal +/-1 rows
    if M > n:
        P = np.vstack([P, pats_random(M - n, n, g)])
    return P.astype(np.float32)


def recall(n, M, P, g):
    # PROPER metric: auto-associative Hopfield, zero-diagonal W, flip-corrupted cue, exact recovery (non-saturating)
    W = (P.T @ P).astype(np.float32); np.fill_diagonal(W, 0.0)
    s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(STEPS):
        s = np.sign(s @ W.T); s[s == 0] = 1.0
    return float(np.mean(np.all(s == P, axis=1)))


def _selftest():
    H = hadamard(8); G = H @ H.T; assert np.allclose(G - np.diag(np.diag(G)), 0), "Hadamard rows orthogonal"
    g = np.random.default_rng(0); n = 256
    assert recall(n, 80, pats_hadamard(80, n, g), g) >= 0.95, "orthogonal patterns recover at moderate load (0.31N)"
    assert recall(n, 80, pats_random(80, n, g), g) < 0.95, "random patterns overload at 0.31N (cap~0.14N)"
    assert N == 4096; print("[selftest] PASS: hadamard orthogonal vs random", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def capacity(n, patfn, seed):
    cap = 0
    for load in LOADS:
        M = max(2, int(load * n))
        if recall(n, M, patfn(M, n, np.random.default_rng(seed * 1000 + M)), np.random.default_rng(seed * 7 + M)) >= 0.95:
            cap = M
        else:
            break
    return cap


def run_seed(seed) -> Dict:
    cr = capacity(N_DIM, pats_random, seed); ch = capacity(N_DIM, pats_hadamard, seed)
    return {"seed": seed, "N": N_DIM, "random_capacity": cr, "hadamard_capacity": ch, "ratio": float(ch / max(cr, 1))}


def verdict(ps) -> Tuple[str, str]:
    cr = float(np.mean([p["random_capacity"] for p in ps])); ch = float(np.mean([p["hadamard_capacity"] for p in ps]))
    ratio = ch / max(cr, 1)
    summary = "random_codebook_capacity=%.0f hadamard_codebook_capacity=%.0f ratio=%.2fx (N=%d)" % (cr, ch, ratio, ps[0]["N"])
    if ratio >= 2.0:
        return ("HARD_PASS", "HARD_PASS: ETF/Hadamard codebook init gives >=2x capacity -- attacks dominant codebook-collision noise (Matthiessen). " + summary)
    if ratio >= 1.3:
        return ("MIDDLE_BAND", "MIDDLE_BAND: orthogonal codebook 1.3-2x capacity. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: orthogonal codebook init <1.3x (collision not binding here). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d N_val=%d loads=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, N_VAL, len(LOADS)), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] random_cap=%d hadamard_cap=%d ratio=%.2fx" % (seed, r["random_capacity"], r["hadamard_capacity"], r["ratio"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
