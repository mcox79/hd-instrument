"""
exp_permutation_seq_length_cpu_v1.py -- permutation-power sequence recovery vs length L (CPU fine sweep) -- CPU.

ROUTING: CPU substrate-physics characterization (sequence length sweep). Encode ordered sequences of length L in {5,10,15,20} via permutation powers (S = sum P^k(item_k)); recover each position via P^-k + cleanup. Finds the sequence-length capacity at N=2048. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS position recovery >= 0.90 at L=15. MIDDLE >= 0.80. HARD-FAIL < 0.80.
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
ANCHOR_NAME = "permutation_seq_length_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    p = np.array([2, 0, 1]); inv = np.argsort(p); assert (p[inv] == np.arange(3)).all(), "inverse perm"; print("[selftest] PASS: permutation-seq-length-cpu", flush=True)
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def run() -> Dict:
    g = np.random.default_rng(15); N = 2048; V = 200; perm = g.permutation(N); inv = np.argsort(perm); book = cphasor(V, N, g)
    TR = 20 if SMOKE else 60; Ls = [5, 10] if SMOKE else [5, 10, 15, 20]; by = {}
    def permute(v, k):
        out = v; idx = perm if k >= 0 else inv
        for _ in range(abs(k)):
            out = out[idx]
        return out
    for L in Ls:
        hit = 0; tot = 0
        for _ in range(TR):
            seq = g.choice(V, L, replace=False); S = np.zeros(N, dtype=np.complex64)
            for k in range(L):
                S = S + permute(book[seq[k]], k)
            for k in range(L):
                rec = permute(S, -k); pred = int(np.argmax((book @ rec.conj()).real)); hit += int(pred == int(seq[k])); tot += 1
        by["L%d" % L] = hit / tot; print("  L=%d position-recovery=%.3f" % (L, by["L%d" % L]), flush=True)
    return {"by": by}
def verdict(r) -> Tuple[str, str]:
    l15 = r["by"].get("L15", r["by"].get("L10", 0.0)); s = "recovery by L: %s" % {k: round(v, 3) for k, v in r["by"].items()}
    if l15 >= 0.90: return ("HARD_PASS", "HARD_PASS: ordered-sequence recovery >=0.90 at L=15 -- long timelines representable at N=2048. " + s)
    if l15 >= 0.80: return ("MIDDLE_BAND", "MIDDLE_BAND: L=15 recovery 0.80-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: L=15 recovery <0.80. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
