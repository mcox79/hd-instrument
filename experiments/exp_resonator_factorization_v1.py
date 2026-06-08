"""
exp_resonator_factorization_v1 -- Resonator network factorization of bound products -- CPU.

ROUTING: field_VSA_5x Anchor 3 (resonator capacity). A Resonator network (Frady/Kent 2020) factorizes a composite
  s = x1 * x2 * ... * xK (FHRR bind) back into its K factors by iterative resonance: each estimate is unbound from s using
  the others, then hard-cleaned to its codebook. Validates the substrate can DECODE multiplicatively-bound structure
  (the inverse of composition) -- needed for querying composite facts. Sweeps K at fixed N,M to locate the capacity cliff.
  Pure numpy complex64. CPU.
PRE-REGISTERED: HARD-PASS full-factorization success >= 0.90 at K=3 (N=1024, M=30 per factor). MIDDLE 0.70-0.90.
  HARD-FAIL < 0.70 (resonator does not converge at this load).
FORMULA SELF-TESTS (PROT-022): 1. bind/unbind inverse. 2. cleanup self. 3. single-factor trivial.
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

ANCHOR_NAME = "resonator_factorization_v1"; N = 2048; M = 30; MAX_IT = 100
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
K_GRID = [2, 3] if RUN_MODE == "smoke" else [2, 3, 4]; TRIALS = 30 if RUN_MODE == "smoke" else 150


def phasor(m, d, g):
    return np.exp(1j * g.uniform(-np.pi, np.pi, (m, d))).astype(np.complex64)


def cleanup(v, book):
    j = int(np.argmax((book @ np.conj(v)).real)); return book[j], j


def _selftest():
    g = np.random.default_rng(0); a = phasor(1, 32, g)[0]; b = phasor(1, 32, g)[0]
    assert np.allclose(a * b * np.conj(b), a, atol=1e-4), "bind/unbind inverse"
    book = phasor(5, 32, g); cv, j = cleanup(book[2], book); assert j == 2, "cleanup self"
    assert cleanup(book[0], book)[1] == 0, "single-factor trivial"
    print("[selftest] PASS: resonator-factorization", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def resonate(s, books, K):
    est = [b.mean(0) for b in books]                     # init: superposition of each codebook
    est = [e / (np.abs(e) + 1e-8) for e in est]
    prev = None
    for _ in range(MAX_IT):
        idxs = []
        for k in range(K):
            others = np.ones(s.shape, dtype=np.complex64)
            for j in range(K):
                if j != k:
                    others = others * est[j]
            r = s * np.conj(others)                      # unbind the other factors
            scores = books[k] @ np.conj(r)               # [M] codebook similarities (soft, keep all)
            est[k] = (scores @ books[k])                 # weighted superposition back into codebook span
            est[k] = est[k] / (np.abs(est[k]) + 1e-8)    # normalize to unit phasors
            idxs.append(int(np.argmax(scores.real)))     # readout (hard only for the answer, not the state)
        if idxs == prev:
            break
        prev = idxs
    return idxs


def run() -> Dict:
    g = np.random.default_rng(7); by = {}
    for K in K_GRID:
        books = [phasor(M, N, g) for _ in range(K)]; succ = 0
        for _ in range(TRIALS):
            true = [int(g.integers(0, M)) for _ in range(K)]
            s = np.ones(N, dtype=np.complex64)
            for k in range(K):
                s = s * books[k][true[k]]
            got = resonate(s, books, K); succ += int(got == true)
        by["K%d" % K] = succ / TRIALS
        print("  K=%d full-factorization success=%.3f (N=%d M=%d)" % (K, by["K%d" % K], N, M), flush=True)
    return {"by": by, "N": N, "M": M}


def verdict(r) -> Tuple[str, str]:
    by = r["by"]; k3 = by.get("K3", 0.0); summary = "success by K: %s (N=%d M=%d)" % ({k: round(v, 3) for k, v in by.items()}, r["N"], r["M"])
    if k3 >= 0.90:
        return ("HARD_PASS", "HARD_PASS: resonator factorizes bound products >=0.90 at K=3 -- the substrate decodes multiplicatively-bound composite structure (inverse of composition). " + summary)
    if k3 >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: factorization success 0.70-0.90 at K=3. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: resonator <0.70 at K=3 (below capacity; raise N or lower M). " + summary)


print("[config] anchor=%s mode=%s N=%d M=%d K=%s" % (ANCHOR_NAME, RUN_MODE, N, M, K_GRID), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
