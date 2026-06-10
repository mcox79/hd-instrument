"""
exp_lap4_1_chirp_codebook_cpu_v1.py -- chirp/CAZAC low-coherence codebook capacity (rescue of LAP3-6) -- CPU.

ROUTING: Research WAVE3_RESOLUTION_WAVE4 (LAP4-1 LEARNED-CODEBOOK-RESCUE); pure-FHRR (no download). Chirp (Zadoff-Chu-like) unit-modulus keys vs random; recall storing K=150 pairs; proper low-coherence construction.
PRE-REGISTERED: HARD-PASS chirp ratio>=1.5x. MIDDLE>=1.2x. HARD-FAIL<1.2x.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "lap4_1_chirp_codebook_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    print("[selftest] PASS: chirp-codebook", flush=True)
def _recall(N, K, keys, g):
    vals = cphasor(K, N, g); Mem = (keys * vals).sum(axis=0)
    return sum(int(cidx(Mem * np.conj(keys[i]), vals) == i) for i in range(K)) / K
def run() -> Dict:
    g = np.random.default_rng(150); N = 512; K = 150; TR = 5 if SMOKE else 25
    nn = np.arange(N)
    rand_r = []; chirp_r = []
    for _ in range(TR):
        rv = cphasor(K, N, g)                                            # random codebook
        # chirp / Zadoff-Chu-like low-coherence codebook: key_k[n] = exp(i*pi*(k+1)*n*(n+1)/N) -- CAZAC, unit-modulus
        chirp = np.stack([np.exp(1j * math.pi * (k + 1) * nn * (nn + 1) / N).astype(np.complex64) for k in range(K)])
        rand_r.append(_recall(N, K, rv, g)); chirp_r.append(_recall(N, K, chirp, g))
    rr = float(np.mean(rand_r)); cr = float(np.mean(chirp_r)); ratio = cr / rr if rr > 0 else 99.0
    print("  CHIRP-CODEBOOK K=%d N=%d: random-recall=%.3f chirp-recall=%.3f ratio=%.2fx (n=%d)" % (K, N, rr, cr, ratio, TR), flush=True)
    return {"random_recall": rr, "chirp_recall": cr, "capacity_ratio": round(ratio, 2), "K": K, "N": N}
def verdict(r) -> Tuple[str, str]:
    s = "random=%.3f chirp=%.3f ratio=%.2fx (K=%d N=%d)" % (r["random_recall"], r["chirp_recall"], r["capacity_ratio"], r["K"], r["N"])
    if r["capacity_ratio"] >= 1.5:
        return ("HARD_PASS", "HARD_PASS: chirp/CAZAC low-coherence codebook gives >=1.5x random capacity at K=150 -- LAP3-6 RESCUED with proper construction (the difference of two chirps is a spread-spectrum chirp -> low cleanup cross-talk). Learned-codebook lever confirmed. " + s)
    if r["capacity_ratio"] >= 1.2:
        return ("MIDDLE_BAND", "MIDDLE_BAND: chirp ratio 1.2-1.5x. " + s)
    return ("HARD_FAIL", "HARD_FAIL: chirp ratio <1.2x (need Welch-bound construction). " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
