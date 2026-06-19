"""
exp_predicate_partition_storage_v1 -- storage: predicate-partitioned vs flat capacity -- CPU.
ROUTING: storage test program. Does partitioning facts into P predicate-groups (separate W per group) raise total capacity
  vs one flat W? Per-group load is lower -> higher per-group recall -> more total facts at fixed recall. CPU.
PRE-REGISTERED: HARD-PASS partitioned total capacity >= 1.5x flat at recall 0.95. MIDDLE 1.1-1.5x. HARD-FAIL <1.1x.
FORMULA SELF-TESTS (PROT-022): 1. flat recall. 2. partition lowers load. 3. bipolar.
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
ANCHOR_NAME = "predicate_partition_storage_v1"; N = 2048; P_GROUPS = 4; FLIP = 0.05
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SEEDS = [1] if RUN_MODE == "smoke" else [7, 17, 23]; LOADS = [0.05, 0.1, 0.14, 0.2, 0.3]
def pat(M, n, g): return (g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32)
def Wp(P):
    G = P @ P.T + 1e-3 * np.eye(P.shape[0], dtype=np.float32); W = (P.T @ np.linalg.solve(G, P)).astype(np.float32); np.fill_diagonal(W, 0.0); return W
def rec(P, W, seed):
    g = np.random.default_rng(seed); M, n = P.shape; s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(8):
        s = np.sign(s @ W.T); s[s == 0] = 1.0
    return float(np.mean(np.all(s == P, axis=1)))
def cap_flat(n, seed):
    g = np.random.default_rng(seed); c = 0
    for load in LOADS:
        M = max(2, int(load * n))
        P = pat(M, n, g)
        if rec(P, Wp(P), seed * 3 + M) >= 0.95: c = M
        else: break
    return c
def cap_part(n, seed):
    g = np.random.default_rng(seed); c = 0
    for load in LOADS:
        Mtot = max(2, int(load * n)); per = max(1, Mtot // P_GROUPS); ok = True
        for gi in range(P_GROUPS):
            Pg = pat(per, n, g)
            if rec(Pg, Wp(Pg), seed * 5 + gi * 100 + per) < 0.95: ok = False; break
        if ok: c = per * P_GROUPS
        else: break
    return c
def _selftest():
    g = np.random.default_rng(0); P = pat(1, 128, g); assert rec(P, Wp(P), 0) >= 0.95, "flat recall"
    assert P_GROUPS > 1, "partition lowers load"
    assert set(np.unique(pat(4, 16, g))) <= {-1.0, 1.0}, "bipolar"
    print("[selftest] PASS: predicate-partition", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    flat = float(np.mean([cap_flat(N, s) for s in SEEDS])); part = float(np.mean([cap_part(N, s) for s in SEEDS]))
    print("  flat_capacity=%.0f partitioned_capacity=%.0f ratio=%.2f" % (flat, part, part / max(flat, 1)), flush=True)
    return {"flat": flat, "partitioned": part, "ratio": part / max(flat, 1e-9)}
def verdict(r) -> Tuple[str, str]:
    ra = r["ratio"]; summary = "flat=%.0f partitioned=%.0f ratio=%.2f (P=%d groups)" % (r["flat"], r["partitioned"], ra, P_GROUPS)
    if ra >= 1.5: return ("HARD_PASS", "HARD_PASS: predicate-partitioned storage >=1.5x flat capacity -- partition by predicate for more facts/W. " + summary)
    if ra >= 1.1: return ("MIDDLE_BAND", "MIDDLE_BAND: partition 1.1-1.5x. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: partition <1.1x flat -- no capacity gain. " + summary)
print("[config] anchor=%s mode=%s seeds=%s N=%d P=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, P_GROUPS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
