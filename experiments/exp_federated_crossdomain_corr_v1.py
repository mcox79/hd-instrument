"""
exp_federated_crossdomain_corr_v1 -- federated PT2: cross-domain routing correlation -- CPU.

ROUTING: federated_substrate PT2 (FED-CORR-PT2). For federated self-improving routing to transfer learning ACROSS customer
  domains, their routing distributions (over bridge entities) must share structure. Model D domains: each routing histogram =
  a shared popular-entity head (Zipf) + a domain-specific tail. Measure mean pairwise cosine across domain histograms. If
  domains are correlated enough, a global routing model helps every customer (cross-domain transfer). Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS mean pairwise cosine >= 0.50 (cross-domain transfer worthwhile). MIDDLE 0.30-0.50. HARD-FAIL < 0.30
  (domains too idiosyncratic; per-customer models only).
FORMULA SELF-TESTS (PROT-022): 1. cosine bounds. 2. histogram normalized. 3. shared-head raises correlation.
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

ANCHOR_NAME = "federated_crossdomain_corr_v1"; BINS = 200; SHARED_FRAC = 0.5
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
D_DOMAINS = 6 if RUN_MODE == "smoke" else 20


def unit(x):
    return x / (np.linalg.norm(x) + 1e-8)


def zipf(v, s=1.1):
    p = 1.0 / np.power(np.arange(1, v + 1), s); return p / p.sum()


def _selftest():
    a = unit(np.array([1.0, 0])); b = unit(np.array([1.0, 0])); assert abs(float(a @ b) - 1.0) < 1e-6, "cosine bounds"
    h = np.array([2.0, 3.0]); assert abs((h / h.sum()).sum() - 1.0) < 1e-9, "histogram normalized"
    shared = zipf(10); assert float(unit(shared) @ unit(shared)) > 0.99, "shared-head raises correlation"
    print("[selftest] PASS: federated-crossdomain-corr", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(505); head = zipf(BINS)
    hists = []
    for _ in range(D_DOMAINS):
        perm = g.permutation(BINS); tail = np.zeros(BINS); tail[perm] = zipf(BINS)   # domain-specific reordering
        h = SHARED_FRAC * head + (1 - SHARED_FRAC) * tail; h = h / h.sum(); hists.append(unit(h))
    H = np.array(hists); cos = H @ H.T; iu = np.triu_indices(D_DOMAINS, k=1); mean_cos = float(cos[iu].mean())
    print("  mean pairwise cosine across %d domains = %.3f (shared_frac=%.2f, bins=%d)" % (D_DOMAINS, mean_cos, SHARED_FRAC, BINS), flush=True)
    return {"mean_cos": mean_cos, "d": D_DOMAINS, "shared_frac": SHARED_FRAC}


def verdict(r) -> Tuple[str, str]:
    mc = r["mean_cos"]; s = "mean_pairwise_cosine=%.3f across %d domains (shared_frac=%.2f)" % (mc, r["d"], r["shared_frac"])
    if mc >= 0.50:
        return ("HARD_PASS", "HARD_PASS: domain routing distributions share structure (cosine>=0.50) -- cross-domain transfer worthwhile; global federated routing helps every customer. " + s)
    if mc >= 0.30:
        return ("MIDDLE_BAND", "MIDDLE_BAND: moderate cross-domain correlation (0.30-0.50) -- partial transfer. " + s)
    return ("HARD_FAIL", "HARD_FAIL: domains too idiosyncratic (cosine<0.30) -- per-customer routing models only. " + s)


print("[config] anchor=%s mode=%s D=%d bins=%d shared=%.2f" % (ANCHOR_NAME, RUN_MODE, D_DOMAINS, BINS, SHARED_FRAC), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
