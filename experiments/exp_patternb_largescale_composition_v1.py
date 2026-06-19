"""
exp_patternb_largescale_composition_v1 -- Pattern B role-filler composition at large vocabulary -- CPU.

ROUTING: scale-gap / pattern_b extension. Validates that Pattern B compositional recall (bundle K role-filler pairs, recover
  each filler via unbind+cleanup) holds at a LARGE filler vocabulary (V up to 100K) -- the production knowledge-base regime.
  FHRR phasors; cleanup chunked over the V-codebook. Sweeps K (pairs per bundle) at fixed V to find the composition capacity
  at scale. Pure numpy complex64. CPU.
PRE-REGISTERED: HARD-PASS recall@1 >= 0.95 at K=4 with V=100K (composition holds at production vocab). MIDDLE 0.85-0.95.
  HARD-FAIL < 0.85 (crosstalk at scale; needs higher D).
FORMULA SELF-TESTS (PROT-022): 1. bind/unbind inverse. 2. cleanup self. 3. chunked cleanup == full.
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

ANCHOR_NAME = "patternb_largescale_composition_v1"; D = 512; CHUNK = 20000
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
V = 10000 if RUN_MODE == "smoke" else 100000; K_GRID = [2, 4] if RUN_MODE == "smoke" else [2, 4, 6]; TRIALS = 30 if RUN_MODE == "smoke" else 120


def phasor(m, d, g):
    return np.exp(1j * g.uniform(-np.pi, np.pi, (m, d))).astype(np.complex64)


def cleanup_idx_chunked(v, book, chunk):
    best = -1; best_sc = -1e18; vc = np.conj(v)
    for c0 in range(0, book.shape[0], chunk):
        c1 = min(c0 + chunk, book.shape[0]); sc = (book[c0:c1] @ vc).real
        j = int(np.argmax(sc))
        if sc[j] > best_sc:
            best_sc = sc[j]; best = c0 + j
    return best


def _selftest():
    g = np.random.default_rng(0); a = phasor(1, 32, g)[0]; b = phasor(1, 32, g)[0]
    assert np.allclose(a * b * np.conj(b), a, atol=1e-4), "bind/unbind inverse"
    book = phasor(6, 32, g); assert cleanup_idx_chunked(book[3], book, 4) == 3, "cleanup self"
    assert cleanup_idx_chunked(book[2], book, 2) == cleanup_idx_chunked(book[2], book, 6), "chunked cleanup == full"
    print("[selftest] PASS: patternb-largescale-composition", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(909)
    print("  building V=%d filler codebook (D=%d, ~%.2f GB)..." % (V, D, V * D * 8 / 1e9), flush=True)
    book = phasor(V, D, g)
    by = {}
    for K in K_GRID:
        hit = 0; tot = 0
        for _ in range(TRIALS):
            roles = phasor(K, D, g); fidx = g.choice(V, size=K, replace=False)
            B = np.sum([roles[i] * book[fidx[i]] for i in range(K)], axis=0)
            for i in range(K):
                rec = B * np.conj(roles[i]); hit += int(cleanup_idx_chunked(rec, book, CHUNK) == fidx[i]); tot += 1
        by["K%d" % K] = hit / tot
        print("  K=%d recall@1=%.3f (V=%d)" % (K, by["K%d" % K], V), flush=True)
    return {"by": by, "V": V, "D": D}


def verdict(r) -> Tuple[str, str]:
    by = r["by"]; k4 = by.get("K4", 0.0); summary = "recall@1 by K: %s (V=%d D=%d)" % ({k: round(v, 3) for k, v in by.items()}, r["V"], r["D"])
    if k4 >= 0.95:
        return ("HARD_PASS", "HARD_PASS: Pattern B composition recall@1>=0.95 at K=4 with V=%d -- composition holds at production vocab scale. " % r["V"] + summary)
    if k4 >= 0.85:
        return ("MIDDLE_BAND", "MIDDLE_BAND: K=4 recall 0.85-0.95 at scale -- mild crosstalk; higher D closes it. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: K=4 recall <0.85 at V=%d -- composition crosstalk at scale (raise D). " % r["V"] + summary)


print("[config] anchor=%s mode=%s V=%d D=%d K_grid=%s" % (ANCHOR_NAME, RUN_MODE, V, D, K_GRID), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
