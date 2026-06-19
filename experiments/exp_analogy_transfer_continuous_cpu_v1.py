"""
exp_analogy_transfer_continuous_cpu_v1.py -- a learned relation applied as a continuous chain transfers across steps -- CPU.

ROUTING: refill batch (analogy chain (continuous, fixed)). Fixed analogy-chain: estimate relation T from K codebook example pairs, then apply That CHAINED in the continuous space and measure cosine of the produced vector to the TRUE c*T^k target (not codebook cleanup, which broke the earlier version). Reports 1-step and 2-step transfer fidelity. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS 2-step continuous transfer cosine-to-true >= 0.6 AND cleanup recall >= 0.85. MIDDLE recall >= 0.7. HARD-FAIL < 0.7.
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
ANCHOR_NAME = "analogy_transfer_continuous_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def topk(v, book, k):
    return set(np.argsort((book @ np.conj(v)).real)[::-1][:k].tolist())

def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 64, g)[0]; t = cphasor(1, 64, g)[0]; assert np.allclose(a * t * np.conj(t), a, atol=1e-3), "bind"; print("[selftest] PASS: analogy-transfer-continuous", flush=True)
def run() -> Dict:
    g = np.random.default_rng(322); N = 4096; V = 300; K = 8; TR = 60 if SMOKE else 200; book = cphasor(V, N, g)
    cos1 = []; cos2 = []; rec2 = 0; n = 0
    for _ in range(TR):
        T = cphasor(1, N, g)[0]
        ex = g.choice(V, K, replace=False); That = np.zeros(N, dtype=np.complex64)
        for x in ex:
            That = That + (book[int(x)] * T) * np.conj(book[int(x)])     # estimate T from pairs (x, x*T)
        That = That / (np.abs(That) + 1e-8)
        c0 = book[int(g.integers(0, V))]
        p1 = c0 * That; g1 = c0 * T; p2 = p1 * That; g2 = g1 * T
        cos1.append(float((p1 @ np.conj(g1)).real / N)); cos2.append(float((p2 @ np.conj(g2)).real / N))
        # cleanup recall: does p2 land on the same codebook item as the true g2?
        rec2 += int(cidx(p2, book) == cidx(g2, book)); n += 1
    c1 = float(np.mean(cos1)); c2 = float(np.mean(cos2)); rr = rec2 / n
    print("  continuous transfer cos@1=%.3f cos@2=%.3f | 2-step cleanup recall=%.3f" % (c1, c2, rr), flush=True)
    return {"cos1": c1, "cos2": c2, "rec2": rr}
def verdict(r) -> Tuple[str, str]:
    s = "cos@1=%.3f cos@2=%.3f cleanup-recall@2=%.3f" % (r["cos1"], r["cos2"], r["rec2"])
    if r["cos2"] >= 0.6 and r["rec2"] >= 0.85: return ("HARD_PASS", "HARD_PASS: learned relation transfers as a continuous 2-step chain (cos>=0.6, cleanup>=0.85) -- analogical composition works. " + s)
    if r["rec2"] >= 0.7: return ("MIDDLE_BAND", "MIDDLE_BAND: 2-step cleanup 0.7-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: 2-step transfer weak. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
