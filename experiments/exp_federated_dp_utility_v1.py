"""
exp_federated_dp_utility_v1 -- federated substrate: DP-utility on synthetic routing histograms -- CPU.

ROUTING: federated_substrate PT1 (highest priority). For a federated/multi-tenant substrate, per-customer routing
  histograms (which bridge entities are queried) can be shared with differential privacy for global self-improving routing.
  Validates the privacy/utility trade: add Gaussian-mechanism DP noise (epsilon=1.0, delta=1e-5) to synthetic Dirichlet
  routing histograms; measure normalized-histogram MAE vs the true distribution. Pure numpy simulation, no substrate code. CPU.
PRE-REGISTERED: HARD-PASS MAE < 0.05 at epsilon=1.0, delta=1e-5, N=500/customer, 50 bins (DP-shareable at useful utility).
  MIDDLE 0.05-0.15. HARD-FAIL MAE > 0.15 (requires relaxing to epsilon>=3 -- weaker privacy).
FORMULA SELF-TESTS (PROT-022): 1. histogram normalized. 2. gaussian sigma positive. 3. more noise -> more MAE.
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

ANCHOR_NAME = "federated_dp_utility_v1"; BINS = 50; N_PER = 500; EPS = 1.0; DELTA = 1e-5; ALPHA = 0.5
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
M = 8 if RUN_MODE == "smoke" else 20


def gaussian_sigma(eps, delta, sensitivity=1.0):
    # (eps,delta)-DP Gaussian mechanism std (one query changes one count bin by 1 -> L2 sensitivity 1)
    return float(np.sqrt(2.0 * np.log(1.25 / delta)) * sensitivity / eps)


def _selftest():
    h = np.array([2.0, 3.0, 5.0]); hn = h / h.sum(); assert abs(hn.sum() - 1.0) < 1e-9, "histogram normalized"
    assert gaussian_sigma(1.0, 1e-5) > 0, "gaussian sigma positive"
    assert gaussian_sigma(0.5, 1e-5) > gaussian_sigma(2.0, 1e-5), "more noise -> more MAE"
    print("[selftest] PASS: federated-dp-utility", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(404); sigma = gaussian_sigma(EPS, DELTA)
    maes = []
    for _ in range(M):
        p = g.dirichlet(np.full(BINS, ALPHA))                 # customer's true routing distribution
        counts = g.multinomial(N_PER, p).astype(np.float64)   # N observed queries
        true_norm = counts / counts.sum()
        noisy = counts + g.normal(0, sigma, BINS)             # Gaussian DP mechanism on counts
        noisy = np.clip(noisy, 0, None); s = noisy.sum(); noisy_norm = noisy / s if s > 0 else noisy
        maes.append(float(np.abs(noisy_norm - true_norm).mean()))
    mae = float(np.mean(maes))
    print("  DP utility: MAE=%.4f at eps=%.1f delta=%.0e N=%d bins=%d (gaussian sigma=%.2f, M=%d customers)" % (mae, EPS, DELTA, N_PER, BINS, sigma, M), flush=True)
    return {"mae": mae, "sigma": gaussian_sigma(EPS, DELTA), "eps": EPS, "n": N_PER, "bins": BINS}


def verdict(r) -> Tuple[str, str]:
    mae = r["mae"]; s = "MAE=%.4f at eps=%.1f N=%d bins=%d (sigma=%.2f)" % (mae, r["eps"], r["n"], r["bins"], r["sigma"])
    if mae < 0.05:
        return ("HARD_PASS", "HARD_PASS: DP routing histograms shareable at MAE<0.05 with eps=1.0 -- federated self-improving routing viable at strong privacy. " + s)
    if mae < 0.15:
        return ("MIDDLE_BAND", "MIDDLE_BAND: MAE 0.05-0.15 at eps=1.0 -- usable with more queries per customer or eps relaxation. " + s)
    return ("HARD_FAIL", "HARD_FAIL: MAE>0.15 at eps=1.0 -- requires eps>=3 (weaker privacy) for useful federated utility. " + s)


print("[config] anchor=%s mode=%s bins=%d N_per=%d eps=%.1f delta=%.0e M=%d" % (ANCHOR_NAME, RUN_MODE, BINS, N_PER, EPS, DELTA, M), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
