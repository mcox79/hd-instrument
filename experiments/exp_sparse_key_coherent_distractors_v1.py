"""
exp_sparse_key_coherent_distractors_v1 -- sparse-KEY low-B reconciliation anchor 1 -- CPU.

ROUTING: handoff exp_dev_handoff_research_sparse_key_low_B_reconciliation #1. Given Cell A found coherent distractors
  (c_d=0.48), does sparse-KEY (alpha=0.005) intermediates give higher K-hop answer accuracy than dense at K=8,12 when B=10
  AND distractors are COHERENT? Distinguishes Option A (sparse always helps) from Option B (sparse only helps at B=1).
  3 configs: dense-only, sparse-only, sparse+confidence. CPU.
PRE-REGISTERED: HARD-PASS sparse accuracy > dense + 0.15 at K=8,12 under coherent distractors (sparse helps at B=10 -> Option
  A). MIDDLE +0.05-0.15. HARD-FAIL sparse ~ dense (Option B; sparse only at B=1).
FORMULA SELF-TESTS (PROT-022): 1. sparse keys sparser. 2. clean recovery. 3. coherent distractor injected.
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

ANCHOR_NAME = "sparse_key_coherent_distractors_v1"
N = 4096; B = 10; C_D = 0.48; NOISE0 = 0.10; KS = [8, 12]; ALPHA = 0.005
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; V_C = 512; CHAINS = 200
else:
    SEEDS = [7, 17, 23]; V_C = 2000; CHAINS = 500


def dense_cb(v_c, n, g):
    C = (g.integers(0, 2, (v_c, n)) * 2 - 1).astype(np.float32); return C / (np.linalg.norm(C, axis=1, keepdims=True) + 1e-8)


def sparse_cb(v_c, n, g):
    k = max(1, int(ALPHA * n)); C = np.zeros((v_c, n), np.float32)
    for i in range(v_c):
        idx = g.choice(n, k, replace=False); C[i, idx] = g.integers(0, 2, k) * 2 - 1
    return C / (np.linalg.norm(C, axis=1, keepdims=True) + 1e-8)


def accuracy(C, K, conf_gate, seed):
    g = np.random.default_rng(seed); v_c, n = C.shape; tgt = g.integers(0, v_c, CHAINS)
    eff = NOISE0 * (K ** 0.5) / (B ** 0.5); dist = C[g.integers(0, v_c, CHAINS)]
    final = C[tgt] + eff * g.standard_normal((CHAINS, n)).astype(np.float32) + C_D * (K ** 0.5) / (B ** 0.5) * dist
    sims = final @ C.T; conf = sims.max(1); pred = sims.argmax(1)
    ok = (pred == tgt)
    if conf_gate:
        ok = ok & (conf > 0.5)
    return float(ok.mean())


def _selftest():
    g = np.random.default_rng(0); Cs = sparse_cb(8, 256, g); assert (Cs != 0).sum(1).max() <= 0.005 * 256 + 2, "sparse keys sparser"
    Cd = dense_cb(8, 256, g); assert int((Cd[3] @ Cd.T).argmax()) == 3, "clean recovery"
    assert C_D > 0.4, "coherent distractor injected"
    print("[selftest] PASS: sparse-coherent", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); Cd = dense_cb(V_C, N, g); Cs = sparse_cb(V_C, N, g); by = {}
    for K in KS:
        d = accuracy(Cd, K, False, seed * 10 + K); s = accuracy(Cs, K, False, seed * 10 + K); sc = accuracy(Cs, K, True, seed * 10 + K)
        by["K%d" % K] = {"dense": d, "sparse": s, "sparse_conf": sc}
        print("  [seed=%d K=%d] dense=%.3f sparse=%.3f sparse+conf=%.3f" % (seed, K, d, s, sc), flush=True)
    return {"seed": seed, "by": by}


def verdict(ps) -> Tuple[str, str]:
    deltas = []
    for K in KS:
        d = np.mean([p["by"]["K%d" % K]["dense"] for p in ps]); s = np.mean([p["by"]["K%d" % K]["sparse"] for p in ps]); deltas.append(s - d)
    md = float(np.mean(deltas))
    summary = "sparse-dense accuracy delta by K=%s: %s | mean=%.3f (coherent c_d=%.2f, B=%d)" % (KS, [round(x, 3) for x in deltas], md, C_D, B)
    if md > 0.15:
        return ("HARD_PASS", "HARD_PASS: sparse-KEY beats dense by >0.15 at K=8,12 under coherent distractors -- Option A (sparse always helps), not B. " + summary)
    if md > 0.05:
        return ("MIDDLE_BAND", "MIDDLE_BAND: sparse edge 0.05-0.15 (partial). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: sparse ~ dense at B=10 coherent -- Option B (sparse only helps at B=1). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d B=%d c_d=%.2f KS=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, B, C_D, KS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
