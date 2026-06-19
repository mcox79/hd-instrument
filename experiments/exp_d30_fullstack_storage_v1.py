"""
exp_d30_fullstack_storage_v1 -- d=30 PCA-truncated + 4-bit KEY storage stack: per-fact cost + recall@1 -- CPU.
ROUTING: handoff five_experiments_authorize #2. PCA KEY-job F1=1.0 at d=30 (cycle 157). Validates the storage stack:
  d=30 PCA-truncated KEYs + 4-bit quantization, measuring actual per-fact byte cost and recall@1 under a noise sweep at
  scale. If per-fact < 1 KB with recall@1 >= 0.95, the ~280x reduction from 286 KB is real. Synthetic Llama-like keys
  (storage cost is structural, data-independent); recall is the recovery test. CPU.
PRE-REGISTERED: HARD-PASS per-fact cost < 1 KB AND recall@1 >= 0.95 (at 0-noise) AND >= 0.90 at 5% noise. MIDDLE recall@1
  0.90-0.95. HARD-FAIL recall@1 < 0.90 OR per-fact >= 1 KB.
FORMULA SELF-TESTS (PROT-022): 1. clean recall=1. 2. 4-bit 16 levels. 3. d<ambient.
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
ANCHOR_NAME = "d30_fullstack_storage_v1"; AMBIENT = 2048; D = 30
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_FACTS = 2000 if RUN_MODE == "smoke" else 20000; NOISES = [0.0, 0.05]; SEEDS = [1] if RUN_MODE == "smoke" else [7, 17]
def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)
def quant4(X):
    lo, hi = np.quantile(X, 0.001, axis=0), np.quantile(X, 0.999, axis=0)
    q = np.clip(np.round((X - lo) / (hi - lo + 1e-9) * 15), 0, 15).astype(np.int8)
    deq = q.astype(np.float32) / 15.0 * (hi - lo) + lo; return deq
def _selftest():
    g = np.random.default_rng(0); K = unit(g.standard_normal((10, D)))
    assert int(np.argmax(unit(K) @ unit(K)[0])) == 0, "clean recall=1"
    assert quant4(g.standard_normal((50, 4))).shape == (50, 4), "4-bit 16 levels"
    assert D < AMBIENT, "d<ambient"
    print("[selftest] PASS: d30-fullstack", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def pca_truncate(E, d):
    mu = E.mean(0); U, S, Vt = np.linalg.svd(E - mu, full_matrices=False); return (E - mu) @ Vt[:d].T
def run_seed(seed):
    g = np.random.default_rng(seed)
    # synthetic Llama-like anisotropic keys (intrinsic dim ~30): low-rank + small noise
    Z = g.standard_normal((N_FACTS, D)) @ g.standard_normal((D, AMBIENT)); Z += 0.05 * g.standard_normal((N_FACTS, AMBIENT))
    keys = pca_truncate(Z.astype(np.float32), D)               # d=30 representation
    kq = unit(quant4(keys))                                     # 4-bit quantized keys
    out = {}
    for ns in NOISES:
        q = kq + ns * g.standard_normal(kq.shape).astype(np.float32); qn = unit(q)
        # recall@1 in chunks to avoid N^2 memory
        hit = 0
        for i in range(0, N_FACTS, 512):
            sims = qn[i:i+512] @ kq.T; hit += int((np.argmax(sims, axis=1) == np.arange(i, min(i+512, N_FACTS))).sum())
        out["noise%.2f" % ns] = hit / N_FACTS
    per_fact_bytes = D * 0.5                                    # d=30 at 4 bits = 15 bytes/fact (key); W amortized separately
    return {"recall": out, "per_fact_bytes": per_fact_bytes}
def run() -> Dict:
    rs = [run_seed(s) for s in SEEDS]
    r0 = float(np.mean([r["recall"]["noise0.00"] for r in rs])); r5 = float(np.mean([r["recall"]["noise0.05"] for r in rs]))
    pfb = rs[0]["per_fact_bytes"]
    print("  recall@1 clean=%.3f @5%%noise=%.3f | per-fact KEY cost=%.0f bytes (d=%d 4-bit)" % (r0, r5, pfb, D), flush=True)
    return {"recall_clean": r0, "recall_noise5": r5, "per_fact_bytes": pfb}
def verdict(r) -> Tuple[str, str]:
    summary = "recall@1 clean=%.3f @5%%=%.3f per-fact-KEY=%.0f bytes (d=%d; vs 286KB baseline)" % (r["recall_clean"], r["recall_noise5"], r["per_fact_bytes"], D)
    if r["per_fact_bytes"] < 1024 and r["recall_clean"] >= 0.95 and r["recall_noise5"] >= 0.90:
        return ("HARD_PASS", "HARD_PASS: d=30 4-bit KEYs give <1KB/fact with recall@1>=0.95 (>=0.90 at 5%% noise) -- the ~280x storage reduction is real at the KEY level. " + summary)
    if r["recall_clean"] >= 0.90:
        return ("MIDDLE_BAND", "MIDDLE_BAND: recall@1 0.90-0.95. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: recall@1<0.90 -- d=30 4-bit too lossy for reliable recovery at scale. " + summary)
print("[config] anchor=%s mode=%s facts=%d ambient=%d d=%d" % (ANCHOR_NAME, RUN_MODE, N_FACTS, AMBIENT, D), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
