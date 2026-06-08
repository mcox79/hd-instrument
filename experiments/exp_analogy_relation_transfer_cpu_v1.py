"""
exp_analogy_relation_transfer_cpu_v1.py -- estimate a relation from K example pairs and apply it to a new input (analogy) -- CPU.

ROUTING: CPU substrate capability characterization (few-shot relation learning). A fixed relation T binds a->b (b = a*T + noise). Estimate T_hat from K noisy example pairs (averaging), then apply to a new c to predict d = c*T. Measures fidelity (cosine to true) vs number of examples -- few-shot relational generalization. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS cosine(d_hat, d_true) >= 0.90 at K=5 examples. MIDDLE >= 0.80. HARD-FAIL < 0.80.
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
ANCHOR_NAME = "analogy_relation_transfer_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)

def _selftest():
    a = cphasor(1, 16, np.random.default_rng(0))[0]; assert abs(abs(np.vdot(a, a)) - 16) < 1e-3, "phasor norm"; print("[selftest] PASS: analogy-relation-transfer-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(41); N = 2048; TR = 60 if SMOKE else 200; NOISE = 1.0; by = {}
    for K in [1, 3, 5, 10]:
        coss = []
        for _ in range(TR):
            T = cphasor(1, N, g)[0]; a = cphasor(K, N, g)
            noise = (g.standard_normal((K, N)) + 1j * g.standard_normal((K, N))).astype(np.complex64) * (NOISE / math.sqrt(2))
            b = a * T + noise; T_hat = (b * a.conj()).mean(0)
            c = cphasor(1, N, g)[0]; d_hat = c * T_hat; d_true = c * T
            coss.append(abs(np.vdot(d_hat, d_true)) / (np.linalg.norm(d_hat) * np.linalg.norm(d_true) + 1e-9))
        by["K%d" % K] = float(np.mean(coss)); print("  K=%d cosine(d_hat,d_true)=%.3f" % (K, by["K%d" % K]), flush=True)
    return {"by": by}
def verdict(r) -> Tuple[str, str]:
    k5 = r["by"].get("K5", 0.0); s = "cosine by #examples: %s" % {k: round(v, 3) for k, v in r["by"].items()}
    if k5 >= 0.90: return ("HARD_PASS", "HARD_PASS: a relation learned from 5 example pairs transfers to a new input at cosine>=0.90 -- few-shot relational generalization. " + s)
    if k5 >= 0.80: return ("MIDDLE_BAND", "MIDDLE_BAND: K=5 transfer cosine 0.80-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: K=5 transfer cosine <0.80. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
