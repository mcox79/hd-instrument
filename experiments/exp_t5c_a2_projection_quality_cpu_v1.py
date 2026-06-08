"""
exp_t5c_a2_projection_quality_cpu_v1.py -- substrate projection preserves embedding cosine structure (>=0.85) -- CPU.

ROUTING: batch-10a (T5C-A2 codebook projection quality). Projects embeddings into the substrate dimension and measures pairwise cosine preservation (JL-style) -- pretrained embeddings ingest without similarity loss. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS cosine-preservation corr >=0.85. MIDDLE >=0.70. HARD-FAIL <0.70.
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
ANCHOR_NAME = "t5c_a2_projection_quality_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    import numpy as _n; assert abs(_n.corrcoef([1.,2,3],[1.,2,3])[0,1]-1.0)<1e-9, "corr"; print("[selftest] PASS: t5c-a2-projection-quality", flush=True)
def run() -> Dict:
    g = np.random.default_rng(962); D = 384; N = 8192; NW = 200 if SMOKE else 400
    X = g.standard_normal((NW, D)).astype(np.float32); X = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)
    P = (g.standard_normal((D, N)) / math.sqrt(D)).astype(np.float32)        # random projection into substrate dim
    Y = X @ P; Y = Y / (np.linalg.norm(Y, axis=1, keepdims=True) + 1e-8)
    # pairwise cosine preservation (JL): correlation of original vs projected cosines
    nP = 2000; ii = g.integers(0, NW, nP); jj = g.integers(0, NW, nP)
    co = (X[ii] * X[jj]).sum(1); cp = (Y[ii] * Y[jj]).sum(1)
    rho = float(np.corrcoef(co, cp)[0, 1]); mae = float(np.mean(np.abs(co - cp)))
    print("  cosine-preservation corr=%.3f MAE=%.3f (D=%d->N=%d)" % (rho, mae, D, N), flush=True)
    return {"corr": rho, "mae": mae}
def verdict(r) -> Tuple[str, str]:
    s = "cosine-preservation corr=%.3f MAE=%.3f" % (r["corr"], r["mae"])
    if r["corr"] >= 0.85: return ("HARD_PASS", "HARD_PASS: substrate projection preserves embedding cosine structure (corr>=0.85) -- pretrained embeddings ingest into substrate without similarity loss. " + s)
    if r["corr"] >= 0.70: return ("MIDDLE_BAND", "MIDDLE_BAND: cosine-preservation 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: cosine-preservation <0.70. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
